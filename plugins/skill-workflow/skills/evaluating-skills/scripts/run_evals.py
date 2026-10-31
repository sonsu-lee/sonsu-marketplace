#!/usr/bin/env python3
"""Run a skill's evals/evals.json with the skill and with a baseline.

Each eval runs once per configuration and repetition, in a fresh session and
an empty temporary git directory, and writes skill-creator's layout:
<workspace>/<client>/iteration-N/eval-<id>/<config>/run-<r>/.

Exit status: 0 when every run was measured, 1 for invalid input, 2 when some
runs were not measured (retry them with --resume), 130 when interrupted.
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
import tempfile
import threading
from concurrent.futures import ThreadPoolExecutor
from datetime import datetime, timezone

from scripts.clients import get_client
from scripts.clients.base import (
    INTERRUPTED, Settings, check_home, init_workdir, model_matches, plugin_root, stop_all,
)
from scripts.evalsets import EvalSetError, copy_inputs, default_workspace, load_evals
from scripts.utils import parse_skill_md

# A resumed iteration must have been started with the same settings.
SETTINGS_KEYS = ("client", "model", "effort", "home", "skill_path", "baseline", "runs")
PRINT_LOCK = threading.Lock()


def say(message: str) -> None:
    with PRINT_LOCK:
        print(message, flush=True)


def build_brief(prompt: str, skill_dir, inputs: list, outputs_dir: Path) -> str:
    lines = ["Execute this task:"]
    if skill_dir is not None:
        lines.append(f"- Skill path: {skill_dir}")
    lines.append(f"- Task: {prompt.strip().replace(chr(10), chr(10) + '  ')}")
    lines.append(f"- Input files: {', '.join(inputs) or 'none'}")
    lines.append(f"- Save outputs to: {outputs_dir}/")
    return "\n".join(lines)


def measured(run_dir: Path) -> bool:
    timing = run_dir / "timing.json"
    return timing.is_file() and json.loads(timing.read_text()).get("error") is None


def write_run(run_dir: Path, case: dict, brief: str, result, client: str,
              settings: Settings, error) -> None:
    outputs = run_dir / "outputs"
    (run_dir / "events.jsonl").write_text("\n".join(result.raw_lines) + "\n", encoding="utf-8")
    transcript = (
        f"## Eval Prompt\n\n{case['prompt']}\n\n## Brief\n\n{brief}\n\n"
        f"## Transcript\n\n{result.transcript or '(no events)'}\n\n"
        f"## Final Message\n\n{result.final_text or '(none)'}\n\n## Run\n\n"
        f"- Client: {client}\n- Model: {result.model} (requested {settings.model})\n"
        f"- Effort: {result.effort} (requested {settings.effort})\n"
        f"- Duration: {result.duration_ms / 1000:.1f}s\n- Tokens: {result.total_tokens}\n"
        f"- Error: {error or 'none'}\n"
    )
    (run_dir / "transcript.md").write_text(transcript, encoding="utf-8")
    created = sorted(p.relative_to(outputs).as_posix() for p in outputs.rglob("*") if p.is_file())
    (outputs / "final_message.md").write_text(result.final_text, encoding="utf-8")
    metrics = {
        "tool_calls": result.tool_calls,
        "total_tool_calls": sum(result.tool_calls.values()),
        "errors_encountered": result.tool_errors,
        "files_created": created,
        "output_chars": sum(p.stat().st_size for p in outputs.rglob("*") if p.is_file()),
        "transcript_chars": len(transcript),
    }
    (outputs / "metrics.json").write_text(json.dumps(metrics, indent=2) + "\n")
    timing = {
        "total_tokens": result.total_tokens,
        "duration_ms": result.duration_ms,
        "total_duration_seconds": round(result.duration_ms / 1000, 1),
        "client": client,
        "model_requested": settings.model,
        "model_observed": result.model,
        "effort_requested": settings.effort,
        "effort_observed": result.effort,
        "error": error,
    }
    (run_dir / "timing.json").write_text(json.dumps(timing, indent=2) + "\n")


def run_one(client, settings: Settings, skill_dir: Path, case: dict, arm,
            run_dir: Path, run_number: int) -> bool:
    label = f"[{client.name}] eval-{case['id']} {arm.config} run-{run_number}"
    # 1. After an interrupt, leave queued runs and their earlier files alone.
    if INTERRUPTED.is_set():
        return False
    # 2. Start from an empty run directory so stale outputs cannot be graded.
    shutil.rmtree(run_dir, ignore_errors=True)
    outputs = (run_dir / "outputs").resolve()
    outputs.mkdir(parents=True)
    workdir = init_workdir("skill-eval-")
    try:
        # 3. Run the task in an empty git directory holding only the inputs.
        inputs = copy_inputs(skill_dir, case.get("files", []), workdir)
        brief = build_brief(case["prompt"], arm.skill_dir, inputs, outputs)
        result = client.run_task(brief, workdir, outputs, arm, settings)
        # 4. A run on another model or effort does not count for this one.
        error = result.error
        if error is None and result.model and not model_matches(settings.model, result.model):
            error = f"off-profile: ran {result.model}, requested {settings.model}"
        if error is None and result.effort and result.effort != settings.effort:
            error = f"off-profile: ran {result.effort} effort, requested {settings.effort}"
        write_run(run_dir, case, brief, result, client.name, settings, error)
    except Exception as exc:  # A crashed run stays unmeasured; the others go on.
        error = f"{type(exc).__name__}: {exc}"
        (run_dir / "timing.json").write_text(json.dumps({"client": client.name, "error": error}) + "\n")
    finally:
        shutil.rmtree(workdir, ignore_errors=True)
    say(f"{label}: " + (f"error: {error}" if error else
                        f"ok {result.duration_ms / 1000:.0f}s {result.total_tokens} tokens"))
    return error is None


def main() -> None:
    parser = argparse.ArgumentParser(description="Run a skill's evals with and without the skill")
    parser.add_argument("--skill-path", required=True, type=Path)
    parser.add_argument("--client", required=True, choices=["omp", "codex"])
    parser.add_argument("--model", required=True)
    parser.add_argument("--effort", required=True)
    parser.add_argument("--home", required=True, type=Path, help="Dedicated client home")
    parser.add_argument("--iteration", required=True, type=int)
    parser.add_argument("--resume", action="store_true",
                        help="Retry the unmeasured runs of an existing iteration")
    parser.add_argument("--workspace", type=Path, default=None)
    parser.add_argument("--baseline", choices=["without", "old"], default="without")
    parser.add_argument("--runs", type=int, default=3)
    parser.add_argument("--eval-id", type=int, action="append", default=None)
    parser.add_argument("--workers", type=int, default=4)
    parser.add_argument("--timeout", type=int, default=900)
    args = parser.parse_args()

    # 1. Read the evals and refuse a home where the skill is installed,
    #    because it would load in the baseline runs too.
    skill_dir = args.skill_path.resolve()
    try:
        data = load_evals(skill_dir)
    except (EvalSetError, OSError, json.JSONDecodeError) as error:
        sys.exit(str(error))
    name = parse_skill_md(skill_dir)[0]
    client = get_client(args.client)
    settings = Settings(args.model, args.effort, args.home.expanduser().resolve(), args.timeout)
    problem = check_home(client, settings, name)
    if problem:
        sys.exit(problem)

    # 2. Start a new iteration, or resume one started with the same settings.
    #    The workspace outlives sessions, so reusing a number by accident would
    #    otherwise report the earlier runs as this evaluation.
    workspace = (args.workspace or default_workspace(name)).expanduser().resolve()
    snapshot = workspace / "skill-snapshot"
    if args.baseline == "old" and not (snapshot / "SKILL.md").is_file():
        sys.exit(f"--baseline old needs the previous version in {snapshot}")
    iteration_dir = workspace / args.client / f"iteration-{args.iteration}"
    record = {"client": args.client, "model": args.model, "effort": args.effort,
              "home": str(settings.home), "skill_path": str(skill_dir), "skill_name": name,
              "baseline": args.baseline, "runs": args.runs,
              "created": datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")}
    record_path = iteration_dir / "iteration.json"
    if record_path.is_file():
        if not args.resume:
            sys.exit(f"{iteration_dir} exists; use a new --iteration, or --resume to retry "
                     "its unmeasured runs")
        existing = json.loads(record_path.read_text())
        changed = [key for key in SETTINGS_KEYS if existing.get(key) != record[key]]
        if changed:
            sys.exit(f"{iteration_dir} was started with different {', '.join(changed)}")
    else:
        iteration_dir.mkdir(parents=True)
        record_path.write_text(json.dumps(record, indent=2) + "\n")

    tmp = Path(tempfile.mkdtemp(prefix="skill-eval-arms-"))
    pool = ThreadPoolExecutor(max_workers=args.workers)
    try:
        # 3. Copy the skill for each arm, without evals/.
        plugin = plugin_root(skill_dir)
        baseline = ("old_skill", snapshot) if args.baseline == "old" else ("without_skill", skill_dir)
        arms = [client.prepare_arm("with_skill", skill_dir, tmp, plugin),
                client.prepare_arm(*baseline, tmp, plugin)]

        # 4. Write each eval's metadata, then queue every unmeasured run.
        jobs = []
        for case in data["evals"]:
            if args.eval_id and case["id"] not in args.eval_id:
                continue
            eval_dir = iteration_dir / f"eval-{case['id']}"
            eval_dir.mkdir(exist_ok=True)
            metadata = {"eval_id": case["id"], "eval_name": f"eval-{case['id']}",
                        "prompt": case["prompt"], "expected_output": case["expected_output"],
                        "files": case.get("files", []), "assertions": case.get("assertions", [])}
            (eval_dir / "eval_metadata.json").write_text(
                json.dumps(metadata, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
            for arm in arms:
                for number in range(1, args.runs + 1):
                    run_dir = eval_dir / arm.config / f"run-{number}"
                    if not measured(run_dir):
                        jobs.append((case, arm, run_dir, number))

        # 5. Run them. On Ctrl-C, end the client sessions first, so in-flight
        #    runs are recorded as unmeasured before their skill copies go.
        say(f"[{args.client}] {len(jobs)} runs to execute in {iteration_dir}")
        futures = [pool.submit(run_one, client, settings, skill_dir, *job) for job in jobs]
        try:
            outcomes = [future.result() for future in futures]
        except KeyboardInterrupt:
            stop_all()
            pool.shutdown(wait=True, cancel_futures=True)
            sys.exit(130)
    finally:
        pool.shutdown(wait=True)
        shutil.rmtree(tmp, ignore_errors=True)

    print(iteration_dir)
    if not all(outcomes):
        print(f"{outcomes.count(False)} runs were not measured; rerun with --resume",
              file=sys.stderr)
        sys.exit(2)


if __name__ == "__main__":
    main()
