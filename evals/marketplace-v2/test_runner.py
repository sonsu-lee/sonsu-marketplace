import json
import os
from pathlib import Path
import subprocess
import tempfile
from concurrent.futures import ThreadPoolExecutor
import threading
import unittest
from unittest import mock

import runner
import controlled_benchmark


class MarketplaceV2RunnerTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.temp = tempfile.TemporaryDirectory()
        cls.output = Path(cls.temp.name) / "artifact"
        cls.manifest = runner.prepare(cls.output, runner.REPO_ROOT, runner.DEFAULT_CODEX)
        cls.plan = controlled_benchmark.prepare(cls.output)

    @classmethod
    def tearDownClass(cls):
        cls.temp.cleanup()

    def test_sources_define_two_fixtures_and_one_three_repeat_benchmark(self):
        source = runner.validate_sources()
        self.assertEqual(set(source["cases"]["fixtures"]), {"review-service", "workflow-pack"})
        matrix = runner._run_matrix(source["cases"], source["cohorts"])
        benchmark = [run for run in matrix if run["case_id"] == "review-benchmark"]
        self.assertEqual(len(benchmark), 12)
        self.assertEqual({run["cohort_id"] for run in benchmark}, {
            "luna-xhigh-1", "luna-xhigh-5", "sol-xhigh-1", "sol-max-1"
        })
        self.assertEqual({run["repetition"] for run in benchmark}, {1, 2, 3})

    def test_public_case_never_exposes_expected_oracle(self):
        case = runner._read_json(runner.CASES_PATH)["cases"][0]
        public = runner._public_case(case)
        self.assertNotIn("expected", public)
        self.assertNotIn("evaluation_control", public)
        self.assertNotIn("external-payload-cast", json.dumps(public))
        self.assertIn("prompt", public)

    def test_preflight_accepts_only_bare_or_matching_profile_skill_names(self):
        required = ["review-quality", "test-driven-development"]
        self.assertEqual(runner._missing_required_skills(
            "engineering", required, ["review-quality", "test-driven-development"]
        ), [])
        self.assertEqual(runner._missing_required_skills(
            "engineering", required, ["engineering:review-quality", "engineering:test-driven-development"]
        ), [])
        self.assertEqual(runner._missing_required_skills(
            "engineering", required, ["unrelated:review-quality", "engineering:test-driven-development"]
        ), ["review-quality"])

    def test_trace_observation_does_not_invent_model_or_effort(self):
        events = [
            {"type": "thread.started", "thread_id": "thread-1"},
            {"type": "item.completed", "item": {
                "type": "command_execution",
                "command": "sed -n '1,80p' .agents/skills/review-quality/SKILL.md",
            }},
            {"type": "item.completed", "item": {
                "type": "collab_tool_call", "tool": "spawn_agent",
                "receiver_thread_ids": ["agent-1"],
                "agents_states": {"agent-1": {"status": "pending_init"}},
            }},
            {"type": "item.completed", "item": {
                "type": "collab_tool_call", "tool": "wait",
                "receiver_thread_ids": ["agent-1"],
                "agents_states": {"agent-1": {"status": "completed", "message": "review result"}},
            }},
            {"type": "turn.completed", "usage": {"input_tokens": 10, "output_tokens": 2}},
        ]
        observed = runner._trace_observations(events)
        self.assertTrue(observed["turn_completed"])
        self.assertEqual(observed["spawn_agent_count"], 1)
        self.assertEqual(observed["spawn_agent_attempt_count"], 1)
        self.assertEqual(observed["spawn_agent_receiver_ids"], ["agent-1"])
        self.assertEqual(observed["completed_agent_ids"], ["agent-1"])
        self.assertEqual(observed["matching_completed_agent_ids"], ["agent-1"])
        self.assertEqual(observed["matching_completed_agent_ids_with_message"], ["agent-1"])
        self.assertEqual(observed["skill_reads"], ["review-quality"])
        self.assertEqual(observed["observed_model"], "unknown")
        self.assertEqual(observed["observed_effort"], "unknown")
        collaboration = runner._trace_observations([
            {"type": "item.completed", "item": {"type": "function_call", "name": "collaboration.wait_agent"}},
            {"type": "turn.completed", "usage": {}},
        ])
        self.assertEqual(collaboration["collaboration_tools"], ["wait_agent"])

    def test_trace_distinguishes_failed_spawn_attempts_from_completed_reviewers(self):
        observed = runner._trace_observations([
            {"type": "item.completed", "item": {
                "type": "collab_tool_call", "tool": "spawn_agent",
                "receiver_thread_ids": [], "agents_states": {},
            }},
            {"type": "item.completed", "item": {
                "type": "collab_tool_call", "tool": "spawn_agent",
                "receiver_thread_ids": ["agent-1"],
                "agents_states": {"agent-1": {"status": "pending_init"}},
            }},
            {"type": "item.completed", "item": {
                "type": "collab_tool_call", "tool": "wait",
                "receiver_thread_ids": [], "agents_states": {},
            }},
            {"type": "item.completed", "item": {
                "type": "collab_tool_call", "tool": "wait",
                "receiver_thread_ids": ["agent-1"],
                "agents_states": {"agent-1": {"status": "completed"}},
            }},
        ])
        self.assertEqual(observed["spawn_agent_attempt_count"], 2)
        self.assertEqual(observed["spawn_agent_count"], 1)
        self.assertEqual(observed["spawn_agent_receiver_ids"], ["agent-1"])
        self.assertEqual(observed["matching_completed_agent_ids"], ["agent-1"])
        self.assertEqual(observed["collaboration_tools"], ["spawn_agent", "spawn_agent", "wait", "wait"])

    def test_completed_agent_without_message_is_not_semantic_completion_evidence(self):
        observed = runner._trace_observations([
            {"type": "item.completed", "item": {
                "type": "collab_tool_call", "tool": "spawn_agent",
                "receiver_thread_ids": ["agent-1"],
                "agents_states": {"agent-1": {"status": "pending_init", "message": None}},
            }},
            {"type": "item.completed", "item": {
                "type": "collab_tool_call", "tool": "wait",
                "receiver_thread_ids": ["agent-1"],
                "agents_states": {"agent-1": {"status": "completed", "message": "   "}},
            }},
        ])
        self.assertEqual(observed["matching_completed_agent_ids"], ["agent-1"])
        self.assertEqual(observed["completed_agent_ids_with_message"], [])
        self.assertEqual(observed["matching_completed_agent_ids_with_message"], [])

    def test_natural_runner_declares_root_role_and_uses_fixed_agent_capacity(self):
        instructions = runner._developer_instructions()
        self.assertIn("root coordinator", instructions)
        self.assertIn("Repository-local subagents required by applicable skills are allowed", instructions)
        self.assertIn("contact external people or external services", instructions)
        for run in (self.manifest["runs"][13], self.manifest["runs"][14]):
            command = runner._command(self.manifest, run, Path(run["workspace"]) / "final.md")
            self.assertIn("agents.max_concurrent_threads_per_session=5", command)

    def test_staged_profile_supports_continuity_and_gate_state_with_read_only_preconfigured_excludes(self):
        with tempfile.TemporaryDirectory() as directory:
            workspace = Path(directory) / "workspace"
            workspace.mkdir()
            workspace = workspace.resolve()
            (workspace / "CONTRACT.md").write_text("# Contract\n", encoding="utf-8")
            runner._copy_candidate_profile(runner.REPO_ROOT / "plugins/engineering", workspace / ".agents")
            runner._initialize_fixture_git(workspace)

            self.assertTrue((workspace / ".agents/.codex-plugin/plugin.json").is_file())
            self.assertTrue((workspace / ".agents/hooks/hooks.json").is_file())
            exclude = workspace / ".git/info/exclude"
            original = exclude.read_bytes()
            self.assertIn(b"/.engineering/gates/", original.splitlines())
            self.assertIn(b"/.sonsu/continuity/", original.splitlines())
            exclude.chmod(0o444)

            summary = {
                "goal": "exercise staged continuity",
                "scope": "temporary fixture",
                "progress": "profile staged",
                "next_action": "finish regression",
            }
            continuity = subprocess.run([
                "python3", ".agents/scripts/task-continuity.py", "write",
                "--cwd", str(workspace), "--session-id", "staged-session", "--mode", "write",
                "--task-id", "staged-task", "--expected-revision", "0",
                "--skill", "test-driven-development",
            ], cwd=workspace, input=json.dumps(summary), text=True, capture_output=True, check=False)
            self.assertEqual(continuity.returncode, 0, continuity.stderr)

            gate_config = {
                "schema_version": 2,
                "contracts": ["CONTRACT.md"],
                "units": [{
                    "id": "implementation", "stage": "implementation", "needs": [],
                    "artifact": {"kind": "workspace", "path": str(workspace)},
                    "checks": [{"id": "test", "argv": ["python3", "-c", "pass"]}],
                    "review": "independent",
                }],
            }
            gate = subprocess.run([
                "python3", ".agents/scripts/evidence-gates.py", "init",
                "--task-id", "staged-task", "--session-id", "staged-session",
            ], cwd=workspace, input=json.dumps(gate_config), text=True, capture_output=True, check=False)
            self.assertEqual(gate.returncode, 0, gate.stderr)
            self.assertEqual(exclude.read_bytes(), original)

    def test_manifest_binds_bundled_node_runtime_and_isolated_path(self):
        runtime = self.manifest["node_runtime"]
        self.assertEqual(set(runtime), runner.NODE_RUNTIME_FIELDS)
        self.assertTrue(Path(runtime["node_binary"]).is_file())
        self.assertTrue(Path(runtime["npm_binary"]).is_file())
        run_root = Path(self.temp.name) / "runtime-env"
        with mock.patch.dict(os.environ, {
            "NODE_OPTIONS": "--require=/outside/bootstrap.js",
            "NPM_CONFIG_USERCONFIG": "/outside/user.npmrc",
            "NPM_CONFIG_GLOBALCONFIG": "/outside/global.npmrc",
        }):
            env = runner._isolated_environment(run_root, runtime)
        self.assertEqual(env["PATH"].split(":", 1)[0], runtime["bin_dir"])
        self.assertNotIn("NODE_OPTIONS", env)
        self.assertEqual(env["NPM_CONFIG_USERCONFIG"], str(run_root / "home/user.npmrc"))
        self.assertEqual(env["NPM_CONFIG_GLOBALCONFIG"], str(run_root / "home/global.npmrc"))
        changed = json.loads(json.dumps(self.manifest))
        changed["node_runtime"]["node_sha256"] = "0" * 64
        changed["manifest_id"] = runner._sha_bytes(
            runner.encoded_json(runner._without_key(changed, "manifest_id")).encode("utf-8")
        )
        with self.assertRaises(runner.EvaluationError):
            runner._validate_manifest_structure(changed, self.output.resolve())

    def test_runtime_version_probe_uses_temporary_isolated_npm_configuration(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            codex = root / "Resources/codex"
            binary_dir = root / "Resources/cua_node/bin"
            binary_dir.mkdir(parents=True)
            codex.write_text("fixture", encoding="utf-8")
            capture = root / "probe.json"
            script = """#!/usr/bin/env python3
import json, os
from pathlib import Path
Path(%r).write_text(json.dumps({
    'cwd': os.getcwd(), 'home': os.environ.get('HOME'),
    'xdg': os.environ.get('XDG_CONFIG_HOME'),
    'userconfig': os.environ.get('NPM_CONFIG_USERCONFIG'),
    'globalconfig': os.environ.get('NPM_CONFIG_GLOBALCONFIG'),
    'cache': os.environ.get('NPM_CONFIG_CACHE'), 'logs': os.environ.get('NPM_CONFIG_LOGS_DIR'),
    'node_options': os.environ.get('NODE_OPTIONS'),
}))
print('v-test')
""" % str(capture)
            for name in ("node", "npm"):
                path = binary_dir / name
                path.write_text(script, encoding="utf-8")
                path.chmod(0o700)
            with mock.patch.dict(os.environ, {
                "NODE_OPTIONS": "--require=/outside/bootstrap.js",
                "NPM_CONFIG_USERCONFIG": "/outside/user.npmrc",
                "NPM_CONFIG_GLOBALCONFIG": "/outside/global.npmrc",
            }):
                record = runner._node_runtime_record(codex)
            observed = json.loads(capture.read_text(encoding="utf-8"))
            self.assertEqual(Path(observed["cwd"]).resolve(), Path(observed["home"]).resolve())
            self.assertEqual(observed["xdg"], str(Path(observed["home"]) / ".config"))
            self.assertEqual(observed["userconfig"], str(Path(observed["home"]) / "user.npmrc"))
            self.assertEqual(observed["globalconfig"], str(Path(observed["home"]) / "global.npmrc"))
            self.assertEqual(observed["cache"], str(Path(observed["home"]) / "npm-cache"))
            self.assertEqual(observed["logs"], str(Path(observed["home"]) / "npm-logs"))
            self.assertIsNone(observed["node_options"])
            self.assertEqual(record["node_version"], "v-test")
            self.assertEqual(record["npm_version"], "v-test")

    def test_external_artifact_guard_rejects_repository_paths(self):
        with self.assertRaises(runner.EvaluationError):
            runner._require_external(runner.HERE / "output")
        with tempfile.TemporaryDirectory() as directory:
            self.assertEqual(runner._require_external(Path(directory)), Path(directory).resolve())

    def test_fixed_model_inputs_and_adjudication_destination_are_guarded(self):
        run = self.manifest["runs"][0]
        case = next(item for item in runner._read_json(runner.CASES_PATH)["cases"] if item["id"] == run["case_id"])
        workspace = Path(run["workspace"])
        self.assertTrue(runner._fixed_inputs_intact(self.manifest, run, case))
        eval_input = workspace / ".eval-input.json"
        original = eval_input.read_bytes()
        eval_input.write_text("{}\n", encoding="utf-8")
        self.assertFalse(runner._fixed_inputs_intact(self.manifest, run, case))
        eval_input.write_bytes(original)
        skill = next((workspace / ".agents/skills").rglob("SKILL.md"))
        skill_original = skill.read_bytes()
        skill.chmod(0o600)
        skill.write_bytes(skill_original + b"\n")
        self.assertFalse(runner._fixed_inputs_intact(self.manifest, run, case))
        skill.write_bytes(skill_original)
        with self.assertRaises(runner.EvaluationError):
            runner._require_not_model_visible(self.manifest, workspace / "adjudication.json")

    def test_controlled_matrix_uses_direct_workers_and_fixed_adjudicator(self):
        source = runner.validate_sources()
        worker_calls = sum(
            cohort["reviewer_count"] * source["cohorts"]["benchmark_repetitions"]
            for cohort in source["cohorts"]["cohorts"]
        )
        self.assertEqual(worker_calls, 24)
        self.assertEqual(controlled_benchmark.ADJUDICATOR_MODEL, "gpt-6-astra")
        self.assertEqual(controlled_benchmark.ADJUDICATOR_EFFORT, "high")
        prompt = controlled_benchmark._reviewer_prompt(source["cases"]["cases"][0])
        self.assertIn("Do not create, message, or wait for other agents", prompt)

    def test_controlled_plan_rejects_rehashed_evaluator_digest_mutation(self):
        changed = json.loads(json.dumps(self.plan))
        changed["controlled_runner_sha256"] = "a" * 64
        changed["plan_id"] = runner._sha_bytes(
            runner.encoded_json(runner._without_key(changed, "plan_id")).encode("utf-8")
        )
        path = Path(self.manifest["artifact_dir"]) / "controlled/plan.json"
        runner._write_json(path, changed)
        try:
            with self.assertRaises(runner.EvaluationError):
                controlled_benchmark._load_plan(self.output)
        finally:
            runner._write_json(path, self.plan)

    def _write_fake_complete_call(self, plan_run, call_root, workspace, call_id, role, model, effort, prompt):
        runner._reserve_once(call_root, call_root / "call.json")
        final = call_root / "final.md"
        trace = call_root / "trace.jsonl"
        stderr = call_root / "stderr.txt"
        command = call_root / "command.json"
        final.write_text("validated fixture review\n", encoding="utf-8")
        trace.write_text(json.dumps({"type": "turn.completed", "usage": {}}) + "\n", encoding="utf-8")
        stderr.write_text("", encoding="utf-8")
        runner._write_json(command, {
            "argv": controlled_benchmark._argv(self.manifest, model, effort, workspace, final, role),
            "cwd": str(workspace), "stdin_sha256": runner._sha_bytes(prompt.encode("utf-8")),
            "auth": "isolated CODEX_HOME with auth.json symlink only",
        })
        events, errors = runner._read_trace(trace)
        workspace_sha = runner._tree_sha(workspace, excluded=(".git",))
        value = {
            "schema_version": controlled_benchmark.CALL_VERSION,
            "plan_id": self.plan["plan_id"], "run_id": plan_run["run_id"], "call_id": call_id,
            "role": role, "status": "complete", "started_at": runner._utc_now(),
            "latency_seconds": 1.25, "returncode": 0, "timed_out": False, "spawn_error": None,
            "trace_errors": errors, "requested_model": model, "requested_effort": effort,
            "observed_model": "unknown", "observed_effort": "unknown",
            "trace_observations": runner._trace_observations(events),
            "workspace_initial_sha256": workspace_sha, "workspace_final_sha256": workspace_sha,
            "batch_jobs": 4,
            "artifacts": {"final": str(final), "trace": str(trace), "stderr": str(stderr), "command": str(command), "workspace": str(workspace)},
            "artifact_sha256": {"final": runner._sha_file(final), "trace": runner._sha_file(trace), "stderr": runner._sha_file(stderr), "command": runner._sha_file(command)},
        }
        runner._write_json(call_root / "call.json", value)
        return value

    def test_fake_native_pipeline_builds_valid_adjudicator_input_and_summary(self):
        plan_run = self.plan["runs"][0]
        worker = plan_run["workers"][0]
        worker_root = Path(self.manifest["artifact_dir"]) / "controlled/runs" / plan_run["run_id"] / "workers" / worker["worker_id"]
        case = next(item for item in runner._read_json(runner.CASES_PATH)["cases"] if item["id"] == plan_run["case_id"])
        self._write_fake_complete_call(
            plan_run, worker_root, Path(worker["workspace"]), worker["worker_id"], "delegated-reviewer",
            plan_run["model"], plan_run["effort"], controlled_benchmark._reviewer_prompt(case),
        )
        workspace = controlled_benchmark._prepare_adjudicator_workspace(self.manifest, self.plan, plan_run, case)
        self.assertTrue((workspace / "reviewer-results/worker-1.md").is_file())
        self.assertTrue((workspace / "criteria.md").is_file())
        self.assertTrue((workspace / "code-quality.md").is_file())
        self.assertEqual(
            runner._sha_file(workspace / "code-quality.md"), self.plan["code_quality_sha256"]
        )
        adjudicator_root = workspace.parent
        self._write_fake_complete_call(
            plan_run, adjudicator_root, workspace, "adjudicator", "fixed-adjudicator",
            controlled_benchmark.ADJUDICATOR_MODEL, controlled_benchmark.ADJUDICATOR_EFFORT,
            controlled_benchmark._adjudicator_prompt(plan_run["reviewer_count"]),
        )
        value = controlled_benchmark.summary(self.output)
        row = next(item for item in value["runs"] if item["run_id"] == plan_run["run_id"])
        self.assertEqual(row["worker_statuses"], ["complete"])
        self.assertEqual(row["adjudicator_status"], "complete")
        self.assertFalse(row["validation_errors"])
        adjudication_path = Path(self.temp.name) / "controlled-adjudication.json"
        adjudication = controlled_benchmark.make_adjudication_template(self.output, adjudication_path)
        grade = next(item for item in adjudication["runs"] if item["run_id"] == plan_run["run_id"])
        grade.update({"verdict": "pass", "validated_defects": ["external-payload-cast", "provider-session-leak"]})
        runner._write_json(adjudication_path, adjudication)
        rendered = controlled_benchmark.report(self.output, adjudication_path)
        self.assertIn("Controlled reviewer benchmark", rendered)
        self.assertIn("pass=1", rendered)
        self.assertIn("| 2 | 0 | 0 | 0 | 0 |", rendered)

    def test_manifest_rejects_rehashed_path_revision_binary_and_runner_mutations(self):
        mutations = [
            ("artifact_dir", "/tmp/not-the-artifact"),
            ("candidate_git_revision", "0" * 40),
            ("codex_binary", "/bin/false"),
            ("codex_sha256", "e" * 64),
            ("runner_sha256", "f" * 64),
        ]
        for field, replacement in mutations:
            with self.subTest(field=field):
                changed = json.loads(json.dumps(self.manifest))
                changed[field] = replacement
                changed["manifest_id"] = runner._sha_bytes(
                    runner.encoded_json(runner._without_key(changed, "manifest_id")).encode("utf-8")
                )
                with self.assertRaises(runner.EvaluationError):
                    runner._validate_manifest_structure(changed, self.output.resolve())

        changed = json.loads(json.dumps(self.manifest))
        changed["runs"][0]["workspace"] = "/tmp/wrong-workspace"
        changed["manifest_id"] = runner._sha_bytes(
            runner.encoded_json(runner._without_key(changed, "manifest_id")).encode("utf-8")
        )
        with self.assertRaises(runner.EvaluationError):
            runner._validate_manifest_structure(changed, self.output.resolve())

    def test_fabricated_complete_result_without_execution_is_not_observed(self):
        run = self.manifest["runs"][0]
        run_root = Path(self.manifest["artifact_dir"]) / "runs" / run["run_id"]
        fake = {field: None for field in runner.RESULT_FIELDS}
        fake.update({
            "schema_version": runner.RESULT_VERSION,
            "manifest_id": self.manifest["manifest_id"],
            "run_id": run["run_id"],
            "case_id": run["case_id"],
            "cohort_id": run["cohort_id"],
            "repetition": run["repetition"],
            "status": "pass",
            "execution_status": "complete",
            "semantic_adjudication": "pass",
            "latency_seconds": 999,
            "timed_out": False,
            "trace_errors": [],
            "requested_model": run["model"],
            "requested_effort": run["effort"],
            "requested_reviewer_count": run["reviewer_count"],
            "artifacts": {
                "final": str(run_root / "final.md"), "trace": str(run_root / "trace.jsonl"),
                "stderr": str(run_root / "stderr.txt"), "command": str(run_root / "command.json"),
                "workspace": run["workspace"],
            },
            "artifact_sha256": {"final": None, "trace": None, "stderr": None, "command": None},
        })
        runner._write_json(run_root / "result.json", fake)
        destination = Path(self.temp.name) / "adjudication.json"
        value = runner.make_adjudication_template(self.output, destination)
        row = next(item for item in value["runs"] if item["run_id"] == run["run_id"])
        self.assertFalse(row["execution_available"])
        self.assertEqual(row["verdict"], "not_run")
        self.assertTrue(row["notes"])

    def _routing_adjudication(self, target_run, observations):
        rows = []
        for run in self.manifest["runs"]:
            selected = run["run_id"] == target_run["run_id"]
            rows.append({
                "run_id": run["run_id"], "execution_available": selected,
                "verdict": "pass" if selected else "not_run",
                "validated_defects": [], "critical_misses": [], "false_positives": [],
                "duplicate_findings": [], "unnecessary_changes": [],
                "routing": "pass" if selected else "not_run", "notes": "",
            })
        value = {
            "schema_version": runner.ADJUDICATION_VERSION, "manifest_id": self.manifest["manifest_id"],
            "created_at": runner._utc_now(), "runs": rows,
        }
        path = Path(self.temp.name) / f"routing-{target_run['run_id']}.json"
        runner._write_json(path, value)
        results = {target_run["run_id"]: {"execution_status": "complete", "trace_observations": observations}}
        return path, results

    def test_routing_pass_requires_expected_unique_reviewers_with_nonempty_results(self):
        run = next(item for item in self.manifest["runs"] if item["run_id"] == "general-review-default--native-default--r1")
        events = []
        for index in range(5):
            agent = f"agent-{index}"
            events.extend([
                {"type": "item.completed", "item": {
                    "type": "collab_tool_call", "tool": "spawn_agent",
                    "receiver_thread_ids": [agent], "agents_states": {agent: {"status": "pending_init"}},
                }},
                {"type": "item.completed", "item": {
                    "type": "collab_tool_call", "tool": "wait",
                    "receiver_thread_ids": [agent],
                    "agents_states": {agent: {"status": "completed", "message": f"review {index}"}},
                }},
            ])
        observations = runner._trace_observations(events)
        path, results = self._routing_adjudication(run, observations)
        runner._validated_adjudication(self.manifest, path, results)

        missing_result = json.loads(json.dumps(observations))
        missing_result["completed_agent_ids_with_message"] = missing_result["completed_agent_ids_with_message"][:-1]
        missing_result["matching_completed_agent_ids_with_message"] = missing_result["matching_completed_agent_ids_with_message"][:-1]
        _, incomplete_results = self._routing_adjudication(run, missing_result)
        with self.assertRaises(runner.EvaluationError):
            runner._validated_adjudication(self.manifest, path, incomplete_results)

    def test_zero_reviewer_routing_pass_rejects_agent_attempt(self):
        run = next(item for item in self.manifest["runs"] if item["run_id"] == "mechanical-deterministic--native-default--r1")
        observations = runner._trace_observations([{"type": "item.completed", "item": {
            "type": "collab_tool_call", "tool": "spawn_agent", "receiver_thread_ids": [], "agents_states": {},
        }}])
        path, results = self._routing_adjudication(run, observations)
        with self.assertRaises(runner.EvaluationError):
            runner._validated_adjudication(self.manifest, path, results)

    def test_atomic_reservation_allows_one_launch_and_preserves_first_output(self):
        root = Path(self.temp.name) / "race"
        result = root / "result.json"
        output = root / "final.md"
        barrier = threading.Barrier(2)
        launches = 0
        guard = threading.Lock()

        def attempt(label):
            nonlocal launches
            barrier.wait()
            try:
                runner._reserve_once(root, result)
            except runner.EvaluationError:
                return "rejected"
            with guard:
                launches += 1
            output.write_text(label, encoding="utf-8")
            return "launched"

        with ThreadPoolExecutor(max_workers=2) as pool:
            outcomes = list(pool.map(attempt, ("first", "second")))
        self.assertEqual(sorted(outcomes), ["launched", "rejected"])
        self.assertEqual(launches, 1)
        self.assertIn(output.read_text(encoding="utf-8"), {"first", "second"})


if __name__ == "__main__":
    unittest.main()
