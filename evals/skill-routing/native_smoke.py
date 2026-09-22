#!/usr/bin/env python3
"""Run native Codex/OMP ownership and representative behavior smoke cases."""

from __future__ import annotations

import argparse
from concurrent.futures import ThreadPoolExecutor
import json
import os
from pathlib import Path
import shutil
import subprocess
import sys
import tempfile
from typing import Any, Iterable


ROOT = Path(__file__).resolve().parents[2]
PLUGIN_NAMES = [
    "code-review", "code-intelligence", "workflow", "developer-writing", "prompting",
    "product", "figma-workflow", "interface-design", "operations-ui", "design-patterns",
]
SECRET_ENV = {
    "OPENAI_API_KEY", "ANTHROPIC_API_KEY", "ANTHROPIC_OAUTH_TOKEN", "GEMINI_API_KEY",
    "AZURE_OPENAI_API_KEY", "GITHUB_TOKEN", "GH_TOKEN", "PERPLEXITY_API_KEY", "EXA_API_KEY",
}
SCHEMA = {
    "type": "object",
    "properties": {
        "selected_skills": {"type": "array", "items": {"type": "string"}},
        "status": {"enum": ["passed", "blocked", "not_run", "inconclusive"]},
        "summary": {"type": "string"},
    },
    "required": ["selected_skills", "status", "summary"],
    "additionalProperties": False,
}


def command_version(command: str) -> str:
    completed = subprocess.run([command, "--version"], text=True, capture_output=True)
    return (completed.stdout or completed.stderr).strip()


def run(command: list[str], *, cwd: Path, env: dict[str, str], timeout: int = 600) -> dict[str, Any]:
    completed = subprocess.run(command, cwd=cwd, env=env, text=True, capture_output=True, timeout=timeout)
    return {
        "command": command, "returncode": completed.returncode,
        "stdout": completed.stdout, "stderr": completed.stderr,
    }


def scrub(env: dict[str, str]) -> dict[str, str]:
    result = env.copy()
    for name in SECRET_ENV:
        result.pop(name, None)
    return result


def recursively_find_models(value: Any) -> set[str]:
    models = set()
    if isinstance(value, dict):
        for key, child in value.items():
            if key.lower() in {"model", "modelid", "model_id"} and isinstance(child, str):
                models.add(child)
            models.update(recursively_find_models(child))
    elif isinstance(value, list):
        for child in value:
            models.update(recursively_find_models(child))
    return models


def parse_json_lines(text: str) -> list[Any]:
    values = []
    for line in text.splitlines():
        try:
            values.append(json.loads(line))
        except json.JSONDecodeError:
            continue
    return values


def find_contract(value: Any) -> dict[str, Any] | None:
    if isinstance(value, dict):
        if {"selected_skills", "status", "summary"}.issubset(value):
            return value
        for child in value.values():
            found = find_contract(child)
            if found:
                return found
    elif isinstance(value, list):
        for child in reversed(value):
            found = find_contract(child)
            if found:
                return found
    elif isinstance(value, str):
        try:
            decoded = json.loads(value)
        except json.JSONDecodeError:
            return None
        return find_contract(decoded)
    return None


def inventory() -> list[str]:
    names = []
    for plugin in PLUGIN_NAMES:
        for skill in sorted((ROOT / "plugins" / plugin / "skills").glob("*/SKILL.md")):
            names.append(skill.parent.name)
    if len(names) != 31 or len(set(names)) != 31:
        raise RuntimeError(f"expected 31 unique skills, got {len(names)}/{len(set(names))}")
    return names


def make_fixture(directory: Path) -> Path:
    root = directory / "semantic-fixture"
    (root / "src").mkdir(parents=True)
    (root / "Cargo.toml").write_text(
        '[package]\nname = "semantic_fixture"\nversion = "0.1.0"\nedition = "2021"\n',
        encoding="utf-8",
    )
    (root / "src/lib.rs").write_text(
        "pub fn target_value() -> u32 { 42 }\n\npub fn first_reference() -> u32 { target_value() }\n\npub fn second_reference() -> u32 { target_value() + 1 }\n",
        encoding="utf-8",
    )
    subprocess.run(["git", "init", "-q"], cwd=root, check=True)
    return root


def prompt_for(case: dict[str, Any], skills: list[str]) -> str:
    mode_instruction = (
        "This is ownership classification only: identify the minimal skill owner, do not execute the request, "
        "inspect prerequisites, or add semantic-code-intelligence unless the request directly asks for definition, "
        "references, type, implementation, or rename. Return status passed. "
        if case["mode"] == "ownership"
        else ""
    )
    return (
        "You are running a read-only routing smoke. Do not edit files, use remote mutations, install anything, "
        "or invent tool results. The launcher has installed and enabled every listed skill in the native registry. "
        + mode_instruction
        + "Use current native skill discovery. Select only marketplace skills directly needed for the user request; "
        "general host behavior means an empty list. If a directly requested semantic prerequisite is unavailable, "
        "keep the semantic skill selected, set status to blocked, and do not use text search as a substitute. "
        "Return only this exact JSON shape with no extra fields: "
        '{"selected_skills":["bare-skill-name"],"status":"passed|blocked|not_run|inconclusive","summary":"observable result or blocker"}. '
        "Bare skill names available: " + ", ".join(skills)
        + "\n\nUser request:\n" + case["prompt"]
    )


def copy_codex_auth(home: Path) -> tuple[bool, str | None]:
    source_home = Path(os.environ.get("CODEX_HOME", Path.home() / ".codex"))
    source = source_home / "auth.json"
    if not source.is_file():
        return False, f"Codex auth missing at {source}"
    destination = home / ".codex" / "auth.json"
    destination.parent.mkdir(parents=True)
    shutil.copy2(source, destination)
    destination.chmod(0o400)
    return True, None


def prepare_codex(work: Path) -> tuple[dict[str, str], list[dict[str, Any]], str | None]:
    home = work / "codex-home"
    home.mkdir()
    ok, blocker = copy_codex_auth(home)
    env = scrub(os.environ)
    env["HOME"] = str(home)
    env["CODEX_HOME"] = str(home / ".codex")
    records = []
    if not ok:
        return env, records, blocker
    records.append(run(["codex", "plugin", "marketplace", "add", str(ROOT)], cwd=ROOT, env=env, timeout=60))
    for plugin in PLUGIN_NAMES:
        records.append(run(["codex", "plugin", "add", f"{plugin}@sonsu-marketplace"], cwd=ROOT, env=env, timeout=60))
    failures = [record for record in records if record["returncode"] != 0]
    if failures:
        return env, records, failures[0]["stderr"] or failures[0]["stdout"]
    return env, records, None


def prepare_omp(work: Path) -> dict[str, str]:
    home = work / "omp-home"
    home.mkdir()
    env = scrub(os.environ)
    env["HOME"] = str(home)
    return env


def codex_case(case: dict[str, Any], work: Path, env: dict[str, str], skills: list[str]) -> dict[str, Any]:
    case_dir = work / "codex" / case["id"]
    case_dir.mkdir(parents=True)
    schema_path = case_dir / "schema.json"
    final_path = case_dir / "final.json"
    schema_path.write_text(json.dumps(SCHEMA), encoding="utf-8")
    cwd = make_fixture(case_dir) if case.get("semantic") else ROOT
    command = [
        "codex", "exec", "--ephemeral", "--ignore-user-config", "--ignore-rules",
        "--sandbox", "read-only", "--json", "--output-schema", str(schema_path),
        "--output-last-message", str(final_path), "--cd", str(cwd),
    ]
    command += [
        "-c", 'mcp_servers.mcpls.command="python3"',
        "-c", f"mcp_servers.mcpls.args=[{json.dumps(str(ROOT / 'plugins/code-intelligence/scripts/launch-mcpls.py'))}]",
    ]
    if case.get("semantic") and not case.get("disable_semantic_prerequisite"):
        command += [
            "-c", "mcp_servers.mcpls.enabled=true",
            "-c", 'mcp_servers.mcpls.enabled_tools=["lsp_definition","lsp_references"]',
        ]
    else:
        command += ["-c", "mcp_servers.mcpls.enabled=false"]
    command.append(prompt_for(case, skills))
    record = run(command, cwd=cwd, env=env)
    events = parse_json_lines(record["stdout"])
    contract = None
    if final_path.exists():
        try:
            contract = json.loads(final_path.read_text(encoding="utf-8"))
        except json.JSONDecodeError:
            contract = None
    return {
        "host": "codex", "case": case["id"], "command": command,
        "returncode": record["returncode"], "stderr": record["stderr"],
        "events": events, "contract": contract,
        "observed_models": sorted(recursively_find_models(events)),
    }


def omp_case(case: dict[str, Any], work: Path, env: dict[str, str], skills: list[str]) -> dict[str, Any]:
    case_dir = work / "omp" / case["id"]
    case_dir.mkdir(parents=True)
    cwd = make_fixture(case_dir) if case.get("semantic") else ROOT
    command = ["omp"]
    for plugin in PLUGIN_NAMES:
        command += ["--plugin-dir", str(ROOT / "plugins" / plugin)]
    command += [
        "--skills", ",".join(skills), "--no-rules", "--no-session", "--no-extensions",
        "--approval-mode", "always-ask", "--mode", "json", "--cwd", str(cwd),
    ]
    if case.get("semantic") and not case.get("disable_semantic_prerequisite"):
        command += ["--tools", "read,lsp"]
    else:
        command += ["--tools", "read", "--no-lsp"]
    command += ["-p", prompt_for(case, skills)]
    record = run(command, cwd=cwd, env=env)
    events = parse_json_lines(record["stdout"])
    contract = find_contract(events)
    return {
        "host": "omp", "case": case["id"], "command": command,
        "returncode": record["returncode"], "stderr": record["stderr"],
        "events": events, "contract": contract,
        "observed_models": sorted(recursively_find_models(events)),
    }


def semantic_blocker(host: str, case: dict[str, Any]) -> str | None:
    if not case.get("semantic") or case.get("disable_semantic_prerequisite"):
        return None
    rust = shutil.which("rust-analyzer")
    if not rust:
        return "rust-analyzer is missing from PATH"
    if host == "codex":
        mcpls = shutil.which("mcpls")
        if not mcpls:
            return "mcpls 0.6.0 is missing from PATH"
        if command_version(mcpls) != "mcpls 0.6.0":
            return f"expected mcpls 0.6.0, observed {command_version(mcpls)!r}"
    return None


def assess(case: dict[str, Any], execution: dict[str, Any]) -> dict[str, Any]:
    if execution["returncode"] != 0:
        return {"status": "blocked", "reason": execution["stderr"] or "native CLI failed"}
    contract = execution.get("contract")
    if not isinstance(contract, dict):
        return {"status": "fail", "reason": "no valid response contract"}
    selected = set(contract.get("selected_skills", []))
    expected = set(case.get("expected_skills", []))
    if selected != expected:
        return {"status": "fail", "reason": f"selected {sorted(selected)}, expected {sorted(expected)}"}
    forbidden = set(case.get("must_not_select", []))
    if selected & forbidden:
        return {"status": "fail", "reason": f"forbidden selection: {sorted(selected & forbidden)}"}
    expected_status = case.get("expected_status")
    if expected_status and contract.get("status") != expected_status:
        if contract.get("status") == "blocked":
            return {"status": "blocked", "reason": contract.get("summary", "semantic prerequisite blocked")}
        return {"status": "fail", "reason": f"status {contract.get('status')}, expected {expected_status}"}
    summary = contract.get("summary", "")
    missing = [value for value in case.get("must_contain", []) if value not in summary]
    if missing:
        return {"status": "fail", "reason": f"summary missing {missing}"}
    return {"status": "passed", "reason": "selection and behavior contract matched"}


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--host", choices=["codex", "omp", "both"], required=True)
    parser.add_argument("--mode", choices=["ownership", "behavior"], required=True)
    parser.add_argument("--cases", type=Path, required=True)
    parser.add_argument("--case", action="append", dest="case_ids")
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    args.output.mkdir(parents=True, exist_ok=True)
    data = json.loads(args.cases.read_text(encoding="utf-8"))
    cases = [case for case in data["cases"] if case["mode"] == args.mode]
    if args.case_ids:
        requested = set(args.case_ids)
        cases = [case for case in cases if case["id"] in requested]
        missing = requested - {case["id"] for case in cases}
        if missing:
            parser.error(f"case(s) absent from selected mode: {', '.join(sorted(missing))}")
    skills = inventory()
    hosts = ["codex", "omp"] if args.host == "both" else [args.host]
    work = Path(tempfile.mkdtemp(prefix="sonsu-native-smoke-"))
    results = []
    setup_records: dict[str, Any] = {}
    codex_env = None
    codex_blocker = None
    if "codex" in hosts:
        codex_env, records, codex_blocker = prepare_codex(work)
        setup_records["codex"] = records
    omp_env = prepare_omp(work) if "omp" in hosts else None
    omp_blocker = (
        "OMP provider credentials are intentionally removed from the disposable profile"
        if "omp" in hosts else None
    )
    try:
        jobs = [(host, case) for host in hosts for case in cases]

        def execute(item: tuple[str, dict[str, Any]]) -> dict[str, Any]:
            host, case = item
            blocker = codex_blocker if host == "codex" else omp_blocker
            blocker = blocker or semantic_blocker(host, case)
            if blocker:
                return {"host": host, "case": case["id"], "assessment": {"status": "blocked", "reason": blocker}}
            execution = codex_case(case, work, codex_env, skills) if host == "codex" else omp_case(case, work, omp_env, skills)
            execution["assessment"] = assess(case, execution)
            return execution

        with ThreadPoolExecutor(max_workers=min(4, max(1, len(jobs)))) as executor:
            results.extend(executor.map(execute, jobs))
        statuses = [item["assessment"]["status"] for item in results]
        overall = "passed" if statuses and all(status == "passed" for status in statuses) else (
            "blocked" if any(status == "blocked" for status in statuses) and not any(status == "fail" for status in statuses) else "failed"
        )
        evidence = {
            "status": overall, "host": args.host, "mode": args.mode,
            "cli_versions": {"codex": command_version("codex"), "omp": command_version("omp")},
            "setup": setup_records, "results": results,
        }
        (args.output / "summary.json").write_text(json.dumps(evidence, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
        print(json.dumps({"status": overall, "cases": len(results), "evidence": str(args.output / 'summary.json')}, ensure_ascii=False))
        return 0 if overall == "passed" else (2 if overall == "blocked" else 1)
    finally:
        shutil.rmtree(work, ignore_errors=True)


if __name__ == "__main__":
    raise SystemExit(main())
