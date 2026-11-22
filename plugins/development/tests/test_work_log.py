"""Exercise the work log's opt-in, privacy, and concurrent append contract."""

import concurrent.futures
import json
import os
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest

HOOK = Path(__file__).resolve().parents[1] / "hooks" / "work_log.py"


class WorkLogTests(unittest.TestCase):
    def invoke(self, event, directory=None):
        env = dict(os.environ)
        env.pop("SONSU_WORK_LOG_DIR", None)
        if directory is not None:
            env["SONSU_WORK_LOG_DIR"] = str(directory)
        return subprocess.run([sys.executable, str(HOOK), "claude"], input=json.dumps(event),
                              text=True, capture_output=True, env=env, check=False)

    def test_opt_in_and_private_event_without_input_contents(self):
        event = {"hook_event_name": "SubagentStart", "session_id": "session-secret",
                 "agent_id": "agent-secret", "prompt": "private prompt"}
        with tempfile.TemporaryDirectory() as tmp:
            target = Path(tmp) / "logs"
            self.assertEqual(self.invoke(event).returncode, 0)
            self.assertFalse(target.exists())
            self.assertEqual(self.invoke(event, target).returncode, 0)
            path = target / "events.jsonl"
            text = path.read_text()
            entry = json.loads(text)
            self.assertEqual(entry["event"], "subagent_started")
            self.assertEqual(entry["client"], "claude")
            self.assertNotIn("secret", text)
            self.assertNotIn("private prompt", text)
            self.assertEqual(path.stat().st_mode & 0o077, 0)

    def test_parallel_writers_leave_complete_individual_events(self):
        with tempfile.TemporaryDirectory() as tmp:
            target = Path(tmp) / "logs"
            event = {"hook_event_name": "SessionStart", "session_id": "s"}
            with concurrent.futures.ThreadPoolExecutor(max_workers=8) as pool:
                results = list(pool.map(lambda _: self.invoke(event, target), range(24)))
            self.assertTrue(all(result.returncode == 0 and not result.stderr for result in results))
            entries = [json.loads(line) for line in (target / "events.jsonl").read_text().splitlines()]
            self.assertEqual(len(entries), 24)
            self.assertTrue(all(entry["event"] == "session_started" for entry in entries))

    def test_task_completion_is_recorded_as_a_request_not_a_success(self):
        with tempfile.TemporaryDirectory() as tmp:
            target = Path(tmp) / "logs"
            result = self.invoke({"hook_event_name": "TaskCompleted", "task_id": "task-1"}, target)
            self.assertEqual(result.returncode, 0)
            entry = json.loads((target / "events.jsonl").read_text())
            self.assertEqual(entry["event"], "task_completion_requested")

    def test_failed_turn_is_not_recorded_as_success(self):
        with tempfile.TemporaryDirectory() as tmp:
            target = Path(tmp) / "logs"
            self.invoke({"hook_event_name": "StopFailure", "error": "private"}, target)
            entry = json.loads((target / "events.jsonl").read_text())
            self.assertEqual(entry["event"], "turn_failed")
            self.assertNotIn("private", json.dumps(entry))

    def test_log_failure_does_not_block_hook(self):
        with tempfile.TemporaryDirectory() as tmp:
            target = Path(tmp) / "not-a-directory"
            target.write_text("existing")
            result = self.invoke({"hook_event_name": "SessionStart"}, target)
            self.assertEqual(result.returncode, 0)
            self.assertIn("work log unavailable", result.stderr)
            self.assertEqual(target.read_text(), "existing")

    def test_existing_public_log_is_not_appended(self):
        with tempfile.TemporaryDirectory() as tmp:
            target = Path(tmp)
            path = target / "events.jsonl"
            path.write_text("existing\n")
            path.chmod(0o644)
            result = self.invoke({"hook_event_name": "SessionStart"}, target)
            self.assertEqual(result.returncode, 0)
            self.assertIn("work log unavailable", result.stderr)
            self.assertEqual(path.read_text(), "existing\n")

    def test_codex_subagent_stop_is_nonblocking_with_missing_or_working_script(self):
        configs = ("codex.json", "codex-user.json")
        for config in configs:
            command = json.loads((HOOK.parent / config).read_text())["hooks"]["SubagentStop"][0]["hooks"][0]["command"]
            with self.subTest(config=config), tempfile.TemporaryDirectory() as tmp:
                env = dict(os.environ, PLUGIN_ROOT=tmp, DEVELOPMENT_PLUGIN_ROOT=tmp)
                env.pop("SONSU_WORK_LOG_DIR", None)
                result = subprocess.run(command, shell=True, input="{}", text=True, capture_output=True, env=env)
                self.assertEqual(result.returncode, 0)
                self.assertEqual(json.loads(result.stdout), {})
                env.update(PLUGIN_ROOT=str(HOOK.parent.parent),
                           DEVELOPMENT_PLUGIN_ROOT=str(HOOK.parent.parent),
                           SONSU_WORK_LOG_DIR=tmp)
                event = json.dumps({"hook_event_name": "SubagentStop", "session_id": "s"})
                result = subprocess.run(command, shell=True, input=event, text=True, capture_output=True, env=env)
                self.assertEqual(result.returncode, 0)
                self.assertEqual(json.loads(result.stdout), {})
                entry = json.loads((Path(tmp) / "events.jsonl").read_text())
                self.assertEqual(entry["event"], "subagent_stopped")


if __name__ == "__main__":
    unittest.main()
