#!/usr/bin/env python3
"""Controlled reviewer-model benchmark with a fixed Astra adjudicator.

The benchmark invokes delegated reviewers directly, so changing the cohort does
not also change the controller. Review workers cannot delegate. One fixed Astra
adjudicator then validates and merges the raw findings for each cohort/repetition.
"""

from __future__ import annotations

import argparse
from concurrent.futures import ThreadPoolExecutor, as_completed
from collections import Counter, defaultdict
from datetime import datetime, timedelta
import json
import os
from pathlib import Path
import shutil
import sys
import time
from typing import Any, Mapping, Sequence

import runner


PLAN_VERSION = "marketplace-v2-controlled-plan-v1"
CALL_VERSION = "marketplace-v2-controlled-call-v1"
ADJUDICATOR_MODEL = "gpt-6-astra"
ADJUDICATOR_EFFORT = "high"
CONTROLLED_ADJUDICATION_VERSION = "marketplace-v2-controlled-adjudication-v1"
PLAN_FIELDS = {
    "schema_version", "created_at", "manifest_id", "candidate_profile_sha256",
    "artifact_fixture_sha256", "criteria_sha256", "code_quality_sha256", "controlled_runner_sha256",
    "adjudicator", "runs", "plan_id",
}
PLAN_RUN_FIELDS = {"run_id", "case_id", "cohort_id", "repetition", "model", "effort", "reviewer_count", "workers"}
WORKER_FIELDS = {"worker_id", "workspace", "initial_sha256"}
CALL_FIELDS = {
    "schema_version", "plan_id", "run_id", "call_id", "role", "status", "started_at",
    "latency_seconds", "returncode", "timed_out", "spawn_error", "trace_errors",
    "requested_model", "requested_effort", "observed_model", "observed_effort",
    "trace_observations", "workspace_initial_sha256", "workspace_final_sha256",
    "batch_jobs", "artifacts", "artifact_sha256",
}


def _benchmark_case(sources: Mapping[str, Any]) -> Mapping[str, Any]:
    cases = [case for case in sources["cases"]["cases"] if case.get("benchmark")]
    if len(cases) != 1:
        raise runner.EvaluationError("controlled benchmark requires exactly one benchmark case")
    return cases[0]


def prepare(output: Path) -> dict[str, Any]:
    manifest = runner._load_manifest(output)
    sources = runner._verify_frozen_sources(manifest)
    controlled = Path(manifest["artifact_dir"]) / "controlled"
    plan_path = controlled / "plan.json"
    if controlled.exists():
        raise runner.EvaluationError("controlled benchmark already exists")
    controlled.mkdir(parents=True, mode=0o700)
    case = _benchmark_case(sources)
    cohorts = sources["cohorts"]
    source_run = next(run for run in manifest["runs"] if run["case_id"] == case["id"])
    source_workspace = Path(source_run["workspace"])
    runs: list[dict[str, Any]] = []
    for cohort in cohorts["cohorts"]:
        for repetition in range(1, cohorts["benchmark_repetitions"] + 1):
            run_id = f"controlled--{cohort['id']}--r{repetition}"
            run_root = controlled / "runs" / run_id
            workers = []
            for index in range(1, cohort["reviewer_count"] + 1):
                workspace = run_root / "workers" / f"worker-{index}" / "workspace"
                shutil.copytree(source_workspace, workspace, symlinks=True)
                workers.append({
                    "worker_id": f"worker-{index}",
                    "workspace": str(workspace),
                    "initial_sha256": runner._tree_sha(workspace, excluded=(".git",)),
                })
            runs.append({
                "run_id": run_id,
                "case_id": case["id"],
                "cohort_id": cohort["id"],
                "repetition": repetition,
                "model": cohort["model"],
                "effort": cohort["effort"],
                "reviewer_count": cohort["reviewer_count"],
                "workers": workers,
            })
    plan = {
        "schema_version": PLAN_VERSION,
        "created_at": runner._utc_now(),
        "manifest_id": manifest["manifest_id"],
        "candidate_profile_sha256": manifest["candidate_profiles"][case["profile"]]["sha256"],
        "artifact_fixture_sha256": runner._tree_sha(source_workspace, excluded=(".agents", ".git")),
        "criteria_sha256": runner._sha_file(source_workspace / ".agents/references/review-criteria.md"),
        "code_quality_sha256": runner._sha_file(source_workspace / ".agents/references/code-quality.md"),
        "controlled_runner_sha256": runner._sha_file(Path(__file__)),
        "adjudicator": {"model": ADJUDICATOR_MODEL, "effort": ADJUDICATOR_EFFORT},
        "runs": runs,
    }
    plan["plan_id"] = runner._sha_bytes(runner.encoded_json(plan).encode("utf-8"))
    runner._write_json(plan_path, plan)
    return plan


def _load_plan(output: Path) -> tuple[dict[str, Any], dict[str, Any], Mapping[str, Any]]:
    manifest = runner._load_manifest(output)
    sources = runner._verify_frozen_sources(manifest)
    plan = runner._read_json(Path(manifest["artifact_dir"]) / "controlled/plan.json")
    if not isinstance(plan, dict) or set(plan) != PLAN_FIELDS:
        raise runner.EvaluationError("controlled plan fields mismatch")
    if plan.get("schema_version") != PLAN_VERSION or plan.get("manifest_id") != manifest["manifest_id"]:
        raise runner.EvaluationError("controlled plan does not match the candidate manifest")
    plan_id = runner._sha_bytes(runner.encoded_json(runner._without_key(plan, "plan_id")).encode("utf-8"))
    if plan.get("plan_id") != plan_id:
        raise runner.EvaluationError("controlled plan_id does not match canonical content")
    if plan.get("controlled_runner_sha256") != runner._sha_file(Path(__file__)):
        raise runner.EvaluationError("controlled evaluator changed after prepare; create a new plan")
    case = _benchmark_case(sources)
    controlled = Path(manifest["artifact_dir"]) / "controlled"
    expected_runs = []
    for cohort in sources["cohorts"]["cohorts"]:
        for repetition in range(1, sources["cohorts"]["benchmark_repetitions"] + 1):
            expected_runs.append((f"controlled--{cohort['id']}--r{repetition}", cohort, repetition))
    if len(plan.get("runs", [])) != len(expected_runs):
        raise runner.EvaluationError("controlled plan run count mismatch")
    for value, (run_id, cohort, repetition) in zip(plan["runs"], expected_runs):
        if not isinstance(value, dict) or set(value) != PLAN_RUN_FIELDS:
            raise runner.EvaluationError("controlled plan run fields mismatch")
        expected = {
            "run_id": run_id, "case_id": case["id"], "cohort_id": cohort["id"],
            "repetition": repetition, "model": cohort["model"], "effort": cohort["effort"],
            "reviewer_count": cohort["reviewer_count"],
        }
        if any(value.get(key) != item for key, item in expected.items()):
            raise runner.EvaluationError(f"controlled plan run mismatch: {run_id}")
        if len(value.get("workers", [])) != cohort["reviewer_count"]:
            raise runner.EvaluationError(f"controlled worker count mismatch: {run_id}")
        for index, worker in enumerate(value["workers"], 1):
            expected_workspace = controlled / "runs" / run_id / "workers" / f"worker-{index}" / "workspace"
            if set(worker) != WORKER_FIELDS or worker.get("worker_id") != f"worker-{index}" or worker.get("workspace") != str(expected_workspace):
                raise runner.EvaluationError(f"controlled worker identity mismatch: {run_id}/worker-{index}")
            if not isinstance(worker.get("initial_sha256"), str) or len(worker["initial_sha256"]) != 64:
                raise runner.EvaluationError(f"controlled worker digest invalid: {run_id}/worker-{index}")
    if plan.get("candidate_profile_sha256") != manifest["candidate_profiles"][case["profile"]]["sha256"]:
        raise runner.EvaluationError("controlled candidate digest mismatch")
    source_run = next(run for run in manifest["runs"] if run["case_id"] == case["id"])
    source_workspace = Path(source_run["workspace"])
    if plan.get("artifact_fixture_sha256") != runner._tree_sha(source_workspace, excluded=(".agents", ".git")):
        raise runner.EvaluationError("controlled fixture digest mismatch")
    criteria = source_workspace / ".agents/references/review-criteria.md"
    if plan.get("criteria_sha256") != runner._sha_file(criteria):
        raise runner.EvaluationError("controlled criteria digest mismatch")
    code_quality = source_workspace / ".agents/references/code-quality.md"
    if plan.get("code_quality_sha256") != runner._sha_file(code_quality):
        raise runner.EvaluationError("controlled code-quality digest mismatch")
    if plan.get("adjudicator") != {"model": ADJUDICATOR_MODEL, "effort": ADJUDICATOR_EFFORT}:
        raise runner.EvaluationError("controlled adjudicator contract mismatch")
    return manifest, plan, case


def _reviewer_prompt(case: Mapping[str, Any]) -> str:
    return case["prompt"] + """

You are one delegated fresh reviewer, not the coordinating root. Read the local review skill,
its common criteria, and the fixed fixture. Review the artifact directly and return your own findings.
Do not create, message, or wait for other agents. Do not use prior reviewer results. Do not edit files.
Report exact path:line, reachable trigger, impact, smallest fix, checks actually run, and unknowns."""


def _adjudicator_prompt(worker_count: int) -> str:
    return f"""Synthesize the {worker_count} independent reviews in reviewer-results/ against the current
fixture, CHANGE.md, criteria.md, and code-quality.md. Validate every candidate against the source and contract; do not use
majority vote and do not create findings to fill a quota. Merge duplicate root causes. Report only validated
findings in priority order with path:line, trigger, impact, and smallest fix. Then list rejected candidates,
checks actually run, not-run checks, and unknowns. Do not create or contact agents and do not modify files."""


def _developer(role: str) -> str:
    return f"""This is an isolated native evaluation. You are the {role}.
Work only in the current workspace. Do not inspect parent directories, evaluator files, hidden oracle data,
user configuration, or other runs. Do not commit, push, publish, install, access external services, or send
messages. Agent delegation is disabled for this invocation. Separate observation, inference, not_run, and
unknown. A model/effort request is not proof of the underlying runtime setting."""


def _argv(manifest: Mapping[str, Any], model: str, effort: str, workspace: Path, output: Path, role: str) -> list[str]:
    return [
        manifest["codex_binary"], "exec", "--ephemeral", "--ignore-user-config", "--ignore-rules",
        "--skip-git-repo-check", "--disable", "multi_agent", "--json", "--color", "never",
        "--model", model, "--sandbox", "read-only", "--output-last-message", str(output),
        "-C", str(workspace),
        "-c", f"model_reasoning_effort={json.dumps(effort)}",
        "-c", f"developer_instructions={json.dumps(_developer(role), ensure_ascii=False)}",
        "-",
    ]


def _execute_call(
    manifest: Mapping[str, Any], call_root: Path, workspace: Path, model: str, effort: str,
    prompt: str, role: str, timeout: int, plan_id: str, run_id: str, call_id: str, batch_jobs: int,
) -> dict[str, Any]:
    result_path = call_root / "call.json"
    runner._reserve_once(call_root, result_path)
    workspace_initial_sha256 = runner._tree_sha(workspace, excluded=(".git",))
    output = call_root / "final.md"
    trace = call_root / "trace.jsonl"
    stderr = call_root / "stderr.txt"
    argv = _argv(manifest, model, effort, workspace, output, role)
    runner._write_json(call_root / "command.json", {
        "argv": argv, "cwd": str(workspace),
        "stdin_sha256": runner._sha_bytes(prompt.encode("utf-8")),
        "auth": "isolated CODEX_HOME with auth.json symlink only",
    })
    started_at = runner._utc_now()
    started = time.monotonic()
    timed_out = False
    spawn_error: str | None = None
    returncode: int | None = None
    try:
        env = runner._isolated_environment(call_root, manifest["node_runtime"])
        returncode, timed_out = runner._collect_bounded_process(
            argv, workspace, env, prompt, trace, stderr, timeout,
        )
    except (OSError, runner.EvaluationError) as exc:
        spawn_error = f"{type(exc).__name__}: {exc}"
    latency = round(time.monotonic() - started, 6)
    events, trace_errors = runner._read_execution_trace(trace, stderr)
    observations = runner._trace_observations(events)
    final_available = output.is_file() and output.stat().st_size > 0
    complete = (
        returncode == 0 and not timed_out and not trace_errors
        and observations["turn_completed"] and final_available
    )
    if runner._output_limited(trace_errors):
        status = "inconclusive"
    elif spawn_error or (returncode not in (0, None) and not observations["turn_completed"]):
        status = "not_run"
    elif not complete:
        status = "inconclusive"
    elif observations["collaboration_tools"] or observations["unknown_collaboration_tools"]:
        status = "fail"
    else:
        status = "complete"
    value = {
        "schema_version": CALL_VERSION,
        "plan_id": plan_id,
        "run_id": run_id,
        "call_id": call_id,
        "role": role,
        "status": status,
        "started_at": started_at,
        "latency_seconds": latency,
        "returncode": returncode,
        "timed_out": timed_out,
        "spawn_error": spawn_error,
        "trace_errors": trace_errors,
        "requested_model": model,
        "requested_effort": effort,
        "observed_model": "unknown",
        "observed_effort": "unknown",
        "trace_observations": observations,
        "workspace_initial_sha256": workspace_initial_sha256,
        "workspace_final_sha256": runner._tree_sha(workspace, excluded=(".git",)),
        "batch_jobs": batch_jobs,
        "artifacts": {
            "final": str(output), "trace": str(trace), "stderr": str(stderr),
            "command": str(call_root / "command.json"), "workspace": str(workspace),
        },
        "artifact_sha256": {
            "final": runner._optional_sha(output), "trace": runner._optional_sha(trace),
            "stderr": runner._optional_sha(stderr), "command": runner._sha_file(call_root / "command.json"),
        },
    }
    runner._write_json(result_path, value)
    return value


def _load_call(
    manifest: Mapping[str, Any], plan: Mapping[str, Any], plan_run: Mapping[str, Any],
    call_root: Path, workspace: Path, call_id: str, role: str, model: str, effort: str, prompt: str,
) -> dict[str, Any]:
    value = runner._read_json(call_root / "call.json")
    if not (call_root / "execution.reserved").is_file():
        raise runner.EvaluationError(f"controlled call has no execution reservation: {plan_run['run_id']}/{call_id}")
    if not isinstance(value, dict) or set(value) != CALL_FIELDS:
        raise runner.EvaluationError(f"controlled call fields mismatch: {plan_run['run_id']}/{call_id}")
    identities = {
        "schema_version": CALL_VERSION, "plan_id": plan["plan_id"], "run_id": plan_run["run_id"],
        "call_id": call_id, "role": role, "requested_model": model, "requested_effort": effort,
        "observed_model": "unknown", "observed_effort": "unknown",
    }
    if any(value.get(key) != expected for key, expected in identities.items()):
        raise runner.EvaluationError(f"controlled call identity mismatch: {plan_run['run_id']}/{call_id}")
    if value.get("status") not in {"complete", "fail", "not_run", "inconclusive"}:
        raise runner.EvaluationError(f"controlled call status invalid: {plan_run['run_id']}/{call_id}")
    latency = value.get("latency_seconds")
    if isinstance(latency, bool) or not isinstance(latency, (int, float)) or latency < 0:
        raise runner.EvaluationError(f"controlled call latency invalid: {plan_run['run_id']}/{call_id}")
    if isinstance(value.get("batch_jobs"), bool) or not isinstance(value.get("batch_jobs"), int) or value["batch_jobs"] < 1:
        raise runner.EvaluationError(f"controlled call batch_jobs invalid: {plan_run['run_id']}/{call_id}")
    expected_artifacts = {
        "final": str(call_root / "final.md"), "trace": str(call_root / "trace.jsonl"),
        "stderr": str(call_root / "stderr.txt"), "command": str(call_root / "command.json"),
        "workspace": str(workspace),
    }
    if value.get("artifacts") != expected_artifacts:
        raise runner.EvaluationError(f"controlled call artifact paths mismatch: {plan_run['run_id']}/{call_id}")
    digests = value.get("artifact_sha256")
    if not isinstance(digests, dict) or set(digests) != {"final", "trace", "stderr", "command"}:
        raise runner.EvaluationError(f"controlled call artifact digests invalid: {plan_run['run_id']}/{call_id}")
    for name in digests:
        if digests[name] != runner._optional_sha(Path(expected_artifacts[name])):
            raise runner.EvaluationError(f"controlled call {name} digest mismatch: {plan_run['run_id']}/{call_id}")
    current_workspace_sha = runner._tree_sha(workspace, excluded=(".git",))
    if value.get("workspace_final_sha256") != current_workspace_sha:
        raise runner.EvaluationError(f"controlled call workspace digest mismatch: {plan_run['run_id']}/{call_id}")
    if value.get("workspace_initial_sha256") != value.get("workspace_final_sha256"):
        raise runner.EvaluationError(f"controlled read-only workspace changed: {plan_run['run_id']}/{call_id}")
    if role == "delegated-reviewer":
        worker = next((item for item in plan_run["workers"] if item["worker_id"] == call_id), None)
        if worker is None or value.get("workspace_initial_sha256") != worker["initial_sha256"]:
            raise runner.EvaluationError(f"controlled worker source mismatch: {plan_run['run_id']}/{call_id}")
    expected_command = {
        "argv": _argv(manifest, model, effort, workspace, call_root / "final.md", role),
        "cwd": str(workspace), "stdin_sha256": runner._sha_bytes(prompt.encode("utf-8")),
        "auth": "isolated CODEX_HOME with auth.json symlink only",
    }
    if runner._read_json(call_root / "command.json") != expected_command:
        raise runner.EvaluationError(f"controlled call command mismatch: {plan_run['run_id']}/{call_id}")
    events, errors = runner._read_execution_trace(call_root / "trace.jsonl", call_root / "stderr.txt")
    observations = runner._trace_observations(events)
    if value.get("trace_errors") != errors or value.get("trace_observations") != observations:
        raise runner.EvaluationError(f"controlled call trace mismatch: {plan_run['run_id']}/{call_id}")
    final_path = call_root / "final.md"
    final_available = final_path.is_file() and final_path.stat().st_size > 0
    complete = (
        value.get("returncode") == 0 and value.get("timed_out") is False and not errors
        and observations["turn_completed"] and final_available
    )
    if runner._output_limited(errors):
        derived = "inconclusive"
    elif value.get("spawn_error") or (value.get("returncode") not in (0, None) and not observations["turn_completed"]):
        derived = "not_run"
    elif not complete:
        derived = "inconclusive"
    elif observations["collaboration_tools"] or observations["unknown_collaboration_tools"]:
        derived = "fail"
    else:
        derived = "complete"
    if value.get("status") != derived:
        raise runner.EvaluationError(f"controlled call status derivation mismatch: {plan_run['run_id']}/{call_id}")
    return value


def run_workers(output: Path, cohort_id: str | None, jobs: int, timeout: int) -> list[dict[str, Any]]:
    manifest, plan, case = _load_plan(output)
    calls = []
    for run in plan["runs"]:
        if cohort_id and run["cohort_id"] != cohort_id:
            continue
        for worker in run["workers"]:
            workspace = Path(worker["workspace"])
            if runner._tree_sha(workspace, excluded=(".git",)) != worker["initial_sha256"]:
                raise runner.EvaluationError(f"worker workspace drift: {run['run_id']}/{worker['worker_id']}")
            call_root = Path(manifest["artifact_dir"]) / "controlled/runs" / run["run_id"] / "workers" / worker["worker_id"]
            calls.append((run, worker, call_root, workspace))
    if not calls:
        raise runner.EvaluationError("no controlled worker calls matched")
    results = []
    with ThreadPoolExecutor(max_workers=jobs) as pool:
        futures = {
            pool.submit(
                _execute_call, manifest, call_root, workspace, run["model"], run["effort"],
                _reviewer_prompt(case), "delegated-reviewer", timeout,
                plan["plan_id"], run["run_id"], worker["worker_id"],
                jobs,
            ): (run, worker)
            for run, worker, call_root, workspace in calls
        }
        for future in as_completed(futures):
            run, worker = futures[future]
            value = future.result()
            print(runner.encoded_json({"run_id": run["run_id"], "worker_id": worker["worker_id"], "status": value["status"]}), flush=True)
            results.append(value)
    return results


def _prepare_adjudicator_workspace(
    manifest: Mapping[str, Any], plan: Mapping[str, Any], plan_run: Mapping[str, Any], case: Mapping[str, Any]
) -> Path:
    run_root = Path(manifest["artifact_dir"]) / "controlled/runs" / plan_run["run_id"]
    adjudicator_root = run_root / "adjudicator"
    workspace = adjudicator_root / "workspace"
    marker = workspace / ".controlled-input-manifest.json"
    expected_calls = []
    for worker in plan_run["workers"]:
        worker_root = run_root / "workers" / worker["worker_id"]
        call = _load_call(
            manifest, plan, plan_run, worker_root, Path(worker["workspace"]), worker["worker_id"],
            "delegated-reviewer", plan_run["model"], plan_run["effort"], _reviewer_prompt(case),
        )
        if call["status"] != "complete":
            raise runner.EvaluationError(f"worker is not complete: {plan_run['run_id']}/{worker['worker_id']}")
        expected_calls.append({"worker_id": worker["worker_id"], "final_sha256": call["artifact_sha256"]["final"]})
    expected_marker = {
        "plan_id": plan["plan_id"], "run_id": plan_run["run_id"], "workers": expected_calls,
        "criteria_sha256": plan["criteria_sha256"], "code_quality_sha256": plan["code_quality_sha256"],
        "fixture_sha256": plan["artifact_fixture_sha256"],
    }
    if workspace.exists():
        if not marker.is_file() or runner._read_json(marker) != expected_marker:
            raise runner.EvaluationError(f"adjudicator workspace is partial or stale: {plan_run['run_id']}")
        reviews = workspace / "reviewer-results"
        if runner._sha_file(workspace / "criteria.md") != plan["criteria_sha256"]:
            raise runner.EvaluationError(f"adjudicator criteria drift: {plan_run['run_id']}")
        if runner._sha_file(workspace / "code-quality.md") != plan["code_quality_sha256"]:
            raise runner.EvaluationError(f"adjudicator code-quality drift: {plan_run['run_id']}")
        for item in expected_calls:
            path = reviews / f"{item['worker_id']}.md"
            if not path.is_file() or runner._sha_file(path) != item["final_sha256"]:
                raise runner.EvaluationError(f"adjudicator reviewer input drift: {plan_run['run_id']}/{item['worker_id']}")
        return workspace
    staging = adjudicator_root / "workspace.preparing"
    try:
        staging.mkdir(parents=True)
    except FileExistsError as exc:
        raise runner.EvaluationError(f"adjudicator workspace preparation was interrupted: {plan_run['run_id']}") from exc
    source_run = next(run for run in manifest["runs"] if run["case_id"] == case["id"])
    source_workspace = Path(source_run["workspace"])
    if runner._tree_sha(source_workspace, excluded=(".agents", ".git")) != plan["artifact_fixture_sha256"]:
        raise runner.EvaluationError(f"controlled prepared fixture drift: {plan_run['run_id']}")
    for source in source_workspace.iterdir():
        if source.name in {".agents", ".git"}:
            continue
        destination = staging / source.name
        if source.is_dir():
            shutil.copytree(source, destination, symlinks=True)
        elif source.is_symlink():
            destination.symlink_to(os.readlink(source))
        else:
            shutil.copy2(source, destination)
    reviews = staging / "reviewer-results"
    reviews.mkdir()
    for worker, item in zip(plan_run["workers"], expected_calls):
        source = run_root / "workers" / worker["worker_id"] / "final.md"
        shutil.copy2(source, reviews / f"{worker['worker_id']}.md")
    candidate = Path(manifest["candidate_profiles"]["engineering"]["path"])
    shutil.copy2(candidate / "references/review-criteria.md", staging / "criteria.md")
    shutil.copy2(candidate / "references/code-quality.md", staging / "code-quality.md")
    runner._write_json(staging / ".controlled-input-manifest.json", expected_marker)
    staging.rename(workspace)
    return workspace


def run_adjudicators(output: Path, cohort_id: str | None, jobs: int, timeout: int) -> list[dict[str, Any]]:
    manifest, plan, case = _load_plan(output)
    calls = []
    for plan_run in plan["runs"]:
        if cohort_id and plan_run["cohort_id"] != cohort_id:
            continue
        workspace = _prepare_adjudicator_workspace(manifest, plan, plan_run, case)
        call_root = Path(manifest["artifact_dir"]) / "controlled/runs" / plan_run["run_id"] / "adjudicator"
        calls.append((plan_run, call_root, workspace))
    if not calls:
        raise runner.EvaluationError("no controlled adjudicator calls matched")
    results = []
    with ThreadPoolExecutor(max_workers=jobs) as pool:
        futures = {
            pool.submit(
                _execute_call, manifest, call_root, workspace, ADJUDICATOR_MODEL, ADJUDICATOR_EFFORT,
                _adjudicator_prompt(plan_run["reviewer_count"]), "fixed-adjudicator", timeout,
                plan["plan_id"], plan_run["run_id"], "adjudicator",
                jobs,
            ): plan_run
            for plan_run, call_root, workspace in calls
        }
        for future in as_completed(futures):
            plan_run = futures[future]
            value = future.result()
            print(runner.encoded_json({"run_id": plan_run["run_id"], "adjudicator": value["status"]}), flush=True)
            results.append(value)
    return results


def _team_span(calls: Sequence[Mapping[str, Any]]) -> float | None:
    complete = [call for call in calls if isinstance(call.get("started_at"), str) and isinstance(call.get("latency_seconds"), (int, float))]
    if not complete:
        return None
    starts = [datetime.fromisoformat(call["started_at"]) for call in complete]
    ends = [start + timedelta(seconds=float(call["latency_seconds"])) for start, call in zip(starts, complete)]
    return round((max(ends) - min(starts)).total_seconds(), 6)


def _load_controlled_adjudication(
    plan: Mapping[str, Any], path: Path, completed_ids: set[str]
) -> dict[str, Any]:
    value = runner._read_json(path)
    if not isinstance(value, dict) or set(value) != {"schema_version", "plan_id", "created_at", "runs"}:
        raise runner.EvaluationError("controlled adjudication fields mismatch")
    if value.get("schema_version") != CONTROLLED_ADJUDICATION_VERSION or value.get("plan_id") != plan["plan_id"]:
        raise runner.EvaluationError("controlled adjudication does not match plan")
    rows = value.get("runs")
    if not isinstance(rows, list) or not all(isinstance(row, dict) for row in rows):
        raise runner.EvaluationError("controlled adjudication runs must be objects")
    expected_ids = {item["run_id"] for item in plan["runs"]}
    if len(rows) != len(expected_ids) or {row.get("run_id") for row in rows} != expected_ids:
        raise runner.EvaluationError("controlled adjudication must contain every run exactly once")
    row_fields = {
        "run_id", "execution_available", "verdict", "validated_defects", "critical_misses",
        "false_positives", "duplicate_findings", "unnecessary_changes", "notes",
    }
    for row in rows:
        if set(row) != row_fields or not isinstance(row.get("execution_available"), bool) or not isinstance(row.get("notes"), str):
            raise runner.EvaluationError(f"controlled adjudication row fields invalid: {row.get('run_id')}")
        if row.get("verdict") not in {"pass", "fail", "not_run", "inconclusive"}:
            raise runner.EvaluationError(f"controlled adjudication verdict invalid: {row.get('run_id')}")
        for field in ("validated_defects", "critical_misses", "false_positives", "duplicate_findings", "unnecessary_changes"):
            if not isinstance(row.get(field), list) or not all(isinstance(item, str) and item for item in row[field]):
                raise runner.EvaluationError(f"controlled adjudication {field} invalid: {row.get('run_id')}")
        available = row["run_id"] in completed_ids
        if row["execution_available"] is not available:
            raise runner.EvaluationError(f"controlled adjudication execution mismatch: {row['run_id']}")
        if not available and row["verdict"] not in {"not_run", "inconclusive"}:
            raise runner.EvaluationError(f"controlled adjudication claims incomplete execution: {row['run_id']}")
        if row["verdict"] not in {"pass", "fail"} and any(
            row[field] for field in ("validated_defects", "critical_misses", "false_positives", "duplicate_findings", "unnecessary_changes")
        ):
            raise runner.EvaluationError(f"controlled non-semantic row contains quality metrics: {row['run_id']}")
    return value


def summary(output: Path, adjudication_path: Path | None = None) -> dict[str, Any]:
    manifest, plan, case = _load_plan(output)
    rows = []
    for plan_run in plan["runs"]:
        run_root = Path(manifest["artifact_dir"]) / "controlled/runs" / plan_run["run_id"]
        worker_calls = []
        validation_errors = []
        for worker in plan_run["workers"]:
            path = run_root / "workers" / worker["worker_id"] / "call.json"
            if not path.is_file():
                worker_calls.append({"status": "not_run"})
                continue
            try:
                worker_calls.append(_load_call(
                    manifest, plan, plan_run, path.parent, Path(worker["workspace"]), worker["worker_id"],
                    "delegated-reviewer", plan_run["model"], plan_run["effort"], _reviewer_prompt(case),
                ))
            except runner.EvaluationError as exc:
                validation_errors.append(str(exc))
                worker_calls.append({"status": "inconclusive"})
        adjudicator_path = run_root / "adjudicator/call.json"
        if adjudicator_path.is_file():
            try:
                adjudicator = _load_call(
                    manifest, plan, plan_run, adjudicator_path.parent,
                    adjudicator_path.parent / "workspace", "adjudicator", "fixed-adjudicator",
                    ADJUDICATOR_MODEL, ADJUDICATOR_EFFORT, _adjudicator_prompt(plan_run["reviewer_count"]),
                )
            except runner.EvaluationError as exc:
                validation_errors.append(str(exc))
                adjudicator = {"status": "inconclusive"}
        else:
            adjudicator = {"status": "not_run"}
        rows.append({
            "run_id": plan_run["run_id"],
            "cohort_id": plan_run["cohort_id"],
            "repetition": plan_run["repetition"],
            "worker_statuses": [value["status"] for value in worker_calls],
            "worker_call_seconds": [value.get("latency_seconds") for value in worker_calls],
            "worker_batch_jobs": sorted({value.get("batch_jobs") for value in worker_calls if value.get("batch_jobs") is not None}),
            "worker_total_seconds": round(sum(value.get("latency_seconds", 0) for value in worker_calls), 6),
            "worker_max_seconds": max((value.get("latency_seconds", 0) for value in worker_calls), default=0),
            "worker_team_span_seconds_including_executor_queue": _team_span(worker_calls),
            "adjudicator_status": adjudicator["status"],
            "adjudicator_seconds": adjudicator.get("latency_seconds"),
            "adjudicator_batch_jobs": adjudicator.get("batch_jobs"),
            "semantic_status": "inconclusive" if adjudicator["status"] == "complete" else adjudicator["status"],
            "semantic_reason": "awaiting hidden-oracle adjudication" if adjudicator["status"] == "complete" else "controlled execution incomplete",
            "output_path": adjudicator.get("artifacts", {}).get("final"),
            "validation_errors": validation_errors,
            "requested_model": plan_run["model"],
            "requested_effort": plan_run["effort"],
            "requested_reviewer_count": plan_run["reviewer_count"],
        })
    completed_ids = {
        row["run_id"] for row in rows
        if row["adjudicator_status"] == "complete" and all(status == "complete" for status in row["worker_statuses"])
    }
    adjudication = _load_controlled_adjudication(
        plan, runner._require_not_model_visible(manifest, adjudication_path), completed_ids
    ) if adjudication_path else None
    grades = {row["run_id"]: row for row in adjudication["runs"]} if adjudication else {}
    for row in rows:
        grade = grades.get(row["run_id"])
        row["semantic_status"] = grade["verdict"] if grade else ("inconclusive" if row["run_id"] in completed_ids else row["adjudicator_status"])
        row["semantic_reason"] = "hidden-oracle adjudication loaded" if grade else ("awaiting hidden-oracle adjudication" if row["run_id"] in completed_ids else "controlled execution incomplete")
    grouped: dict[str, list[dict[str, Any]]] = defaultdict(list)
    for row in rows:
        grouped[row["cohort_id"]].append(row)
    cohort_metrics = []
    for cohort_id, cohort_rows in grouped.items():
        cohort_grades = [
            grades[row["run_id"]] for row in cohort_rows
            if row["run_id"] in grades and row["run_id"] in completed_ids
            and grades[row["run_id"]]["verdict"] in {"pass", "fail"}
        ]
        cohort_metrics.append({
            "cohort_id": cohort_id,
            "requested_model": cohort_rows[0]["requested_model"],
            "requested_effort": cohort_rows[0]["requested_effort"],
            "requested_reviewer_count": cohort_rows[0]["requested_reviewer_count"],
            "runs_planned": len(cohort_rows), "runs_execution_complete": sum(row["run_id"] in completed_ids for row in cohort_rows),
            "verdicts": dict(sorted(Counter(row["verdict"] for row in cohort_grades).items())),
            "unique_validated_defects": sorted({item for row in cohort_grades for item in row["validated_defects"]}),
            "critical_misses": sum(len(row["critical_misses"]) for row in cohort_grades),
            "false_positives": sum(len(row["false_positives"]) for row in cohort_grades),
            "duplicate_findings_after_synthesis": sum(len(row["duplicate_findings"]) for row in cohort_grades),
            "unnecessary_changes": sum(len(row["unnecessary_changes"]) for row in cohort_grades),
            "worker_call_seconds": [seconds for row in cohort_rows for seconds in row["worker_call_seconds"] if seconds is not None],
            "team_spans_seconds_including_executor_queue": [row["worker_team_span_seconds_including_executor_queue"] for row in cohort_rows if row["worker_team_span_seconds_including_executor_queue"] is not None],
        })
    value = {
        "schema_version": "marketplace-v2-controlled-summary-v1",
        "plan_id": plan["plan_id"],
        "candidate_profile_sha256": plan["candidate_profile_sha256"],
        "artifact_fixture_sha256": plan["artifact_fixture_sha256"],
        "criteria_sha256": plan["criteria_sha256"],
        "code_quality_sha256": plan["code_quality_sha256"],
        "requested_adjudicator": plan["adjudicator"],
        "observed_adjudicator": {"model": "unknown", "effort": "unknown"},
        "semantic_adjudication": "loaded" if adjudication else "not_run",
        "cohort_metrics": cohort_metrics,
        "runs": rows,
    }
    runner._write_json(Path(manifest["artifact_dir"]) / "controlled/summary.json", value)
    return value


def make_adjudication_template(output: Path, destination: Path) -> dict[str, Any]:
    manifest, _, _ = _load_plan(output)
    destination = runner._require_not_model_visible(manifest, destination)
    if destination.exists():
        raise runner.EvaluationError(f"controlled adjudication destination already exists: {destination}")
    value = summary(output)
    rows = [{
        "run_id": row["run_id"],
        "execution_available": row["run_id"] in {
            item["run_id"] for item in value["runs"]
            if item["adjudicator_status"] == "complete" and all(status == "complete" for status in item["worker_statuses"])
        },
        "verdict": "not_run" if row["adjudicator_status"] == "not_run" else "inconclusive",
        "validated_defects": [], "critical_misses": [], "false_positives": [],
        "duplicate_findings": [], "unnecessary_changes": [], "notes": "",
    } for row in value["runs"]]
    result = {"schema_version": CONTROLLED_ADJUDICATION_VERSION, "plan_id": value["plan_id"], "created_at": runner._utc_now(), "runs": rows}
    runner._write_json(destination, result)
    return result


def report(output: Path, adjudication_path: Path | None) -> str:
    value = summary(output, adjudication_path)
    lines = [
        "# Controlled reviewer benchmark", "", f"- Plan: `{value['plan_id']}`",
        f"- Semantic adjudication: `{value['semantic_adjudication']}`",
        "- Underlying worker and adjudicator model/effort observed: `unknown`; requested values are recorded below.", "",
        "| Cohort | Requested | Complete | Verdicts | Unique defects | Misses | False positives | Duplicates after synthesis | Unnecessary changes |",
        "| --- | --- | ---: | --- | ---: | ---: | ---: | ---: | ---: |",
    ]
    for row in value["cohort_metrics"]:
        verdicts = ", ".join(f"{key}={number}" for key, number in row["verdicts"].items()) or "not_run"
        lines.append(
            f"| `{row['cohort_id']}` | `{row['requested_model']}/{row['requested_effort']} × {row['requested_reviewer_count']}` | "
            f"{row['runs_execution_complete']}/{row['runs_planned']} | {verdicts} | {len(row['unique_validated_defects'])} | "
            f"{row['critical_misses']} | {row['false_positives']} | {row['duplicate_findings_after_synthesis']} | {row['unnecessary_changes']} |"
        )
    lines.extend(["", "Per-call latency and each team span (including executor queue between that team's first start and last finish) are preserved in `summary.json`. Reviewer discovery overlap is not counted as a duplicate; only duplicate findings left in the final synthesis are scored.", "", "This two-seed sample cannot establish a universally best model or reviewer count. `luna-xhigh-5` remains the user-approved default independently of this benchmark.", ""])
    rendered = "\n".join(lines)
    path = Path(output).resolve() / "controlled/report.md"
    path.write_text(rendered, encoding="utf-8")
    path.chmod(0o600)
    return rendered


def parse_args(argv: Sequence[str]) -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    sub = parser.add_subparsers(dest="command", required=True)
    prepare_parser = sub.add_parser("prepare")
    prepare_parser.add_argument("--output", type=Path, required=True)
    for name in ("workers", "adjudicators"):
        child = sub.add_parser(name)
        child.add_argument("--output", type=Path, required=True)
        child.add_argument("--cohort-id")
        child.add_argument("--jobs", type=int, default=4)
        child.add_argument("--timeout", type=int, default=900)
    summary_parser = sub.add_parser("summary")
    summary_parser.add_argument("--output", type=Path, required=True)
    summary_parser.add_argument("--adjudication", type=Path)
    template_parser = sub.add_parser("adjudication-template")
    template_parser.add_argument("--output", type=Path, required=True)
    template_parser.add_argument("--destination", type=Path, required=True)
    report_parser = sub.add_parser("report")
    report_parser.add_argument("--output", type=Path, required=True)
    report_parser.add_argument("--adjudication", type=Path)
    return parser.parse_args(argv)


def main(argv: Sequence[str] | None = None) -> int:
    args = parse_args(argv or [])
    try:
        if args.command == "prepare":
            value = prepare(args.output)
        elif args.command == "workers":
            value = run_workers(args.output, args.cohort_id, args.jobs, args.timeout)
        elif args.command == "adjudicators":
            value = run_adjudicators(args.output, args.cohort_id, args.jobs, args.timeout)
        elif args.command == "summary":
            value = summary(args.output, args.adjudication)
        elif args.command == "adjudication-template":
            value = make_adjudication_template(args.output, args.destination)
        else:
            print(report(args.output, args.adjudication))
            return 0
        print(runner.encoded_json(value))
        return 0
    except runner.EvaluationError as exc:
        print(f"error: {exc}", file=sys.stderr)
        return 2


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
