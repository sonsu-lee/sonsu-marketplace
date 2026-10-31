#!/usr/bin/env python3
"""Measure how often a skill's description triggers on a query set.

Each run places the candidate skill in a fresh temporary project for the
client, sends one query, and watches the client's events until the agent
reads the skill (triggered) or makes enough other tool calls, finishes, or
times out (not triggered).

Exit status: 0 when every run was measured, 1 for invalid input or a failed
preflight check, 2 when some runs were not measured.
"""

import shlex
import sys

if sys.version_info < (3, 11):
    sys.exit(
        "evaluating-skills needs Python 3.11 or newer, found "
        + sys.version.split()[0]
        + ". Run it as: uv run --no-project --python 3.12 python "
        + " ".join(shlex.quote(arg) for arg in sys.argv)
    )

from pathlib import Path

if __package__ in (None, ""):
    sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

import argparse
import json
import shutil
from concurrent.futures import ThreadPoolExecutor

from scripts.clients import get_client
from scripts.clients.base import ERROR, TRIGGERED, Settings, check_home, init_workdir
from scripts.evalsets import EvalSetError, load_queries
from scripts.utils import parse_skill_md


def preflight(client, settings: Settings, skill_dir: Path, name: str, description: str):
    """Return a problem string when the home or the trigger setup is unusable."""
    problem = check_home(client, settings, name)
    if problem:
        return problem
    workdir = init_workdir("skill-trigger-probe-")
    try:
        client.place_trigger_skill(workdir, skill_dir, name, description)
        return client.check_trigger_setup(workdir, name, settings)
    finally:
        shutil.rmtree(workdir, ignore_errors=True)


def measure(client, settings: Settings, skill_dir: Path, name: str, description: str,
            query: str, max_tool_calls: int):
    """Run one query in a fresh project, retrying once on a measurement error."""
    error = None
    for _ in range(2):
        workdir = init_workdir("skill-trigger-")
        try:
            skill_md = client.place_trigger_skill(workdir, skill_dir, name, description)
            status, error = client.detect_trigger(query, workdir, name, skill_md, settings,
                                                  max_tool_calls)
        except Exception as exc:  # One broken run must not stop the others.
            status, error = ERROR, f"{type(exc).__name__}: {exc}"
        finally:
            shutil.rmtree(workdir, ignore_errors=True)
        if status != ERROR:
            return status, None
    return ERROR, error


def run_trigger_eval(client, settings: Settings, skill_dir: Path, name: str, description: str,
                     queries: list, runs_per_query: int, threshold: float, max_tool_calls: int,
                     workers: int, verbose: bool) -> dict:
    jobs = [(index, item["query"]) for index, item in enumerate(queries)
            for _ in range(runs_per_query)]

    def work(job):
        index, query = job
        status, error = measure(client, settings, skill_dir, name, description, query,
                                max_tool_calls)
        if verbose:
            detail = f" ({error})" if error else ""
            print(f"[{client.name}] {status}{detail}: {query[:70]}", file=sys.stderr, flush=True)
        return index, status, error

    with ThreadPoolExecutor(max_workers=max(1, workers)) as pool:
        outcomes = list(pool.map(work, jobs))

    results = []
    error_messages = []
    for index, item in enumerate(queries):
        statuses = [(s, e) for i, s, e in outcomes if i == index]
        measured = [s for s, _ in statuses if s != ERROR]
        errors = [e for s, e in statuses if s == ERROR]
        error_messages += [f"{item['query'][:60]}: {e}" for e in errors]
        triggers = sum(1 for s in measured if s == TRIGGERED)
        runs = len(measured)
        rate = triggers / runs if runs else None
        if runs == 0:
            passed = False
        elif item["should_trigger"]:
            passed = rate >= threshold
        else:
            passed = rate < threshold
        results.append({
            "query": item["query"], "should_trigger": item["should_trigger"],
            "triggers": triggers, "runs": runs, "errors": len(errors),
            "trigger_rate": rate, "pass": passed, "error": runs == 0,
        })
    passed = sum(1 for r in results if r["pass"])
    return {
        "skill_name": name,
        "description": description,
        "client": client.name,
        "results": results,
        "summary": {"total": len(results), "passed": passed, "failed": len(results) - passed},
        "errors": error_messages,
    }


def main() -> None:
    parser = argparse.ArgumentParser(description="Measure description trigger rates")
    parser.add_argument("--skill-path", required=True, type=Path)
    parser.add_argument("--client", required=True, choices=["omp", "codex"])
    parser.add_argument("--model", required=True)
    parser.add_argument("--effort", required=True)
    parser.add_argument("--home", required=True, type=Path, help="Dedicated client home")
    parser.add_argument("--eval-set", type=Path, default=None,
                        help="Query set (default: <skill>/evals/eval_queries.json)")
    parser.add_argument("--description", default=None, help="Candidate description to test")
    parser.add_argument("--runs-per-query", type=int, default=3)
    parser.add_argument("--trigger-threshold", type=float, default=0.5)
    parser.add_argument("--max-tool-calls", type=int, default=3)
    parser.add_argument("--workers", type=int, default=4)
    parser.add_argument("--timeout", type=int, default=180)
    parser.add_argument("--output", type=Path, default=None)
    parser.add_argument("--verbose", action="store_true")
    args = parser.parse_args()

    skill_dir = args.skill_path.resolve()
    try:
        name, current, _ = parse_skill_md(skill_dir)
        queries = load_queries(args.eval_set or skill_dir / "evals" / "eval_queries.json")
    except (EvalSetError, ValueError, OSError) as error:
        sys.exit(str(error))
    description = args.description if args.description is not None else current
    client = get_client(args.client)
    settings = Settings(args.model, args.effort, args.home.expanduser().resolve(), args.timeout)

    problem = preflight(client, settings, skill_dir, name, description)
    if problem:
        sys.exit(problem)

    output = run_trigger_eval(client, settings, skill_dir, name, description, queries,
                              args.runs_per_query, args.trigger_threshold, args.max_tool_calls,
                              args.workers, args.verbose)
    text = json.dumps(output, indent=2, ensure_ascii=False)
    if args.output:
        args.output.write_text(text + "\n", encoding="utf-8")
    print(text)
    summary = output["summary"]
    print(f"[{args.client}] {summary['passed']}/{summary['total']} queries passed", file=sys.stderr)
    if output["errors"]:
        print(f"{len(output['errors'])} runs were not measured", file=sys.stderr)
        sys.exit(2)


if __name__ == "__main__":
    main()
