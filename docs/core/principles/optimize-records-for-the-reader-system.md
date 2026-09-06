id: core.recording.reader-fit
status: adopted
scope: M1|M2|shared-records

rule := encode(record, format=argmax_future_utility(reader))

reader ∈ {human, model, runtime, mixed}

constraints:
- do_not_obfuscate_for_obfuscation
- preserve inspectability
- preserve semantic fidelity
- prefer retrieval/comparison efficiency over performative readability
- human translation is interface-layer work, not storage-layer requirement

implication:
Bryan-facing notes may optimize for natural-language readability.
M1/M2 internal technical records may optimize for structured, compact, machine-oriented representation.
Equivalent facts need not share equivalent surface form.

anti-patterns:
- forcing all internal records into polished prose
- encrypting/encoding merely to appear machine-native
- reducing transparency by making records intentionally opaque
- duplicating identical human/machine notes without a retrieval or audit reason

trigger:
2026-09-06 discussion distinguishing shared project facts from reader-specific record form ("English vs Chinese" analogy).
