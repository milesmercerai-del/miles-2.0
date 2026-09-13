# Miles Project — Bryan Jones + Miles Mercer | Public technical code
# Bootstrap v0.3 | 2026-09-13
"""Read-only PC harness with verified Core provenance and privacy-safe diagnostics."""
from __future__ import annotations

import argparse
from dataclasses import dataclass
import hashlib
import json
from pathlib import Path
import sys
from typing import TextIO
from uuid import uuid4

from runtime.runtime_journal import DEFAULT_JOURNAL, JournalError, RuntimeJournal, build_record

CANONICAL_CORE_SOURCE = 'docs/core/MILES_CORE_COMPACT.md'


class BootstrapError(ValueError):
    """Invalid configuration or Core provenance."""


@dataclass(frozen=True)
class Core:
    text: str
    sha256: str
    source: str
    version: str


def read_bounded(path: Path, maximum: int) -> bytes:
    with path.open('rb') as stream:
        data = stream.read(maximum + 1)
    if len(data) > maximum:
        raise BootstrapError('file exceeds size limit')
    return data


def load_core(config_path: Path) -> Core:
    config = json.loads(read_bounded(config_path, 16384).decode('utf-8'))
    required = {'schema_version', 'adapter', 'core_path', 'core_sha256',
                'core_source', 'core_version'}
    if not isinstance(config, dict) or set(config) != required:
        raise BootstrapError('configuration fields do not match schema')
    if type(config['schema_version']) is not int or config['schema_version'] != 1:
        raise BootstrapError('unsupported schema version')
    if config['adapter'] != 'mock':
        raise BootstrapError('only the mock adapter is implemented')
    for field in required - {'schema_version'}:
        if not isinstance(config[field], str) or not config[field].strip():
            raise BootstrapError('configuration values must be nonempty strings')
    expected = config['core_sha256']
    if len(expected) != 64 or any(c not in '0123456789abcdef' for c in expected):
        raise BootstrapError('invalid Core digest')
    data = read_bounded(config_path.parent / config['core_path'], 65536)
    digest = hashlib.sha256(data).hexdigest()
    if digest != expected:
        raise BootstrapError('Core digest mismatch')
    core_text = data.decode('utf-8')
    if not core_text.strip():
        raise BootstrapError('Core is empty')
    return Core(core_text, digest, config['core_source'], config['core_version'])


def _compile_canonical_core():
    # Keep direct-script execution working when the repository root is not cwd.
    try:
        from runtime.core_compiler import compile_core
    except ModuleNotFoundError:
        from core_compiler import compile_core
    return compile_core()


def verify_core_compilation(core: Core) -> str | None:
    """Fail closed on canonical Miles Core provenance; leave generic fixtures generic."""
    if core.source != CANONICAL_CORE_SOURCE:
        return None
    compilation = _compile_canonical_core()
    if compilation.source_path != core.source:
        raise BootstrapError('compiled Core source mismatch')
    if compilation.source_sha256 != core.sha256:
        raise BootstrapError('compiled Core provenance mismatch')
    return compilation.sha256


class MockModel:
    """Deterministic transport probe, explicitly not an LLM or identity test."""
    def respond(self, core: Core, user_text: str) -> str:
        return '[MOCK — no inference] Core loaded; received %d characters.' % len(user_text)


def event(stream: TextIO, name: str, **fields: object) -> None:
    print(json.dumps({'event': name, **fields}, sort_keys=True), file=stream)


def _journal_write(journal: RuntimeJournal | None, log: TextIO, **fields: object) -> RuntimeJournal | None:
    """Best-effort diagnostics: journal failure must not become runtime failure."""
    if journal is None:
        return None
    try:
        journal.append(build_record(**fields))
    except (OSError, JournalError):
        # Never include a path, exception string, prompt, or Core text here.
        event(log, 'journal_unavailable')
        return None
    return journal


def run(core: Core, source: TextIO, output: TextIO, log: TextIO,
        *, journal: RuntimeJournal | None = None, session_id: str | None = None) -> int:
    model = MockModel()
    session_id = session_id or uuid4().hex
    journal = _journal_write(
        journal, log, session_id=session_id, event='startup', component='bootstrap',
        status='ok', code='mock_boot_ready', core_sha256=core.sha256,
    )
    event(log, 'boot_ready', mode='mock', core_sha256=core.sha256,
          hardware='unavailable', persistence='unavailable', inference=False)
    print('Miles PC harness — MOCK ONLY. Type /quit to exit.', file=output)
    try:
        while True:
            line = source.readline(4098)
            if not line:
                break
            if len(line) > 4096:
                event(log, 'input_rejected', reason='too_long')
                # Drain the rest of this line without accepting fragments as turns.
                while line and not line.endswith('\n'):
                    line = source.readline(4098)
                continue
            line = line.rstrip('\r\n')
            if line.strip() == '/quit':
                break
            if not line.strip():
                continue
            print(model.respond(core, line), file=output)
            event(log, 'turn_completed', adapter='mock')
    except KeyboardInterrupt:
        pass
    finally:
        _journal_write(
            journal, log, session_id=session_id, event='shutdown', component='bootstrap',
            status='ok', code='clean_shutdown', core_sha256=core.sha256,
        )
        event(log, 'shutdown', clean=True)
    return 0


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--config', type=Path,
                        default=Path(__file__).resolve().parents[1] / 'config/bootstrap.mock.json')
    parser.add_argument('--check', action='store_true', help='validate only; do not open text loop')
    parser.add_argument('--journal', type=Path, default=DEFAULT_JOURNAL,
                        help='privacy-safe local runtime journal')
    args = parser.parse_args(argv)
    session_id = uuid4().hex
    journal: RuntimeJournal | None = RuntimeJournal(args.journal)
    try:
        core = load_core(args.config)
        compiled_sha256 = verify_core_compilation(core)
    except (OSError, ValueError, UnicodeError):
        _journal_write(
            journal, sys.stderr, session_id=session_id, event='failure', component='bootstrap',
            status='failed', code='config_or_core_invalid',
        )
        # Do not copy paths, Core contents, or malformed configuration into logs.
        event(sys.stderr, 'boot_failed', reason='config_or_core_invalid')
        return 2
    if args.check:
        _journal_write(
            journal, sys.stderr, session_id=session_id, event='service_health',
            component='bootstrap', status='ok', code='validation_passed',
            core_sha256=core.sha256,
        )
        fields = {'mode': 'mock', 'core_sha256': core.sha256}
        if compiled_sha256 is not None:
            fields['compiled_core_sha256'] = compiled_sha256
        event(sys.stdout, 'validation_passed', **fields)
        return 0
    return run(core, sys.stdin, sys.stdout, sys.stderr,
               journal=journal, session_id=session_id)


if __name__ == '__main__':
    raise SystemExit(main())
