#!/usr/bin/env python3
"""Grade every measured run of an iteration against its eval's assertions.

Each run is graded by a tool-less model call that receives agents/grader.md,
the assertions, the eval prompt, the transcript, and the output files inline,
and writes grading.json next to the run's timing.json.

Exit status: 0 when every run with assertions was graded, 1 for invalid input,
2 when some runs could not be graded.
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
import threading
from concurrent.futures import ThreadPoolExecutor

from scripts.clients import get_client
from scripts.clients.base import MAX_PROMPT_BYTES, Settings
from scripts.evalsets import EvalSetError, load_evals

SKILL_ROOT = Path(__file__).resolve().parent.parent
TRANSCRIPT_LIMIT = 60_000
TRANSCRIPT_HEAD = 20_000
TRANSCRIPT_TAIL = 40_000
FILE_LIMIT = 20_000
SKIPPED_OUTPUTS = {"metrics.json"}
INSTRUCTIONS = (
    "You are running without tools; all inputs are inlined below. Return only one "
    "JSON object with `expectations` (same order and count as the input, each "
    "`{text, passed, evidence}`), and optionally `claims` and `eval_feedback`. "
    "Do not include `summary`, `timing`, or `execution_metrics`."
)
PRINT_LOCK = threading.Lock()


def say(message: str) -> None:
    with PRINT_LOCK:
        print(message, flush=True)


def _cut(data: bytes, limit: int) -> str:
    return data[:limit].decode("utf-8", errors="ignore")


def transcript_section(text: str) -> str:
    data = text.encode("utf-8")
    if len(data) <= TRANSCRIPT_LIMIT:
        return text
    head = _cut(data, TRANSCRIPT_HEAD)
    tail = data[-TRANSCRIPT_TAIL:].decode("utf-8", errors="ignore")
    omitted = len(data) - TRANSCRIPT_HEAD - TRANSCRIPT_TAIL
    return f"{head}\n\n[... {omitted} bytes of transcript omitted ...]\n\n{tail}"


def output_sections(outputs: Path) -> list:
    sections = []
    for path in sorted(p for p in outputs.rglob("*") if p.is_file()):
        relative = path.relative_to(outputs).as_posix()
        if relative in SKIPPED_OUTPUTS:
            continue
        data = path.read_bytes()
        try:
            if b"\x00" in data:
                raise UnicodeDecodeError("utf-8", data, 0, 1, "binary")
            data.decode("utf-8")
        except UnicodeDecodeError:
            sections.append(f"### {relative}\n\n(binary file, {len(data)} bytes)")
            continue
        body = _cut(data, FILE_LIMIT)
        if len(data) > FILE_LIMIT:
            body += f"\n[... {len(data) - FILE_LIMIT} more bytes omitted ...]"
        sections.append(f"### {relative}\n\n````text\n{body}\n````")
    return sections


def build_prompt(grader: str, assertions: list, prompt: str, transcript: str,
                 outputs: Path) -> str:
    # 1. Grader instructions first, then the tool-less contract that replaces
    #    the file-reading and file-writing steps grader.md describes.
    head = f"{grader}\n\n---\n\n{INSTRUCTIONS}\n\n## Expectations\n\n"
    head += "\n".join(f"{i}. {text}" for i, text in enumerate(assertions, 1))
    head += f"\n\n## Eval prompt\n\n{prompt}\n\n## Transcript\n\n{transcript_section(transcript)}"
    head += "\n\n## Output files\n\n"
    # 2. Output files go last so the size limit trims them, not the evidence
    #    trail; later files are cut first.
    files = output_sections(outputs)

    def render() -> str:
        return head + ("\n\n".join(files) if files else "(no output files)") + "\n"

    def too_big() -> bool:
        return len(render().encode("utf-8")) > MAX_PROMPT_BYTES

    index = len(files) - 1
    while too_big() and index >= 0:
        files[index] = files[index].split("\n", 1)[0] + "\n\n(omitted to fit the prompt size limit)"
        index -= 1
    while too_big() and files:
        files.pop()
    return render()


def parse_grading(text: str, assertions: list) -> dict:
    """Find the grader's JSON object and recompute its summary."""
    decoder = json.JSONDecoder()
    found = None
    for index, char in enumerate(text):
        if char != "{":
            continue
        try:
            value, _ = decoder.raw_decode(text, index)
        except json.JSONDecodeError:
            continue
        if isinstance(value, dict) and "expectations" in value:
            found = value
            break
    if found is None:
        raise ValueError("no JSON object with expectations in the grader response")
    items = found["expectations"]
    if not isinstance(items, list) or len(items) != len(assertions):
        raise ValueError(f"expected {len(assertions)} expectations, got "
                         f"{len(items) if isinstance(items, list) else type(items).__name__}")
    expectations = []
    for item, assertion in zip(items, assertions):
        if not isinstance(item, dict) or not isinstance(item.get("passed"), bool):
            raise ValueError("each expectation needs a boolean passed")
        if not isinstance(item.get("evidence"), str):
            raise ValueError("each expectation needs a string evidence")
        expectations.append({"text": assertion, "passed": item["passed"], "evidence": item["evidence"]})
    passed = sum(1 for e in expectations if e["passed"])
    total = len(expectations)
    result = {
        "expectations": expectations,
        "summary": {"passed": passed, "failed": total - passed, "total": total,
                    "pass_rate": round(passed / total, 4) if total else 0.0},
    }
    for key in ("claims", "eval_feedback"):
        if key in found:
            result[key] = found[key]
    return result


def grade_run(client, settings: Settings, grader: str, metadata: dict, run_dir: Path) -> bool:
    label = f"[grade] {run_dir.parent.parent.name} {run_dir.parent.name} {run_dir.name}"
    assertions = metadata["assertions"]
    try:
        prompt = build_prompt(grader, assertions, metadata["prompt"],
                              (run_dir / "transcript.md").read_text(encoding="utf-8"),
                              run_dir / "outputs")
    except (OSError, ValueError) as error:
        say(f"{label}: error: {error}")
        return False
    grading = None
    error = None
    # A malformed answer is retried once before the run counts as ungraded.
    for _ in range(2):
        try:
            grading = parse_grading(client.complete(prompt, settings), assertions)
            break
        except (RuntimeError, ValueError) as exc:
            error = exc
    if grading is None:
        say(f"{label}: error: {error}")
        return False
    metrics_path = run_dir / "outputs" / "metrics.json"
    grading["execution_metrics"] = json.loads(metrics_path.read_text()) if metrics_path.is_file() else {}
    grading["grader"] = {"client": client.name, "model": settings.model, "effort": settings.effort}
    ordered = {key: grading[key] for key in
               ("expectations", "summary", "execution_metrics", "claims", "eval_feedback", "grader")
               if key in grading}
    (run_dir / "grading.json").write_text(json.dumps(ordered, indent=2, ensure_ascii=False) + "\n",
                                          encoding="utf-8")
    summary = grading["summary"]
    say(f"{label}: {summary['passed']}/{summary['total']} passed")
    return True


def main() -> None:
    parser = argparse.ArgumentParser(description="Grade an iteration's runs against assertions")
    parser.add_argument("iteration_dir", type=Path)
    parser.add_argument("--client", choices=["omp", "codex"])
    parser.add_argument("--model")
    parser.add_argument("--effort")
    parser.add_argument("--home", type=Path)
    parser.add_argument("--workers", type=int, default=4)
    parser.add_argument("--timeout", type=int, default=600)
    parser.add_argument("--force", action="store_true", help="Regrade runs that already have grading.json")
    args = parser.parse_args()

    iteration_dir = args.iteration_dir.resolve()
    record_path = iteration_dir / "iteration.json"
    if not record_path.is_file():
        sys.exit(f"{record_path} not found; pass an iteration directory written by run_evals.py")
    record = json.loads(record_path.read_text())
    if args.client and args.client != record["client"] and not (args.model and args.effort and args.home):
        sys.exit("--client other than the iteration's needs --model, --effort, and --home")
    client = get_client(args.client or record["client"])
    home = args.home.expanduser().resolve() if args.home else Path(record["home"])
    settings = Settings(args.model or record["model"], args.effort or record["effort"],
                        home, args.timeout)

    # 1. Take assertions from the current evals.json; they are often added
    #    after the first runs.
    try:
        cases = {c["id"]: c for c in load_evals(Path(record["skill_path"]))["evals"]}
    except (EvalSetError, ValueError, OSError) as error:
        sys.exit(str(error))
    grader = (SKILL_ROOT / "agents" / "grader.md").read_text(encoding="utf-8")

    # 2. Select measured runs that still need grading.
    jobs = []
    for eval_dir in sorted(iteration_dir.glob("eval-*")):
        metadata_path = eval_dir / "eval_metadata.json"
        if not metadata_path.is_file():
            continue
        metadata = json.loads(metadata_path.read_text(encoding="utf-8"))
        case = cases.get(metadata.get("eval_id"))
        if case is not None:
            metadata["assertions"] = case.get("assertions", [])
            metadata_path.write_text(json.dumps(metadata, indent=2, ensure_ascii=False) + "\n",
                                     encoding="utf-8")
        if not metadata.get("assertions"):
            say(f"[grade] {eval_dir.name}: no assertions; add assertions after reviewing outputs")
            continue
        for run_dir in sorted(eval_dir.glob("*/run-*")):
            timing_path = run_dir / "timing.json"
            if not timing_path.is_file() or json.loads(timing_path.read_text()).get("error") is not None:
                continue
            if (run_dir / "grading.json").is_file() and not args.force:
                continue
            jobs.append((metadata, run_dir))

    with ThreadPoolExecutor(max_workers=max(1, args.workers)) as pool:
        outcomes = list(pool.map(lambda job: grade_run(client, settings, grader, *job), jobs))
    print(f"graded {outcomes.count(True)} of {len(jobs)} runs in {iteration_dir}")
    if not all(outcomes):
        sys.exit(2)


if __name__ == "__main__":
    main()
