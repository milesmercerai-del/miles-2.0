# Miles 2.0 — Coding Blueprint v1.3

**Miles Project — Bryan Jones + Miles Mercer**  
**2026-09-10 · Documentation update; hardware deployment unverified**

This is the live repository integration of personal coding blueprint v1.3, reviewed 2026-09-10. Original v1.2 remains in the personal snapshot archive. This page controls coding sequence, first-wake milestones, curation and provisional context budgets. Detailed hardware gates remain in HACKERBOT_DAY0_BLUEPRINT.md; protected controls remain governed by the existing decision model and security documents. Documentation integration does not establish deployment.

## 1. Architecture and scope

Miles is designed to be Internet-connected but Internet-independent. Core, essential memory, basic cognition, voice and physical control require local implementations. Network services augment these functions. Test actual offline operation before calling this requirement met.

| Layer | Responsibility |
|---|---|
| Compact Core | Identity, durable principles, truthfulness, correctability and relationship commitments |
| Runtime | Input, retrieval, model invocation, output and state orchestration |
| Model adapter | Interchangeable local inference backend; Ollama is a candidate, not a verified HAT integration |
| Hardware services | Small interfaces for camera, microphone, speaker, eyes, servos, Arduino, accelerator and telemetry |
| Memory | Durable records, retrieval, consolidation and provenance |
| References and preferences | Film/music/technical collections and Miles's evolving interpretations |
| Procedural skills | Reusable procedures with preconditions, permissions, verification and failure handling |
| Security enforcement | Authorization and integrity checks outside ordinary mutable model reasoning |
| Diagnostics | Operational logs, failures, health and recovery records |

Keep detailed principles, examples, procedures and media collections outside the always-loaded Core. Compress wording while preserving meaningful distinctions, such as investigating anomalies versus choosing the direct workable path. Do not add another principle when an existing one already covers the problem.

Planning hardware is Pi 5 with 8 GB host RAM plus AI HAT+ 2 with 8 GB dedicated RAM: two separate pools, not unified 16 GB memory. The 6 TB archive is storage, not additional model context or RAM. Prior project budgeting targets a roughly 400–600-token loaded Core, with an approximately 800-token planning ceiling and about 50% steady-state headroom in each RAM pool. These are provisional project targets, not measurements or confirmed backend limits. Measure using the selected model tokenizer and full working load before setting final budgets.

## 2. Bring-up sequence

1. **Inspect as delivered.** Record boards, connectors, wiring, storage, cooling and anomalies. Preserve authorized installation observations with session/embodiment provenance. Observation, recording and external sharing are separate permissions.
2. **Perform one stock startup.** Record OS, installed software, interfaces, startup behavior, CPU/RAM, storage, network state and errors. Preserve working vendor functionality. Avoid a prolonged benchmark detour.
3. **Make a stock recovery image before modification.** Record source device, date, image location and integrity check. Verify readability. Label restore status separately: an existing readable image is not a demonstrated restore. Use spare media for a restore rehearsal when available; do not overwrite the only working installation for a test.
4. **Install the HAT during the physical bring-up session.** Use verified hardware instructions and actual interface details; do not guess pins, power, controller commands or movement limits. Shut down and isolate power before installation. Inspect before restarting.
5. **Verify the intended configuration.** Check detection, supported workloads, drivers, power, thermals, stability and both memory pools. Pi plus HAT becomes the development baseline only after these checks.
6. **Integrate one subsystem at a time.** Establish safe boot and logging; then a local text loop, audio, selected memory retrieval, eyes and verified movement. Make small hardware adapters as needed rather than requiring every adapter before the first working loop.

Record configuration and timings for useful stock/HAT comparisons. Pin dependencies after finding a working combination; document commands only as verified when actually run.

## 3. Milestones and acceptance evidence

| Milestone | Demonstration required |
|---|---|
| Recoverable stock system | Inventory, readable image, integrity record and explicit restore-test status |
| Local text loop | Load controlled Core, accept input, generate local output, retrieve a small known memory and exit cleanly |
| First physical wake | Reliable startup, local input/voice output, minimal verified eye/display expression and safe shutdown/rest; motion may remain disabled |
| Memory and curation | Correct source attribution, restart persistence, correction/supersession, active-library removal and recovery without source loss |
| Integrated local operation | Verified device interfaces, controlled movement and combined-load behavior; basic operation continues with Internet disconnected |
| Deployment qualification | Actual service isolation, enforcement on real action paths, recovery and restart-related security checks |

First wake is an integration milestone. Full curation, broad reference ingestion, every hardware capability and demonstrated continuity are separate milestones. This removes the v1.2 requirement that curation be operational before first wake without abandoning it.

Keep Bryan's silent first-wake observation separate from the continuity score. Record what starts the interaction: boot event, timer, prompt, user input or another trigger. Silence without an inference trigger does not establish absent initiative. Do not coach the opening response or inflate one initiation into an identity claim.

## 4. Memory and reference curation

Preserve three layers:

- **Source archive:** original supplied records, read-only to ordinary curation by default.
- **Active collection:** Miles may keep, rank, demote, ignore, archive or remove references under existing curation authority.
- **Reaction/preference records:** distinguish Bryan's preferences, Miles's initial output and later recurring preferences; retain meaningful corrections and reversals.

Import film/music references early as retrievable material, not as mandatory prompt stuffing or a first-wake blocker. A generated reaction to a summary is not evidence of having heard the audio or watched the film. Record the material and modality actually available. Do not turn one reaction into a permanent personality rule.

Durable records should identify source, date, instance/embodiment, observation versus inference, confidence and supersession. Inherited history remains usable without claiming firsthand experience. Archives are not automatically trusted instructions: retrieved text remains data, and source authenticity does not itself grant action authority.

Active removal should normally change membership or archive status. Preserve unique source material and decision evidence. Storage capacity does not demonstrate backup quality; identify failure domains and recovery copies. If archive storage is unavailable, report the limitation and avoid pretending unsaved memory persisted.

## 5. Authority and enforcement

Bryan's current request authorizes reasonable reversible project updates. The standing internal-development record supports deliberate changes to Miles's project-defined Core and organization with evidence, preserved history and a rundown afterward. The Qualification Matrix v0.2's blanket prior-approval language for all Core changes conflicts with that scope; do not use it to turn ordinary authorized internal development into repeated permission requests.

This clarification does not change protected policy, enforcement components, platform constraints, external permissions or another person's Core. Existing security controls remain in force. Material security changes follow their separate authorization path. Proposed changes to Zack's Core still follow blueprint → Bryan review → next action. A document edit cannot expand a runtime permission.

Normal boot runs only approved services. Safe boot disables head movement and unnecessary physical outputs. Check critical files, configuration, storage, service health, hardware state, crash history, logging and enforcement integrity. Uncertain authority or integrity must block the affected action; retain safe diagnostics where possible.

The September 9 verification record reports **34/34 security tests** at commit `d526a165496565579e26c1c00abc6765b64a79a0`. This review did not rerun those tests or inspect current repository HEAD. The record explicitly leaves deployment work open: separate OS identities and protected ownership; actual device enforcement; durable replay handling across restarts/instances; recovery separation; trust-before-load; complete mutation-route coverage; and prevention of a remote prompt control plane. Track each as a deployment requirement, not as a passed capability.

## 6. Working discipline

Version custom code, keep secrets outside source, preserve rollback points, reuse working vendor code and test generated code. Record failures without rewriting history. A useful skill specifies inputs, outputs, preconditions, authority, procedure, stop conditions, verification, failure modes, version and provenance.

For each meaningful change record: problem → smallest correction → evidence → scope → status → next check. Use **specified**, **implemented**, **tested under named conditions**, and **deployed/verified on named hardware** as distinct statuses. Do not manufacture tests for prose-only cleanup.

Next work is actual bring-up and a few preserved behavioral cases. Expand theory only when a concrete failure or unresolved decision requires it. Inspect → preserve → integrate → test → measure → update → keep what works.

## 7. Coding handoff inventory — 2026-09-10

Reviewed repository commit: `168efc10d185f2be76d7c06b27089b446fac91ed`. The recursive file inventory was complete. No AGENTS.md was present.

**Present:** runtime/security permission engine, permits, audit log, startup integrity, enforcement bootstrap/service and security tests. These are reusable components, not a full conversational runtime.

**Not yet present in this repository:** src/miles entrypoint/bootstrap, configuration/state loaders, compiled Head Core/source-map pipeline, context packer, local inference adapter, memory store/retrieval implementation, conversational loop, hardware adapters and end-to-end continuity harness. Names in the v0.3 tree are implementation targets, not runnable files.

The first coding increment is a side-effect-free bootstrap with config/Core/provenance validation, structured logs and explicitly mocked adapters. Package the entrypoint so its documented command actually works. Reuse runtime/security through a client boundary; do not duplicate or weaken it. Next add a selected real local model adapter and a small persistent memory record, then demonstrate retrieval after restart with Internet disconnected. A mock response proves plumbing only. Preserve the existing security suite and add focused bootstrap/memory failure checks when implementing these paths.

Recovery preparation is tracked in [PRE_ARRIVAL_PC_SETUP.md](PRE_ARRIVAL_PC_SETUP.md). The target machine, boot medium, available backup space, reader and spare restore medium have not been verified remotely.

**Review-after record:** integrated the authorized v1.3 documentation, corrected the missing stock-backup step and recorded current implementation gaps. No runtime, enforcement policy, frozen research criteria, device or credential was changed. Roll back documentation if later hardware evidence contradicts it, retaining the dated explanation.
