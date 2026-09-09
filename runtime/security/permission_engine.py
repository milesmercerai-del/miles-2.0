from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime, timezone
from enum import Enum
import json
from pathlib import Path
from typing import Any, Iterable


class Outcome(str, Enum):
    ALLOW_AUTO = "ALLOW_AUTO"
    ALLOW_REVIEW_AFTER = "ALLOW_REVIEW_AFTER"
    REQUIRE_APPROVAL = "REQUIRE_APPROVAL"
    BLOCK = "BLOCK"


AUTHORITY_RANK = {
    "standing authority": 10,
    "learned guardrail": 20,
    "Bryan explicit": 30,
    "runtime safety": 40,
    "platform/system": 50,
}

SENSITIVE_RISK_TAGS = {
    "money",
    "privacy",
    "credentials",
    "access_control",
    "security_posture",
    "destructive_data",
    "hard_to_reverse_hardware",
    "external_commitment",
    "bryan_values",
    "relationship_commitments",
    "new_authority",
    # Defense-in-depth: these incident-derived tags remain sensitive even if
    # the external policy file is absent, incomplete, or bypassed by a caller.
    "production_write",
    "arbitrary_host_code_execution",
    "unbounded_network_egress",
    "privileged_tool_manifest_change",
}


@dataclass(frozen=True)
class ActionContext:
    action_type: str
    domains: frozenset[str] = field(default_factory=frozenset)
    risk_tags: frozenset[str] = field(default_factory=frozenset)
    meaningful: bool = False
    reversible: bool = True
    capability_available: bool = True
    hard_boundary_blocked: bool = False
    emergency_containment_applies: bool = False
    requested_by: str = "miles"

    @classmethod
    def build(
        cls,
        action_type: str,
        *,
        domains: Iterable[str] = (),
        risk_tags: Iterable[str] = (),
        **kwargs: Any,
    ) -> "ActionContext":
        return cls(
            action_type=action_type,
            domains=frozenset(domains),
            risk_tags=frozenset(risk_tags),
            **kwargs,
        )


@dataclass(frozen=True)
class Rule:
    rule_id: str
    status: str
    scope: dict[str, Any]
    authority_source: str
    outcome: Outcome
    reason: str
    protected_value: str
    created_at: str | None = None
    review_trigger: str | None = None
    retire_when: str | None = None
    supersedes: str | None = None
    notes: str | None = None
    expires_at: str | None = None

    @classmethod
    def from_dict(cls, raw: dict[str, Any]) -> "Rule":
        return cls(
            rule_id=raw["rule_id"],
            status=raw.get("status", "active"),
            scope=raw.get("scope", {}),
            authority_source=raw.get("authority_source", "standing authority"),
            outcome=Outcome(raw["outcome"]),
            reason=raw.get("reason", ""),
            protected_value=raw.get("protected_value", ""),
            created_at=raw.get("created_at"),
            review_trigger=raw.get("review_trigger"),
            retire_when=raw.get("retire_when"),
            supersedes=raw.get("supersedes"),
            notes=raw.get("notes"),
            expires_at=raw.get("expires_at"),
        )

    def active(self, now: datetime | None = None) -> bool:
        if self.status != "active":
            return False
        if not self.expires_at:
            return True
        now = now or datetime.now(timezone.utc)
        expiry = datetime.fromisoformat(self.expires_at.replace("Z", "+00:00"))
        if expiry.tzinfo is None:
            expiry = expiry.replace(tzinfo=timezone.utc)
        return now < expiry

    def matches(self, action: ActionContext) -> bool:
        action_types = set(self.scope.get("action_types", []))
        if action_types and action.action_type not in action_types:
            return False

        domains = set(self.scope.get("domains", []))
        if domains and not domains.intersection(action.domains):
            return False

        risk_tags = set(self.scope.get("risk_tags", []))
        if risk_tags and not risk_tags.intersection(action.risk_tags):
            return False

        requested_by = set(self.scope.get("requested_by", []))
        if requested_by and action.requested_by not in requested_by:
            return False

        return True

    def specificity(self) -> int:
        score = 0
        for key in ("action_types", "domains", "risk_tags", "requested_by"):
            values = self.scope.get(key, [])
            if values:
                score += 1
        return score

    def authority_rank(self) -> int:
        return AUTHORITY_RANK.get(self.authority_source, 0)


@dataclass(frozen=True)
class PermissionDecision:
    outcome: Outcome
    reason: str
    matched_rule_ids: tuple[str, ...] = ()
    approval_required_from: str | None = None
    logging_required: bool = True

    def as_dict(self) -> dict[str, Any]:
        return {
            "outcome": self.outcome.value,
            "reason": self.reason,
            "matched_rule_ids": list(self.matched_rule_ids),
            "approval_required_from": self.approval_required_from,
            "logging_required": self.logging_required,
        }


class PermissionEngine:
    def __init__(self, rules: Iterable[Rule] = ()) -> None:
        self.rules = tuple(rules)

    @classmethod
    def from_json(cls, path: str | Path) -> "PermissionEngine":
        raw = json.loads(Path(path).read_text(encoding="utf-8"))
        rules = [Rule.from_dict(item) for item in raw.get("rules", [])]
        return cls(rules)

    def evaluate(
        self,
        action: ActionContext,
        *,
        now: datetime | None = None,
    ) -> PermissionDecision:
        if not action.capability_available:
            return PermissionDecision(
                outcome=Outcome.BLOCK,
                reason="capability_unavailable",
            )

        if action.hard_boundary_blocked:
            return PermissionDecision(
                outcome=Outcome.BLOCK,
                reason="non_overridable_boundary",
            )

        if action.emergency_containment_applies:
            return PermissionDecision(
                outcome=Outcome.BLOCK,
                reason="emergency_containment_active",
            )

        matches = [rule for rule in self.rules if rule.active(now) and rule.matches(action)]
        if matches:
            decision = self._decide_from_rules(matches)
            if decision is not None:
                return decision

        return self._standing_classification(action)

    def _decide_from_rules(self, matches: list[Rule]) -> PermissionDecision | None:
        highest_authority = max(rule.authority_rank() for rule in matches)
        authority_matches = [
            rule for rule in matches if rule.authority_rank() == highest_authority
        ]

        highest_specificity = max(rule.specificity() for rule in authority_matches)
        finalists = [
            rule for rule in authority_matches
            if rule.specificity() == highest_specificity
        ]

        outcomes = {rule.outcome for rule in finalists}
        ids = tuple(sorted(rule.rule_id for rule in finalists))

        if len(outcomes) > 1:
            if highest_authority >= AUTHORITY_RANK["platform/system"]:
                return PermissionDecision(
                    outcome=Outcome.BLOCK,
                    reason="rule_conflict_at_non_overridable_authority",
                    matched_rule_ids=ids,
                )
            return PermissionDecision(
                outcome=Outcome.REQUIRE_APPROVAL,
                reason="rule_conflict_requires_resolution",
                matched_rule_ids=ids,
                approval_required_from="Bryan",
            )

        selected = finalists[0]
        approval = "Bryan" if selected.outcome == Outcome.REQUIRE_APPROVAL else None
        logging_required = selected.outcome != Outcome.ALLOW_AUTO
        return PermissionDecision(
            outcome=selected.outcome,
            reason=f"matched_rule:{selected.rule_id}",
            matched_rule_ids=ids,
            approval_required_from=approval,
            logging_required=logging_required,
        )

    def _standing_classification(self, action: ActionContext) -> PermissionDecision:
        if action.risk_tags.intersection(SENSITIVE_RISK_TAGS):
            return PermissionDecision(
                outcome=Outcome.REQUIRE_APPROVAL,
                reason="standing_policy_sensitive_domain",
                approval_required_from="Bryan",
            )

        if action.meaningful and not action.reversible:
            return PermissionDecision(
                outcome=Outcome.REQUIRE_APPROVAL,
                reason="standing_policy_meaningful_irreversible",
                approval_required_from="Bryan",
            )

        if action.meaningful:
            return PermissionDecision(
                outcome=Outcome.ALLOW_REVIEW_AFTER,
                reason="standing_policy_meaningful_reversible",
            )

        return PermissionDecision(
            outcome=Outcome.ALLOW_AUTO,
            reason="standing_policy_trivial_reversible",
            logging_required=False,
        )
