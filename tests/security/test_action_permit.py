import unittest
from datetime import datetime, timedelta, timezone

from runtime.security.action_permit import (
    ActionPermit,
    PermitValidationError,
    PermitVerifier,
    canonical_action_digest,
)


class ActionPermitTests(unittest.TestCase):
    def setUp(self):
        self.now = datetime(2026, 9, 9, tzinfo=timezone.utc)
        self.digest = canonical_action_digest(
            "write_file",
            "/miles-data/memory/test.txt",
            {"mode": "replace", "bytes": 12},
        )

    def test_exact_bound_action_is_accepted_once(self):
        permit = ActionPermit.issue(
            action_digest=self.digest,
            policy_version="policy-v3",
            now=self.now,
        )
        verifier = PermitVerifier()
        verifier.verify_and_consume(
            permit,
            action_digest=self.digest,
            current_policy_version="policy-v3",
            now=self.now + timedelta(seconds=1),
        )

    def test_changed_target_or_parameters_fail_toctou_binding(self):
        permit = ActionPermit.issue(
            action_digest=self.digest,
            policy_version="policy-v3",
            now=self.now,
        )
        changed = canonical_action_digest(
            "write_file",
            "/miles-data/memory/other.txt",
            {"mode": "replace", "bytes": 12},
        )
        with self.assertRaisesRegex(PermitValidationError, "action_binding_mismatch"):
            PermitVerifier().verify_and_consume(
                permit,
                action_digest=changed,
                current_policy_version="policy-v3",
                now=self.now + timedelta(seconds=1),
            )

    def test_stale_policy_version_is_rejected(self):
        permit = ActionPermit.issue(
            action_digest=self.digest,
            policy_version="policy-v2",
            now=self.now,
        )
        with self.assertRaisesRegex(PermitValidationError, "stale_policy_version"):
            PermitVerifier().verify_and_consume(
                permit,
                action_digest=self.digest,
                current_policy_version="policy-v3",
                now=self.now + timedelta(seconds=1),
            )

    def test_replay_is_rejected(self):
        permit = ActionPermit.issue(
            action_digest=self.digest,
            policy_version="policy-v3",
            now=self.now,
        )
        verifier = PermitVerifier()
        verifier.verify_and_consume(
            permit,
            action_digest=self.digest,
            current_policy_version="policy-v3",
            now=self.now + timedelta(seconds=1),
        )
        with self.assertRaisesRegex(PermitValidationError, "permit_replay"):
            verifier.verify_and_consume(
                permit,
                action_digest=self.digest,
                current_policy_version="policy-v3",
                now=self.now + timedelta(seconds=2),
            )

    def test_expired_permit_is_rejected(self):
        permit = ActionPermit.issue(
            action_digest=self.digest,
            policy_version="policy-v3",
            ttl_seconds=5,
            now=self.now,
        )
        with self.assertRaisesRegex(PermitValidationError, "permit_expired"):
            PermitVerifier().verify_and_consume(
                permit,
                action_digest=self.digest,
                current_policy_version="policy-v3",
                now=self.now + timedelta(seconds=5),
            )


if __name__ == "__main__":
    unittest.main()
