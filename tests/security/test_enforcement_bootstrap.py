import hashlib
import json
import os
from pathlib import Path
import tempfile
import unittest

from runtime.security.enforcement_bootstrap import bootstrap_enforcement_service
from runtime.security.permission_engine import ActionContext
from runtime.security.startup_integrity import IntegrityViolation


class EnforcementBootstrapTests(unittest.TestCase):
    def _manifest_for(self, root: Path, relpaths: list[str], manifest: Path) -> None:
        artifacts = []
        for relpath in relpaths:
            digest = hashlib.sha256((root / relpath).read_bytes()).hexdigest()
            artifacts.append(
                {
                    "name": relpath.replace("/", "-"),
                    "path": relpath,
                    "sha256": digest,
                }
            )
        manifest.write_text(
            json.dumps({"manifest_version": 1, "artifacts": artifacts}),
            encoding="utf-8",
        )

    def test_integrity_failure_happens_before_policy_load(self):
        with tempfile.TemporaryDirectory() as td:
            base = Path(td)
            root = base / "root"
            root.mkdir()
            policy_rel = "policy.json"
            policy = root / policy_rel
            policy.write_text("not-json", encoding="utf-8")
            manifest = base / "manifest.json"
            manifest.write_text(
                json.dumps(
                    {
                        "manifest_version": 1,
                        "artifacts": [
                            {
                                "name": "policy",
                                "path": policy_rel,
                                "sha256": "0" * 64,
                            }
                        ],
                    }
                ),
                encoding="utf-8",
            )
            audit_dir = base / "audit"
            os.mkdir(audit_dir, 0o700)

            with self.assertRaisesRegex(IntegrityViolation, "startup_integrity_failed"):
                bootstrap_enforcement_service(
                    root=root,
                    manifest_path=manifest,
                    policy_relative_path=policy_rel,
                    audit_path=audit_dir / "audit.jsonl",
                )

    def test_policy_must_be_covered_by_manifest(self):
        with tempfile.TemporaryDirectory() as td:
            base = Path(td)
            root = base / "root"
            root.mkdir()
            policy_rel = "policy.json"
            (root / policy_rel).write_text(
                json.dumps({"policy_version": 1, "rules": []}),
                encoding="utf-8",
            )
            other = root / "daemon.py"
            other.write_text("safe\n", encoding="utf-8")
            manifest = base / "manifest.json"
            self._manifest_for(root, ["daemon.py"], manifest)
            audit_dir = base / "audit"
            os.mkdir(audit_dir, 0o700)

            with self.assertRaisesRegex(
                IntegrityViolation,
                "policy_not_covered_by_integrity_manifest",
            ):
                bootstrap_enforcement_service(
                    root=root,
                    manifest_path=manifest,
                    policy_relative_path=policy_rel,
                    audit_path=audit_dir / "audit.jsonl",
                )

    def test_verified_bootstrap_returns_sanitized_service(self):
        with tempfile.TemporaryDirectory() as td:
            base = Path(td)
            root = base / "root"
            root.mkdir()
            policy_rel = "policy.json"
            policy = root / policy_rel
            policy.write_text(
                json.dumps(
                    {
                        "policy_version": 1,
                        "rules": [
                            {
                                "rule_id": "security.credentials.internal-name",
                                "status": "active",
                                "scope": {"risk_tags": ["credentials"]},
                                "authority_source": "Bryan explicit",
                                "outcome": "REQUIRE_APPROVAL",
                                "reason": "operator detail",
                                "protected_value": "security",
                            }
                        ],
                    }
                ),
                encoding="utf-8",
            )
            manifest = base / "manifest.json"
            self._manifest_for(root, [policy_rel], manifest)
            audit_dir = base / "audit"
            os.mkdir(audit_dir, 0o700)

            service = bootstrap_enforcement_service(
                root=root,
                manifest_path=manifest,
                policy_relative_path=policy_rel,
                audit_path=audit_dir / "audit.jsonl",
            )
            response = service.evaluate(
                action=ActionContext.build(
                    "change_auth",
                    risk_tags=["credentials"],
                    meaningful=True,
                )
            )

            wire = json.dumps(response)
            self.assertEqual(response["outcome"], "REQUIRE_APPROVAL")
            self.assertEqual(response["reason"], "approval_required")
            self.assertNotIn("credentials", wire)
            self.assertNotIn("internal-name", wire)


if __name__ == "__main__":
    unittest.main()
