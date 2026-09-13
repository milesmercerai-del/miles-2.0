from contextlib import closing
from datetime import datetime, timezone
from pathlib import Path
import sqlite3
import tempfile
import unittest

from runtime.memory import (
    SCHEMA,
    MemoryError,
    archive,
    recall,
    remember,
    restore,
)


class MemoryCurationTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.path = Path(self.temp.name) / "memory.sqlite3"

    def test_archive_hides_active_recall_but_preserves_history(self):
        remember(self.path, "cube", "blue", "original")
        remember(self.path, "cube", "green", "correction")

        archive(self.path, "cube", "curation test")

        self.assertEqual(recall(self.path, "cube"), [])
        self.assertEqual(
            [record["text"] for record in recall(self.path, "cube", history=True)],
            ["green", "blue"],
        )

        with closing(sqlite3.connect(self.path)) as db:
            self.assertEqual(
                db.execute(
                    "SELECT COUNT(*) FROM memories WHERE key='cube'"
                ).fetchone()[0],
                2,
            )

    def test_restore_reactivates_latest_record(self):
        remember(self.path, "cube", "green", "correction")
        archive(self.path, "cube", "archive test")
        restore(self.path, "cube", "restore test")

        self.assertEqual(recall(self.path, "cube")[0]["text"], "green")

        with closing(sqlite3.connect(self.path)) as db:
            actions = [
                row[0]
                for row in db.execute(
                    "SELECT action FROM memory_membership_events "
                    "WHERE key='cube' ORDER BY id"
                )
            ]
        self.assertEqual(actions, ["archive", "restore"])

    def test_new_record_does_not_silently_restore_archived_key(self):
        remember(self.path, "cube", "green", "before archive")
        archive(self.path, "cube", "archive test")

        remember(self.path, "cube", "purple", "new information")

        self.assertEqual(recall(self.path, "cube"), [])
        self.assertEqual(
            [record["text"] for record in recall(self.path, "cube", history=True)],
            ["purple", "green"],
        )

        restore(self.path, "cube", "explicit restore")
        self.assertEqual(recall(self.path, "cube")[0]["text"], "purple")

    def test_archive_missing_key_fails_without_membership_event(self):
        remember(self.path, "existing", "safe", "fixture")

        with self.assertRaises(MemoryError):
            archive(self.path, "missing", "curation test")

        self.assertEqual(recall(self.path, "existing")[0]["text"], "safe")

        with closing(sqlite3.connect(self.path)) as db:
            self.assertEqual(
                db.execute(
                    "SELECT COUNT(*) FROM memory_membership_events"
                ).fetchone()[0],
                0,
            )

    def test_v1_database_migrates_without_losing_source_record(self):
        with closing(sqlite3.connect(self.path)) as db:
            db.execute(SCHEMA)
            db.execute("CREATE INDEX memory_key_id ON memories(key, id)")
            db.execute(
                """INSERT INTO memories
                (key,text,source,recorded_at,instance,evidence,adoption,supersedes)
                VALUES (?,?,?,?,?,'operator_supplied','candidate',NULL)""",
                (
                    "legacy",
                    "preserved",
                    "v1 fixture",
                    datetime.now(timezone.utc).isoformat(),
                    "pc-prototype",
                ),
            )
            db.execute("PRAGMA user_version=1")
            db.commit()

        archive(self.path, "legacy", "migration test")

        with closing(sqlite3.connect(self.path)) as db:
            self.assertEqual(
                db.execute("PRAGMA user_version").fetchone()[0],
                2,
            )
            self.assertEqual(
                db.execute(
                    "SELECT COUNT(*) FROM memories WHERE key='legacy'"
                ).fetchone()[0],
                1,
            )

        self.assertEqual(recall(self.path, "legacy"), [])
        self.assertEqual(
            recall(self.path, "legacy", history=True)[0]["text"],
            "preserved",
        )

        restore(self.path, "legacy", "migration restore")
        self.assertEqual(
            recall(self.path, "legacy")[0]["text"],
            "preserved",
        )


if __name__ == "__main__":
    unittest.main()