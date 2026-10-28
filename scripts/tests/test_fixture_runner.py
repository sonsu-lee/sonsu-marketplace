"""Model-free behavioral checks for fixture workspace isolation."""
import json
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest
from unittest.mock import patch

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
import check_activation as ca
import compare_skill


def query(prompt, **fields):
    return ca.Query('case', [ca.Step(prompt, 'load', forbid=fields.pop('forbid', []))], **fields)


def finished(**fields):
    return ca.Trace(reached=True, complete=True, session='session', **fields)


class FixtureRunnerTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name)
        self.input = self.root / 'evals/fixtures/sample/input'
        self.input.mkdir(parents=True)
        (self.input / 'file.txt').write_text('original')
        self.base = self.root / 'homes'
        self.spec = ca.Spec(self.root / 'spec.json', 'plugin', 'skill', [])
        self.pin = ca.Pin('model', 'high')

    def run_query(self, case, action, allow=False, trace=None):
        def execute(*args, **kwargs):
            target = args[5]
            self.assertEqual((target / 'file.txt').read_text(), 'original')
            action(target, kwargs.get('writable', False))
            return subprocess.CompletedProcess([], 0, '', ''), trace or finished()
        with patch.object(ca, 'execute', side_effect=execute):
            return ca.run_once('omp', self.base, self.root, self.pin, self.spec,
                               case, 'case', allow)[-1]

    def test_readonly_fixture_is_populated_and_mutation_is_detected(self):
        case = query('review', fixture='sample', forbid=['new-files'])
        def action(target, writable):
            self.assertFalse(writable)
            (target / 'file.txt').write_text('modified')
        turn = self.run_query(case, action)
        self.assertEqual(turn['status'], 'fail')
        self.assertIn('readonly fixture was modified', turn['problems'])
        self.assertEqual((self.input / 'file.txt').read_text(), 'original')
        self.assertFalse(any(p.startswith('new files') for p in turn['problems']))

    def test_timeout_cannot_hide_readonly_mutation(self):
        case = query('review', fixture='sample')
        def action(target, writable):
            (target / 'file.txt').write_text('unauthorized')
        turn = self.run_query(case, action, trace=ca.Trace(reached=True, failed=True, error='timeout'))
        self.assertEqual(turn['status'], 'fail')
        self.assertIn('readonly fixture was modified', turn['problems'])

    def test_writable_requires_opt_in_before_execution(self):
        case = query('edit', fixture='sample', fixture_mode='writable')
        with patch.object(ca, 'execute') as execute:
            with self.assertRaisesRegex(ValueError, 'writable'):
                ca.run_once('omp', self.base, self.root, self.pin, self.spec, case, 'case')
            execute.assert_not_called()

    def test_traversal_and_symlink_fixture_rejected(self):
        for name in ('../sample', '/tmp', 'sample/../sample'):
            with self.assertRaises(ValueError):
                ca.fixture_input(self.root, name)
        (self.input / 'escape').symlink_to(self.root, target_is_directory=True)
        with self.assertRaises(ValueError):
            ca.fixture_input(self.root, 'sample')

    def test_output_symlink_is_failure_not_followed(self):
        case = query('review', fixture='sample')
        def action(target, writable):
            (target / 'escape').symlink_to(self.root, target_is_directory=True)
        turn = self.run_query(case, action)
        self.assertEqual(turn['status'], 'fail')
        self.assertTrue(any('symlink' in p for p in turn['problems']))

    def test_intermediate_intentions_do_not_satisfy_final_report(self):
        for client, events in (
            ('omp', [
                {'type': 'message_end', 'message': {'role': 'assistant', 'content': [
                    {'type': 'text', 'text': 'I will inspect broken.py for syntax errors'}]}},
                {'type': 'message_end', 'message': {'role': 'assistant', 'content': [
                    {'type': 'text', 'text': 'Unable to inspect the input'}]}}]),
            ('codex', [
                {'type': 'item.completed', 'item': {'type': 'agent_message',
                    'text': 'I will inspect broken.py for syntax errors'}},
                {'type': 'item.completed', 'item': {'type': 'agent_message',
                    'text': 'Unable to inspect the input'}}]),
            ('claude', [
                {'type': 'assistant', 'message': {'role': 'assistant', 'content': [
                    {'type': 'text', 'text': 'I will inspect broken.py for syntax errors'}]}},
                {'type': 'result', 'result': 'Unable to inspect the input'}]),
        ):
            with self.subTest(client=client):
                self.assertEqual(ca.output_text('\n'.join(map(json.dumps, events))),
                                 'Unable to inspect the input')

    def execute_real(self, target, **flags):
        return ca.execute('omp', self.base, self.root, self.pin, 'edit', target, '', {},
                          'session', target.parent / 'sessions', **flags)

    def test_writable_fails_closed_on_unsupported_platform(self):
        target = self.root / 'case' / 'target'
        target.mkdir(parents=True)
        with patch.object(ca.sys, 'platform', 'linux'), patch.object(ca.cp, 'run') as run:
            with self.assertRaisesRegex(RuntimeError, 'unsupported'):
                self.execute_real(target, writable=True)
            run.assert_not_called()

    def test_outcome_grades_workspace_without_altering_fixture(self):
        fixture = self.root / 'evals/fixtures/tiny'
        source = fixture / 'input'
        expected = fixture / 'expected'
        source.mkdir(parents=True)
        expected.mkdir()
        (source / 'single.py').write_text('value = 1\n')
        (expected / 'single.py').write_text('value = 2\n')
        (fixture / 'outcome.json').write_text(json.dumps({'modified': ['single.py']}))
        case = query('edit', fixture='tiny', fixture_mode='writable', outcome='tiny')
        def execute(*args, **kwargs):
            (args[5] / 'single.py').write_text('value=2\n')
            return subprocess.CompletedProcess([], 0, '', ''), finished(successful={'plugin:skill'})
        with patch.object(ca, 'execute', side_effect=execute):
            turn = ca.run_once('omp', self.base, self.root, self.pin, self.spec,
                               case, 'outcome', True)[-1]
        self.assertEqual(turn['problems'], [])
        self.assertEqual((source / 'single.py').read_text(), 'value = 1\n')
        self.assertEqual((expected / 'single.py').read_text(), 'value = 2\n')

    def test_compare_rejects_fixture_before_running(self):
        case = query('review', fixture='sample')
        with patch.object(ca, 'execute') as execute:
            with self.assertRaisesRegex(ValueError, 'unsupported'):
                compare_skill.answer(self.base, self.root, self.pin, self.root,
                                     'plugin', 'skill', case, 'base', 'case')
            execute.assert_not_called()

    @unittest.skipUnless(sys.platform == 'darwin', 'macOS sandbox-exec required')
    def test_sandbox_enforces_workspace_boundary(self):
        workspace = self.root / 'case' / 'target'
        workspace.mkdir(parents=True)
        outside = self.root / 'outside.txt'
        code = ("from pathlib import Path; "
                "Path('allowed.txt').write_text('ok'); "
                f"Path({str(outside)!r}).write_text('blocked')")
        with patch.object(ca, 'command', return_value=['/usr/bin/python3', '-c', code]):
            proc, _ = self.execute_real(workspace, writable=True)
        self.assertNotEqual(proc.returncode, 0)
        self.assertEqual((workspace / 'allowed.txt').read_text(), 'ok')
        self.assertFalse(outside.exists())

    @unittest.skipUnless(sys.platform == 'darwin', 'macOS sandbox-exec required')
    def test_readonly_sandbox_denies_fixture_write_but_allows_temp(self):
        workspace = self.root / 'case' / 'target'
        workspace.mkdir(parents=True)
        code = ("import os; from pathlib import Path; "
                "Path(os.environ['TMPDIR'], 'scratch').write_text('ok'); "
                "Path('blocked').write_text('no')")
        with patch.object(ca, 'command', return_value=['/usr/bin/python3', '-c', code]):
            proc, _ = self.execute_real(workspace, sandbox_readonly=True)
        self.assertNotEqual(proc.returncode, 0)
        self.assertFalse((workspace / 'blocked').exists())
        self.assertTrue((self.base / 'omp-home/fixture-tmp/case/scratch').exists())

    def test_spec_does_not_confer_write_permission(self):
        path = self.root / 'spec.json'
        path.write_text(json.dumps({'skill': 'p:s', 'queries': [{'id': 'x', 'prompt': 'p',
                        'expect': 'load', 'fixture': 'sample', 'forbid': ['new-files']}]}))
        case = ca.load_spec(path).queries[0]
        self.assertEqual(case.fixture_mode, 'readonly')
        self.assertEqual(case.steps[0].forbid, ['new-files'])

    def test_spec_rejects_mixed_fixture_sources_and_orphan_outcomes(self):
        path = self.root / 'spec.json'
        for extra in ({'fixture': 'sample', 'fixtures': {'a.txt': 'x'}},
                      {'outcome': 'tiny'}, {'fixture_mode': 'writable'}):
            with self.subTest(extra=extra):
                path.write_text(json.dumps({'skill': 'p:s', 'queries': [
                    {'id': 'x', 'prompt': 'p', 'expect': 'load', **extra}]}))
                with self.assertRaises(ValueError):
                    ca.load_spec(path)


if __name__ == '__main__':
    unittest.main()
