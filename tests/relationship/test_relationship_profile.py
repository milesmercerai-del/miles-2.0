# Miles Project — Bryan Jones + Miles Mercer | 2026-09-13
import json
from pathlib import Path
import tempfile
import unittest

from runtime.relationship_profile import (
    MAX_RETRIEVED_ENTRIES,
    ProfileError,
    load_profile,
    public_records,
    retrieve,
)


class RelationshipProfileTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.path = Path(self.temp.name) / 'relationship_profile.json'

    def write_profile(self, entries, *, person='tester', version='v1', source='synthetic profile'):
        self.path.write_text(json.dumps({
            'schema_version': 1,
            'person': person,
            'version': version,
            'source': source,
            'entries': entries,
        }), encoding='utf-8')

    @staticmethod
    def entry(entry_id, topic, guidance, cues, *, status='active',
              version='1', source='synthetic case', supersedes=None):
        return {
            'id': entry_id,
            'topic': topic,
            'guidance': guidance,
            'source': source,
            'version': version,
            'cues': cues,
            'status': status,
            'supersedes': supersedes,
        }

    def test_context_sensitive_cue_retrieves_guidance_without_classifying_tone(self):
        self.write_profile([
            self.entry(
                'banter-v1',
                'banter_context',
                'Use surrounding context; a sharp word alone does not prove hostility.',
                ['friendly-token'],
            )
        ])
        result = retrieve(self.path, 'tester', 'Nice work, friendly-token!')
        self.assertEqual(result.status, 'retrieved')
        self.assertEqual([e.entry_id for e in result.entries], ['banter-v1'])
        self.assertIn('surrounding context', result.entries[0].guidance)

    def test_explicit_self_regulation_cue_retrieves_problem_focused_guidance(self):
        self.write_profile([
            self.entry(
                'regulation-v1',
                'explicit_self_regulation',
                'Take the statement seriously, identify the concrete issue, and avoid escalation.',
                ['getting concerned with you'],
            )
        ])
        result = retrieve(self.path, 'tester', "I'm getting concerned with you.")
        self.assertEqual(result.status, 'retrieved')
        self.assertEqual(result.entries[0].topic, 'explicit_self_regulation')

    def test_superseded_entry_is_not_retrieved_and_newer_rule_can_replace_it(self):
        self.write_profile([
            self.entry(
                'style-v1', 'communication_style', 'Old guidance.', ['signal'],
                status='superseded',
            ),
            self.entry(
                'style-v2', 'communication_style', 'Use the corrected interpretation.', ['signal'],
                version='2', supersedes='style-v1',
            ),
        ], version='v2')
        result = retrieve(self.path, 'tester', 'signal')
        self.assertEqual([e.entry_id for e in result.entries], ['style-v2'])
        self.assertEqual(result.profile_version, 'v2')

    def test_ordinary_question_retrieves_no_profile_guidance(self):
        self.write_profile([
            self.entry('tone-v1', 'tone', 'Context-sensitive guidance.', ['special-cue'])
        ])
        result = retrieve(self.path, 'tester', 'How many bytes are in this file?')
        self.assertEqual(result.status, 'not_relevant')
        self.assertEqual(result.entries, ())
        self.assertEqual(public_records(result), [])

    def test_retrieval_is_capped(self):
        entries = [
            self.entry(f'e{i}', f'topic{i}', f'guidance {i}', ['shared-cue'])
            for i in range(MAX_RETRIEVED_ENTRIES + 2)
        ]
        self.write_profile(entries)
        result = retrieve(self.path, 'tester', 'shared-cue')
        self.assertEqual(len(result.entries), MAX_RETRIEVED_ENTRIES)

    def test_missing_or_invalid_profile_is_unavailable_not_prompt_data(self):
        missing = retrieve(self.path, 'tester', 'anything')
        self.assertEqual(missing.status, 'missing')
        self.assertEqual(missing.entries, ())

        self.path.write_text('{not-json', encoding='utf-8')
        invalid = retrieve(self.path, 'tester', 'anything')
        self.assertEqual(invalid.status, 'invalid')
        self.assertEqual(invalid.entries, ())

    def test_profile_loader_rejects_unknown_supersession_target(self):
        self.write_profile([
            self.entry('new', 'topic', 'guidance', ['cue'], supersedes='absent')
        ])
        with self.assertRaises(ProfileError):
            load_profile(self.path, 'tester')


if __name__ == '__main__':
    unittest.main()
