# Miles Project — Bryan Jones + Miles Mercer | Public technical code
# Runtime journal v0.1 | 2026-09-13
"""Privacy-safe append-only runtime diagnostics that survive process restarts."""
from __future__ import annotations

from dataclasses import asdict, dataclass
from datetime import datetime, timezone
import json
import os
from pathlib import Path
import re
import stat
from typing import Any
from uuid import uuid4

DEFAULT_JOURNAL = Path.home() / '.miles' / 'runtime-journal.jsonl'
MAX_LINE_BYTES = 8192
MAX_TAIL_BYTES = 131072
MAX_TAIL_RECORDS = 200

EVENTS = {
    'startup', 'shutdown', 'model_request', 'model_response',
    'memory_retrieval', 'relationship_retrieval', 'service_health', 'failure',
}
COMPONENTS = {
    'bootstrap', 'chat', 'model', 'memory', 'relationship', 'runtime',
}
STATUSES = {'ok', 'info', 'degraded', 'failed'}
_CODE_RE = re.compile(r'^[a-z0-9][a-z0-9_.-]{0,63}$')
_MODEL_RE = re.compile(r'^[A-Za-z0-9][A-Za-z0-9_.:/+-]{0,127}$')


class JournalError(ValueError):
    """Runtime-journal record or storage is invalid."""


@dataclass(frozen=True)
class JournalRecord:
    event_id: str
    recorded_at: str
    session_id: str
    event: str
    component: str
    status: str
    code: str
    core_sha256: str | None = None
    model: str | None = None
    memory_records: int | None = None
    relationship_records: int | None = None
    duration_ms: int | None = None

    def public_dict(self) -> dict[str, Any]:
        return {key: value for key, value in asdict(self).items() if value is not None}


def _safe_token(value: Any, name: str, pattern: re.Pattern[str]) -> str:
    if not isinstance(value, str) or pattern.fullmatch(value) is None:
        raise JournalError('invalid ' + name)
    return value


def _digest(value: Any, name: str) -> str:
    if value is None:
        return value
    if (
        not isinstance(value, str)
        or len(value) != 64
        or any(character not in '0123456789abcdef' for character in value)
    ):
        raise JournalError('invalid ' + name)
    return value


def _count(value: Any, name: str) -> int | None:
    if value is None:
        return None
    if type(value) is not int or value < 0 or value > 1_000_000:
        raise JournalError('invalid ' + name)
    return value


def _duration(value: Any) -> int | None:
    if value is None:
        return None
    if type(value) is not int or value < 0 or value > 86_400_000:
        raise JournalError('invalid duration')
    return value


def _timestamp(when: datetime | None) -> str:
    moment = when or datetime.now(timezone.utc)
    if not isinstance(moment, datetime):
        raise JournalError('invalid timestamp')
    if moment.tzinfo is None:
        moment = moment.replace(tzinfo=timezone.utc)
    return moment.astimezone(timezone.utc).isoformat().replace('+00:00', 'Z')


def build_record(
    *,
    session_id: str,
    event: str,
    component: str,
    status: str,
    code: str,
    core_sha256: str | None = None,
    model: str | None = None,
    memory_records: int | None = None,
    relationship_records: int | None = None,
    duration_ms: int | None = None,
    recorded_at: datetime | None = None,
) -> JournalRecord:
    """Build a fixed-schema diagnostic record; arbitrary text is not accepted."""
    session_id = _safe_token(session_id, 'session id', _CODE_RE)
    if event not in EVENTS:
        raise JournalError('invalid event')
    if component not in COMPONENTS:
        raise JournalError('invalid component')
    if status not in STATUSES:
        raise JournalError('invalid status')
    code = _safe_token(code, 'code', _CODE_RE)
    core_sha256 = _digest(core_sha256, 'Core digest')
    if model is not None:
        model = _safe_token(model, 'model', _MODEL_RE)
    return JournalRecord(
        event_id=str(uuid4()),
        recorded_at=_timestamp(recorded_at),
        session_id=session_id,
        event=event,
        component=component,
        status=status,
        code=code,
        core_sha256=core_sha256,
        model=model,
        memory_records=_count(memory_records, 'memory record count'),
        relationship_records=_count(relationship_records, 'relationship record count'),
        duration_ms=_duration(duration_ms),
    )


def _validate_record(record: JournalRecord) -> None:
    if not isinstance(record, JournalRecord):
        raise JournalError('invalid journal record')
    _safe_token(record.session_id, 'session id', _CODE_RE)
    if record.event not in EVENTS:
        raise JournalError('invalid event')
    if record.component not in COMPONENTS:
        raise JournalError('invalid component')
    if record.status not in STATUSES:
        raise JournalError('invalid status')
    _safe_token(record.code, 'code', _CODE_RE)
    _digest(record.core_sha256, 'Core digest')
    if record.model is not None:
        _safe_token(record.model, 'model', _MODEL_RE)
    _count(record.memory_records, 'memory record count')
    _count(record.relationship_records, 'relationship record count')
    _duration(record.duration_ms)
    if not isinstance(record.event_id, str) or not record.event_id:
        raise JournalError('invalid event id')
    if not isinstance(record.recorded_at, str) or not record.recorded_at.endswith('Z'):
        raise JournalError('invalid recorded timestamp')


def _decode_record(raw: bytes) -> JournalRecord:
    if len(raw) > MAX_LINE_BYTES:
        raise JournalError('journal record exceeds line limit')
    try:
        value = json.loads(raw.decode('utf-8'))
    except (UnicodeError, json.JSONDecodeError) as exc:
        raise JournalError('invalid journal JSON') from exc
    allowed = {
        'event_id', 'recorded_at', 'session_id', 'event', 'component', 'status',
        'code', 'core_sha256', 'model', 'memory_records',
        'relationship_records', 'duration_ms',
    }
    required = {
        'event_id', 'recorded_at', 'session_id', 'event', 'component', 'status', 'code',
    }
    if not isinstance(value, dict) or not required.issubset(value) or set(value) - allowed:
        raise JournalError('journal fields do not match schema')
    record = JournalRecord(
        event_id=value['event_id'],
        recorded_at=value['recorded_at'],
        session_id=value['session_id'],
        event=value['event'],
        component=value['component'],
        status=value['status'],
        code=value['code'],
        core_sha256=value.get('core_sha256'),
        model=value.get('model'),
        memory_records=value.get('memory_records'),
        relationship_records=value.get('relationship_records'),
        duration_ms=value.get('duration_ms'),
    )
    _validate_record(record)
    return record


class RuntimeJournal:
    """Append fixed-schema diagnostics and read only a bounded recent tail."""

    def __init__(self, path: str | Path = DEFAULT_JOURNAL, *, fsync: bool = True) -> None:
        self.path = Path(path)
        self.fsync = fsync

    def _prepare_parent(self) -> None:
        parent = self.path.parent
        parent.mkdir(parents=True, mode=0o700, exist_ok=True)
        if os.name == 'posix':
            mode = stat.S_IMODE(parent.stat().st_mode)
            if mode & 0o077:
                raise JournalError('journal directory is not private')

    def _open_append(self) -> int:
        self._prepare_parent()
        if self.path.exists() and self.path.is_symlink():
            raise JournalError('journal must not be a symlink')
        flags = (
            os.O_WRONLY | os.O_CREAT | os.O_APPEND
            | getattr(os, 'O_CLOEXEC', 0)
            | getattr(os, 'O_NOFOLLOW', 0)
            | getattr(os, 'O_BINARY', 0)
        )
        try:
            fd = os.open(self.path, flags, 0o600)
        except OSError as exc:
            raise JournalError('unable to open journal') from exc
        try:
            info = os.fstat(fd)
            if not stat.S_ISREG(info.st_mode):
                raise JournalError('journal must be a regular file')
            if os.name == 'posix' and stat.S_IMODE(info.st_mode) & 0o077:
                raise JournalError('journal file is not private')
            return fd
        except Exception:
            os.close(fd)
            raise

    def verify_ready(self) -> None:
        fd = self._open_append()
        os.close(fd)

    def append(self, record: JournalRecord) -> None:
        _validate_record(record)
        payload = (
            json.dumps(record.public_dict(), sort_keys=True, separators=(',', ':'),
                       ensure_ascii=False) + '\n'
        ).encode('utf-8')
        if len(payload) > MAX_LINE_BYTES:
            raise JournalError('journal record exceeds line limit')
        fd = self._open_append()
        try:
            view = memoryview(payload)
            while view:
                written = os.write(fd, view)
                if written <= 0:
                    raise JournalError('journal short write')
                view = view[written:]
            if self.fsync:
                os.fsync(fd)
        finally:
            os.close(fd)

    def tail(self, limit: int = 20) -> tuple[JournalRecord, ...]:
        if type(limit) is not int or limit < 1 or limit > MAX_TAIL_RECORDS:
            raise JournalError('invalid tail limit')
        if not self.path.exists():
            return ()
        if self.path.is_symlink() or not self.path.is_file():
            raise JournalError('journal is not a regular file')
        size = self.path.stat().st_size
        with self.path.open('rb') as stream:
            start = max(0, size - MAX_TAIL_BYTES)
            stream.seek(start)
            data = stream.read(MAX_TAIL_BYTES + 1)
        if len(data) > MAX_TAIL_BYTES:
            data = data[-MAX_TAIL_BYTES:]
            start = max(1, start)
        lines = data.splitlines()
        if start > 0 and lines:
            lines = lines[1:]
        if not lines:
            return ()
        selected = lines[-limit:]
        return tuple(_decode_record(line) for line in selected)
