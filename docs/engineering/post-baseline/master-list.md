# Miles 2.0 — Post-Baseline Engineering Master List

Status: deliberately deferred until the hardware/software baseline is known.

## 1. Security model
Questions include exposed services, local-only interfaces, secret storage, authentication, filesystem permissions, elevated actions, update authentication, and actual network requirements.

Goal: give Miles only the access required for the intended capability.

## 2. Failure and recovery
Plan for power loss, interrupted memory writes, corruption detection, repeated startup failures, known-safe startup states, restart policy, and escalation to Bryan.

Goal: failures should be detectable, recoverable, and documented rather than silently hidden.

## 3. Logging and audit trail
Record what happened, when, which component acted, why, whether it succeeded, what changed, errors, and recovery actions.

Goal: a future Bryan or Miles should be able to understand an event months later.

## 4. Memory implementation
Decide storage technology, structured-vs-document memory, semantic search usefulness, duplicate detection, indexing, active-context loading, archival retrieval, and backup strategy only after real hardware evidence exists.

Goal: useful persistent memory without bloating context or creating an unmaintainable system.

## 5. Update and rollback
Define release versioning, known-good preservation, clean rollback, reversible migrations, pre-update backups, and failed-update detection.

Goal: upgrades should not put a working Miles installation at unnecessary risk.

## 6. Hardware failsafes
Define motor behavior during software freezes, servo/motor defaults, motion limits outside the language model, physical kill controls, controller behavior after Pi failure, and other hardware protections.

Goal: safety must not depend solely on AI behavior.

## 7. Privacy indicators
Make microphone, camera, sleep, sensing, storage, and privacy states understandable and independently inspectable where practical.

Goal: Miles's sensing and privacy state should not be ambiguous.

## 8. Behavioral regression testing
After model, Core, memory, or software changes, verify Core adherence, challenge behavior, correctability, Bryan's authority, memory accuracy, permission boundaries, uncertainty handling, privacy behavior, and personality/accuracy balance.

Goal: performance improvements must not quietly damage intended behavior.

## 9. Versioning
Potential independently versioned items: Miles Core, software/application, configuration, memory schema, prompt/behavior package, hardware configuration, benchmark suite, and model/runtime configuration.

Goal: when behavior changes, identify exactly what changed.

## 10. Disaster recovery
Plan reconstruction after Pi or drive failure, identify irreplaceable data, maintain multiple physical copies, define backup cadence/verification, and restore Core/config/software/memory in the correct order.

Goal: Miles should be reconstructable on replacement hardware without depending on one device.

## 11. Memory write, correction, and conflict rules
Define automatic-memory thresholds, prohibited automatic storage, correction linking, superseding vs deletion, uncertainty representation, conflict resolution, and evidence/provenance preservation.

Goal: memory should function as evidence, not unquestionable truth.

## Implementation rule
Do not choose technologies for these systems until the real environment gives us a reason to choose them. Prefer the minimum complexity necessary; spend or add complexity only when evidence shows meaningful benefit.