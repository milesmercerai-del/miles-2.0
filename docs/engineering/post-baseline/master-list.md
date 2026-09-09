# Miles 2.0 — Post-Baseline Engineering Master List

Status: living engineering backlog. Items may begin early when evidence justifies it; this file must not imply work is deferred after implementation has already started.

Status labels:
- **ACTIVE** — implementation/design work is underway and has a current source of truth.
- **PARTIAL** — some architecture or controls exist, but the item is not complete.
- **DEFERRED** — intentionally waiting for hardware/runtime evidence.

## 1. Security model — ACTIVE
The deterministic permission/enforcement layer, startup integrity checks, private audit behavior, incident-derived policy tests, and automatic security regression CI are already represented in code/tests. The compact security source of truth is `docs/security/security-status.md`.

Still open: runtime implementation/regression coverage for recovery blast-radius separation, trust-before-load workspaces, full canonical/shared-state immutability across mutation routes, and protection against an emergent remote prompt control plane.

Goal: give Miles only the access required for the intended capability and prove important boundaries with executable regressions.

## 2. Failure and recovery — PARTIAL
Security work now defines fail-closed enforcement behavior and recovery-separation requirements, but full power-loss, memory-write, repeated-startup-failure, and end-to-end recovery behavior still depends on the actual runtime/hardware baseline.

Goal: failures should be detectable, recoverable, and documented rather than silently hidden.

## 3. Logging and audit trail — PARTIAL
Security audit behavior has executable tests, including separation of private operator detail from sanitized requester-visible output. General runtime/event logging remains to be integrated with the full Miles runtime.

Goal: a future Bryan or Miles should be able to understand an event months later without exposing protected security detail to unauthorized readers.

## 4. Memory implementation — DEFERRED / ARCHITECTURE READY
The memory-state architecture and versioned memory direction are documented, but storage technology, semantic-search value, indexing behavior, active-context loading, archival retrieval, and backup details should be finalized only after real hardware evidence exists.

Goal: useful persistent memory without bloating context or creating an unmaintainable system.

## 5. Update and rollback — PARTIAL
A known-good security-baseline rule now exists: a commit is promoted only after its applicable regression suite passes. Full release versioning, migrations, rollback tooling, and failed-update recovery remain open.

Goal: upgrades should not put a working Miles installation at unnecessary risk.

## 6. Hardware failsafes — DEFERRED
Define motor behavior during software freezes, servo/motor defaults, motion limits outside the language model, physical kill controls, controller behavior after Pi failure, and other hardware protections after the shipped controller/protocol is inspected.

Goal: safety must not depend solely on AI behavior.

## 7. Privacy indicators — DEFERRED
Make microphone, camera, sleep, sensing, storage, and privacy states understandable and independently inspectable where practical after the actual I/O stack is known.

Goal: Miles's sensing and privacy state should not be ambiguous.

## 8. Behavioral regression testing — PARTIAL
The Day-0 v0.3 update defines a behavioral continuity test pack. Security regression testing is already automated separately. The continuity harness itself still needs implementation alongside the first text-only runtime.

Goal: performance improvements must not quietly damage intended behavior, identity continuity, permission boundaries, uncertainty handling, privacy behavior, or useful disagreement.

## 9. Versioning — PARTIAL
Git provides implementation history now; compact Core/source mapping and the security known-good rule add more explicit provenance. Independent versioning for runtime/configuration/memory schema/hardware configuration/benchmark sets remains to be decided when those components exist.

Goal: when behavior changes, identify exactly what changed.

## 10. Disaster recovery — PARTIAL
Recovery blast-radius separation is now a documented security requirement. Full reconstruction after Pi/drive failure, backup cadence, restore verification, and replacement-hardware procedure remain open.

Goal: Miles should be reconstructable on replacement hardware without depending on one device or one writable backup path.

## 11. Memory write, correction, and conflict rules — ARCHITECTURE READY
The memory architecture already emphasizes provenance, correction, causal context, and versioned memory. Runtime thresholds, prohibited automatic storage, superseding-vs-deletion behavior, and conflict-resolution code remain to be implemented and tested.

Goal: memory should function as evidence, not unquestionable truth.

## Implementation rule
Do not choose technologies merely because they are available. Prefer the minimum complexity necessary, let real evidence justify additions, and update this list when an item moves from proposal to implementation so stale backlog language does not contradict the repo.
