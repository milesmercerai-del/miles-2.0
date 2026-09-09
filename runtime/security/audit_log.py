from __future__ import annotations

from dataclasses import asdict, dataclass
from datetime import datetime, timezone
import json
import os
from pathlib import Path
import stat
from typing import Any
from uuid import uuid4

from .permission_engine import ActionContext, Outcome, PermissionDecision


class AuditSecurityError(RuntimeError):
    """Raised when the audit sink is not private enough to hold security data."""


_PUBLIC_REASON_BY_OUTCOME = {
    Outcome.ALLOW_AUTO: "allowed",
    Outcome.ALLOW_REVIEW_AFTER: "allowed_review_after",
    Outcome.REQUIRE_APPROVAL: "approval_required",
    Outcome.BLOCK: "action_blocked",
}


@dataclass(frozen=True)
class AuditRecord:
    """Structured operator-side security record.

    Deliberately excludes raw prompts, message bodies, credentials, tokens,
    filesystem targets, recipients, URLs, and arbitrary free-form metadata.
    Those values can contain secrets or become an attacker-facing policy oracle.
    """

    event_id: str
    action_id: str
    recorded_at: str
    requested_by: str
    action_type: str
    outcome: str
    internal_reason: str
    matched_rule_ids: tuple[str, ...]
    approval_required_from: str | None
    risk_tags: tuple[str, ...]
    public_reason: str

    def operator_dict(self) -> dict[str, Any]:
        raw = asdict(self)
        raw["matched_rule_ids"] = list(self.matched_rule_ids)
        raw["risk_tags"] = list(self.risk_tags)
        return raw

    def requester_dict(self) -> dict[str, Any]:
        # Keep requester-facing detail intentionally small. In particular, do
        # not expose matched rule IDs, internal thresholds, risk tags, or the
        # internal reason string.
        return {
            "event_id": self.event_id,
            "action_id": self.action_id,
            "recorded_at": self.recorded_at,
            "outcome": self.outcome,
            "reason": self.public_reason,
            "approval_required_from": self.approval_required_from,
        }


def build_audit_record(
    *,
    action_id: str,
    action: ActionContext,
    decision: PermissionDecision,
    recorded_at: datetime | None = None,
) -> AuditRecord:
    when = recorded_at or datetime.now(timezone.utc)
    if when.tzinfo is None:
        when = when.replace(tzinfo=timezone.utc)

    return AuditRecord(
        event_id=str(uuid4()),
        action_id=action_id,
        recorded_at=when.astimezone(timezone.utc).isoformat().replace("+00:00", "Z"),
        requested_by=action.requested_by,
        action_type=action.action_type,
        outcome=decision.outcome.value,
        internal_reason=decision.reason,
        matched_rule_ids=tuple(decision.matched_rule_ids),
        approval_required_from=decision.approval_required_from,
        risk_tags=tuple(sorted(action.risk_tags)),
        public_reason=_PUBLIC_REASON_BY_OUTCOME[decision.outcome],
    )


class SecureAuditWriter:
    """Append structured records to a private JSONL sink.

    This class intentionally provides no audit-log read API. Runtime callers
    should receive AuditRecord.requester_dict() from the enforcement service.
    Operator reads belong behind a separately authorized OS/service boundary.
    """

    def __init__(
        self,
        path: str | Path,
        *,
        expected_owner_uid: int | None = None,
        fsync: bool = True,
    ) -> None:
        self.path = Path(path)
        self.expected_owner_uid = expected_owner_uid
        self.fsync = fsync

    def _prepare_parent(self) -> None:
        parent = self.path.parent
        parent.mkdir(parents=True, mode=0o700, exist_ok=True)

        if os.name == "posix":
            st = parent.stat()
            if stat.S_IMODE(st.st_mode) & 0o077:
                raise AuditSecurityError("audit_directory_not_private")
            if self.expected_owner_uid is not None and st.st_uid != self.expected_owner_uid:
                raise AuditSecurityError("audit_directory_owner_mismatch")

    def _open_append(self) -> int:
        self._prepare_parent()

        if self.path.exists() and self.path.is_symlink():
            raise AuditSecurityError("audit_log_must_not_be_symlink")

        flags = (
            os.O_WRONLY
            | os.O_CREAT
            | os.O_APPEND
            | getattr(os, "O_CLOEXEC", 0)
            | getattr(os, "O_NOFOLLOW", 0)
        )
        try:
            fd = os.open(self.path, flags, 0o600)
        except OSError as exc:
            raise AuditSecurityError("unable_to_open_private_audit_log") from exc

        try:
            st = os.fstat(fd)
            if not stat.S_ISREG(st.st_mode):
                raise AuditSecurityError("audit_log_must_be_regular_file")
            if os.name == "posix":
                if stat.S_IMODE(st.st_mode) & 0o077:
                    raise AuditSecurityError("audit_log_permissions_not_private")
                if self.expected_owner_uid is not None and st.st_uid != self.expected_owner_uid:
                    raise AuditSecurityError("audit_log_owner_mismatch")
            return fd
        except Exception:
            os.close(fd)
            raise

    def verify_ready(self) -> None:
        """Fail closed at startup if the protected audit sink is unsafe."""
        fd = self._open_append()
        os.close(fd)

    def append(self, record: AuditRecord) -> dict[str, Any]:
        payload = (
            json.dumps(
                record.operator_dict(),
                sort_keys=True,
                separators=(",", ":"),
                ensure_ascii=False,
            )
            + "\n"
        ).encode("utf-8")

        fd = self._open_append()
        try:
            view = memoryview(payload)
            while view:
                written = os.write(fd, view)
                if written <= 0:
                    raise AuditSecurityError("audit_log_short_write")
                view = view[written:]
            if self.fsync:
                os.fsync(fd)
        finally:
            os.close(fd)

        return record.requester_dict()
