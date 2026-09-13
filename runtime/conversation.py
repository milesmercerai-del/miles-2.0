# Miles Project — Bryan Jones + Miles Mercer | Public technical code
# Continuous local conversation v0.1 | 2026-09-13
"""Bounded in-memory local conversation using the verified Miles chat path."""

from __future__ import annotations

import argparse
import json
from pathlib import Path
import sqlite3
import sys
import urllib.error
from uuid import uuid4

from runtime.bootstrap import event, load_core
from runtime.chat import CONFIG, MODEL, ChatError, _journal_write, assemble, generate
from runtime.context_packer import MAX_PACKED_BYTES
from runtime.memory import DEFAULT_DB, recall
from runtime.relationship_profile import DEFAULT_PROFILE, public_records, retrieve
from runtime.runtime_journal import DEFAULT_JOURNAL, RuntimeJournal


MAX_HISTORY_MESSAGES = 8
MAX_HISTORY_BYTES = 2400
QUIT_COMMANDS = {'quit', 'exit', '/quit', '/exit'}


def _message_bytes(messages: list[dict[str, str]]) -> int:
    return len(
        json.dumps(
            messages,
            ensure_ascii=False,
            separators=(',', ':'),
        ).encode('utf-8')
    )


def _drop_oldest_turn(history: list[dict[str, str]]) -> list[dict[str, str]]:
    if not history:
        return []

    remaining = list(history[1:])
    if history[0].get('role') == 'user' and remaining:
        if remaining[0].get('role') == 'assistant':
            remaining = remaining[1:]

    return remaining


def bounded_history(
    history: list[dict[str, str]],
    *,
    max_messages: int = MAX_HISTORY_MESSAGES,
    max_bytes: int = MAX_HISTORY_BYTES,
) -> list[dict[str, str]]:
    """Keep only recent complete messages; never truncate message text."""

    if type(max_messages) is not int or max_messages < 0:
        raise ChatError('invalid history message limit')
    if type(max_bytes) is not int or max_bytes < 0:
        raise ChatError('invalid history byte limit')

    clean: list[dict[str, str]] = []

    for item in history:
        if not isinstance(item, dict):
            raise ChatError('invalid conversation history')

        role = item.get('role')
        content = item.get('content')

        if role not in {'user', 'assistant'}:
            raise ChatError('invalid conversation history role')
        if not isinstance(content, str) or not content.strip():
            raise ChatError('invalid conversation history content')

        clean.append({'role': role, 'content': content})

    while len(clean) > max_messages:
        clean = _drop_oldest_turn(clean)

    while clean and _message_bytes(clean) > max_bytes:
        clean = _drop_oldest_turn(clean)

    return clean


def assemble_turn(
    prompt: str,
    core,
    records: list[dict],
    relationship_records: list[dict] | None,
    history: list[dict[str, str]],
) -> dict:
    """Build one request with bounded prior user/assistant turns."""

    payload = assemble(prompt, core, records, relationship_records)

    base_messages = list(payload['messages'])
    current_prompt = base_messages[-1]
    prefix = base_messages[:-1]

    retained = bounded_history(history)
    messages = prefix + retained + [current_prompt]

    while retained and _message_bytes(messages) > MAX_PACKED_BYTES:
        retained = _drop_oldest_turn(retained)
        messages = prefix + retained + [current_prompt]

    if _message_bytes(messages) > MAX_PACKED_BYTES:
        raise ChatError('context exceeds prototype limit')

    result = dict(payload)
    result['messages'] = messages
    return result


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        '--memory-key',
        help='explicitly include the latest record for this key on every turn',
    )
    parser.add_argument('--db', type=Path, default=DEFAULT_DB)
    parser.add_argument(
        '--profile',
        type=Path,
        default=DEFAULT_PROFILE,
        help='local relationship/profile JSON; unavailable profiles are ignored',
    )
    parser.add_argument(
        '--profile-person',
        default='operator',
        help='person identifier expected inside the local profile',
    )
    parser.add_argument(
        '--journal',
        type=Path,
        default=DEFAULT_JOURNAL,
        help='privacy-safe local runtime journal',
    )
    args = parser.parse_args(argv)

    session_id = uuid4().hex
    journal: RuntimeJournal | None = RuntimeJournal(args.journal)
    core = None

    try:
        core = load_core(CONFIG)

        records = (
            recall(args.db, args.memory_key)
            if args.memory_key is not None
            else []
        )

        if args.memory_key is not None and not records:
            _journal_write(
                journal,
                session_id=session_id,
                event='failure',
                component='memory',
                status='failed',
                code='memory_key_not_found',
                core_sha256=core.sha256,
            )
            event(sys.stderr, 'chat_failed', reason='memory_key_not_found')
            return 2

        journal = _journal_write(
            journal,
            session_id=session_id,
            event='startup',
            component='conversation',
            status='ok',
            code='conversation_started',
            core_sha256=core.sha256,
        )

        history: list[dict[str, str]] = []

        print('Miles local conversation. Type quit or /quit to exit.')

        while True:
            try:
                prompt = input('You> ')
            except EOFError:
                break

            prompt = prompt.strip()

            if not prompt:
                continue

            if prompt.lower() in QUIT_COMMANDS:
                break

            relationship = retrieve(
                args.profile,
                args.profile_person,
                prompt,
            )
            relationship_records = public_records(relationship)

            payload = assemble_turn(
                prompt,
                core,
                records,
                relationship_records,
                history,
            )

            journal = _journal_write(
                journal,
                session_id=session_id,
                event='model_request',
                component='model',
                status='info',
                code='local_request',
                core_sha256=core.sha256,
                model=MODEL,
                memory_records=len(records),
                relationship_records=len(relationship_records),
            )

            event(
                sys.stderr,
                'local_request',
                model=MODEL,
                core_sha256=core.sha256,
                memory_records=len(records),
                relationship_profile_status=relationship.status,
                relationship_records=len(relationship_records),
                conversation_history=len(history),
            )

            answer = generate(payload)

            print(f'Miles> {answer}')

            history.extend([
                {'role': 'user', 'content': prompt},
                {'role': 'assistant', 'content': answer},
            ])
            history = bounded_history(history)

            journal = _journal_write(
                journal,
                session_id=session_id,
                event='model_response',
                component='model',
                status='ok',
                code='local_response',
                core_sha256=core.sha256,
                model=MODEL,
            )

        _journal_write(
            journal,
            session_id=session_id,
            event='shutdown',
            component='conversation',
            status='ok',
            code='conversation_complete',
            core_sha256=core.sha256,
        )

    except KeyboardInterrupt:
        print()
        _journal_write(
            journal,
            session_id=session_id,
            event='failure',
            component='conversation',
            status='degraded',
            code='conversation_cancelled',
            core_sha256=core.sha256 if core is not None else None,
        )
        event(sys.stderr, 'chat_cancelled')
        return 130

    except (OSError, ValueError, sqlite3.Error, urllib.error.URLError):
        _journal_write(
            journal,
            session_id=session_id,
            event='failure',
            component='conversation',
            status='failed',
            code='core_memory_or_local_model_error',
            core_sha256=core.sha256 if core is not None else None,
        )
        event(
            sys.stderr,
            'chat_failed',
            reason='core_memory_or_local_model_error',
        )
        return 2

    return 0


if __name__ == '__main__':
    raise SystemExit(main())
