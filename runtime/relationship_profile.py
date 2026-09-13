# Miles Project — Bryan Jones + Miles Mercer | Public technical code
# Relationship/profile retrieval v0.1 | 2026-09-13
"""Small cue-aware person-specific guidance; separate from Core and episodic memory."""
from __future__ import annotations

from dataclasses import dataclass
import json
from pathlib import Path
from typing import Any

DEFAULT_PROFILE = Path.home() / '.miles' / 'relationship_profile.json'
MAX_PROFILE_BYTES = 64 * 1024
MAX_RETRIEVED_ENTRIES = 3
MAX_RETRIEVED_GUIDANCE_CHARS = 1800


class ProfileError(ValueError):
    pass


@dataclass(frozen=True)
class ProfileEntry:
    entry_id: str
    topic: str
    guidance: str
    source: str
    version: str
    cues: tuple[str, ...]
    status: str
    supersedes: str | None = None


@dataclass(frozen=True)
class ProfileRetrieval:
    person: str
    profile_version: str | None
    source: str | None
    entries: tuple[ProfileEntry, ...]
    status: str


def _text(value: Any, name: str, maximum: int) -> str:
    if not isinstance(value, str) or not value.strip() or len(value) > maximum:
        raise ProfileError('invalid ' + name)
    return value.strip()


def _parse_entry(raw: Any) -> ProfileEntry:
    if not isinstance(raw, dict):
        raise ProfileError('invalid profile entry')
    cues = raw.get('cues')
    if not isinstance(cues, list) or not cues or len(cues) > 32:
        raise ProfileError('invalid profile cues')
    parsed_cues = tuple(_text(item, 'profile cue', 128).casefold() for item in cues)
    status = _text(raw.get('status'), 'profile status', 32)
    if status not in ('active', 'superseded'):
        raise ProfileError('invalid profile status')
    supersedes = raw.get('supersedes')
    if supersedes is not None:
        supersedes = _text(supersedes, 'profile supersedes', 128)
    return ProfileEntry(
        entry_id=_text(raw.get('id'), 'profile id', 128),
        topic=_text(raw.get('topic'), 'profile topic', 128),
        guidance=_text(raw.get('guidance'), 'profile guidance', 1200),
        source=_text(raw.get('source'), 'profile source', 256),
        version=_text(raw.get('version'), 'profile entry version', 64),
        cues=parsed_cues,
        status=status,
        supersedes=supersedes,
    )


def load_profile(path: Path, person: str) -> tuple[str, str, tuple[ProfileEntry, ...]]:
    person = _text(person, 'person', 128)
    target = path.expanduser().resolve()
    data = target.read_bytes()
    if len(data) > MAX_PROFILE_BYTES:
        raise ProfileError('profile too large')
    try:
        raw = json.loads(data.decode('utf-8'))
    except (UnicodeDecodeError, json.JSONDecodeError) as exc:
        raise ProfileError('invalid profile json') from exc
    if not isinstance(raw, dict) or raw.get('schema_version') != 1:
        raise ProfileError('unsupported profile schema')
    if _text(raw.get('person'), 'profile person', 128) != person:
        raise ProfileError('profile person mismatch')
    profile_version = _text(raw.get('version'), 'profile version', 64)
    source = _text(raw.get('source'), 'profile source', 256)
    entries_raw = raw.get('entries')
    if not isinstance(entries_raw, list) or len(entries_raw) > 64:
        raise ProfileError('invalid profile entries')
    entries = tuple(_parse_entry(item) for item in entries_raw)
    ids = [entry.entry_id for entry in entries]
    if len(ids) != len(set(ids)):
        raise ProfileError('duplicate profile id')
    known = set(ids)
    for entry in entries:
        if entry.supersedes is not None and entry.supersedes not in known:
            raise ProfileError('unknown superseded profile id')
    return profile_version, source, entries


def retrieve(path: Path, person: str, prompt: str) -> ProfileRetrieval:
    person = _text(person, 'person', 128)
    if not isinstance(prompt, str) or not prompt.strip():
        raise ProfileError('invalid prompt')
    try:
        version, source, entries = load_profile(path, person)
    except FileNotFoundError:
        return ProfileRetrieval(person, None, None, (), 'missing')
    except (OSError, ProfileError):
        return ProfileRetrieval(person, None, None, (), 'invalid')

    folded = prompt.casefold()
    selected: list[ProfileEntry] = []
    guidance_chars = 0
    for entry in entries:
        if entry.status != 'active':
            continue
        if not any(cue in folded for cue in entry.cues):
            continue
        if len(selected) >= MAX_RETRIEVED_ENTRIES:
            break
        if guidance_chars + len(entry.guidance) > MAX_RETRIEVED_GUIDANCE_CHARS:
            break
        selected.append(entry)
        guidance_chars += len(entry.guidance)
    return ProfileRetrieval(
        person=person,
        profile_version=version,
        source=source,
        entries=tuple(selected),
        status='retrieved' if selected else 'not_relevant',
    )


def public_records(result: ProfileRetrieval) -> list[dict[str, str]]:
    """Return only fields intended for model context; omit cue lists and history metadata."""
    return [
        {
            'id': entry.entry_id,
            'topic': entry.topic,
            'guidance': entry.guidance,
            'source': entry.source,
            'version': entry.version,
        }
        for entry in result.entries
    ]
