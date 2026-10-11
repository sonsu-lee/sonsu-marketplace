"""Regression coverage for bounded receipts, streaming input, and zombie recovery."""
import importlib.util
import json
import os
from pathlib import Path
import sys
from types import SimpleNamespace
import unittest
from unittest import mock
import test_evidence_gates_v2 as fixtures


def module(name, path):
    spec = importlib.util.spec_from_file_location(name, path)
    result = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(result)
    return result


class Followup(unittest.TestCase):
    def setUp(self):
        self.f = fixtures.ManagedGates()
        self.f.setUp()
        self.addCleanup(self.f.doCleanups)
        self.g = module('followup_gate', self.f.script)
        self.m = module('followup_managed', self.f.script.parent / 'evidence_gates_v2.py')
        self.m.G = self.g

    def test_large_existing_history_compacts_without_losing_attempts(self):
        f = self.f
        f.init()
        f.checked()
        path = f.root / '.engineering/gates/tasks/task/state.json'
        state = json.loads(path.read_text())
        receipt = state['units']['design']['checks']['verify'][0]
        history = [dict(receipt, attempt=i) for i in range(1, 251)]
        state['units']['design']['checks']['verify'] = history
        path.write_bytes(self.g.encode(state))
        self.assertLess(path.stat().st_size, self.g.MAX_JSON)
        f.ok('run', '--unit', 'design', '--check', 'verify')
        latest = json.loads(path.read_text())['units']['design']['checks']['verify']
        self.assertEqual([r['attempt'] for r in latest], [251])
        self.assertLess(path.stat().st_size, 10000)
        for previous in history:
            archived = path.parent / ('design-check-verify-' + str(previous['attempt']) + '.receipt.json')
            self.assertEqual(json.loads(archived.read_text()), previous)
        f.ok('run', '--unit', 'design', '--check', 'verify')
        f.complete()
        self.assertTrue(f.ok('status')['ready'])

    def test_archive_retry_preserves_receipt_and_conflict_blocks_launch(self):
        f = self.f
        f.init()
        f.checked()
        args = SimpleNamespace(task_id='task', unit='design', check='verify', timeout=5)
        path = f.root / '.engineering/gates/tasks/task/design-check-verify-1.receipt.json'
        with mock.patch.object(self.m, 'save', side_effect=RuntimeError('interrupted save')):
            with self.assertRaisesRegex(RuntimeError, 'interrupted save'):
                self.m.run(f.root, args)
        original = path.read_bytes()
        f.ok('run', '--unit', 'design', '--check', 'verify')
        self.assertEqual(path.read_bytes(), original)
        # A conflicting file for the next archive must never be overwritten.
        conflict = path.with_name('design-check-verify-2.receipt.json')
        conflict.write_text('foreign evidence')
        result = f.call('run', '--unit', 'design', '--check', 'verify')
        self.assertIn('archived check receipt conflicts', result.stderr)
        self.assertEqual(conflict.read_text(), 'foreign evidence')
        self.assertFalse(path.with_name('design-check-verify-3.log').exists())

    def test_empty_package_does_not_reserve_round(self):
        f = self.f
        f.config['units'][0]['review'] = 'independent'
        f.init()
        f.checked()
        f.report.write_bytes(b' \n' * 100000)
        result = f.call('prepare-review', '--unit', 'design', '--gate', 'final-review', '--package', str(f.report))
        self.assertIn('empty review package', result.stderr)
        state = self.m.load(f.root, 'task')
        self.assertEqual(state['units']['design']['reviews']['final-review'], [])

    def test_package_is_streamed_and_frozen(self):
        f = self.f
        f.config['units'][0]['review'] = 'independent'
        f.init()
        f.checked()
        content = b' evidence\n' * 300000
        f.report.write_bytes(content)
        original = Path.read_bytes
        def guarded(path):
            if path == f.report:
                self.fail('bulk read of review input')
            return original(path)
        args = SimpleNamespace(task_id='task', unit='design', gate='final-review', package=str(f.report))
        with mock.patch.object(Path, 'read_bytes', guarded):
            with self.g.lock(f.root):
                row = self.m.prepare(f.root, self.m.load(f.root, 'task'), args, {})
        self.assertEqual(Path(row['package']).read_bytes(), content)
        self.assertEqual(row['files'][Path(row['package']).name], self.g.digest(content))

    @unittest.skipUnless(sys.platform == 'linux', 'Linux thread-group regression')
    def test_zombie_leader_with_live_thread_still_blocks(self):
        import signal
        import subprocess
        import time
        code = "import ctypes, threading, time; threading.Thread(target=lambda: time.sleep(30)).start(); ctypes.CDLL(None).pthread_exit(None)"
        child = subprocess.Popen([sys.executable, '-c', code], start_new_session=True)
        try:
            deadline = time.monotonic() + 5
            while time.monotonic() < deadline:
                fields = Path('/proc/' + str(child.pid) + '/stat').read_text().rsplit(') ', 1)[1].split()
                if fields[0] == 'Z':
                    break
                time.sleep(0.01)
            self.assertEqual(fields[0], 'Z')
            self.assertGreater(int(fields[17]), 1)
            self.assertFalse(self.m.zombie_group(child.pid))
        finally:
            os.killpg(child.pid, signal.SIGKILL)
            child.wait(timeout=5)

    @unittest.skipUnless(sys.platform == 'linux', 'Linux procfs regression')
    def test_zombie_group_recovers_but_live_group_blocks(self):
        f = self.f
        f.init()
        state = self.m.load(f.root, 'task')
        directory = self.m.directory(f.root, state)
        (directory / 'test.lease').touch()
        pid = os.fork()
        if pid == 0:
            os.setsid()
            import time
            time.sleep(0.3)
            os._exit(0)
        try:
            import time
            deadline = time.monotonic() + 2
            while os.getpgid(pid) != pid and time.monotonic() < deadline:
                time.sleep(0.001)
            self.g.atomic_write(directory / 'test.process.json', self.g.encode({'invocation_id': 'test', 'pid': pid, 'pgid': pid}))
            row = {'invocation': {'id': 'test', 'scope': 'process-group-and-inherited-lease', 'lease': 'test.lease', 'process': 'test.process.json'}}
            with self.assertRaisesRegex(self.g.GateError, 'still active'):
                with self.m.quiescent_check(f.root, state, row):
                    pass
            os.waitid(os.P_PID, pid, os.WEXITED | os.WNOWAIT)
            with self.m.quiescent_check(f.root, state, row):
                pass
        finally:
            os.waitpid(pid, 0)
