# Local memory prototype v0.1

**Miles Project — Bryan Jones + Miles Mercer | Public technical record | 2026-09-13**

This operator-driven CLI adds real local persistence alongside the mock bootstrap. It is a separate command, not yet part of model conversation. No model, network, hardware, or privileged action is invoked. Python's standard-library SQLite implementation is the only storage dependency.

## Windows walkthrough

From the repository directory in PowerShell:

```powershell
py -3 -m runtime.memory remember test-cube "The test cube is blue." --source "Bryan's manual PC test"
```

Expect `memory_saved`. This appears only after the SQLite transaction commits. The process then exits, so the next command is a separate process:

```powershell
py -3 -m runtime.memory recall test-cube
```

Expect the saved text, source, UTC recording timestamp, recording instance, evidence type, adoption state and record ID. These are operator-supplied candidate records, not verified truth or firsthand model experiences. Source is a label, not authenticated authorship. Reads use exact case-sensitive keys; no semantic retrieval exists yet.

To correct a record, remember the same key with new text and a new source. The new row points to the previous row through `supersedes`; the old row remains accessible with:

```powershell
py -3 -m runtime.memory recall test-cube --history
```

## Storage and boundaries

Default database: `.miles/memory.sqlite3` under the current user's home folder, outside the repository. On the demonstrated PC this is `C:\Users\jones\.miles\memory.sqlite3`. An operator can choose another file with `--db PATH` before the subcommand. Do not place private databases in public source control. Database extensions are ignored as an extra guard, not access control.

Records are unencrypted and rely on the local user account's filesystem permissions; this prototype does not qualify Windows ACLs or service isolation. Use synthetic test facts during bring-up. Recall intentionally prints requested content to the terminal. Write diagnostics omit text and source; command arguments may remain in shell history. No background logging or automatic upload is implemented.

Writes are append-only through this API and transactional, with a five-second lock timeout. Other local tools can still alter the database; this is not tamper-proof storage. A correction does not rewrite earlier records. Schema version 1 is checked; unsupported or corrupt databases are not automatically reset. Reads open in read-only mode and never create a missing substitute database. Exit codes: 0 success, 1 absent key in a valid store, 2 storage/validation failure. Success means SQLite committed locally, not that a separate backup exists or disk hardware survived a power failure.

This is the first durable-record increment, not the full memory architecture. No automatic conversation ingestion, model-driven write authority, Core adoption, confidence scoring, consolidation, cross-device synchronization, or backup/restore is claimed. The existing mock bootstrap still correctly reports its own persistence as unavailable. Future model integration must keep write decisions runtime-owned and action enforcement separate.

## Evidence

Eight memory tests pass on Linux, including retrieval from a second process, provenance, correction history, missing/corrupt storage, unknown schema, invalid records, instruction-like data and failed writes. Existing bootstrap (7) and security (34) suites are retained. Windows verification is the next user-run gate.

The previous bootstrap's seven tests plus startup/input/shutdown were demonstrated on Windows in the assisted session. Git's CRLF checkout caused its first integrity failure; `.gitattributes` now pins the canonical Core to LF, and the existing checkout was repaired without changing wording or expected digest.
