"""Regression tests use a local fake executable; no Codex/model calls."""

import json
import os
from pathlib import Path
import sys
import tempfile
import time
import unittest
from unittest import mock

import controlled_benchmark
import runner


class BoundedExecutionTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name).resolve()
        self.workspace = self.root / "workspace"
        self.workspace.mkdir()
        (self.workspace / ".agents").mkdir()
        (self.workspace / ".agents/check.sh").write_text("echo fixture\n")
        (self.workspace / ".agents/check.sh").chmod(0o644)
        self.case = {"id": "fixture", "profile": "engineering", "prompt": "review fixture"}
        runner._write_json(self.workspace / ".eval-input.json", self.case)
        self.executable = self.root / "fake-codex"
        self.manifest = {
            "artifact_dir": str(self.root), "manifest_id": "manifest", "node_runtime": {},
            "codex_binary": str(self.executable),
            "candidate_profiles": {"engineering": {"sha256": runner._tree_sha(self.workspace / ".agents")}},
        }
        self.run = {
            "run_id": "fixture--fake", "case_id": "fixture", "cohort_id": "fake", "repetition": 1,
            "workspace": str(self.workspace), "model": "fake", "effort": "high",
            "reviewer_count": 1, "sandbox": "read-only",
            "workspace_initial_sha256": runner._tree_sha(self.workspace, excluded=(".git",)),
            "public_input_sha256": runner._sha_bytes(runner.encoded_json(self.case).encode()),
        }
        self.addCleanup(mock.patch.stopall)
        mock.patch.object(runner, "_isolated_environment", return_value=dict(os.environ)).start()
        # Patch policy values only; real pipe I/O, subprocess cleanup, parsing and
        # result readback remain in use. create=True lets missing bounds fail RED.
        for name, value in {
            "MAX_STDOUT_BYTES": 4096, "MAX_STDERR_BYTES": 1024,
            "MAX_TRACE_LINE_BYTES": 512, "MAX_TRACE_LINES": 10,
        }.items():
            mock.patch.object(runner, name, value, create=True).start()

    def _write_executable(self, body):
        self.executable.write_text(
            f"#!{sys.executable}\nimport os, sys, time\nfrom pathlib import Path\n"
            "output = Path(sys.argv[sys.argv.index('--output-last-message') + 1])\n"
            "output.write_text('fixture final\\n')\n" + body + "\n"
        )
        self.executable.chmod(0o755)

    def _execute(self, entrypoint, body, timeout=2):
        self._write_executable(body)
        if entrypoint == "native":
            value = runner.execute_run(self.manifest, self.run, self.case, timeout)
            loaded = runner._validate_result(self.manifest, self.run, self.case)
        else:
            call_root = self.root / "controlled-call"
            value = controlled_benchmark._execute_call(
                self.manifest, call_root, self.workspace, "fake", "high", self.case["prompt"],
                "fixed-adjudicator", timeout, "plan", self.run["run_id"], "adjudicator", 1,
            )
            loaded = controlled_benchmark._load_call(
                self.manifest, {"plan_id": "plan"}, self.run, call_root, self.workspace,
                "adjudicator", "fixed-adjudicator", "fake", "high", self.case["prompt"],
            )
        self.assertEqual(loaded, value)
        return value

    def _assert_limited(self, entrypoint, body, expected_error):
        value = self._execute(entrypoint, body)
        self.assertLessEqual(Path(value["artifacts"]["trace"]).stat().st_size, 4096)
        self.assertLessEqual(Path(value["artifacts"]["stderr"]).stat().st_size, 1024)
        self.assertEqual(value["status"], "inconclusive")
        self.assertTrue(any(expected_error in error for error in value["trace_errors"]), value)
        if entrypoint == "native":
            self.assertEqual(value["execution_status"], "incomplete")
            self.assertEqual(value["semantic_adjudication"], "not_run")
        # A partial trace containing turn.completed cannot be promoted on readback.
        result_path = Path(value["artifacts"]["trace"]).parent / (
            "result.json" if entrypoint == "native" else "call.json"
        )
        changed = dict(value)
        if entrypoint == "native":
            changed["execution_status"] = "complete"
        else:
            changed["status"] = "complete"
        runner._write_json(result_path, changed)
        with self.assertRaises(runner.EvaluationError):
            if entrypoint == "native":
                runner._validate_result(self.manifest, self.run, self.case)
            else:
                controlled_benchmark._load_call(
                    self.manifest, {"plan_id": "plan"}, self.run, result_path.parent, self.workspace,
                    "adjudicator", "fixed-adjudicator", "fake", "high", self.case["prompt"],
                )

    def test_native_stdout_overflow_is_bounded_and_inconclusive(self):
        self._assert_limited("native", "os.write(1, b'{\"type\":\"turn.completed\"}\\n' + b' ' * 8192)", "stdout byte limit")

    def test_controlled_stdout_overflow_is_bounded_and_inconclusive(self):
        self._assert_limited("controlled", "os.write(1, b'{\"type\":\"turn.completed\"}\\n' + b' ' * 8192)", "stdout byte limit")

    def test_native_stderr_overflow_is_bounded_and_inconclusive(self):
        self._assert_limited("native", "os.write(1, b'{\"type\":\"turn.completed\"}\\n')\nos.write(2, b'e' * 8192)", "stderr byte limit")

    def test_controlled_stderr_overflow_is_bounded_and_inconclusive(self):
        self._assert_limited("controlled", "os.write(1, b'{\"type\":\"turn.completed\"}\\n')\nos.write(2, b'e' * 8192)", "stderr byte limit")

    def test_native_huge_json_line_is_inconclusive(self):
        self._assert_limited("native", "os.write(1, b'{\"type\":\"turn.completed\",\"padding\":\"' + b'x' * 2000 + b'\"}\\n')", "trace line byte limit")

    def test_controlled_huge_json_line_is_inconclusive(self):
        self._assert_limited("controlled", "os.write(1, b'{\"type\":\"turn.completed\",\"padding\":\"' + b'x' * 2000 + b'\"}\\n')", "trace line byte limit")

    def test_native_excessive_event_count_is_inconclusive(self):
        self._assert_limited("native", "os.write(1, b'{\"type\":\"turn.completed\"}\\n' + b'{}\\n' * 20)", "trace line count limit")

    def test_controlled_excessive_event_count_is_inconclusive(self):
        self._assert_limited("controlled", "os.write(1, b'{\"type\":\"turn.completed\"}\\n' + b'{}\\n' * 20)", "trace line count limit")

    def test_noisy_native_timeout_keeps_bounded_evidence(self):
        self._assert_timeout("native")

    def test_noisy_controlled_timeout_keeps_bounded_evidence(self):
        self._assert_timeout("controlled")

    def _assert_timeout(self, entrypoint):
        started = time.monotonic()
        value = self._execute(entrypoint, "while True:\n    os.write(1, b'{}\\n')\n    time.sleep(0.2)", timeout=1)
        self.assertLess(time.monotonic() - started, 3)
        self.assertTrue(value["timed_out"])
        self.assertIn(value["status"], {"not_run", "inconclusive"})
        self.assertGreater(Path(value["artifacts"]["trace"]).stat().st_size, 0)

    def test_successful_trace_remains_available(self):
        for entrypoint in ("native", "controlled"):
            with self.subTest(entrypoint=entrypoint):
                value = self._execute(entrypoint, "assert sys.stdin.read() == 'review fixture'\nos.write(1, b'{\"type\":\"turn.completed\"}\\n')")
                self.assertEqual(value["trace_errors"], [])
                self.assertEqual(value["status"], "inconclusive" if entrypoint == "native" else "complete")

    def test_large_stdin_is_delivered_completely_for_both_entrypoints(self):
        self.case["prompt"] = "fixture-" * 32768
        runner._write_json(self.workspace / ".eval-input.json", self.case)
        self.run["public_input_sha256"] = runner._sha_bytes(runner.encoded_json(self.case).encode())
        self.run["workspace_initial_sha256"] = runner._tree_sha(self.workspace, excluded=(".git",))
        for entrypoint in ("native", "controlled"):
            with self.subTest(entrypoint=entrypoint):
                value = self._execute(entrypoint,
                    "os.write(1, b'{}\\n')\nassert sys.stdin.read() == 'fixture-' * 32768\n"
                    "os.write(1, b'{\"type\":\"turn.completed\"}\\n')")
                self.assertEqual(value["returncode"], 0)
                self.assertFalse(value["timed_out"])
                self.assertEqual(value["trace_errors"], [])

    def test_deep_valid_json_observation_does_not_depend_on_python_recursion_budget(self):
        # Valid JSON can be decoded with more recursion headroom than the later
        # observer has. Traversal must preserve a deep leaf without recursion.
        original_limit = sys.getrecursionlimit()
        try:
            sys.setrecursionlimit(5000)
            event = json.loads('{"type":"item.completed","item":' + '[' * 1500
                               + '{"tool":"wait_agent"}' + ']' * 1500 + '}')
        finally:
            sys.setrecursionlimit(original_limit)
        observations = runner._trace_observations([event])
        self.assertEqual(observations["collaboration_tools"], ["wait_agent"])

    def test_execute_bit_changes_invalidate_fixed_candidate(self):
        self.assertTrue(runner._fixed_inputs_intact(self.manifest, self.run, self.case))
        (self.workspace / ".agents/check.sh").chmod(0o755)
        self.assertFalse(runner._fixed_inputs_intact(self.manifest, self.run, self.case))

    def test_execute_bit_changes_invalidate_preexecution_workspace(self):
        (self.workspace / ".agents/check.sh").chmod(0o755)
        self._write_executable("pass")
        with self.assertRaisesRegex(runner.EvaluationError, "workspace changed before execution"):
            runner.execute_run(self.manifest, self.run, self.case, 2)

    def test_execute_bit_changes_invalidate_result_workspace(self):
        self._execute("native", "os.write(1, b'{\"type\":\"turn.completed\"}\\n')")
        (self.workspace / ".agents/check.sh").chmod(0o755)
        with self.assertRaisesRegex(runner.EvaluationError, "final workspace digest mismatch"):
            runner._validate_result(self.manifest, self.run, self.case)


class ControlledTemplateTests(unittest.TestCase):
    def test_unavailable_execution_template_roundtrips_without_semantic_failure(self):
        rows = [{"run_id": status, "adjudicator_status": status, "worker_statuses": ["complete"]}
                for status in ("fail", "not_run", "inconclusive", "complete")]
        plan = {"plan_id": "plan", "runs": [{"run_id": row["run_id"]} for row in rows]}
        value = {"plan_id": "plan", "runs": rows}
        with tempfile.TemporaryDirectory() as directory:
            destination = Path(directory) / "adjudication.json"
            with mock.patch.object(controlled_benchmark, "_load_plan", return_value=({}, {}, plan)), \
                    mock.patch.object(controlled_benchmark, "summary", return_value=value), \
                    mock.patch.object(runner, "_require_not_model_visible", side_effect=lambda _, path: path):
                template = controlled_benchmark.make_adjudication_template(Path(directory), destination)
            controlled_benchmark._load_controlled_adjudication(plan, destination, {"complete"})
            verdicts = {row["run_id"]: row["verdict"] for row in template["runs"]}
            self.assertEqual(verdicts, {"fail": "inconclusive", "not_run": "not_run", "inconclusive": "inconclusive", "complete": "inconclusive"})
            self.assertEqual(rows[0]["adjudicator_status"], "fail")


if __name__ == "__main__":
    unittest.main()
