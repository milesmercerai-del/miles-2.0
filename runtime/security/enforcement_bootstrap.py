from __future__ import annotations

import json
from pathlib import Path

from .audit_log import SecureAuditWriter
from .enforcement_service import EnforcementService
from .permission_engine import PermissionEngine, Rule
from .startup_integrity import IntegrityViolation, enforce_manifest, read_verified_bytes


def bootstrap_enforcement_service(
    *,
    root: str | Path,
    manifest_path: str | Path,
    policy_relative_path: str,
    audit_path: str | Path,
    expected_manifest_owner_uid: int | None = None,
    expected_audit_owner_uid: int | None = None,
) -> EnforcementService:
    """Build the enforcement service only after startup integrity passes.

    Ordering is intentional:
    1. verify all protected artifacts in the external manifest;
    2. require the policy file itself to be covered by that manifest;
    3. verify that the audit sink is private enough to hold operator detail;
    4. re-read the policy through one no-follow file descriptor and verify the
       exact bytes that will be parsed against the approved digest;
    5. only then expose the enforcement service.

    A production launcher must itself be protected outside Miles runtime write
    authority. This bootstrap enforces the sequence but is not a substitute for
    OS ownership/immutability of the launcher and manifest.
    """
    root_path = Path(root).resolve()
    report = enforce_manifest(
        manifest_path,
        root=root_path,
        expected_manifest_owner_uid=expected_manifest_owner_uid,
    )

    candidate = Path(policy_relative_path)
    if candidate.is_absolute() or ".." in candidate.parts:
        raise IntegrityViolation("policy_path_must_be_relative_to_integrity_root")
    normalized_policy = candidate.as_posix()

    covered = {item.path for item in report.results if item.ok}
    if normalized_policy not in covered:
        raise IntegrityViolation("policy_not_covered_by_integrity_manifest")

    audit_writer = SecureAuditWriter(
        audit_path,
        expected_owner_uid=expected_audit_owner_uid,
    )
    audit_writer.verify_ready()

    policy_path = (root_path / normalized_policy).resolve(strict=True)
    try:
        policy_path.relative_to(root_path)
    except ValueError as exc:
        raise IntegrityViolation("policy_path_escaped_integrity_root") from exc

    policy_result = next(item for item in report.results if item.path == normalized_policy)
    policy_bytes = read_verified_bytes(
        policy_path,
        expected_sha256=policy_result.expected_sha256,
    )
    try:
        raw = json.loads(policy_bytes.decode("utf-8"))
    except (UnicodeDecodeError, json.JSONDecodeError) as exc:
        raise IntegrityViolation("verified_policy_is_not_valid_utf8_json") from exc

    engine = PermissionEngine(Rule.from_dict(item) for item in raw.get("rules", []))
    return EnforcementService(engine=engine, audit_writer=audit_writer)
