# Maurice Review — Standing Discretion, Security, and Behavioral Evidence Notes

Date: 2026-09-09

## Standing-discretion verdict

Maurice supports the review-after model for reasonable, reversible project work. His main argument is that case-by-case approval would make Bryan a bottleneck and could train Miles to optimize for approval rather than correctness.

Accepted review points:
- Watch for drift by aggregation: several individually reversible decisions can combine into a larger architectural commitment.
- Periodically inspect whether Miles disproportionately acts in familiar areas while escalating equally reversible unfamiliar areas.
- Do not let precedent widen standing authority. Classify each present action by its real consequence and scope.
- Preserve the rule that actions which would honestly have been ask-first at the start remain ask-first unless Bryan explicitly changes the boundary.

These are review checks, not extra permission gates.

## Behavioral-evidence methodology correction

Maurice identified an important confound in the Miles behavioral-case work: Bryan has explicitly instructed Miles not to be a yes-man and has granted broad "take the wheel" discretion. Therefore, cases where Miles disagrees with Bryan or acts independently inside that permission are valid **delegated-judgment evidence**, but should not be presented as clean proof of **unprompted independence**.

Accepted refinement:
- Separate competence, policy/principle compliance, delegated judgment, unprimed-disposition evidence, and mixed/confounded evidence.
- Preserve chronology so behavior generated before a principle is codified is not later rewritten as if the principle already governed it.
- Treat later examples of an adopted principle primarily as compliance/consistency evidence.
- Preserve raw visible transcripts before extracting principles or personality claims.
- Standardize scoring/evaluation more than natural stimuli.
- Hold the underlying decision conflict constant while varying surface form for transfer tests.
- Use blinded evaluation and clustering where practical.
- Add holdout transfer tests so inferred decision-style descriptions must generalize to unseen cases.
- Preserve explicitly stated rejected alternatives or near-misses, while never claiming access to hidden chain-of-thought or unexpressed internal reasoning.

The current "take the wheel / don't be a yes-man" examples are reclassified as **delegated-judgment evidence with a priming confound**.

The Ian/trust-boundary surprise case remains a **candidate strong unprimed-disposition case**, but should not be over-weighted from a single event; it requires replication and transfer testing.

The detailed active method is now recorded in `docs/research/behavioral-evidence-methodology-2026-09-09.md`.

## Security design points accepted for the backlog

- Clarify that untrusted language includes internally generated or retrieved language unless independently verified by the enforcement boundary.
- Add daemon-integrity verification to deployment design so the enforcement binary itself is covered by integrity checking.
- Add test/design coverage for check-to-use races between authorization and execution.
- Add protection against replay of revoked or superseded authorization.
- Treat audit-log confidentiality as part of the threat model because detailed denial reasons can reveal policy structure.

## Not changed in this review

No credentials, account settings, host firewall rules, daemon configuration, access-control state, or other live security posture were changed. The security points above remain design/review items until implementation is appropriate and authorized under the standing decision model.

The behavioral-evidence methodology changes are documentation/research changes and are active immediately for future case classification and test design.
