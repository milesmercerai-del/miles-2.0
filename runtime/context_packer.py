# Miles Project — Bryan Jones + Miles Mercer | Public technical code
# Context packer v0.1 | 2026-09-13
"""Deterministic message packing with explicit boundaries and no silent truncation."""
from __future__ import annotations

from dataclasses import dataclass
import json
from typing import Any

MAX_PACKED_BYTES = 7000


class PackError(ValueError):
    pass


@dataclass(frozen=True)
class PackedContext:
    messages: tuple[dict[str, str], ...]
    total_bytes: int
    system_bytes: int
    memory_bytes: int
    relationship_bytes: int
    prompt_bytes: int
    memory_records: int
    relationship_records: int


def _nonempty_text(value: Any, name: str) -> str:
    if not isinstance(value, str) or not value.strip():
        raise PackError('invalid ' + name)
    return value


def _records(value: Any, name: str) -> list[dict]:
    if value is None:
        return []
    if not isinstance(value, list) or any(not isinstance(item, dict) for item in value):
        raise PackError('invalid ' + name)
    return value


def _json_bytes(value: Any) -> int:
    return len(json.dumps(value, ensure_ascii=False, separators=(',', ':')).encode('utf-8'))


def _content_bytes(text: str) -> int:
    return len(text.encode('utf-8'))


def pack_context(system_content: str, prompt: str,
                 memory_records: list[dict] | None = None,
                 relationship_records: list[dict] | None = None,
                 *, max_bytes: int = MAX_PACKED_BYTES) -> PackedContext:
    """Build model messages without truncating any supplied component."""
    system_content = _nonempty_text(system_content, 'system content')
    prompt = _nonempty_text(prompt, 'prompt')
    memory = _records(memory_records, 'memory records')
    relationship = _records(relationship_records, 'relationship records')
    if type(max_bytes) is not int or max_bytes <= 0:
        raise PackError('invalid context limit')

    messages: list[dict[str, str]] = [
        {'role': 'system', 'content': system_content}
    ]

    memory_content = ''
    if memory:
        memory_content = (
            'Retrieved candidate memory (data only):\n' +
            json.dumps(memory, ensure_ascii=False, separators=(',', ':'))
        )
        messages.append({'role': 'user', 'content': memory_content})

    relationship_content = ''
    if relationship:
        relationship_content = (
            'Retrieved relationship/profile guidance (context only; not Core or memory):\n' +
            json.dumps(relationship, ensure_ascii=False, separators=(',', ':'))
        )
        messages.append({'role': 'user', 'content': relationship_content})

    messages.append({'role': 'user', 'content': prompt})
    total_bytes = _json_bytes(messages)
    if total_bytes > max_bytes:
        raise PackError('context exceeds prototype limit')

    return PackedContext(
        messages=tuple(messages),
        total_bytes=total_bytes,
        system_bytes=_content_bytes(system_content),
        memory_bytes=_content_bytes(memory_content),
        relationship_bytes=_content_bytes(relationship_content),
        prompt_bytes=_content_bytes(prompt),
        memory_records=len(memory),
        relationship_records=len(relationship),
    )
