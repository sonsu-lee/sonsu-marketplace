"""Focused contract tests for the bounded Fluent Japanese evaluator."""

import importlib.util
import json
import datetime as dt
from pathlib import Path
import stat
import sys
import tempfile
import unittest
from unittest.mock import patch


MODULE = Path(__file__).with_name("eval.py")
SPEC = importlib.util.spec_from_file_location("fluent_japanese_eval", MODULE)
evaluation = importlib.util.module_from_spec(SPEC)
assert SPEC.loader is not None
SPEC.loader.exec_module(evaluation)


def write_fixture(root: Path):
    cases = {
        "schema_version": "fluent-japanese-cases-v1",
        "cases": [
            {
                "id": "ordered-code",
                "kind": "generation",
                "prompt": "日本語で説明してください。",
                "evidence": "first, then second",
                "expectations": {
                    "exact": {
                        "protected_literals": ["first", "second"],
                        "required_headings": ["## 手順", "## 終了"],
                        "ordered_markers": ["first", "second"],
                        "exact_code_blocks": ["```sh\nfirst\nsecond\n```"],
                        "literal_counts": {"first": 2},
                    }
                },
            },
            {
                "id": "native-route-only",
                "kind": "routing",
                "prompt": "日本語で答えてください。",
                "evidence": "route",
                "expectations": {"exact": {}},
            },
        ],
    }
    case_path = root / "cases.json"
    case_path.write_text(json.dumps(cases, ensure_ascii=False), encoding="utf-8")
    base = root / "baseline.md"
    candidate = root / "candidate.md"
    protocol = root / "protocol.md"
    base.write_text("---\nname: fluent-japanese\n---\nbase", encoding="utf-8")
    candidate.write_text("---\nname: fluent-japanese\n---\ncandidate", encoding="utf-8")
    protocol.write_text("# Frozen protocol\n", encoding="utf-8")
    return case_path, base, candidate, protocol


class ManifestAndGateTests(unittest.TestCase):
    def test_plan_balances_ab_ba_and_excludes_native_routing(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            cases, base, candidate, protocol = write_fixture(root)
            manifest_path = root / "outside" / "manifest.json"
            manifest = evaluation.create_manifest(cases, base, candidate, manifest_path, seed=5, protocol_path=protocol)
            self.assertEqual(len(manifest["runs"]), 4)
            self.assertEqual([row["arm"] for row in manifest["runs"][:2]], list(reversed([row["arm"] for row in manifest["runs"][2:]])))
            self.assertEqual(manifest["routing_cases_excluded"][0]["id"], "native-route-only")
            self.assertEqual(manifest["hashes"]["runner_sha256"], evaluation._sha_file(MODULE))
            self.assertEqual(manifest["hashes"]["protocol_sha256"], evaluation._sha_file(protocol))

    def test_hard_check_detects_wrong_heading_order_and_literal_count(self):
        case = {
            "expectations": {
                "exact": {
                    "protected_literals": ["alpha"],
                    "required_headings": ["## A", "## B"],
                    "ordered_markers": ["alpha", "omega"],
                    "literal_counts": {"alpha": 2},
                }
            }
        }
        result = evaluation.hard_check(case, "## B\nalpha\n## A\nomega")
        gates = {failure["gate"] for failure in result["failures"]}
        self.assertEqual(result["status"], "fail")
        self.assertIn("heading_order", gates)
        self.assertIn("literal_count", gates)

    def test_exact_code_block_accepts_three_space_list_indent_but_not_changed_code(self):
        expected = "```sh\ndeployctl status --env prod\ndeployctl retry --job JOB-417\n```"
        case = {"expectations": {"exact": {"exact_code_blocks": [expected]}}}
        indented = "1. 実行します。\n\n   ```sh\n   deployctl status --env prod\n   deployctl retry --job JOB-417\n   ```"
        self.assertEqual(evaluation.hard_check(case, indented)["status"], "pass")
        changed = indented.replace("retry --job JOB-417", "retry --job JOB-418")
        failures = evaluation.hard_check(case, changed)["failures"]
        self.assertIn("exact_code_block", {row["gate"] for row in failures})

    def test_execution_classifier_never_calls_timeout_a_complete_result(self):
        status, reason, trace, check = evaluation._classify(
            {"timed_out": True, "spawn_error": None, "returncode": 0},
            "answer",
            [{"type": "turn.completed"}],
            [],
            {"expectations": {"exact": {}}},
        )
        self.assertEqual((status, reason), ("timeout", "deadline"))
        self.assertTrue(trace["turn_completed"])
        self.assertEqual(check["status"], "pass")

    def test_prompt_inspection_reads_content_parts_before_contamination_gate(self):
        messages = evaluation._preflight_messages(
            [{"role": "developer", "content": [{"type": "input_text", "text": "intended"}]}, {"role": "user", "content": [{"type": "input_text", "text": "probe"}]}]
        )
        self.assertEqual(messages, [("developer", "intended"), ("user", "probe")])

    def test_two_sided_sign_test_is_symmetric(self):
        self.assertEqual(evaluation.exact_two_sided_sign_test(4, 1), evaluation.exact_two_sided_sign_test(1, 4))
        self.assertEqual(evaluation.exact_two_sided_sign_test(0, 0), 1.0)
        self.assertLess(evaluation.exact_two_sided_sign_test(10, 0), 0.01)

    def test_case_level_sign_samples_require_two_matching_repetitions(self):
        outcomes = evaluation.case_level_outcomes([
            {"pair_id": "one-r1", "winner": "candidate", "preference": "candidate"},
            {"pair_id": "one-r2", "winner": "candidate", "preference": "candidate"},
            {"pair_id": "two-r1", "winner": "candidate", "preference": "candidate"},
            {"pair_id": "two-r2", "winner": "baseline", "preference": "baseline"},
            {"pair_id": "partial-r1", "winner": "candidate", "preference": "candidate"},
        ])
        self.assertEqual([(row["case_id"], row["winner"]) for row in outcomes], [("one", "candidate"), ("two", None)])
        self.assertEqual(outcomes[0]["target_ok_score"], {"baseline": 0, "candidate": 0})

    def test_judge_result_joins_by_opaque_id_and_rejects_swapped_unknown_or_duplicate_ids(self):
        def item(item_id, preference):
            return {"item_id": item_id, "semantic_ok": {"X": True, "Y": True}, "target_ok": {"X": True, "Y": True}, "overcorrection": {"X": False, "Y": False}, "preference": preference, "rationale": "evidence"}
        # Reordered array is harmless because callers address this map by ID.
        parsed = evaluation._validated_judge_items(json.dumps({"items": [item("opaque-b", "Y"), item("opaque-a", "X")]}), ["opaque-a", "opaque-b"])
        self.assertEqual(parsed["opaque-a"]["preference"], "X")
        with self.assertRaisesRegex(ValueError, "set does not match"):
            evaluation._validated_judge_items(json.dumps({"items": [item("opaque-a", "X"), item("unknown", "Y")]}), ["opaque-a", "opaque-b"])
        with self.assertRaisesRegex(ValueError, "duplicate"):
            evaluation._validated_judge_items(json.dumps({"items": [item("opaque-a", "X"), item("opaque-a", "Y")]}), ["opaque-a", "opaque-b"])

    def test_cached_judge_result_cannot_be_reused_for_a_different_grade_plan(self):
        expected = {"manifest_id": "m", "grade_plan_sha256": "new-plan", "batch_id": "batch-001", "judge": 1, "item_ids": ["opaque-a"], "input_sha256": "input", "developer_sha256": "developer"}
        cached = dict(expected)
        cached["grade_plan_sha256"] = "old-plan"
        with self.assertRaisesRegex(evaluation.ValidationError, "frozen grade plan"):
            evaluation._validate_cached_judge_result(cached, expected, Path("/outside/result.json"))

    def test_existing_grade_plan_rejects_a_later_batch_size(self):
        with tempfile.TemporaryDirectory() as directory:
            manifest = {"manifest_id": "m", "artifact_dir": directory}
            pairs = [
                {"pair_id": "a-r1", "case": {"prompt": "p1", "evidence": "e1"}, "outputs": {"baseline": "b1", "candidate": "c1"}},
                {"pair_id": "b-r1", "case": {"prompt": "p2", "evidence": "e2"}, "outputs": {"baseline": "b2", "candidate": "c2"}},
            ]
            evaluation._write_grade_plan(manifest, evaluation._grade_plan(manifest, pairs, 1))
            with self.assertRaisesRegex(evaluation.ValidationError, "grade plan differs"):
                evaluation._write_grade_plan(manifest, evaluation._grade_plan(manifest, pairs, 2))

    def test_hidden_judge_payload_includes_semantic_rules_and_rejects_bad_shapes(self):
        pair = {"pair_id": "case-r1", "case": {"expectations": {"semantic": {"must_preserve": ["actor remains"], "must_not_introduce": ["new actor"]}, "target_ok": {"ja": "keep usage"}}, "review_points": ["preserve register"]}}
        text = evaluation._judge_developer([pair], {"case-r1": {"item_id": "opaque-a", "X": "baseline", "Y": "candidate"}})
        self.assertIn("actor remains", text)
        self.assertIn("new actor", text)
        broken = {"pair_id": "bad-r1", "case": {"expectations": {"semantic": {"must_preserve": "not-a-list"}}}}
        with self.assertRaisesRegex(evaluation.ValidationError, "semantic.must_preserve"):
            evaluation._judge_developer([broken], {"bad-r1": {"item_id": "opaque-b", "X": "baseline", "Y": "candidate"}})

    def test_family_gate_blocks_effect_claim_after_candidate_regression(self):
        gates = evaluation.family_gates([{"family": "particles", "overcorrection": {"baseline": False, "candidate": True}, "semantic_ok": {"baseline": True, "candidate": False}, "structural_status": {"baseline": "pass", "candidate": "fail"}}])
        self.assertTrue(gates["particles"]["overcorrection_regression"])
        self.assertEqual(gates["particles"]["new_candidate_semantic_violations"], 1)
        self.assertEqual(gates["particles"]["new_candidate_exact_violations"], 1)

    def test_high_win_truncated_subset_is_inconclusive_not_effect_eligible(self):
        completeness = {"expected_pairs": 100, "pairs_available": 8, "pairs_judged_complete": 8, "expected_judge_calls": 30, "judge_calls_requested": 3, "judge_calls_complete": 3, "expected_cases_with_both_repetitions": 50, "cases_with_both_repetitions_complete": 4, "complete": False}
        gate = evaluation.effect_claim_gate(8, 0, evaluation.exact_two_sided_sign_test(8, 0), 0, 0, [], completeness)
        self.assertEqual(gate["status"], "inconclusive_missing_data")
        self.assertTrue(gate["requirements"]["two_sided_p_lt_0_05"])


class ReviewRegressionTests(unittest.TestCase):
    def make_manifest(self, root):
        cases, base, candidate, protocol = write_fixture(root)
        path = root / "runs" / "manifest.json"
        return path, evaluation.create_manifest(cases, base, candidate, path, seed=5, protocol_path=protocol)

    def seed_results(self, manifest):
        for run in manifest["runs"]:
            path = evaluation._result_path(manifest, run)
            output = path.parent / "output.md"
            evaluation._write_text(output, "answer")
            evaluation._write_json(path, {
                "schema_version": evaluation.RESULT_VERSION,
                "manifest_id": manifest["manifest_id"],
                **{key: run[key] for key in ("run_id", "case_id", "arm", "repetition")},
                "execution_status": "complete", "structural_status": "pass", "check": {},
                "artifacts": {"output": str(output), "output_sha256": evaluation._sha_file(output)},
            })

    def test_generation_identity_is_checked_in_grade_resume_and_summary(self):
        with tempfile.TemporaryDirectory() as directory:
            path, manifest = self.make_manifest(Path(directory))
            self.seed_results(manifest)
            self.assertEqual(len(evaluation._completed_pairs(manifest)), 2)
            run = manifest["runs"][0]
            record_path = evaluation._result_path(manifest, run)
            original = evaluation._load_json(record_path)
            for key, bad in (("manifest_id", "other"), ("run_id", "other"), ("case_id", "other"), ("arm", "other"), ("repetition", 99)):
                evaluation._write_json(record_path, {**original, key: bad})
                consumers = {
                    "grade": lambda: evaluation._completed_pairs(manifest),
                    "resume": lambda: evaluation._execute_one(manifest, run, manifest["generation_cases"][0], 600),
                    "summary": lambda: evaluation.summarize(path),
                }
                for consumer, call in consumers.items():
                    with self.subTest(key=key, consumer=consumer), self.assertRaises(evaluation.ValidationError):
                        call()
            evaluation._write_json(record_path, original)
            self.assertTrue(evaluation.summarize(path)["complete"])

    def test_another_manifests_preflight_cannot_authorize_execution(self):
        with tempfile.TemporaryDirectory() as directory:
            path, manifest = self.make_manifest(Path(directory))
            self.seed_results(manifest)
            proof = Path(manifest["artifact_dir"]) / "preflight" / "result.json"
            evaluation._write_json(proof, {"status": "pass", "manifest_id": "other"})
            with self.assertRaises(evaluation.ValidationError):
                evaluation.run_manifest(path, workers=1)
            evaluation._write_json(proof, {"status": "pass", "manifest_id": manifest["manifest_id"]})
            self.assertTrue(evaluation.run_manifest(path, workers=1)["complete"])

    def test_timeout_above_protocol_limit_is_rejected_before_execution(self):
        with tempfile.TemporaryDirectory() as directory:
            path, manifest = self.make_manifest(Path(directory))
            self.seed_results(manifest)
            evaluation._write_json(Path(manifest["artifact_dir"]) / "preflight" / "result.json", {"status": "pass", "manifest_id": manifest["manifest_id"]})
            for timeout in (601, 3600):
                with self.subTest(timeout=timeout), self.assertRaises(evaluation.ValidationError):
                    evaluation.run_manifest(path, workers=1, timeout=timeout)
            self.assertTrue(evaluation.run_manifest(path, workers=1, timeout=600)["complete"])

    def test_writing_artifacts_preserves_existing_directory_mode(self):
        with tempfile.TemporaryDirectory() as directory:
            shared = Path(directory) / "shared"
            shared.mkdir(mode=0o755)
            shared.chmod(0o755)
            for filename, writer, value in (("one.json", evaluation._write_json, {}), ("two.txt", evaluation._write_text, "text")):
                writer(shared / filename, value)
                self.assertEqual(stat.S_IMODE(shared.stat().st_mode), 0o755)
            leaf = shared / "private"
            evaluation._write_json(leaf / "record.json", {})
            self.assertEqual(stat.S_IMODE(leaf.stat().st_mode), 0o700)

    def test_plan_rejects_wrong_language_missing_frontmatter_and_unresolved_include(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            cases, base, candidate, protocol = write_fixture(root)
            invalid = (
                "---\nname: fluent-english\n---\nbody",
                "body\nname: fluent-japanese\n",
                "---\nname: fluent-japanese\n---\n{{ include: common.md }}",
            )
            for index, text in enumerate(invalid):
                base.write_text(text, encoding="utf-8")
                with self.subTest(index=index), self.assertRaises(evaluation.ValidationError):
                    evaluation.create_manifest(cases, base, candidate, root / ("invalid-%d.json" % index), protocol_path=protocol)

    def test_fenced_headings_and_structural_markers_do_not_count_as_document_structure(self):
        case = {"expectations": {"exact": {"required_headings": ["## A"], "ordered_markers": ["1. first", "2. second"]}}}
        body = "## A\n1. first\n2. second\n"
        self.assertEqual(evaluation.hard_check(case, body)["status"], "pass")
        for opening, closing in (("```markdown", "```"), ("~~~~markdown", "~~~~"), ("   ```markdown", "   ```"), ("```markdown", "")):
            with self.subTest(opening=opening, closing=closing):
                result = evaluation.hard_check(case, opening + "\n" + body + closing)
                self.assertEqual(result["status"], "fail")
                self.assertIn("required_heading", {failure["gate"] for failure in result["failures"]})
                self.assertIn("ordered_marker", {failure["gate"] for failure in result["failures"]})

    def test_fence_content_still_participates_in_literal_and_exact_code_checks(self):
        block = "```sh\nfirst\nsecond\n```"
        case = {"expectations": {"exact": {"required_headings": ["## A"], "protected_literals": ["first"], "exact_code_blocks": [block], "literal_counts": {"first": 1}}}}
        self.assertEqual(evaluation.hard_check(case, "## A\n" + block)["status"], "pass")

    def test_preflight_normalizes_actual_scratch_under_default_and_custom_temp_roots(self):
        real_tempdir = tempfile.TemporaryDirectory
        for temp_root in (None, "/tmp"):
            with real_tempdir(dir=temp_root) as directory:
                path, _ = self.make_manifest(Path(directory))
                for different_rule in (False, True):
                    arm_index = iter((0, 1))
                    # Replace only the external CLI; retain parsing and the pass gate.
                    def prompt_input(argv, cwd, stdin, timeout, stdout, stderr):
                        index = next(arm_index)
                        config = next(value for value in argv if value.startswith("developer_instructions="))
                        developer = json.loads(config.split("=", 1)[1])
                        rule = "rule B" if different_rule and index else "rule A"
                        messages = [{"role": "developer", "content": developer}, {"role": "user", "content": "Return exactly: PRELIGHT_OK"}, {"role": "system", "content": "cwd=" + str(cwd) + "\n" + rule + "\nfixed=/var/folders/shared/rules"}]
                        stdout.write_text(json.dumps(messages), encoding="utf-8")
                        stderr.write_text("")
                        return {"returncode": 0, "timed_out": False, "spawn_error": None, "latency_seconds": 0}
                    raw = evaluation._load_json(path)
                    attempt = Path(directory) / ("different" if different_rule else "same")
                    raw["artifact_dir"] = str(attempt)
                    attempt_path = attempt / "manifest.json"
                    evaluation._write_json(attempt_path, raw)
                    def scratch_dir(**kwargs):
                        return real_tempdir(prefix="jp-writing-preflight-", dir=directory)
                    with patch.object(evaluation, "_run_process", side_effect=prompt_input), patch.object(evaluation.tempfile, "TemporaryDirectory", side_effect=scratch_dir):
                        result = evaluation.preflight(attempt_path)
                    with self.subTest(temp_root=temp_root, different_rule=different_rule):
                        self.assertEqual(result["status"], "fail" if different_rule else "pass")
                        common = evaluation._load_json(attempt / "preflight/baseline.common-context.json")
                        self.assertIn("fixed=/var/folders/shared/rules", json.dumps(common["entries"]))

    def test_unknown_and_tool_items_are_inconclusive_in_generation(self):
        process = {"timed_out": False, "spawn_error": None, "returncode": 0}
        case = {"expectations": {"exact": {}}}
        for item_type in ("web_search", "file_change", "image_view", "image_generation", "future_tool", "todo_list", "error", "command_execution"):
            events = [{"type": "item.completed", "item": {"type": item_type}}, {"type": "turn.completed"}]
            with self.subTest(item_type=item_type):
                self.assertEqual(evaluation._classify(process, "answer", events, [], case)[0], "inconclusive")
        events = [{"type": "item.completed", "item": {"type": "reasoning", "text": "thinking"}}, {"type": "item.completed", "item": {"type": "agent_message", "text": "answer"}}, {"type": "turn.completed"}]
        self.assertEqual(evaluation._classify(process, "answer", events, [], case)[0], "complete")

    def test_process_records_start_and_completion_around_real_child_execution(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            result = evaluation._run_process([sys.executable, "-c", "import datetime; print(datetime.datetime.now(datetime.timezone.utc).isoformat())"], root, "", 30, root / "stdout", root / "stderr")
            self.assertIn("started_at", result)
            self.assertIn("completed_at", result)
            child_time = dt.datetime.fromisoformat((root / "stdout").read_text().strip())
            self.assertLessEqual(dt.datetime.fromisoformat(result["started_at"].replace("Z", "+00:00")), child_time)
            self.assertLessEqual(child_time, dt.datetime.fromisoformat(result["completed_at"].replace("Z", "+00:00")))
            self.assertEqual(result.get("timeout_seconds"), 30)

    def test_generation_retains_process_timestamps_and_records_effective_timeout(self):
        with tempfile.TemporaryDirectory() as directory:
            _, manifest = self.make_manifest(Path(directory))
            run = manifest["runs"][0]
            process_record = {"returncode": 0, "timed_out": False, "spawn_error": None, "latency_seconds": 2.0, "started_at": "2026-09-06T00:00:00+00:00", "completed_at": "2026-09-06T00:00:02+00:00", "timeout_seconds": 45}
            def process(argv, cwd, stdin, timeout, stdout, stderr):
                Path(argv[argv.index("--output-last-message") + 1]).write_text("answer")
                stdout.write_text('{"type":"turn.completed"}\n')
                stderr.write_text("")
                return process_record
            with patch.object(evaluation, "_run_process", side_effect=process):
                result = evaluation._execute_one(manifest, run, manifest["generation_cases"][0], 45)
            self.assertEqual(result["started_at"], "2026-09-06T00:00:00+00:00")
            self.assertEqual(result["completed_at"], "2026-09-06T00:00:02+00:00")
            self.assertEqual(result["timeout_seconds"], 45)
            command = evaluation._load_json(Path(result["artifacts"]["command"]))
            self.assertEqual(command["timeout_seconds"], 45)

    def test_judge_rejects_tool_and_future_items_even_with_valid_votes(self):
        pair = {"pair_id": "one-r1", "case": {"prompt": "p", "evidence": "e", "expectations": {}}, "outputs": {"baseline": "b", "candidate": "c"}}
        for item_type in ("agent_message", "web_search", "future_tool"):
            with tempfile.TemporaryDirectory() as directory:
                manifest = {"manifest_id": "m", "artifact_dir": directory}
                def process(argv, cwd, stdin, timeout, stdout, stderr):
                    item_id = json.loads(stdin)["items"][0]["item_id"]
                    item = {"item_id": item_id, "semantic_ok": {"X": True, "Y": True}, "target_ok": {"X": True, "Y": True}, "overcorrection": {"X": False, "Y": False}, "preference": "tie", "rationale": "equivalent"}
                    Path(argv[argv.index("--output-last-message") + 1]).write_text(json.dumps({"items": [item]}))
                    stdout.write_text(json.dumps({"type": "item.completed", "item": {"type": item_type}}) + '\n{"type":"turn.completed"}\n')
                    stderr.write_text("")
                    return {"returncode": 0, "timed_out": False, "spawn_error": None, "latency_seconds": 0}
                with patch.object(evaluation, "_run_process", side_effect=process):
                    result = evaluation._judge_one(manifest, [pair], "batch-001", 1, evaluation._grade_plan(manifest, [pair], 1))
                with self.subTest(item_type=item_type):
                    self.assertEqual(result["execution_status"], "complete" if item_type == "agent_message" else "inconclusive")


if __name__ == "__main__":
    unittest.main()
