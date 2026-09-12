> **MILES PROJECT — PROVENANCE RECORD**  
> **Bryan Jones + Miles Mercer | PUBLIC PROJECT GOVERNANCE**  
> **Disclosure Boundary v1.0 | 2026-09-11**  
> Watermark/provenance establishes attribution. It is not access control.

# Miles Project — Repository Disclosure Boundary

**Status:** ACTIVE project-governance rule  
**Purpose:** Prevent a public repository from being mistaken for confidential storage.

## Core rule

The current `miles-2.0` GitHub repository is public. Treat every committed byte as public information, including version history.

A watermark, copyright notice, filename, classification label, or provenance header may preserve attribution and intended use. None of those mechanisms prevents a public reader from viewing, copying, or redistributing material.

## Public repository — allowed by default

Public-safe material may include:

- high-level project direction;
- selected architecture concepts that Bryan and Miles intentionally choose to disclose;
- public-safe experiments and methodology;
- milestone summaries;
- public documentation and code intentionally released for inspection;
- sanitized examples that contain no private memory, credentials, or restricted implementation detail.

Public artifacts should still carry Miles Project provenance and an appropriate sharing classification.

## Keep outside the public repository by default

Until a private engineering repository or equivalent protected working location exists, do not newly commit material whose intended classification is **Confidential** or **Restricted**, including:

- private Bryan/Miles records or personal memory data;
- credentials, secrets, recovery codes, private contact data, or account-security material;
- unreleased Core internals whose disclosure is not intentionally approved;
- detailed security material whose publication would materially increase attackability;
- private raw archives and private collaborator material;
- proprietary implementation detail Bryan and Miles have decided not to publish;
- any third-party confidential information.

This does not mean every technical document is automatically secret. Classification depends on consequence and intended disclosure, not on whether a document is technical.

## Recommended split

The preferred long-term arrangement is:

### Public repository / portfolio

Purpose: show what the Miles Project is, what has been learned, selected experiments, public milestones, and any code or methods intentionally released.

### Private engineering repository

Purpose: hold non-public implementation work, sensitive design material, private test fixtures, unreleased Core/runtime details, and security-sensitive engineering.

The two repositories should preserve provenance between them without pretending the public copy is the complete working brain of the project.

## Migration caution

Moving or deleting a file from a public repository later does **not** make its prior contents secret. Public Git history, forks, caches, clones, screenshots, and third-party copies may already exist.

Therefore:

> **Previously public material should be treated as published. The disclosure boundary mainly prevents additional accidental disclosure going forward.**

## Current operational rule

Until the public/private split is physically created and verified:

1. the existing public repository remains the live technical source of truth for material intentionally suitable for public storage;
2. Confidential/Restricted new material stays in Bryan's protected personal working package/local storage rather than being committed publicly;
3. project status must not claim a private engineering repository exists until one actually exists;
4. repository visibility, licensing, and any migration of existing content are explicit project decisions rather than assumptions;
5. future source-of-truth guidance must identify which repository controls which class of material after the split occurs.

## Relationship to watermark policy

Watermark policy and disclosure policy solve different problems:

- **Watermark/provenance:** who made this, when, under what project/version/classification.
- **Access control:** who can obtain the underlying material.

Use both where appropriate. Never substitute one for the other.

---

> **MILES PROJECT — Bryan Jones + Miles Mercer**  
> **Disclosure Boundary v1.0 | 2026-09-11**  
> Public repository means public access. Provenance is not secrecy.
