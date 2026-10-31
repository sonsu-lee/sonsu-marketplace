#!/usr/bin/env python3
"""Run a skill's evals/evals.json with the skill and with a baseline.

Each eval runs in a fresh session and a temporary git directory, once per
configuration and repetition, and writes skill-creator's workspace layout:
<workspace>/<client>/iteration-N/eval-<id>/<config>/run-<r>/.

Exit status: 0 when every run was measured, 1 for invalid input, 2 when some
runs were not measured. Rerun the same command to retry failed runs.
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
import hashlib
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
from scripts.evalsets import (
    EvalSetError, copy_inputs, default_workspace, load_evals, lock_iteration,
)
from scripts.utils import parse_skill_md

RUNNER_FILES = {"final_message.md", "metrics.json"}
WORKDIR_OUTPUTS = "working-directory"
# A rerun into an existing iteration must match all of these, including the
# content of the skill, its previous version, and the eval prompts and inputs.
MATCHED_KEYS = ("client", "model", "effort", "home", "skill_path", "baseline", "runs",
                "skill_digest", "snapshot_digest", "plugin_digest", "cases_digest")
PRINT_LOCK = threading.Lock()


def say(message: str) -> None:
    with PRINT_LOCK:
        print(message, flush=True)


def build_brief(prompt: str, skill_dir, inputs: list, outputs_dir: Path) -> str:
    task = prompt.strip().replace("\n", "\n  ")
    lines = ["Execute this task:"]
    if skill_dir is not None:
        lines.append(f"- Skill path: {skill_dir}")
    lines.append(f"- Task: {task}")
    lines.append(f"- Input files: {', '.join(inputs) if inputs else 'none'}")
    lines.append(f"- Save outputs to: {outputs_dir}/")
    return "\n".join(lines)


def measured(run_dir: Path) -> bool:
    timing = run_dir / "timing.json"
    if not timing.is_file():
        return False
    try:
        return json.loads(timing.read_text()).get("error") is None
    except (json.JSONDecodeError, OSError):
        return False


def write_run(run_dir: Path, case: dict, brief: str, result, client: str,
              settings: Settings, error) -> None:
    outputs = run_dir / "outputs"
    (run_dir / "events.jsonl").write_text("\n".join(result.raw_lines) + "\n", encoding="utf-8")
    run_lines = [
        f"- Client: {client}",
        f"- Model: {result.model or 'not observed'} (requested {settings.model})",
        f"- Effort: {result.effort or 'not observed'} (requested {settings.effort})",
        f"- Duration: {result.duration_ms / 1000:.1f}s",
        f"- Tokens: {result.total_tokens}",
        f"- Error: {error or 'none'}",
    ]
    transcript = (
        f"## Eval Prompt\n\n{case['prompt']}\n\n## Brief\n\n{brief}\n\n"
        f"## Transcript\n\n{result.transcript or '(no events)'}\n\n"
        f"## Final Message\n\n{result.final_text or '(none)'}\n\n## Run\n\n"
        + "\n".join(run_lines) + "\n"
    )
    (run_dir / "transcript.md").write_text(transcript, encoding="utf-8")
    (outputs / "final_message.md").write_text(result.final_text, encoding="utf-8")
    created = sorted(str(p.relative_to(outputs)) for p in outputs.rglob("*")
                     if p.is_file() and p.relative_to(outputs).as_posix() not in RUNNER_FILES)
    output_chars = sum(p.stat().st_size for p in outputs.rglob("*")
                       if p.is_file() and p.name != "metrics.json")
    metrics = {
        "tool_calls": result.tool_calls,
        "total_tool_calls": sum(result.tool_calls.values()),
        "errors_encountered": result.tool_errors,
        "files_created": created,
        "output_chars": output_chars,
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


def file_digests(root: Path) -> dict:
    return {p.relative_to(root).as_posix(): hashlib.sha256(p.read_bytes()).hexdigest()
            for p in root.rglob("*")
            if p.is_file() and ".git" not in p.relative_to(root).parts}


def collect_outputs(scratch: Path, workdir: Path, inputs: dict, outputs: Path) -> None:
    """Move the agent's work into the run directory so the grader can see it."""
    shutil.copytree(scratch, outputs, dirs_exist_ok=True)
    # Files the agent created or changed in its working directory instead of
    # the outputs directory would otherwise be deleted with it.
    for relative, digest in file_digests(workdir).items():
        if inputs.get(relative) != digest:
            target = outputs / WORKDIR_OUTPUTS / relative
            target.parent.mkdir(parents=True, exist_ok=True)
            shutil.copy2(workdir / relative, target)


def run_one(client, settings: Settings, skill_dir: Path, case: dict, arm,
            run_dir: Path, run_number: int) -> bool:
    # 1. After an interrupt, leave queued runs and their earlier results alone.
    if INTERRUPTED.is_set():
        return False
    # 2. Start from an empty run directory so stale outputs cannot be graded.
    shutil.rmtree(run_dir, ignore_errors=True)
    outputs = run_dir / "outputs"
    outputs.mkdir(parents=True)
    label = f"[{client.name}] eval-{case['id']} {arm.config} run-{run_number}"
    workdir = scratch = None
    try:
        # 3. Give the agent a fresh git directory holding only the inputs, and
        #    a temporary outputs directory outside the workspace, whose eval
        #    metadata holds the expected output and assertions.
        workdir = init_workdir("skill-eval-")
        scratch = Path(tempfile.mkdtemp(prefix="skill-eval-outputs-")).resolve()
        copy_inputs(skill_dir, case.get("files", []), workdir)
        inputs = file_digests(workdir)
        brief = build_brief(case["prompt"], arm.skill_dir, sorted(inputs), scratch)
        # 4. Run the task, then reject runs on another model or effort.
        result = client.run_task(brief, workdir, scratch, arm, settings)
        error = result.error
        if error is None and result.model and not model_matches(settings.model, result.model):
            error = f"off-profile: ran {result.model}, requested {settings.model}"
        if error is None and result.effort and result.effort != settings.effort:
            error = f"off-profile: ran {result.effort}, requested {settings.effort}"
        # 5. Record everything, including failures, for review and retries.
        collect_outputs(scratch, workdir, inputs, outputs)
        write_run(run_dir, case, brief, result, client.name, settings, error)
    except Exception as exc:  # A crashed run stays unmeasured; others continue.
        error = f"{type(exc).__name__}: {exc}"
        (run_dir / "timing.json").write_text(json.dumps({"client": client.name, "error": error}, indent=2) + "\n")
        say(f"{label}: error: {error}")
        return False
    finally:
        for path in (workdir, scratch):
            if path is not None:
                shutil.rmtree(path, ignore_errors=True)
    if error:
        say(f"{label}: error: {error}")
        return False
    if not result.total_tokens:
        say(f"{label}: warning: no token usage reported")
    say(f"{label}: ok {result.duration_ms / 1000:.0f}s {result.total_tokens} tokens")
    return True


def tree_digest(root: Path, skip_evals: bool) -> str:
    """Hash a directory's files, ignoring caches, workspaces, and optionally evals/.

    With skip_evals, both a skill's own evals/ and, for a plugin root, each
    skills/<name>/evals/ are left out, since assertions may change freely.
    """
    digest = hashlib.sha256()
    for path in sorted(p for p in Path(root).rglob("*") if p.is_file()):
        parts = path.relative_to(root).parts
        if "__pycache__" in parts or any(part.endswith("-workspace") for part in parts):
            continue
        if skip_evals and (parts[0] == "evals"
                           or (parts[0] == "skills" and len(parts) > 2 and parts[2] == "evals")):
            continue
        digest.update("/".join(parts).encode() + b"\0" + path.read_bytes() + b"\0")
    return digest.hexdigest()


def cases_digest(skill_dir: Path, cases: list) -> str:
    """Hash what the runs depend on: prompts and input files, not assertions."""
    digest = hashlib.sha256(json.dumps(
        [[c["id"], c["prompt"], c.get("files", [])] for c in cases]).encode())
    files = skill_dir / "evals" / "files"
    if files.is_dir():
        digest.update(tree_digest(files, skip_evals=False).encode())
    return digest.hexdigest()


def prepare_iteration(iteration_dir: Path, record: dict) -> None:
    path = iteration_dir / "iteration.json"
    if path.is_file():
        existing = json.loads(path.read_text())
        changed = [key for key in MATCHED_KEYS if existing.get(key) != record.get(key)]
        if changed:
            sys.exit(f"{iteration_dir} was run with different {', '.join(changed)}; "
                     "use a new iteration number")
        return
    iteration_dir.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(record, indent=2) + "\n")


def main() -> None:
    parser = argparse.ArgumentParser(description="Run a skill's evals with and without the skill")
    parser.add_argument("--skill-path", required=True, type=Path)
    parser.add_argument("--client", required=True, choices=["omp", "codex"])
    parser.add_argument("--model", required=True)
    parser.add_argument("--effort", required=True)
    parser.add_argument("--home", required=True, type=Path, help="Dedicated client home")
    parser.add_argument("--iteration", required=True, type=int)
    parser.add_argument("--workspace", type=Path, default=None)
    parser.add_argument("--baseline", choices=["without", "old"], default="without")
    parser.add_argument("--runs", type=int, default=3)
    parser.add_argument("--eval-id", type=int, action="append", default=None)
    parser.add_argument("--workers", type=int, default=4)
    parser.add_argument("--timeout", type=int, default=900)
    parser.add_argument("--force", action="store_true", help="Rerun measured runs too")
    args = parser.parse_args()

    skill_dir = args.skill_path.resolve()
    home = args.home.expanduser().resolve()
    try:
        data = load_evals(skill_dir)
    except (EvalSetError, ValueError, OSError) as error:
        sys.exit(str(error))
    name = parse_skill_md(skill_dir)[0]
    client = get_client(args.client)
    settings = Settings(args.model, args.effort, home, args.timeout)

    # 1. Refuse homes where the skill is installed; it would load in the baseline.
    problem = check_home(client, settings, name)
    if problem:
        sys.exit(problem)

    # 2. Pin the iteration to one client, model, effort, home, and baseline.
    workspace = (args.workspace or default_workspace(name)).expanduser().resolve()
    snapshot = workspace / "skill-snapshot"
    # 3. A revision is compared with the snapshot of its previous version.
    if args.baseline == "old" and not (snapshot / "SKILL.md").is_file():
        sys.exit(f"--baseline old needs the previous version in {snapshot}")
    baseline = "old_skill" if args.baseline == "old" else "without_skill"
    iteration_dir = workspace / args.client / f"iteration-{args.iteration}"
    iteration_dir.mkdir(parents=True, exist_ok=True)
    # Two writers would mix their files into the same run directories.
    lock = lock_iteration(iteration_dir)
    plugin = plugin_root(skill_dir)
    prepare_iteration(iteration_dir, {
        "client": args.client, "model": args.model, "effort": args.effort,
        "home": str(home), "skill_path": str(skill_dir), "skill_name": name,
        "baseline": args.baseline, "runs": args.runs,
        "snapshot": str(snapshot) if args.baseline == "old" else None,
        "skill_digest": tree_digest(skill_dir, skip_evals=True),
        "snapshot_digest": tree_digest(snapshot, skip_evals=True) if args.baseline == "old" else None,
        # omp arms load the whole plugin, so its agents and sibling skills count.
        "plugin_digest": tree_digest(plugin, skip_evals=True) if plugin else None,
        "cases_digest": cases_digest(skill_dir, data["evals"]),
        "created": datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"),
    })

    cases = [c for c in data["evals"] if not args.eval_id or c["id"] in args.eval_id]
    if not cases:
        sys.exit("no evals match --eval-id")

    tmp = Path(tempfile.mkdtemp(prefix="skill-eval-arms-"))
    pool = ThreadPoolExecutor(max_workers=max(1, args.workers))
    try:
        # 4. Prepare skill copies without evals/ so answers cannot leak.
        arms = [client.prepare_arm("with_skill", skill_dir, tmp, plugin)]
        if baseline == "old_skill":
            arms.append(client.prepare_arm("old_skill", snapshot, tmp, plugin))
        else:
            # The plugin minus the evaluated skill, so that only the skill differs.
            arms.append(client.prepare_arm("without_skill", skill_dir, tmp, plugin))

        # 5. Record each eval's metadata for grading and the viewer.
        jobs = []
        for case in cases:
            eval_dir = iteration_dir / f"eval-{case['id']}"
            eval_dir.mkdir(parents=True, exist_ok=True)
            metadata = {
                "eval_id": case["id"], "eval_name": f"eval-{case['id']}",
                "prompt": case["prompt"], "expected_output": case["expected_output"],
                "files": case.get("files", []), "assertions": case.get("assertions", []),
            }
            (eval_dir / "eval_metadata.json").write_text(
                json.dumps(metadata, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
            # 6. Expand eval x configuration x repetition, skipping measured runs.
            for arm in arms:
                for number in range(1, args.runs + 1):
                    run_dir = eval_dir / arm.config / f"run-{number}"
                    if measured(run_dir) and not args.force:
                        continue
                    jobs.append((case, arm, run_dir, number))

        say(f"[{args.client}] {len(jobs)} runs to execute in {iteration_dir}")
        futures = [pool.submit(run_one, client, settings, skill_dir, *job) for job in jobs]
        # 7. On interrupt, end the client sessions first, so in-flight runs are
        #    recorded as unmeasured before their skill copies are removed.
        try:
            outcomes = [future.result() for future in futures]
        except KeyboardInterrupt:
            stop_all()
            pool.shutdown(wait=True, cancel_futures=True)
            print("interrupted; in-flight runs are recorded as unmeasured", file=sys.stderr)
            sys.exit(130)
    finally:
        pool.shutdown(wait=True)
        shutil.rmtree(tmp, ignore_errors=True)
        lock.close()

    print(iteration_dir)
    if not all(outcomes):
        print(f"{outcomes.count(False)} runs were not measured; rerun the same command to retry",
              file=sys.stderr)
        sys.exit(2)


if __name__ == "__main__":
    main()
