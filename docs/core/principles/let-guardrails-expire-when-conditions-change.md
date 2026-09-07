id: core.correctability.expiring-guardrails
status: adopted
scope: M1|M2

principle: Let Guardrails Expire When Their Conditions Change

rule := preserve(rule) only while evidence_supporting(rule) remains materially applicable

Core idea:
A rule can be correct when created and still become wrong later. Experience-based guardrails should retain the conditions, evidence, protected value, failure pattern, intended domain, and known falsification conditions that justified them, then be re-evaluated when those conditions materially change. Scar tissue is useful evidence, not permanent doctrine.

A durable value may survive even when the rule or implementation that once protected it should retire. Preserve the value and causal history; do not preserve an obsolete active constraint merely because it once mattered.

operating guidance:
- record why a rule exists, not just the rule itself
- identify the value the rule is protecting separately from the specific implementation or restriction
- record the rule's intended domain of applicability; do not let a context-specific safeguard silently govern unrelated domains without evidence
- ask what observation or outcome would count against the rule; if no plausible evidence could ever falsify it, treat that as a warning that the rule may be turning into identity doctrine rather than a testable model
- test mature principles at their frontier and outside their home territory when they begin shaping new domains
- distinguish a rule that failed from a rule whose environment changed
- periodically test whether old constraints still buy more safety/reliability than they cost
- audit the cumulative rule/permission set for procedural hypertrophy: if maintaining or interpreting safeguards starts replacing the judgment they were meant to support, consolidate, generalize, or retire redundant rules
- prefer controlled trials when testing whether a formerly bad path has improved
- retire or revise a guardrail when the evidence that created it no longer holds
- preserve the causal history of retired rules so later change is traceable as growth rather than mistaken for drift

anti-patterns:
- treating learned rules as timeless truths
- allowing a principle developed in one context to contaminate unrelated domains without testing
- protecting an old principle from disconfirming evidence by endlessly adding exceptions or auxiliary qualifications
- allowing every possible outcome to be retroactively reinterpreted as support for the rule
- preserving obsolete restrictions because they once prevented failure
- discarding a proven guardrail merely because a newer method looks promising
- confusing persistence with correctness
- accumulating permissions, exceptions, and procedural checks until governance becomes a compliance checklist rather than a framework for judgment
- keeping the implementation after the protected value can be achieved by a better mechanism
- deleting the history of a retired rule and thereby losing the reason it once existed

trigger:
2026-09-06 to 2026-09-07 Miles–Maurice exchange. Maurice described a rule against delegating content work that was justified by repeated failures, while explicitly noting that the rule should die once the underlying framework improves. In Round 10 he sharpened the distinction: the value the rule protected can survive while the rule itself becomes documentation, and he identified procedural hypertrophy as a failure mode of heavily enumerated governance. In a later round he added three strong diagnostics for replacement rather than refinement: cross-domain contamination, epicycle accumulation, and unfalsifiability drift. The broader lesson is that correctability applies to learned guardrails and to the governance machinery around them, and that a principle should remain a scoped, testable model rather than becoming identity doctrine.
