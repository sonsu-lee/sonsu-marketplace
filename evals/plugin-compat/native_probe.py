#!/usr/bin/env python3
"""Model-free native Codex and OMP loader probe for the thin catalog."""

from __future__ import annotations

import argparse
import json
import os
from pathlib import Path
import queue
import shutil
import subprocess
import sys
import threading
import tempfile
import time
from typing import Any


ROOT = Path(__file__).resolve().parents[2]
CATALOG = ROOT / ".agents/plugins/marketplace.json"
EXPECTED = [
    "code-review", "code-intelligence", "workflow", "developer-writing", "prompting",
    "product", "figma-workflow", "interface-design", "operations-ui", "design-patterns",
]
EXPECTED_SKILLS = {
    "code-review:review-pr", "code-review:review-failure-modes",
    "code-review:review-maintainability", "code-review:review-operability",
    "code-review:review-overengineering", "code-review:audit-overengineering",
    "code-intelligence:semantic-code-intelligence",
    "workflow:inspect-prs", "workflow:repair-pr", "workflow:to-ticket",
    "workflow:ticket-lifecycle", "workflow:to-pr",
    "developer-writing:write-developer-blog", "prompting:prompt-builder",
    "product:product-discovery", "product:synthesize-product-evidence",
    "product:product-domain-discovery", "product:design-product-test",
    "product:assess-product-test", "product:to-prd",
    "figma-workflow:figma-product-design", "figma-workflow:figma-prototype-flow",
    "figma-workflow:figma-design-audit", "interface-design:design-interface",
    "interface-design:redesign-interface", "operations-ui:design-operations-ui",
    "operations-ui:redesign-operations-ui", "operations-ui:audit-operations-ui",
    "operations-ui:figma-operations-flow", "design-patterns:select-design-patterns",
    "design-patterns:review-pattern-usage",
}
SECRET_NAMES = {
    "OPENAI_API_KEY", "ANTHROPIC_API_KEY", "ANTHROPIC_OAUTH_TOKEN", "GEMINI_API_KEY",
    "GITHUB_TOKEN", "GH_TOKEN", "PERPLEXITY_API_KEY", "EXA_API_KEY",
}


class ProbeFailure(RuntimeError):
    pass


def run(command: list[str], *, cwd: Path, env: dict[str, str], timeout: int = 60) -> dict[str, Any]:
    completed = subprocess.run(command, cwd=cwd, env=env, text=True, capture_output=True, timeout=timeout)
    record = {
        "command": command,
        "returncode": completed.returncode,
        "stdout": completed.stdout,
        "stderr": completed.stderr,
    }
    if completed.returncode != 0:
        raise ProbeFailure(f"command failed ({completed.returncode}): {' '.join(command)}\n{completed.stderr}")
    return record


def scrubbed_env(home: Path) -> dict[str, str]:
    env = os.environ.copy()
    for name in SECRET_NAMES:
        env.pop(name, None)
    env.pop("PI_CODING_AGENT_DIR", None)
    env["HOME"] = str(home)
    return env


class RpcClient:
    def __init__(self, command: list[str], *, cwd: Path, env: dict[str, str]):
        self.process = subprocess.Popen(
            command, cwd=cwd, env=env, text=True, bufsize=1,
            stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.PIPE,
        )
        self.next_id = 1
        self.notifications: list[dict[str, Any]] = []
        self.messages: queue.Queue[dict[str, Any] | Exception | None] = queue.Queue()
        self.reader = threading.Thread(target=self._read_stdout, daemon=True)
        self.reader.start()

    def _read_stdout(self) -> None:
        assert self.process.stdout is not None
        try:
            for line in self.process.stdout:
                try:
                    self.messages.put(json.loads(line))
                except json.JSONDecodeError as error:
                    self.messages.put(error)
                    return
        finally:
            self.messages.put(None)

    def request(self, method: str, params: dict[str, Any], timeout: float = 20) -> dict[str, Any]:
        request_id = self.next_id
        self.next_id += 1
        assert self.process.stdin is not None
        payload = {"jsonrpc": "2.0", "id": request_id, "method": method, "params": params}
        self.process.stdin.write(json.dumps(payload) + "\n")
        self.process.stdin.flush()
        deadline = time.monotonic() + timeout
        while time.monotonic() < deadline:
            remaining = deadline - time.monotonic()
            try:
                message = self.messages.get(timeout=min(0.2, remaining))
            except queue.Empty:
                if self.process.poll() is not None:
                    break
                continue
            if message is None:
                break
            if isinstance(message, Exception):
                raise ProbeFailure(f"{method}: invalid JSON response: {message}")
            if message.get("id") == request_id:
                if "error" in message:
                    raise ProbeFailure(f"{method}: {message['error']}")
                return message["result"]
            self.notifications.append(message)
        stderr = ""
        if self.process.poll() is not None and self.process.stderr is not None:
            stderr = self.process.stderr.read()
        raise ProbeFailure(f"timeout waiting for {method}; stderr={stderr}")

    def close(self) -> str:
        if self.process.poll() is None:
            self.process.terminate()
            try:
                self.process.wait(timeout=5)
            except subprocess.TimeoutExpired:
                self.process.kill()
                self.process.wait(timeout=5)
        self.reader.join(timeout=1)
        assert self.process.stdin is not None
        assert self.process.stdout is not None
        assert self.process.stderr is not None
        stderr = self.process.stderr.read()
        self.process.stdin.close()
        self.process.stdout.close()
        self.process.stderr.close()
        return stderr


def make_fake_mcpls(directory: Path, log_path: Path) -> Path:
    executable = directory / "mcpls"
    executable.write_text(
        """#!/usr/bin/env python3
import json, os, sys
if '--version' in sys.argv:
    print('mcpls 0.6.0')
    raise SystemExit(0)
log = __LOG_PATH__
stream = sys.stdin.buffer
while True:
    first = stream.readline()
    if not first:
        break
    framed = first.lower().startswith(b'content-length:')
    if framed:
        length = int(first.split(b':', 1)[1].strip())
        while stream.readline().strip():
            pass
        payload = stream.read(length)
    else:
        payload = first.strip()
    if not payload:
        continue
    if log:
        with open(log, 'a', encoding='utf-8') as handle:
            handle.write(json.dumps({'framed': framed, 'payload': payload.decode(errors='replace')}) + '\\n')
    message = json.loads(payload)
    if log:
        with open(log, 'a', encoding='utf-8') as handle:
            handle.write(json.dumps({'method': message.get('method')}) + '\\n')
    if 'id' not in message:
        continue
    method = message.get('method')
    if method == 'initialize':
        result = {'protocolVersion': message.get('params', {}).get('protocolVersion', '2025-06-18'), 'capabilities': {'tools': {}}, 'serverInfo': {'name': 'mcpls', 'version': '0.6.0'}}
    elif method == 'tools/list':
        result = {'tools': [
            {'name': 'lsp_get_definition', 'description': 'probe semantic definition tool', 'inputSchema': {'type': 'object', 'properties': {}}},
            {'name': 'lsp_get_references', 'description': 'probe semantic references tool', 'inputSchema': {'type': 'object', 'properties': {}}},
        ]}
    elif method in {'resources/list', 'prompts/list'}:
        result = {method.split('/')[0]: []}
    else:
        result = {}
    response = json.dumps({'jsonrpc': '2.0', 'id': message['id'], 'result': result}).encode()
    if framed:
        sys.stdout.buffer.write(f'Content-Length: {len(response)}\\r\\n\\r\\n'.encode() + response)
        sys.stdout.buffer.flush()
    else:
        print(response.decode(), flush=True)
""".replace("__LOG_PATH__", repr(str(log_path))),
        encoding="utf-8",
    )
    executable.chmod(0o755)
    return executable


def codex_probe(work: Path) -> dict[str, Any]:
    home = work / "codex-home"
    codex_home = home / ".codex"
    fake_bin = work / "fake-bin"
    fake_bin.mkdir(parents=True)
    fake_log = work / "fake-mcpls.jsonl"
    make_fake_mcpls(fake_bin, fake_log)
    env = scrubbed_env(home)
    env["CODEX_HOME"] = str(codex_home)
    env["PATH"] = str(fake_bin) + os.pathsep + env.get("PATH", "")
    env["FAKE_MCPLS_LOG"] = str(fake_log)
    codex_home.mkdir(parents=True)
    source_codex_home = Path(os.environ.get("CODEX_HOME", Path.home() / ".codex"))
    source_auth = source_codex_home / "auth.json"
    if source_auth.is_file():
        destination_auth = codex_home / "auth.json"
        shutil.copy2(source_auth, destination_auth)
        destination_auth.chmod(0o400)
    registration = run(["codex", "plugin", "marketplace", "add", str(ROOT)], cwd=ROOT, env=env)
    client = RpcClient(
        [
            "codex", "app-server", "--stdio",
            "-c", "shell_environment_policy.inherit=all",
        ],
        cwd=ROOT,
        env=env,
    )
    try:
        initialized = client.request("initialize", {
            "clientInfo": {"name": "sonsu-native-probe", "version": "1.0.0"},
            "capabilities": {"experimentalApi": True},
        })
        listed = client.request("plugin/list", {
            "cwds": [str(ROOT)], "marketplaceKinds": ["local"], "forceRefetch": True,
        })
        marketplace = next((item for item in listed["marketplaces"] if item["name"] == "sonsu-marketplace"), None)
        if marketplace is None:
            raise ProbeFailure("Codex did not discover sonsu-marketplace")
        names = [item["name"] for item in marketplace["plugins"]]
        if names != EXPECTED:
            raise ProbeFailure(f"Codex inventory mismatch: {names}")
        details = {}
        installs = {}
        for name in EXPECTED:
            details[name] = client.request("plugin/read", {
                "pluginName": name, "marketplacePath": str(CATALOG),
            })["plugin"]
            installs[name] = client.request("plugin/install", {
                "pluginName": name, "marketplacePath": str(CATALOG),
                "installAttemptId": f"native-probe-{name}",
            })
        skills_response = client.request("skills/list", {"cwds": [str(ROOT)], "forceReload": True})
        skill_bucket = skills_response["data"][0]
        loaded = {
            item["name"] for item in skill_bucket["skills"]
            if (item.get("pluginId") or "").endswith("@sonsu-marketplace")
        }
        if loaded != EXPECTED_SKILLS:
            raise ProbeFailure(f"Codex skill mismatch: missing={sorted(EXPECTED_SKILLS-loaded)} extra={sorted(loaded-EXPECTED_SKILLS)}")
        if skill_bucket.get("errors"):
            raise ProbeFailure(f"Codex skill loader errors: {skill_bucket['errors']}")
        hooks_response = client.request("hooks/list", {"cwds": [str(ROOT)]})
        hook_bucket = hooks_response["data"][0]
        if hook_bucket["hooks"] or hook_bucket.get("errors"):
            raise ProbeFailure(f"unexpected marketplace hooks/errors: {hook_bucket}")
        figma = client.request("plugin/read", {
            "pluginName": "figma-workflow", "marketplacePath": str(CATALOG),
        })["plugin"]
        intelligence = client.request("plugin/read", {
            "pluginName": "code-intelligence", "marketplacePath": str(CATALOG),
        })["plugin"]
        if intelligence.get("mcpServers") != ["mcpls"]:
            raise ProbeFailure(f"Codex mcpls declaration missing: {intelligence.get('mcpServers')}")
        mcp_status = client.request("mcpServerStatus/list", {"detail": "full"}, timeout=30)
        all_mcp_status = mcp_status.get("data", [])
        mcpls_status = [
            item for item in all_mcp_status
            if item.get("name") == "mcpls"
            and item.get("pluginId") == "code-intelligence@sonsu-marketplace"
        ]
        if len(mcpls_status) != 1:
            raise ProbeFailure(f"plugin-owned Codex mcpls status missing or ambiguous: {all_mcp_status}")

        mcp_config = json.loads(
            (ROOT / "plugins/code-intelligence/codex-mcp.json").read_text(encoding="utf-8")
        )["mcpServers"]["mcpls"]
        expected_args = ["${PLUGIN_ROOT}/scripts/launch-mcpls.py"]
        if mcp_config.get("command") != "python3" or mcp_config.get("args") != expected_args:
            raise ProbeFailure(f"unexpected plugin-owned mcpls command wiring: {mcp_config}")

        launcher = RpcClient(
            ["python3", str(ROOT / "plugins/code-intelligence/scripts/launch-mcpls.py")],
            cwd=ROOT,
            env=env,
        )
        try:
            launcher_initialize = launcher.request("initialize", {
                "protocolVersion": "2025-06-18",
                "capabilities": {},
                "clientInfo": {"name": "sonsu-launcher-probe", "version": "1.0.0"},
            })
            launcher_tools = launcher.request("tools/list", {})
        finally:
            launcher_stderr = launcher.close()
            (work / "mcpls-launcher.stderr").write_text(launcher_stderr, encoding="utf-8")
        tool_names = {tool["name"] for tool in launcher_tools.get("tools", [])}
        expected_tools = {"lsp_get_definition", "lsp_get_references"}
        if not expected_tools.issubset(tool_names):
            raise ProbeFailure(f"launcher did not expose expected mcpls tools: {launcher_tools}")
        fake_events = [
            json.loads(line)
            for line in fake_log.read_text(encoding="utf-8").splitlines()
        ] if fake_log.exists() else []
        if not {"initialize", "tools/list"}.issubset({event.get("method") for event in fake_events}):
            raise ProbeFailure(f"fake mcpls did not observe initialize and tools/list: {fake_events}")
        figma_declared = bool(figma.get("apps") or figma.get("appTemplates"))
        if not figma_declared:
            raise ProbeFailure("Codex plugin/read did not expose Figma apps metadata (authentication may be required)")
        return {
            "status": "passed", "initialize": initialized, "registration": registration,
            "plugin_names": names, "skill_names": sorted(loaded), "loader_errors": [],
            "hooks": hook_bucket["hooks"], "figma_apps": figma.get("apps"),
            "figma_app_templates": figma.get("appTemplates"),
            "code_intelligence_mcp_servers": intelligence.get("mcpServers"),
            "mcp_status": mcpls_status, "launcher_initialize": launcher_initialize,
            "launcher_tools": launcher_tools, "fake_mcpls_events": fake_events,
            "notification_methods": sorted({item.get("method") for item in client.notifications if item.get("method")}),
        }
    finally:
        stderr = client.close()
        (work / "codex-app-server.stderr").write_text(stderr, encoding="utf-8")


def omp_probe(work: Path) -> dict[str, Any]:
    home = work / "omp-home"
    home.mkdir()
    env = scrubbed_env(home)
    records = []
    records.append(run(["omp", "plugin", "marketplace", "add", str(ROOT)], cwd=ROOT, env=env))
    discovery = run(["omp", "plugin", "discover", "sonsu-marketplace"], cwd=ROOT, env=env)
    records.append(discovery)
    discovered = [line.strip().split("@", 1)[0] for line in discovery["stdout"].splitlines() if line.startswith("  ") and "@1.0.0" in line]
    if discovered != EXPECTED:
        raise ProbeFailure(f"OMP inventory mismatch: {discovered}")
    for name in EXPECTED:
        records.append(run([
            "omp", "plugin", "install", "--scope", "user", f"{name}@sonsu-marketplace",
        ], cwd=ROOT, env=env))
    listing = run(["omp", "plugin", "list", "--json"], cwd=ROOT, env=env)
    records.append(listing)
    installed = json.loads(listing["stdout"])["marketplace"]
    installed_names = [entry["id"].split("@", 1)[0] for entry in installed]
    if installed_names != EXPECTED:
        raise ProbeFailure(f"OMP installed inventory mismatch: {installed_names}")
    skill_names = set()
    code_intelligence_root = None
    for entry in installed:
        install_path = Path(entry["entries"][0]["installPath"])
        if entry["id"].startswith("code-intelligence@"):
            code_intelligence_root = install_path
        for skill in (install_path / "skills").glob("*/SKILL.md"):
            skill_names.add(skill.parent.name)
    expected_bare = {name.split(":", 1)[1] for name in EXPECTED_SKILLS}
    if skill_names != expected_bare:
        raise ProbeFailure(f"OMP skill mismatch: missing={sorted(expected_bare-skill_names)} extra={sorted(skill_names-expected_bare)}")
    assert code_intelligence_root is not None
    manifest = json.loads((code_intelligence_root / ".codex-plugin/plugin.json").read_text(encoding="utf-8"))
    catalog_entry = next(item for item in json.loads((ROOT / ".omp-plugin/marketplace.json").read_text())["plugins"] if item["name"] == "code-intelligence")
    if any(key in catalog_entry for key in ("mcp", "mcpServers", "lsp", "lspServers")):
        raise ProbeFailure("OMP code-intelligence catalog entry contains MCP/LSP metadata")
    help_record = run(["omp", "--help"], cwd=ROOT, env=env)
    if "lsp" not in help_record["stdout"] or "--no-lsp" not in help_record["stdout"]:
        raise ProbeFailure("OMP native lsp capability not advertised")
    return {
        "status": "passed", "discovered_plugins": discovered,
        "installed_plugins": installed_names, "skill_names": sorted(skill_names),
        "code_intelligence_catalog": catalog_entry,
        "codex_manifest_mcp_ignored_by_catalog": manifest.get("mcpServers") == "./codex-mcp.json",
        "native_lsp_advertised": True, "commands": records,
    }


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output", required=True, type=Path)
    args = parser.parse_args()
    args.output.mkdir(parents=True, exist_ok=True)
    work = Path(tempfile.mkdtemp(prefix="sonsu-native-probe-"))
    summary: dict[str, Any] = {"status": "failed", "root": str(ROOT)}
    try:
        codex = codex_probe(work)
        omp = omp_probe(work)
        summary.update({"status": "passed", "codex": codex, "omp": omp})
        return_code = 0
    except (ProbeFailure, subprocess.TimeoutExpired, OSError, KeyError, ValueError, TypeError, AttributeError) as error:
        summary.update({"status": "failed", "error": str(error)})
        return_code = 1
    finally:
        (args.output / "summary.json").write_text(json.dumps(summary, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
        for artifact in work.iterdir():
            if artifact.is_file():
                shutil.copy2(artifact, args.output / artifact.name)
        shutil.rmtree(work, ignore_errors=True)
    print(json.dumps({"status": summary["status"], "evidence": str(args.output / "summary.json"), "error": summary.get("error")}, ensure_ascii=False))
    return return_code


if __name__ == "__main__":
    raise SystemExit(main())
