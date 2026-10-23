#!/usr/bin/env python3
"""Compare two Git revisions of one skill in omp without revealing which is which.

Each revision's skill directory is extracted under a random label. omp handles
every query that has `criteria` in `evals/<plugin>/<skill>.toml` once per
revision, then a separate omp run without tools judges the two answers, shown
as A and B in random order, against those criteria. Only after judging are the
labels mapped back to the base and head revisions. Results support review;
they do not replace it.
"""

from __future__ import annotations

import argparse
import json
import random
import re
import shutil
import subprocess
import sys
import tarfile
import tempfile
import time
from concurrent.futures import ThreadPoolExecutor
from dataclasses import dataclass, field
from pathlib import Path

import check_activation as ca
import check_plugins as cp

JUDGE_TIMEOUT = 600


@dataclass
class Answer:
    side: str  # "base" or "head"
    trace: ca.Trace
    text: str
    log: Path


@dataclass
class Verdict:
    winner: str = ""  # "base", "head", "tie", or "" when not judged
    reason: str = ""
    passed: dict[str, int] = field(default_factory=dict)
    error: str = ""
    a_side: str = ""  # which revision the judge saw as A, for reading its reason


def git(*args: str, cwd: Path) -> subprocess.CompletedProcess[str]:
    return subprocess.run(["git", *args], cwd=cwd, capture_output=True, text=True)


def files(directory: Path) -> dict[Path, bytes]:
    return {p.relative_to(directory): p.read_bytes()
            for p in directory.rglob("*") if p.is_file()}


def extract(root: Path, ref: str, plugin: str, skill: str, dest: Path) -> Path:
    """Extract one revision's skill directory and return its path."""
    rel = f"plugins/{plugin}/skills/{skill}"
    archive = subprocess.run(["git", "archive", "--format=tar", ref, rel], cwd=root,
                             capture_output=True)
    if archive.returncode != 0:
        raise ValueError(f"{ref} has no {rel}: {archive.stderr.decode().strip()}")
    dest.mkdir(parents=True)
    tar_path = dest / "skill.tar"
    tar_path.write_bytes(archive.stdout)
    with tarfile.open(tar_path) as tar:
        if hasattr(tarfile, "data_filter"):  # added in Python 3.11.4
            tar.extractall(dest, filter="data")
        else:
            tar.extractall(dest)
    tar_path.unlink()
    return dest / rel


def final_text(stdout: str) -> tuple[str, str]:
    """Return the last assistant text and the stop reason of the last message."""
    text, stop = "", ""
    for event in ca.events(stdout):
        message = event.get("message", {})
        if event.get("type") != "message_end" or message.get("role") != "assistant":
            continue
        stop = str(message.get("stopReason", ""))
        parts = [b.get("text", "") for b in message.get("content", [])
                 if b.get("type") == "text"]
        if any(p.strip() for p in parts):
            text = "\n".join(parts)
    return text, stop


def answer(base: Path, root: Path, pin: ca.Pin, skill_dir: Path, plugin: str, skill: str,
           query: ca.Query, side: str, label: str) -> Answer:
    target = base / "compare-runs" / label
    shutil.rmtree(target, ignore_errors=True)
    target.mkdir(parents=True)
    subprocess.run(["git", "init", "-q", str(target)], check=True)
    prompt = (f"Follow the agent skill in {skill_dir}: read {skill_dir}/SKILL.md "
              "first, read the files it points to when they apply, then handle "
              f"this request.\n\n{query.prompt}")
    proc, trace = ca.execute("omp", base, root, pin, prompt, target, plugin, skill)
    log = base / "compare-runs" / f"{label}.jsonl"
    log.write_text(proc.stdout, encoding="utf-8")
    text, stop = final_text(proc.stdout)
    # Only a final message that stopped normally is a complete answer.
    if proc.returncode == 124 or stop != "stop":
        trace.failed = True
        trace.error = trace.error or (f"last message stopped with {stop!r}" if stop
                                      else cp.tail(proc))
    return Answer(side, trace, text, log)


def judge(base: Path, root: Path, pin: ca.Pin, query: ca.Query, first: Answer,
          second: Answer, label: str) -> tuple[dict, str]:
    """Ask omp, without tools, to grade A and B; return its JSON and the log."""
    criteria = "\n".join(f"{i}. {c}" for i, c in enumerate(query.criteria, 1))
    prompt = (
        "You are grading two answers to the same request. Judge only the answers "
        "against the numbered criteria; ignore style and length unless a criterion "
        "names them.\n\n"
        f"Request:\n{query.prompt}\n\nCriteria:\n{criteria}\n\n"
        f"<answer id=\"A\">\n{first.text}\n</answer>\n\n"
        f"<answer id=\"B\">\n{second.text}\n</answer>\n\n"
        "Reply with only this JSON object: "
        '{"criteria": [{"n": 1, "A": true, "B": false}, ...], '
        '"winner": "A" or "B" or "tie", "reason": "one sentence"}')
    env, _ = ca.client_env("omp", base)
    target = base / "compare-runs" / f"{label}-judge"
    shutil.rmtree(target, ignore_errors=True)
    target.mkdir(parents=True)
    proc = cp.run(["omp", "-p", "--no-session", "--mode", "json", "--no-tools",
                   "--model", pin.model, "--thinking", pin.effort, prompt],
                  env, target, timeout=JUDGE_TIMEOUT)
    log = base / "compare-runs" / f"{label}-judge.jsonl"
    log.write_text(proc.stdout, encoding="utf-8")
    # The judge decides the winner, so it must have run on the selected profile.
    mismatch = ca.pin_mismatch("omp", ca.parse_omp(proc.stdout, "", ""), pin)
    if mismatch:
        raise ValueError(f"judge off profile: {mismatch}")
    text, _ = final_text(proc.stdout)
    match = re.search(r"\{.*\}", text, re.S)
    if not match:
        raise ValueError(f"judge gave no JSON: {text[:120] or cp.tail(proc)}")
    return json.loads(match.group(0)), str(log)


def compare(base: Path, root: Path, pin: ca.Pin, query: ca.Query,
            answers: dict[str, Answer], rng: random.Random, label: str) -> Verdict:
    problems = []
    for side in ("base", "head"):
        trace = answers[side].trace
        if trace.refused or trace.failed or not trace.reached or not answers[side].text:
            reason = trace.refused and "refused by provider" or trace.error or "no answer"
            problems.append(f"{side} did not complete: {reason}")
        elif not trace.loaded:
            # An answer that never read its revision does not measure that revision.
            problems.append(f"{side} did not read its SKILL.md")
    if problems:
        return Verdict(error="; ".join(problems))
    order = ["base", "head"]
    rng.shuffle(order)
    letters = {"A": order[0], "B": order[1]}
    try:
        result, _ = judge(base, root, pin, query, answers[order[0]], answers[order[1]],
                          label)
    except (ValueError, json.JSONDecodeError) as exc:
        return Verdict(error=str(exc)[:160])
    winner = str(result.get("winner", "")).strip()
    verdict = Verdict(winner=letters.get(winner, "tie" if winner == "tie" else ""),
                      reason=str(result.get("reason", ""))[:200], a_side=order[0])
    if not verdict.winner:
        return Verdict(error=f"judge winner was {winner!r}")
    # Require exactly one boolean A/B pair per numbered criterion.
    items = result.get("criteria")
    if not isinstance(items, list) or not all(isinstance(item, dict) for item in items):
        return Verdict(error="judge did not grade every criterion with true or false")
    numbers = [item.get("n") for item in items]
    if (sorted(numbers, key=str) != sorted(range(1, len(query.criteria) + 1), key=str)
            or not all(isinstance(item.get(k), bool) for item in items for k in "AB")):
        return Verdict(error="judge did not grade every criterion with true or false")
    verdict.passed = {side: sum(item[letter] for item in items)
                      for letter, side in letters.items()}
    return verdict


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("skill", help="<plugin>:<skill> to compare")
    parser.add_argument("--homes", type=Path, default=ca.DEFAULT_HOMES,
                        help="test homes from `check_activation.py --clients omp prepare` "
                             f"(default: {ca.DEFAULT_HOMES})")
    parser.add_argument("--base", default="origin/main", help="base revision (default origin/main)")
    parser.add_argument("--head", default="HEAD", help="head revision (default HEAD)")
    parser.add_argument("--root", type=Path, default=ca.REPO,
                        help="repository to read revisions from (default: this one)")
    parser.add_argument("--reps", type=int, default=3, help="comparisons per query")
    parser.add_argument("--jobs", type=int, default=4, help="parallel omp runs")
    parser.add_argument("--seed", type=int, help="seed for label and A/B order")
    parser.add_argument("--profile", default="default",
                        help=f"model profile in {ca.MODELS_FILE} (default: default)")
    args = parser.parse_args()
    if args.reps < 1 or args.jobs < 1:
        parser.error("--reps and --jobs must be at least 1")
    plugin, _, skill = args.skill.partition(":")
    if not plugin or not skill:
        parser.error("skill must be <plugin>:<skill>")
    root, base = args.root.resolve(), Path(args.homes).resolve()
    if not (base / "omp-home").is_dir():
        print(f"{base} has no omp home; run `check_activation.py --clients omp prepare`")
        return 2
    try:
        spec = ca.load_spec(root / "evals" / plugin / f"{skill}.toml")
        pin = ca.load_pins(root, args.profile)["omp"]
    except (OSError, ValueError) as exc:
        print(f"spec error: {exc}")
        return 2
    queries = [q for q in spec.queries if q.criteria]
    if not queries:
        print(f"{spec.path} has no query with `criteria`")
        return 2
    refs = {}
    for side, ref in (("base", args.base), ("head", args.head)):
        proc = git("rev-parse", "--verify", f"{ref}^{{commit}}", cwd=root)
        if proc.returncode != 0:
            print(f"unknown revision: {ref}")
            return 2
        refs[side] = proc.stdout.strip()

    rng = random.Random(args.seed)
    work = Path(tempfile.mkdtemp(prefix="skill-revisions-"))
    try:
        dirs = {}
        for side in ("base", "head"):
            label = f"rev-{rng.getrandbits(32):08x}"
            try:
                dirs[side] = extract(root, refs[side], plugin, skill, work / label)
            except ValueError as exc:
                print(exc)
                return 2
        if files(dirs["base"]) == files(dirs["head"]):
            print("the two revisions have identical skill files; nothing to compare")
            return 2
        # The answers must follow only the extracted revisions, so remove the
        # installed copy that `prepare` added; `check_activation.py run`
        # reinstalls it.
        market = cp.load_marketplace(root)[0]
        env, target = ca.client_env("omp", base)
        cp.run(["omp", "plugin", "uninstall", f"{plugin}@{market}"], env, target)
        listing = cp.run(["omp", "skill", "list"], env, target)
        if any(line.split(None, 1)[0] == skill
               for line in listing.stdout.splitlines() if line.strip()):
            print(f"omp still lists the installed {skill}; cannot compare blind")
            return 2
        problem = ca.preflight("omp", base, root, pin)
        if problem:
            print(f"omp unavailable: {problem}")
            return 2

        stamp = time.strftime("%Y%m%d-%H%M%S")
        jobs = [(qi, rep, side) for qi in range(len(queries))
                for rep in range(1, args.reps + 1) for side in ("base", "head")]
        with ThreadPoolExecutor(max_workers=args.jobs) as pool:
            futures = {
                (qi, rep, side): pool.submit(
                    answer, base, root, pin, dirs[side], plugin, skill, queries[qi], side,
                    f"{stamp}-{queries[qi].id}-{rep}-{rng.getrandbits(32):08x}")
                for qi, rep, side in jobs}
            answers = {key: f.result() for key, f in futures.items()}
            verdicts = {
                (qi, rep): pool.submit(
                    compare, base, root, pin, queries[qi],
                    {s: answers[(qi, rep, s)] for s in ("base", "head")},
                    random.Random(rng.getrandbits(64)), f"{stamp}-{queries[qi].id}-{rep}")
                for qi in range(len(queries)) for rep in range(1, args.reps + 1)}
            verdicts = {key: f.result() for key, f in verdicts.items()}
    finally:
        shutil.rmtree(work, ignore_errors=True)

    print(f"{args.skill}: base {args.base} ({refs['base'][:7]}) vs head {args.head} "
          f"({refs['head'][:7]}), answered and judged blind by omp {pin.model} "
          f"({pin.effort}, profile {args.profile})")
    incomplete = False
    for qi, query in enumerate(queries):
        for rep in range(1, args.reps + 1):
            verdict = verdicts[(qi, rep)]
            reads = {s: ",".join(sorted(r.removeprefix("references/")
                                        for r in answers[(qi, rep, s)].trace.reads)) or "-"
                     for s in ("base", "head")}
            name = f"{query.id}#{rep}"
            if verdict.error:
                incomplete = True
                print(f"NONE  {name:<14} {verdict.error}")
                continue
            total = len(query.criteria)
            print(f"{verdict.winner.upper():<5} {name:<14} criteria base "
                  f"{verdict.passed['base']}/{total}, head {verdict.passed['head']}/{total}; "
                  f"reads base {reads['base']}, head {reads['head']}; "
                  f"judge (A={verdict.a_side}): {verdict.reason}")
    summary = base / "compare-runs" / f"{stamp}-summary.json"
    summary.write_text(json.dumps([
        {"query": query.id, "rep": rep,
         "base": str(answers[(qi, rep, "base")].log),
         "head": str(answers[(qi, rep, "head")].log),
         "judge": str(base / "compare-runs" / f"{stamp}-{query.id}-{rep}-judge.jsonl"),
         "a_side": verdicts[(qi, rep)].a_side,
         "winner": verdicts[(qi, rep)].winner, "error": verdicts[(qi, rep)].error}
        for qi, query in enumerate(queries) for rep in range(1, args.reps + 1)],
        indent=2), encoding="utf-8")
    print(f"\ntraces: {base / 'compare-runs'}; base/head mapping: {summary}")
    return 2 if incomplete else 0


if __name__ == "__main__":
    sys.exit(main())
