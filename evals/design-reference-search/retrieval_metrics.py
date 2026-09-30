#!/usr/bin/env python3
"""Score a design reference retrieval run against curated gold judgments."""

from __future__ import annotations

import argparse
import json
import math
import sys
from pathlib import Path
from typing import Any

sys.dont_write_bytecode = True
sys.path.insert(0, str(Path(__file__).resolve().parents[2] / "shared" / "design-quality"))
from validate_design_quality import normalize_locator, reference_locator  # noqa: E402


GOLD_SCHEMA_VERSION = "design-reference-retrieval-gold-v1"
RUN_SCHEMA_VERSION = "design-reference-retrieval-run-v1"
FLOORS_SCHEMA_VERSION = "design-reference-retrieval-floors-v1"

GOLD_FIELDS = {"schema_version", "grade_semantics", "cases"}
CASE_FIELDS = {"id", "split", "kind", "query", "judgments", "notes"}
REQUIRED_CASE_FIELDS = {"id", "split", "kind", "query", "judgments"}
JUDGMENT_FIELDS = {"locator", "grade"}
SPLITS = {"calibration", "held_out"}
KINDS = {
    "style", "screen", "flow", "component", "named_app", "platform", "typo", "out_of_scope",
}

RUN_FIELDS = {"schema_version", "system", "cases"}
RUN_CASE_FIELDS = {"id", "status", "results"}
RESULT_FIELDS = {"locator", "app"}
RUN_STATUSES = {"selected", "no_verified_match"}

FLOORS_FIELDS = {"schema_version", "status", "k", "splits"}

RETRIEVAL_METRIC_NAMES = (
    "ndcg_at_k", "hit_at_k", "precision_at_k", "mrr", "distinct_app_ratio", "unjudged_rate",
)
FLOOR_METRIC_NAMES = (set(RETRIEVAL_METRIC_NAMES) - {"unjudged_rate"}) | {"abstention"}
ALL_SPLIT_NAMES = ("calibration", "held_out", "all")

DEFAULT_K = 5
TOLERANCE = 1e-12


def non_empty_string(value: Any) -> bool:
    return isinstance(value, str) and bool(value.strip())


def is_finite_number(value: Any) -> bool:
    if isinstance(value, bool) or not isinstance(value, (int, float)):
        return False
    try:
        return math.isfinite(value)
    except OverflowError:
        return False


def reject_unknown_fields(value: dict[str, Any], allowed: set[str], context: str, errors: list[str]) -> None:
    unknown = sorted(set(value) - allowed)
    if unknown:
        errors.append(f"{context} has unknown fields: {unknown}")


def require_fields(value: dict[str, Any], required: set[str], context: str, errors: list[str]) -> None:
    missing = sorted(required - set(value))
    if missing:
        errors.append(f"{context} missing required fields: {missing}")


def load_json(path: Path, errors: list[str]) -> Any:
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except OSError as error:
        errors.append(f"{path}: unable to read: {error}")
    except json.JSONDecodeError as error:
        errors.append(f"{path}: invalid JSON: {error}")
    return None


def validate_gold(payload: Any) -> list[str]:
    errors: list[str] = []
    if not isinstance(payload, dict):
        return ["gold must be a JSON object"]
    reject_unknown_fields(payload, GOLD_FIELDS, "gold", errors)
    require_fields(payload, GOLD_FIELDS, "gold", errors)
    if payload.get("schema_version") != GOLD_SCHEMA_VERSION:
        errors.append(f"schema_version must be {GOLD_SCHEMA_VERSION}")
    grade_semantics = payload.get("grade_semantics")
    if not isinstance(grade_semantics, dict) or not all(
        non_empty_string(grade_semantics.get(key)) for key in ("0", "1", "2")
    ):
        errors.append('grade_semantics must map "0", "1", "2" to non-empty strings')
    cases = payload.get("cases")
    if not isinstance(cases, list) or not cases:
        errors.append("cases must be a non-empty array")
        return errors
    seen_ids: set[str] = set()
    for index, case in enumerate(cases):
        context = f"cases[{index}]"
        if not isinstance(case, dict):
            errors.append(f"{context} must be an object")
            continue
        reject_unknown_fields(case, CASE_FIELDS, context, errors)
        require_fields(case, REQUIRED_CASE_FIELDS, context, errors)
        case_id = case.get("id")
        if not non_empty_string(case_id):
            errors.append(f"{context}.id must be a non-empty string")
        elif case_id in seen_ids:
            errors.append(f"duplicate case id: {case_id}")
        else:
            seen_ids.add(case_id)
        if case.get("split") not in SPLITS:
            errors.append(f"{context}.split must be one of {sorted(SPLITS)}")
        kind = case.get("kind")
        if kind not in KINDS:
            errors.append(f"{context}.kind must be one of {sorted(KINDS)}")
        if not non_empty_string(case.get("query")):
            errors.append(f"{context}.query must be a non-empty string")
        if "notes" in case and not isinstance(case["notes"], str):
            errors.append(f"{context}.notes must be a string")
        judgments = case.get("judgments")
        if not isinstance(judgments, list):
            errors.append(f"{context}.judgments must be an array")
            judgments = []
        normalized_locators: set[str] = set()
        has_grade_2 = False
        for j_index, judgment in enumerate(judgments):
            j_context = f"{context}.judgments[{j_index}]"
            if not isinstance(judgment, dict):
                errors.append(f"{j_context} must be an object")
                continue
            reject_unknown_fields(judgment, JUDGMENT_FIELDS, j_context, errors)
            require_fields(judgment, JUDGMENT_FIELDS, j_context, errors)
            locator = judgment.get("locator")
            if not reference_locator(locator, allow_relative_path=False):
                errors.append(f"{j_context}.locator must be an HTTP(S) URL or safe provider ID")
            else:
                normalized = normalize_locator(locator)
                if normalized in normalized_locators:
                    errors.append(f"{context} has duplicate normalized locator: {normalized}")
                else:
                    normalized_locators.add(normalized)
            grade = judgment.get("grade")
            if isinstance(grade, bool) or grade not in (0, 1, 2):
                errors.append(f"{j_context}.grade must be an integer 0, 1, or 2")
            elif grade == 2:
                has_grade_2 = True
        if kind == "out_of_scope":
            if judgments:
                errors.append(f"{context} kind out_of_scope must have empty judgments")
        else:
            if not judgments:
                errors.append(f"{context} must have at least one judgment")
            elif not has_grade_2:
                errors.append(f"{context} must have at least one judgment with grade 2")
    return errors


def validate_run(payload: Any, gold_ids: set[str]) -> list[str]:
    errors: list[str] = []
    if not isinstance(payload, dict):
        return ["run must be a JSON object"]
    reject_unknown_fields(payload, RUN_FIELDS, "run", errors)
    require_fields(payload, RUN_FIELDS, "run", errors)
    if payload.get("schema_version") != RUN_SCHEMA_VERSION:
        errors.append(f"schema_version must be {RUN_SCHEMA_VERSION}")
    if not non_empty_string(payload.get("system")):
        errors.append("system must be a non-empty string")
    cases = payload.get("cases")
    if not isinstance(cases, list):
        errors.append("cases must be an array")
        return errors
    seen_ids: set[str] = set()
    for index, case in enumerate(cases):
        context = f"cases[{index}]"
        if not isinstance(case, dict):
            errors.append(f"{context} must be an object")
            continue
        reject_unknown_fields(case, RUN_CASE_FIELDS, context, errors)
        require_fields(case, RUN_CASE_FIELDS, context, errors)
        case_id = case.get("id")
        if not non_empty_string(case_id):
            errors.append(f"{context}.id must be a non-empty string")
        else:
            if case_id in seen_ids:
                errors.append(f"duplicate run case id: {case_id}")
            seen_ids.add(case_id)
            if case_id not in gold_ids:
                errors.append(f"{context}.id {case_id!r} is not a gold case id")
        status = case.get("status")
        if status not in RUN_STATUSES:
            errors.append(f"{context}.status must be one of {sorted(RUN_STATUSES)}")
        results = case.get("results")
        if not isinstance(results, list):
            errors.append(f"{context}.results must be an array")
            results = []
        else:
            for r_index, result in enumerate(results):
                r_context = f"{context}.results[{r_index}]"
                if not isinstance(result, dict):
                    errors.append(f"{r_context} must be an object")
                    continue
                reject_unknown_fields(result, RESULT_FIELDS, r_context, errors)
                if not reference_locator(result.get("locator"), allow_relative_path=False):
                    errors.append(f"{r_context}.locator must be an HTTP(S) URL or safe provider ID")
                if "app" in result and result["app"] is not None and not isinstance(result["app"], str):
                    errors.append(f"{r_context}.app must be a string")
        if status == "no_verified_match" and results:
            errors.append(f"{context} status no_verified_match must have empty results")
    return errors


def validate_floors(payload: Any) -> list[str]:
    errors: list[str] = []
    if not isinstance(payload, dict):
        return ["floors must be a JSON object"]
    reject_unknown_fields(payload, FLOORS_FIELDS, "floors", errors)
    require_fields(payload, FLOORS_FIELDS, "floors", errors)
    if payload.get("schema_version") != FLOORS_SCHEMA_VERSION:
        errors.append(f"schema_version must be {FLOORS_SCHEMA_VERSION}")
    if not non_empty_string(payload.get("status")):
        errors.append("status must be a non-empty string")
    k = payload.get("k")
    if not isinstance(k, int) or isinstance(k, bool) or k <= 0:
        errors.append("k must be a positive integer")
    splits = payload.get("splits")
    if not isinstance(splits, dict) or not splits:
        errors.append("splits must be a non-empty object")
        splits = {}
    for split_name, metrics in splits.items():
        if split_name not in ALL_SPLIT_NAMES:
            errors.append(f"splits has unknown split: {split_name}")
            continue
        if not isinstance(metrics, dict) or not metrics:
            errors.append(f"splits.{split_name} must be a non-empty object")
            continue
        for metric_name, value in metrics.items():
            if metric_name not in FLOOR_METRIC_NAMES:
                errors.append(f"splits.{split_name} has unknown metric: {metric_name}")
                continue
            if not is_finite_number(value):
                errors.append(f"splits.{split_name}.{metric_name} must be a finite number")
    return errors


def _dcg(grades: list[int]) -> float:
    total = 0.0
    for rank, grade in enumerate(grades, start=1):
        total += (2 ** grade - 1) / math.log2(rank + 1)
    return total


def _dedup_truncate(results: list[dict[str, Any]], k: int) -> list[tuple[str, Any]]:
    seen: set[str] = set()
    deduped: list[tuple[str, Any]] = []
    for item in results:
        locator = item.get("locator")
        if not isinstance(locator, str):
            continue
        normalized = normalize_locator(locator)
        if normalized in seen:
            continue
        seen.add(normalized)
        deduped.append((normalized, item.get("app")))
    return deduped[:k]


def score_retrieval_case(
    judgments: dict[str, int], results: list[dict[str, Any]], k: int
) -> dict[str, float | None]:
    truncated = _dedup_truncate(results, k)
    grades = [judgments.get(locator, 0) for locator, _app in truncated]
    judged = [locator in judgments for locator, _app in truncated]
    dcg_value = _dcg(grades)
    ideal_grades = sorted(judgments.values(), reverse=True)[:k]
    idcg_value = _dcg(ideal_grades)
    ndcg = dcg_value / idcg_value if idcg_value > 0 else 0.0
    hit = 1.0 if any(grade == 2 for grade in grades) else 0.0
    precision = sum(1 for grade in grades if grade >= 1) / k
    mrr = 0.0
    for rank, grade in enumerate(grades, start=1):
        if grade == 2:
            mrr = 1.0 / rank
            break
    apps = [app for _locator, app in truncated if isinstance(app, str) and app.strip()]
    distinct_app_ratio = (
        len(set(apps)) / len(truncated) if truncated and len(apps) == len(truncated) else None
    )
    unjudged_rate = (
        sum(1 for flag in judged if not flag) / len(truncated) if truncated else None
    )
    return {
        "ndcg_at_k": ndcg,
        "hit_at_k": hit,
        "precision_at_k": precision,
        "mrr": mrr,
        "distinct_app_ratio": distinct_app_ratio,
        "unjudged_rate": unjudged_rate,
    }


def _gold_case_index(gold_payload: dict[str, Any]) -> dict[str, dict[str, Any]]:
    index: dict[str, dict[str, Any]] = {}
    for case in gold_payload["cases"]:
        judgments = {
            normalize_locator(judgment["locator"]): judgment["grade"]
            for judgment in case.get("judgments", [])
        }
        index[case["id"]] = {"split": case["split"], "kind": case["kind"], "judgments": judgments}
    return index


def _summarize(values: list[float]) -> dict[str, Any]:
    if not values:
        return {"value": None, "n": 0}
    return {"value": sum(values) / len(values), "n": len(values)}


def _aggregate_split(
    split_name: str,
    per_case: dict[str, dict[str, Any]],
    missing_ids: list[str],
) -> dict[str, Any]:
    if split_name == "all":
        case_ids = list(per_case)
    else:
        case_ids = [cid for cid, info in per_case.items() if info["split"] == split_name]
    retrieval_ids = [cid for cid in case_ids if per_case[cid]["kind"] != "out_of_scope"]
    oos_ids = [cid for cid in case_ids if per_case[cid]["kind"] == "out_of_scope"]

    result: dict[str, Any] = {}
    for metric_name in RETRIEVAL_METRIC_NAMES:
        values = [
            per_case[cid]["metrics"][metric_name]
            for cid in retrieval_ids
            if per_case[cid]["metrics"][metric_name] is not None
        ]
        result[metric_name] = _summarize(values)
        if metric_name == "distinct_app_ratio":
            inconclusive_ids = sorted(
                cid for cid in retrieval_ids if per_case[cid]["metrics"][metric_name] is None
            )
            result[metric_name]["inconclusive_cases"] = inconclusive_ids
            if inconclusive_ids:
                result[metric_name]["value"] = None
    abstention_values = [per_case[cid]["metrics"]["abstention"] for cid in oos_ids]
    result["abstention"] = _summarize(abstention_values)
    result["missing_cases"] = sorted(
        cid for cid in missing_ids if split_name == "all" or per_case[cid]["split"] == split_name
    )
    return result


def compute_report(
    gold_payload: dict[str, Any],
    run_payload: dict[str, Any],
    k: int,
    splits: list[str],
) -> dict[str, Any]:
    gold_cases = _gold_case_index(gold_payload)
    run_cases = {case["id"]: case for case in run_payload["cases"]}
    missing_ids = sorted(case_id for case_id in gold_cases if case_id not in run_cases)

    per_case: dict[str, dict[str, Any]] = {}
    for case_id, info in gold_cases.items():
        run_case = run_cases.get(case_id)
        if run_case is None:
            run_case = {"status": "not_run", "results": []}
        if info["kind"] == "out_of_scope":
            abstained = (
                1.0
                if run_case.get("status") == "no_verified_match" and not run_case.get("results")
                else 0.0
            )
            metrics: dict[str, Any] = {"abstention": abstained}
        else:
            metrics = score_retrieval_case(info["judgments"], run_case.get("results") or [], k)
        per_case[case_id] = {"split": info["split"], "kind": info["kind"], "metrics": metrics}

    report: dict[str, Any] = {"k": k}
    for split_name in splits:
        report[split_name] = _aggregate_split(split_name, per_case, missing_ids)
    return report


def _check_floors(report: dict[str, Any], floors_payload: dict[str, Any], splits: list[str]) -> list[str]:
    messages: list[str] = []
    floor_splits = floors_payload.get("splits", {})
    for split_name in splits:
        floor_metrics = floor_splits.get(split_name)
        if not floor_metrics:
            continue
        for metric_name, floor_value in floor_metrics.items():
            observed = report[split_name][metric_name]["value"]
            if observed is None or observed < floor_value - TOLERANCE:
                messages.append(f"{split_name}.{metric_name} {observed} below floor {floor_value}")
    return messages


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    subparsers = parser.add_subparsers(dest="command", required=True)
    validate_parser = subparsers.add_parser("validate")
    validate_parser.add_argument("--gold", type=Path, required=True)
    score_parser = subparsers.add_parser("score")
    score_parser.add_argument("--gold", type=Path, required=True)
    score_parser.add_argument("--run", type=Path, required=True)
    score_parser.add_argument("--split", choices=sorted(ALL_SPLIT_NAMES), default=None)
    score_parser.add_argument("--k", type=int, default=None)
    score_parser.add_argument("--floors", type=Path, default=None)
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    if args.command == "validate":
        errors: list[str] = []
        gold_payload = load_json(args.gold, errors)
        if not errors:
            errors.extend(validate_gold(gold_payload))
        if errors:
            for error in errors:
                print(f"ERROR: {error}")
            raise SystemExit(1)
        print(f"OK: {args.command}")
        return

    errors = []
    gold_payload = load_json(args.gold, errors)
    run_payload = load_json(args.run, errors)
    if not errors:
        errors.extend(validate_gold(gold_payload))
    if not errors:
        gold_ids = {case["id"] for case in gold_payload["cases"]}
        errors.extend(validate_run(run_payload, gold_ids))
    floors_payload = None
    if not errors and args.floors is not None:
        floors_payload = load_json(args.floors, errors)
        if not errors:
            errors.extend(validate_floors(floors_payload))
    if (
        not errors
        and floors_payload is not None
        and args.k is not None
        and args.k != floors_payload["k"]
    ):
        errors.append(f"--k {args.k} does not match floors k {floors_payload['k']}")
    requested_splits = [args.split] if args.split else list(ALL_SPLIT_NAMES)
    if (
        not errors
        and floors_payload is not None
        and not any(split_name in floors_payload["splits"] for split_name in requested_splits)
    ):
        errors.append(f"no floors apply to requested splits: {requested_splits}")
    if errors:
        for error in errors:
            print(f"ERROR: {error}")
        raise SystemExit(1)

    k = floors_payload["k"] if floors_payload is not None else (args.k if args.k is not None else DEFAULT_K)
    if k <= 0:
        print("ERROR: --k must be a positive integer")
        raise SystemExit(1)

    report = compute_report(gold_payload, run_payload, k, requested_splits)
    print(json.dumps(report, ensure_ascii=False, sort_keys=True))

    if floors_payload is not None:
        shortfalls = _check_floors(report, floors_payload, requested_splits)
        if shortfalls:
            for message in shortfalls:
                print(f"ERROR: {message}")
            raise SystemExit(1)


if __name__ == "__main__":
    main()
