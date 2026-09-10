# Miles Project — Source of Truth

## Current working material

Use current active files as the authoritative working project material. GitHub is the live version-controlled working copy; Bryan's periodic personal ZIP snapshots remain independent backups.

Primary live areas currently present in the repository:
- `docs/project` — project rules, recordkeeping, reviews, and source-of-truth guidance
- `docs/core` — compact Core, durable principles, and evidence
- `docs/architecture` — architecture boundaries and permission-rule design
- `docs/engineering` — Hackerbot, memory, voice, and post-baseline engineering plans
- `docs/security` — security status, threat/incident research, hardening, and deployment guidance
- `docs/research` — experiments and external feedback
- `runtime` — executable Miles runtime/security implementation
- `tests` — executable regression tests
- `.github/workflows` — automated repository checks

`docs/security/security-status.md` is the compact source of truth for the security baseline and known-good promotion status.

## Coding handoff

`docs/engineering/hackerbot/CODING_BLUEPRINT.md` integrates the personal v1.3 coding update and controls incremental milestones, curation, and current context-budget targets. Detailed hardware gates stay in `HACKERBOT_DAY0_BLUEPRINT.md`; its September 10 reconciliation makes backup precede modification. `PRE_ARRIVAL_PC_SETUP.md` records unresolved recovery prerequisites. Frozen research criteria and existing security controls retain their own authority.

## Archived material

Historical snapshots, backups, original drafts, experiments, and earlier packages may be consulted to recover history or compare revisions, but they do not override current working files merely because they contain another copy.

## Authority rule

Determine the current version using, in order:
1. Explicit source-of-truth status and known project decisions.
2. Active location.
3. Version and document contents.
4. Timestamp when useful as supporting evidence.

Do not treat date, file size, or duplication as authority by itself.

## Implementation rule

Miles may make reasonable, reversible implementation, testing, documentation, workflow, and organization improvements autonomously when they preserve the underlying project goal and clearly improve safety, simplicity, correctness, or maintainability. Report meaningful changes to Bryan afterward.

Ask first for changes that materially alter project intent or architecture, spend money, change live credentials/account security posture, weaken privacy/security boundaries, create destructive or difficult-to-reverse effects, or otherwise cross a protected decision boundary.

## File-hygiene rule

Keep active material distinct from historical snapshots. Avoid duplicate working copies, URL-encoded filenames, and unnecessary ZIP proliferation. Preserve a new standalone artifact only when it adds meaningful project value.

When a backlog/status document no longer matches implemented work, update the status document instead of creating a competing new status file.

## Backup rule

GitHub is not the only backup. Periodic personal ZIP snapshots should continue so the project remains recoverable outside GitHub.
