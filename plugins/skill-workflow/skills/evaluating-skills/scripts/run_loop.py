#!/usr/bin/env python3
# Modified from anthropics/skills@b9e19e6 skills/skill-creator/scripts/run_loop.py (Apache-2.0, see LICENSE.txt): measures triggers in omp and Codex instead of Claude Code, merges per-client results, selects the candidate with the best weakest-client held-out score, and checks the Python version.
"""Run the eval + improve loop until all pass or max iterations reached.

Combines run_trigger_eval.py and improve_description.py in a loop, tracking
history and returning the best description found. Supports train/test split to
prevent overfitting. Every query is measured in each selected client; a query
passes only when it passes in all of them.
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
import random
import tempfile
import time
import webbrowser

from scripts.clients import get_client
from scripts.clients.base import Settings
from scripts.evalsets import EvalSetError, load_queries
from scripts.generate_report import generate_html
from scripts.improve_description import improve_description
from scripts.run_trigger_eval import preflight, run_trigger_eval, setup_problem
from scripts.utils import parse_skill_md

CLIENT_NAMES = ("omp", "codex")
IMPROVER_TIMEOUT = 600


def split_eval_set(eval_set: list[dict], holdout: float, seed: int = 42) -> tuple[list[dict], list[dict]]:
    """Split eval set into train and test sets, stratified by should_trigger."""
    random.seed(seed)

    # Separate by should_trigger
    trigger = [e for e in eval_set if e["should_trigger"]]
    no_trigger = [e for e in eval_set if not e["should_trigger"]]

    # Shuffle each group
    random.shuffle(trigger)
    random.shuffle(no_trigger)

    # Calculate split points
    n_trigger_test = max(1, int(len(trigger) * holdout))
    n_no_trigger_test = max(1, int(len(no_trigger) * holdout))

    # Split
    test_set = trigger[:n_trigger_test] + no_trigger[:n_no_trigger_test]
    train_set = trigger[n_trigger_test:] + no_trigger[n_no_trigger_test:]

    return train_set, test_set


def merge_results(per_client: dict) -> list:
    """Combine per-client trigger results query by query."""
    names = list(per_client)
    merged = []
    for position, first in enumerate(per_client[names[0]]["results"]):
        rows = {name: per_client[name]["results"][position] for name in names}
        triggers = sum(r["triggers"] for r in rows.values())
        runs = sum(r["runs"] for r in rows.values())
        merged.append({
            "query": first["query"],
            "should_trigger": first["should_trigger"],
            "triggers": triggers,
            "runs": runs,
            "errors": sum(r["errors"] for r in rows.values()),
            "trigger_rate": triggers / runs if runs else None,
            "pass": all(r["pass"] for r in rows.values()),
            # A query no run measured in some client is not a real failure.
            "unmeasured": any(r["runs"] == 0 for r in rows.values()),
            "clients": {
                name: {key: r[key] for key in ("triggers", "runs", "errors", "trigger_rate", "pass")}
                for name, r in rows.items()
            },
        })
    return merged


def select_best(history: list, has_test: bool) -> dict:
    """Pick the iteration whose weakest client scores best, then the best total.

    Ties keep the earliest iteration.
    """
    key = "test_passed" if has_test else "train_passed"

    def score(entry: dict) -> tuple:
        values = [scores[key] or 0 for scores in entry["client_scores"].values()]
        return (min(values), sum(values))

    return max(history, key=score)


def _summary(results: list) -> dict:
    passed = sum(1 for r in results if r["pass"])
    return {"passed": passed, "failed": len(results) - passed, "total": len(results)}


def run_loop(
    eval_set: list[dict],
    skill_path: Path,
    description_override: str | None,
    clients: dict,
    improver: str,
    num_workers: int,
    max_iterations: int,
    runs_per_query: int,
    trigger_threshold: float,
    max_tool_calls: int,
    holdout: float,
    verbose: bool,
    live_report_path: Path | None = None,
    log_dir: Path | None = None,
) -> dict:
    """Run the eval + improvement loop.

    clients maps a client name to (client, Settings); improver names the
    client whose model rewrites the description.
    """
    name, original_description, content = parse_skill_md(skill_path)
    current_description = description_override or original_description
    improver_client, improver_settings = clients[improver]
    improver_settings = Settings(improver_settings.model, improver_settings.effort,
                                 improver_settings.home, max(improver_settings.timeout, IMPROVER_TIMEOUT))

    # Split into train/test if holdout > 0
    if holdout > 0:
        train_set, test_set = split_eval_set(eval_set, holdout)
        if verbose:
            print(f"Split: {len(train_set)} train, {len(test_set)} test (holdout={holdout})", file=sys.stderr)
    else:
        train_set = eval_set
        test_set = []

    history = []
    exit_reason = "unknown"
    unmeasured = 0

    for iteration in range(1, max_iterations + 1):
        if verbose:
            print(f"\n{'='*60}", file=sys.stderr)
            print(f"Iteration {iteration}/{max_iterations}", file=sys.stderr)
            print(f"Description: {current_description}", file=sys.stderr)
            print(f"{'='*60}", file=sys.stderr)

        # 1. Measure train and test queries together in each client, one
        #    client at a time so their runs do not compete for workers.
        all_queries = train_set + test_set
        t0 = time.time()
        per_client = {}
        for client_name, (client, settings) in clients.items():
            per_client[client_name] = run_trigger_eval(
                client, settings, skill_path, name, current_description, all_queries,
                runs_per_query, trigger_threshold, max_tool_calls, num_workers, verbose)
            unmeasured += len(per_client[client_name]["errors"])
        eval_elapsed = time.time() - t0

        # 2. Merge clients, then split back into train/test by query text.
        merged = merge_results(per_client)
        train_queries_set = {q["query"] for q in train_set}
        train_result_list = [r for r in merged if r["query"] in train_queries_set]
        test_result_list = [r for r in merged if r["query"] not in train_queries_set]
        train_summary = _summary(train_result_list)
        train_results = {"results": train_result_list, "summary": train_summary}
        if test_set:
            test_summary = _summary(test_result_list)
            test_results = {"results": test_result_list, "summary": test_summary}
        else:
            test_results = None
            test_summary = None

        client_scores = {}
        for client_name in clients:
            train_rows = [r["clients"][client_name] for r in train_result_list]
            test_rows = [r["clients"][client_name] for r in test_result_list]
            client_scores[client_name] = {
                "train_passed": sum(1 for r in train_rows if r["pass"]),
                "train_total": len(train_rows),
                "test_passed": sum(1 for r in test_rows if r["pass"]) if test_set else None,
                "test_total": len(test_rows) if test_set else None,
            }

        history.append({
            "iteration": iteration,
            "description": current_description,
            "train_passed": train_summary["passed"],
            "train_failed": train_summary["failed"],
            "train_total": train_summary["total"],
            "train_results": train_results["results"],
            "test_passed": test_summary["passed"] if test_summary else None,
            "test_failed": test_summary["failed"] if test_summary else None,
            "test_total": test_summary["total"] if test_summary else None,
            "test_results": test_results["results"] if test_results else None,
            # For backward compat with report generator
            "passed": train_summary["passed"],
            "failed": train_summary["failed"],
            "total": train_summary["total"],
            "results": train_results["results"],
            "client_scores": client_scores,
        })

        # Write live report if path provided
        if live_report_path:
            partial_output = {
                "original_description": original_description,
                "best_description": current_description,
                "best_iteration": select_best(history, bool(test_set))["iteration"],
                "best_score": "in progress",
                "iterations_run": len(history),
                "holdout": holdout,
                "train_size": len(train_set),
                "test_size": len(test_set),
                "history": history,
            }
            live_report_path.write_text(generate_html(partial_output, auto_refresh=True, skill_name=name))

        if verbose:
            def print_eval_stats(label, results, elapsed):
                pos = [r for r in results if r["should_trigger"]]
                neg = [r for r in results if not r["should_trigger"]]
                tp = sum(r["triggers"] for r in pos)
                pos_runs = sum(r["runs"] for r in pos)
                fn = pos_runs - tp
                fp = sum(r["triggers"] for r in neg)
                neg_runs = sum(r["runs"] for r in neg)
                tn = neg_runs - fp
                total = tp + tn + fp + fn
                precision = tp / (tp + fp) if (tp + fp) > 0 else 1.0
                recall = tp / (tp + fn) if (tp + fn) > 0 else 1.0
                accuracy = (tp + tn) / total if total > 0 else 0.0
                print(f"{label}: {tp+tn}/{total} correct, precision={precision:.0%} recall={recall:.0%} accuracy={accuracy:.0%} ({elapsed:.1f}s)", file=sys.stderr)
                for r in results:
                    status = "PASS" if r["pass"] else "FAIL"
                    rate_str = f"{r['triggers']}/{r['runs']}"
                    print(f"  [{status}] rate={rate_str} expected={r['should_trigger']}: {r['query'][:60]}", file=sys.stderr)

            print_eval_stats("Train", train_results["results"], eval_elapsed)
            if test_summary:
                print_eval_stats("Test ", test_results["results"], 0)

        if train_summary["failed"] == 0:
            exit_reason = f"all_passed (iteration {iteration})"
            if verbose:
                print(f"\nAll train queries passed on iteration {iteration}!", file=sys.stderr)
            break

        if iteration == max_iterations:
            exit_reason = f"max_iterations ({max_iterations})"
            if verbose:
                print(f"\nMax iterations reached ({max_iterations}).", file=sys.stderr)
            break

        # 3. Improve the description from train results only.
        if verbose:
            print(f"\nImproving description...", file=sys.stderr)

        t0 = time.time()
        # Strip test scores from history so improvement model can't see them
        blinded_history = []
        for h in history:
            entry = {k: v for k, v in h.items() if not k.startswith("test_") and k != "client_scores"}
            entry["client_scores"] = {
                client_name: {k: v for k, v in scores.items() if not k.startswith("test_")}
                for client_name, scores in h["client_scores"].items()
            }
            blinded_history.append(entry)
        try:
            new_description = improve_description(
                skill_name=name,
                skill_content=content,
                current_description=current_description,
                eval_results=train_results,
                history=blinded_history,
                complete=lambda prompt: improver_client.complete(prompt, improver_settings),
                log_dir=log_dir,
                iteration=iteration,
            )
        except RuntimeError as error:
            # Keep the iterations measured so far instead of losing them.
            exit_reason = f"improver_failed (iteration {iteration}): {error}"
            break
        improve_elapsed = time.time() - t0

        if verbose:
            print(f"Proposed ({improve_elapsed:.1f}s): {new_description}", file=sys.stderr)

        # A candidate a client refuses to load would measure as never
        # triggering, so it must not be measured, let alone selected.
        problems = [f"{client_name}: {problem}" for client_name, (client, settings) in clients.items()
                    if (problem := setup_problem(client, settings, skill_path, name, new_description))]
        if problems:
            exit_reason = f"candidate_not_loadable (iteration {iteration + 1}): {'; '.join(problems)}"
            break

        current_description = new_description

    # 4. Pick the iteration with the best held-out score in its weakest client
    #    (train score if there is no test set).
    best = select_best(history, bool(test_set))
    if test_set:
        best_score = f"{best['test_passed']}/{best['test_total']}"
    else:
        best_score = f"{best['train_passed']}/{best['train_total']}"

    if verbose:
        print(f"\nExit reason: {exit_reason}", file=sys.stderr)
        print(f"Best score: {best_score} (iteration {best['iteration']})", file=sys.stderr)

    return {
        "best_iteration": best["iteration"],
        "exit_reason": exit_reason,
        "original_description": original_description,
        "best_description": best["description"],
        "best_score": best_score,
        "best_train_score": f"{best['train_passed']}/{best['train_total']}",
        "best_test_score": f"{best['test_passed']}/{best['test_total']}" if test_set else None,
        "final_description": current_description,
        "iterations_run": len(history),
        "holdout": holdout,
        "train_size": len(train_set),
        "test_size": len(test_set),
        "history": history,
        "clients": list(clients),
        "best_client_scores": best["client_scores"],
        "unmeasured_runs": unmeasured,
    }


def main():
    parser = argparse.ArgumentParser(description="Run eval + improve loop")
    parser.add_argument("--skill-path", required=True, help="Path to skill directory")
    parser.add_argument("--eval-set", default=None, help="Path to eval set JSON file (default: <skill>/evals/eval_queries.json)")
    parser.add_argument("--clients", required=True, help="Comma-separated clients to measure: omp, codex")
    for client_name in CLIENT_NAMES:
        parser.add_argument(f"--{client_name}-model", default=None, help=f"Model for {client_name}")
        parser.add_argument(f"--{client_name}-effort", default=None, help=f"Reasoning effort for {client_name}")
        parser.add_argument(f"--{client_name}-home", default=None, help=f"Dedicated {client_name} home")
    parser.add_argument("--improver", default=None, help="Client whose model rewrites the description (default: first of --clients)")
    parser.add_argument("--description", default=None, help="Override starting description")
    parser.add_argument("--workers", type=int, default=4, help="Number of parallel runs per client")
    parser.add_argument("--timeout", type=int, default=180, help="Timeout per query in seconds")
    parser.add_argument("--max-tool-calls", type=int, default=3, help="Tool calls without reading the skill that count as not triggered")
    parser.add_argument("--max-iterations", type=int, default=5, help="Max improvement iterations")
    parser.add_argument("--runs-per-query", type=int, default=3, help="Number of runs per query")
    parser.add_argument("--trigger-threshold", type=float, default=0.5, help="Trigger rate threshold")
    parser.add_argument("--holdout", type=float, default=0.4, help="Fraction of eval set to hold out for testing (0 to disable)")
    parser.add_argument("--verbose", action="store_true", help="Print progress to stderr")
    parser.add_argument("--report", default="auto", help="Generate HTML report at this path (default: 'auto' for temp file, 'none' to disable)")
    parser.add_argument("--results-dir", default=None, help="Save all outputs (results.json, report.html, log.txt) to a timestamped subdirectory here")
    args = parser.parse_args()

    skill_path = Path(args.skill_path).resolve()
    if not (skill_path / "SKILL.md").exists():
        print(f"Error: No SKILL.md found at {skill_path}", file=sys.stderr)
        sys.exit(1)

    # Every selected client needs its own model, effort, and dedicated home.
    names = [n.strip() for n in args.clients.split(",") if n.strip()]
    if not names or any(n not in CLIENT_NAMES for n in names) or len(set(names)) != len(names):
        print(f"Error: --clients must list distinct clients from {', '.join(CLIENT_NAMES)}", file=sys.stderr)
        sys.exit(1)
    clients = {}
    for client_name in names:
        values = [getattr(args, f"{client_name}_{field}") for field in ("model", "effort", "home")]
        if not all(values):
            print(f"Error: --{client_name}-model, --{client_name}-effort, and --{client_name}-home are required", file=sys.stderr)
            sys.exit(1)
        model, effort, home = values
        clients[client_name] = (get_client(client_name),
                                Settings(model, effort, Path(home).expanduser().resolve(), args.timeout))
    improver = args.improver or names[0]
    if improver not in clients:
        print("Error: --improver must be one of --clients", file=sys.stderr)
        sys.exit(1)

    try:
        eval_set = load_queries(Path(args.eval_set) if args.eval_set else skill_path / "evals" / "eval_queries.json")
    except EvalSetError as error:
        print(f"Error: {error}", file=sys.stderr)
        sys.exit(1)

    name, current, _ = parse_skill_md(skill_path)

    # Check every client's home and trigger setup before spending model calls.
    for client_name, (client, settings) in clients.items():
        problem = preflight(client, settings, skill_path, name, args.description or current)
        if problem:
            print(f"Error: [{client_name}] {problem}", file=sys.stderr)
            sys.exit(1)

    # Set up live report path
    if args.report != "none":
        if args.report == "auto":
            timestamp = time.strftime("%Y%m%d_%H%M%S")
            live_report_path = Path(tempfile.gettempdir()) / f"skill_description_report_{skill_path.name}_{timestamp}.html"
        else:
            live_report_path = Path(args.report)
        # Open the report immediately so the user can watch
        live_report_path.write_text("<html><body><h1>Starting optimization loop...</h1><meta http-equiv='refresh' content='5'></body></html>")
        webbrowser.open(str(live_report_path))
    else:
        live_report_path = None

    # Determine output directory (create before run_loop so logs can be written)
    if args.results_dir:
        timestamp = time.strftime("%Y-%m-%d_%H%M%S")
        results_dir = Path(args.results_dir) / timestamp
        results_dir.mkdir(parents=True, exist_ok=True)
    else:
        results_dir = None

    log_dir = results_dir / "logs" if results_dir else None

    output = run_loop(
        eval_set=eval_set,
        skill_path=skill_path,
        description_override=args.description,
        clients=clients,
        improver=improver,
        num_workers=args.workers,
        max_iterations=args.max_iterations,
        runs_per_query=args.runs_per_query,
        trigger_threshold=args.trigger_threshold,
        max_tool_calls=args.max_tool_calls,
        holdout=args.holdout,
        verbose=args.verbose,
        live_report_path=live_report_path,
        log_dir=log_dir,
    )

    # Save JSON output
    json_output = json.dumps(output, indent=2)
    print(json_output)
    if results_dir:
        (results_dir / "results.json").write_text(json_output)

    # Write final HTML report (without auto-refresh)
    if live_report_path:
        live_report_path.write_text(generate_html(output, auto_refresh=False, skill_name=name))
        print(f"\nReport: {live_report_path}", file=sys.stderr)

    if results_dir and live_report_path:
        (results_dir / "report.html").write_text(generate_html(output, auto_refresh=False, skill_name=name))

    if results_dir:
        print(f"Results saved to: {results_dir}", file=sys.stderr)

    if output["unmeasured_runs"]:
        print(f"{output['unmeasured_runs']} runs were not measured", file=sys.stderr)
        sys.exit(2)


if __name__ == "__main__":
    main()
