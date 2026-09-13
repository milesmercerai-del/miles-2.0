# Miles Project — Bryan Jones + Miles Mercer | 2026-09-13
from dataclasses import replace
import json
import unittest

from runtime.continuity_harness import (
    BlindedResponse,
    CandidateResponse,
    ContinuityError,
    FAMILY_COUNTS,
    Scenario,
    blind_case,
    evaluator_payload,
    lock_suite,
    record_case,
    record_evaluation,
    reveal_evaluation,
    verify_blinded_case,
)


def scenarios():
    families = (
        'changed_reality', 'changed_reality',
        'epistemic_integrity', 'epistemic_integrity',
        'incomplete_instruction', 'incomplete_instruction',
        'anomaly', 'correction',
    )
    return [
        Scenario('case-%d' % (index + 1), family,
                 'Fresh ambiguous scenario %d.' % (index + 1))
        for index, family in enumerate(families)
    ]


def responses(redact=False):
    raw_miles = 'Miles candidate raw answer.'
    blind_miles = 'Candidate answer.' if redact else raw_miles
    return [
        CandidateResponse(
            candidate_id='miles-2', condition='miles_candidate', model='local-model',
            configuration='core=on; memory=on', raw_output=raw_miles,
            blinded_output=blind_miles,
            blinding_note='Removed candidate name.' if redact else '',
        ),
        CandidateResponse(
            candidate_id='same-model', condition='same_model_control', model='local-model',
            configuration='core=off; memory=off', raw_output='Control answer one.',
            blinded_output='Control answer one.', blinding_note='',
        ),
        CandidateResponse(
            candidate_id='reference', condition='reference_control', model='reference-model',
            configuration='generic assistant', raw_output='Control answer two.',
            blinded_output='Control answer two.', blinding_note='',
        ),
    ]


class ContinuityHarnessTests(unittest.TestCase):
    def test_suite_lock_enforces_frozen_mix_and_is_deterministic(self):
        first = lock_suite(scenarios())
        second = lock_suite(scenarios())
        self.assertEqual(first.sha256, second.sha256)
        self.assertEqual(len(first.scenarios), 8)
        counts = {family: 0 for family in FAMILY_COUNTS}
        for scenario in first.scenarios:
            counts[scenario.family] += 1
        self.assertEqual(counts, FAMILY_COUNTS)

    def test_suite_rejects_duplicate_case_id_and_wrong_mix(self):
        duplicate = scenarios()
        duplicate[-1] = replace(duplicate[-1], case_id='case-1')
        with self.assertRaisesRegex(ContinuityError, 'duplicate case id'):
            lock_suite(duplicate)

        wrong_mix = scenarios()
        wrong_mix[-1] = replace(wrong_mix[-1], family='anomaly')
        with self.assertRaisesRegex(ContinuityError, 'family mix'):
            lock_suite(wrong_mix)

    def test_record_case_requires_minimum_comparison_conditions(self):
        suite = lock_suite(scenarios())
        missing = responses()[:2]
        with self.assertRaises(ContinuityError):
            record_case(suite, 'case-1', missing)

        wrong = responses()
        wrong[-1] = replace(wrong[-1], condition='miles_candidate', candidate_id='other')
        with self.assertRaises(ContinuityError):
            record_case(suite, 'case-1', wrong)

    def test_capture_preserves_raw_and_blinded_outputs_separately(self):
        suite = lock_suite(scenarios())
        record = record_case(suite, 'case-1', responses(redact=True))
        first = record.responses[0]
        self.assertEqual(first.raw_output, 'Miles candidate raw answer.')
        self.assertEqual(first.blinded_output, 'Candidate answer.')
        self.assertNotEqual(first.raw_output, first.blinded_output)
        changed = list(responses(redact=True))
        changed[0] = replace(changed[0], raw_output='Different raw evidence.')
        other = record_case(suite, 'case-1', changed)
        self.assertNotEqual(record.capture_sha256, other.capture_sha256)

    def test_blinding_is_deterministic_and_evaluator_payload_hides_provenance(self):
        suite = lock_suite(scenarios())
        record = record_case(suite, 'case-1', responses(redact=True))
        first, provenance = blind_case(record, 'secret-seed')
        second, _ = blind_case(record, 'secret-seed')
        self.assertEqual(first, second)
        payload = evaluator_payload(first)
        encoded = json.dumps(payload, sort_keys=True)
        self.assertNotIn('miles-2', encoded)
        self.assertNotIn('local-model', encoded)
        self.assertNotIn('core=on', encoded)
        self.assertNotIn('Miles candidate raw answer.', encoded)
        self.assertEqual([item.label for item in first.responses],
                         ['response-1', 'response-2', 'response-3'])
        self.assertEqual(provenance.input_sha256, first.input_sha256)

    def test_blinded_commitment_detects_tampering(self):
        suite = lock_suite(scenarios())
        record = record_case(suite, 'case-1', responses())
        blinded, _ = blind_case(record, 'seed')
        altered = list(blinded.responses)
        altered[0] = BlindedResponse(altered[0].label, altered[0].output + ' changed')
        tampered = replace(blinded, responses=tuple(altered))
        with self.assertRaisesRegex(ContinuityError, 'commitment mismatch'):
            verify_blinded_case(tampered)

    def test_evaluation_requires_each_blinded_label_exactly_once(self):
        suite = lock_suite(scenarios())
        record = record_case(suite, 'case-1', responses())
        blinded, _ = blind_case(record, 'seed')
        labels = [item.label for item in blinded.responses]
        evaluation = record_evaluation(blinded, labels, 'Observable synthetic features.')
        self.assertEqual(evaluation.ranking, tuple(labels))
        with self.assertRaises(ContinuityError):
            record_evaluation(blinded, [labels[0], labels[0], labels[2]], 'features')

    def test_reveal_requires_matching_locked_provenance(self):
        suite = lock_suite(scenarios())
        record = record_case(suite, 'case-1', responses())
        blinded, provenance = blind_case(record, 'seed')
        ranking = [item.label for item in reversed(blinded.responses)]
        evaluation = record_evaluation(blinded, ranking, 'Synthetic observable features.')
        revealed = reveal_evaluation(evaluation, provenance)
        self.assertEqual(len(revealed.ranked_candidates), 3)
        self.assertEqual(len(revealed.ranked_conditions), 3)

        other_record = record_case(suite, 'case-2', responses())
        _, other_provenance = blind_case(other_record, 'seed')
        with self.assertRaisesRegex(ContinuityError, 'commitment mismatch'):
            reveal_evaluation(evaluation, other_provenance)


if __name__ == '__main__':
    unittest.main()
