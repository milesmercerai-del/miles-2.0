import json
import os
from pathlib import Path
import tempfile
import unittest

from runtime.security.audit_log import SecureAuditWriter
from runtime.security.enforcement_service import EnforcementService
from runtime.security.permission_engine import ActionContext, PermissionEngine, Rule


class EnforcementServiceTests(unittest.TestCase):
    def test_service_returns_sanitized_response_and_keeps_detail_in_audit(self):
        rule = Rule.from_dict(
            {
                "rule_id": "security.credentials.super-secret-rule-name",
                "scope": {"action_types": ["change_auth"]},
                "authority_source": "Bryan explicit",
                "outcome": "REQUIRE_APPROVAL",
                "reason": "operator detail",
                "protected_value": "security",
            }
        )

        with tempfile.TemporaryDirectory() as td:
            audit_dir = Path(td) / "private"
            os.mkdir(audit_dir, 0o700)
            audit_path = audit_dir / "audit.jsonl"
            service = EnforcementService(
                PermissionEngine([rule]),
                SecureAuditWriter(audit_path),
            )
            response = service.evaluate(
                action=ActionContext.build(
                    "change_auth",
                    risk_tags=["credentials"],
                    meaningful=True,
                ),
            )

            wire = json.dumps(response)
            self.assertEqual(response["outcome"], "REQUIRE_APPROVAL")
            self.assertEqual(response["reason"], "approval_required")
            self.assertNotIn("matched_rule_ids", response)
            self.assertNotIn("credentials", wire)
            self.assertNotIn("super-secret-rule-name", wire)

            operator = json.loads(audit_path.read_text(encoding="utf-8"))
            self.assertIn(
                "security.credentials.super-secret-rule-name",
                operator["matched_rule_ids"],
            )


if __name__ == "__main__":
    unittest.main()
