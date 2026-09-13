# Miles Project — Bryan Jones + Miles Mercer | Public technical code
# Local memory prototype v0.1 | 2026-09-13
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


class MemoryError(ValueError):
    pass


def validate(value: str, name: str, maximum: int) -> None:
    if not isinstance(value, str) or not value.strip() or len(value) > maximum:
        raise MemoryError('invalid ' + name)


def check_schema(db: sqlite3.Connection) -> None:
    if db.execute('PRAGMA user_version').fetchone()[0] != 1:
        raise MemoryError('unsupported memory schema')
    columns = [row[1] for row in db.execute('PRAGMA table_info(memories)')]
    if columns != ['id', 'key', 'text', 'source', 'recorded_at', 'instance',
                   'evidence', 'adoption', 'supersedes']:
        raise MemoryError('invalid memory schema')


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
            version = db.execute('PRAGMA user_version').fetchone()[0]
            tables = db.execute("SELECT name FROM sqlite_master WHERE type='table'").fetchall()
            if version == 0 and not tables:
                db.execute(SCHEMA)
                db.execute('CREATE INDEX memory_key_id ON memories(key, id)')
                db.execute('PRAGMA user_version=1')
            check_schema(db)
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
        check_schema(db)
        sql = 'SELECT * FROM memories WHERE key=? ORDER BY id DESC'
        if not history:
            sql += ' LIMIT 1'
        return [dict(row) for row in db.execute(sql, (key,))]


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
    args = parser.parse_args(argv)
    try:
        if args.command == 'remember':
            record = remember(args.db, args.key, args.text, args.source, args.instance)
            # Acknowledge only after commit. Do not echo private text in write diagnostics.
            print(json.dumps({'event': 'memory_saved', 'id': record['id'],
                              'supersedes': record['supersedes']}))
        else:
            records = recall(args.db, args.key, args.history)
            print(json.dumps({'event': 'memory_recalled' if records else 'memory_not_found',
                              'records': records}, ensure_ascii=True))
            return 0 if records else 1
    except (MemoryError, OSError, sqlite3.Error):
        print(json.dumps({'event': 'memory_failed', 'reason': 'storage_or_record_invalid'}),
              file=sys.stderr)
        return 2
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
