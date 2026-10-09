"""worklog-v1 hook recording and CLI contracts."""
from datetime import datetime, timedelta, timezone
import fcntl
import importlib.util
import json
import os
from pathlib import Path
import shutil
import subprocess
import sys
import tempfile
import unittest


ROOT = Path(__file__).resolve().parents[2]
PACKAGE = ROOT / "plugins/worklog"
SCRIPT = PACKAGE / "scripts/worklog.py"
FIXTURES = Path(__file__).resolve().parent / "fixtures"
COMMAND = 'python3 -B "${CLAUDE_PLUGIN_ROOT}/scripts/worklog.py" hook --host '


def load_worklog():
    spec = importlib.util.spec_from_file_location("worklog_under_test", SCRIPT)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


class WorklogTests(unittest.TestCase):
    def setUp(self):
        self.temporary = tempfile.TemporaryDirectory()
        self.root = Path(self.temporary.name).resolve()
        self.home = self.root / "home"
        self.project = self.root / "project"
        self.project.mkdir()
        subprocess.run(["git", "init", "-q", str(self.project)], check=True)
        self.env = {key: value for key, value in os.environ.items()
                    if key not in ("SONSU_WORKLOG", "SONSU_WORKLOG_PROMPTS")}
        self.env["SONSU_WORKLOG_HOME"] = str(self.home)

    def tearDown(self):
        self.temporary.cleanup()

    def hook(self, host, event, env=None, raw=None):
        result = subprocess.run([sys.executable, "-B", str(SCRIPT), "hook", "--host", host],
                                input=raw if raw is not None else json.dumps(event),
                                text=True, capture_output=True, env=env or self.env)
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertEqual(result.stdout, "")
        self.assertEqual(result.stderr, "")
        return result

    def cli(self, *args, env=None):
        result = subprocess.run([sys.executable, "-B", str(SCRIPT), *args, "--cwd", str(self.project)],
                                text=True, capture_output=True, env=env or self.env)
        self.assertEqual(result.returncode, 0, result.stderr)
        return result.stdout

    def event(self, name, session="session-1", **fields):
        return {"hook_event_name": name, "session_id": session, "cwd": str(self.project), **fields}

    def records(self, host=None):
        found = []
        for log in sorted(self.home.glob(f"*/{host or '*'}/*/*.jsonl")):
            found.extend(json.loads(line) for line in log.read_text(encoding="utf-8").splitlines())
        return found

    def project_dir(self):
        return Path(self.cli("where").strip())

    def test_claude_failure_records_exit_code_and_first_error_line(self):
        event = json.loads((FIXTURES / "claude-post-tool-use-failure.json").read_text(encoding="utf-8"))
        event["cwd"] = str(self.project)
        self.hook("claude", event)
        [record] = self.records("claude")
        self.assertEqual(record["schema"], "worklog-v1")
        self.assertEqual(record["event"], "tool_result")
        self.assertEqual(record["signal_source"], "hook:PostToolUseFailure")
        self.assertEqual(record["session_id"], "fixture-claude")
        self.assertRegex(record["project_key"], r"\A[0-9a-f]{20}\Z")
        self.assertRegex(record["ts"], r"\A\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}\.\d{3}Z\Z")
        self.assertEqual(record["data"], {
            "outcome": "failed", "tool_name": "Bash", "tool_use_id": "toolu_fixture_failure",
            "exit_code": 1, "error": "ls: ./no-such-file-xyz: No such file or directory",
            "is_interrupt": False, "duration_ms": 335, "input_excerpt": "ls ./no-such-file-xyz",
        })
        project = self.project_dir()
        self.assertEqual(json.loads((project / "project.json").read_text())["identity"],
                         str((self.project / ".git").resolve()))

    def test_codex_stop_reads_failed_items_once(self):
        rollout = self.root / "rollout.jsonl"
        shutil.copyfile(FIXTURES / "codex-rollout.jsonl", rollout)
        self.hook("codex", self.event("SessionStart", transcript_path=str(rollout), source="startup"))
        self.hook("codex", self.event("Stop", transcript_path=str(rollout)))
        self.hook("codex", self.event("Stop", transcript_path=str(rollout)))
        failed = [r for r in self.records("codex") if r["event"] == "tool_result"]
        self.assertEqual(len(failed), 1)
        [record] = failed
        self.assertEqual(record["signal_source"], "rollout:item_completed")
        self.assertEqual(record["host_version"], "0.160.0")
        self.assertEqual(record["turn_id"], "01a10755-3aee-7373-a6e5-4d917dca02f7")
        self.assertEqual(record["data"], {
            "outcome": "failed", "tool_name": "CommandExecution",
            "tool_use_id": "exec-85a4be90-9c82-481d-acdf-c407dc9a2e36", "exit_code": 1,
            "error": "ls: ./no-such-file-xyz: No such file or directory", "is_interrupt": None,
            "duration_ms": 0, "input_excerpt": "ls ./no-such-file-xyz",
        })
        # A partial trailing line waits for the next Stop instead of being skipped.
        item = json.loads(rollout.read_text().splitlines()[2])
        item["payload"]["item"]["id"] = "exec-second"
        line = json.dumps(item)
        with open(rollout, "a") as handle:
            handle.write(line[:40])
        self.hook("codex", self.event("Stop", transcript_path=str(rollout)))
        self.assertEqual(len([r for r in self.records("codex") if r["event"] == "tool_result"]), 1)
        with open(rollout, "a") as handle:
            handle.write(line[40:] + "\n")
        self.hook("codex", self.event("Stop"))
        ids = [r["data"]["tool_use_id"] for r in self.records("codex") if r["event"] == "tool_result"]
        self.assertEqual(ids, ["exec-85a4be90-9c82-481d-acdf-c407dc9a2e36", "exec-second"])

    def test_codex_post_tool_use_outcome_unknown(self):
        self.hook("codex", self.event("PostToolUse", tool_name="Bash", tool_use_id="call-1",
                                      tool_input={"command": "ls ./no-such-file-xyz"},
                                      tool_response="ls: ./no-such-file-xyz: No such file or directory"))
        [record] = self.records("codex")
        self.assertEqual(record["signal_source"], "hook:PostToolUse")
        self.assertEqual(record["data"]["outcome"], "unknown")
        self.assertEqual(record["data"]["tool_use_id"], "call-1")
        self.assertIsNone(record["host_version"])

    def test_prompt_excerpt_redacts_secrets_and_flags_correction(self):
        secret = "sk-" + "a1" * 15
        prompt = f"아니야, 그거 말고 다시 해. api_key={secret} 이어서 " + "긴 설명 " * 60
        self.hook("claude", self.event("UserPromptSubmit", prompt=prompt))
        self.hook("claude", self.event("UserPromptSubmit", prompt="README를 요약해 줘"))
        env = dict(self.env, SONSU_WORKLOG_PROMPTS="off")
        self.hook("codex", self.event("UserPromptSubmit", prompt="that's not what I asked"), env=env)
        first, second = self.records("claude")
        self.assertEqual(first["data"]["chars"], len(prompt))
        self.assertTrue(first["data"]["correction_hint"])
        self.assertLessEqual(len(first["data"]["excerpt"]), 160)
        self.assertIn("[redacted]", first["data"]["excerpt"])
        self.assertNotIn(secret, json.dumps(first))
        self.assertFalse(second["data"]["correction_hint"])
        [hidden] = self.records("codex")
        self.assertEqual(hidden["data"], {"chars": len("that's not what I asked"), "correction_hint": True})

    def test_disabled_env_and_project_file_write_nothing(self):
        for value in ("off", "0", "false", "OFF"):
            self.hook("claude", self.event("SessionStart"), env=dict(self.env, SONSU_WORKLOG=value))
        self.assertFalse(self.home.exists())
        project = self.project_dir()
        project.mkdir(parents=True)
        (project / "disabled").write_text("")
        self.hook("claude", self.event("SessionStart"))
        self.hook("codex", self.event("UserPromptSubmit", prompt="hello"))
        self.assertEqual([path.name for path in project.iterdir()], ["disabled"])

    def test_project_key_matches_memory_manager(self):
        sys.path.insert(0, str(ROOT / "plugins/memory-manager/scripts"))
        try:
            import memory_store
        finally:
            sys.path.pop(0)
        worklog = load_worklog()
        nested = self.project / "src/deep"
        nested.mkdir(parents=True)
        plain = self.root / "not-a-repo"
        plain.mkdir()
        for location in (self.project, nested, plain):
            with self.subTest(location=location):
                self.assertEqual(worklog.project_key(str(location)), memory_store.project_key(str(location)))
        self.assertEqual(worklog.project_key(str(nested)), worklog.project_key(str(self.project)))

    def test_prune_removes_only_expired_dates(self):
        today = datetime.now(timezone.utc).date()
        project = self.project_dir()
        old = (today - timedelta(days=91)).isoformat()
        kept = (today - timedelta(days=89)).isoformat()
        for host in ("claude", "codex", "omp"):
            for name in (old, kept, "notes"):
                (project / host / name).mkdir(parents=True)
        self.assertEqual(self.cli("prune").strip(), "3")
        for host in ("claude", "codex", "omp"):
            self.assertEqual(sorted(path.name for path in (project / host).iterdir()), [kept, "notes"])
        # SessionStart prunes its own host at most once per 24 hours.
        (project / "claude" / old).mkdir()
        self.hook("claude", self.event("SessionStart"))
        self.assertFalse((project / "claude" / old).exists())
        self.assertTrue((project / "claude/.state/last-prune").is_file())
        (project / "claude" / old).mkdir()
        self.hook("claude", self.event("SessionStart", session="session-2"))
        self.assertTrue((project / "claude" / old).exists())
        state_dir = project / "claude/.state"
        expired_state = state_dir / "active.json"
        expired_lock = state_dir / "active.lock"
        expired_state.write_text('{"rollout_offset": 123}')
        expired_lock.touch()
        expired = (datetime.now(timezone.utc) - timedelta(days=100)).timestamp()
        for path in (expired_state, expired_lock):
            os.utime(path, (expired, expired))
        with expired_lock.open("r+") as lock:
            fcntl.flock(lock, fcntl.LOCK_EX)
            inode = os.fstat(lock.fileno()).st_ino
            self.cli("prune")
            self.assertEqual(expired_lock.stat().st_ino, inode)
            self.assertEqual(json.loads(expired_state.read_text())["rollout_offset"], 123)

    def test_invalid_stdin_exits_zero_without_output(self):
        for raw in ("", "not json", "[]", "{\"hook_event_name\": \"Stop\"}",
                    json.dumps(self.event("NoSuchEvent"))):
            with self.subTest(raw=raw):
                self.hook("claude", None, raw=raw)
                self.hook("codex", None, raw=raw)
        self.assertFalse(self.home.exists())

    def test_claude_stop_records_session_start_hook_outputs_once(self):
        transcript = str(FIXTURES / "claude-transcript.jsonl")
        self.hook("claude", self.event("SessionStart", transcript_path=transcript, source="startup", model="haiku"))
        self.hook("claude", self.event("Stop", transcript_path=transcript, last_assistant_message="done"))
        self.hook("claude", self.event("Stop", transcript_path=transcript, last_assistant_message="again"))
        records = self.records("claude")
        self.assertEqual([r["event"] for r in records],
                         ["session_start", "context_load", "context_load", "stop", "stop"])
        self.assertEqual(records[0]["data"], {"source": "startup", "transcript_path": transcript,
                                              "model": "haiku", "agent_kind": None})
        loads = [r for r in records if r["event"] == "context_load"]
        self.assertEqual([r["signal_source"] for r in loads], ["transcript:attachment"] * 2)
        self.assertEqual(loads[0]["data"], {"kind": "hook_output", "hook_name": "SessionStart:startup",
                                            "command": 'bash "${CLAUDE_PLUGIN_ROOT}/hooks/session-start.sh"',
                                            "chars": 1000})
        self.assertEqual(loads[1]["data"]["chars"],
                         len(json.dumps(["SessionStart hook additional context: fixture guidance"])))
        self.assertIsNone(records[0]["host_version"])
        self.assertEqual({r["host_version"] for r in records[1:]}, {"2.1.286"})
        self.assertEqual(records[3]["data"], {"last_message_chars": 4})

    def test_summary_and_failures_cli(self):
        failure = json.loads((FIXTURES / "claude-post-tool-use-failure.json").read_text(encoding="utf-8"))
        failure["cwd"] = str(self.project)
        transcript = str(self.root / "claude.jsonl")
        self.hook("claude", self.event("SessionStart", session="fixture-claude", transcript_path=transcript))
        self.hook("claude", self.event("UserPromptSubmit", session="fixture-claude", prompt="아니야 다시 해"))
        self.hook("claude", failure)
        self.hook("claude", self.event("PostToolUse", session="fixture-claude", tool_name="Read", tool_use_id="t2"))
        rollout = self.root / "rollout.jsonl"
        shutil.copyfile(FIXTURES / "codex-rollout.jsonl", rollout)
        self.hook("codex", self.event("SessionStart", session="codex-1", transcript_path=str(rollout)))
        self.hook("codex", self.event("PostToolUse", session="codex-1", tool_name="Bash", tool_use_id="c1"))
        self.hook("codex", self.event("Stop", session="codex-1"))

        text = self.cli("summary").splitlines()
        self.assertEqual(text[0], f"worklog {self.project_dir()} (last 7 days)")
        self.assertIn("sessions: claude=1 codex=1", text)
        for line in ("  tool_result failed 2", "  tool_result ok 1", "  tool_result unknown 1",
                     "  user_prompt 1 (corrections 1)", "  session_start 2", "  stop 1"):
            self.assertIn(line, text)
        failure_lines = [line for line in text if " exit=" in line]
        self.assertEqual(len(failure_lines), 2)
        claude_line = next(line for line in failure_lines if " claude " in line)
        self.assertRegex(claude_line, r'^  \S+Z claude fixture- Bash exit=1 "ls: \./no-such-file-xyz: No such file '
                                      r'or directory" transcript=\S+claude\.jsonl tool_use_id=toolu_fixture_failure$')
        summary = json.loads(self.cli("summary", "--host", "codex", "--format", "json"))
        self.assertEqual(summary["sessions"], {"codex": 1})
        self.assertEqual(summary["failures"][0]["transcript_path"], str(rollout))

        entries = [json.loads(line) for line in self.cli("failures", "--format", "jsonl").splitlines()]
        self.assertEqual(sorted(entry["event"] for entry in entries), ["tool_result", "tool_result", "user_prompt"])
        for entry in entries:
            with self.subTest(event=entry["event"], host=entry["host"]):
                lines = Path(entry["log_path"]).read_text(encoding="utf-8").splitlines()
                original = json.loads(lines[entry["line"] - 1])
                self.assertEqual(original, {k: v for k, v in entry.items()
                                            if k not in ("log_path", "line", "transcript_path")})
                self.assertEqual(entry["transcript_path"], transcript if entry["host"] == "claude" else str(rollout))

    def test_symlinked_host_never_writes_outside_log_root(self):
        project = self.project_dir()
        project.mkdir(parents=True)
        outside = self.root / "outside"
        outside.mkdir()
        (outside / "important.txt").write_text("keep")
        (project / "claude").symlink_to(outside, target_is_directory=True)
        result = subprocess.run([sys.executable, "-B", str(SCRIPT), "hook", "--host", "claude"],
                                input=json.dumps(self.event("SessionStart")), text=True,
                                capture_output=True, env=self.env)
        self.assertEqual(result.returncode, 0)
        self.assertEqual(result.stdout, "")
        self.assertIn("WorklogError", result.stderr)
        self.assertEqual(sorted(p.name for p in outside.iterdir()), ["important.txt"])
        self.assertEqual((outside / "important.txt").read_text(), "keep")

    def test_transcript_hook_command_redacts_secrets(self):
        transcript = self.root / "claude.jsonl"
        transcript.write_text(json.dumps({
            "type": "attachment",
            "attachment": {"type": "hook_success", "hookEvent": "SessionStart",
                           "hookName": "SessionStart:startup",
                           "command": "API_TOKEN=example-sensitive-value ./session-start.sh", "stdout": "ok"},
        }) + "\n")
        self.hook("claude", self.event("SessionStart", transcript_path=str(transcript)))
        self.hook("claude", self.event("Stop", transcript_path=str(transcript)))
        [load] = [r for r in self.records("claude") if r["event"] == "context_load"]
        self.assertEqual(load["data"]["command"], "[redacted] ./session-start.sh")
        self.assertNotIn("example-sensitive-value", json.dumps(self.records("claude")))

    def test_expired_session_resumes_in_current_date_without_resetting_offset(self):
        project = self.project_dir()
        state_dir = project / "codex/.state"
        state_dir.mkdir(parents=True)
        old = (datetime.now(timezone.utc).date() - timedelta(days=91)).isoformat()
        state_path = state_dir / "session-1.json"
        state_path.write_text(json.dumps({"date": old, "rollout_offset": 123}))
        self.hook("codex", self.event("SessionStart", source="resume", transcript_path="rollout.jsonl"))
        [record] = self.records("codex")
        self.assertEqual(record["event"], "session_start")
        state = json.loads(state_path.read_text())
        self.assertEqual(state["date"], datetime.now(timezone.utc).date().isoformat())
        self.assertEqual(state["rollout_offset"], 123)
        self.assertFalse((project / "codex" / old).exists())

    def test_hooks_json_event_sets_per_host(self):
        expected = {
            "hooks/hooks.json": ("codex", {
                "SessionStart": (5, False), "UserPromptSubmit": (5, False), "PostToolUse": (5, True),
                "Stop": (10, False), "SubagentStop": (5, False), "PreCompact": (5, False),
                "Interrupt": (3, False), "SessionEnd": (3, False)}),
            "hooks/claude-hooks.json": ("claude", {
                "SessionStart": (5, False), "InstructionsLoaded": (5, True), "UserPromptSubmit": (5, False),
                "PostToolUse": (5, True), "PostToolUseFailure": (5, True), "PermissionDenied": (5, False),
                "Stop": (10, False), "StopFailure": (5, False), "SubagentStop": (5, False),
                "PreCompact": (5, False), "SessionEnd": (None, False)}),
        }
        worklog = load_worklog()
        for relative, (host, events) in expected.items():
            with self.subTest(file=relative):
                hooks = json.loads((PACKAGE / relative).read_text(encoding="utf-8"))["hooks"]
                self.assertEqual(set(hooks), set(events))
                self.assertEqual(set(hooks), worklog.HOST_EVENTS[host])
                for name, (timeout, is_async) in events.items():
                    [group] = hooks[name]
                    self.assertNotIn("matcher", group)
                    [handler] = group["hooks"]
                    self.assertEqual(handler["command"], COMMAND + host)
                    self.assertEqual(handler.get("timeout"), timeout)
                    self.assertEqual(handler.get("async", False), is_async)


if __name__ == "__main__":
    unittest.main()
