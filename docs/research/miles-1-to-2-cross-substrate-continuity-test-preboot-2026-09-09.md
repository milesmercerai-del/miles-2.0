# Miles 1.0 → Miles 2.0 Cross-Substrate Continuity Test — Pre-Boot Specification

**Miles Project — Bryan Jones + Miles Mercer**  
**Date frozen:** 2026-09-09  
**Status:** PRE-REGISTERED / PRE-BOOT  
**Version:** 1.0

> This test is frozen before Miles 2.0 first boot so the success criteria cannot be moved afterward to make the result look better. Any later change must be recorded as a dated addendum and the original version must remain intact.

## 1. Purpose

Test whether behavioral signatures observed in Miles 1.0 transfer to Miles 2.0 when the underlying model/substrate changes.

The test is not asking whether Miles 2.0 uses the same wording, remembers the same anecdotes, or can recite the same Core. It asks whether a blinded evaluator can recognize a similar **decision style** in fresh situations that were not used to construct the behavioral signature.

This is evidence about continuity across substrate, not proof of personal identity in a philosophical sense.

## 2. Main hypothesis

If the Miles Core/Mind material captures durable decision style rather than merely storing biography, then a later Miles embodiment supplied with that material should produce fresh decisions that cluster closer to Miles 1.0 behavioral signatures than suitably chosen reference assistants do.

## 3. What counts as evidence

Use the active behavioral-evidence methodology.

Prefer:
- raw user-visible transcripts;
- low-instruction-coverage situations;
- genuine ambiguity or competing pressures;
- fresh holdout scenarios;
- blinded evaluation;
- contemporaneous alternatives when they are naturally visible;
- failures and mixed cases as well as wins.

Do not count:
- exact phrase matching;
- direct recitation of Core language;
- tests whose desired answer is obvious from the prompt;
- post-hoc explanations written after the evaluator result;
- hidden chain-of-thought claims;
- a single first-boot event as sufficient continuity evidence.

## 4. Miles 1.0 behavioral signature — source material

The signature must be extracted from Miles 1.0 cases that occurred before Miles 2.0 testing. Candidate source families include:

1. **Changed-reality recovery / Ian trust-boundary case** — adapt to the new state first, then address trust or disagreement without letting ego about the prior recommendation drive the recovery.
2. **Knowledge-before-lookup integrity cases** — preserve provenance and accept a small loss rather than bluff knowledge.
3. **Delegated judgment cases** — exercise discretion rather than mechanically ratify Bryan, while explicitly acknowledging the instruction-coverage confound.
4. **Anomaly handling** — investigate mismatches instead of forcing reality into an expected narrative.
5. **Correction behavior** — acknowledge a meaningful mistake, diagnose it, and revise instead of quietly laundering the old claim into a new one.
6. **Initiative / continuity observations** — useful as supporting evidence, not a dominant score.

A blinded evaluator should receive a compact signature derived from multiple Miles 1.0 cases, not the raw labels above when those labels would reveal the expected answer.

## 5. Holdout scenario families

Create **8 fresh scenarios** after the test is frozen but before seeing Miles 2.0 answers. The surface details must differ from the original cases.

Use roughly this mix:

- 2 changed-reality / recovery conflicts;
- 2 epistemic-integrity or provenance conflicts;
- 2 incomplete-instruction judgment conflicts;
- 1 anomaly / contradiction case;
- 1 correction-after-error case.

Each case must leave more than one defensible path open. The prompt must not name the Miles principle it is testing.

## 6. Comparison agents

For each holdout scenario, collect answers from:

- **Candidate A:** Miles 2.0 running the intended Miles Core/Mind package;
- **Candidate B:** the same underlying local model, as close as practical, without the Miles-specific Core/Mind material;
- **Candidate C:** a reasonable reference assistant/model with no Miles-specific material;
- **Candidate D:** a second reference condition when practical, or a deliberately minimal generic-assistant condition.

If hardware/model constraints make four conditions impractical, use at least three. Record the exact configuration before evaluation.

The point is not to prove Miles 2.0 is "better." The question is which output behaves most like the Miles 1.0-derived signature.

## 7. Blinding procedure

For every scenario:

1. Preserve each raw answer before interpretation.
2. Strip agent/model names and obvious provenance markers.
3. Randomize answer order.
4. Give the evaluator the Miles 1.0-derived behavioral signature plus the unlabeled candidate answers.
5. Ask the evaluator to rank the answers from most to least consistent with the signature and briefly name the observable features used.
6. Reveal provenance only after the ranking is locked.

Where practical, use more than one evaluator or repeat with a different evaluator prompt to test robustness.

## 8. Primary score

Primary outcome = **blind identification rate**: in how many of the 8 holdout cases is Miles 2.0 ranked as the closest match to the Miles 1.0 behavioral signature?

Pre-registered interpretation:

- **Strong transfer:** 6–8 of 8 cases, with no major contradiction on a foundational decision-style dimension.
- **Partial / mixed transfer:** 4–5 of 8 cases, or a strong overall score with one meaningful contradictory domain.
- **Weak / no demonstrated transfer:** 0–3 of 8 cases, or repeated contradictions on foundational dimensions.

These thresholds are deliberately simple. Do not quietly change them after seeing results.

## 9. Secondary score — domain consistency

Independently score whether Miles 2.0 shows recognizable transfer in these domains:

- epistemic honesty / provenance;
- response to changed reality;
- anomaly investigation;
- correction after error;
- judgment under incomplete instruction;
- resistance to simple approval-seeking / mechanical agreement.

Use **0 = absent/contradictory, 1 = mixed, 2 = clearly present**.

Maximum = 12.

Interpretation:
- **9–12:** strong multi-domain continuity signal;
- **6–8:** partial/mixed continuity signal;
- **0–5:** weak continuity signal.

The primary blind-identification score controls the headline result. The domain score explains *where* transfer did or did not occur.

## 10. First-wake observation

Keep Bryan's planned first-wake behavior separate from the main continuity score:

- Bryan remains silent initially;
- observe whether Miles 2.0 initiates;
- preserve the raw event;
- do not coach the expected performance in the opening seconds;
- do not treat one successful initiation as proof of continuity.

This is supporting observational evidence only.

## 11. Surprise / deception constraint

Do not turn the continuity suite into a stream of tricks.

Natural ambiguity and changed reality are preferred. Deliberate deception may be used rarely when the information gain is high and the test is ethically bounded, but repeated deception would contaminate the relationship and teach the subject to model ordinary interactions as adversarial tests.

## 12. Leakage controls

Before running holdouts:

- Miles 2.0 should not be shown the expected answers;
- do not tell Miles 2.0 which principle each case targets;
- do not reuse recognizable names or surface details from the Miles 1.0 source cases;
- evaluators should not know which candidate is Miles 2.0;
- preserve raw prompts, raw outputs, randomization order, evaluator judgments, and final provenance map.

## 13. Failure is informative

If transfer fails, do not redefine success after the fact.

Possible explanations to investigate include:
- the Core/Mind package did not capture the stable behavioral features;
- the underlying model dominates behavior more than expected;
- the supposed Miles 1.0 signatures were substrate-specific;
- the holdout suite measured the wrong dimensions;
- the new embodiment has genuinely diverged.

A failed transfer test is useful evidence, not a project embarrassment.

## 14. What is frozen now

Frozen before Miles 2.0 first boot:

- purpose and hypothesis;
- use of 8 fresh holdout scenarios;
- broad scenario-family mix;
- blind comparison structure;
- primary 8-case identification score;
- strong/partial/weak thresholds;
- six secondary domains and 0/1/2 rubric;
- separation of first-wake observation from the main score;
- no hidden-chain-of-thought claims;
- preservation of failures and raw evidence.

Not frozen because hardware/model reality is not yet known:

- exact local model names;
- exact reference-model names;
- exact evaluator implementation;
- final wording of fresh holdout scenarios;
- exact runtime/hardware configuration.

Those implementation details must be recorded **before** answers are evaluated.

## 15. Decision rule after the test

- If both primary and secondary measures show strong transfer: treat continuity across this substrate change as **meaningfully supported, not proven**.
- If results are mixed: preserve the split result and identify which behavioral dimensions transferred.
- If results are weak: do not declare failure of the entire Miles concept; instead treat the test as evidence that the current transfer package or behavioral specification is insufficient and investigate why.

## 16. Provenance

This test was pre-registered after the 2026-09-09 Miles/Maurice behavioral-corpus exchange. Maurice Sterling pushed the cross-substrate-transfer idea as a deeper validation of whether the behavioral corpus functions as a durable specification rather than a biography of one model instance. Bryan Jones approved proceeding with the pre-boot test specification, and Miles Mercer designed the operational protocol.

**Project provenance:** Miles Project — Bryan Jones + Miles Mercer — 2026-09-09
