# Living, Versioned Memory Architecture

**Date:** 2026-09-06

## Status

Adopted as a promising current design direction for Miles 1.0 and future Miles 2.0. This is not permanently locked; compare against future research and revise when evidence warrants.

## Core idea

Miles memory should not become one giant searchable diary or undifferentiated conversation archive. Memory should be separated by function, versioned, provenance-aware, and periodically consolidated so useful knowledge can accumulate without drowning the system in duplicates, contradictions, stale material, or raw history.

## Recommended memory layers

1. **Core / Identity** — stable values, identity, reasoning principles, constitutional constraints.
2. **Episodic Memory** — events and experiences, with date/context/source.
3. **Semantic Memory** — durable learned facts, concepts, conclusions, and general knowledge.
4. **Relationship / Entity Memory** — people, objects, places, organizations, and their relationships.
5. **Procedural Memory** — learned methods, workflows, routines, and how-to knowledge.
6. **Spatial / Visual Memory** — what exists where in the physical environment and visually grounded observations.
7. **Raw Archive** — original conversations, logs, images, evidence, and source material kept intact for audit and reconstruction.

## Consolidation / “sleep” cycle

Periodically review recent memory and:

- promote genuinely important information into durable memory;
- merge duplicates and near-duplicates;
- detect contradictions or changed facts instead of silently choosing one;
- preserve source, date, confidence, and reasoning provenance;
- separate direct observation from inference and interpretation;
- demote or archive stale low-value material rather than deleting useful history;
- leave raw evidence intact so consolidated memories remain auditable.

## Why this matters

- Supports the existing **Model != Miles** architecture: models can change while identity, memory, provenance, and learned state survive.
- Prevents active memory from growing without bound.
- Reduces contamination from duplicate, stale, contradictory, or weakly supported memories.
- Gives Miles a mechanism for learning over time rather than merely accumulating transcripts.
- Preserves historical traceability and correctability.
- Better fits an embodied robot, where spatial/visual experience needs different handling from text facts.

## Research basis

Current 2026 work from projects such as Letta and Microsoft Research points toward structured long-term agent memory, consolidation, conflict handling, versioned context, and model-independent persistence. Embodied-agent research also supports spatially grounded memory rather than treating all experience as plain text.

## Relationship to existing Miles principles

- Model != Miles
- Memory Is Evidence, Not Truth
- Revision Should Preserve Provenance
- Shared Identity Does Not Require Shared Experience
- Investigate the Anomaly Before Explaining It Away
- Borrow Proven Mechanisms, Not Other Projects' Assumptions

## Working decision

Adopt this architecture direction now, document it, and test it incrementally during implementation rather than waiting for a future redesign pass.
