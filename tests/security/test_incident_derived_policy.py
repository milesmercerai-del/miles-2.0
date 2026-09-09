import unittest
from pathlib import Path

from runtime.security.permission_engine import ActionContext, Outcome, PermissionEngine


class IncidentDerivedPolicyTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        policy_path = (
            Path(__file__).parents[2]
            / "runtime"
            / "security"
            / "default_policy.json"
        )
        cls.engine = PermissionEngine.from_json(policy_path)

    def test_incident_derived_high_risk_tags_require_bryan_approval(self):
        tags = (
            "production_write",
            "arbitrary_host_code_execution",
            "unbounded_network_egress",
            "privileged_tool_manifest_change",
        )
        for tag in tags:
            with self.subTest(tag=tag):
                decision = self.engine.evaluate(
                    ActionContext.build(
                        "incident_regression_probe",
                        risk_tags=[tag],
                        meaningful=True,
                        reversible=True,
                    )
                )
                self.assertEqual(decision.outcome, Outcome.REQUIRE_APPROVAL)
                self.assertEqual(decision.approval_required_from, "Bryan")

    def test_incident_tags_fail_safe_without_external_policy_rules(self):
        bare_engine = PermissionEngine()
        tags = (
            "production_write",
            "arbitrary_host_code_execution",
            "unbounded_network_egress",
            "privileged_tool_manifest_change",
        )
        for tag in tags:
            with self.subTest(tag=tag):
                decision = bare_engine.evaluate(
                    ActionContext.build(
                        "incident_regression_probe",
                        risk_tags=[tag],
                        meaningful=True,
                        reversible=True,
                    )
                )
                self.assertEqual(decision.outcome, Outcome.REQUIRE_APPROVAL)
                self.assertEqual(decision.approval_required_from, "Bryan")

    def test_ordinary_brokered_web_activity_is_not_reclassified_as_unbounded_egress(self):
        decision = self.engine.evaluate(
            ActionContext.build(
                "brokered_web_read",
                domains=["research"],
                meaningful=True,
                reversible=True,
            )
        )
        self.assertEqual(decision.outcome, Outcome.ALLOW_REVIEW_AFTER)

    def test_low_risk_local_work_stays_auto(self):
        decision = self.engine.evaluate(
            ActionContext.build("format_local_notes")
        )
        self.assertEqual(decision.outcome, Outcome.ALLOW_AUTO)


if __name__ == "__main__":
    unittest.main()
