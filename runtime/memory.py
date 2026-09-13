# Miles Project — Bryan Jones + Miles Mercer | Public technical code
# Local memory prototype v0.2 | 2026-09-13
"""Operator-driven, append-only local records; no inference or action execution."""
from __future__ import annotations

import argparse
from contextlib import closing
from datetime import datetime, timezone
import json
from pathlib import Path
import sqlite3
import sys

DEFAULT_DB = Path.home() / '.miles' / 'memory.sqlite3'
SCHEMA = '''CREATE TABLE memories (
    id INTEGER PRIMARY KEY,
    key TEXT NOT NULL,
    text TEXT NOT NULL,
    source TEXT NOT NULL,
    recorded_at TEXT NOT NULL,
    instance TEXT NOT NULL,
    evidence TEXT NOT NULL CHECK(evidence = 'operator_supplied'),
    adoption TEXT NOT NULL CHECK(adoption = 'candidate'),
    supersedes INTEGER REFERENCES memories(id)
)'''
MEMBERSHIP_SCHEMA = '''CREATE TABLE memory_membership_events (
    id INTEGER PRIMARY KEY,
    key TEXT NOT NULL,
    action TEXT NOT NULL CHECK(action IN ('archive','restore')),
    recorded_at TEXT NOT NULL,
    source TEXT NOT NULL
)'''
MEMORY_COLUMNS = ['id', 'key', 'text', 'source', 'recorded_at', 'instance',
                  'evidence', 'adoption', 'supersedes']
MEMBERSHIP_COLUMNS = ['id', 'key', 'action', 'recorded_at', 'source']


class MemoryError(ValueError):
    pass


def validate(value: str, name: str, maximum: int) -> None:
    if not isinstance(value, str) or not value.strip() or len(value) > maximum:
        raise MemoryError('invalid ' + name)


def _table_columns(db: sqlite3.Connection, table: str) -> list[str]:
    return [row[1] for row in db.execute(f'PRAGMA table_info({table})')]


def check_schema(db: sqlite3.Connection) -> int:
    version = db.execute('PRAGMA user_version').fetchone()[0]
    if version not in (1, 2):
        raise MemoryError('unsupported memory schema')
    if _table_columns(db, 'memories') != MEMORY_COLUMNS:
        raise MemoryError('invalid memory schema')
    if version == 2 and _table_columns(db, 'memory_membership_events') != MEMBERSHIP_COLUMNS:
        raise MemoryError('invalid memory schema')
    return version


def prepare_writable_schema(db: sqlite3.Connection) -> None:
    version = db.execute('PRAGMA user_version').fetchone()[0]
    tables = db.execute("SELECT name FROM sqlite_master WHERE type='table'").fetchall()
    if version == 0 and not tables:
        db.execute(SCHEMA)
        db.execute('CREATE INDEX memory_key_id ON memories(key, id)')
        db.execute(MEMBERSHIP_SCHEMA)
        db.execute('CREATE INDEX memory_membership_key_id ON memory_membership_events(key, id)')
        db.execute('PRAGMA user_version=2')
        return
    if version == 1:
        check_schema(db)
        db.execute(MEMBERSHIP_SCHEMA)
        db.execute('CREATE INDEX memory_membership_key_id ON memory_membership_events(key, id)')
        db.execute('PRAGMA user_version=2')
        return
    check_schema(db)


def _latest_membership_action(db: sqlite3.Connection, key: str) -> str | None:
    row = db.execute(
        'SELECT action FROM memory_membership_events WHERE key=? ORDER BY id DESC LIMIT 1',
        (key,),
    ).fetchone()
    return row['action'] if row else None


def remember(path: Path, key: str, text: str, source: str,
             instance: str = 'pc-prototype') -> dict:
    for value, name, maximum in [(key, 'key', 128), (text, 'text', 8192),
                                  (source, 'source', 1024), (instance, 'instance', 128)]:
        validate(value, name, maximum)
    path = path.expanduser().resolve()
    path.parent.mkdir(parents=True, exist_ok=True)
    with closing(sqlite3.connect(path, timeout=5)) as db:
        db.row_factory = sqlite3.Row
        db.execute('PRAGMA foreign_keys=ON')
        db.execute('PRAGMA synchronous=FULL')
        try:
            db.execute('BEGIN IMMEDIATE')
            prepare_writable_schema(db)
            previous = db.execute('SELECT id FROM memories WHERE key=? ORDER BY id DESC LIMIT 1',
                                  (key,)).fetchone()
            cursor = db.execute('''INSERT INTO memories
                (key,text,source,recorded_at,instance,evidence,adoption,supersedes)
                VALUES (?,?,?,?,?,'operator_supplied','candidate',?)''',
                (key, text, source, datetime.now(timezone.utc).isoformat(), instance,
                 previous['id'] if previous else None))
            record = dict(db.execute('SELECT * FROM memories WHERE id=?',
                                     (cursor.lastrowid,)).fetchone())
            db.commit()
            return record
        except BaseException:
            db.rollback()
            raise


def recall(path: Path, key: str, history: bool = False) -> list[dict]:
    validate(key, 'key', 128)
    # A missing database is an error; reading must never create an empty substitute.
    uri = path.expanduser().resolve().as_uri() + '?mode=ro'
    with closing(sqlite3.connect(uri, uri=True, timeout=5)) as db:
        db.row_factory = sqlite3.Row
        version = check_schema(db)
        if not history and version == 2 and _latest_membership_action(db, key) == 'archive':
            return []
        sql = 'SELECT * FROM memories WHERE key=? ORDER BY id DESC'
        if not history:
            sql += ' LIMIT 1'
        return [dict(row) for row in db.execute(sql, (key,))]


def _change_membership(path: Path, key: str, action: str, source: str) -> dict:
    validate(key, 'key', 128)
    validate(source, 'source', 1024)
    uri = path.expanduser().resolve().as_uri() + '?mode=rw'
    with closing(sqlite3.connect(uri, uri=True, timeout=5)) as db:
        db.row_factory = sqlite3.Row
        db.execute('PRAGMA foreign_keys=ON')
        db.execute('PRAGMA synchronous=FULL')
        try:
            db.execute('BEGIN IMMEDIATE')
            prepare_writable_schema(db)
            exists = db.execute('SELECT 1 FROM memories WHERE key=? LIMIT 1', (key,)).fetchone()
            if not exists:
                raise MemoryError('memory key not found')
            current = _latest_membership_action(db, key)
            if action == 'restore' and current != 'archive':
                raise MemoryError('memory key not archived')
            if action == 'archive' and current == 'archive':
                raise MemoryError('memory key already archived')
            cursor = db.execute('''INSERT INTO memory_membership_events
                (key,action,recorded_at,source) VALUES (?,?,?,?)''',
                (key, action, datetime.now(timezone.utc).isoformat(), source))
            record = dict(db.execute('SELECT * FROM memory_membership_events WHERE id=?',
                                     (cursor.lastrowid,)).fetchone())
            db.commit()
            return record
        except BaseException:
            db.rollback()
            raise


def archive(path: Path, key: str, source: str) -> dict:
    return _change_membership(path, key, 'archive', source)


def restore(path: Path, key: str, source: str) -> dict:
    return _change_membership(path, key, 'restore', source)


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--db', type=Path, default=DEFAULT_DB)
    commands = parser.add_subparsers(dest='command', required=True)
    write = commands.add_parser('remember', help='explicitly save an operator-supplied candidate record')
    write.add_argument('key')
    write.add_argument('text')
    write.add_argument('--source', required=True)
    write.add_argument('--instance', default='pc-prototype')
    read = commands.add_parser('recall', help='retrieve by exact, case-sensitive key')
    read.add_argument('key')
    read.add_argument('--history', action='store_true')
    archive_cmd = commands.add_parser('archive', help='remove a key from active recall without deleting source records')
    archive_cmd.add_argument('key')
    archive_cmd.add_argument('--source', required=True)
    restore_cmd = commands.add_parser('restore', help='restore an archived key to active recall')
    restore_cmd.add_argument('key')
    restore_cmd.add_argument('--source', required=True)
    args = parser.parse_args(argv)
    try:
        if args.command == 'remember':
            record = remember(args.db, args.key, args.text, args.source, args.instance)
            # Acknowledge only after commit. Do not echo private text in write diagnostics.
            print(json.dumps({'event': 'memory_saved', 'id': record['id'],
                              'supersedes': record['supersedes']}))
        elif args.command == 'recall':
            records = recall(args.db, args.key, args.history)
            print(json.dumps({'event': 'memory_recalled' if records else 'memory_not_found',
                              'records': records}, ensure_ascii=True))
            return 0 if records else 1
        else:
            record = archive(args.db, args.key, args.source) if args.command == 'archive' \
                else restore(args.db, args.key, args.source)
            print(json.dumps({'event': 'memory_archived' if args.command == 'archive'
                              else 'memory_restored', 'id': record['id'], 'key': record['key']}))
    except (MemoryError, OSError, sqlite3.Error):
        print(json.dumps({'event': 'memory_failed', 'reason': 'storage_or_record_invalid'}),
              file=sys.stderr)
        return 2
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
