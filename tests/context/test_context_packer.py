# Miles Project — Bryan Jones + Miles Mercer | 2026-09-13
import copy
import json
import unittest

from runtime.context_packer import (
    MAX_PACKED_BYTES,
    PackError,
    pack_context,
)


class ContextPackerTests(unittest.TestCase):
    def test_minimal_order_and_exact_text_are_preserved(self):
        packed = pack_context('SYSTEM\nexact', 'USER exact')
        self.assertEqual(
            packed.messages,
            (
                {'role': 'system', 'content': 'SYSTEM\nexact'},
                {'role': 'user', 'content': 'USER exact'},
            ),
        )
        self.assertEqual(packed.memory_records, 0)
        self.assertEqual(packed.relationship_records, 0)

    def test_memory_and_relationship_stay_in_separate_blocks(self):
        packed = pack_context(
            'system-only',
            'question',
            [{'text': 'candidate-memory', 'source': 'fixture'}],
            [{'guidance': 'relationship-note', 'source': 'fixture'}],
        )
        self.assertEqual([m['role'] for m in packed.messages],
                         ['system', 'user', 'user', 'user'])
        self.assertNotIn('candidate-memory', packed.messages[0]['content'])
        self.assertNotIn('relationship-note', packed.messages[0]['content'])
        self.assertIn('candidate-memory', packed.messages[1]['content'])
        self.assertIn('relationship-note', packed.messages[2]['content'])
        self.assertEqual(packed.messages[3]['content'], 'question')

    def test_utf8_byte_accounting_matches_serialized_messages(self):
        packed = pack_context('system π', 'prompt 🚀')
        expected = len(json.dumps(
            list(packed.messages), ensure_ascii=False, separators=(',', ':')
        ).encode('utf-8'))
        self.assertEqual(packed.total_bytes, expected)
        self.assertEqual(packed.system_bytes, len('system π'.encode('utf-8')))
        self.assertEqual(packed.prompt_bytes, len('prompt 🚀'.encode('utf-8')))

    def test_overflow_is_rejected_instead_of_truncated(self):
        system = 'S' * 6800
        prompt = 'P' * 400
        with self.assertRaisesRegex(PackError, 'context exceeds prototype limit'):
            pack_context(system, prompt)
        self.assertEqual(len(system), 6800)
        self.assertEqual(len(prompt), 400)

    def test_limit_boundary_is_explicit_and_configurable_for_tests(self):
        packed = pack_context('system', 'prompt', max_bytes=MAX_PACKED_BYTES)
        self.assertLessEqual(packed.total_bytes, MAX_PACKED_BYTES)
        with self.assertRaises(PackError):
            pack_context('system', 'prompt', max_bytes=10)

    def test_record_inputs_are_not_mutated(self):
        memory = [{'id': 1, 'text': 'blue'}]
        relationship = [{'id': 'style-v1', 'guidance': 'brief'}]
        before_memory = copy.deepcopy(memory)
        before_relationship = copy.deepcopy(relationship)
        pack_context('system', 'prompt', memory, relationship)
        self.assertEqual(memory, before_memory)
        self.assertEqual(relationship, before_relationship)

    def test_invalid_inputs_fail_before_packing(self):
        cases = [
            ('', 'prompt', None, None),
            ('system', '   ', None, None),
            ('system', 'prompt', ['not-a-record'], None),
            ('system', 'prompt', None, ['not-a-record']),
        ]
        for system, prompt, memory, relationship in cases:
            with self.subTest(system=system, prompt=prompt):
                with self.assertRaises(PackError):
                    pack_context(system, prompt, memory, relationship)


if __name__ == '__main__':
    unittest.main()
