# Miles Security Status

This file is the compact source of truth for the current Miles security baseline. Detailed design rationale and incident research stay in the other security documents; this page answers: **what is enforced, what is tested, what is still only a requirement, and what commit is eligible to be called known-good?**

## Baseline policy

A commit is **known-good** only when the full security regression suite passes for that exact commit (or a descendant whose only changes are non-executable documentation and whose security-relevant ancestry is unchanged).

A newer commit is a **candidate baseline** until that proof exists. Documentation alone does not promote a baseline.

## Current candidate

- Candidate commit: `ba1d6173a273e3e894da3f3065a8ec30e6362353`
- Includes automatic GitHub security regression workflow.
- At the time this file was written, no completed CI run had been observed for that candidate, so it is **not yet declared known-good**.

## Executable security controls already represented in tests

The current `tests/security` suite covers the implemented permission/enforcement layer, including:

- exact action permits and replay/TOCTOU defenses;
- audit-log behavior and protection;
- enforcement bootstrap and policy/integrity loading;
- enforcement service behavior;
- incident-derived high-risk policy tags;
- permission-engine behavior, including fail-safe outcomes;
- startup integrity and policy artifact verification.

## Design requirements not automatically considered implemented

The following newer hardening requirements remain requirements until corresponding runtime mechanisms and regression tests exist:

1. **Recovery blast-radius separation** — at least one verifiable recovery generation must sit outside ordinary runtime delete/write authority.
2. **Trust-before-load workspace handling** — untrusted repositories/bundles can be inspected without activating local hooks, plugins, MCP definitions, policy overrides, environment files, or similar executable configuration; path/symlink escape must be checked.
3. **Canonical/shared object immutability across every mutation route** — protected state must remain protected through direct edit, bulk upload, restore/import, replacement, and session-local paths.
4. **No emergent remote prompt control plane** — untrusted tool/sandbox/parser output remains provenance-marked data and cannot create an unbounded authority-bearing command loop.

These are documented in `security-watch-hardening-2026-09-09.md` and should move into the executable suite as the corresponding runtime components are built.

## Promotion checklist

Before promoting a candidate to known-good:

- run the entire `tests/security` suite for the exact candidate;
- require every test to pass;
- confirm any newly implemented security feature has both a positive test and an abuse/near-miss test;
- confirm policy/integrity verification still fails closed;
- confirm audit output does not expose protected security detail to unauthorized readers;
- record the passing commit SHA here.

## Operating rule

Prefer **incident/failure class -> control -> executable regression -> passing commit** over accumulating security prose. New research that does not produce a new failure class, defense, or test should not create additional project complexity.
