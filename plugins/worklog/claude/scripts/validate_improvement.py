#!/usr/bin/env python3
"""Validate frozen worklog-improve records (Python 3.9+, standard library).

Usage: validate_improvement.py RECORD.json
JSON stdout; exit 0 = valid record (not necessarily accepted), 1 = contract
violation, 2 = unreadable/invalid JSON. Does not execute models or modify files.
"""
import argparse
import difflib
import hashlib
import json
from pathlib import Path
import re


STATES = {"pass", "fail", "not_run", "inconclusive"}


def digest(value):
    return hashlib.sha256(json.dumps(value, ensure_ascii=False, sort_keys=True,
                                     separators=(",", ":")).encode()).hexdigest()


def require(condition, message):
    if not condition:
        raise ValueError(message)


def text(value):
    return isinstance(value, str) and bool(value.strip())


def object_at(value, label):
    require(isinstance(value, dict), f"{label}: expected object")
    return value


def case_at(value):
    object_at(value, "case")
    require(text(value.get("id")) and text(value.get("input")), "case: id/input required")
    require(isinstance(value.get("fixtures"), dict) and
            all(text(k) and isinstance(v, str) for k, v in value["fixtures"].items()),
            "case: fixtures must map paths to text")
    expected = value.get("expected")
    require(isinstance(expected, list) and expected and all(text(v) for v in expected),
            "case: expected must be nonempty text array")
    return value


def instructions_at(value):
    require(isinstance(value, dict) and value and
            all(text(k) and isinstance(v, str) for k, v in value.items()),
            "instructions: nonempty path-to-content map required")
    return value


def validate(record):
    object_at(record, "record")
    require(type(record.get("schema_version")) is int and record["schema_version"] == 1,
            "schema_version: expected 1")
    fixed = object_at(record.get("fixed"), "fixed")
    revision = fixed.get("revision")
    require(isinstance(revision, str) and re.fullmatch(r"[0-9a-f]{40}|[0-9a-f]{64}", revision),
            "fixed.revision: full Git commit hash required")
    instructions = instructions_at(fixed.get("instructions"))
    config = object_at(fixed.get("configuration"), "configuration")
    require(text(config.get("model")) and isinstance(config.get("settings"), dict) and
            text(config.get("command")) and isinstance(config.get("environment"), dict),
            "configuration: model/settings/command/environment required")
    case = case_at(fixed.get("case"))
    regressions = fixed.get("regressions")
    require(isinstance(regressions, list) and len(regressions) <= 5,
            "regressions: expected at most five cases")
    cases = [case_at(c) for c in regressions]
    ids = [c["id"] for c in cases]
    require(ids == sorted(set(ids)) and case["id"] not in ids,
            "regressions: unique sorted IDs excluding new case required")
    contexts = set()

    def runs_at(bundle, snapshot):
        object_at(bundle, "execution bundle")
        runs = bundle.get("runs")
        regression_runs = bundle.get("regressions")
        require(isinstance(runs, list) and len(runs) == 3, "runs: exactly three slots required")
        require(isinstance(regression_runs, dict) and set(regression_runs) == set(ids),
                "regressions: fixed case IDs required")

        def run_at(run, target):
            object_at(run, "run")
            require(run.get("revision") == revision, "run: baseline revision changed")
            require(run.get("configuration") == config, "run: model/settings/command/environment changed")
            require(run.get("case_sha256") == digest(target), "run: case input/fixture/expected changed")
            require(run.get("instructions_sha256") == digest(snapshot), "run: instruction snapshot changed")
            verdicts = run.get("verdicts")
            require(isinstance(verdicts, list) and len(verdicts) == len(target["expected"]) and
                    all(isinstance(v, str) and v in STATES for v in verdicts),
                    "run: one valid verdict per expected item required")
            status = next((v for v in ("not_run", "inconclusive", "fail") if v in verdicts), "pass")
            require(isinstance(run.get("output"), str), "run: output text required")
            if status != "not_run":
                context = run.get("context")
                require(text(context) and context not in contexts, "run: fresh unique context required")
                contexts.add(context)
                require(text(run["output"]), "run: executed output required")
            return status

        statuses = [run_at(r, case) for r in runs]
        regression_statuses = {c["id"]: run_at(regression_runs[c["id"]], c) for c in cases}
        all_statuses = statuses + list(regression_statuses.values())
        return {"passed": statuses.count("pass"), "total": 3,
                "n_of_3": f"{statuses.count('pass')}/3", "runs": statuses,
                "regressions": regression_statuses,
                "not_run": all_statuses.count("not_run"),
                "inconclusive": all_statuses.count("inconclusive")}

    baseline = runs_at(record.get("baseline"), instructions)
    candidates = record.get("candidates")
    require(isinstance(candidates, list) and len(candidates) <= 3, "candidates: at most three required")
    stopped = bool(baseline["not_run"] or baseline["inconclusive"] or baseline["passed"] == 3)
    results = []
    candidate_ids = set()
    for candidate in candidates:
        require(not stopped, "candidates: evaluation must stop after acceptance or unresolved result")
        object_at(candidate, "candidate")
        candidate_id = candidate.get("id")
        require(text(candidate_id) and candidate_id not in candidate_ids, "candidate: unique id required")
        candidate_ids.add(candidate_id)
        require(candidate.get("parent") == "baseline" and candidate.get("base_revision") == revision and
                candidate.get("base_instructions_sha256") == digest(instructions),
                "candidate: independent original baseline required")
        snapshot = instructions_at(candidate.get("instructions"))
        require(set(snapshot) == set(instructions), "candidate: target instruction paths changed")
        added = deleted = 0
        for path, before in instructions.items():
            for line in difflib.ndiff(before.splitlines(), snapshot[path].splitlines()):
                added += line.startswith("+ ")
                deleted += line.startswith("- ")
        require(added + deleted > 0, "candidate: unchanged instructions")
        net = added - deleted
        require(type(candidate.get("net_lines")) is int and candidate["net_lines"] == net,
                "candidate: recorded net_lines differs from snapshot diff")
        approval = candidate.get("approval")
        require(approval is None or text(approval), "candidate: approval must be null or evidence text")
        result = runs_at(candidate, snapshot)
        lost = [i for i in ids if baseline["regressions"][i] == "pass" and
                result["regressions"][i] != "pass"]
        if net > 15 and not approval:
            status = "approval_required"
        elif result["not_run"]:
            status = "not_run"
        elif result["inconclusive"]:
            status = "inconclusive"
        elif result["passed"] >= 2 and result["passed"] > baseline["passed"] and not lost:
            status = "pass"
        else:
            status = "fail"
        results.append({"id": candidate_id, **result, "added": added, "deleted": deleted,
                        "net_lines": net, "lost_regression_ids": lost, "status": status})
        stopped = status != "fail"
    if baseline["not_run"]:
        status = "not_run"
    elif baseline["inconclusive"] or baseline["passed"] == 3:
        status = "inconclusive"
    else:
        status = results[-1]["status"] if results else "baseline_only"
    return {"schema_version": 1, "valid": True, "status": status, "baseline": baseline,
            "candidates": results, "regression_count": len(ids),
            "limitations": [] if ids else ["no-regression-cases"], "violations": []}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("record", type=Path)
    args = parser.parse_args()
    try:
        record = json.loads(args.record.read_text(encoding="utf-8"))
    except (OSError, UnicodeError, json.JSONDecodeError) as error:
        print(json.dumps({"valid": False, "status": "unreadable", "errors": [str(error)]}))
        return 2
    try:
        result = validate(record)
    except ValueError as error:
        print(json.dumps({"valid": False, "status": "invalid", "violations": [str(error)]}))
        return 1
    print(json.dumps(result, ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
