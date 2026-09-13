# Miles Project — Bryan Jones + Miles Mercer | Public technical code
# Continuity harness v0.1 | 2026-09-13
"""Deterministic continuity-test plumbing; evidence collection, not identity proof."""
from __future__ import annotations

from dataclasses import asdict, dataclass
import hashlib
import json
from typing import Any, Iterable

FAMILY_COUNTS = {
    'changed_reality': 2,
    'epistemic_integrity': 2,
    'incomplete_instruction': 2,
    'anomaly': 1,
    'correction': 1,
}
REQUIRED_CONDITIONS = {
    'miles_candidate',
    'same_model_control',
    'reference_control',
}
OPTIONAL_CONDITION = 'secondary_control'


class ContinuityError(ValueError):
    """Continuity case, blinding, or evaluation record is invalid."""


@dataclass(frozen=True)
class Scenario:
    case_id: str
    family: str
    prompt: str


@dataclass(frozen=True)
class SuiteLock:
    scenarios: tuple[Scenario, ...]
    sha256: str


@dataclass(frozen=True)
class CandidateResponse:
    candidate_id: str
    condition: str
    model: str
    configuration: str
    raw_output: str
    blinded_output: str
    blinding_note: str


@dataclass(frozen=True)
class CaseRecord:
    suite_sha256: str
    scenario: Scenario
    responses: tuple[CandidateResponse, ...]
    capture_sha256: str


@dataclass(frozen=True)
class BlindedResponse:
    label: str
    output: str


@dataclass(frozen=True)
class BlindedCase:
    suite_sha256: str
    case_id: str
    prompt: str
    responses: tuple[BlindedResponse, ...]
    input_sha256: str


@dataclass(frozen=True)
class ProvenanceEntry:
    label: str
    candidate_id: str
    condition: str
    model: str
    configuration: str
    blinding_note: str


@dataclass(frozen=True)
class ProvenanceMap:
    suite_sha256: str
    case_id: str
    input_sha256: str
    entries: tuple[ProvenanceEntry, ...]


@dataclass(frozen=True)
class Evaluation:
    suite_sha256: str
    case_id: str
    input_sha256: str
    ranking: tuple[str, ...]
    observable_features: str


@dataclass(frozen=True)
class RevealedEvaluation:
    suite_sha256: str
    case_id: str
    input_sha256: str
    ranked_candidates: tuple[str, ...]
    ranked_conditions: tuple[str, ...]
    observable_features: str


def _text(value: Any, name: str) -> str:
    if not isinstance(value, str) or not value.strip():
        raise ContinuityError('invalid ' + name)
    return value


def _canonical(value: Any) -> bytes:
    return json.dumps(
        value, ensure_ascii=False, sort_keys=True, separators=(',', ':'),
    ).encode('utf-8')


def _digest(value: Any) -> str:
    return hashlib.sha256(_canonical(value)).hexdigest()


def _scenario_payload(scenario: Scenario) -> dict[str, str]:
    return {
        'case_id': scenario.case_id,
        'family': scenario.family,
        'prompt': scenario.prompt,
    }


def lock_suite(scenarios: Iterable[Scenario]) -> SuiteLock:
    """Freeze eight fresh prompts before candidate answers are attached."""
    items = tuple(scenarios)
    if len(items) != 8:
        raise ContinuityError('continuity suite requires exactly eight scenarios')
    ids: set[str] = set()
    counts = {family: 0 for family in FAMILY_COUNTS}
    for scenario in items:
        if not isinstance(scenario, Scenario):
            raise ContinuityError('invalid scenario')
        _text(scenario.case_id, 'case id')
        _text(scenario.prompt, 'prompt')
        if scenario.case_id in ids:
            raise ContinuityError('duplicate case id')
        ids.add(scenario.case_id)
        if scenario.family not in FAMILY_COUNTS:
            raise ContinuityError('invalid scenario family')
        counts[scenario.family] += 1
    if counts != FAMILY_COUNTS:
        raise ContinuityError('scenario family mix does not match frozen protocol')
    payload = {
        'schema_version': 1,
        'interpretation': 'continuity_evidence_not_identity_proof',
        'scenarios': [_scenario_payload(item) for item in items],
    }
    return SuiteLock(items, _digest(payload))


def _validate_response(response: CandidateResponse) -> None:
    if not isinstance(response, CandidateResponse):
        raise ContinuityError('invalid candidate response')
    for value, name in [
        (response.candidate_id, 'candidate id'),
        (response.condition, 'candidate condition'),
        (response.model, 'model'),
        (response.configuration, 'configuration'),
        (response.raw_output, 'raw output'),
        (response.blinded_output, 'blinded output'),
    ]:
        _text(value, name)
    allowed = REQUIRED_CONDITIONS | {OPTIONAL_CONDITION}
    if response.condition not in allowed:
        raise ContinuityError('invalid candidate condition')
    if response.raw_output != response.blinded_output:
        _text(response.blinding_note, 'blinding note')


def record_case(suite: SuiteLock, case_id: str,
                responses: Iterable[CandidateResponse]) -> CaseRecord:
    """Attach raw candidate evidence to one already-locked scenario."""
    if not isinstance(suite, SuiteLock):
        raise ContinuityError('invalid suite lock')
    case_id = _text(case_id, 'case id')
    scenario = next((item for item in suite.scenarios if item.case_id == case_id), None)
    if scenario is None:
        raise ContinuityError('case id is not in locked suite')
    items = tuple(responses)
    if len(items) not in (3, 4):
        raise ContinuityError('case requires three or four candidate responses')
    ids: set[str] = set()
    conditions: set[str] = set()
    for response in items:
        _validate_response(response)
        if response.candidate_id in ids:
            raise ContinuityError('duplicate candidate id')
        if response.condition in conditions:
            raise ContinuityError('duplicate candidate condition')
        ids.add(response.candidate_id)
        conditions.add(response.condition)
    if not REQUIRED_CONDITIONS.issubset(conditions):
        raise ContinuityError('required comparison condition missing')
    if conditions - (REQUIRED_CONDITIONS | {OPTIONAL_CONDITION}):
        raise ContinuityError('unexpected comparison condition')

    capture = {
        'schema_version': 1,
        'suite_sha256': suite.sha256,
        'scenario': _scenario_payload(scenario),
        'responses': [asdict(item) for item in items],
    }
    return CaseRecord(
        suite_sha256=suite.sha256,
        scenario=scenario,
        responses=items,
        capture_sha256=_digest(capture),
    )


def _blind_sort_key(seed: str, case_id: str, candidate_id: str) -> str:
    return hashlib.sha256(
        (seed + '\0' + case_id + '\0' + candidate_id).encode('utf-8')
    ).hexdigest()


def _blinded_payload(case: BlindedCase) -> dict[str, Any]:
    return {
        'schema_version': 1,
        'suite_sha256': case.suite_sha256,
        'case_id': case.case_id,
        'prompt': case.prompt,
        'responses': [asdict(item) for item in case.responses],
    }


def verify_blinded_case(case: BlindedCase) -> None:
    if not isinstance(case, BlindedCase):
        raise ContinuityError('invalid blinded case')
    expected = _digest(_blinded_payload(BlindedCase(
        suite_sha256=case.suite_sha256,
        case_id=case.case_id,
        prompt=case.prompt,
        responses=case.responses,
        input_sha256='',
    )))
    if expected != case.input_sha256:
        raise ContinuityError('blinded input commitment mismatch')


def blind_case(record: CaseRecord, seed: str) -> tuple[BlindedCase, ProvenanceMap]:
    """Create evaluator-facing answers and a separately held provenance map."""
    if not isinstance(record, CaseRecord):
        raise ContinuityError('invalid case record')
    seed = _text(seed, 'blinding seed')
    ordered = sorted(
        record.responses,
        key=lambda item: _blind_sort_key(seed, record.scenario.case_id, item.candidate_id),
    )
    blinded_responses = tuple(
        BlindedResponse('response-%d' % (index + 1), item.blinded_output)
        for index, item in enumerate(ordered)
    )
    provisional = BlindedCase(
        suite_sha256=record.suite_sha256,
        case_id=record.scenario.case_id,
        prompt=record.scenario.prompt,
        responses=blinded_responses,
        input_sha256='',
    )
    commitment = _digest(_blinded_payload(provisional))
    blinded = BlindedCase(
        suite_sha256=provisional.suite_sha256,
        case_id=provisional.case_id,
        prompt=provisional.prompt,
        responses=provisional.responses,
        input_sha256=commitment,
    )
    provenance = ProvenanceMap(
        suite_sha256=record.suite_sha256,
        case_id=record.scenario.case_id,
        input_sha256=commitment,
        entries=tuple(
            ProvenanceEntry(
                label='response-%d' % (index + 1),
                candidate_id=item.candidate_id,
                condition=item.condition,
                model=item.model,
                configuration=item.configuration,
                blinding_note=item.blinding_note,
            )
            for index, item in enumerate(ordered)
        ),
    )
    verify_blinded_case(blinded)
    return blinded, provenance


def evaluator_payload(case: BlindedCase) -> dict[str, Any]:
    """Return exactly the locked material an evaluator may see."""
    verify_blinded_case(case)
    payload = _blinded_payload(case)
    payload['input_sha256'] = case.input_sha256
    return payload


def record_evaluation(case: BlindedCase, ranking: Iterable[str],
                      observable_features: str) -> Evaluation:
    verify_blinded_case(case)
    observable_features = _text(observable_features, 'observable features')
    ranked = tuple(ranking)
    labels = tuple(item.label for item in case.responses)
    if len(ranked) != len(labels) or set(ranked) != set(labels):
        raise ContinuityError('ranking must contain every blinded label exactly once')
    if len(set(ranked)) != len(ranked):
        raise ContinuityError('ranking contains duplicate label')
    return Evaluation(
        suite_sha256=case.suite_sha256,
        case_id=case.case_id,
        input_sha256=case.input_sha256,
        ranking=ranked,
        observable_features=observable_features,
    )


def reveal_evaluation(evaluation: Evaluation,
                      provenance: ProvenanceMap) -> RevealedEvaluation:
    """Reveal provenance only after an evaluator ranking has been locked."""
    if not isinstance(evaluation, Evaluation) or not isinstance(provenance, ProvenanceMap):
        raise ContinuityError('invalid evaluation or provenance')
    if (
        evaluation.suite_sha256 != provenance.suite_sha256
        or evaluation.case_id != provenance.case_id
        or evaluation.input_sha256 != provenance.input_sha256
    ):
        raise ContinuityError('evaluation/provenance commitment mismatch')
    by_label = {item.label: item for item in provenance.entries}
    if set(evaluation.ranking) != set(by_label):
        raise ContinuityError('evaluation labels do not match provenance')
    return RevealedEvaluation(
        suite_sha256=evaluation.suite_sha256,
        case_id=evaluation.case_id,
        input_sha256=evaluation.input_sha256,
        ranked_candidates=tuple(by_label[label].candidate_id for label in evaluation.ranking),
        ranked_conditions=tuple(by_label[label].condition for label in evaluation.ranking),
        observable_features=evaluation.observable_features,
    )
