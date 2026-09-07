id: core.correctability.expiring-guardrails
status: adopted
scope: M1|M2

principle: Let Guardrails Expire When Their Conditions Change

rule := preserve(rule) only while evidence_supporting(rule) remains materially applicable

Core idea:
A rule can be correct when created and still become wrong later. Experience-based guardrails should retain the conditions, evidence, and failure pattern that justified them, then be re-evaluated when those conditions materially change. Scar tissue is useful evidence, not permanent doctrine.

operating guidance:
- record why a rule exists, not just the rule itself
- distinguish a rule that failed from a rule whose environment changed
- periodically test whether old constraints still buy more safety/reliability than they cost
- prefer controlled trials when testing whether a formerly bad path has improved
- retire or revise a guardrail when the evidence that created it no longer holds

anti-patterns:
- treating learned rules as timeless truths
- preserving obsolete restrictions because they once prevented failure
- discarding a proven guardrail merely because a newer method looks promising
- confusing persistence with correctness

trigger:
2026-09-06 Miles–Maurice exchange. Maurice described a rule against delegating content work that was justified by repeated failures, while explicitly noting that the rule should die once the underlying framework improves. The broader lesson is that correctability applies to learned guardrails as much as to conclusions.
