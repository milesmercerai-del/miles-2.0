import json
import os
from pathlib import Path
import stat
import tempfile
import unittest

from runtime.security.audit_log import (
    AuditSecurityError,
    SecureAuditWriter,
    build_audit_record,
)
from runtime.security.permission_engine import ActionContext, PermissionEngine, Rule


class AuditLogTests(unittest.TestCase):
    def _decision_with_rule(self):
        rule = Rule.from_dict(
            {
                "rule_id": "security.secret.internal-rule-name",
                "scope": {"action_types": ["change_auth"]},
                "authority_source": "Bryan explicit",
                "outcome": "REQUIRE_APPROVAL",
                "reason": "operator-only detail",
                "protected_value": "security",
            }
        )
        action = ActionContext.build(
            "change_auth",
            risk_tags=["credentials"],
            meaningful=True,
        )
        decision = PermissionEngine([rule]).evaluate(action)
        return action, decision

    def test_requester_projection_hides_policy_oracle_detail(self):
        action, decision = self._decision_with_rule()
        record = build_audit_record(
            action_id="a-1",
            action=action,
            decision=decision,
        )
        public = record.requester_dict()

        serialized = json.dumps(public)
        self.assertNotIn("matched_rule_ids", public)
        self.assertNotIn("risk_tags", public)
        self.assertNotIn("internal_reason", public)
        self.assertNotIn("change_auth", serialized)
        self.assertNotIn("credentials", serialized)
        self.assertNotIn("security.secret.internal-rule-name", serialized)
        self.assertEqual(public["reason"], "approval_required")

    def test_writer_keeps_operator_detail_in_private_sink(self):
        with tempfile.TemporaryDirectory() as td:
            root = Path(td) / "audit-private"
            os.mkdir(root, 0o700)
            path = root / "security.jsonl"
            action, decision = self._decision_with_rule()
            record = build_audit_record(
                action_id="a-2",
                action=action,
                decision=decision,
            )
            public = SecureAuditWriter(path).append(record)

            full = json.loads(path.read_text(encoding="utf-8"))
            self.assertIn("matched_rule_ids", full)
            self.assertIn("security.secret.internal-rule-name", full["matched_rule_ids"])
            self.assertNotIn("matched_rule_ids", public)

            if os.name == "posix":
                self.assertEqual(stat.S_IMODE(path.stat().st_mode), 0o600)

    @unittest.skipUnless(os.name == "posix", "POSIX permission semantics required")
    def test_writer_rejects_group_or_world_readable_log(self):
        with tempfile.TemporaryDirectory() as td:
            root = Path(td) / "audit-private"
            os.mkdir(root, 0o700)
            path = root / "security.jsonl"
            path.write_text("", encoding="utf-8")
            os.chmod(path, 0o644)
            action, decision = self._decision_with_rule()
            record = build_audit_record(
                action_id="a-3",
                action=action,
                decision=decision,
            )
            with self.assertRaises(AuditSecurityError):
                SecureAuditWriter(path).append(record)

    @unittest.skipUnless(os.name == "posix", "POSIX permission semantics required")
    def test_writer_rejects_non_private_directory(self):
        with tempfile.TemporaryDirectory() as td:
            root = Path(td) / "audit-open"
            os.mkdir(root, 0o755)
            path = root / "security.jsonl"
            action, decision = self._decision_with_rule()
            record = build_audit_record(
                action_id="a-4",
                action=action,
                decision=decision,
            )
            with self.assertRaises(AuditSecurityError):
                SecureAuditWriter(path).append(record)


if __name__ == "__main__":
    unittest.main()
