# Miles Project — Bryan Jones + Miles Mercer | 2026-09-13
import json
from pathlib import Path
import tempfile
import unittest

from runtime.core_compiler import (
    CoreCompileError,
    SUPPORT_HASH_MODE,
    compile_core,
    public_manifest,
)


class CoreCompilerTests(unittest.TestCase):
    def _fixture(self, root: Path, *, omit_section: int | None = None,
                 omit_map: int | None = None, missing_source: int | None = None,
                 escape_source: bool = False, crlf_support: bool = False) -> Path:
        core_dir = root / 'docs' / 'core'
        support_dir = core_dir / 'support'
        support_dir.mkdir(parents=True)

        pieces = ['# Fixture Core\n\n']
        for number in range(1, 9):
            if number == omit_section:
                continue
            pieces.append(f'## {number}. Section {number}\n\nBody {number} — café.\n\n')
        pieces.append('---\n\n## Supporting-source map\n\n')

        for number in range(1, 9):
            if number == omit_map:
                continue
            relative = f'support/s{number}.md'
            if escape_source and number == 1:
                relative = '../../../outside.md'
                (root.parent / 'outside.md').write_text('outside\n', encoding='utf-8')
            elif number != missing_source:
                content = f'support {number}\nsecond line\n'
                if crlf_support:
                    (support_dir / f's{number}.md').write_bytes(content.replace('\n', '\r\n').encode('utf-8'))
                else:
                    (support_dir / f's{number}.md').write_text(content, encoding='utf-8', newline='\n')
            pieces.append(f'- `{relative}` → §{number}\n')

        pieces.append('\n## Compression rule\n\nKeep meaning.\n')
        source = core_dir / 'MILES_CORE_COMPACT.md'
        source.write_text(''.join(pieces), encoding='utf-8', newline='\n')
        return source

    def test_repository_core_compiles_to_eight_sections_only(self):
        compiled = compile_core()
        self.assertEqual([section.number for section in compiled.sections], list(range(1, 9)))
        self.assertNotIn('Supporting-source map', compiled.text)
        self.assertNotIn('Compression rule', compiled.text)
        self.assertNotIn('\n---\n', compiled.text)
        self.assertTrue(all(section.sources for section in compiled.sections))

    def test_manifest_is_deterministic_and_records_hash_mode(self):
        first = public_manifest(compile_core())
        second = public_manifest(compile_core())
        self.assertEqual(first, second)
        self.assertEqual(first['support_hash_mode'], SUPPORT_HASH_MODE)
        self.assertEqual(first['schema_version'], 1)
        json.dumps(first, sort_keys=True)

    def test_byte_offsets_recover_exact_section_text(self):
        compiled = compile_core()
        data = compiled.text.encode('utf-8')
        for section in compiled.sections:
            recovered = data[section.start_byte:section.end_byte].decode('utf-8')
            self.assertEqual(recovered, section.text)
        self.assertEqual(compiled.sections[0].start_byte, 0)
        self.assertEqual(compiled.sections[-1].end_byte + 1, len(data))

    def test_support_hash_is_stable_across_crlf_and_lf(self):
        with tempfile.TemporaryDirectory() as d:
            root = Path(d)
            source = self._fixture(root, crlf_support=True)
            first = compile_core(source, root).sections[0].sources[0].sha256
            support = root / 'docs' / 'core' / 'support' / 's1.md'
            support.write_text('support 1\nsecond line\n', encoding='utf-8', newline='\n')
            second = compile_core(source, root).sections[0].sources[0].sha256
            self.assertEqual(first, second)

    def test_missing_numbered_section_fails_closed(self):
        with tempfile.TemporaryDirectory() as d:
            root = Path(d)
            source = self._fixture(root, omit_section=4)
            with self.assertRaises(CoreCompileError):
                compile_core(source, root)

    def test_unmapped_section_fails_closed(self):
        with tempfile.TemporaryDirectory() as d:
            root = Path(d)
            source = self._fixture(root, omit_map=8)
            with self.assertRaises(CoreCompileError):
                compile_core(source, root)

    def test_missing_mapped_source_fails_closed(self):
        with tempfile.TemporaryDirectory() as d:
            root = Path(d)
            source = self._fixture(root, missing_source=3)
            with self.assertRaises(CoreCompileError):
                compile_core(source, root)

    def test_mapped_source_cannot_escape_repository_root(self):
        with tempfile.TemporaryDirectory() as d:
            root = Path(d) / 'repo'
            root.mkdir()
            source = self._fixture(root, escape_source=True)
            with self.assertRaises(CoreCompileError):
                compile_core(source, root)


if __name__ == '__main__':
    unittest.main()
