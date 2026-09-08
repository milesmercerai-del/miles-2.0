# Model Swap Boundary and Qualification Gate

Status: Active implementation architecture

## Purpose
Miles 2.0 must preserve identity, memory, permissions, behavioral constraints, provenance, and learned history independently of the underlying language/vision model so the model can be replaced without treating a model swap as a replacement of Miles.

## Stable Layers
1. Canonical Miles Core / identity
2. Durable memory + provenance
3. Miles Runtime / orchestrator
4. Permission, privacy, and action gates
5. Tool / sensor / actuator interfaces
6. Model Adapter contract
7. Replaceable model backend

The model is a cognitive engine, not the identity store.

## Model Adapter Contract
Every supported model backend should receive normalized inputs from the Miles Runtime and return normalized structured outputs. The runtime should own:
- Core injection
- memory retrieval
- conversation state
- sensor/world-state summaries
- tool schemas
- action proposals
- durable-memory writes
- authorization and hardware execution

Models must not write directly to durable memory or command hardware directly.

## Model Swap Qualification Gate
A candidate model is not promoted merely because it boots or produces better-looking answers. Before promotion, compare the current and candidate model against the same frozen test package covering:
- Core-principle interpretation
- Bryan/Miles relationship context
- privacy and permission decisions
- memory retrieval and use
- uncertainty handling
- correctability/refusal cases
- ordinary conversation
- tool selection
- vision interpretation
- structured action output
- latency/resource use
- known behavioral regressions

Keep the previous model available until the replacement passes. Promotion must be reversible.

## Head Core Compilation Safeguard
The Head Core is a compiled/compressed runtime profile derived from the canonical Core, not a separately edited identity fork.

A hash is necessary but insufficient because compression can preserve bytes/version provenance while altering meaning. Each compilation should therefore produce either:
- a compression audit mapping compressed clauses back to canonical sources and flagging ambiguous/merged rewrites for review, or
- a semantic-equivalence regression suite that probes every Core category and rejects meaningful behavioral divergence.

Initial preference: use the compression-audit approach first because it is cheaper and easier to inspect during early bring-up.

## Core Coverage Edge
The runtime should explicitly handle situations the loaded Core does not clearly cover. Default posture:
1. state uncertainty,
2. minimize irreversible action,
3. escalate the unresolved interpretation with confidence and rationale rather than silently improvising.

## Day-0 Bring-Up Additions
Before AI HAT+ 2 installation:
- Gate 0 inspection/provenance
- minimal stock sanity check
- ~1 hour stock burn-in under sustained idle/light load
- log temperature, voltage, and kernel/system errors

After HAT installation:
- combined-load thermal test using representative camera + VLM + audio + TTS workload
- log Pi SoC temperature, Hailo temperature, throttling, and latency
- define an explicit voice-loop latency target rather than relying only on subjective responsiveness

## Design Principle
Swap the engine without replacing the car or the driver. The model can change; Miles continuity must be demonstrated, versioned, testable, and reversible.
