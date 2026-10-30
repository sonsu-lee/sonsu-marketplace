#!/usr/bin/env python3
"""Compare two Git revisions of one skill in omp without revealing which is which.

Each revision's skill directory is extracted under a random label. omp handles
every query that has `criteria` in `evals/<plugin>/<skill>.json` once per
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
import subprocess
import sys
import tarfile
import uuid
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
    criteria: list[dict] = field(default_factory=list)


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
    if query.fixture:
        raise ValueError("fixture comparisons are unsupported; use check_activation.py")
    work = base / "compare-runs" / label
    target = work / "target"
    ca.prepare_target(target, query.fixtures)
    inventory = ca.skill_files(root)
    identity = f"{plugin}:{skill}"
    inventory[identity] = skill_dir
    session, result = str(uuid.uuid4()), ca.Trace()
    texts = []
    coverage = {}
    for index, step in enumerate(query.steps):
        prompt = step.prompt
        if index == 0:
            prompt = (f"Follow the agent skill in {skill_dir}: read {skill_dir}/SKILL.md "
                      "first, read the files it points to when they apply, then handle "
                      f"this request.\n\n{prompt}")
        proc, trace = ca.execute("omp", base, root, pin, prompt, target, identity,
                                 inventory, session, work / "sessions", resume=index > 0,
                                 coverage=coverage)
        log = work / f"turn-{index + 1}.jsonl"
        log.write_text(proc.stdout, encoding="utf-8")
        text, stop = final_text(proc.stdout)
        texts.append(text)
        if index == 0 and identity not in trace.successful:
            result.failed = True
            result.error = trace.error or "assigned revision was not loaded for the first answer"
            break
        result.successful.update(trace.successful & {identity})
        result.reads.update(trace.reads)
        result.reached = trace.reached
        if trace.failed or trace.refused or stop != "stop":
            result.failed, result.refused = True, trace.refused
            result.error = trace.error or f"last message stopped with {stop!r}"
            break
        session = trace.session
    return Answer(side, result, "\n\n".join(texts), work)


def judge(base: Path, root: Path, pin: ca.Pin, query: ca.Query, first: Answer,
          second: Answer | None, label: str) -> tuple[dict, str]:
    """Ask omp, without tools, to grade one answer or a blinded pair."""
    criteria = "\n".join(f"{i}. {c}" for i, c in enumerate(query.criteria, 1))
    pair = second is not None
    prompt = (
        f"You are grading {'two answers' if pair else 'one answer'} to the same request. "
        "Judge only the answers against the numbered criteria; ignore style and length "
        "unless a criterion names them.\n\n"
        "Requests in conversation order:\n" + "\n\n".join(
            f"Turn {i}: {step.prompt}" for i, step in enumerate(query.steps, 1)) +
        f"\n\nCriteria:\n{criteria}\n\n"
        f"<answer id=\"A\">\n{first.text}\n</answer>\n\n"
        + (f"<answer id=\"B\">\n{second.text}\n</answer>\n\n" if pair else "")
        + "Reply with only this JSON object: "
        + ('{"criteria": [{"n": 1, "A": true, "B": false, "reason": "evidence"}, ...], '
           '"winner": "A" or "B" or "tie", "reason": "one sentence"}'
           if pair else
           '{"criteria": [{"n": 1, "A": true, "reason": "evidence"}, ...], '
           '"reason": "one sentence"}'))
    env, _ = ca.client_env("omp", base)
    target = base / "compare-runs" / f"{label}-judge"
    target.mkdir(parents=True)
    proc = cp.run(["omp", "-p", "--no-session", "--mode", "json", "--no-tools",
                   "--no-context-files", "--no-extensions", "--no-rules",
                   "--model", pin.model, "--thinking", pin.effort, prompt],
                  env, target, timeout=JUDGE_TIMEOUT)
    log = base / "compare-runs" / f"{label}-judge.jsonl"
    log.write_text(proc.stdout, encoding="utf-8")
    # The judge decides the winner, so it must have run on the selected profile.
    trace = ca.parse_omp(proc.stdout, "", {})
    if proc.returncode or trace.failed or trace.refused or not trace.reached or not trace.complete:
        raise ValueError(f"judge did not complete: {trace.error or trace.refused or cp.tail(proc)}")
    mismatch = ca.pin_mismatch("omp", trace, pin)
    if mismatch:
        raise ValueError(f"judge off profile: {mismatch}")
    text, _ = final_text(proc.stdout)
    match = re.search(r"\{.*\}", text, re.S)
    if not match:
        raise ValueError(f"judge gave no JSON: {text[:120] or cp.tail(proc)}")
    return json.loads(match.group(0)), str(log)


def grade(base: Path, root: Path, pin: ca.Pin, query: ca.Query,
          answers: dict[str, Answer], rng: random.Random, label: str,
          *, check_trace: bool = True) -> Verdict:
    sides = list(answers)
    if check_trace:
        problems = []
        for side in sides:
            trace = answers[side].trace
            if trace.refused or trace.failed or not trace.reached or not answers[side].text:
                reason = trace.refused and "refused by provider" or trace.error or "no answer"
                problems.append(f"{side} did not complete: {reason}")
            elif not trace.successful:
                # An answer that never read its revision does not measure that revision.
                problems.append(f"{side} did not read its SKILL.md")
        if problems:
            return Verdict(error="; ".join(problems))
    rng.shuffle(sides)
    letters = {letter: side for letter, side in zip("AB", sides)}
    try:
        result, _ = judge(base, root, pin, query, answers[sides[0]],
                          answers[sides[1]] if len(sides) == 2 else None, label)
    except (ValueError, OSError, subprocess.SubprocessError) as exc:
        return Verdict(error=str(exc)[:160])
    if not isinstance(result, dict):
        return Verdict(error="judge result was not an object")
    winner = result.get("winner", "") if len(sides) == 2 else "head"
    if len(sides) == 2 and winner not in ("A", "B", "tie"):
        return Verdict(error=f"judge winner was {winner!r}")
    items = result.get("criteria")
    if (not isinstance(items, list) or len(items) != len(query.criteria)
            or not all(isinstance(item, dict) for item in items)):
        return Verdict(error="judge did not grade every criterion with true or false")
    numbers = [item.get("n") for item in items]
    if (any(type(n) is not int for n in numbers)
            or set(numbers) != set(range(1, len(query.criteria) + 1))
            or not all(isinstance(item.get(k), bool) for item in items for k in letters)
            or not all(isinstance(item.get("reason"), str) and item["reason"].strip()
                       for item in items)):
        return Verdict(error="judge did not grade every criterion with true or false")
    records = [{"n": item["n"], "criterion": query.criteria[item["n"] - 1],
                **{side: item[letter] for letter, side in letters.items()},
                "reason": item["reason"]} for item in sorted(items, key=lambda x: x["n"])]
    return Verdict(winner=letters.get(winner, winner),
                   reason=str(result.get("reason", ""))[:200], a_side=sides[0],
                   passed={side: sum(item[side] for item in records) for side in sides},
                   criteria=records)


def compare(base: Path, root: Path, pin: ca.Pin, query: ca.Query,
            answers: dict[str, Answer], rng: random.Random, label: str) -> Verdict:
    return grade(base, root, pin, query, answers, rng, label)


def load_calibration(path: Path) -> list[tuple[ca.Query, list[dict]]]:
    data = json.loads(path.read_text(encoding="utf-8"), object_pairs_hook=ca._spec_object)
    if not isinstance(data, dict) or set(data) != {"cases"} or not isinstance(data["cases"], list) or not data["cases"]:
        raise ValueError("calibration must contain a nonempty cases array")
    cases, ids = [], set()
    for case in data["cases"]:
        if not isinstance(case, dict) or set(case) != {"id", "prompt", "criteria", "examples"}:
            raise ValueError("calibration case requires id, prompt, criteria, examples")
        ident, prompt, criteria, examples = (case[k] for k in ("id", "prompt", "criteria", "examples"))
        if (not isinstance(ident, str) or not ident.strip() or ident in ids
                or not isinstance(prompt, str) or not prompt.strip()
                or not isinstance(criteria, list) or not criteria
                or any(not isinstance(c, str) or not c.strip() for c in criteria)
                or not isinstance(examples, list) or not examples):
            raise ValueError("invalid calibration case")
        ids.add(ident)
        example_ids = set()
        for example in examples:
            if (not isinstance(example, dict) or set(example) != {"id", "text", "expected"}
                    or not isinstance(example["id"], str) or not example["id"].strip()
                    or example["id"] in example_ids
                    or not isinstance(example["text"], str) or not example["text"].strip()
                    or not isinstance(example["expected"], list)
                    or len(example["expected"]) != len(criteria)
                    or any(type(value) is not bool for value in example["expected"])):
                raise ValueError(f"invalid calibration example in {ident}")
            example_ids.add(example["id"])
        cases.append((ca.Query(id=ident, steps=[ca.Step(prompt=prompt, expect="load")],
                               criteria=criteria), examples))
    return cases


def calibrate(base: Path, root: Path, pin: ca.Pin, cases: list, stamp: str) -> list[dict]:
    results = []
    for ci, (query, examples) in enumerate(cases):
        for ei, example in enumerate(examples):
            answer_record = Answer("head", ca.Trace(), example["text"], Path())
            label = f"{stamp}-calibration-{ci}-{ei}"
            verdict = grade(base, root, pin, query, {"head": answer_record},
                            random.Random(), label, check_trace=False)
            actual = [item["head"] for item in verdict.criteria]
            error = verdict.error or ("calibration misclassification"
                                      if actual != example["expected"] else "")
            results.append({"case": query.id, "example": example["id"],
                            "expected": example["expected"], "criteria": verdict.criteria,
                            "reason": verdict.reason, "error": error,
                            "judge": str(base / "compare-runs" / f"{label}-judge.jsonl")})
    return results


def exit_status(verdicts: list[Verdict], calibration: list[dict]) -> int:
    if any(v.error for v in verdicts) or any(item["error"] for item in calibration):
        return 2
    return 1 if any(any(not item["head"] for item in v.criteria) for v in verdicts) else 0


def select_queries(spec: ca.Spec, wanted: list[str] | None) -> list[ca.Query]:
    # フィクスチャの最終状態は check_activation.py が判定する。比較では回答本文しか採点できない。
    queries = [q for q in spec.queries if q.criteria and not q.fixture]
    if wanted:
        unknown = set(wanted) - {q.id for q in queries}
        if unknown:
            raise ValueError(f"unknown query IDs: {', '.join(sorted(unknown))}")
        queries = [q for q in queries if q.id in wanted]
    return queries


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
    parser.add_argument("--evaluate", action="store_true", help="grade head alone")
    parser.add_argument("--query", action="append", help="select query ID (repeatable)")
    parser.add_argument("--calibration", type=Path, help="JSON calibration cases")
    parser.add_argument("--calibration-only", action="store_true",
                        help="grade calibration examples without generating answers")
    args = parser.parse_args()
    if args.reps < 1 or args.jobs < 1:
        parser.error("--reps and --jobs must be at least 1")
    if args.calibration_only and not args.calibration:
        parser.error("--calibration-only requires --calibration")
    if not ca.QUALIFIED.fullmatch(args.skill):
        parser.error("skill must be <plugin>:<skill>")
    plugin, skill = args.skill.split(":")
    source, auth_base = args.root.resolve(), Path(args.homes).resolve()
    if not (auth_base / "omp-home").is_dir():
        print(f"{auth_base} has no omp home; run `check_activation.py --clients omp prepare`")
        return 2
    try:
        queries = ([] if args.calibration_only else
                   select_queries(ca.load_spec(source / "evals" / plugin / f"{skill}.json"),
                                  args.query))
        pin = ca.load_pins(source, args.profile)["omp"]
        calibration_cases = load_calibration(args.calibration) if args.calibration else []
    except (OSError, ValueError) as exc:
        print(f"spec error: {exc}")
        return 2
    if not queries and not args.calibration_only:
        print(f"evals/{plugin}/{skill}.json has no selected query with `criteria`")
        return 2
    sides = ("head",) if args.evaluate else ("base", "head")
    refs = {}
    if not args.calibration_only:
        for side, ref in ((s, args.base if s == "base" else args.head) for s in sides):
            proc = git("rev-parse", "--verify", f"{ref}^{{commit}}", cwd=source)
            if proc.returncode != 0:
                print(f"unknown revision: {ref}")
                return 2
            refs[side] = proc.stdout.strip()

    rng = random.Random(args.seed)
    base, root, hashes = ca.new_campaign(source)
    try:
        pin = ca.load_pins(root, args.profile)["omp"]
        if not args.calibration_only:
            queries = select_queries(ca.load_spec(root / "evals" / plugin / f"{skill}.json"),
                                     args.query)
            if not queries:
                raise ValueError("snapshot has no selected query with criteria")
    except (OSError, ValueError) as exc:
        print(f"snapshot error: {exc}")
        return 2
    dirs = {}
    for side in () if args.calibration_only else sides:
        label = f"rev-{rng.getrandbits(64):016x}"
        try:
            dirs[side] = extract(source, refs[side], plugin, skill, base / "revisions" / label)
        except ValueError as exc:
            print(exc)
            return 2
    if len(dirs) == 2 and files(dirs["base"]) == files(dirs["head"]):
        # Identical revisions cannot differ; grade the candidate alone.
        sides = ("head",)
    stamp = "compare"
    with ca.AuthLease("omp", auth_base, base) as authentication:
        problem = authentication.error
        if not args.calibration_only:
            market, plugins, _, results = cp.load_marketplace(root)
            if not all(r.ok for r in results):
                problem = problem or "snapshot catalogs are inconsistent"
            if not problem:
                problem = "; ".join(ca.install("omp", root, market,
                                              [p for p in plugins if p != plugin], base)[1])
            if not problem:
                problem = "; ".join(ca.installed_problems("omp", base, root, market, {plugin}))
            if not problem:
                env, target = ca.client_env("omp", base)
                listing = cp.run(["omp", "skill", "list"], env, target)
                if listing.returncode or any(line.split(None, 1)[0] == skill
                                             for line in listing.stdout.splitlines() if line.strip()):
                    problem = "target skill still discoverable; cannot compare blind"
        if not problem:
            problem = ca.preflight("omp", base, root, pin)
        if problem:
            print(f"omp unavailable: {problem}")
            return 2
        calibration_results = calibrate(base, root, pin, calibration_cases, stamp)
        jobs = [(qi, rep, side) for qi in range(len(queries))
                for rep in range(1, args.reps + 1) for side in sides]
        with ThreadPoolExecutor(max_workers=args.jobs) as pool:
            futures = {
                (qi, rep, side): pool.submit(
                    answer, base, root, pin, dirs[side], plugin, skill, queries[qi], side,
                    f"q{qi}-{rep}-{rng.getrandbits(64):016x}")
                for qi, rep, side in jobs}
            answers = {key: f.result() for key, f in futures.items()}
            verdicts = {
                (qi, rep): pool.submit(
                    compare, base, root, pin, queries[qi],
                    {s: answers[(qi, rep, s)] for s in sides},
                    random.Random(rng.getrandbits(64)), f"{stamp}-q{qi}-{rep}")
                for qi in range(len(queries)) for rep in range(1, args.reps + 1)}
            verdicts = {key: f.result() for key, f in verdicts.items()}

    # The lease saves refreshed credentials on exit, so read its status only here.
    auth_failed = authentication.sync_status == "failed"
    if args.calibration_only:
        summary = base / "compare-runs" / f"{stamp}-calibration.json"
        summary.parent.mkdir(parents=True, exist_ok=True)
        summary.write_text(json.dumps(calibration_results, indent=2), encoding="utf-8")
        if auth_failed:
            print(f"NONE authentication: {authentication.error}")
        for item in calibration_results:
            print(f"{'NONE' if item['error'] else 'PASS'}  {item['case']}/{item['example']} {item['error']}")
        print(f"calibration: {summary}")
        return 2 if auth_failed else exit_status([], calibration_results)
    if len(sides) == 1:
        print(f"{args.skill}: head {args.head} ({refs['head'][:7]}) evaluated by omp "
              f"{pin.model} ({pin.effort}, profile {args.profile})")
    else:
        print(f"{args.skill}: base {args.base} ({refs['base'][:7]}) vs head {args.head} "
              f"({refs['head'][:7]}), answered and judged blind by omp {pin.model} "
              f"({pin.effort}, profile {args.profile})")
    if auth_failed:
        print(f"NONE authentication: {authentication.error}")
    for item in calibration_results:
        print(f"{'NONE' if item['error'] else 'PASS'}  calibration {item['case']}/{item['example']} {item['error']}")
    for qi, query in enumerate(queries):
        for rep in range(1, args.reps + 1):
            verdict = verdicts[(qi, rep)]
            reads = {s: ",".join(sorted(r.removeprefix("references/")
                                        for r in answers[(qi, rep, s)].trace.reads)) or "-"
                     for s in sides}
            name = f"{query.id}#{rep}"
            if verdict.error:
                print(f"NONE  {name:<14} {verdict.error}")
                continue
            total = len(query.criteria)
            scores = ", ".join(f"{s} {verdict.passed[s]}/{total}" for s in sides)
            readout = ", ".join(f"{s} {reads[s]}" for s in sides)
            print(f"{verdict.winner.upper():<5} {name:<14} criteria {scores}; "
                  f"reads {readout}; judge (A={verdict.a_side}): {verdict.reason}")
    summary = base / "compare-runs" / f"{stamp}-summary.json"
    summary.write_text(json.dumps({"source_hashes": hashes, "revisions": refs,
        "profile": args.profile, "model": pin.model, "effort": pin.effort,
        "auth_sync": authentication.sync_status, "cases": [
        {"query": query.id, "rep": rep,
         "base": str(answers[(qi, rep, "base")].log) if "base" in sides else None,
         "head": str(answers[(qi, rep, "head")].log),
         "judge": str(base / "compare-runs" / f"{stamp}-q{qi}-{rep}-judge.jsonl"),
         "a_side": verdicts[(qi, rep)].a_side,
         "winner": verdicts[(qi, rep)].winner, "error": verdicts[(qi, rep)].error,
         "reason": verdicts[(qi, rep)].reason, "criteria": verdicts[(qi, rep)].criteria}
        for qi, query in enumerate(queries) for rep in range(1, args.reps + 1)]},
        indent=2), encoding="utf-8")
    if calibration_cases:
        calibration_summary = base / "compare-runs" / f"{stamp}-calibration.json"
        calibration_summary.write_text(json.dumps(calibration_results, indent=2), encoding="utf-8")
        print(f"calibration: {calibration_summary}")
    print(f"\ntraces: {base / 'compare-runs'}; base/head mapping: {summary}")
    return 2 if auth_failed else exit_status(list(verdicts.values()), calibration_results)


if __name__ == "__main__":
    sys.exit(main())
