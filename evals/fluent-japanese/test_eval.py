"""Focused contract tests for the bounded Fluent Japanese evaluator."""

import importlib.util
import json
from pathlib import Path
import tempfile
import unittest


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
    base.write_text("---\nname: baseline-ja\n---\nbase", encoding="utf-8")
    candidate.write_text("---\nname: candidate-ja\n---\ncandidate", encoding="utf-8")
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


if __name__ == "__main__":
    unittest.main()
