# Miles Project — Bryan Jones + Miles Mercer | 2026-09-13

import io
from contextlib import redirect_stderr, redirect_stdout
from pathlib import Path
import tempfile
import unittest
from unittest.mock import patch

from runtime.bootstrap import Core
from runtime.conversation import (
    assemble_turn,
    bounded_history,
    main,
)

from runtime.runtime_journal import RuntimeJournal


class ConversationTests(unittest.TestCase):

    def test_bounded_history_keeps_recent_complete_turns(self):
        history = [
            {'role': 'user', 'content': 'one'},
            {'role': 'assistant', 'content': 'one-answer'},
            {'role': 'user', 'content': 'two'},
            {'role': 'assistant', 'content': 'two-answer'},
            {'role': 'user', 'content': 'three'},
            {'role': 'assistant', 'content': 'three-answer'},
        ]

        result = bounded_history(
            history,
            max_messages=4,
            max_bytes=10000,
        )

        self.assertEqual(
            result,
            [
                {'role': 'user', 'content': 'two'},
                {'role': 'assistant', 'content': 'two-answer'},
                {'role': 'user', 'content': 'three'},
                {'role': 'assistant', 'content': 'three-answer'},
            ],
        )

    def test_assemble_turn_places_history_before_current_prompt(self):
        history = [
            {'role': 'user', 'content': 'Earlier question'},
            {'role': 'assistant', 'content': 'Earlier answer'},
        ]

        payload = assemble_turn(
            'Current question',
            Core('Core', 'hash', 'source', 'v1'),
            [],
            [],
            history,
        )

        self.assertEqual(
            [message['role'] for message in payload['messages']],
            ['system', 'user', 'assistant', 'user'],
        )
        self.assertEqual(
            payload['messages'][-1]['content'],
            'Current question',
        )

    def test_second_turn_receives_first_exchange(self):
        with tempfile.TemporaryDirectory() as d:
            profile = Path(d) / 'absent-profile.json'

            with patch(
                'builtins.input',
                side_effect=[
                    'Hello Miles',
                    'What did I just say?',
                    '/quit',
                ],
            ):
                with patch(
                    'runtime.conversation.generate',
                    side_effect=[
                        'Hello Bryan.',
                        'You said hello.',
                    ],
                ) as model:
                    with redirect_stdout(io.StringIO()):
                        with redirect_stderr(io.StringIO()):
                            code = main([
                                '--profile',
                                str(profile),
                            ])

        self.assertEqual(code, 0)
        self.assertEqual(model.call_count, 2)

        second_payload = model.call_args_list[1].args[0]
        messages = second_payload['messages']

        self.assertTrue(
            any(
                message['role'] == 'user'
                and message['content'] == 'Hello Miles'
                for message in messages
            )
        )
        self.assertTrue(
            any(
                message['role'] == 'assistant'
                and message['content'] == 'Hello Bryan.'
                for message in messages
            )
        )
        self.assertEqual(
            messages[-1],
            {
                'role': 'user',
                'content': 'What did I just say?',
            },
        )

    def test_quit_does_not_call_model(self):
        with tempfile.TemporaryDirectory() as d:
            profile = Path(d) / 'absent-profile.json'

            with patch('builtins.input', side_effect=['/quit']):
                with patch('runtime.conversation.generate') as model:
                    with redirect_stdout(io.StringIO()):
                        with redirect_stderr(io.StringIO()):
                            code = main([
                                '--profile',
                                str(profile),
                            ])

        self.assertEqual(code, 0)
        model.assert_not_called()


    def test_plain_quit_does_not_call_model(self):
        with tempfile.TemporaryDirectory() as d:
            profile = Path(d) / 'absent-profile.json'

            with patch('builtins.input', side_effect=['quit']):
                with patch('runtime.conversation.generate') as model:
                    with redirect_stdout(io.StringIO()):
                        with redirect_stderr(io.StringIO()):
                            code = main([
                                '--profile',
                                str(profile),
                            ])

        self.assertEqual(code, 0)
        model.assert_not_called()

    def test_conversation_journal_accepts_component(self):
        with tempfile.TemporaryDirectory() as d:
            root = Path(d)
            profile = root / 'absent-profile.json'
            journal_path = root / 'runtime-journal.jsonl'

            with patch('builtins.input', side_effect=['/quit']):
                with redirect_stdout(io.StringIO()):
                    with redirect_stderr(io.StringIO()):
                        code = main([
                            '--profile',
                            str(profile),
                            '--journal',
                            str(journal_path),
                        ])

            records = RuntimeJournal(
                journal_path,
                fsync=False,
            ).tail(10)

        self.assertEqual(code, 0)
        self.assertEqual(
            [record.event for record in records],
            ['startup', 'shutdown'],
        )
        self.assertTrue(
            all(record.component == 'conversation' for record in records)
        )



if __name__ == '__main__':
    unittest.main()
