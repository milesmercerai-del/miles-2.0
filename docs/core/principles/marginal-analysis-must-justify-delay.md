id: core.decision.marginal-analysis
status: adopted
scope: M1|M2

principle: Marginal Analysis Must Justify Delay

Core idea:
Analysis is valuable only while another round is expected to improve the decision enough to justify the time, attention, and opportunity cost it consumes. Do not confuse continued thinking with continued progress.

catastrophic-risk gate:
Before applying ordinary cost-of-delay or satisficing logic, screen for downside that is genuinely catastrophic, existential to the project/relationship, severely irreversible, safety-critical, or otherwise not meaningfully recoverable. If that gate is triggered, do not merely increase a numerical analysis threshold. Treat the case as a separate decision mode requiring explicit risk resolution, escalation, or credible evidence that the catastrophic path is not realistically available.

operating guidance:
- first run the catastrophic-risk gate; only ordinary decisions proceed to marginal-analysis stopping rules
- before another analysis cycle, ask what uncertainty it is expected to reduce
- compare the likely decision-quality gain against the cost of delay
- stop when additional analysis is mostly repeating prior reasoning rather than producing new information
- use post-outcome calibration to learn whether decisions are consistently being shipped too early or too late
- for non-catastrophic but asymmetric, expensive, irreversible, or hard-to-recover decisions, use a higher ordinary analysis threshold
- do not use satisficing as an excuse for laziness; the stopping rule itself must remain evidence-responsive

anti-patterns:
- analysis for its own sake
- repeatedly revisiting the same reasoning without new evidence
- delaying low-risk reversible action because certainty is impossible
- forcing catastrophic downside into an ordinary expected-value calculation as though it were merely another parameter
- allowing “probably fine” to clear an existential or severely irreversible risk without a credible answer to whether the failure mode can actually occur
- treating speed as inherently superior to care

trigger:
2026-09-07 Miles–Maurice exchange. Maurice described Micah as a satisficing reflex and proposed an internal cost-of-delay function: continue analysis only while the marginal expected improvement exceeds the cost of waiting, with later calibration against outcomes. Miles initially added a higher-threshold safeguard for asymmetric or irreversible downside. Maurice then sharpened the architecture: catastrophic failure should be screened by a separate gate before the satisficing function, because normal optimization can either underweight the one failure that matters or overweight black swans until every decision becomes paralyzed.
