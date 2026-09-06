# Miles 2.0

Version-controlled technical development for the Miles 2.0 AI assistant project: runtime, memory systems, skills, tests, documentation, and hardware integration code.

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

This repository is intended to become the technical source of truth for implementation work as Miles 2.0 develops.
