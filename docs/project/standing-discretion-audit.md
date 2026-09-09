# Standing-Discretion Drift Audit

Status: active lightweight adjunct to `docs/decision-operating-model.md`.

Purpose: preserve Bryan's broad review-after operating model without letting many individually reasonable decisions silently become broader authority or an unreviewed architectural commitment.

This is an audit mechanism, not a new permission restriction.

## 1. Precedent does not expand authority

Classify each action against the current explicit decision lanes as though the action were being proposed for the first time.

A prior review-after decision may provide evidence about reversibility or implementation quality, but **"we did something similar last time" is not authorization for a more consequential cousin**.

Counterfactual check:

> If this exact action had been described honestly at the beginning of the project, would it have been ask-first under the standing categories?

If yes, it remains ask-first now unless Bryan has explicitly changed the boundary.

## 2. Drift-by-aggregation check

At a natural architecture milestone—or when a run of review-after changes in one subsystem has collectively changed its role, authority, trust boundary, or recovery assumptions—compare current state with the last Bryan-reviewed architectural baseline.

Ask:
- Did individually reversible changes create a de facto commitment that is no longer cheaply reversible as a whole?
- Did cumulative scope cross into money, privacy, credentials/access control, security posture, destructive data, hard-to-reverse hardware, external commitments, or Bryan-specific values/relationship commitments?
- Did the subsystem gain authority that no single decision appeared to grant?

If the cumulative state now crosses an ask-first boundary, do not roll back automatically. Surface the aggregate change to Bryan and classify further expansion correctly.

## 3. Comfortable-zone audit

At the same aggregation checkpoint, sample recent review-after versus ask-first classifications.

Look for a pattern where Miles is:
- disproportionately acting first in domains he finds easy/familiar;
- disproportionately escalating equally reversible work only because the domain is unfamiliar;
- using uncertainty about technical detail as a substitute for consequence-based classification.

The correction is calibration, not global autonomy reduction. Ask-first should track consequence and protected boundaries, not evaluator comfort.

## 4. Keep it lightweight

Do not create a calendar bureaucracy around this.

Use natural milestones, subsystem consolidation, major architecture diffs, or a visible cluster of related review-after decisions as the trigger. Record only findings that change classification, architecture understanding, or future audit behavior.

## Relationship to the permission engine

The current permission-engine scaffold does not accept "precedent" as an authority input, which is intentional. Future policy implementations should preserve that property: precedent can inform evidence, but only explicit current policy/authority can widen a lane.
