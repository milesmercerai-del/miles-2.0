import hashlib
import json
import os
from pathlib import Path
import tempfile
import unittest

from runtime.security.startup_integrity import (
    IntegrityManifestError,
    IntegrityViolation,
    enforce_manifest,
    verify_manifest,
)


class StartupIntegrityTests(unittest.TestCase):
    def _write_manifest(self, root: Path, manifest: Path, relpath: str) -> None:
        target = root / relpath
        digest = hashlib.sha256(target.read_bytes()).hexdigest()
        manifest.write_text(
            json.dumps(
                {
                    "manifest_version": 1,
                    "artifacts": [
                        {
                            "name": "permission-daemon",
                            "path": relpath,
                            "sha256": digest,
                        }
                    ],
                }
            ),
            encoding="utf-8",
        )

    def test_valid_manifest_passes(self):
        with tempfile.TemporaryDirectory() as td:
            base = Path(td)
            root = base / "root"
            root.mkdir()
            target = root / "daemon.py"
            target.write_text("print('ok')\n", encoding="utf-8")
            manifest = base / "manifest.json"
            self._write_manifest(root, manifest, "daemon.py")

            report = enforce_manifest(manifest, root=root)
            self.assertTrue(report.ok)

    def test_modified_artifact_fails_closed(self):
        with tempfile.TemporaryDirectory() as td:
            base = Path(td)
            root = base / "root"
            root.mkdir()
            target = root / "daemon.py"
            target.write_text("v1\n", encoding="utf-8")
            manifest = base / "manifest.json"
            self._write_manifest(root, manifest, "daemon.py")
            target.write_text("tampered\n", encoding="utf-8")

            report = verify_manifest(manifest, root=root)
            self.assertFalse(report.ok)
            self.assertEqual(report.failures[0].reason, "sha256_mismatch")
            with self.assertRaises(IntegrityViolation):
                enforce_manifest(manifest, root=root)

    def test_manifest_rejects_parent_escape(self):
        with tempfile.TemporaryDirectory() as td:
            base = Path(td)
            root = base / "root"
            root.mkdir()
            manifest = base / "manifest.json"
            manifest.write_text(
                json.dumps(
                    {
                        "manifest_version": 1,
                        "artifacts": [
                            {
                                "name": "escape",
                                "path": "../outside",
                                "sha256": "0" * 64,
                            }
                        ],
                    }
                ),
                encoding="utf-8",
            )
            with self.assertRaises(IntegrityManifestError):
                verify_manifest(manifest, root=root)

    @unittest.skipUnless(hasattr(os, "symlink"), "symlink support required")
    def test_symlink_target_is_rejected(self):
        with tempfile.TemporaryDirectory() as td:
            base = Path(td)
            root = base / "root"
            root.mkdir()
            real = root / "real.py"
            real.write_text("safe\n", encoding="utf-8")
            link = root / "daemon.py"
            try:
                link.symlink_to(real)
            except (OSError, NotImplementedError):
                self.skipTest("symlink creation unavailable")

            digest = hashlib.sha256(real.read_bytes()).hexdigest()
            manifest = base / "manifest.json"
            manifest.write_text(
                json.dumps(
                    {
                        "manifest_version": 1,
                        "artifacts": [
                            {
                                "name": "daemon",
                                "path": "daemon.py",
                                "sha256": digest,
                            }
                        ],
                    }
                ),
                encoding="utf-8",
            )
            self.assertFalse(verify_manifest(manifest, root=root).ok)


if __name__ == "__main__":
    unittest.main()
