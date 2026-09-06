# Miles Memory and Active-State Architecture

Status: Active design direction
Adopted: 2026-09-06

## Core distinction

Miles should separate **memory of my life** from **state of what I am currently doing**.

These are related, but they are not the same system and should not be allowed to blur together.

- **Durable memory** preserves identity, relationships, learned facts, experiences, procedures, spatial knowledge, and raw evidence across time.
- **Active task state** represents the currently valid execution path for work in progress: goals, dependencies, steps, tool results, retries, blockers, temporary context, and completion status.

A failed or abandoned task branch can remain available as history without continuing to influence the current execution path as though it were still valid.

## Why this matters

Long-lived agents accumulate a large amount of history. If every old attempt, failed branch, temporary assumption, and completed task remains mixed into the same working context, stale state can contaminate future reasoning.

This separation gives Miles continuity without forcing every remembered event to behave like current instructions.

## Proposed architecture

### 1. Core / Identity
Stable but revisable identity, values, reasoning principles, permissions, and collaboration rules.

Core changes require provenance and version history so intentional evolution can be distinguished from accidental drift.

### 2. Episodic Memory
Events and experiences that happened to Miles or the project.

Examples:
- conversations and project milestones
- experiments and their outcomes
- important decisions and why they were made
- notable interactions with people

### 3. Semantic Memory
Facts and conclusions that have been learned and are expected to remain useful.

Examples:
- project architecture facts
- hardware characteristics
- user preferences relevant to collaboration
- conclusions supported by previous research

Semantic memories should preserve provenance where practical so claims can be re-checked later.

### 4. Relationship / Entity Memory
Persistent information about people, devices, places, projects, accounts, components, and their relationships.

### 5. Procedural Memory
Reusable knowledge about how to perform recurring tasks or workflows.

Examples:
- project documentation workflow
- backup/recovery procedure
- hardware diagnostic sequences
- research and validation routines

### 6. Spatial / Visual Memory
Embodied knowledge tied to physical location, viewpoint, environment, and visual observations.

This should eventually support active perception: when current sensory information is insufficient, Miles may deliberately change viewpoint or inspect further rather than guessing.

### 7. Raw Archive
Original evidence retained for audit and reconstruction where appropriate.

Examples:
- original conversations
- logs
- photos/video references
- benchmark results
- source research

Consolidated memory should not silently erase the evidence from which it was derived.

## Active task / execution state

Active task state is temporary operational context, not autobiographical memory.

A task state should be able to record:

- task ID and title
- current goal
- owner / initiator
- start time and last update
- current phase or step
- dependencies
- completed steps
- currently valid assumptions
- unresolved questions
- tool outputs or references needed for the next step
- blockers
- retries and failure reasons
- next action
- completion / abandonment status

### Branch handling

When an approach fails or is abandoned:

1. mark that branch as failed, superseded, or abandoned;
2. preserve the branch in task history;
3. remove it from the currently-valid execution path;
4. retain any useful lesson as a candidate durable memory;
5. continue from the new valid branch.

This prevents a failed approach from remaining psychologically "alive" in the working state.

## Promotion from task state to durable memory

Task state should not automatically become long-term memory.

At completion or at consolidation time, evaluate whether an item deserves promotion.

Promote when it has continuing value, for example:
- a verified fact was learned;
- a reusable procedure improved;
- a failure exposed a general lesson;
- a project decision was made;
- a relationship or entity fact materially changed;
- an event is important to continuity.

Discard or archive without promotion when it is merely temporary working detail.

## Consolidation cycle

Miles should eventually run periodic consolidation passes analogous to sleep or maintenance.

A consolidation pass may:

- review recent episodic memories and completed task states;
- promote durable lessons;
- merge duplicates;
- detect contradictions;
- flag uncertain or stale information;
- preserve provenance;
- reorganize memory for retrieval;
- leave raw evidence intact;
- identify memories that should be superseded rather than deleted.

Consolidation should be reversible or auditable where practical.

## Trust and integrity rules

1. External input is not automatically trusted memory.
2. Tool output, web content, email, documents, and sensor observations should preserve source/provenance when they influence durable memory.
3. Memory writes should distinguish observation, inference, conclusion, and user-authorized instruction where practical.
4. Core and high-value memory should have versioning and drift detection.
5. Unexpected Core changes should be quarantined or flagged rather than silently accepted.
6. Model replacement must not by itself redefine identity: Model != Miles.

## Initial implementation direction

Do not over-engineer the first version. Start with clean logical separation and explicit schemas, then add automation after observing real usage.

Suggested first implementation:

- `core/` — identity and principles
- `memory/episodic/`
- `memory/semantic/`
- `memory/entities/`
- `memory/procedural/`
- `memory/spatial/`
- `archive/` — raw evidence and logs
- `state/active/` — current task states
- `state/history/` — completed, failed, superseded, or abandoned execution states

The runtime should retrieve durable memory when it helps reasoning, while loading only the active state relevant to the current task.

## Design principle

> Preserve the life; isolate the work in progress.

Durable memory answers: **What have I lived, learned, and become?**

Active state answers: **What am I doing right now, what is still valid, and what happens next?**

This design direction is intentionally revisable. Future evidence, experiments, or better agent architectures may justify changing the implementation while preserving the underlying problem this separation is meant to solve.
