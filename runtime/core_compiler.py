# Miles Project — Bryan Jones + Miles Mercer | Public technical code
# Core compiler v0.1 | 2026-09-13
"""Read-only compact-Core compiler with deterministic provenance mapping."""
from __future__ import annotations

import argparse
from dataclasses import dataclass
import hashlib
import json
from pathlib import Path
import re
from typing import Any

REPO_ROOT = Path(__file__).resolve().parents[1]
DEFAULT_SOURCE = REPO_ROOT / 'docs' / 'core' / 'MILES_CORE_COMPACT.md'
MAX_CORE_BYTES = 65536
MAX_SUPPORT_BYTES = 262144
SUPPORT_HASH_MODE = 'utf8-lf-sha256'
_SECTION_RE = re.compile(r'^## ([1-8])\. ([^\r\n]+)$', re.MULTILINE)
_MAP_RE = re.compile(
    r'^- `([^`\r\n]+)` → §([1-8])(?: ([^\r\n]+))?$',
    re.MULTILINE,
)


class CoreCompileError(ValueError):
    """Canonical Core or supporting-source provenance is invalid."""


@dataclass(frozen=True)
class SourceRef:
    path: str
    sha256: str
    note: str


@dataclass(frozen=True)
class CompiledSection:
    number: int
    title: str
    text: str
    start_byte: int
    end_byte: int
    sources: tuple[SourceRef, ...]


@dataclass(frozen=True)
class CoreCompilation:
    text: str
    sha256: str
    source_sha256: str
    source_path: str
    sections: tuple[CompiledSection, ...]


def _read_bounded(path: Path, maximum: int) -> bytes:
    with path.open('rb') as stream:
        data = stream.read(maximum + 1)
    if len(data) > maximum:
        raise CoreCompileError('source exceeds size limit')
    return data


def _inside(root: Path, candidate: Path) -> bool:
    try:
        candidate.relative_to(root)
    except ValueError:
        return False
    return True


def _sha256(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def _support_sha256(data: bytes) -> str:
    text = data.decode('utf-8')
    normalized = text.replace('\r\n', '\n').replace('\r', '\n')
    return _sha256(normalized.encode('utf-8'))


def _parse_sections(text: str) -> list[tuple[int, str, str]]:
    map_marker = '\n## Supporting-source map\n'
    map_start = text.find(map_marker)
    if map_start < 0:
        raise CoreCompileError('supporting-source map missing')
    section_matches = list(_SECTION_RE.finditer(text[:map_start]))
    if [int(match.group(1)) for match in section_matches] != list(range(1, 9)):
        raise CoreCompileError('Core must contain sections 1 through 8 exactly once and in order')

    final_separator = text.rfind('\n\n---\n', section_matches[-1].start(), map_start)
    if final_separator < 0:
        raise CoreCompileError('Core/source-map separator missing')

    parsed: list[tuple[int, str, str]] = []
    for index, match in enumerate(section_matches):
        if index + 1 < len(section_matches):
            end = section_matches[index + 1].start()
        else:
            end = final_separator
        block = text[match.start():end].rstrip()
        if not block.strip():
            raise CoreCompileError('Core section is empty')
        parsed.append((int(match.group(1)), match.group(2).strip(), block))
    return parsed


def _parse_source_map(text: str) -> dict[int, list[tuple[str, str]]]:
    marker = '## Supporting-source map\n'
    start = text.find(marker)
    if start < 0:
        raise CoreCompileError('supporting-source map missing')
    compression = text.find('\n## Compression rule\n', start)
    if compression < 0:
        raise CoreCompileError('compression rule missing')
    block = text[start:compression]
    matches = list(_MAP_RE.finditer(block))
    if not matches:
        raise CoreCompileError('supporting-source map is empty')

    mapped: dict[int, list[tuple[str, str]]] = {number: [] for number in range(1, 9)}
    seen: set[tuple[int, str]] = set()
    for match in matches:
        path = match.group(1).strip()
        number = int(match.group(2))
        note = (match.group(3) or '').strip()
        key = (number, path)
        if key in seen:
            raise CoreCompileError('duplicate source-map entry')
        seen.add(key)
        mapped[number].append((path, note))
    if any(not mapped[number] for number in range(1, 9)):
        raise CoreCompileError('every Core section requires at least one mapped source')
    return mapped


def _resolve_sources(source_path: Path, root: Path,
                     mapped: dict[int, list[tuple[str, str]]]) -> dict[int, tuple[SourceRef, ...]]:
    resolved: dict[int, tuple[SourceRef, ...]] = {}
    for number in range(1, 9):
        refs: list[SourceRef] = []
        for relative, note in mapped[number]:
            candidate = (source_path.parent / relative).resolve()
            if not _inside(root, candidate):
                raise CoreCompileError('mapped source escapes repository root')
            if not candidate.is_file():
                raise CoreCompileError('mapped source missing')
            data = _read_bounded(candidate, MAX_SUPPORT_BYTES)
            refs.append(SourceRef(
                path=candidate.relative_to(root).as_posix(),
                sha256=_support_sha256(data),
                note=note,
            ))
        resolved[number] = tuple(refs)
    return resolved


def compile_core(source_path: Path = DEFAULT_SOURCE, root: Path = REPO_ROOT) -> CoreCompilation:
    """Compile the eight canonical sections without rewriting their wording."""
    root = root.resolve()
    source_path = source_path.resolve()
    if not _inside(root, source_path):
        raise CoreCompileError('Core source escapes repository root')
    source_data = _read_bounded(source_path, MAX_CORE_BYTES)
    text = source_data.decode('utf-8')
    sections = _parse_sections(text)
    mapped = _parse_source_map(text)
    sources = _resolve_sources(source_path, root, mapped)

    compiled_text = '\n\n'.join(block for _, _, block in sections) + '\n'
    compiled: list[CompiledSection] = []
    cursor = 0
    for number, title, block in sections:
        start_byte = cursor
        end_byte = start_byte + len(block.encode('utf-8'))
        compiled.append(CompiledSection(
            number=number,
            title=title,
            text=block,
            start_byte=start_byte,
            end_byte=end_byte,
            sources=sources[number],
        ))
        cursor = end_byte + (2 if number < 8 else 1)

    compiled_data = compiled_text.encode('utf-8')
    if cursor != len(compiled_data):
        raise CoreCompileError('compiled byte accounting mismatch')
    return CoreCompilation(
        text=compiled_text,
        sha256=_sha256(compiled_data),
        source_sha256=_sha256(source_data),
        source_path=source_path.relative_to(root).as_posix(),
        sections=tuple(compiled),
    )


def public_manifest(compilation: CoreCompilation) -> dict[str, Any]:
    return {
        'schema_version': 1,
        'support_hash_mode': SUPPORT_HASH_MODE,
        'source_path': compilation.source_path,
        'source_sha256': compilation.source_sha256,
        'compiled_sha256': compilation.sha256,
        'compiled_bytes': len(compilation.text.encode('utf-8')),
        'sections': [
            {
                'number': section.number,
                'title': section.title,
                'start_byte': section.start_byte,
                'end_byte': section.end_byte,
                'sources': [
                    {'path': ref.path, 'sha256': ref.sha256, 'note': ref.note}
                    for ref in section.sources
                ],
            }
            for section in compilation.sections
        ],
    }


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--source', type=Path, default=DEFAULT_SOURCE)
    parser.add_argument('--root', type=Path, default=REPO_ROOT)
    args = parser.parse_args(argv)
    try:
        compilation = compile_core(args.source, args.root)
    except (OSError, UnicodeError, CoreCompileError):
        print(json.dumps({'event': 'core_compile_failed'}, sort_keys=True))
        return 2
    print(json.dumps(public_manifest(compilation), ensure_ascii=False, sort_keys=True))
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
