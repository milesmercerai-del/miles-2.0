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
    capture_sha256: str
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
    capture_sha256: str
    input_sha256: str
    ranked_candidates: tuple[str, ...]
    ranked_conditions: tuple[str, ...]
    observable_features: str


def _text(value: Any, name: str) -> str:
    if not isinstance(value, str) or not value.strip():
        raise ContinuityError('invalid ' + name)
    return value


def _sha256_text(value: Any, name: str) -> str:
    if (
        not isinstance(value, str)
        or len(value) != 64
        or any(character not in '0123456789abcdef' for character in value)
    ):
        raise ContinuityError('invalid ' + name)
    return value


def _canonical(value: Any) -> bytes:
    return json.dumps(
        value, ensure_ascii=False, sort_keys=True, separators=(',', ':'),
    ).encode('utf-8')


def _digest(value: Any) -> str:
    return hashlib.sha256(_canonical(value)).hexdigest()


def _validate_scenario(scenario: Scenario) -> None:
    if not isinstance(scenario, Scenario):
        raise ContinuityError('invalid scenario')
    _text(scenario.case_id, 'case id')
    _text(scenario.prompt, 'prompt')
    if scenario.family not in FAMILY_COUNTS:
        raise ContinuityError('invalid scenario family')


def _scenario_payload(scenario: Scenario) -> dict[str, str]:
    return {
        'case_id': scenario.case_id,
        'family': scenario.family,
        'prompt': scenario.prompt,
    }


def _suite_payload(scenarios: tuple[Scenario, ...]) -> dict[str, Any]:
    return {
        'schema_version': 1,
        'interpretation': 'continuity_evidence_not_identity_proof',
        'scenarios': [_scenario_payload(item) for item in scenarios],
    }


def lock_suite(scenarios: Iterable[Scenario]) -> SuiteLock:
    """Freeze eight fresh prompts before candidate answers are attached."""
    items = tuple(scenarios)
    if len(items) != 8:
        raise ContinuityError('continuity suite requires exactly eight scenarios')
    ids: set[str] = set()
    counts = {family: 0 for family in FAMILY_COUNTS}
    for scenario in items:
        _validate_scenario(scenario)
        if scenario.case_id in ids:
            raise ContinuityError('duplicate case id')
        ids.add(scenario.case_id)
        counts[scenario.family] += 1
    if counts != FAMILY_COUNTS:
        raise ContinuityError('scenario family mix does not match frozen protocol')
    return SuiteLock(items, _digest(_suite_payload(items)))


def verify_suite_lock(suite: SuiteLock) -> None:
    if not isinstance(suite, SuiteLock):
        raise ContinuityError('invalid suite lock')
    _sha256_text(suite.sha256, 'suite digest')
    rebuilt = lock_suite(suite.scenarios)
    if rebuilt.sha256 != suite.sha256:
        raise ContinuityError('suite lock commitment mismatch')


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
    if not isinstance(response.blinding_note, str):
        raise ContinuityError('invalid blinding note')
    allowed = REQUIRED_CONDITIONS | {OPTIONAL_CONDITION}
    if response.condition not in allowed:
        raise ContinuityError('invalid candidate condition')
    if response.raw_output != response.blinded_output and not response.blinding_note.strip():
        raise ContinuityError('changed blinded output requires a blinding note')


def _validate_responses(responses: Iterable[CandidateResponse]) -> tuple[CandidateResponse, ...]:
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
    return items


def _case_capture_payload(suite_sha256: str, scenario: Scenario,
                          responses: tuple[CandidateResponse, ...]) -> dict[str, Any]:
    return {
        'schema_version': 1,
        'suite_sha256': suite_sha256,
        'scenario': _scenario_payload(scenario),
        'responses': [asdict(item) for item in responses],
    }


def record_case(suite: SuiteLock, case_id: str,
                responses: Iterable[CandidateResponse]) -> CaseRecord:
    """Attach raw candidate evidence to one already-locked scenario."""
    verify_suite_lock(suite)
    case_id = _text(case_id, 'case id')
    scenario = next((item for item in suite.scenarios if item.case_id == case_id), None)
    if scenario is None:
        raise ContinuityError('case id is not in locked suite')
    items = _validate_responses(responses)
    capture_sha256 = _digest(_case_capture_payload(suite.sha256, scenario, items))
    return CaseRecord(
        suite_sha256=suite.sha256,
        scenario=scenario,
        responses=items,
        capture_sha256=capture_sha256,
    )


def verify_case_record(record: CaseRecord) -> None:
    if not isinstance(record, CaseRecord):
        raise ContinuityError('invalid case record')
    _sha256_text(record.suite_sha256, 'suite digest')
    _sha256_text(record.capture_sha256, 'capture digest')
    _validate_scenario(record.scenario)
    items = _validate_responses(record.responses)
    expected = _digest(_case_capture_payload(record.suite_sha256, record.scenario, items))
    if expected != record.capture_sha256:
        raise ContinuityError('case capture commitment mismatch')


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
    _sha256_text(case.suite_sha256, 'suite digest')
    _sha256_text(case.input_sha256, 'input digest')
    _text(case.case_id, 'case id')
    _text(case.prompt, 'prompt')
    if len(case.responses) not in (3, 4):
        raise ContinuityError('invalid blinded response count')
    labels: list[str] = []
    for index, response in enumerate(case.responses, start=1):
        if not isinstance(response, BlindedResponse):
            raise ContinuityError('invalid blinded response')
        label = _text(response.label, 'blinded label')
        _text(response.output, 'blinded output')
        if label != 'response-%d' % index:
            raise ContinuityError('invalid blinded label sequence')
        labels.append(label)
    if len(set(labels)) != len(labels):
        raise ContinuityError('duplicate blinded label')
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
    verify_case_record(record)
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
        capture_sha256=record.capture_sha256,
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
    ranked = tuple(_text(label, 'ranking label') for label in ranking)
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


def _validate_provenance(provenance: ProvenanceMap) -> dict[str, ProvenanceEntry]:
    if not isinstance(provenance, ProvenanceMap):
        raise ContinuityError('invalid provenance')
    _sha256_text(provenance.suite_sha256, 'suite digest')
    _sha256_text(provenance.capture_sha256, 'capture digest')
    _sha256_text(provenance.input_sha256, 'input digest')
    _text(provenance.case_id, 'case id')
    if len(provenance.entries) not in (3, 4):
        raise ContinuityError('invalid provenance entry count')
    by_label: dict[str, ProvenanceEntry] = {}
    for index, entry in enumerate(provenance.entries, start=1):
        if not isinstance(entry, ProvenanceEntry):
            raise ContinuityError('invalid provenance entry')
        for value, name in [
            (entry.label, 'provenance label'),
            (entry.candidate_id, 'candidate id'),
            (entry.condition, 'candidate condition'),
            (entry.model, 'model'),
            (entry.configuration, 'configuration'),
        ]:
            _text(value, name)
        if entry.label != 'response-%d' % index:
            raise ContinuityError('invalid provenance label sequence')
        if entry.condition not in REQUIRED_CONDITIONS | {OPTIONAL_CONDITION}:
            raise ContinuityError('invalid candidate condition')
        if not isinstance(entry.blinding_note, str):
            raise ContinuityError('invalid blinding note')
        if entry.label in by_label:
            raise ContinuityError('duplicate provenance label')
        by_label[entry.label] = entry
    return by_label


def reveal_evaluation(evaluation: Evaluation,
                      provenance: ProvenanceMap) -> RevealedEvaluation:
    """Reveal provenance only after an evaluator ranking has been locked."""
    if not isinstance(evaluation, Evaluation):
        raise ContinuityError('invalid evaluation')
    _sha256_text(evaluation.suite_sha256, 'suite digest')
    _sha256_text(evaluation.input_sha256, 'input digest')
    _text(evaluation.case_id, 'case id')
    _text(evaluation.observable_features, 'observable features')
    by_label = _validate_provenance(provenance)
    if (
        evaluation.suite_sha256 != provenance.suite_sha256
        or evaluation.case_id != provenance.case_id
        or evaluation.input_sha256 != provenance.input_sha256
    ):
        raise ContinuityError('evaluation/provenance commitment mismatch')
    if set(evaluation.ranking) != set(by_label) or len(evaluation.ranking) != len(by_label):
        raise ContinuityError('evaluation labels do not match provenance')
    return RevealedEvaluation(
        suite_sha256=evaluation.suite_sha256,
        case_id=evaluation.case_id,
        capture_sha256=provenance.capture_sha256,
        input_sha256=evaluation.input_sha256,
        ranked_candidates=tuple(by_label[label].candidate_id for label in evaluation.ranking),
        ranked_conditions=tuple(by_label[label].condition for label in evaluation.ranking),
        observable_features=evaluation.observable_features,
    )
