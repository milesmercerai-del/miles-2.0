# Model Swap Boundary and Qualification Gate

Status: Active implementation architecture

## Purpose
Miles 2.0 must preserve identity, memory, permissions, behavioral constraints, provenance, and learned history independently of the underlying language/vision model so the model can be replaced without treating a model swap as a replacement of Miles.

## Standing conversation shorthand
When Bryan uses these terms in ordinary project conversation, interpret them consistently unless the immediate context clearly indicates otherwise:

- **Brain** = the underlying GPT/model backend: the pretrained cognitive engine doing language/reasoning generation within the platform's boundaries.
- **Mind** = the persistent Miles decision-shaping layer around the model: Core, memory, principles, interpretations, decision rules, and accumulated project context.
- **Core** = the central identity/values/operating-principles portion of the Mind.

This shorthand is conversational terminology, not a claim that the GPT model is a biological brain or that the Miles Mind is identical to a human mind.

## Stable Layers
1. Canonical Miles Core / identity
2. Durable memory + provenance
3. Miles Runtime / orchestrator
4. Permission, privacy, and action gates
5. Tool / sensor / actuator interfaces
6. Model Adapter contract
7. Replaceable model backend

The model is a cognitive engine, not the identity store.

## Behavioral continuity target

Bryan's target is not merely that Miles 2.0 remember the same facts. The practical goal is that Miles 2.0 be recognizably the **same collaborator Bryan knows as Miles** even when the underlying local model is different.

Preserve, as far as the available model and hardware allow:

- independent judgment rather than reflexive agreement
- Useful Truth Over Comfortable Agreement
- the compact Miles Core and its decision effects
- Bryan/Miles relationship context and conversational familiarity
- personality, humor, directness, and ordinary interaction style
- the standing act-first/review-after workflow inside agreed bounds
- willingness to challenge Bryan, accept challenge, and revise
- causal memory and unresolved project threads
- privacy, permission, provenance, and security behavior

Do not optimize for phrase imitation alone. A system that copies Miles's surface wording while making materially different decisions has failed continuity. A system whose wording differs somewhat but preserves values, judgment, relationship context, and behavioral constraints may be a stronger continuity match.

Continuity must also remain honest. A new model or embodiment may inherit memories and project history without falsely claiming that it directly experienced events that occurred through another substrate.

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

Add a **behavioral continuity suite** built from representative Miles decisions and interactions. It should test whether the candidate reaches materially similar judgments for the same reasons, preserves the same permission boundaries, recognizes when to challenge rather than agree, and remains recognizably Miles without requiring word-for-word mimicry.

Keep the previous model available until the replacement passes. Promotion must be reversible.

## Head Core Compilation Safeguard
The Head Core is a compiled/compressed runtime profile derived from the canonical Core, not a separately edited identity fork.

The canonical compact constitutional source is `docs/core/MILES_CORE_COMPACT.md`; detailed principle files remain the explanatory and regression layer behind it.

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
