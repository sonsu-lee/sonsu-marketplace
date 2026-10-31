#!/usr/bin/env python3
"""Grade each measured run of an iteration against its eval's assertions.

The iteration's own client and model grade each run in one tool-less call
that receives agents/grader.md, the assertions, the eval prompt, the
transcript, and the output files, and the result is written to grading.json.
Runs already graded against the current assertions are skipped, so rerunning
grades only what is missing or out of date.

Exit status: 0 when every measured run with assertions is graded, 1 for
invalid input, 2 when some runs could not be graded (rerun to retry).
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
from concurrent.futures import ThreadPoolExecutor

from scripts.clients import get_client
from scripts.clients.base import Settings
from scripts.evalsets import load_evals

SKILL_ROOT = Path(__file__).resolve().parent.parent
# Prompts travel as one argv string, which Linux limits to 128 KiB.
PROMPT_LIMIT = 100_000
FILE_LIMIT = 20_000
INSTRUCTIONS = (
    "You are running without tools; all inputs are inlined below. Return only one "
    "JSON object with `expectations` (same order and count as the input, each "
    "`{text, passed, evidence}`), and optionally `claims` and `eval_feedback`."
)


def clip(text: str, limit: int) -> str:
    if len(text) <= limit:
        return text
    return text[: limit // 3] + f"\n[... {len(text) - limit} chars omitted ...]\n" + text[-limit * 2 // 3:]


def build_prompt(grader: str, assertions: list, prompt: str, transcript: str,
                 outputs: Path) -> str:
    # 1. Grader instructions, then the tool-less contract that replaces its
    #    file-reading and file-writing steps.
    head = f"{grader}\n\n---\n\n{INSTRUCTIONS}\n\n## Expectations\n\n"
    head += "\n".join(f"{i}. {text}" for i, text in enumerate(assertions, 1))
    head += f"\n\n## Eval prompt\n\n{prompt}\n\n## Transcript\n\n{clip(transcript, 60_000)}"
    head += "\n\n## Output files\n"
    # 2. Output files last, so the size limit drops them before the transcript.
    sections = []
    for path in sorted(p for p in outputs.rglob("*") if p.is_file() and p.name != "metrics.json"):
        relative = path.relative_to(outputs).as_posix()
        try:
            body = f"````text\n{clip(path.read_text(encoding='utf-8'), FILE_LIMIT)}\n````"
        except UnicodeDecodeError:
            body = f"(binary file, {path.stat().st_size} bytes)"
        sections.append(f"\n### {relative}\n\n{body}\n")
    while sections and len((head + "".join(sections)).encode("utf-8")) > PROMPT_LIMIT:
        sections.pop()
    return head + ("".join(sections) or "\n(no output files)\n")


def parse_grading(text: str, assertions: list) -> dict:
    """Take the first JSON object with expectations and recompute its summary."""
    decoder = json.JSONDecoder()
    for index in (i for i, char in enumerate(text) if char == "{"):
        try:
            found, _ = decoder.raw_decode(text, index)
        except json.JSONDecodeError:
            continue
        if isinstance(found, dict) and "expectations" in found:
            break
    else:
        raise ValueError("no JSON object with expectations in the grader response")
    items = found["expectations"]
    if len(items) != len(assertions):
        raise ValueError(f"expected {len(assertions)} expectations, got {len(items)}")
    expectations = [{"text": a, "passed": bool(i["passed"]), "evidence": str(i["evidence"])}
                    for i, a in zip(items, assertions)]
    passed = sum(e["passed"] for e in expectations)
    result = {"expectations": expectations,
              "summary": {"passed": passed, "failed": len(expectations) - passed,
                          "total": len(expectations),
                          "pass_rate": round(passed / len(expectations), 4)}}
    result.update({k: found[k] for k in ("claims", "eval_feedback") if k in found})
    return result


def grade_run(client, settings: Settings, grader: str, metadata: dict, run_dir: Path) -> bool:
    label = f"[grade] {run_dir.parent.parent.name} {run_dir.parent.name} {run_dir.name}"
    prompt = build_prompt(grader, metadata["assertions"], metadata["prompt"],
                          (run_dir / "transcript.md").read_text(encoding="utf-8"),
                          run_dir / "outputs")
    try:
        grading = parse_grading(client.complete(prompt, settings), metadata["assertions"])
    except (RuntimeError, ValueError, KeyError, TypeError) as error:
        print(f"{label}: error: {error}", flush=True)
        return False
    grading["execution_metrics"] = json.loads((run_dir / "outputs" / "metrics.json").read_text())
    grading["grader"] = {"client": client.name, "model": settings.model, "effort": settings.effort}
    (run_dir / "grading.json").write_text(json.dumps(grading, indent=2, ensure_ascii=False) + "\n",
                                          encoding="utf-8")
    print(f"{label}: {grading['summary']['passed']}/{grading['summary']['total']} passed", flush=True)
    return True


def main() -> None:
    parser = argparse.ArgumentParser(description="Grade an iteration's runs against assertions")
    parser.add_argument("iteration_dir", type=Path)
    parser.add_argument("--workers", type=int, default=4)
    parser.add_argument("--timeout", type=int, default=600)
    args = parser.parse_args()

    iteration_dir = args.iteration_dir.resolve()
    record = json.loads((iteration_dir / "iteration.json").read_text())
    client = get_client(record["client"])
    settings = Settings(record["model"], record["effort"], Path(record["home"]), args.timeout)
    grader = (SKILL_ROOT / "agents" / "grader.md").read_text(encoding="utf-8")
    # 1. Take assertions from the current evals.json; they are usually
    #    finalized after the first runs.
    cases = {c["id"]: c for c in load_evals(Path(record["skill_path"]))["evals"]}

    # 2. Queue measured runs whose grading is missing or used other assertions.
    jobs = []
    for eval_dir in sorted(iteration_dir.glob("eval-*")):
        metadata_path = eval_dir / "eval_metadata.json"
        metadata = json.loads(metadata_path.read_text(encoding="utf-8"))
        metadata["assertions"] = cases[metadata["eval_id"]].get("assertions", [])
        metadata_path.write_text(json.dumps(metadata, indent=2, ensure_ascii=False) + "\n",
                                 encoding="utf-8")
        if not metadata["assertions"]:
            print(f"[grade] {eval_dir.name}: no assertions yet; add them to evals.json")
        for run_dir in sorted(eval_dir.glob("*/run-*")):
            grading_path = run_dir / "grading.json"
            if grading_path.is_file():
                texts = [e["text"] for e in json.loads(grading_path.read_text())["expectations"]]
                if texts == metadata["assertions"]:
                    continue
                grading_path.unlink()
            timing = json.loads((run_dir / "timing.json").read_text())
            if metadata["assertions"] and timing.get("error") is None:
                jobs.append((metadata, run_dir))

    # 3. Grade them.
    with ThreadPoolExecutor(max_workers=args.workers) as pool:
        outcomes = list(pool.map(lambda job: grade_run(client, settings, grader, *job), jobs))
    print(f"graded {outcomes.count(True)} of {len(jobs)} runs in {iteration_dir}")
    if not all(outcomes):
        sys.exit(2)


if __name__ == "__main__":
    main()
