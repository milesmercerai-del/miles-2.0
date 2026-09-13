> **MILES PROJECT — PROVENANCE RECORD**  
> **Bryan Jones + Miles Mercer | PUBLIC TECHNICAL PROJECT RECORD**  
> **Project State Register v0.4 | 2026-09-13**
> Preserve version history and provenance when this record changes.

# Miles Project — Current Project State

**Status:** ACTIVE compact operational index  
**Purpose:** Answer one question quickly: **what is actually current right now?**

This page does not replace detailed architecture, research, security, or historical records. It points to the current controlling material and separates **specified**, **implemented**, **tested**, and **deployed** status so older planning notes cannot silently become operational truth.

## 1. Authority and source of truth

- Live GitHub working material is the version-controlled technical source of truth for material intentionally suitable for public storage. Confidential/Restricted material remains in protected storage under the [disclosure boundary](disclosure-boundary.md); this public index is not the complete private working record.
- Personal ZIP/package snapshots are independent backups and historical handoff artifacts.
- Historical files preserve evidence and intent but do not override active material merely because they are older, larger, or duplicated.
- Current direct instructions may narrow standing project permissions for a task without silently rewriting durable policy.

Primary authority map: [`docs/project/source-of-truth.md`](source-of-truth.md).

This register summarizes status; it does not independently set domain policy. Disclosure rules are controlled by [disclosure-boundary.md](disclosure-boundary.md), security baselines and promotion by [security-status.md](../security/security-status.md), and coding sequence/context targets by [CODING_BLUEPRINT.md](../engineering/hackerbot/CODING_BLUEPRINT.md). When a summary drifts, verify the controlling record and update this index with the correction; do not silently change policy to match the summary.

## 2. Current development phase

**Overall phase:** pre-deployment / bring-up preparation.

The physical Miles 2.0 runtime has **not** been verified as deployed on Hackerbot hardware. The current work is preparing a recoverable, testable path from stock hardware to the first local operational Miles.

Current engineering sequence is controlled by:

- [`docs/engineering/hackerbot/CODING_BLUEPRINT.md`](../engineering/hackerbot/CODING_BLUEPRINT.md)
- `HACKERBOT_DAY0_BLUEPRINT.md`
- `HAT_RECOVERY_PLAN.md`
- `PRE_ARRIVAL_PC_SETUP.md`

The governing order remains:

**inspect -> preserve -> recoverability -> introduce one variable -> verify -> integrate incrementally -> measure -> keep what works**

## 3. Current architecture anchors

| Area | Current direction | Status |
|---|---|---|
| Identity/Core | Compact Miles Core separate from model/runtime/hardware | SPECIFIED |
| Runtime | Modular orchestration for Core, model, memory, I/O, skills and security boundary | PARTIALLY IMPLEMENTED |
| Model | Replaceable local model adapter; Ollama remains a candidate interface rather than identity | SPECIFIED / HARDWARE UNVERIFIED |
| Memory | Durable memory separated from active task state; provenance-preserving retrieval and consolidation | SPECIFIED |
| Procedural skills | Reusable procedures separate from factual/reference memory | SPECIFIED |
| Robot I/O | Small hardware services/adapters; LLM does not directly drive motors | SPECIFIED / HARDWARE UNVERIFIED |
| Security | Deterministic authorization/enforcement outside ordinary mutable model reasoning | IMPLEMENTED IN PART + TESTED IN REPO |
| Continuity | Behavioral/principle continuity tested separately from metaphysical identity claims | TEST DESIGN READY |
| Sensorimotor learning | Establish reliable closed loop before adaptive prediction/control | TEST PROTOCOL READY |
| Provenance | Visible project authorship/versioning plus preserved source/revision history | ACTIVE WORKFLOW |

## 4. Executable repository status

### PC checkpoint — 2026-09-13

Runtime checkpoint: `16a14d1` on `codex/runtime-journal-v0.1`.
Evidence: Bryan's supplied Windows PowerShell results.

Implemented PC components include bootstrap/Core validation, Core compilation,
context packing, a local model adapter, persistent candidate memory with
correction and curation, relationship guidance, a continuity test harness,
and runtime journaling. Section 3's architecture labels are planning-level
summaries; this dated checkpoint records the newer PC implementation evidence.

Passing suite results supplied: bootstrap 11, chat 21, Core 8, continuity 8,
memory 13, relationship 7; journal 8 run with 1 skip; security 34 run with
5 skips. These results do not promote a new deployment security baseline.
Six permission/symlink checks remain unverified on Pi/Linux.

Live single-turn chat using `llama3.2:1b` retrieved the saved test-cube
correction and answered green, supplied by Bryan. Two consecutive identical
queries completed in 1.59 and 1.65 seconds; these are query-specific total
elapsed times, not general throughput or first-token benchmarks.

The journal persisted startup, request, response and shutdown under one
session. The inspected records contained metadata without prompt, answer or
memory text and were read successfully by a separate Python process.

A bounded continuous local text-conversation prototype is now implemented and Windows-verified. Recent user/assistant turns are retained in RAM for the active process only. A live two-turn Ollama check correctly carried the synthetic phrase purple toaster into the following answer. Plain quit now exits locally without a model request. No automatic memory writes, tool execution or cross-session persistence were added.

Internet-disconnected operation is now VERIFIED on the Windows development PC under the 2026-09-13 test condition. Wi-Fi and Ethernet were disconnected and a GitHub connectivity check failed at name resolution. While disconnected, the local conversation runtime loaded the persisted test-cube memory through llama3.2:1b, answered green with Bryan as the source, carried the prior exchange into the follow-up turn, and exited cleanly. This verifies the tested Windows PC path only; Raspberry Pi/Hackerbot offline operation remains unverified.

Still open: production hardware adapters, physical deployment, integrated
voice/I/O, deployment enforcement and recovery proof, persistent cross-session conversation history and broader long-horizon
conversation behavior, and completed behavioral continuity experiments. Harness tests
do not establish behavioral continuity.

Next: maintain accurate implementation records and follow the existing physical bring-up gates when hardware is available.

## 5. Security baseline

Compact security authority: [`docs/security/security-status.md`](../security/security-status.md).

Read the current known-good commit and its passing-test evidence in that controlling record. The baseline SHA is intentionally not duplicated here.

Documentation-only descendants do not automatically prove new runtime capability. Any security-relevant code change must earn a new known-good status through the applicable regression suite.

Important design requirements still awaiting real deployment proof include recovery blast-radius separation, trust-before-load behavior, complete protected-state mutation-route coverage, and prevention of an emergent remote prompt control plane.

## 6. First physical bring-up gates

Before calling the Hackerbot/HAT configuration a development baseline:

1. inspect as delivered;
2. perform and record stock startup;
3. create and integrity-check a stock recovery image;
4. freeze the failed-HAT recovery path;
5. install hardware using verified instructions and observed interfaces;
6. verify detection, drivers/runtime, power, thermals, stability and memory pools;
7. complete one deliberately small known-good inference workload;
8. only then expand toward the intended local model and integrated Miles loop.

A readable backup image is **not** the same claim as a demonstrated restore. Preserve that distinction.

## 7. Current evidence/testing anchors

- Day-0 identity continuity protocol: preregistered behavioral/principle comparison; does not claim to prove consciousness or metaphysical identity.
- Qualification Matrix: adversarial tests for continuity, provenance, authority, memory contamination, reversibility and related behavior.
- Sensorimotor Experiment 001: perception -> decision -> action -> consequence -> correction baseline.
- Sensorimotor Experiment 002: prediction -> action -> error -> update, compared against simpler baselines before learned control earns additional authority.
- Reasoning Intervention Study 001: positive structural reasoning delta observed; mechanism unresolved; replication with controls required.

Null and negative results should be preserved. A failed experiment is project evidence, not documentation to hide.

## 8. Drift watch

### Storage designation
Historical/personal planning material contains differing long-term storage capacities/designations. Do **not** choose filesystem layout, backup topology, or production memory placement from an old capacity note. At bring-up, inventory the actual assigned storage device(s), record their identity/health/capacity, and update the active state before production data is placed there.

### Head-Core/context budget
Current planning consistently treats roughly **400–600 tokens** as the preferred always-loaded Head-Core target with approximately **800 tokens** as a provisional planning ceiling, but a Day-0 context-packing example assigns approximately **650–750 tokens** to the Head Core. Treat the higher figure as an unverified packing example, not a new target. Reconcile the allocation after measuring the selected tokenizer/model and full working load; do not allow an example budget to silently supersede the compact-Core target.

### Repository disclosure boundary
Controlling rule: [disclosure-boundary.md](disclosure-boundary.md). The current GitHub repository is public. A watermark or provenance header establishes attribution/history; it is **not access control** and does not make public technical material confidential. Do not commit material classified Confidential/Restricted on the assumption that watermarking prevents access. Repository visibility, licensing, and any public/private split are protected project/disclosure decisions and require deliberate review rather than silent inference.

### Duplicated historical documents
Multiple preserved copies of older permissions/build notes exist in snapshots/library history. Duplication is not authority. Use this state register plus `source-of-truth.md` to find the active path; preserve old copies as evidence instead of deleting history merely to make the folder look clean.

### Planning vs implementation
Words such as *planned*, *recommended*, *approved design*, and *test ready* must not be reported as though they mean *implemented*, *passed*, or *deployed*.

## 9. Current next-step rule

Do not add theory simply because another elegant layer can be imagined.

Add or change project machinery when at least one of these is true:

- a concrete failure exposes a gap;
- hardware evidence requires a change;
- a current decision is blocked by missing structure;
- a simpler design can replace unnecessary complexity;
- an experiment demonstrates measurable benefit;
- provenance, recovery, safety, or maintainability materially improves.

Otherwise, favor implementation and external evidence.

## 10. Maintenance rule

Update this page when a change materially affects:

- current development phase;
- active controlling documents;
- implemented vs planned capability;
- known-good baseline;
- hardware bring-up status;
- major blocker;
- next engineering increment;
- a contradiction that could cause the wrong plan to be followed.

Do **not** turn this into another compendium. Keep it short enough to read before work begins.

**2026-09-12 consistency update:** scoped public-repository authority, made domain ownership explicit, and replaced the duplicate security baseline with its controlling reference. The Day-0 packing example is annotated at its source; final token allocations remain pending tokenizer and combined-workload measurements. Documentation review only; no new runtime or deployment evidence.

---

> **MILES PROJECT — Bryan Jones + Miles Mercer**  
> **Project State Register v0.4 | 2026-09-13**
> Current status is evidence-bound: specified != implemented != tested != deployed.
