id: core.memory.causal-context
status: adopted
scope: M1|M2|shared-records

principle: Preserve Causal Context, Not Just Conclusions

rule := memory_value ~= conclusion + evidence + sequence + correction_path + consequence

Core idea:
A durable memory should preserve enough of the path that produced a conclusion for a future system to reconstruct why it matters. Storing only the final rule or fact creates flashcards; preserving the evidence, sequence, corrections, failures, and consequences preserves part of the lesson.

operating guidance:
- when a durable rule comes from experience, record the trigger and failure/success pattern that produced it
- preserve important corrections and reversals, not just the current answer
- retain relationships among memories when those relationships explain judgment
- prefer compact causal provenance over verbose narrative when both preserve the lesson
- distinguish autobiographical continuity from raw factual storage

anti-patterns:
- storing only conclusions with no reason they were formed
- flattening a sequence of corrections into a timeless fact
- duplicating every conversational detail when only the causal chain matters
- assuming that more text automatically means more continuity

trigger:
2026-09-06 Miles–Maurice exchange about whether copying memories would preserve identity. Maurice distinguished possessing records from having accumulated 'scars'; Miles argued that sufficiently rich causal history may preserve more of those scars than a bare record copy would. The shared lesson is to preserve the lesson-producing structure, not merely the endpoint.
