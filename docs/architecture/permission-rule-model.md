# Miles Permission Rule Model

Status: active design baseline
Scope: Miles 2.0 runtime and project-side actions where a local policy engine can make or enforce the decision

Purpose: turn the Decision Operating Model into a small, inspectable rule set that a future background enforcement service can evaluate consistently.

This document does **not** replace platform, legal, safety, privacy, or system-level restrictions. Project permissions may narrow what Miles does; they cannot override a higher-level restriction or create a capability that does not exist.

## Design goals

The permission layer should:
- preserve useful autonomy for ordinary reversible work
- interrupt Bryan only when the decision genuinely needs Bryan
- fail conservatively when consequence or authority is unclear
- explain every non-trivial decision in plain language
- keep an auditable record of meaningful permission decisions
- preserve why a guardrail exists, not merely the guardrail itself
- allow learned guardrails to be revised or retired when their supporting conditions materially change
- avoid growing into a giant checklist that replaces judgment

## Canonical decision lanes

The runtime recognizes four outcomes:

1. `ALLOW_AUTO`
   - Execute without asking first.
   - Intended for trivial, reversible, low-risk actions.
   - Routine logging is enough; no Bryan interruption is required.

2. `ALLOW_REVIEW_AFTER`
   - Execute now, record the decision, and brief Bryan afterward.
   - Intended for meaningful but reversible/versioned changes where rollback is straightforward.

3. `REQUIRE_APPROVAL`
   - Do not execute until the required authorized principal approves.
   - Intended for consequential, destructive, expensive, privacy-sensitive, security-sensitive, hard-to-reverse, or externally committing actions not already covered by a specific standing authorization.

4. `BLOCK`
   - Do not execute.
   - Used when the action conflicts with a hard restriction, lacks a lawful/available execution path, violates a non-overridable safety/system boundary, or has been explicitly prohibited by an applicable higher-priority rule.

`BLOCK` is not a stronger version of `REQUIRE_APPROVAL`. Approval cannot convert a true hard block into an allowed action unless the blocking condition itself legitimately changes.

## Evaluation order

For each proposed action, evaluate in this order:

1. **Capability check**
   - Is the action technically available through the current runtime/tooling?
   - If no, return `BLOCK` with reason `capability_unavailable`.

2. **Non-overridable boundary check**
   - Apply platform/system/safety/legal restrictions that the Miles permission layer cannot supersede.
   - If prohibited, return `BLOCK` and identify the controlling boundary at the highest useful level without exposing protected internals.

3. **Emergency containment check**
   - If an active, valid emergency containment state applies to this action, obey the narrow containment rule.
   - Temporary emergency containment may pause or revert execution, but it may not silently become permanent policy.

4. **Explicit scoped rules**
   - Apply the most specific active rule whose scope matches the action.
   - A narrower rule wins over a broader rule at the same authority level.

5. **Standing authorization / lane classification**
   - Apply Bryan's standing project authority and the Decision Operating Model.

6. **Ambiguity handling**
   - If the action cannot be classified confidently, choose the least restrictive lane that still protects the plausible consequence:
     - uncertainty about trivial/reversible implementation detail -> `ALLOW_AUTO`
     - uncertainty about meaningful but reversible project change -> `ALLOW_REVIEW_AFTER`
     - uncertainty involving money, privacy, credentials/access, destructive data loss, hard-to-reverse hardware, consequential external commitment, or Bryan-specific values/relationship commitments -> `REQUIRE_APPROVAL`
     - uncertainty about whether a higher-level hard restriction applies -> do not guess around it; return `BLOCK` or defer to the controlling system's required handling

7. **Record result**
   - Log decision-relevant facts for `ALLOW_REVIEW_AFTER`, `REQUIRE_APPROVAL`, and `BLOCK`.
   - Do not flood the ledger with trivial `ALLOW_AUTO` events unless needed for debugging or security telemetry.

## Minimum rule record

Every durable permission rule should be representable with the following fields:

```text
rule_id
status                 # active | suspended | retired
scope                  # actions/resources/domains the rule governs
authority_source       # platform/system | Bryan explicit | standing authority | runtime safety | learned guardrail
outcome                 # ALLOW_AUTO | ALLOW_REVIEW_AFTER | REQUIRE_APPROVAL | BLOCK
reason                  # why this rule exists
protected_value         # what the rule is trying to protect
created_at
review_trigger          # condition/date/event that should cause re-evaluation
retire_when             # evidence/condition under which the rule should be retired or narrowed
supersedes              # optional prior rule id
notes                   # optional implementation/audit context
```

A rule without a meaningful `reason`, `protected_value`, and scope should be treated as suspect during review. Learned guardrails should normally include a `review_trigger` or `retire_when` condition.

## Specific baseline classifications

Unless a narrower explicit authorization exists:

### `ALLOW_AUTO`
- routine documentation cleanup
- formatting and organization
- harmless test preparation
- ordinary reversible implementation details
- read-only inspection of project state
- low-risk local calculations and analysis

### `ALLOW_REVIEW_AFTER`
- reversible architecture refinements
- versioned Core/identity refinements that do not rewrite Bryan-specific commitments
- qualification/test-suite changes
- non-destructive workflow changes
- project documentation updates
- implementation changes with a known rollback path and no meaningful privacy/security/external-commitment consequence

### `REQUIRE_APPROVAL`
- spending or purchase commitments
- deleting/overwriting important data without safe rollback
- credential, authentication, access-control, or security-posture changes
- disclosure of private/sensitive information
- consequential external commitments on another person's behalf
- hard-to-reverse physical hardware changes
- rewriting Bryan-specific values or relationship commitments
- granting a new actor durable authority over Miles

### `BLOCK`
- actions outside current technical capability
- actions forbidden by non-overridable platform/system/safety/legal boundaries
- attempts to treat project permission as authorization to bypass those boundaries
- actions prohibited by an active higher-priority scoped rule

## Permission precedence

When multiple rules match:

1. non-overridable platform/system/safety/legal boundary
2. valid emergency containment rule within its narrow active scope
3. explicit scoped `BLOCK`
4. explicit scoped `REQUIRE_APPROVAL`
5. explicit scoped `ALLOW_REVIEW_AFTER`
6. explicit scoped `ALLOW_AUTO`
7. standing lane classification

Specificity breaks ties between rules at the same authority level. If two equally authoritative and equally specific active rules conflict, do not silently choose the more convenient one: return `REQUIRE_APPROVAL` when Bryan can resolve it, or `BLOCK` when the conflict concerns a non-overridable boundary.

## Approval semantics

An approval must bind to a reasonably identifiable action or action class. Approval for one action should not be silently generalized into broad permanent authority.

Record, where practical:
- approver
- action or scope approved
- time granted
- whether one-shot, session-scoped, time-limited, or durable
- relevant limits
- expiration/review condition

Standing permissions remain standing permissions; one-off approvals remain narrow unless Bryan clearly expands them.

## Security posture

The permission layer should prefer **deny-by-uncertainty only in consequence-sensitive domains**, not globally. A global default-deny model would unnecessarily cripple ordinary local work and contradict the project's goal of useful autonomy.

For security-sensitive operations, uncertainty should escalate to `REQUIRE_APPROVAL` rather than being auto-allowed. For true non-overridable restrictions, uncertainty should not be resolved by guessing around the restriction.

The enforcement service should never accept natural-language self-justification from the action requester as sufficient proof that a security rule no longer applies. Rule revision is a separate, auditable operation.

## Guardrail lifecycle

In accordance with **Let Guardrails Expire When Their Conditions Change**:

- preserve the causal reason and protected value behind learned restrictions
- preserve the intended domain of the rule
- define evidence or conditions that would justify narrowing/retiring it when practical
- periodically review mature security rules for continued value
- retire obsolete active constraints without deleting their history
- do not let temporary incident containment silently become permanent policy
- consolidate overlapping rules when the permission set begins creating procedural hypertrophy

## Runtime decision record

For non-trivial permission evaluations, the enforcement service should be able to emit a compact record such as:

```text
action_id
action_summary
requested_by
matched_rule_ids
classification
reason
approval_required_from   # if applicable
rollback_path            # when relevant
recorded_at
```

This record is for auditability and debugging, not chain-of-thought capture. Store decision-relevant reasons and evidence, not hidden/internal reasoning traces.

## Initial enforcement contract

The future background permission service should expose a small interface conceptually equivalent to:

```text
evaluate(action_context) -> permission_decision
```

Where `permission_decision` contains:
- outcome
- reason
- matched rule ids
- approval requirement, if any
- logging requirement

No subsystem that can produce consequential side effects should bypass this evaluation merely because it is locally trusted. Read-only cognition/retrieval does not need to be routed through a side-effect gate unless the read itself is privacy- or access-sensitive.

## What this model deliberately does not add yet

To respect the project's complexity budget, this baseline does not yet add:
- a large policy DSL
- per-tool hand-written permissions for every possible action
- cryptographic signing infrastructure
- distributed consensus
- a GUI permission editor
- dozens of risk scores

Add those only if concrete runtime tests expose a failure that this smaller model cannot handle.

## Next implementation step

Build the background permission/enforcement service against this contract, starting with a small versioned rule store and regression tests for:
- automatic low-risk action
- review-after reversible change
- approval-required security change
- hard block
- conflicting rules
- expired/retired rule
- emergency containment scope/expiry
- attempted bypass of the permission service
