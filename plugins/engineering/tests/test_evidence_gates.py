"""Exercise the installed gate CLI and hooks in disposable Git worktrees."""
import concurrent.futures
import fcntl
import json
import os
from pathlib import Path
import shutil
import subprocess
import sys
import tempfile
import time
import unittest


ROOT = Path(__file__).resolve().parents[3]
SCRIPT = ROOT / "plugins/engineering/scripts/evidence-gates.py"


class EvidenceGateTests(unittest.TestCase):
    def setUp(self):
        self.assertTrue(SCRIPT.is_file(), "evidence gate runtime has not been implemented")
        self.tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        self.base = Path(self.tmp.name).resolve()
        self.work = self.base / "work space"
        self.work.mkdir()
        self.package = self.base / "installed engineering"
        (self.package / "scripts").mkdir(parents=True)
        self.script = self.package / "scripts/evidence-gates.py"
        shutil.copyfile(SCRIPT, self.script)
        policy = self.package / "skills/using-engineering-skills/references/quality-gates.md"
        policy.parent.mkdir(parents=True)
        policy.write_text("Verification, final review, and a fresh red-team are required.\n")
        self.policy = policy
        self.env = dict(os.environ, CODEX_THREAD_ID="session-a", PYTHONDONTWRITEBYTECODE="1")
        for key in ("CLAUDE_CODE_SESSION_ID", "GIT_DIR", "GIT_WORK_TREE", "GIT_INDEX_FILE", "GIT_COMMON_DIR"):
            self.env.pop(key, None)
        self.git("init", "-q")
        (self.work / ".gitignore").write_text(".engineering/\nignored.txt\n")
        (self.work / "source.py").write_text("value = 1\n")
        (self.work / ".engineering").mkdir()
        (self.work / ".engineering/plan.md").write_text("Implement value and verify it.\n")
        self.git("add", ".gitignore", "source.py")
        self.config = {"inputs": [".engineering/plan.md"], "checks": [
            {"id": "unit", "argv": [sys.executable, "-c", "print('verified')"]}]}
        self.bundle = self.base / "review-input.md"
        self.bundle.write_text("Immutable review input for the whole change.\n")
        self.report = self.base / "review-output.md"
        self.report.write_text("Reviewed the supplied change and verification evidence.\n")

    def git(self, *args):
        return subprocess.run(["git", *args], cwd=self.work, env=self.env,
                              check=True, capture_output=True, text=True).stdout.strip()

    def call(self, command, *args, data=None, env=None):
        return subprocess.run([sys.executable, str(self.script), command, *args],
                              cwd=self.work, env=env or self.env, text=True,
                              input=json.dumps(data) if data is not None else "",
                              capture_output=True, timeout=15)

    def ok(self, result):
        self.assertEqual(result.returncode, 0, result.stderr + result.stdout)
        return json.loads(result.stdout) if result.stdout.strip() else None

    def init(self, **kw):
        return self.call("init", "--task-id", "task-a", data=kw.get("config", self.config), env=kw.get("env"))

    def status(self):
        return self.ok(self.call("status", "--task-id", "task-a"))

    def run_check(self):
        return self.call("run", "--task-id", "task-a", "--check", "unit")

    def prepare(self, gate="final-review"):
        return self.call("prepare-review", "--task-id", "task-a", "--gate", gate,
                         "--package", str(self.bundle))

    def record(self, gate="final-review", attempt=1, verdict=None, reviewer=None):
        return self.call("record-review", "--task-id", "task-a", "--gate", gate,
                         "--attempt", str(attempt), "--verdict",
                         verdict or ("passed" if gate == "final-review" else "survives_challenge"),
                         "--reviewer-id", reviewer or gate + "-reviewer", "--report", str(self.report))

    def review(self, gate="final-review"):
        ticket = self.ok(self.prepare(gate))
        return self.ok(self.record(gate, ticket["attempt"]))

    def hook(self, **changes):
        event = {"hook_event_name": "Stop", "session_id": "session-a", "cwd": str(self.work),
                 "permission_mode": "default", "stop_hook_active": False}
        event.update(changes)
        return self.call("hook", data=event)

    @property
    def state_path(self):
        return self.work / ".engineering/gates/tasks/task-a/state.json"

    def test_resume_rejects_previous_reviewers_without_mutating_state(self):
        self.ok(self.init())
        self.ok(self.run_check())
        self.review()
        self.review("red-team")
        before = self.state_path.read_bytes()
        for reviewer in ("final-review-reviewer", "red-team-reviewer"):
            result = self.init(env=dict(self.env, CODEX_THREAD_ID=reviewer))
            self.assertEqual(result.returncode, 2)
            self.assertIn("session conflicts with an existing reviewer", result.stderr)
            self.assertEqual(self.state_path.read_bytes(), before)
        self.assertTrue(self.status()["ready"])
        self.ok(self.init(env=dict(self.env, CODEX_THREAD_ID="new-controller")))

    def test_default_review_package_normalizes_temp_parent(self):
        self.git("-c", "user.name=Test", "-c", "user.email=test@example.invalid",
                 "-c", "commit.gpgsign=false", "commit", "-qm", "fixture")
        (self.work / "source.py").write_text("value = 2\n")
        self.ok(self.init())
        self.ok(self.run_check())
        alias = self.base / "temp-alias"
        alias.symlink_to(self.base, target_is_directory=True)
        helper = ROOT / "plugins/engineering/skills/requesting-code-review/scripts/review-package"
        result = subprocess.run(["bash", str(helper), "working-tree"], cwd=self.work,
                                env=dict(self.env, TMPDIR=str(alias)), text=True, capture_output=True)
        self.assertEqual(result.returncode, 0, result.stderr)
        package = next(line.removeprefix("Package: ") for line in result.stdout.splitlines() if line.startswith("Package: "))
        self.assertEqual(Path(package), Path(package).resolve())
        self.ok(self.call("prepare-review", "--task-id", "task-a", "--gate", "final-review", "--package", package))

    def test_output_overflow_is_bounded_and_never_passes(self):
        self.config["checks"][0]["argv"] = [sys.executable, "-c", "import os; os.write(1, b'x' * (9 * 1024 * 1024))"]
        self.ok(self.init())
        result = self.run_check()
        self.assertEqual(result.returncode, 1, result.stderr)
        receipt = json.loads(self.state_path.read_text())["checks"]["unit"][-1]
        self.assertEqual(receipt["outcome"], "inconclusive")
        self.assertEqual(receipt["execution"], "incomplete")
        log = self.state_path.parent / next(iter(receipt["files"]))
        self.assertLessEqual(log.stat().st_size, 8 * 1024 * 1024)
        self.assertIn(b"check output exceeded log limit", log.read_bytes())
        self.assertFalse(self.status()["ready"])

    def test_timeout_diagnostic_stays_within_log_limit(self):
        self.config["checks"][0]["argv"] = [sys.executable, "-c",
            "import os,time; os.write(1, b'x' * (8 * 1024 * 1024)); time.sleep(5)"]
        self.ok(self.init())
        result = self.call("run", "--task-id", "task-a", "--check", "unit", "--timeout", "0.5")
        self.assertEqual(result.returncode, 1, result.stderr)
        log = self.state_path.parent / "check-unit-1.log"
        self.assertLessEqual(log.stat().st_size, 8 * 1024 * 1024)
        self.assertIn(b"check timed out before completion", log.read_bytes())

    def test_slow_hook_records_inconclusive_before_host_timeout(self):
        self.ok(self.init())
        self.script.write_text(self.script.read_text().replace("HOOK_SECONDS = 6", "HOOK_SECONDS = 0.2")
                               .replace("def inspect(root, state):", "def inspect(root, state):\n    __import__('time').sleep(1)"))
        before = self.state_path.read_bytes()
        started = time.monotonic()
        result = self.hook()
        self.assertLess(time.monotonic() - started, 3)
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertIn("systemMessage", json.loads(result.stdout))
        observation = json.loads((self.state_path.parent / "observation.json").read_text())
        self.assertEqual(observation["reason"], "time_budget_exceeded")
        self.assertFalse(observation["ready"])
        self.assertEqual(self.state_path.read_bytes(), before)

    def test_hook_budget_interrupts_receipt_hashing(self):
        self.ok(self.init())
        self.ok(self.run_check())
        self.script.write_text(self.script.read_text().replace("HOOK_SECONDS = 6", "HOOK_SECONDS = 0.2")
                               .replace("def file_digest(path):", "def file_digest(path):\n    __import__('time').sleep(1)"))
        # Keep the receipt current after instrumentation changes the runtime digest.
        import importlib.util
        spec = importlib.util.spec_from_file_location("instrumented_gates", self.script)
        module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(module)
        state = json.loads(self.state_path.read_text())
        state["checks"]["unit"][-1]["artifact_digest"] = module.snapshot(self.work, self.config)
        self.state_path.write_text(json.dumps(state))
        result = self.hook()
        self.assertEqual(result.returncode, 0, result.stderr)
        observation = json.loads((self.state_path.parent / "observation.json").read_text())
        self.assertEqual(observation.get("reason"), "time_budget_exceeded")
        self.assertIn("systemMessage", json.loads(result.stdout))

    def test_missing_evidence_is_not_a_pass_and_check_fails(self):
        self.ok(self.init())
        status = self.status()
        self.assertFalse(status["ready"])
        self.assertEqual(status["gates"], {"verification": "not_run", "final-review": "not_run", "red-team": "not_run"})
        self.assertEqual(self.call("check", "--task-id", "task-a").returncode, 1)

    def test_complete_path_requires_all_checks_then_both_reviews(self):
        self.config["checks"].append({"id": "second", "argv": [sys.executable, "-c", "print('second')"]})
        self.ok(self.init())
        self.ok(self.run_check())
        self.assertEqual(self.status()["gates"]["verification"], "not_run")
        self.assertNotEqual(self.prepare().returncode, 0)
        self.ok(self.call("run", "--task-id", "task-a", "--check", "second"))
        self.review()
        self.assertFalse(self.status()["ready"])
        self.review("red-team")
        self.assertTrue(self.status()["ready"])
        self.ok(self.call("check", "--task-id", "task-a"))
        self.ok(self.call("close", "--task-id", "task-a"))
        self.assertEqual(self.hook().stdout, "")

    def test_runner_uses_real_exit_code_and_stops_review_preparation(self):
        self.config["checks"][0]["argv"] = [sys.executable, "-c", "print('not passed');raise SystemExit(7)"]
        self.ok(self.init())
        result = self.run_check()
        self.assertEqual(result.returncode, 1, result.stderr)
        self.assertEqual(self.status()["gates"]["verification"], "failed")
        self.assertIn("dependency", self.prepare().stderr)

    def test_runner_cannot_credit_a_different_inherited_git_worktree(self):
        other = self.base / "other repo"
        other.mkdir()
        subprocess.run(["git", "init", "-q"], cwd=other, env=self.env, check=True)
        self.config["checks"][0]["argv"] = ["git", "diff", "--check"]
        (self.work / "source.py").write_text("value = 1   \n")
        self.ok(self.init())
        env = dict(self.env, GIT_DIR=str(other / ".git"), GIT_WORK_TREE=str(other))
        result = self.call("run", "--task-id", "task-a", "--check", "unit", env=env)
        self.assertEqual(result.returncode, 1, result.stdout + result.stderr)
        self.assertEqual(self.status()["gates"]["verification"], "failed")

    def test_source_edits_invalidate_all_downstream_passes_without_a_commit(self):
        self.ok(self.init())
        self.ok(self.run_check())
        self.review()
        self.review("red-team")
        (self.work / "source.py").write_text("value = 2\n")
        self.assertEqual(set(self.status()["gates"].values()), {"inconclusive"})
        self.assertNotEqual(self.call("close", "--task-id", "task-a").returncode, 0)

    def test_index_only_changes_invalidate_a_now_failing_git_check_and_both_reviews(self):
        self.config["checks"][0]["argv"] = ["git", "diff", "--check"]
        original = self.git("rev-parse", ":source.py")
        (self.work / "source.py").write_text("value = 1  \n")
        self.git("add", "source.py")
        self.ok(self.init())
        self.ok(self.run_check())
        self.review()
        self.review("red-team")
        self.assertTrue(self.status()["ready"])
        self.git("update-index", "--cacheinfo", "100644," + original + ",source.py")
        direct = subprocess.run(["git", "diff", "--check"], cwd=self.work, env=self.env,
                                text=True, capture_output=True)
        self.assertNotEqual(direct.returncode, 0)
        self.assertIn("trailing whitespace", direct.stdout)
        status = self.status()
        self.assertFalse(status["ready"])
        self.assertEqual(set(status["gates"].values()), {"inconclusive"})

    def test_index_flags_that_hide_diff_failures_invalidate_evidence_when_cleared(self):
        self.config["checks"][0]["argv"] = ["git", "diff", "--check"]
        (self.work / "source.py").write_text("value = 1  \n")
        self.ok(self.init())
        for flag in ("assume-unchanged", "skip-worktree"):
            with self.subTest(flag=flag):
                self.git("update-index", "--" + flag, "source.py")
                self.ok(self.run_check())
                self.review()
                self.review("red-team")
                self.assertTrue(self.status()["ready"])
                self.git("update-index", "--no-" + flag, "source.py")
                direct = subprocess.run(["git", "diff", "--check"], cwd=self.work, env=self.env,
                                        text=True, capture_output=True)
                self.assertNotEqual(direct.returncode, 0)
                self.assertIn("trailing whitespace", direct.stdout)
                self.assertFalse(self.status()["ready"])
                self.assertEqual(set(self.status()["gates"].values()), {"inconclusive"})

    def test_resolving_intent_to_add_invalidates_a_now_failing_cached_diff_check(self):
        self.git("-c", "user.name=Fixture", "-c", "user.email=fixture@example.test",
                 "commit", "-qm", "baseline")
        (self.work / "new.py").write_text("")
        self.git("add", "-N", "new.py")
        self.config["checks"][0]["argv"] = ["git", "diff", "--cached", "--exit-code"]
        self.ok(self.init())
        self.ok(self.run_check())
        self.review()
        self.review("red-team")
        self.assertTrue(self.status()["ready"])
        self.git("add", "new.py")
        direct = subprocess.run(["git", "diff", "--cached", "--exit-code"],
                                cwd=self.work, env=self.env, text=True, capture_output=True)
        self.assertEqual(direct.returncode, 1)
        self.assertIn("new file mode", direct.stdout)
        self.assertFalse(self.status()["ready"])
        self.assertEqual(set(self.status()["gates"].values()), {"inconclusive"})

    def test_head_only_changes_invalidate_a_now_failing_head_based_check(self):
        self.git("-c", "user.name=Fixture", "-c", "user.email=fixture@example.test",
                 "commit", "-qm", "clean")
        original = self.git("rev-parse", "HEAD")
        (self.work / "source.py").write_text("value = 1  \n")
        self.git("add", "source.py")
        self.git("-c", "user.name=Fixture", "-c", "user.email=fixture@example.test",
                 "commit", "-qm", "whitespace")
        self.config["checks"][0]["argv"] = ["git", "diff", "--check", "HEAD"]
        self.ok(self.init())
        self.ok(self.run_check())
        self.git("update-ref", "HEAD", original)
        direct = subprocess.run(["git", "diff", "--check", "HEAD"], cwd=self.work, env=self.env,
                                text=True, capture_output=True)
        self.assertNotEqual(direct.returncode, 0)
        self.assertIn("trailing whitespace", direct.stdout)
        self.assertEqual(self.status()["gates"]["verification"], "inconclusive")

    def test_same_source_new_check_receipt_invalidates_dependent_review(self):
        self.ok(self.init())
        self.ok(self.run_check())
        self.review()
        self.review("red-team")
        before = self.status()["artifact_digest"]
        self.ok(self.run_check())
        status = self.status()
        self.assertEqual(before, status["artifact_digest"])
        self.assertEqual(status["gates"]["verification"], "passed")
        self.assertEqual(status["gates"]["final-review"], "inconclusive")
        self.assertEqual(status["gates"]["red-team"], "inconclusive")

    def test_changes_during_a_check_are_inconclusive_even_with_zero_exit(self):
        self.config["checks"][0]["argv"] = [sys.executable, "-c", "from pathlib import Path;Path('source.py').write_text('value = 3\\n')"]
        self.ok(self.init())
        self.assertEqual(self.run_check().returncode, 1)
        self.assertEqual(self.status()["gates"]["verification"], "inconclusive")

    def test_finished_check_is_recorded_when_snapshot_inputs_become_unavailable(self):
        plan = self.work / ".engineering/plan.md"
        original = plan.read_bytes()
        self.config["checks"][0]["argv"] = [sys.executable, "-c", (
            "from pathlib import Path;Path('.engineering/plan.md').unlink();"
            "print('finished');raise SystemExit(7)")]
        self.ok(self.init())
        result = self.run_check()
        self.assertEqual(result.returncode, 2)
        self.assertIn("declared input is missing", result.stderr)
        receipt = json.loads(self.state_path.read_text())["checks"]["unit"][0]
        self.assertEqual(receipt["execution"], "complete")
        self.assertEqual(receipt["exit_code"], 7)
        self.assertEqual(receipt["outcome"], "inconclusive")
        self.assertIn("check-unit-1.log", receipt["files"])
        self.assertIn("finished", (self.state_path.parent / "check-unit-1.log").read_text())
        plan.write_bytes(original)
        self.assertEqual(self.status()["gates"]["verification"], "inconclusive")
        self.config["checks"][0]["argv"] = [sys.executable, "-c", "print('recovered')"]
        self.ok(self.call("revise", "--task-id", "task-a", data=self.config))
        self.ok(self.run_check())
        self.assertEqual(self.status()["checks"]["unit"]["attempts"], 2)

    def test_untracked_files_permissions_and_declared_ignored_inputs_are_fingerprinted(self):
        self.ok(self.init())
        before = self.status()["artifact_digest"]
        (self.work / "new.py").write_text("new = 1\n")
        self.assertNotEqual(before, self.status()["artifact_digest"])
        (self.work / "new.py").unlink()
        self.assertEqual(before, self.status()["artifact_digest"])
        (self.work / "source.py").chmod(0o755)
        self.assertNotEqual(before, self.status()["artifact_digest"])
        (self.work / "source.py").chmod(0o644)
        (self.work / "ignored.txt").write_text("ignored\n")
        self.assertEqual(before, self.status()["artifact_digest"])
        (self.work / ".engineering/plan.md").write_text("Changed requirements.\n")
        self.assertNotEqual(before, self.status()["artifact_digest"])

    def test_runtime_change_invalidates_evidence(self):
        self.ok(self.init())
        self.ok(self.run_check())
        with self.script.open("a") as out:
            out.write("\n# policy revision\n")
        self.assertEqual(self.status()["gates"]["verification"], "inconclusive")

    def test_policy_change_invalidates_evidence(self):
        self.ok(self.init())
        self.ok(self.run_check())
        self.policy.write_text("Updated gate policy.\n")
        self.assertEqual(self.status()["gates"]["verification"], "inconclusive")

    def test_correcting_check_configuration_preserves_history_and_budget(self):
        self.config["checks"][0]["argv"] = ["/no-such-engineering-check"]
        self.ok(self.init())
        self.assertEqual(self.run_check().returncode, 1)
        status = self.status()
        self.assertEqual(status["gates"]["verification"], "blocked")
        self.assertEqual(status["checks"]["unit"].get("execution"), "incomplete")
        previous = json.loads(self.state_path.read_text())["checks"]["unit"][0]
        self.config["checks"][0]["argv"] = [sys.executable, "-c", "print('corrected')"]
        self.ok(self.call("revise", "--task-id", "task-a", data=self.config))
        self.assertEqual(self.status()["gates"]["verification"], "inconclusive")
        self.ok(self.run_check())
        state = json.loads(self.state_path.read_text())
        self.assertEqual(state["checks"]["unit"][0], previous)
        self.assertEqual(state["config_history"][0]["checks"][0]["argv"], ["/no-such-engineering-check"])
        self.assertEqual(self.status()["checks"]["unit"]["attempts"], 2)

    def test_timeout_is_incomplete_and_consumes_an_attempt(self):
        self.config["checks"][0]["argv"] = [sys.executable, "-c", "import time;time.sleep(10)"]
        self.ok(self.init())
        result = self.call("run", "--task-id", "task-a", "--check", "unit", "--timeout", "0.05")
        self.assertEqual(result.returncode, 1, result.stderr)
        status = self.status()
        self.assertEqual(status["gates"]["verification"], "inconclusive")
        self.assertEqual(status["checks"]["unit"].get("execution"), "incomplete")
        self.assertEqual(status["checks"]["unit"]["attempts"], 1)

    def test_review_needs_reservation_and_cannot_replay_or_stamp_stale_input(self):
        self.ok(self.init())
        self.ok(self.run_check())
        self.assertNotEqual(self.record().returncode, 0)
        self.ok(self.prepare())
        before = self.state_path.read_bytes()
        (self.work / "source.py").write_text("value = 4\n")
        self.assertIn("stale", self.record().stderr)
        self.assertEqual(before, self.state_path.read_bytes())
        (self.work / "source.py").write_text("value = 1\n")
        self.ok(self.record())
        self.assertIn("pending", self.record().stderr)

    def test_review_copies_input_and_report_and_tracks_tampered_evidence(self):
        self.ok(self.init())
        self.ok(self.run_check())
        ticket = self.ok(self.prepare())
        self.bundle.write_text("Changed outside input after preparation.\n")
        self.ok(self.record())
        self.report.unlink()
        self.assertEqual(self.status()["gates"]["final-review"], "passed")
        frozen = Path(ticket["package"])
        self.assertIn("Immutable review input", frozen.read_text())
        frozen.write_text("Tampered\n")
        self.assertEqual(self.status()["gates"]["final-review"], "inconclusive")

    def test_review_verdicts_and_reviewer_identity_are_stage_specific(self):
        self.ok(self.init())
        self.ok(self.run_check())
        self.ok(self.prepare())
        self.assertNotEqual(self.record(reviewer="session-a").returncode, 0)
        self.assertNotEqual(self.record(verdict="survives_challenge").returncode, 0)
        self.ok(self.record())
        self.ok(self.prepare("red-team"))
        self.assertNotEqual(self.record("red-team", reviewer="final-review-reviewer").returncode, 0)
        self.ok(self.record("red-team", verdict="inconclusive"))
        self.assertFalse(self.status()["ready"])

    def test_resume_keeps_attempts_and_budget(self):
        self.ok(self.init())
        for i in range(5):
            self.ok(self.run_check())
            env = dict(self.env, CODEX_THREAD_ID="resumed-" + str(i))
            self.ok(self.init(env=env))
        self.assertEqual(self.status()["checks"]["unit"]["attempts"], 5)
        self.assertIn("budget", self.run_check().stderr)

    def test_abandon_does_not_refund_or_allow_late_results(self):
        self.ok(self.init())
        self.ok(self.run_check())
        self.ok(self.prepare())
        self.ok(self.call("abandon", "--task-id", "task-a", "--gate", "final-review", "--attempt", "1"))
        self.assertIn("pending", self.record().stderr)
        self.assertEqual(self.ok(self.prepare())["attempt"], 2)

    def test_concurrent_review_reservations_have_one_owner(self):
        self.ok(self.init())
        self.ok(self.run_check())
        with concurrent.futures.ThreadPoolExecutor(max_workers=2) as pool:
            results = list(pool.map(lambda _: self.prepare(), range(2)))
        self.assertEqual(sum(r.returncode == 0 for r in results), 1)
        self.assertEqual(self.status()["attempts"]["final-review"], 1)

    def test_completed_check_waits_for_the_writer_lock_without_losing_its_receipt(self):
        self.config["checks"][0]["argv"] = [sys.executable, "-c", (
            "from pathlib import Path; import time; "
            "Path('.engineering/started').touch(); "
            "exec(\"while not Path('.engineering/go').exists(): time.sleep(0.01)\"); "
            "print('verified', flush=True)")]
        self.ok(self.init())
        process = subprocess.Popen([sys.executable, str(self.script), "run", "--task-id", "task-a",
                                    "--check", "unit"], cwd=self.work, env=self.env,
                                   text=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        try:
            deadline = time.monotonic() + 5
            while not (self.work / ".engineering/started").exists() and time.monotonic() < deadline:
                time.sleep(0.01)
            self.assertTrue((self.work / ".engineering/started").exists())
            with (self.work / ".engineering/gates/.lock").open("a+b") as stream:
                fcntl.flock(stream, fcntl.LOCK_EX)
                (self.work / ".engineering/go").touch()
                log = self.state_path.parent / "check-unit-1.log"
                deadline = time.monotonic() + 5
                while "verified" not in log.read_text() and time.monotonic() < deadline:
                    time.sleep(0.01)
                self.assertIn("verified", log.read_text())
                time.sleep(0.2)
                self.assertIsNone(process.poll(), "completed check must wait to save its receipt")
            stdout, stderr = process.communicate(timeout=5)
            self.assertEqual(process.returncode, 0, stderr + stdout)
            self.assertEqual(json.loads(stdout)["gates"]["verification"], "passed")
            receipt = json.loads(self.state_path.read_text())["checks"]["unit"][0]
            self.assertEqual(receipt["exit_code"], 0)
            self.assertEqual(receipt["execution"], "complete")
            self.assertEqual(self.status()["checks"]["unit"]["attempts"], 1)
        finally:
            if process.poll() is None:
                process.kill()
            process.communicate(timeout=5)

    def test_hook_is_silent_outside_git_but_diagnoses_a_broken_repository(self):
        outside = self.base / "non-git"
        outside.mkdir()
        result = self.hook(cwd=str(outside))
        self.assertEqual((result.returncode, result.stdout, result.stderr), (0, "", ""))
        self.assertEqual(list(outside.iterdir()), [])
        (outside / ".git").write_text("broken repository pointer\n")
        self.assertIn("observation unavailable", self.hook(cwd=str(outside)).stderr)

    def test_hook_is_inert_without_registration_and_ignores_other_sessions_children_and_plan_mode(self):
        before = sorted(str(p.relative_to(self.work)) for p in self.work.rglob("*"))
        self.assertEqual(self.hook().stdout, "")
        self.assertEqual(before, sorted(str(p.relative_to(self.work)) for p in self.work.rglob("*")))
        self.ok(self.init())
        for changes in ({"session_id": "other"}, {"agent_id": "child"},
                        {"parent_session_id": "parent"}, {"permission_mode": "plan"},
                        {"hook_event_name": "PreToolUse"}):
            self.assertEqual(self.hook(**changes).stdout, "", changes)
        self.assertFalse((self.state_path.parent / "observation.json").exists())

    def test_hook_records_only_observations_never_blocks_and_suppresses_duplicates(self):
        self.ok(self.init())
        before = self.state_path.read_bytes()
        output = self.ok(self.hook())
        self.assertEqual(set(output), {"systemMessage"})
        self.assertTrue((self.state_path.parent / "observation.json").is_file())
        self.assertEqual(before, self.state_path.read_bytes())
        self.assertEqual(self.hook().stdout, "")
        self.assertEqual(self.status()["checks"]["unit"]["attempts"], 0)

    def test_generated_stop_command_runs_with_either_host_plugin_root(self):
        self.ok(self.init())
        hooks = json.loads((ROOT / "plugins/engineering/hooks/hooks.json").read_text())["hooks"]
        self.assertIn("Stop", hooks, "Engineering must package the observation hook")
        command = hooks["Stop"][0]["hooks"][0]["command"]
        event = {"hook_event_name": "Stop", "session_id": "session-a", "cwd": str(self.work)}
        for variable in ("PLUGIN_ROOT", "CLAUDE_PLUGIN_ROOT"):
            env = self.env.copy()
            env.pop("PLUGIN_ROOT", None)
            env.pop("CLAUDE_PLUGIN_ROOT", None)
            env[variable] = str(self.package)
            observation = self.state_path.parent / "observation.json"
            if observation.exists():
                observation.unlink()
            result = subprocess.run(command, shell=True, cwd=self.work, env=env,
                                    input=json.dumps(event), text=True, capture_output=True, timeout=15)
            self.assertEqual(set(self.ok(result)), {"systemMessage"})
            self.assertTrue(observation.is_file())

    def test_unsupported_and_broken_receipts_never_become_ready(self):
        self.ok(self.init())
        self.ok(self.run_check())
        self.review()
        self.review("red-team")
        original = self.state_path.read_text()
        for mutation in (lambda s: s["reviews"].pop("red-team"),
                         lambda s: s["checks"]["unit"][0].update(exit_code=4),
                         lambda s: s["reviews"]["final-review"][0].update(files={}),
                         lambda s: s.update(workspace_root=str(self.base))):
            state = json.loads(original)
            mutation(state)
            self.state_path.write_text(json.dumps(state))
            self.assertNotEqual(self.call("check", "--task-id", "task-a").returncode, 0)
        self.state_path.write_text(original)

    def test_check_receipt_output_changes_are_detected(self):
        self.ok(self.init())
        self.ok(self.run_check())
        log = self.state_path.parent / "check-unit-1.log"
        self.assertIn("verified", log.read_text())
        log.write_text("replaced output\n")
        self.assertEqual(self.status()["gates"]["verification"], "inconclusive")

    def test_status_is_read_only_and_invalid_inputs_do_not_replace_state(self):
        self.ok(self.init())
        before = self.state_path.read_bytes()
        self.status()
        self.assertEqual(before, self.state_path.read_bytes())
        for config in ({"inputs": [], "checks": []},
                       dict(self.config, unknown=True),
                       dict(self.config, inputs=["../outside"]),
                       dict(self.config, checks=[self.config["checks"][0]] * 2)):
            self.assertNotEqual(self.init(config=config).returncode, 0)
            self.assertEqual(before, self.state_path.read_bytes())

    def test_symlink_state_is_rejected_without_writing_through_it(self):
        outside = self.base / "outside"
        outside.mkdir()
        (self.work / ".engineering/gates").symlink_to(outside, target_is_directory=True)
        self.assertNotEqual(self.init().returncode, 0)
        self.assertEqual(list(outside.iterdir()), [])

    def test_declared_inputs_reject_dangling_and_directory_symlinks(self):
        plan = self.work / ".engineering/plan.md"
        for target in (self.work / "absent.md", self.work / ".engineering"):
            with self.subTest(target=target.name):
                plan.unlink()
                plan.symlink_to(target, target_is_directory=target.is_dir())
                result = self.init()
                self.assertEqual(result.returncode, 2)
                self.assertIn("declared input", result.stderr)
                self.assertFalse((self.work / ".engineering/gates").exists())

    def test_corrupt_state_observation_fails_open_without_repair(self):
        self.ok(self.init())
        self.state_path.write_text('{"schema_version":999}')
        before = self.state_path.read_bytes()
        result = self.hook()
        self.assertEqual(result.returncode, 0)
        self.assertEqual(result.stdout, "")
        self.assertIn("observation unavailable", result.stderr)
        self.assertEqual(before, self.state_path.read_bytes())

    def test_close_requires_completion_but_superseding_keeps_evidence(self):
        self.ok(self.init())
        self.ok(self.run_check())
        self.assertNotEqual(self.call("close", "--task-id", "task-a").returncode, 0)
        self.ok(self.call("close", "--task-id", "task-a", "--outcome", "superseded"))
        self.assertEqual(self.hook().stdout, "")
        self.ok(self.init())
        self.assertEqual(self.status()["checks"]["unit"]["attempts"], 1)


if __name__ == "__main__":
    unittest.main()
