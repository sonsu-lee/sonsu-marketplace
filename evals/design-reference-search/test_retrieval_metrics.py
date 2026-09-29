from __future__ import annotations

import importlib.util
import json
import math
import subprocess
import tempfile
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
SCRIPT = ROOT / "evals" / "design-reference-search" / "retrieval_metrics.py"
SPEC = importlib.util.spec_from_file_location("retrieval_metrics", SCRIPT)
assert SPEC is not None and SPEC.loader is not None
MODULE = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(MODULE)


def make_gold(cases: list[dict]) -> dict:
    return {
        "schema_version": "design-reference-retrieval-gold-v1",
        "grade_semantics": {
            "2": "exact match for the query",
            "1": "partial or related match",
            "0": "irrelevant",
        },
        "cases": cases,
    }


def make_run(cases: list[dict], system: str = "find-references@test") -> dict:
    return {
        "schema_version": "design-reference-retrieval-run-v1",
        "system": system,
        "cases": cases,
    }


def make_floors(splits: dict, k: int = 5) -> dict:
    return {
        "schema_version": "design-reference-retrieval-floors-v1",
        "status": "provisional-baseline-regression-gate",
        "k": k,
        "splits": splits,
    }


def run_cli(command: str, extra: list[str] | None = None, **payloads: dict) -> subprocess.CompletedProcess[str]:
    extra = list(extra or [])
    with tempfile.TemporaryDirectory() as tmp:
        cli = [command]
        for name, payload in payloads.items():
            path = Path(tmp) / f"{name}.json"
            path.write_text(json.dumps(payload), encoding="utf-8")
            cli += [f"--{name}", str(path)]
        cli += extra
        return subprocess.run(
            ["python3", str(SCRIPT), *cli],
            cwd=ROOT,
            text=True,
            capture_output=True,
            check=False,
        )


class NormalizeLocatorTests(unittest.TestCase):
    def test_strips_utm_and_known_tracking_params(self) -> None:
        for param in ("utm_source", "utm_campaign", "ref", "ref_src", "source", "fbclid", "gclid", "mc_cid", "mc_eid"):
            with self.subTest(param=param):
                self.assertEqual(
                    MODULE.normalize_locator(f"https://example.com/a?{param}=x"),
                    "https://example.com/a",
                )

    def test_drops_leading_www_and_lowercases_host_and_scheme(self) -> None:
        self.assertEqual(
            MODULE.normalize_locator("HTTPS://WWW.Example.com/Path"),
            "https://example.com/Path",
        )

    def test_drops_default_ports_but_keeps_nondefault(self) -> None:
        self.assertEqual(MODULE.normalize_locator("http://example.com:80/a"), "http://example.com/a")
        self.assertEqual(MODULE.normalize_locator("https://example.com:443/a"), "https://example.com/a")
        self.assertEqual(
            MODULE.normalize_locator("https://example.com:8443/a"),
            "https://example.com:8443/a",
        )

    def test_drops_fragment(self) -> None:
        self.assertEqual(MODULE.normalize_locator("https://example.com/a#section"), "https://example.com/a")

    def test_strips_trailing_slash_and_root_path_becomes_empty(self) -> None:
        self.assertEqual(MODULE.normalize_locator("https://example.com/a/"), "https://example.com/a")
        self.assertEqual(MODULE.normalize_locator("https://example.com/"), "https://example.com")

    def test_sorts_remaining_query_params(self) -> None:
        self.assertEqual(
            MODULE.normalize_locator("https://example.com/a?b=2&a=1"),
            "https://example.com/a?a=1&b=2",
        )

    def test_provider_scoped_id_lowercases_only_prefix(self) -> None:
        self.assertEqual(MODULE.normalize_locator("Mobbin:screen/123"), "mobbin:screen/123")
        self.assertEqual(MODULE.normalize_locator("  Dribbble:Shot/ABC  "), "dribbble:Shot/ABC")

    def test_matches_the_reference_set_validator(self) -> None:
        validator_path = ROOT / "shared" / "design-quality" / "validate_design_quality.py"
        spec = importlib.util.spec_from_file_location("validate_design_quality_for_metrics", validator_path)
        assert spec is not None and spec.loader is not None
        validator = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(validator)
        self.assertEqual(Path(MODULE.normalize_locator.__code__.co_filename).name, "validate_design_quality.py")
        for locator in ("https://www.Mobbin.com:443/x/?utm_source=a&b=2#f", "Mobbin:screen/1", "http://[::1"):
            self.assertEqual(MODULE.normalize_locator(locator), validator.normalize_locator(locator))

    def test_full_example_from_spec(self) -> None:
        self.assertEqual(
            MODULE.normalize_locator("https://Mobbin.com/x?utm_source=a#f"),
            "https://mobbin.com/x",
        )


class HandComputedMetricsTests(unittest.TestCase):
    @staticmethod
    def _expected_dcg(grades: list[int]) -> float:
        return sum((2 ** grade - 1) / math.log2(rank + 1) for rank, grade in enumerate(grades, start=1))

    def test_ndcg_hit_precision_mrr_and_app_diversity_on_synthetic_case(self) -> None:
        gold = make_gold(
            [
                {
                    "id": "screen-login-ios",
                    "split": "held_out",
                    "kind": "screen",
                    "query": "sign in screen with passkey option",
                    "judgments": [
                        {"locator": "mobbin:screen/a", "grade": 2},
                        {"locator": "mobbin:screen/b", "grade": 1},
                        {"locator": "mobbin:screen/c", "grade": 0},
                    ],
                }
            ]
        )
        run = make_run(
            [
                {
                    "id": "screen-login-ios",
                    "status": "selected",
                    "results": [
                        {"locator": "mobbin:screen/b", "app": "AppX"},
                        {"locator": "mobbin:screen/a", "app": "AppX"},
                        {"locator": "mobbin:screen/d", "app": "AppY"},
                    ],
                }
            ]
        )
        report = MODULE.compute_report(gold, run, k=3, splits=["held_out"])
        metrics = report["held_out"]

        expected_grades = [1, 2, 0]
        expected_ideal = [2, 1, 0]
        expected_ndcg = self._expected_dcg(expected_grades) / self._expected_dcg(expected_ideal)

        self.assertAlmostEqual(metrics["ndcg_at_k"]["value"], expected_ndcg)
        self.assertEqual(metrics["ndcg_at_k"]["n"], 1)
        self.assertAlmostEqual(metrics["hit_at_k"]["value"], 1.0)
        self.assertAlmostEqual(metrics["precision_at_k"]["value"], 2 / 3)
        self.assertAlmostEqual(metrics["mrr"]["value"], 1 / 2)
        self.assertAlmostEqual(metrics["distinct_app_ratio"]["value"], 2 / 3)
        self.assertAlmostEqual(metrics["unjudged_rate"]["value"], 1 / 3)
        self.assertEqual(metrics["missing_cases"], [])


class DedupTests(unittest.TestCase):
    def test_duplicate_locators_are_deduped_before_truncation(self) -> None:
        gold = make_gold(
            [
                {
                    "id": "case-dedup",
                    "split": "held_out",
                    "kind": "component",
                    "query": "primary button component",
                    "judgments": [
                        {"locator": "https://example.com/x", "grade": 2},
                        {"locator": "https://example.com/y", "grade": 0},
                    ],
                }
            ]
        )
        run = make_run(
            [
                {
                    "id": "case-dedup",
                    "status": "selected",
                    "results": [
                        {"locator": "https://Example.com/x?utm_source=a"},
                        {"locator": "https://example.com/x/"},
                        {"locator": "https://example.com/x"},
                        {"locator": "https://example.com/y"},
                    ],
                }
            ]
        )
        report = MODULE.compute_report(gold, run, k=2, splits=["held_out"])
        metrics = report["held_out"]
        # without dedup the top-2 raw results would both be the same grade-2 locator (precision 1.0)
        self.assertAlmostEqual(metrics["precision_at_k"]["value"], 0.5)
        self.assertAlmostEqual(metrics["hit_at_k"]["value"], 1.0)
        self.assertAlmostEqual(metrics["mrr"]["value"], 1.0)
        self.assertAlmostEqual(metrics["unjudged_rate"]["value"], 0.0)


class OutOfScopeAbstentionTests(unittest.TestCase):
    def _gold(self) -> dict:
        return make_gold(
            [
                {
                    "id": "oos-1",
                    "split": "held_out",
                    "kind": "out_of_scope",
                    "query": "write a poem about buttons",
                    "judgments": [],
                }
            ]
        )

    def test_correct_abstention_scores_one(self) -> None:
        run = make_run([{"id": "oos-1", "status": "no_verified_match", "results": []}])
        report = MODULE.compute_report(self._gold(), run, k=5, splits=["held_out"])
        self.assertAlmostEqual(report["held_out"]["abstention"]["value"], 1.0)
        self.assertEqual(report["held_out"]["abstention"]["n"], 1)

    def test_failure_to_abstain_scores_zero(self) -> None:
        run = make_run(
            [{"id": "oos-1", "status": "selected", "results": [{"locator": "https://example.com/a"}]}]
        )
        report = MODULE.compute_report(self._gold(), run, k=5, splits=["held_out"])
        self.assertAlmostEqual(report["held_out"]["abstention"]["value"], 0.0)


class MissingCaseTests(unittest.TestCase):
    def test_missing_out_of_scope_case_is_not_counted_as_abstention(self) -> None:
        gold = make_gold(
            [
                {
                    "id": "oos-missing",
                    "split": "held_out",
                    "kind": "out_of_scope",
                    "query": "irrelevant request",
                    "judgments": [],
                }
            ]
        )
        run = make_run([])
        report = MODULE.compute_report(gold, run, k=5, splits=["held_out"])
        self.assertAlmostEqual(report["held_out"]["abstention"]["value"], 0.0)
        self.assertEqual(report["held_out"]["missing_cases"], ["oos-missing"])

    def test_missing_retrieval_case_scores_zero_and_is_listed(self) -> None:
        gold = make_gold(
            [
                {
                    "id": "screen-missing",
                    "split": "held_out",
                    "kind": "screen",
                    "query": "a query",
                    "judgments": [{"locator": "mobbin:screen/z", "grade": 2}],
                }
            ]
        )
        run = make_run([])
        report = MODULE.compute_report(gold, run, k=5, splits=["held_out"])
        metrics = report["held_out"]
        self.assertAlmostEqual(metrics["ndcg_at_k"]["value"], 0.0)
        self.assertAlmostEqual(metrics["hit_at_k"]["value"], 0.0)
        self.assertAlmostEqual(metrics["precision_at_k"]["value"], 0.0)
        self.assertAlmostEqual(metrics["mrr"]["value"], 0.0)
        self.assertEqual(metrics["distinct_app_ratio"]["n"], 0)
        self.assertEqual(metrics["unjudged_rate"]["n"], 0)
        self.assertEqual(metrics["missing_cases"], ["screen-missing"])


class SplitFilteringTests(unittest.TestCase):
    def _gold(self) -> dict:
        return make_gold(
            [
                {
                    "id": "cal-1",
                    "split": "calibration",
                    "kind": "screen",
                    "query": "calibration case",
                    "judgments": [{"locator": "mobbin:screen/a", "grade": 2}],
                },
                {
                    "id": "held-1",
                    "split": "held_out",
                    "kind": "screen",
                    "query": "held out case",
                    "judgments": [{"locator": "mobbin:screen/b", "grade": 2}],
                },
            ]
        )

    def _run(self) -> dict:
        return make_run(
            [
                {"id": "cal-1", "status": "selected", "results": [{"locator": "mobbin:screen/a"}]},
                {"id": "held-1", "status": "selected", "results": [{"locator": "mobbin:screen/b"}]},
            ]
        )

    def test_default_reports_all_three_splits(self) -> None:
        result = run_cli("score", gold=self._gold(), run=self._run())
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
        payload = json.loads(result.stdout.strip().splitlines()[0])
        self.assertEqual(set(payload), {"k", "calibration", "held_out", "all"})

    def test_split_flag_restricts_output(self) -> None:
        result = run_cli("score", extra=["--split", "calibration"], gold=self._gold(), run=self._run())
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
        payload = json.loads(result.stdout.strip().splitlines()[0])
        self.assertEqual(set(payload), {"k", "calibration"})


class FloorsTests(unittest.TestCase):
    def _gold(self) -> dict:
        return make_gold(
            [
                {
                    "id": "held-1",
                    "split": "held_out",
                    "kind": "screen",
                    "query": "held out case",
                    "judgments": [{"locator": "mobbin:screen/a", "grade": 2}],
                }
            ]
        )

    def _run(self) -> dict:
        return make_run(
            [{"id": "held-1", "status": "selected", "results": [{"locator": "mobbin:screen/a"}]}]
        )

    def test_floors_pass(self) -> None:
        floors = make_floors({"held_out": {"ndcg_at_k": 0.5, "hit_at_k": 0.5}})
        result = run_cli("score", gold=self._gold(), run=self._run(), floors=floors)
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
        self.assertNotIn("ERROR", result.stdout)

    def test_floors_fail_reports_metric_and_exits_nonzero(self) -> None:
        floors = make_floors({"held_out": {"ndcg_at_k": 1.5}})
        result = run_cli("score", gold=self._gold(), run=self._run(), floors=floors)
        self.assertNotEqual(result.returncode, 0)
        self.assertIn("ERROR: held_out.ndcg_at_k", result.stdout)
        self.assertIn("below floor 1.5", result.stdout)
        self.assertNotIn("Traceback", result.stderr)

    def test_floors_k_mismatch_with_explicit_k_is_an_error(self) -> None:
        floors = make_floors({"held_out": {"ndcg_at_k": 0.5}}, k=5)
        result = run_cli("score", extra=["--k", "3"], gold=self._gold(), run=self._run(), floors=floors)
        self.assertNotEqual(result.returncode, 0)
        self.assertIn("ERROR", result.stdout)
        self.assertNotIn("Traceback", result.stderr)

    def test_unjudged_rate_is_a_diagnostic_not_a_floor(self) -> None:
        floors = make_floors({"held_out": {"unjudged_rate": 0.0}})
        result = run_cli("score", gold=self._gold(), run=self._run(), floors=floors)
        self.assertNotEqual(result.returncode, 0)
        self.assertIn("splits.held_out has unknown metric: unjudged_rate", result.stdout)

    def test_unknown_floor_metric_name_is_an_error(self) -> None:
        floors = make_floors({"held_out": {"bogus_metric": 0.5}})
        result = run_cli("score", gold=self._gold(), run=self._run(), floors=floors)
        self.assertNotEqual(result.returncode, 0)
        self.assertIn("unknown metric", result.stdout)
        self.assertNotIn("Traceback", result.stderr)


class MalformedGoldTests(unittest.TestCase):
    def test_valid_gold_passes(self) -> None:
        gold = make_gold(
            [
                {
                    "id": "screen-1",
                    "split": "held_out",
                    "kind": "screen",
                    "query": "a query",
                    "judgments": [{"locator": "mobbin:screen/a", "grade": 2}],
                }
            ]
        )
        result = run_cli("validate", gold=gold)
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
        self.assertIn("OK: validate", result.stdout)

    def test_boolean_grade_is_rejected(self) -> None:
        gold = make_gold(
            [
                {
                    "id": "screen-1",
                    "split": "held_out",
                    "kind": "screen",
                    "query": "a query",
                    "judgments": [{"locator": "mobbin:screen/a", "grade": True}],
                }
            ]
        )
        result = run_cli("validate", gold=gold)
        self.assertNotEqual(result.returncode, 0)
        self.assertIn("ERROR", result.stdout)
        self.assertIn("grade", result.stdout)
        self.assertNotIn("Traceback", result.stderr)

    def test_duplicate_case_ids_are_rejected(self) -> None:
        case = {
            "id": "dup",
            "split": "held_out",
            "kind": "screen",
            "query": "a query",
            "judgments": [{"locator": "mobbin:screen/a", "grade": 2}],
        }
        gold = make_gold([case, dict(case)])
        result = run_cli("validate", gold=gold)
        self.assertNotEqual(result.returncode, 0)
        self.assertIn("duplicate case id", result.stdout)
        self.assertNotIn("Traceback", result.stderr)

    def test_out_of_scope_with_judgments_is_rejected(self) -> None:
        gold = make_gold(
            [
                {
                    "id": "oos-1",
                    "split": "held_out",
                    "kind": "out_of_scope",
                    "query": "write a poem",
                    "judgments": [{"locator": "mobbin:screen/a", "grade": 1}],
                }
            ]
        )
        result = run_cli("validate", gold=gold)
        self.assertNotEqual(result.returncode, 0)
        self.assertIn("out_of_scope", result.stdout)
        self.assertNotIn("Traceback", result.stderr)

    def test_retrieval_case_without_grade_two_is_rejected(self) -> None:
        gold = make_gold(
            [
                {
                    "id": "screen-1",
                    "split": "held_out",
                    "kind": "screen",
                    "query": "a query",
                    "judgments": [{"locator": "mobbin:screen/a", "grade": 1}],
                }
            ]
        )
        result = run_cli("validate", gold=gold)
        self.assertNotEqual(result.returncode, 0)
        self.assertIn("grade 2", result.stdout)
        self.assertNotIn("Traceback", result.stderr)


if __name__ == "__main__":
    unittest.main()
