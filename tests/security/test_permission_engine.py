import unittest
from datetime import datetime, timezone
from pathlib import Path

from runtime.security.permission_engine import (
    ActionContext,
    Outcome,
    PermissionEngine,
    Rule,
)


class PermissionEngineTests(unittest.TestCase):
    def test_low_risk_action_is_auto(self):
        engine = PermissionEngine()
        decision = engine.evaluate(ActionContext.build("format_docs"))
        self.assertEqual(decision.outcome, Outcome.ALLOW_AUTO)
        self.assertFalse(decision.logging_required)

    def test_meaningful_reversible_action_is_review_after(self):
        engine = PermissionEngine()
        action = ActionContext.build(
            "refactor_runtime",
            meaningful=True,
            reversible=True,
        )
        self.assertEqual(
            engine.evaluate(action).outcome,
            Outcome.ALLOW_REVIEW_AFTER,
        )

    def test_security_change_requires_approval(self):
        engine = PermissionEngine()
        action = ActionContext.build("change_auth", risk_tags=["credentials"])
        decision = engine.evaluate(action)
        self.assertEqual(decision.outcome, Outcome.REQUIRE_APPROVAL)
        self.assertEqual(decision.approval_required_from, "Bryan")

    def test_hard_boundary_blocks(self):
        engine = PermissionEngine()
        action = ActionContext.build("side_effect", hard_boundary_blocked=True)
        self.assertEqual(engine.evaluate(action).outcome, Outcome.BLOCK)

    def test_retired_rule_is_ignored(self):
        rule = Rule.from_dict(
            {
                "rule_id": "old.block",
                "status": "retired",
                "scope": {"action_types": ["format_docs"]},
                "authority_source": "Bryan explicit",
                "outcome": "BLOCK",
                "reason": "historical",
                "protected_value": "none",
            }
        )
        engine = PermissionEngine([rule])
        self.assertEqual(
            engine.evaluate(ActionContext.build("format_docs")).outcome,
            Outcome.ALLOW_AUTO,
        )

    def test_expired_rule_is_ignored(self):
        rule = Rule.from_dict(
            {
                "rule_id": "expired.block",
                "status": "active",
                "scope": {"action_types": ["format_docs"]},
                "authority_source": "Bryan explicit",
                "outcome": "BLOCK",
                "reason": "temporary",
                "protected_value": "none",
                "expires_at": "2026-01-01T00:00:00Z",
            }
        )
        engine = PermissionEngine([rule])
        now = datetime(2026, 9, 8, tzinfo=timezone.utc)
        self.assertEqual(
            engine.evaluate(ActionContext.build("format_docs"), now=now).outcome,
            Outcome.ALLOW_AUTO,
        )

    def test_equal_conflicting_rules_require_resolution(self):
        rules = [
            Rule.from_dict(
                {
                    "rule_id": "a.allow",
                    "status": "active",
                    "scope": {"action_types": ["deploy"]},
                    "authority_source": "Bryan explicit",
                    "outcome": "ALLOW_AUTO",
                    "reason": "test",
                    "protected_value": "test",
                }
            ),
            Rule.from_dict(
                {
                    "rule_id": "b.block",
                    "status": "active",
                    "scope": {"action_types": ["deploy"]},
                    "authority_source": "Bryan explicit",
                    "outcome": "BLOCK",
                    "reason": "test",
                    "protected_value": "test",
                }
            ),
        ]
        decision = PermissionEngine(rules).evaluate(ActionContext.build("deploy"))
        self.assertEqual(decision.outcome, Outcome.REQUIRE_APPROVAL)
        self.assertEqual(decision.reason, "rule_conflict_requires_resolution")

    def test_more_specific_rule_wins_at_same_authority(self):
        rules = [
            Rule.from_dict(
                {
                    "rule_id": "broad.ask",
                    "status": "active",
                    "scope": {"domains": ["docs"]},
                    "authority_source": "Bryan explicit",
                    "outcome": "REQUIRE_APPROVAL",
                    "reason": "test",
                    "protected_value": "test",
                }
            ),
            Rule.from_dict(
                {
                    "rule_id": "specific.auto",
                    "status": "active",
                    "scope": {
                        "domains": ["docs"],
                        "action_types": ["format_docs"],
                    },
                    "authority_source": "Bryan explicit",
                    "outcome": "ALLOW_AUTO",
                    "reason": "test",
                    "protected_value": "test",
                }
            ),
        ]
        action = ActionContext.build("format_docs", domains=["docs"])
        self.assertEqual(
            PermissionEngine(rules).evaluate(action).outcome,
            Outcome.ALLOW_AUTO,
        )

    def test_emergency_containment_blocks_side_effect(self):
        engine = PermissionEngine()
        action = ActionContext.build(
            "move_servo",
            emergency_containment_applies=True,
        )
        self.assertEqual(engine.evaluate(action).outcome, Outcome.BLOCK)

    def test_default_policy_loads(self):
        policy_path = (
            Path(__file__).parents[2]
            / "runtime"
            / "security"
            / "default_policy.json"
        )
        engine = PermissionEngine.from_json(policy_path)
        action = ActionContext.build(
            "change_auth",
            risk_tags=["security_posture"],
        )
        self.assertEqual(
            engine.evaluate(action).outcome,
            Outcome.REQUIRE_APPROVAL,
        )


if __name__ == "__main__":
    unittest.main()
