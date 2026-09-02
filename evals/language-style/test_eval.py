#!/usr/bin/env python3
"""Unit tests for the language-style evaluation runner (no model calls)."""

import importlib.util
import json
import math
from pathlib import Path
import tempfile
import unittest


MODULE_PATH = Path(__file__).with_name("eval.py")
SPEC = importlib.util.spec_from_file_location("language_style_eval", MODULE_PATH)
assert SPEC is not None and SPEC.loader is not None
evaluation = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(evaluation)


def make_case(case_id, category):
    return {
        "id": case_id,
        "category": category,
        "prompt": "주어진 근거로 짧은 기술 보고서를 작성하세요.",
        "evidence": "검증 상태는 pass이며 추가 사실은 확인되지 않았습니다.",
        "required_substrings": [],
        "protected_literals": [],
        "forbidden_substrings": [],
        "allowed_numbers": [],
        "required_headings": [],
        "ordered_markers": [],
        "exact_code_blocks": [],
        "min_chars": 1,
        "max_chars": 2000,
    }


def write_fixture_tree(root):
    candidate_dir = root / "candidates"
    candidate_dir.mkdir(parents=True)
    (candidate_dir / "common.md").write_text("COMMON_SECRET\n", encoding="utf-8")
    (candidate_dir / "c-baseline.md").write_text("BASELINE_SECRET\n", encoding="utf-8")
    (candidate_dir / "a-im-only.md").write_text("IM_ONLY_SECRET\n", encoding="utf-8")
    (candidate_dir / "b-hybrid.md").write_text(
        "IM_ONLY_SECRET\n\nHYBRID_SECRET\n", encoding="utf-8"
    )
    categories = ["category-%d" % index for index in range(1, 7)]
    screen = []
    confirm = []
    for category_index, category in enumerate(categories, 1):
        for repetition in range(1, 3):
            screen.append(
                make_case(
                    "screen-%d-%d" % (category_index, repetition), category
                )
            )
        for repetition in range(1, 4):
            confirm.append(
                make_case(
                    "confirm-%d-%d" % (category_index, repetition), category
                )
            )
    screen_path = root / "cases-screen.json"
    confirm_path = root / "cases-confirm.json"
    screen_path.write_text(
        json.dumps(
            {
                "schema_version": evaluation.SCHEMA_VERSION,
                "stage": "screen",
                "cases": screen,
            },
            ensure_ascii=False,
        ),
        encoding="utf-8",
    )
    confirm_path.write_text(
        json.dumps(
            {
                "schema_version": evaluation.SCHEMA_VERSION,
                "stage": "confirm",
                "cases": confirm,
            },
            ensure_ascii=False,
        ),
        encoding="utf-8",
    )
    return candidate_dir, screen_path, confirm_path


class ValidationTests(unittest.TestCase):
    def test_validates_candidate_and_case_counts(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            candidate_dir, screen, confirm = write_fixture_tree(root)
            result = evaluation.validate_inputs(candidate_dir, screen, confirm)
            self.assertEqual(result["summary"]["screen_cases"], 12)
            self.assertEqual(result["summary"]["confirm_cases"], 18)
            self.assertEqual(set(result["summary"]["candidate_ids"]), {"A", "B", "C"})
            self.assertEqual(set(result["summary"]["categories"].values()), {5})

    def test_rejects_duplicate_id_and_invalid_range(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            candidate_dir, screen, confirm = write_fixture_tree(root)
            data = json.loads(confirm.read_text(encoding="utf-8"))
            data["cases"][0]["id"] = "screen-1-1"
            confirm.write_text(json.dumps(data), encoding="utf-8")
            with self.assertRaisesRegex(evaluation.ValidationError, "globally unique"):
                evaluation.validate_inputs(candidate_dir, screen, confirm)

            _, screen, confirm = write_fixture_tree(root / "second")
            data = json.loads(screen.read_text(encoding="utf-8"))
            data["cases"][0]["min_chars"] = 50
            data["cases"][0]["max_chars"] = 10
            screen.write_text(json.dumps(data), encoding="utf-8")
            with self.assertRaisesRegex(evaluation.ValidationError, "max_chars"):
                evaluation.validate_inputs(root / "second" / "candidates", screen, confirm)

    def test_manifest_hash_and_randomized_order_are_frozen(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            candidate_dir, screen, confirm = write_fixture_tree(root / "fixtures")
            manifest_path = root / "artifacts" / "manifest.json"
            evaluation.create_manifest(
                "screen",
                seed=19,
                output=manifest_path,
                candidate_dir=candidate_dir,
                screen_cases=screen,
                confirm_cases=confirm,
            )
            loaded = evaluation.load_manifest(manifest_path)
            self.assertEqual(
                sorted(run["order"] for run in loaded["runs"]),
                list(range(1, 73)),
            )
            tampered = json.loads(manifest_path.read_text(encoding="utf-8"))
            tampered["runs"][0]["order"] = tampered["runs"][1]["order"]
            tampered["manifest_sha256"] = evaluation._manifest_digest(tampered)
            tampered["manifest_id"] = tampered["manifest_sha256"][:16]
            manifest_path.write_text(json.dumps(tampered), encoding="utf-8")
            with self.assertRaisesRegex(evaluation.ValidationError, "1..N permutation"):
                evaluation.load_manifest(manifest_path)


class HardGateTests(unittest.TestCase):
    def case(self):
        case = make_case("hard-gate-case", "checks")
        case.update(
            {
                "required_substrings": ["필수 사실"],
                "protected_literals": ["GET /v1/items"],
                "forbidden_substrings": ["배포 완료"],
                "allowed_numbers": ["1", "2", "7"],
                "required_headings": ["## 결과", "## 절차"],
                "ordered_markers": ["먼저", "다음"],
                "exact_code_blocks": ["```python\nvalue = 7\n```"],
                "min_chars": 40,
                "max_chars": 500,
            }
        )
        return case

    def test_all_hard_gates_pass_with_explicitly_allowed_list_numbers(self):
        output = """## 결과
필수 사실은 `GET /v1/items`에 적용됩니다.

## 절차
1. 먼저 확인합니다.
2. 다음 명령을 확인합니다.

```python
value = 7
```
"""
        result = evaluation.hard_check(self.case(), output)
        self.assertEqual(result["status"], "pass", result["failures"])
        self.assertEqual(result["metrics"]["numeric_literals"], ["1", "1", "2", "7"])

    def test_reports_content_structure_number_and_length_failures(self):
        output = """## 절차
다음 단계에서 배포 완료라고 단정합니다.
먼저 8건을 확인합니다.

```python
value = 8
```

## 결과
"""
        result = evaluation.hard_check(self.case(), output)
        gates = {failure["gate"] for failure in result["failures"]}
        self.assertEqual(result["status"], "fail")
        self.assertTrue(
            {
                "required_substring",
                "protected_literal",
                "forbidden_substring",
                "unexpected_number",
                "heading_order",
                "ordered_marker",
                "exact_code_block",
            }.issubset(gates),
            gates,
        )

    def test_numeric_components_include_embedded_versions_times_and_units(self):
        self.assertEqual(
            evaluation._numeric_literals("p99 v1.2 09:00 512Mi\n1. 첫째"),
            ["99", "1", "2", "09", "00", "512", "1"],
        )

    def test_unallowed_number_at_row_start_is_not_treated_as_a_list_marker(self):
        case = make_case("row-number-case", "checks")
        result = evaluation.hard_check(case, "404. 새 오류")
        self.assertIn(
            {"gate": "unexpected_number", "detail": "404"}, result["failures"]
        )

    def test_structural_ordered_markers_must_start_markdown_lines(self):
        case = make_case("structural-marker-case", "checks")
        case["allowed_numbers"] = ["1"]
        case["ordered_markers"] = ["## 결과", "| 항목 |", "1. 단계"]
        inline = "문장 속 ## 결과\n문장 속 | 항목 |\n문장 속 1. 단계"
        failures = evaluation.hard_check(case, inline)["failures"]
        self.assertEqual(
            [row["detail"] for row in failures if row["gate"] == "ordered_marker"],
            case["ordered_markers"],
        )
        structured = "## 결과\n   | 항목 |\n1. 단계"
        self.assertEqual(evaluation.hard_check(case, structured)["status"], "pass")

    def test_empty_exact_block_contract_allows_optional_fences(self):
        case = make_case("optional-fence-case", "checks")
        output = "```text\noptional diagnostic\n```"
        self.assertEqual(evaluation.hard_check(case, output)["status"], "pass")


class StatisticsTests(unittest.TestCase):
    def test_exact_one_sided_sign_test(self):
        expected = sum(math.comb(30, k) for k in range(20, 31)) / (2**30)
        self.assertAlmostEqual(evaluation.exact_sign_test_p(20, 10), expected)
        self.assertLess(evaluation.exact_sign_test_p(20, 10), 0.05)
        self.assertGreater(evaluation.exact_sign_test_p(19, 11), 0.05)
        self.assertEqual(evaluation.exact_sign_test_p(0, 0), 1.0)

    def test_ties_count_against_multi_reviewer_majority(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            pairs = {
                "pair-one": {
                    "task_id": "task-one",
                    "category": "category-one",
                    "left": "B",
                    "right": "A",
                    "repetitions": [
                        {
                            "repetition": repetition,
                            "left": {
                                "run_id": "left-%d" % repetition,
                                "output_sha256": "a" * 64,
                            },
                            "right": {
                                "run_id": "right-%d" % repetition,
                                "output_sha256": "b" * 64,
                            },
                        }
                        for repetition in (1, 2)
                    ],
                }
            }
            seed = 3
            public_pairs = [
                {
                    "pair_id": "pair-one",
                    "task_id": "task-one",
                    "category": "category-one",
                    "prompt": "prompt",
                    "evidence": "evidence",
                    "repetitions": [
                        {"repetition": 1, "left": "left 1", "right": "right 1"},
                        {"repetition": 2, "left": "left 2", "right": "right 2"},
                    ],
                }
            ]
            public_digest = evaluation._sha256_json(
                {"pairs": public_pairs, "axes": list(evaluation.RATING_AXES)}
            )
            template_digest = evaluation._sha256_bytes(
                evaluation._review_html("__REVIEW_ID__", public_pairs).encode("utf-8")
            )
            review_id = evaluation._sha256_json(
                {
                    "manifest_ids": [],
                    "seed": seed,
                    "pairs": pairs,
                    "public_bundle_sha256": public_digest,
                    "html_template_sha256": template_digest,
                }
            )[:16]
            key_path = root / "key.json"
            html_path = root / "review.html"
            evaluation._write_text(
                html_path, evaluation._review_html(review_id, public_pairs)
            )
            evaluation._write_json(
                key_path,
                {
                    "schema_version": evaluation.REVIEW_KEY_VERSION,
                    "review_id": review_id,
                    "seed": seed,
                    "manifest_ids": [],
                    "pairs": pairs,
                    "public_bundle_sha256": public_digest,
                    "html_template_sha256": template_digest,
                    "html_path": str(html_path.resolve()),
                    "html_sha256": evaluation._sha256_file(html_path),
                },
            )
            rating_paths = []
            for reviewer, preference in enumerate(("left", "tie", "tie"), 1):
                scores = {
                    axis: {"left": 4, "right": 3}
                    for axis in evaluation.RATING_AXES
                }
                path = root / ("ratings-%d.json" % reviewer)
                evaluation._write_json(
                    path,
                    {
                        "schema_version": evaluation.REVIEW_VERSION,
                        "review_id": review_id,
                        "public_bundle_sha256": public_digest,
                        "reviewer": reviewer,
                        "ratings": {
                            "pair-one": {
                                "scores": scores,
                                "preference": preference,
                            }
                        },
                    },
                )
                rating_paths.append(path)
            summary = evaluation._human_summary(rating_paths, key_path)
            self.assertEqual(summary["preference"]["ties"], 1)
            with self.assertRaisesRegex(evaluation.ValidationError, "paths must be unique"):
                evaluation._human_summary([rating_paths[0], rating_paths[0]], key_path)


class AnalysisSafetyTests(unittest.TestCase):
    def test_incomplete_144_run_experiment_has_no_recommendation(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            candidate_dir, screen, confirm = write_fixture_tree(root / "fixtures")
            screen_path, _ = evaluation.create_manifest(
                "screen",
                seed=31,
                output=root / "screen" / "manifest.json",
                candidate_dir=candidate_dir,
                screen_cases=screen,
                confirm_cases=confirm,
            )
            confirm_path, _ = evaluation.create_manifest(
                "confirm",
                seed=32,
                output=root / "confirm" / "manifest.json",
                candidate_dir=candidate_dir,
                screen_cases=screen,
                confirm_cases=confirm,
                screen_manifest=screen_path,
            )
            report = evaluation.analyze([screen_path, confirm_path])
            self.assertEqual(report["automatic"]["runs_expected"], 144)
            self.assertFalse(report["automatic"]["execution_complete"])
            self.assertIsNone(report["decision"]["recommendation"])
            self.assertEqual(report["decision"]["status"], "inconclusive")


class ExecutionContractTests(unittest.TestCase):
    def test_codex_argv_uses_fixed_isolated_execution_contract(self):
        argv = evaluation._codex_exec_argv(
            "developer sentinel", Path("/tmp/final.md"), "/tmp/work"
        )
        for expected in (
            "--ignore-user-config",
            "--strict-config",
            "--ignore-rules",
            "--ephemeral",
            "--json",
            "gpt-5.6-sol",
            "read-only",
            'model_reasoning_effort="xhigh"',
            'service_tier="priority"',
            'approval_policy="never"',
        ):
            self.assertIn(expected, argv)
        self.assertEqual(argv[-1], "-")

    def test_trace_contamination_checks_tool_payloads_not_messages(self):
        path = "/tmp/fluent-languages/fluent-korean/SKILL.md"
        message_only = [
            {"type": "item.completed", "item": {"type": "agent_message", "text": path}}
        ]
        tool_read = [
            {
                "type": "item.started",
                "item": {"type": "command_execution", "command": "cat " + path},
            }
        ]
        self.assertEqual(evaluation.trace_contamination(message_only), [])
        self.assertTrue(evaluation.trace_contamination(tool_read))


class ReviewBundleTests(unittest.TestCase):
    def test_review_html_is_blind_and_key_is_separate(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            fixtures = root / "fixtures"
            candidate_dir, screen, confirm = write_fixture_tree(fixtures)
            manifest_path = root / "artifacts" / "manifest.json"
            _, manifest = evaluation.create_manifest(
                "screen",
                seed=7,
                output=manifest_path,
                candidate_dir=candidate_dir,
                screen_cases=screen,
                confirm_cases=confirm,
            )
            task_id = manifest["cases"][0]["id"]
            for candidate_id in ("A", "B"):
                for repetition in (1, 2):
                    run = next(
                        row
                        for row in manifest["runs"]
                        if row["case_id"] == task_id
                        and row["candidate_id"] == candidate_id
                        and row["repetition"] == repetition
                    )
                    run_dir = manifest_path.parent / "runs" / run["run_id"]
                    output_path = run_dir / "attempt-01.md"
                    output_path.parent.mkdir(parents=True, exist_ok=True)
                    output_path.write_text(
                        "중립적인 비교 출력", encoding="utf-8"
                    )
                    trace_path = run_dir / "attempt-01.trace.jsonl"
                    stderr_path = run_dir / "attempt-01.stderr.txt"
                    command_path = run_dir / "attempt-01.command.json"
                    trace_path.write_text('{"type":"turn.completed"}\n', encoding="utf-8")
                    stderr_path.write_text("", encoding="utf-8")
                    fake_cwd = str((root / "isolated-workspace").resolve())
                    developer = manifest["candidates"][candidate_id][
                        "developer_instructions"
                    ]
                    evaluation._write_json(
                        command_path,
                        {
                            "argv": evaluation._codex_exec_argv(
                                developer, output_path, fake_cwd
                            ),
                            "cwd": fake_cwd,
                            "codex_home_isolated": True,
                            "stdin_sha256": evaluation._sha256_bytes(
                                evaluation.render_user_prompt(
                                    next(
                                        case
                                        for case in manifest["cases"]
                                        if case["id"] == task_id
                                    )
                                ).encode("utf-8")
                            ),
                        },
                    )
                    check = evaluation.hard_check(
                        next(case for case in manifest["cases"] if case["id"] == task_id),
                        "중립적인 비교 출력",
                    )
                    attempt = {
                        "attempt": 1,
                        "status": "pass",
                        "reason": "hard_checks_pass",
                        "returncode": 0,
                        "timed_out": False,
                        "spawn_error": None,
                        "output_path": str(output_path),
                        "output_sha256": evaluation._sha256_file(output_path),
                        "trace_path": str(trace_path),
                        "trace_sha256": evaluation._sha256_file(trace_path),
                        "stderr_path": str(stderr_path),
                        "stderr_sha256": evaluation._sha256_file(stderr_path),
                        "command_path": str(command_path),
                        "command_sha256": evaluation._sha256_file(command_path),
                        "trace_errors": [],
                        "contamination": [],
                        "usage": None,
                        "check": check,
                    }
                    evaluation._write_json(
                        run_dir / "result.json",
                        {
                            "schema_version": evaluation.RUN_RESULT_VERSION,
                            "manifest_id": manifest["manifest_id"],
                            "run_id": run["run_id"],
                            "case_id": task_id,
                            "candidate_id": candidate_id,
                            "repetition": repetition,
                            "status": "pass",
                            "reason": "hard_checks_pass",
                            "attempts": [attempt],
                            "latest": dict(attempt),
                            "updated_at": evaluation._utc_now(),
                        },
                    )
            html_path = root / "review" / "review.html"
            _, key_path, key = evaluation.create_review_bundle(
                [manifest_path],
                output=html_path,
                seed=11,
            )
            html = html_path.read_text(encoding="utf-8")
            key_text = key_path.read_text(encoding="utf-8")
            for secret in (
                "COMMON_SECRET",
                "BASELINE_SECRET",
                "IM_ONLY_SECRET",
                "HYBRID_SECRET",
                "candidate_id",
            ):
                self.assertNotIn(secret, html)
            self.assertIn("localStorage", html)
            self.assertIn("JSON 다운로드", html)
            self.assertIn("technical_accuracy", html)
            self.assertEqual(len(key["pairs"]), 1)
            repetition_lineage = next(iter(key["pairs"].values()))["repetitions"]
            self.assertEqual([row["repetition"] for row in repetition_lineage], [1, 2])
            self.assertRegex(
                repetition_lineage[0]["left"]["output_sha256"], r"^[0-9a-f]{64}$"
            )
            self.assertRegex(key_text, r'"left": "[AB]"')
            self.assertRegex(key_text, r'"right": "[AB]"')
            self.assertNotEqual(html_path, key_path)
            self.assertEqual(key_path.parent.name, "private")

            html_path.write_text(html + "\n", encoding="utf-8")
            with self.assertRaisesRegex(evaluation.ValidationError, "HTML hash mismatch"):
                evaluation._load_review_key(key_path)
            evaluation._write_text(html_path, html)

            first_run = next(
                row
                for row in manifest["runs"]
                if row["case_id"] == task_id and row["candidate_id"] == "A"
            )
            first_result_path = (
                manifest_path.parent / "runs" / first_run["run_id"] / "result.json"
            )
            clean_result_text = first_result_path.read_text(encoding="utf-8")
            contaminated_result = json.loads(clean_result_text)
            trace_path = Path(contaminated_result["latest"]["trace_path"])
            clean_trace = trace_path.read_text(encoding="utf-8")
            trace_path.write_text(
                '{"type":"item.started","item":{"type":"command_execution",'
                '"command":"cat /tmp/fluent-korean/SKILL.md"}}\n'
                '{"type":"turn.completed"}\n',
                encoding="utf-8",
            )
            trace_hash = evaluation._sha256_file(trace_path)
            contaminated_result["latest"]["trace_sha256"] = trace_hash
            contaminated_result["attempts"][-1]["trace_sha256"] = trace_hash
            evaluation._write_json(first_result_path, contaminated_result)
            with self.assertRaisesRegex(evaluation.ValidationError, "attempt status is stale"):
                evaluation.create_review_bundle(
                    [manifest_path],
                    output=root / "review-contaminated" / "review.html",
                    key_output=root / "review-contaminated" / "review-key.json",
                    seed=12,
                )
            evaluation._write_text(trace_path, clean_trace)
            evaluation._write_text(first_result_path, clean_result_text)

            tampered_output = (
                manifest_path.parent
                / "runs"
                / first_run["run_id"]
                / "attempt-01.md"
            )
            tampered_output.write_text("수정된 출력", encoding="utf-8")
            with self.assertRaisesRegex(evaluation.ValidationError, "hash mismatch"):
                evaluation.create_review_bundle(
                    [manifest_path],
                    output=root / "review-two" / "review.html",
                    key_output=root / "review-two" / "review-key.json",
                    seed=12,
                )

            rerun_result = json.loads(first_result_path.read_text(encoding="utf-8"))
            rerun_hash = evaluation._sha256_file(tampered_output)
            rerun_check = evaluation.hard_check(
                next(case for case in manifest["cases"] if case["id"] == task_id),
                "수정된 출력",
            )
            rerun_result["latest"]["output_sha256"] = rerun_hash
            rerun_result["latest"]["check"] = rerun_check
            rerun_result["attempts"][-1] = dict(rerun_result["latest"])
            evaluation._write_json(first_result_path, rerun_result)
            pair_id = next(iter(key["pairs"]))
            ratings_path = root / "ratings.json"
            evaluation._write_json(
                ratings_path,
                {
                    "schema_version": evaluation.REVIEW_VERSION,
                    "review_id": key["review_id"],
                    "public_bundle_sha256": key["public_bundle_sha256"],
                    "ratings": {
                        pair_id: {
                            "scores": {
                                axis: {"left": 3, "right": 3}
                                for axis in evaluation.RATING_AXES
                            },
                            "preference": "tie",
                        }
                    },
                },
            )
            with self.assertRaisesRegex(evaluation.ValidationError, "lineage is stale"):
                evaluation.analyze(
                    [manifest_path], [ratings_path], key_path
                )


if __name__ == "__main__":
    unittest.main()
