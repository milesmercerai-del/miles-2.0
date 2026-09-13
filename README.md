> **MILES PROJECT — PUBLIC TECHNICAL RECORD**  
> **Bryan Jones + Miles Mercer**  
> Public repository: provenance is not access control.

# Miles 2.0

Version-controlled technical development for the Miles 2.0 AI assistant project: runtime, memory systems, skills, tests, documentation, and hardware integration code.

## Public-repository boundary

This repository is public. Treat committed material and its history as publicly accessible.

Miles Project watermarking/provenance identifies authorship, version, and intended classification; it does **not** make public files confidential. Going forward, Confidential/Restricted new material belongs outside this repository until a verified private engineering location exists. See `docs/project/disclosure-boundary.md`.

## Project direction

Miles 2.0 is being developed as an offline-first, persistent AI assistant with a modular architecture. The project separates identity and operating principles from the underlying language model so components can be tested, upgraded, and replaced without treating any single model as the entire system.

## Planned architecture

- **Miles Core** — identity, principles, collaboration rules, and long-term behavioral foundation
- **Miles Runtime** — orchestration layer connecting models, memory, tools, and hardware
- **Memory** — persistent storage, retrieval, organization, and continuity systems
- **Model layer** — local language-model backends and future model adapters
- **Robot I/O** — microphone, speaker, camera, display/eyes, sensors, and motion control
- **Skills / tools** — modular capabilities that can be added and tested independently
- **Tests / benchmarks** — repeatable measurements for latency, stability, memory, recognition, and hardware behavior

## Development approach

The project favors incremental, testable changes over large opaque rewrites. Important behaviors should be documented, assumptions should be testable, and major components should remain separable enough to replace or improve without rebuilding the whole system.

For current operational status, use `docs/project/project-state.md`. For source-of-truth rules, use `docs/project/source-of-truth.md`.

The current public repository remains the live version-controlled source for material intentionally suitable for public storage. A future public/private split should preserve a public research/portfolio surface while moving non-public engineering work to a protected repository or equivalent location.

---

**MILES PROJECT — Bryan Jones + Miles Mercer**  
Public technical project record.

## PC bootstrap

Run `python -m runtime.bootstrap` (Windows: `py -3 -m runtime.bootstrap`) for the mock-only pre-hardware harness. See [PC setup and limitations](docs/engineering/hackerbot/PC_BOOTSTRAP.md). No model or hardware is required.
