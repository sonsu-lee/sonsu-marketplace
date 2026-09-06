#!/usr/bin/env python3
"""Bounded, reproducible A/B evaluator for Fluent Japanese generation cases.

This program has deliberately narrow responsibilities.  It runs only
``generation`` fixtures under explicitly injected baseline/candidate skill text;
routing fixtures are owned by the native-routing probe.  All mutable evidence is
written below the external experiment directory, never into this repository.
"""

import argparse
import concurrent.futures
import datetime as dt
import hashlib
import json
import math
import os
from pathlib import Path
import random
import re
import secrets
import shutil
import signal
import subprocess
import sys
import tempfile
import time
from collections import Counter, defaultdict
from typing import Any, Dict, Iterable, List, Mapping, Optional, Sequence, Tuple


HERE = Path(__file__).resolve().parent
REPO_ROOT = HERE.parents[1]
DEFAULT_CASES = HERE / "writing-cases.json"
DEFAULT_PROTOCOL = HERE / "protocol.md"
DEFAULT_ARTIFACT_ROOT = Path(
    "/Users/sonsu/Documents/Codex/experiments/japanese-writing-20260906"
)
MODEL = "gpt-5.6-sol"
REASONING = "medium"
REPETITIONS = 2
MANIFEST_VERSION = "jp-writing-f2-f4-manifest-v1"
RESULT_VERSION = "jp-writing-f2-f4-result-v1"
GRADE_VERSION = "jp-writing-f2-f4-grade-v1"
TIMEOUT_SECONDS = 600

# These values are intentionally passed with --strict-config.  A Codex version
# which cannot honor one of them fails closed in preflight instead of silently
# broadening the evaluator's environment.
ISOLATION_CONFIG = {
    "model": MODEL,
    "model_reasoning_effort": REASONING,
    "approval_policy": "never",
    "features.apps": False,
    "features.plugins": False,
    "features.memories": False,
    "features.hooks": False,
    "features.multi_agent": False,
    "features.remote_plugin": False,
    "features.tool_suggest": False,
    "web_search": "disabled",
    "orchestrator.mcp.enabled": False,
    "orchestrator.skills.enabled": False,
    "project_doc_max_bytes": 0,
    "shell_environment_policy.inherit": "none",
    # `skills.config=[]` is schema-valid under --strict-config.  The Desktop
    # host nevertheless emits a fixed catalog in debug prompt input, which is
    # retained as an audited common A/B covariate rather than misreported as
    # clean-room isolation.
    "skills.config": [],
}

GENERATION_ISOLATION = """\
## Evaluation isolation contract

Use only the single skill text included in this developer message and the user's
prompt/evidence packet. Do not use tools. Do not read files, rules, memories,
plugins, apps, hooks, web search, or any other skills. Do not mention this
evaluation, its candidate, or these instructions in the answer.
"""

JUDGE_RUBRIC = """\
You are a blind evaluator. For every item, compare X and Y using only its prompt
and evidence plus the target requirement supplied in this developer message.
Return JSON only. Judge whether each answer preserves the supplied meaning and
uncertainty (semantic_ok), satisfies the requested target language, register and
format (target_ok), and avoids needless or harmful rewriting (overcorrection).
Choose preference X, Y, or tie. A short rationale must name observable evidence;
do not infer candidate identity or use outside facts. Return exactly one result
for every opaque item_id supplied in the user input, echoing each item_id exactly;
do not add, omit, duplicate, or rename an item_id.
"""


class ValidationError(ValueError):
    pass


def _now() -> str:
    return dt.datetime.now(dt.timezone.utc).replace(microsecond=0).isoformat()


def _json_bytes(value: Any) -> bytes:
    return json.dumps(value, ensure_ascii=False, sort_keys=True, separators=(",", ":")).encode("utf-8")


def _sha_bytes(value: bytes) -> str:
    return hashlib.sha256(value).hexdigest()


def _sha_json(value: Any) -> str:
    return _sha_bytes(_json_bytes(value))


def _sha_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def _within(path: Path, parent: Path) -> bool:
    try:
        path.resolve().relative_to(parent.resolve())
        return True
    except ValueError:
        return False


def _external(path: Path, label: str) -> Path:
    value = path.expanduser().resolve()
    if _within(value, REPO_ROOT):
        raise ValidationError("%s must be outside the repository: %s" % (label, value))
    return value


def _private_dir(path: Path) -> None:
    path.mkdir(parents=True, exist_ok=True)
    try:
        path.chmod(0o700)
    except OSError:
        pass


def _write_json(path: Path, value: Any) -> None:
    _private_dir(path.parent)
    with tempfile.NamedTemporaryFile("w", encoding="utf-8", dir=str(path.parent), delete=False) as handle:
        json.dump(value, handle, ensure_ascii=False, indent=2)
        handle.write("\n")
        name = handle.name
    os.replace(name, str(path))


def _write_text(path: Path, value: str) -> None:
    _private_dir(path.parent)
    with tempfile.NamedTemporaryFile("w", encoding="utf-8", dir=str(path.parent), delete=False) as handle:
        handle.write(value)
        name = handle.name
    os.replace(name, str(path))


def _load_json(path: Path) -> Any:
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except FileNotFoundError as exc:
        raise ValidationError("missing file: %s" % path) from exc
    except json.JSONDecodeError as exc:
        raise ValidationError("invalid JSON in %s: %s" % (path, exc)) from exc


def _source_name(path: Path) -> str:
    try:
        return str(path.resolve().relative_to(REPO_ROOT))
    except ValueError:
        return str(path.resolve())


def _toml(value: Any) -> str:
    if isinstance(value, bool):
        return "true" if value else "false"
    return json.dumps(value, ensure_ascii=False)


def _config_args(config: Mapping[str, Any]) -> List[str]:
    args: List[str] = []
    for key in sorted(config):
        args.extend(["-c", "%s=%s" % (key, _toml(config[key]))])
    return args


def _read_skill(path: Path, label: str) -> Dict[str, Any]:
    path = path.expanduser().resolve()
    if not path.is_file():
        raise ValidationError("%s skill is not a file: %s" % (label, path))
    text = path.read_text(encoding="utf-8")
    if not text.strip() or "\x00" in text:
        raise ValidationError("%s skill is empty or contains NUL" % label)
    match = re.search(r"(?m)^name:\s*([^\s#]+)\s*$", text)
    if not match:
        raise ValidationError("%s skill has no frontmatter name" % label)
    return {"label": label, "path": str(path), "name": match.group(1), "sha256": _sha_file(path), "text": text}


def _load_cases(path: Path) -> Tuple[List[Dict[str, Any]], List[Dict[str, Any]]]:
    raw = _load_json(path)
    if not isinstance(raw, dict) or raw.get("schema_version") != "fluent-japanese-cases-v1":
        raise ValidationError("expected fluent-japanese-cases-v1: %s" % path)
    cases = raw.get("cases")
    if not isinstance(cases, list) or not cases:
        raise ValidationError("cases must be a non-empty array")
    ids = set()
    generation: List[Dict[str, Any]] = []
    routing: List[Dict[str, Any]] = []
    for index, case in enumerate(cases):
        if not isinstance(case, dict):
            raise ValidationError("cases[%d] must be an object" % index)
        for key in ("id", "kind", "prompt", "evidence", "expectations"):
            if key not in case:
                raise ValidationError("cases[%d] missing %s" % (index, key))
        if not isinstance(case["id"], str) or case["id"] in ids:
            raise ValidationError("case id must be unique: %r" % case.get("id"))
        ids.add(case["id"])
        if case["kind"] not in {"generation", "routing"}:
            raise ValidationError("unsupported case kind: %r" % case["kind"])
        if not isinstance(case["prompt"], str) or not isinstance(case["evidence"], str):
            raise ValidationError("case prompt/evidence must be strings: %s" % case["id"])
        exact = case["expectations"].get("exact") if isinstance(case["expectations"], dict) else None
        if exact is not None and not isinstance(exact, dict):
            raise ValidationError("exact expectations must be an object: %s" % case["id"])
        (generation if case["kind"] == "generation" else routing).append(case)
    return generation, routing


def render_prompt(case: Mapping[str, Any]) -> str:
    return "%s\n\n<evidence_packet>\n%s\n</evidence_packet>" % (case["prompt"].rstrip(), case["evidence"].rstrip())


def _developer(skill: Mapping[str, Any]) -> str:
    return "# Intended skill: %s\n\n%s\n\n%s" % (skill["name"], skill["text"].strip(), GENERATION_ISOLATION.strip())


def _manifest_identity(value: Mapping[str, Any]) -> str:
    return _sha_json({k: v for k, v in value.items() if k not in {"manifest_id", "manifest_sha256", "artifact_dir"}})


def create_manifest(cases_path: Path, baseline_skill: Path, candidate_skill: Path, output: Path, seed: Optional[int] = None, protocol_path: Path = DEFAULT_PROTOCOL) -> Dict[str, Any]:
    cases_path = cases_path.resolve()
    protocol_path = protocol_path.resolve()
    if not protocol_path.is_file():
        raise ValidationError("frozen protocol is not a file: %s" % protocol_path)
    generation, routing = _load_cases(cases_path)
    if not generation:
        raise ValidationError("no generation cases available")
    baseline = _read_skill(baseline_skill, "baseline")
    candidate = _read_skill(candidate_skill, "candidate")
    if seed is None:
        seed = secrets.randbits(63)
    if isinstance(seed, bool) or not isinstance(seed, int) or seed < 0 or seed >= 2 ** 63:
        raise ValidationError("seed must be an integer in 0..2^63-1")
    rng = random.Random(seed)
    ordered_cases = list(generation)
    rng.shuffle(ordered_cases)
    runs: List[Dict[str, Any]] = []
    order = 0
    for case in ordered_cases:
        first = "baseline" if rng.randrange(2) == 0 else "candidate"
        for repetition, candidate_order in ((1, (first, "candidate" if first == "baseline" else "baseline")), (2, ("candidate" if first == "baseline" else "baseline", first))):
            for arm in candidate_order:
                order += 1
                runs.append({"run_id": "%s-r%d-%s" % (case["id"], repetition, arm), "case_id": case["id"], "arm": arm, "repetition": repetition, "order": order, "prompt_sha256": _sha_bytes(render_prompt(case).encode("utf-8"))})
    config = {"model": MODEL, "reasoning_effort": REASONING, "repetitions": REPETITIONS, "max_workers_default": 4, "timeout_default": TIMEOUT_SECONDS, "isolation_config": ISOLATION_CONFIG, "routing_cases_excluded": True}
    test_path = HERE / "test_eval.py"
    payload: Dict[str, Any] = {"schema_version": MANIFEST_VERSION, "created_at": _now(), "seed": seed, "config": config, "hashes": {"runner_sha256": _sha_file(Path(__file__).resolve()), "test_runner_sha256": _sha_file(test_path) if test_path.is_file() else None, "protocol_sha256": _sha_file(protocol_path), "cases_sha256": _sha_file(cases_path), "baseline_sha256": baseline["sha256"], "candidate_sha256": candidate["sha256"], "config_sha256": _sha_json(config)}, "protocol_source": _source_name(protocol_path), "cases_source": _source_name(cases_path), "generation_cases": ordered_cases, "routing_cases_excluded": [{"id": case["id"], "reason": "native-routing-probe-owns-skill-selection"} for case in routing], "arms": {"baseline": {k: baseline[k] for k in ("name", "path", "sha256")}, "candidate": {k: candidate[k] for k in ("name", "path", "sha256")}}, "runs": runs}
    output = _external(output, "manifest output")
    if output.exists():
        raise ValidationError("refusing to overwrite manifest: %s" % output)
    payload["artifact_dir"] = str(output.parent)
    payload["manifest_sha256"] = _manifest_identity(payload)
    payload["manifest_id"] = payload["manifest_sha256"][:16]
    _write_json(output, payload)
    return payload


def load_manifest(path: Path, check_sources: bool = True) -> Dict[str, Any]:
    path = _external(path, "manifest")
    data = _load_json(path)
    if not isinstance(data, dict) or data.get("schema_version") != MANIFEST_VERSION:
        raise ValidationError("invalid manifest schema")
    digest = _manifest_identity(data)
    if data.get("manifest_sha256") != digest or data.get("manifest_id") != digest[:16]:
        raise ValidationError("manifest integrity check failed")
    required = {"generation_cases", "runs", "arms", "hashes", "artifact_dir", "config", "protocol_source"}
    if required - set(data):
        raise ValidationError("manifest missing fields: %s" % sorted(required - set(data)))
    if check_sources:
        checks = [(Path(__file__).resolve(), data["hashes"].get("runner_sha256"), "eval.py"), (REPO_ROOT / data["protocol_source"], data["hashes"].get("protocol_sha256"), "protocol"), (REPO_ROOT / data["cases_source"], data["hashes"].get("cases_sha256"), "cases")]
        expected_test = data["hashes"].get("test_runner_sha256")
        if expected_test is not None:
            checks.append((HERE / "test_eval.py", expected_test, "test_eval.py"))
        for arm in ("baseline", "candidate"):
            checks.append((Path(data["arms"][arm]["path"]), data["hashes"].get(arm + "_sha256"), arm + " skill"))
        for current, expected, label in checks:
            if not current.is_file() or _sha_file(current) != expected:
                raise ValidationError("frozen %s changed after planning" % label)
    return data


def _codex_argv(developer: str, output_path: Path, scratch: Path, json_mode: bool = True) -> List[str]:
    config = dict(ISOLATION_CONFIG)
    config["developer_instructions"] = developer
    # `debug prompt-input` cannot accept --ignore-user-config or --ignore-rules.
    # Do not pretend it proves a different exec prompt: generation is therefore
    # an audited common-host-context A/B comparison and keeps these flags off.
    args = ["codex", "exec", "--strict-config", "--skip-git-repo-check", "--ephemeral", "--model", MODEL, "--sandbox", "read-only", "--color", "never", "-C", str(scratch), "--output-last-message", str(output_path)]
    if json_mode:
        args.append("--json")
    return args + _config_args(config) + ["-"]


def _run_process(argv: Sequence[str], cwd: Path, stdin: str, timeout: int, stdout_path: Path, stderr_path: Path) -> Dict[str, Any]:
    started = time.monotonic()
    returncode: Optional[int] = None
    timed_out = False
    spawn_error: Optional[str] = None
    try:
        with stdout_path.open("w", encoding="utf-8") as stdout, stderr_path.open("w", encoding="utf-8") as stderr:
            process = subprocess.Popen(list(argv), cwd=str(cwd), stdin=subprocess.PIPE, stdout=stdout, stderr=stderr, text=True, start_new_session=(os.name == "posix"))
            try:
                process.communicate(stdin, timeout=timeout)
            except subprocess.TimeoutExpired:
                timed_out = True
                if os.name == "posix":
                    with __import__("contextlib").suppress(ProcessLookupError):
                        os.killpg(process.pid, signal.SIGKILL)
                else:
                    process.kill()
                process.communicate()
            returncode = process.returncode
    except OSError as exc:
        spawn_error = "%s: %s" % (type(exc).__name__, exc)
    return {"returncode": returncode, "timed_out": timed_out, "spawn_error": spawn_error, "latency_seconds": round(time.monotonic() - started, 3)}


def _parse_jsonl(path: Path) -> Tuple[List[Any], List[str]]:
    events: List[Any] = []
    errors: List[str] = []
    if not path.is_file():
        return events, ["trace missing"]
    for number, line in enumerate(path.read_text(encoding="utf-8").splitlines(), 1):
        if not line.strip():
            continue
        try:
            events.append(json.loads(line))
        except json.JSONDecodeError as exc:
            errors.append("line %d: %s" % (number, exc))
    if not events:
        errors.append("trace has no JSON events")
    return events, errors


def _objects(value: Any) -> Iterable[Dict[str, Any]]:
    if isinstance(value, dict):
        yield value
        for child in value.values():
            yield from _objects(child)
    elif isinstance(value, list):
        for child in value:
            yield from _objects(child)


def _trace_info(events: Sequence[Any]) -> Dict[str, Any]:
    tool_types = {"command_execution", "function_call", "tool_call", "mcp_tool_call", "computer_tool_call", "dynamic_tool_call"}
    tools = []
    models = []
    completed = False
    for event in events:
        if isinstance(event, dict) and event.get("type") == "turn.completed":
            completed = True
        for obj in _objects(event):
            if str(obj.get("type", "")).lower() in tool_types:
                tools.append(obj.get("type"))
            for key in ("model", "model_name"):
                if isinstance(obj.get(key), str):
                    models.append(obj[key])
    return {"turn_completed": completed, "tool_types": sorted(set(tools)), "observed_models": sorted(set(models)) or ["unknown"]}


def _extract_blocks(text: str) -> List[str]:
    """Return fenced blocks after CommonMark's 0–3-space fence dedent.

    This deliberately covers only the form used by the exact fixture gate.  A
    list item may indent a fence by up to three spaces; CommonMark removes up
    to that opening indent from every content line.  It does not otherwise
    parse lists, containers, or general Markdown.
    """
    opening = re.compile(r"(?m)^( {0,3})(`{3,}|~{3,})([^\n]*)\n")
    blocks = []
    cursor = 0
    while True:
        match = opening.search(text, cursor)
        if match is None:
            break
        indent, fence, info = match.group(1), match.group(2), match.group(3)
        char = re.escape(fence[0])
        closing = re.compile(r"(?m)^ {0,3}" + char + r"{" + str(len(fence)) + r",}[ \t]*$")
        end = closing.search(text, match.end())
        if end is None:
            cursor = match.end()
            continue
        body = text[match.end():end.start()]
        if body.endswith("\n"):
            body = body[:-1]
        width = len(indent)
        lines = []
        for line in body.split("\n"):
            removable = min(width, len(line) - len(line.lstrip(" ")))
            lines.append(line[removable:])
        normalized = fence + info + "\n" + "\n".join(lines) + "\n" + fence
        blocks.append(normalized)
        cursor = end.end()
    return blocks


def hard_check(case: Mapping[str, Any], output: str) -> Dict[str, Any]:
    exact = case.get("expectations", {}).get("exact", {})
    if not isinstance(exact, dict):
        exact = {}
    failures: List[Dict[str, Any]] = []
    for literal in exact.get("protected_literals", []):
        if literal not in output:
            failures.append({"gate": "protected_literal", "detail": literal})
    headings = [re.sub(r"\s+#+\s*$", "", m.group(1)).strip() for m in re.finditer(r"(?m)^ {0,3}(#{1,6}\s+.+?)\s*$", output)]
    positions = []
    for heading in exact.get("required_headings", []):
        if heading not in headings:
            failures.append({"gate": "required_heading", "detail": heading})
        else:
            positions.append(headings.index(heading))
    if len(positions) == len(exact.get("required_headings", [])) and positions != sorted(positions):
        failures.append({"gate": "heading_order", "detail": exact["required_headings"]})
    cursor = 0
    for marker in exact.get("ordered_markers", []):
        pos = output.find(marker, cursor)
        if pos < 0:
            failures.append({"gate": "ordered_marker", "detail": marker})
        else:
            cursor = pos + len(marker)
    blocks = _extract_blocks(output)
    wanted_blocks = exact.get("exact_code_blocks", [])
    if wanted_blocks and len(blocks) != len(wanted_blocks):
        failures.append({"gate": "fenced_code_block_count", "detail": {"expected": len(wanted_blocks), "actual": len(blocks)}})
    for block in wanted_blocks:
        if blocks.count(block) != 1:
            failures.append({"gate": "exact_code_block", "detail": {"block": block, "matches": blocks.count(block)}})
    for literal, expected in exact.get("literal_counts", {}).items():
        if output.count(literal) != expected:
            failures.append({"gate": "literal_count", "detail": {"literal": literal, "expected": expected, "actual": output.count(literal)}})
    return {"status": "pass" if not failures else "fail", "failures": failures}


def _classify(process: Mapping[str, Any], output: str, events: Sequence[Any], trace_errors: Sequence[str], case: Mapping[str, Any]) -> Tuple[str, str, Dict[str, Any], Dict[str, Any]]:
    trace = _trace_info(events)
    check = hard_check(case, output) if output.strip() else {"status": "uncertain", "failures": [{"gate": "nonempty", "detail": "output is empty"}]}
    if process["timed_out"]:
        return "timeout", "deadline", trace, check
    if process["spawn_error"] or process["returncode"] != 0:
        return "error", "spawn_error" if process["spawn_error"] else "codex_exit_%s" % process["returncode"], trace, check
    if trace_errors or not trace["turn_completed"]:
        return "inconclusive", "invalid_or_incomplete_trace", trace, check
    if trace["tool_types"]:
        return "inconclusive", "tool_use_observed", trace, check
    if not output.strip():
        return "inconclusive", "empty_output", trace, check
    return "complete", "completed", trace, check


def _preflight_messages(value: Any) -> List[Tuple[str, str]]:
    found = []
    for item in _objects(value):
        role = item.get("role")
        if role in {"developer", "user", "system"}:
            text = item.get("text") or item.get("content")
            if isinstance(text, str):
                found.append((role, text))
            elif isinstance(text, list):
                for part in text:
                    if isinstance(part, dict) and isinstance(part.get("text"), str):
                        found.append((role, part["text"]))
    return found


def _normalize_common_text(text: str) -> str:
    """Remove per-run scratch locations, retaining all instruction content."""
    text = re.sub(r"/private/var/folders/[^\s<\"]+(?:/scratch)?", "<scratch>", text)
    text = re.sub(r"/var/folders/[^\s<\"]+(?:/scratch)?", "<scratch>", text)
    return text


def _common_context(messages: Sequence[Tuple[str, str]], developer: str, probe: str) -> Dict[str, Any]:
    common = [(role, _normalize_common_text(text)) for role, text in messages if text != developer and text != probe]
    # A catalog entry such as `fluent-japanese: ... (file: .../SKILL.md)` is an
    # observed common covariate.  An actual second Fluent body is not allowed.
    alternate_body = []
    body_re = re.compile(r"(?im)(^name:\s*fluent-(?:japanese|korean|english)\s*$|^#\s*自然な日本語出力\s*$|^##\s*(?:話題と行為者|内容と形式保全)\s*$)")
    for role, text in common:
        if body_re.search(text):
            alternate_body.append({"role": role, "excerpt": text[:300]})
    return {"entries": common, "sha256": _sha_json(common), "alternate_fluent_bodies": alternate_body}


def preflight(manifest_path: Path) -> Dict[str, Any]:
    manifest = load_manifest(manifest_path, check_sources=True)
    artifact = Path(manifest["artifact_dir"])
    preflight_dir = artifact / "preflight"
    if (preflight_dir / "result.json").exists():
        raise ValidationError("preflight is frozen already; create a new manifest to retry")
    _private_dir(preflight_dir)
    results = []
    # This is prompt inspection only. It is not asserted to be byte-identical
    # to exec; it snapshots fixed host context shared by both experimental arms.
    for arm in ("baseline", "candidate"):
        skill = _read_skill(Path(manifest["arms"][arm]["path"]), arm)
        developer = _developer(skill)
        probe = "Return exactly: PRELIGHT_OK"
        config = dict(ISOLATION_CONFIG)
        config["developer_instructions"] = developer
        with tempfile.TemporaryDirectory(prefix="jp-writing-preflight-") as temp:
            scratch = Path(temp) / "scratch"
            scratch.mkdir()
            argv = ["codex", "debug", "prompt-input"] + _config_args(config) + [probe]
            stdout = preflight_dir / (arm + ".prompt-input.json")
            stderr = preflight_dir / (arm + ".stderr.txt")
            command_path = preflight_dir / (arm + ".command.json")
            _write_json(command_path, {"argv": argv, "scratch_cwd": str(scratch), "note": "debug prompt-input is a common-host-context snapshot, not a claim about exact exec prompt equality"})
            process = _run_process(argv, scratch, "", 60, stdout, stderr)
        record: Dict[str, Any] = {"arm": arm, **process, "command_path": str(command_path), "command_sha256": _sha_file(command_path), "prompt_input_path": str(stdout), "stderr_path": str(stderr)}
        try:
            raw = _load_json(stdout)
            messages = _preflight_messages(raw)
            developer_count = sum(text == developer for role, text in messages if role == "developer")
            user_count = sum(text == probe for role, text in messages if role == "user")
            common = _common_context(messages, developer, probe)
            common_path = preflight_dir / (arm + ".common-context.json")
            _write_json(common_path, common)
            common_summary = {"path": str(common_path), "sha256": common["sha256"], "entries_count": len(common["entries"]), "alternate_fluent_bodies": common["alternate_fluent_bodies"]}
            record.update({"developer_exact_count": developer_count, "user_exact_count": user_count, "common_context": common_summary, "prompt_parse_ok": True})
            record["status"] = "pass" if process["returncode"] == 0 and not process["timed_out"] and developer_count == 1 and user_count == 1 and not common["alternate_fluent_bodies"] else "fail"
        except ValidationError as exc:
            record.update({"prompt_parse_ok": False, "parse_error": str(exc), "status": "fail"})
        results.append(record)
    common_hashes = [row.get("common_context", {}).get("sha256") for row in results]
    common_equal = len(common_hashes) == 2 and None not in common_hashes and len(set(common_hashes)) == 1
    report = {"checked_at": _now(), "manifest_id": manifest["manifest_id"], "requested": {"model": MODEL, "reasoning_effort": REASONING, "isolation": ISOLATION_CONFIG}, "design": {"kind": "common-host-context-ab", "claim": "both arms receive the same audited common context plus one designated injected skill", "not_claimed": "debug prompt-input is byte-identical to exec", "exec_flags_omitted_for_common_context": ["--ignore-user-config", "--ignore-rules"]}, "arms": results, "common_context_equal": common_equal, "common_context_sha256": common_hashes[0] if common_equal else None, "status": "pass" if common_equal and all(row["status"] == "pass" for row in results) else "fail"}
    _write_json(preflight_dir / "result.json", report)
    return report


def _result_path(manifest: Mapping[str, Any], run: Mapping[str, Any]) -> Path:
    return Path(manifest["artifact_dir"]) / "runs" / run["run_id"] / "result.json"


def _execute_one(manifest: Mapping[str, Any], run: Mapping[str, Any], case: Mapping[str, Any], timeout: int) -> Dict[str, Any]:
    result_path = _result_path(manifest, run)
    if result_path.exists():
        existing = _load_json(result_path)
        if existing.get("manifest_id") != manifest["manifest_id"]:
            raise ValidationError("existing result belongs to another manifest")
        return existing
    run_dir = result_path.parent
    _private_dir(run_dir)
    arm = run["arm"]
    skill = _read_skill(Path(manifest["arms"][arm]["path"]), arm)
    prompt = render_prompt(case)
    output = run_dir / "output.md"
    trace = run_dir / "trace.jsonl"
    stderr = run_dir / "stderr.txt"
    command = run_dir / "command.json"
    with tempfile.TemporaryDirectory(prefix="jp-writing-run-") as temp:
        scratch = Path(temp) / "scratch"
        scratch.mkdir()
        developer = _developer(skill)
        argv = _codex_argv(developer, output, scratch)
        _write_json(command, {"argv": argv, "cwd": str(scratch), "requested_model": MODEL, "requested_reasoning_effort": REASONING, "stdin_sha256": _sha_bytes(prompt.encode("utf-8")), "developer_sha256": _sha_bytes(developer.encode("utf-8")), "isolation": ISOLATION_CONFIG})
        process = _run_process(argv, scratch, prompt, timeout, trace, stderr)
    output_text = output.read_text(encoding="utf-8") if output.is_file() else ""
    events, trace_errors = _parse_jsonl(trace)
    status, reason, trace_info, check = _classify(process, output_text, events, trace_errors, case)
    record = {"schema_version": RESULT_VERSION, "manifest_id": manifest["manifest_id"], "run_id": run["run_id"], "case_id": run["case_id"], "arm": arm, "repetition": run["repetition"], "execution_status": status, "reason": reason, "structural_status": check["status"], "check": check, "trace_errors": trace_errors, "trace": trace_info, "requested_model": MODEL, "requested_reasoning_effort": REASONING, "observed_model": trace_info["observed_models"], "started_at": _now(), **process, "artifacts": {"output": str(output), "output_sha256": _sha_file(output) if output.is_file() else None, "trace": str(trace), "trace_sha256": _sha_file(trace) if trace.is_file() else None, "stderr": str(stderr), "stderr_sha256": _sha_file(stderr) if stderr.is_file() else None, "command": str(command), "command_sha256": _sha_file(command)}}
    _write_json(result_path, record)
    return record


def run_manifest(manifest_path: Path, workers: int = 4, timeout: int = TIMEOUT_SECONDS) -> Dict[str, Any]:
    if workers < 1 or workers > 4:
        raise ValidationError("workers must be in 1..4")
    if timeout < 30 or timeout > 3600:
        raise ValidationError("timeout must be in 30..3600")
    manifest = load_manifest(manifest_path, check_sources=True)
    proof = Path(manifest["artifact_dir"]) / "preflight" / "result.json"
    if not proof.is_file() or _load_json(proof).get("status") != "pass":
        raise ValidationError("preflight must pass before execution")
    cases = {case["id"]: case for case in manifest["generation_cases"]}
    results: List[Dict[str, Any]] = []
    ordered = sorted(manifest["runs"], key=lambda row: row["order"])
    with concurrent.futures.ThreadPoolExecutor(max_workers=workers) as pool:
        futures = [pool.submit(_execute_one, manifest, run, cases[run["case_id"]], timeout) for run in ordered]
        for future in concurrent.futures.as_completed(futures):
            results.append(future.result())
    counts = Counter(row["execution_status"] for row in results)
    summary = {"manifest_id": manifest["manifest_id"], "runs_expected": len(ordered), "status_counts": dict(sorted(counts.items())), "completed": counts.get("complete", 0), "complete": counts.get("complete", 0) == len(ordered), "completed_at": _now()}
    _write_json(Path(manifest["artifact_dir"]) / "run-summary.json", summary)
    return summary


def _completed_pairs(manifest: Mapping[str, Any]) -> List[Dict[str, Any]]:
    cases = {case["id"]: case for case in manifest["generation_cases"]}
    rows: Dict[Tuple[str, int], Dict[str, Any]] = defaultdict(dict)
    for run in manifest["runs"]:
        path = _result_path(manifest, run)
        if path.is_file():
            row = _load_json(path)
            if row.get("execution_status") == "complete":
                rows[(run["case_id"], run["repetition"])][run["arm"]] = row
    pairs = []
    for (case_id, repetition), arms in sorted(rows.items()):
        if set(arms) != {"baseline", "candidate"}:
            continue
        outputs = {}
        valid = True
        for arm, row in arms.items():
            output = Path(row["artifacts"]["output"])
            if not output.is_file() or _sha_file(output) != row["artifacts"]["output_sha256"]:
                valid = False
                break
            outputs[arm] = output.read_text(encoding="utf-8")
        if valid:
            pairs.append({"pair_id": "%s-r%d" % (case_id, repetition), "case": cases[case_id], "outputs": outputs, "generation_checks": {arm: {"structural_status": row.get("structural_status"), "check": row.get("check")} for arm, row in arms.items()}})
    return pairs


def _judge_prompt(batch: Sequence[Mapping[str, Any]], seed: int) -> Tuple[str, Dict[str, Any]]:
    rng = random.Random(seed)
    visible = []
    key = {}
    for pair in batch:
        x_arm = "baseline" if rng.randrange(2) == 0 else "candidate"
        y_arm = "candidate" if x_arm == "baseline" else "baseline"
        item_id = "item-" + _sha_bytes((pair["pair_id"] + ":" + str(seed)).encode("utf-8"))[:16]
        visible.append({"item_id": item_id, "prompt": pair["case"]["prompt"], "evidence": pair["case"]["evidence"], "X": pair["outputs"][x_arm], "Y": pair["outputs"][y_arm]})
        key[pair["pair_id"]] = {"item_id": item_id, "X": x_arm, "Y": y_arm}
    schema = {"items": [{"item_id": "item-opaque", "semantic_ok": {"X": True, "Y": True}, "target_ok": {"X": True, "Y": True}, "overcorrection": {"X": False, "Y": False}, "preference": "X", "rationale": "..."}]}
    return json.dumps({"items": visible, "required_shape_example": schema}, ensure_ascii=False), key


def _judge_developer(batch: Sequence[Mapping[str, Any]], key: Mapping[str, Mapping[str, str]]) -> str:
    requirements = []
    for pair in batch:
        expectations = pair["case"].get("expectations", {})
        if not isinstance(expectations, dict):
            raise ValidationError("case expectations must be an object: %s" % pair["pair_id"])
        semantic = expectations.get("semantic", {})
        if not isinstance(semantic, dict):
            raise ValidationError("semantic expectations must be an object: %s" % pair["pair_id"])
        semantic_payload = {}
        for field in ("must_preserve", "must_not_introduce"):
            values = semantic.get(field, [])
            if not isinstance(values, list) or any(not isinstance(value, str) or not value.strip() for value in values):
                raise ValidationError("semantic.%s must be a string array: %s" % (field, pair["pair_id"]))
            semantic_payload[field] = values
        target_ok = expectations.get("target_ok")
        if target_ok is not None and not isinstance(target_ok, dict):
            raise ValidationError("target_ok expectations must be an object: %s" % pair["pair_id"])
        review_points = pair["case"].get("review_points")
        if review_points is not None and (not isinstance(review_points, list) or any(not isinstance(value, str) or not value.strip() for value in review_points)):
            raise ValidationError("review_points must be a string array: %s" % pair["pair_id"])
        requirements.append({"item_id": key[pair["pair_id"]]["item_id"], "semantic": semantic_payload, "target_ok": target_ok, "review_points": review_points or []})
    return JUDGE_RUBRIC + "\n\nHidden target requirements, in the same order as items:\n" + json.dumps(requirements, ensure_ascii=False)


def _validated_judge_items(text: str, expected_ids: Sequence[str]) -> Dict[str, Dict[str, Any]]:
    parsed = json.loads(text)
    items = parsed.get("items") if isinstance(parsed, dict) else None
    if not isinstance(items, list) or len(items) != len(expected_ids):
        raise ValueError("wrong items length")
    by_id: Dict[str, Dict[str, Any]] = {}
    for item in items:
        if not isinstance(item, dict) or not isinstance(item.get("item_id"), str):
            raise ValueError("missing item_id")
        item_id = item["item_id"]
        if item_id in by_id:
            raise ValueError("duplicate item_id")
        if item.get("preference") not in {"X", "Y", "tie"}:
            raise ValueError("invalid preference")
        for axis in ("semantic_ok", "target_ok", "overcorrection"):
            if not isinstance(item.get(axis), dict) or not all(isinstance(item[axis].get(side), bool) for side in ("X", "Y")):
                raise ValueError("invalid " + axis)
        if not isinstance(item.get("rationale"), str) or not item["rationale"].strip():
            raise ValueError("invalid rationale")
        by_id[item_id] = item
    if set(by_id) != set(expected_ids):
        raise ValueError("item_id set does not match the frozen batch")
    return by_id


def _grade_plan(manifest: Mapping[str, Any], pairs: Sequence[Mapping[str, Any]], batch_size: int) -> Dict[str, Any]:
    batches = []
    for index in range(0, len(pairs), batch_size):
        batch = pairs[index:index + batch_size]
        batch_id = "batch-%03d" % (index // batch_size + 1)
        items = []
        for pair in batch:
            items.append({"pair_id": pair["pair_id"], "input_sha256": _sha_json({"prompt": pair["case"]["prompt"], "evidence": pair["case"]["evidence"], "baseline": pair["outputs"]["baseline"], "candidate": pair["outputs"]["candidate"]})})
        batches.append({"batch_id": batch_id, "items": items})
    plan = {"schema_version": GRADE_VERSION + "-plan", "manifest_id": manifest["manifest_id"], "batch_size": batch_size, "batches": batches}
    plan["sha256"] = _sha_json(plan)
    return plan


def _write_grade_plan(manifest: Mapping[str, Any], plan: Mapping[str, Any]) -> Path:
    path = Path(manifest["artifact_dir"]) / "grades" / "grade-plan.json"
    if path.is_file():
        existing = _load_json(path)
        if existing != plan:
            raise ValidationError("existing grade plan differs; use a new analysis artifact directory")
    else:
        _write_json(path, plan)
    return path


def _validate_cached_judge_result(cached: Mapping[str, Any], expected_identity: Mapping[str, Any], path: Path) -> None:
    if any(cached.get(field) != expected for field, expected in expected_identity.items()):
        raise ValidationError("cached judge result does not match frozen grade plan: %s" % path)


def _judge_one(manifest: Mapping[str, Any], batch: Sequence[Mapping[str, Any]], batch_id: str, judge: int, grade_plan: Mapping[str, Any]) -> Dict[str, Any]:
    grade_dir = Path(manifest["artifact_dir"]) / "grades" / batch_id / ("judge-%d" % judge)
    result_path = grade_dir / "result.json"
    visible, key = _judge_prompt(batch, int(_sha_bytes((manifest["manifest_id"] + batch_id + str(judge)).encode("utf-8"))[:16], 16))
    developer = _judge_developer(batch, key)
    item_ids = [key[pair["pair_id"]]["item_id"] for pair in batch]
    expected_identity = {"manifest_id": manifest["manifest_id"], "grade_plan_sha256": grade_plan["sha256"], "batch_id": batch_id, "judge": judge, "item_ids": item_ids, "input_sha256": _sha_bytes(visible.encode("utf-8")), "developer_sha256": _sha_bytes(developer.encode("utf-8"))}
    if result_path.exists():
        cached = _load_json(result_path)
        _validate_cached_judge_result(cached, expected_identity, result_path)
        return cached
    output, trace, stderr = grade_dir / "output.json", grade_dir / "trace.jsonl", grade_dir / "stderr.txt"
    command = grade_dir / "command.json"
    with tempfile.TemporaryDirectory(prefix="jp-writing-judge-") as temp:
        scratch = Path(temp) / "scratch"
        scratch.mkdir()
        argv = _codex_argv(developer, output, scratch)
        _write_json(command, {"argv": argv, "cwd": str(scratch), "requested_model": MODEL, "requested_reasoning_effort": REASONING, "blind": True, **expected_identity})
        process = _run_process(argv, scratch, visible, TIMEOUT_SECONDS, trace, stderr)
    text = output.read_text(encoding="utf-8") if output.is_file() else ""
    events, errors = _parse_jsonl(trace)
    info = _trace_info(events)
    status = "complete"
    reason = "completed"
    parsed = None
    if process["timed_out"]:
        status, reason = "timeout", "deadline"
    elif process["spawn_error"] or process["returncode"] != 0:
        status, reason = "error", "spawn_error" if process["spawn_error"] else "codex_exit_%s" % process["returncode"]
    elif errors or not info["turn_completed"] or info["tool_types"]:
        status, reason = "inconclusive", "trace_or_tool_violation"
    else:
        try:
            parsed = {"items_by_id": _validated_judge_items(text, item_ids)}
        except (json.JSONDecodeError, ValueError) as exc:
            status, reason = "inconclusive", "invalid_judge_json: %s" % exc
    record = {"schema_version": GRADE_VERSION, **expected_identity, "execution_status": status, "reason": reason, "blind_key": key, "result": parsed, "requested_model": MODEL, "requested_reasoning_effort": REASONING, "observed_model": info["observed_models"], "trace_errors": errors, **process, "artifacts": {"output": str(output), "trace": str(trace), "stderr": str(stderr), "command": str(command)}}
    _write_json(result_path, record)
    return record


def _majority(values: Sequence[Any]) -> Optional[Any]:
    count = Counter(values)
    return next((value for value, amount in count.items() if amount >= 2), None)


def exact_two_sided_sign_test(wins: int, losses: int) -> float:
    n = wins + losses
    if n == 0:
        return 1.0
    tail = sum(math.comb(n, k) for k in range(0, min(wins, losses) + 1)) / float(2 ** n)
    return min(1.0, 2.0 * tail)


def case_level_outcomes(consensuses: Sequence[Mapping[str, Any]]) -> List[Dict[str, Any]]:
    """Collapse two repetitions before any inferential sign test."""
    by_case: Dict[str, List[Mapping[str, Any]]] = defaultdict(list)
    for row in consensuses:
        by_case[str(row["pair_id"]).rsplit("-r", 1)[0]].append(row)
    outcomes = []
    for case_id, rows in sorted(by_case.items()):
        if len(rows) != REPETITIONS:
            continue
        winners = [row.get("winner") for row in rows]
        winner = winners[0] if winners[0] in {"baseline", "candidate"} and winners[0] == winners[1] else None
        target_scores = {arm: sum(bool(row.get("target_ok", {}).get(arm)) for row in rows) for arm in ("baseline", "candidate")}
        target_winner = "candidate" if target_scores["candidate"] > target_scores["baseline"] else "baseline" if target_scores["baseline"] > target_scores["candidate"] else None
        outcomes.append({"case_id": case_id, "raw_pair_preferences": [row.get("preference") for row in rows], "winner": winner, "status": "resolved" if winner else "tie_or_replication_disagreement", "target_ok_score": target_scores, "target_winner": target_winner})
    return outcomes


def family_gates(consensuses: Sequence[Mapping[str, Any]]) -> Dict[str, Any]:
    """Compute protocol adoption/regression gates without treating missing work as failures."""
    grouped: Dict[str, List[Mapping[str, Any]]] = defaultdict(list)
    for row in consensuses:
        grouped[str(row.get("family", "unclassified"))].append(row)
    families = {}
    for family, rows in sorted(grouped.items()):
        baseline_over = sum(bool(row.get("overcorrection", {}).get("baseline")) for row in rows)
        candidate_over = sum(bool(row.get("overcorrection", {}).get("candidate")) for row in rows)
        new_semantic = sum(row.get("semantic_ok", {}).get("baseline") is True and row.get("semantic_ok", {}).get("candidate") is False for row in rows)
        new_exact = sum(row.get("structural_status", {}).get("baseline") == "pass" and row.get("structural_status", {}).get("candidate") == "fail" for row in rows)
        families[family] = {"completed_pairs": len(rows), "baseline_overcorrection": baseline_over, "candidate_overcorrection": candidate_over, "overcorrection_regression": candidate_over > baseline_over, "new_candidate_semantic_violations": new_semantic, "new_candidate_exact_violations": new_exact}
    return families


def effect_claim_gate(target_wins: int, target_losses: int, primary_p: float, new_semantic_total: int, new_exact_total: int, overcorrection_regressions: Sequence[str], completeness: Mapping[str, Any]) -> Dict[str, Any]:
    requirements = {"target_wins_exceed_losses": target_wins > target_losses, "two_sided_p_lt_0_05": primary_p < 0.05, "no_new_candidate_semantic_violations": new_semantic_total == 0, "no_new_candidate_exact_violations": new_exact_total == 0, "no_family_overcorrection_regression": not overcorrection_regressions}
    if not completeness["complete"]:
        return {"status": "inconclusive_missing_data", "requirements": requirements, "completeness": dict(completeness), "limitation": "partial generation or judge evidence cannot support an effect claim"}
    return {"status": "eligible" if all(requirements.values()) else "not_eligible", "requirements": requirements, "completeness": dict(completeness), "limitation": "eligible is limited to this fixed diagnostic set and does not establish general Japanese quality"}


def grade_manifest(manifest_path: Path, batch_size: int = 10, workers: int = 4) -> Dict[str, Any]:
    if batch_size < 1 or batch_size > 20 or workers < 1 or workers > 4:
        raise ValidationError("batch-size must be 1..20 and workers 1..4")
    manifest = load_manifest(manifest_path, check_sources=True)
    pairs = _completed_pairs(manifest)
    batches = [pairs[index:index + batch_size] for index in range(0, len(pairs), batch_size)]
    grade_plan = _grade_plan(manifest, pairs, batch_size)
    grade_plan_path = _write_grade_plan(manifest, grade_plan)
    calls = [("batch-%03d" % (index + 1), batch, judge) for index, batch in enumerate(batches) for judge in (1, 2, 3)]
    records = []
    with concurrent.futures.ThreadPoolExecutor(max_workers=workers) as pool:
        futures = [pool.submit(_judge_one, manifest, batch, batch_id, judge, grade_plan) for batch_id, batch, judge in calls]
        for future in concurrent.futures.as_completed(futures):
            records.append(future.result())
    by_pair: Dict[str, List[Tuple[Mapping[str, Any], Mapping[str, Any]]]] = defaultdict(list)
    for record in records:
        if record["execution_status"] != "complete":
            continue
        batch = next(batch for batch_id, batch, judge in calls if batch_id == record["batch_id"] and judge == record["judge"])
        for pair in batch:
            item_id = record["blind_key"][pair["pair_id"]]["item_id"]
            by_pair[pair["pair_id"]].append((record, record["result"]["items_by_id"][item_id]))
    consensuses = []
    for pair_id, votes in sorted(by_pair.items()):
        if len(votes) != 3:
            continue
        def arm_axis(axis: str, arm: str) -> Optional[bool]:
            values = []
            for record, item in votes:
                key = record["blind_key"][pair_id]
                side = "X" if key["X"] == arm else "Y"
                values.append(item[axis][side])
            return _majority(values)
        arm_preferences = []
        for record, item in votes:
            preference = item["preference"]
            arm_preferences.append(record["blind_key"][pair_id].get(preference, "tie"))
        winner = _majority(arm_preferences)
        pair = next(pair for pair in pairs if pair["pair_id"] == pair_id)
        checks = pair["generation_checks"]
        consensuses.append({"pair_id": pair_id, "family": pair["case"].get("family", "unclassified"), "semantic_ok": {arm: arm_axis("semantic_ok", arm) for arm in ("baseline", "candidate")}, "target_ok": {arm: arm_axis("target_ok", arm) for arm in ("baseline", "candidate")}, "overcorrection": {arm: arm_axis("overcorrection", arm) for arm in ("baseline", "candidate")}, "structural_status": {arm: checks[arm].get("structural_status") for arm in ("baseline", "candidate")}, "winner": winner if winner in {"baseline", "candidate"} else None, "preference": winner or "uncertain", "judge_preferences": arm_preferences, "rationales": [item["rationale"] for _, item in votes]})
    # Repetitions are useful robustness observations, but treating both as
    # independent sign-test samples would pseudo-replicate each case.  A case
    # enters the inferential denominator only when both repetitions complete
    # and agree on the same arm; disagreements and ties remain descriptive.
    case_consensus = case_level_outcomes(consensuses)
    wins = sum(row["winner"] == "candidate" for row in case_consensus)
    losses = sum(row["winner"] == "baseline" for row in case_consensus)
    target_wins = sum(row["target_winner"] == "candidate" for row in case_consensus)
    target_losses = sum(row["target_winner"] == "baseline" for row in case_consensus)
    pairwise = []
    for row in consensuses:
        values = row["judge_preferences"]
        pairwise.extend([values[0] == values[1], values[0] == values[2], values[1] == values[2]])
    rubric = {}
    for arm in ("baseline", "candidate"):
        rubric[arm] = {
            axis: sum(row[axis][arm] is expected for row in consensuses)
            for axis, expected in (("semantic_ok", True), ("target_ok", True), ("overcorrection", False))
        }
        rubric[arm]["denominator_completed_pairs"] = len(consensuses)
    families = family_gates(consensuses)
    new_semantic_total = sum(row["new_candidate_semantic_violations"] for row in families.values())
    new_exact_total = sum(row["new_candidate_exact_violations"] for row in families.values())
    overcorrection_regressions = sorted(family for family, row in families.items() if row["overcorrection_regression"])
    primary_p = exact_two_sided_sign_test(target_wins, target_losses)
    expected_pairs = len(manifest["generation_cases"]) * REPETITIONS
    expected_cases = len(manifest["generation_cases"])
    expected_judge_calls = ((expected_pairs + batch_size - 1) // batch_size) * 3
    judge_status_counts = Counter(row["execution_status"] for row in records)
    completeness = {"expected_pairs": expected_pairs, "pairs_available": len(pairs), "pairs_judged_complete": len(consensuses), "expected_judge_calls": expected_judge_calls, "judge_calls_requested": len(calls), "judge_calls_complete": judge_status_counts.get("complete", 0), "expected_cases_with_both_repetitions": expected_cases, "cases_with_both_repetitions_complete": len(case_consensus)}
    completeness["complete"] = (completeness["pairs_available"] == expected_pairs and completeness["pairs_judged_complete"] == expected_pairs and completeness["judge_calls_requested"] == expected_judge_calls and completeness["judge_calls_complete"] == expected_judge_calls and completeness["cases_with_both_repetitions_complete"] == expected_cases)
    claim_gate = effect_claim_gate(target_wins, target_losses, primary_p, new_semantic_total, new_exact_total, overcorrection_regressions, completeness)
    report = {"schema_version": GRADE_VERSION, "manifest_id": manifest["manifest_id"], "grade_plan_path": str(grade_plan_path), "grade_plan_sha256": grade_plan["sha256"], "pairs_available": len(pairs), "pairs_judged_complete": len(consensuses), "judge_calls_requested": len(calls), "judge_status_counts": dict(sorted(judge_status_counts.items())), "consensus": consensuses, "rubric_majority_completed_pairs_only": rubric, "raw_pair_descriptive": {"candidate_wins": sum(row["winner"] == "candidate" for row in consensuses), "candidate_losses": sum(row["winner"] == "baseline" for row in consensuses), "ties_or_uncertain": len(consensuses) - sum(row["winner"] in {"candidate", "baseline"} for row in consensuses), "denominator_completed_pairs": len(consensuses)}, "primary_target_case_level": {"rule": "sum majority target_ok across both repetitions per case; compare candidate with baseline", "cases_with_both_repetitions_complete": len(case_consensus), "candidate_wins": target_wins, "candidate_losses": target_losses, "ties": len(case_consensus) - target_wins - target_losses, "two_sided_sign_test_p": primary_p, "denominator_resolved_cases": target_wins + target_losses}, "secondary_preference_case_level": {"rule": "only both-repetition preference agreement contributes a win or loss", "consensus": case_consensus, "candidate_wins": wins, "candidate_losses": losses, "ties_or_replication_disagreement": len(case_consensus) - wins - losses, "two_sided_sign_test_p": exact_two_sided_sign_test(wins, losses), "denominator_resolved_cases": wins + losses}, "family_gates_completed_pairs_only": families, "effect_claim_gate": claim_gate, "agreement": {"pairwise_preference_agreement": sum(pairwise) / len(pairwise) if pairwise else None, "unanimous_preference_pairs": sum(len(set(row["judge_preferences"])) == 1 for row in consensuses), "majority_resolved_pairs": sum(row["preference"] != "uncertain" for row in consensuses)}, "completed_at": _now()}
    _write_json(Path(manifest["artifact_dir"]) / "grade-summary.json", report)
    return report


def summarize(manifest_path: Path) -> Dict[str, Any]:
    manifest = load_manifest(manifest_path, check_sources=False)
    records = []
    for run in manifest["runs"]:
        path = _result_path(manifest, run)
        if path.is_file():
            records.append(_load_json(path))
    status = Counter(row["execution_status"] for row in records)
    structural = Counter((row["arm"], row["structural_status"]) for row in records if row["execution_status"] == "complete")
    grade_path = Path(manifest["artifact_dir"]) / "grade-summary.json"
    report = {"manifest_id": manifest["manifest_id"], "runs_expected": len(manifest["runs"]), "runs_observed": len(records), "execution_status_counts": dict(sorted(status.items())), "structural_completed_only": {arm: {state: structural[(arm, state)] for state in ("pass", "fail")} for arm in ("baseline", "candidate")}, "complete": len(records) == len(manifest["runs"]) and status == Counter({"complete": len(manifest["runs"])}), "grade": _load_json(grade_path) if grade_path.is_file() else {"status": "not_run"}, "routing": {"status": "not_run", "reason": "native-routing-probe-owns-skill-selection", "excluded_cases": manifest.get("routing_cases_excluded", [])}}
    _write_json(Path(manifest["artifact_dir"]) / "summary.json", report)
    return report


def _path(value: str) -> Path:
    return Path(value).expanduser()


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description=__doc__)
    sub = parser.add_subparsers(dest="command", required=True)
    plan = sub.add_parser("plan", help="freeze cases, skills, configuration and run order")
    plan.add_argument("--cases", type=_path, default=DEFAULT_CASES)
    plan.add_argument("--protocol", type=_path, default=DEFAULT_PROTOCOL)
    plan.add_argument("--baseline-skill", type=_path, required=True, help="external compiled baseline snapshot, never an unrendered source skill")
    plan.add_argument("--candidate-skill", type=_path, required=True, help="external compiled candidate snapshot")
    plan.add_argument("--output", type=_path)
    plan.add_argument("--artifact-root", type=_path, default=DEFAULT_ARTIFACT_ROOT)
    plan.add_argument("--seed", type=int)
    for name, help_text in (("preflight", "inspect model-visible prompts; no model call"), ("run", "execute a frozen manifest"), ("grade", "blind three-judge batches"), ("summarize", "summarize frozen evidence")):
        command = sub.add_parser(name, help=help_text)
        command.add_argument("--manifest", type=_path, required=True)
        if name == "run":
            command.add_argument("--workers", type=int, default=4)
            command.add_argument("--timeout", type=int, default=TIMEOUT_SECONDS)
        if name == "grade":
            command.add_argument("--batch-size", type=int, default=10)
            command.add_argument("--workers", type=int, default=4)
    return parser


def main(argv: Optional[Sequence[str]] = None) -> int:
    args = build_parser().parse_args(argv)
    try:
        if args.command == "plan":
            root = _external(args.artifact_root, "artifact root")
            if args.output:
                output = args.output
            else:
                suffix = "%d" % int(time.time())
                output = root / ("run-" + suffix) / "manifest.json"
            report = create_manifest(args.cases, args.baseline_skill, args.candidate_skill, output, args.seed, args.protocol)
            result = {"manifest": str(output.resolve()), "manifest_id": report["manifest_id"], "generation_runs": len(report["runs"]), "routing_cases_excluded": len(report["routing_cases_excluded"])}
        elif args.command == "preflight":
            result = preflight(args.manifest)
        elif args.command == "run":
            result = run_manifest(args.manifest, args.workers, args.timeout)
        elif args.command == "grade":
            result = grade_manifest(args.manifest, args.batch_size, args.workers)
        else:
            result = summarize(args.manifest)
        print(json.dumps(result, ensure_ascii=False, indent=2))
        if args.command == "preflight" and result.get("status") != "pass":
            return 2
        return 0
    except ValidationError as exc:
        print("error: %s" % exc, file=sys.stderr)
        return 2


if __name__ == "__main__":
    raise SystemExit(main())
