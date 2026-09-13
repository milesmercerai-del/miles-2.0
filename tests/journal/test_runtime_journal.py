# Miles Project — Bryan Jones + Miles Mercer | 2026-09-13
import json
import os
from pathlib import Path
import tempfile
import unittest

from runtime.runtime_journal import (
    JournalError,
    RuntimeJournal,
    build_record,
)


class RuntimeJournalTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.path = Path(self.temp.name) / 'private' / 'runtime.jsonl'

    def record(self, *, event='startup', component='runtime', status='ok', code='ready', **kwargs):
        return build_record(
            session_id='session-1', event=event, component=component,
            status=status, code=code, **kwargs,
        )

    def test_append_and_tail_preserve_order_and_safe_fields(self):
        journal = RuntimeJournal(self.path, fsync=False)
        journal.append(self.record(event='startup', code='boot-ready'))
        journal.append(self.record(
            event='model_request', component='chat', status='info', code='local-request',
            core_sha256='a' * 64, model='llama3.2:1b', memory_records=1,
            relationship_records=1,
        ))
        records = journal.tail()
        self.assertEqual([item.event for item in records], ['startup', 'model_request'])
        self.assertEqual(records[-1].model, 'llama3.2:1b')
        self.assertEqual(records[-1].memory_records, 1)

    def test_new_journal_instance_reads_records_from_prior_instance(self):
        first = RuntimeJournal(self.path, fsync=False)
        first.append(self.record(event='startup', code='first-process'))
        second = RuntimeJournal(self.path, fsync=False)
        second.append(self.record(event='shutdown', code='second-process'))
        records = RuntimeJournal(self.path, fsync=False).tail()
        self.assertEqual([item.code for item in records], ['first-process', 'second-process'])

    def test_fixed_schema_rejects_free_form_or_sensitive_shaped_values(self):
        with self.assertRaises(TypeError):
            build_record(
                session_id='session-1', event='startup', component='runtime',
                status='ok', code='ready', prompt='private words',
            )
        with self.assertRaisesRegex(JournalError, 'invalid model'):
            self.record(model='secret prompt contents here')
        with self.assertRaisesRegex(JournalError, 'invalid code'):
            self.record(code='contains private sentence')

    def test_serialized_record_contains_no_null_or_arbitrary_payload_fields(self):
        journal = RuntimeJournal(self.path, fsync=False)
        journal.append(self.record(event='service_health', code='healthy'))
        payload = json.loads(self.path.read_text(encoding='utf-8'))
        self.assertNotIn('model', payload)
        self.assertNotIn('memory_records', payload)
        self.assertNotIn('details', payload)
        self.assertNotIn('prompt', payload)
        self.assertEqual(payload['code'], 'healthy')

    def test_tail_limit_and_missing_file_are_bounded(self):
        journal = RuntimeJournal(self.path, fsync=False)
        self.assertEqual(journal.tail(), ())
        for index in range(5):
            journal.append(self.record(code='event-%d' % index))
        self.assertEqual([item.code for item in journal.tail(2)], ['event-3', 'event-4'])
        with self.assertRaisesRegex(JournalError, 'tail limit'):
            journal.tail(0)
        with self.assertRaisesRegex(JournalError, 'tail limit'):
            journal.tail(201)

    def test_malformed_recent_record_fails_visible_instead_of_being_skipped(self):
        journal = RuntimeJournal(self.path, fsync=False)
        journal.append(self.record(code='good'))
        with self.path.open('ab') as stream:
            stream.write(b'{broken-json}\n')
        with self.assertRaisesRegex(JournalError, 'invalid journal JSON'):
            journal.tail()

    def test_unknown_fields_in_existing_record_fail_closed(self):
        journal = RuntimeJournal(self.path, fsync=False)
        journal.append(self.record(code='good'))
        payload = json.loads(self.path.read_text(encoding='utf-8'))
        payload['prompt'] = 'should never be accepted'
        self.path.write_text(json.dumps(payload) + '\n', encoding='utf-8')
        with self.assertRaisesRegex(JournalError, 'fields do not match schema'):
            journal.tail()

    @unittest.skipUnless(os.name == 'posix', 'POSIX permission/symlink semantics required')
    def test_posix_rejects_non_private_file_and_symlink(self):
        journal = RuntimeJournal(self.path, fsync=False)
        journal.append(self.record(code='good'))
        os.chmod(self.path, 0o644)
        with self.assertRaisesRegex(JournalError, 'not private'):
            journal.append(self.record(code='blocked'))

        real = Path(self.temp.name) / 'real.jsonl'
        real.write_text('', encoding='utf-8')
        link = Path(self.temp.name) / 'link.jsonl'
        link.symlink_to(real)
        with self.assertRaisesRegex(JournalError, 'symlink'):
            RuntimeJournal(link, fsync=False).append(self.record(code='blocked'))


if __name__ == '__main__':
    unittest.main()
