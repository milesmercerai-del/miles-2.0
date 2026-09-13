# Miles Project — Bryan Jones + Miles Mercer | Public technical code
# Bootstrap regression tests v0.1 | 2026-09-13
import hashlib
import io
import json
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest
from runtime.bootstrap import BootstrapError, load_core, run


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
