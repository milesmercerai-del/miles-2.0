from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime, timedelta, timezone
import hashlib
import json
import secrets
from typing import Any


class PermitValidationError(ValueError):
    """Raised when a permit cannot authorize the exact action presented."""


def canonical_action_digest(
    action_type: str,
    target: str,
    parameters: dict[str, Any] | None = None,
) -> str:
    """Bind a permit to the resolved action, target, and normalized parameters."""
    payload = {
        "action_type": action_type,
        "target": target,
        "parameters": parameters or {},
    }
    encoded = json.dumps(
        payload,
        sort_keys=True,
        separators=(",", ":"),
        ensure_ascii=False,
    ).encode("utf-8")
    return hashlib.sha256(encoded).hexdigest()


@dataclass(frozen=True)
class ActionPermit:
    permit_id: str
    action_digest: str
    policy_version: str
    issued_at: datetime
    expires_at: datetime

    @classmethod
    def issue(
        cls,
        *,
        action_digest: str,
        policy_version: str,
        ttl_seconds: int = 30,
        now: datetime | None = None,
    ) -> "ActionPermit":
        if ttl_seconds <= 0:
            raise ValueError("ttl_seconds must be positive")
        now = now or datetime.now(timezone.utc)
        if now.tzinfo is None:
            now = now.replace(tzinfo=timezone.utc)
        return cls(
            permit_id=secrets.token_urlsafe(24),
            action_digest=action_digest,
            policy_version=policy_version,
            issued_at=now,
            expires_at=now + timedelta(seconds=ttl_seconds),
        )


class PermitVerifier:
    """Minimal replay/TOCTOU guard for the future enforcement daemon.

    This scaffold deliberately does not pretend to be the final daemon. In a real
    deployment, consumed-permit state must live inside the trusted enforcement
    boundary and survive any lifecycle where replay after restart would matter.
    """

    def __init__(self) -> None:
        self._consumed: set[str] = set()

    def verify_and_consume(
        self,
        permit: ActionPermit,
        *,
        action_digest: str,
        current_policy_version: str,
        now: datetime | None = None,
    ) -> None:
        now = now or datetime.now(timezone.utc)
        if now.tzinfo is None:
            now = now.replace(tzinfo=timezone.utc)

        if permit.permit_id in self._consumed:
            raise PermitValidationError("permit_replay")

        if permit.policy_version != current_policy_version:
            raise PermitValidationError("stale_policy_version")

        if permit.action_digest != action_digest:
            raise PermitValidationError("action_binding_mismatch")

        if now >= permit.expires_at:
            raise PermitValidationError("permit_expired")

        self._consumed.add(permit.permit_id)
