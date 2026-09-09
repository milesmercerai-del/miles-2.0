from __future__ import annotations

from dataclasses import dataclass
from typing import Any
from uuid import uuid4

from .audit_log import SecureAuditWriter, build_audit_record
from .permission_engine import ActionContext, Outcome, PermissionDecision, PermissionEngine


_PUBLIC_REASON_BY_OUTCOME = {
    Outcome.ALLOW_AUTO: "allowed",
    Outcome.ALLOW_REVIEW_AFTER: "allowed_review_after",
    Outcome.REQUIRE_APPROVAL: "approval_required",
    Outcome.BLOCK: "action_blocked",
}


def requester_decision_view(
    *,
    action_id: str,
    decision: PermissionDecision,
) -> dict[str, Any]:
    """Return the minimum requester-facing decision detail.

    Do not expose internal reason strings or matched rule IDs here; those remain
    in the protected operator audit record.
    """
    return {
        "action_id": action_id,
        "outcome": decision.outcome.value,
        "reason": _PUBLIC_REASON_BY_OUTCOME[decision.outcome],
        "approval_required_from": decision.approval_required_from,
    }


@dataclass
class EnforcementService:
    """Small broker that keeps operator detail inside the enforcement boundary.

    Production deployment should run this behind a separate daemon/OS identity.
    The Miles runtime should receive only the returned requester-facing mapping,
    not direct access to the PermissionEngine object or protected audit file.
    """

    engine: PermissionEngine
    audit_writer: SecureAuditWriter

    def evaluate(self, *, action: ActionContext) -> dict[str, Any]:
        # Generate the correlation identifier inside the security boundary so
        # caller-controlled text cannot accidentally smuggle secrets into the
        # operator audit log through an "action id" field.
        action_id = str(uuid4())
        decision = self.engine.evaluate(action)

        if decision.logging_required:
            record = build_audit_record(
                action_id=action_id,
                action=action,
                decision=decision,
            )
            return self.audit_writer.append(record)

        # ALLOW_AUTO normally is not written to the security ledger, but it still
        # uses the same minimum-detail requester projection.
        return requester_decision_view(action_id=action_id, decision=decision)
