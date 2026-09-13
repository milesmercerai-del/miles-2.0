# Miles Project — Bryan Jones + Miles Mercer | 2026-09-13
import hashlib
import io
import json
from contextlib import redirect_stderr, redirect_stdout
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest
from types import SimpleNamespace
from unittest.mock import patch
from runtime.bootstrap import (BootstrapError, CANONICAL_CORE_SOURCE, Core, load_core,
                               main, run, verify_core_compilation)


class BootstrapTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name)
        self.core_path = self.root / 'core.md'
        self.core_path.write_bytes(b'Synthetic test Core.')
        self.config_path = self.root / 'config.json'
        self.config = dict(schema_version=1, adapter='mock', core_path='core.md',
                           core_sha256=hashlib.sha256(self.core_path.read_bytes()).hexdigest(),
                           core_source='synthetic fixture', core_version='test v1')
        self.save()

    def save(self):
        self.config_path.write_text(json.dumps(self.config), encoding='utf-8')

    def test_loads_verified_bytes_and_provenance(self):
        core = load_core(self.config_path)
        self.assertEqual(core.text, 'Synthetic test Core.')
        self.assertEqual(core.source, 'synthetic fixture')

    def test_changed_core_fails_before_loop(self):
        self.core_path.write_text('Altered Core')
        with self.assertRaises(BootstrapError):
            load_core(self.config_path)

    def test_rejects_bad_schema_and_live_adapter(self):
        for field, value in [('adapter', 'hardware'), ('schema_version', True),
                             ('core_source', ''), ('core_sha256', 'invalid')]:
            with self.subTest(field=field):
                old = self.config[field]
                self.config[field] = value
                self.save()
                with self.assertRaises(BootstrapError):
                    load_core(self.config_path)
                self.config[field] = old

    def test_loop_quit_and_no_private_content_in_log(self):
        output, log = io.StringIO(), io.StringIO()
        run(load_core(self.config_path), io.StringIO('private input\n/quit\nignored\n'), output, log)
        self.assertEqual(output.getvalue().count('[MOCK'), 1)
        self.assertNotIn('private input', log.getvalue())
        self.assertNotIn('Synthetic test Core', log.getvalue())
        self.assertIn('shutdown', log.getvalue())

    def test_long_input_is_drained_then_next_turn_works(self):
        output, log = io.StringIO(), io.StringIO()
        run(load_core(self.config_path), io.StringIO('x'*9000+'\nhello\n'), output, log)
        self.assertEqual(output.getvalue().count('[MOCK'), 1)
        self.assertIn('input_rejected', log.getvalue())

    def test_cli_invalid_config_has_nonzero_exit_and_no_traceback(self):
        self.config_path.write_text('{broken')
        result = subprocess.run([sys.executable, '-m', 'runtime.bootstrap', '--config',
                                 str(self.config_path)], capture_output=True, text=True)
        self.assertEqual(result.returncode, 2)
        self.assertNotIn('Traceback', result.stderr)
        self.assertNotIn('boot_ready', result.stderr)

    def test_default_cli_works_from_other_directory(self):
        script = Path(__file__).resolve().parents[2] / 'runtime/bootstrap.py'
        result = subprocess.run([sys.executable, str(script), '--check'], cwd=self.root,
                                 capture_output=True, text=True)
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertIn('validation_passed', result.stdout)
        self.assertIn('compiled_core_sha256', result.stdout)

    def test_synthetic_core_does_not_invoke_miles_compiler(self):
        core = load_core(self.config_path)
        with patch('runtime.bootstrap._compile_canonical_core') as compiler:
            self.assertIsNone(verify_core_compilation(core))
        compiler.assert_not_called()

    def test_canonical_core_requires_matching_compilation_provenance(self):
        digest = 'a' * 64
        core = Core('Canonical fixture', digest, CANONICAL_CORE_SOURCE, 'test')
        good = SimpleNamespace(source_path=CANONICAL_CORE_SOURCE,
                               source_sha256=digest, sha256='b' * 64)
        with patch('runtime.bootstrap._compile_canonical_core', return_value=good):
            self.assertEqual(verify_core_compilation(core), 'b' * 64)

        bad = SimpleNamespace(source_path=CANONICAL_CORE_SOURCE,
                              source_sha256='c' * 64, sha256='d' * 64)
        with patch('runtime.bootstrap._compile_canonical_core', return_value=bad):
            with self.assertRaises(BootstrapError):
                verify_core_compilation(core)

    def test_real_check_reports_compiled_digest_without_core_text(self):
        out, err = io.StringIO(), io.StringIO()
        with redirect_stdout(out), redirect_stderr(err):
            code = main(['--check'])
        self.assertEqual(code, 0, err.getvalue())
        event = json.loads(out.getvalue())
        self.assertEqual(event['event'], 'validation_passed')
        self.assertEqual(event['core_sha256'],
                         '8298ad9605666593cd23aea2e3eca98ade90dcb51cf1bb13fc4dea32b79e2972')
        self.assertEqual(event['compiled_core_sha256'],
                         '40b29fd8e7e1297bce6c95372dec23c4cb8178a2a7b3f256e1ca4bca255c56c3')
        self.assertNotIn('Useful truth over comfortable agreement', out.getvalue())


if __name__ == '__main__':
    unittest.main()
