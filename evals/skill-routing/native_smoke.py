#!/usr/bin/env python3
"""Run native Codex/OMP ownership and representative behavior smoke cases."""

from __future__ import annotations

import argparse
from concurrent.futures import ThreadPoolExecutor
import importlib.util
import json
import os
import re
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


def command_version(command: str) -> str | None:
    try:
        completed = subprocess.run([command, "--version"], text=True, capture_output=True)
    except FileNotFoundError:
        return None
    return (completed.stdout or completed.stderr).strip()


def selected_cli_versions(hosts: Iterable[str]) -> dict[str, str | None]:
    return {host: command_version(host) for host in hosts}


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

def namespaced_inventory() -> set[str]:
    return {
        f"{plugin}:{skill.parent.name}"
        for plugin in PLUGIN_NAMES
        for skill in (ROOT / "plugins" / plugin / "skills").glob("*/SKILL.md")
    }


def load_native_probe() -> Any:
    path = ROOT / "evals/plugin-compat/native_probe.py"
    spec = importlib.util.spec_from_file_location("sonsu_native_probe", path)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"cannot load native probe from {path}")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


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


def prompt_for(case: dict[str, Any], native_catalog: list[dict[str, str]] | None = None) -> str:
    mode_instruction = (
        "This is ownership classification only: identify the minimal skill owner, load that skill from native "
        "discovery, do not execute the request, inspect prerequisites, or add semantic-code-intelligence unless "
        "the request directly asks for definition, references, type, implementation, or rename. Return status "
        "passed. "
        if case["mode"] == "ownership"
        else ""
    )
    semantic_instruction = (
        "For a semantic success request, invoke the native definition and references actions directly and base "
        "the answer on their returned locations. Reading or searching source text is not a substitute. "
        if case.get("semantic") and not case.get("disable_semantic_prerequisite")
        else ""
    )
    discovery = ""
    if native_catalog is not None:
        discovery = (
            "\nNative discovery catalog:\n"
            + json.dumps(native_catalog, ensure_ascii=False, separators=(",", ":"))
        )
    return (
        case["prompt"]
        + discovery
        + "\n\n<routing-probe>\n"
        + "You are running a read-only routing smoke. Do not edit files, use remote mutations, install anything, "
        "or invent tool results. Use the skills exposed by current native discovery. "
        + mode_instruction
        + semantic_instruction
        + "Select only marketplace skills directly needed for the user request; general host behavior means an "
        "empty list. If a directly requested semantic prerequisite is unavailable, keep the semantic skill "
        "selected, set status to blocked, and do not use text search as a substitute. Return only this exact JSON "
        "shape with no extra fields: "
        '{"selected_skills":["bare-skill-name"],"status":"passed|blocked|not_run|inconclusive","summary":"observable result or blocker"}.'
        + "\n</routing-probe>"
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


def codex_registry_skills(env: dict[str, str]) -> tuple[list[dict[str, str]], list[Any]]:
    native_probe = load_native_probe()
    plugin_key = 'plugins."code-intelligence@sonsu-marketplace".mcp_servers.mcpls'
    client = native_probe.RpcClient(
        [
            "codex", "app-server", "--stdio",
            "-c", f"{plugin_key}.enabled=false",
        ],
        cwd=ROOT,
        env=env,
    )
    try:
        client.request("initialize", {
            "clientInfo": {"name": "sonsu-routing-smoke", "version": "1.0.0"},
            "capabilities": {"experimentalApi": True},
        }, timeout=30)
        response = client.request(
            "skills/list",
            {"cwds": [str(ROOT)], "forceReload": True},
            timeout=30,
        )
        bucket = response["data"][0]
        catalog = [
            {"name": skill["name"], "description": skill.get("description", "")}
            for skill in bucket["skills"]
            if (skill.get("pluginId") or "").endswith("@sonsu-marketplace")
        ]
        return catalog, bucket.get("errors", [])
    finally:
        client.close()


def prepare_codex(work: Path) -> tuple[dict[str, str], list[dict[str, Any]], str | None]:
    home = work / "codex-home"
    home.mkdir()
    ok, blocker = copy_codex_auth(home)
    env = scrub(os.environ)
    env["HOME"] = str(home)
    env["CODEX_HOME"] = str(home / ".codex")
    records: list[dict[str, Any]] = []
    if not ok:
        return env, records, blocker
    records.append(run(["codex", "plugin", "marketplace", "add", str(ROOT)], cwd=ROOT, env=env, timeout=60))
    for plugin in PLUGIN_NAMES:
        records.append(run(["codex", "plugin", "add", f"{plugin}@sonsu-marketplace"], cwd=ROOT, env=env, timeout=60))
    failures = [record for record in records if record["returncode"] != 0]
    if failures:
        return env, records, failures[0]["stderr"] or failures[0]["stdout"]
    try:
        catalog, errors = codex_registry_skills(env)
    except (OSError, RuntimeError, KeyError, TypeError, json.JSONDecodeError) as error:
        return env, records, f"Codex native skill registry failed: {error}"
    loaded = {skill["name"] for skill in catalog}
    expected = namespaced_inventory()
    records.append({
        "registry_skills": sorted(loaded),
        "registry_catalog": catalog,
        "registry_errors": errors,
    })
    if errors or loaded != expected:
        return env, records, (
            f"Codex native skill registry mismatch: "
            f"missing={sorted(expected - loaded)} extra={sorted(loaded - expected)} errors={errors}"
        )
    return env, records, None


def prepare_omp(work: Path) -> tuple[dict[str, str], str | None]:
    home = work / "omp-home"
    home.mkdir()
    env = scrub(os.environ)
    env["HOME"] = str(home)
    source_value = os.environ.get("PI_CODING_AGENT_DIR")
    if not source_value:
        return env, (
            "OMP disposable credentials missing: set PI_CODING_AGENT_DIR to an explicit "
            "disposable source profile"
        )
    source = Path(source_value).expanduser().resolve()
    if not source.is_dir():
        return env, f"OMP disposable profile is not a directory: {source}"
    if not (source / "agent.db").is_file():
        return env, f"OMP disposable profile has no agent.db: {source}"
    destination = work / "omp-agent"
    destination.mkdir()
    for name in ("agent.db", "models.db", "config.yml", "lsp.json"):
        candidate = source / name
        if candidate.is_file():
            target = destination / name
            shutil.copy2(candidate, target)
            target.chmod(0o600)
    env["PI_CODING_AGENT_DIR"] = str(destination)
    return env, None


def codex_case(
    case: dict[str, Any],
    work: Path,
    env: dict[str, str],
    native_catalog: list[dict[str, str]],
) -> dict[str, Any]:
    case_dir = work / "codex" / case["id"]
    case_dir.mkdir(parents=True)
    schema_path = case_dir / "schema.json"
    final_path = case_dir / "final.json"
    schema_path.write_text(json.dumps(SCHEMA), encoding="utf-8")
    cwd = make_fixture(case_dir) if case.get("semantic") else ROOT
    command = [
        "codex", "exec", "--ephemeral", "--ignore-rules",
        "--sandbox", "read-only", "--json", "--output-schema", str(schema_path),
        "--output-last-message", str(final_path), "--cd", str(cwd),
    ]
    plugin_key = 'plugins."code-intelligence@sonsu-marketplace".mcp_servers.mcpls'
    if case.get("semantic") and not case.get("disable_semantic_prerequisite"):
        command += [
            "-c", f"{plugin_key}.enabled=true",
            "-c", f'{plugin_key}.enabled_tools=["lsp_get_definition","lsp_get_references"]',
        ]
    else:
        command += ["-c", f"{plugin_key}.enabled=false"]
    command.append(prompt_for(case, native_catalog))
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
    command += ["-p", prompt_for(case)]
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


def response_contract_error(contract: Any) -> str | None:
    if not isinstance(contract, dict):
        return "no valid response contract"
    required = set(SCHEMA["required"])
    if set(contract) != required:
        return f"response fields {sorted(contract)}, expected {sorted(required)}"
    selected = contract["selected_skills"]
    if not isinstance(selected, list) or not all(isinstance(name, str) for name in selected):
        return "selected_skills must be an array of strings"
    if len(selected) != len(set(selected)):
        return "selected_skills must not contain duplicates"
    if contract["status"] not in SCHEMA["properties"]["status"]["enum"]:
        return f"unsupported response status: {contract['status']!r}"
    if not isinstance(contract["summary"], str):
        return "summary must be a string"
    return None


def semantic_tool_results(events: list[Any]) -> dict[str, list[Any]]:
    results: dict[str, list[Any]] = {"definition": [], "references": []}
    suffixes = {
        "definition": "lsp_get_definition",
        "references": "lsp_get_references",
    }
    for event in events:
        if not isinstance(event, dict):
            continue
        if event.get("type") == "tool_execution_end":
            result = event.get("result")
            if not isinstance(result, dict) or result.get("isError") is True:
                continue
            details = result.get("details")
            if not isinstance(details, dict) or details.get("success") is False:
                continue
            action = details.get("action")
            if action not in results:
                request = details.get("request")
                action = request.get("action") if isinstance(request, dict) else None
            if event.get("toolName") == "lsp" and action in results:
                results[action].append(result)
        elif event.get("type") == "item.completed":
            item = event.get("item")
            if not isinstance(item, dict) or item.get("status") == "failed":
                continue
            tool_name = item.get("tool") or item.get("tool_name") or item.get("name")
            if not isinstance(tool_name, str):
                continue
            for action, suffix in suffixes.items():
                if tool_name.endswith(suffix):
                    result = item.get("result", item.get("output"))
                    if result is not None:
                        results[action].append(result)
    return results


def result_contains_location(result: Any, marker: str) -> bool:
    path, line_text = marker.rsplit(":", 1)
    line = int(line_text)
    text = json.dumps(result, ensure_ascii=False).replace("\\\\", "/")
    if path not in text:
        return False
    displayed = re.compile(rf"{re.escape(path)}(?:#L|:L|#|:){line}\b")
    zero_based = re.compile(rf'"(?:line|startLine)"\s*:\s*{line - 1}\b')
    return bool(displayed.search(text) or zero_based.search(text))


def semantic_trace_error(case: dict[str, Any], execution: dict[str, Any]) -> str | None:
    expected = case.get("expected_semantic_trace")
    if not expected:
        return None
    results = semantic_tool_results(execution.get("events", []))
    for action, locations in expected.items():
        action_results = results.get(action, [])
        if not action_results:
            return f"semantic trace missing {action} tool result"
        for location in locations:
            if not any(result_contains_location(result, location) for result in action_results):
                return f"semantic {action} result missing {location}"
    return None


def assess(case: dict[str, Any], execution: dict[str, Any]) -> dict[str, Any]:
    if execution["returncode"] != 0:
        return {"status": "fail", "reason": execution["stderr"] or "native CLI failed"}
    contract = execution.get("contract")
    contract_error = response_contract_error(contract)
    if contract_error:
        return {"status": "fail", "reason": contract_error}
    selected = set(contract["selected_skills"])
    expected = set(case.get("expected_skills", []))
    if selected != expected:
        return {"status": "fail", "reason": f"selected {sorted(selected)}, expected {sorted(expected)}"}
    forbidden = set(case.get("must_not_select", []))
    if selected & forbidden:
        return {"status": "fail", "reason": f"forbidden selection: {sorted(selected & forbidden)}"}
    expected_status = case.get(
        "expected_status",
        "passed" if case.get("mode") == "ownership" else None,
    )
    if expected_status and contract["status"] != expected_status:
        if contract["status"] == "blocked":
            return {"status": "blocked", "reason": contract["summary"]}
        return {"status": "fail", "reason": f"status {contract['status']}, expected {expected_status}"}
    missing = [value for value in case.get("must_contain", []) if value not in contract["summary"]]
    if missing:
        return {"status": "fail", "reason": f"summary missing {missing}"}
    trace_error = semantic_trace_error(case, execution)
    if trace_error:
        return {"status": "fail", "reason": trace_error}
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
    codex_setup_failure = None
    codex_catalog: list[dict[str, str]] = []
    if "codex" in hosts:
        if shutil.which("codex") is None:
            codex_env = scrub(os.environ)
            codex_blocker = "Codex CLI is missing from PATH"
            setup_records["codex"] = []
        else:
            codex_env, records, codex_blocker = prepare_codex(work)
            setup_records["codex"] = records
            if records and "registry_catalog" in records[-1]:
                codex_catalog = records[-1]["registry_catalog"]
            if codex_blocker is not None and records:
                codex_setup_failure = codex_blocker
                codex_blocker = None
    omp_env = None
    omp_blocker = None
    if "omp" in hosts:
        if shutil.which("omp") is None:
            omp_env = scrub(os.environ)
            omp_blocker = "OMP CLI is missing from PATH"
        else:
            omp_env, omp_blocker = prepare_omp(work)
    try:
        jobs = [(host, case) for host in hosts for case in cases]

        def execute(item: tuple[str, dict[str, Any]]) -> dict[str, Any]:
            host, case = item
            blocker = codex_blocker if host == "codex" else omp_blocker
            if host == "codex" and codex_setup_failure:
                return {
                    "host": host,
                    "case": case["id"],
                    "assessment": {"status": "fail", "reason": codex_setup_failure},
                }
            blocker = blocker or semantic_blocker(host, case)
            if blocker:
                return {"host": host, "case": case["id"], "assessment": {"status": "blocked", "reason": blocker}}
            execution = codex_case(case, work, codex_env, codex_catalog) if host == "codex" else omp_case(case, work, omp_env, skills)
            execution["assessment"] = assess(case, execution)
            return execution

        with ThreadPoolExecutor(max_workers=min(4, max(1, len(jobs)))) as executor:
            results.extend(executor.map(execute, jobs))
        statuses = [item["assessment"]["status"] for item in results]
        overall = "passed" if statuses and all(status == "passed" for status in statuses) else (
            "blocked" if any(status == "blocked" for status in statuses) and not any(status == "fail" for status in statuses) else "failed"
        )
        cli_versions = selected_cli_versions(hosts)
        evidence = {
            "status": overall, "host": args.host, "mode": args.mode,
            "cli_versions": cli_versions,
            "setup": setup_records, "results": results,
        }
        (args.output / "summary.json").write_text(json.dumps(evidence, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
        print(json.dumps({"status": overall, "cases": len(results), "evidence": str(args.output / 'summary.json')}, ensure_ascii=False))
        return 0 if overall == "passed" else (2 if overall == "blocked" else 1)
    finally:
        shutil.rmtree(work, ignore_errors=True)


if __name__ == "__main__":
    raise SystemExit(main())
