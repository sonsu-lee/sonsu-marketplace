#!/usr/bin/env python3
"""Check marketplace skills in omp, Codex, and Claude Code without a model.

Every client runs in fresh temporary homes with a minimal environment, so live
settings and credentials are never read. Model requests go to a local receiver
that records and rejects them; a skill passes prompt loading only when its
complete SKILL.md body appears in a recorded request.
"""

from __future__ import annotations

import argparse
import http.server
import json
import os
import re
import queue
import shutil
import subprocess
import sys
import tempfile
import threading
import time
import uuid
from concurrent.futures import ThreadPoolExecutor
from dataclasses import dataclass, field
from pathlib import Path

SKILLS_REF = (
    "git+https://github.com/agentskills/agentskills.git"
    "@69ef37e9424c0a7ea9dd2293b559e43ec8176379#subdirectory=skills-ref"
)
# Codex CLI 0.163.0 truncates a plugin skill's SKILL.md after 8,000 UTF-8 bytes;
# see plugins/skill-workflow/skills/authoring-skills/references/codex.md.
CODEX_SKILL_BYTES = 8000
CLIENTS = ("omp", "codex", "claude")
COMMAND_TIMEOUT = 180
REQUEST_TIMEOUT = 90
PASS_ENV = ("PATH", "LANG", "LC_ALL", "TMPDIR", "USER", "LOGNAME", "SHELL", "TERM")


@dataclass
class Result:
    client: str
    check: str
    ok: bool
    detail: str = ""


@dataclass
class Skill:
    plugin: str
    name: str
    path: Path
    body: str = field(repr=False)


class Receiver:
    """Local model endpoint that records each request and rejects it."""

    def __init__(self) -> None:
        self.bodies: list[str] = []
        self.lock = threading.Lock()
        outer = self

        class Handler(http.server.BaseHTTPRequestHandler):
            def _record(self) -> None:
                length = int(self.headers.get("content-length") or 0)
                raw = self.rfile.read(length) if length else b""
                with outer.lock:
                    outer.bodies.append(raw.decode("utf-8", "replace"))
                self.send_response(400)
                self.send_header("content-type", "application/json")
                self.end_headers()
                self.wfile.write(
                    b'{"type":"error","error":{"type":"invalid_request_error",'
                    b'"message":"model-free check receiver"}}'
                )

            do_POST = _record
            do_GET = _record

            def log_message(self, *args: object) -> None:
                pass

        self.server = http.server.ThreadingHTTPServer(("127.0.0.1", 0), Handler)
        self.port = self.server.server_address[1]
        threading.Thread(target=self.server.serve_forever, daemon=True).start()

    def reset(self) -> None:
        with self.lock:
            self.bodies.clear()

    def contains(self, text: str) -> bool:
        # omp compacts Markdown table padding when injecting a skill, so compare
        # without whitespace; missing or truncated content still fails.
        wanted = squash(text)
        with self.lock:
            bodies = list(self.bodies)
        return any(wanted in squash(s) for body in bodies for s in decoded_strings(body))

    def request_contains(self, marker: str, text: str) -> bool:
        wanted = squash(text)
        with self.lock:
            bodies = list(self.bodies)
        for body in bodies:
            strings = decoded_strings(body)
            if any(marker in s for s in strings) and any(wanted in squash(s) for s in strings):
                return True
        return False

    def count(self) -> int:
        with self.lock:
            return len(self.bodies)

    def close(self) -> None:
        self.server.shutdown()
        self.server.server_close()


def squash(text: str) -> str:
    return re.sub(r"\s+", "", text)


def decoded_strings(body: str) -> list[str]:
    try:
        data = json.loads(body)
    except ValueError:
        return [body]
    out: list[str] = []
    stack = [data]
    while stack:
        item = stack.pop()
        if isinstance(item, str):
            out.append(item)
        elif isinstance(item, dict):
            stack.extend(item.values())
        elif isinstance(item, list):
            stack.extend(item)
    return out


def skill_body(text: str) -> str:
    match = re.match(r"---\n.*?\n---\n", text, re.S)
    return (text[match.end():] if match else text).strip()


def run(cmd: list[str], env: dict[str, str] | None = None, cwd: Path | None = None,
        timeout: int = COMMAND_TIMEOUT) -> subprocess.CompletedProcess[str]:
    try:
        return subprocess.run(cmd, env=env, cwd=cwd, capture_output=True, text=True,
                              timeout=timeout, stdin=subprocess.DEVNULL)
    except subprocess.TimeoutExpired as exc:
        # Captured output on timeout is bytes even with text=True.
        out = exc.stdout or b""
        if isinstance(out, bytes):
            out = out.decode("utf-8", "replace")
        return subprocess.CompletedProcess(cmd, 124, out, f"timed out after {timeout}s")


def tail(proc: subprocess.CompletedProcess[str]) -> str:
    text = (proc.stderr or proc.stdout or "").strip().splitlines()
    return text[-1][:200] if text else f"exit {proc.returncode}"


def base_env(home: Path, **extra: str) -> dict[str, str]:
    env = {key: os.environ[key] for key in PASS_ENV if key in os.environ}
    env["HOME"] = str(home)
    env.update(extra)
    return env


def load_marketplace(root: Path) -> tuple[str, list[str], list[Skill], list[Result]]:
    results: list[Result] = []
    omp = json.loads((root / ".omp-plugin/marketplace.json").read_text())
    codex = json.loads((root / ".agents/plugins/marketplace.json").read_text())
    claude = json.loads((root / ".claude-plugin/marketplace.json").read_text())
    names = [p["name"] for p in omp["plugins"]]
    problems: list[str] = []
    for label, catalog in (("Codex", codex), ("Claude Code", claude)):
        other = [p["name"] for p in catalog["plugins"]]
        if other != names:
            problems.append(f"{label} catalog names or order differ: {other}")
    by_name = {
        "codex": {p["name"]: p for p in codex["plugins"]},
        "claude": {p["name"]: p for p in claude["plugins"]},
    }
    skills: list[Skill] = []
    for entry in omp["plugins"]:
        name = entry["name"]
        source = entry["source"]
        package = (root / source).resolve()
        if not (package / "plugin.json").is_file():
            problems.append(f"{name}: {source} has no plugin.json")
            continue
        manifest = json.loads((package / "plugin.json").read_text())
        if manifest.get("name") != name or package.name != name:
            problems.append(f"{name}: directory or plugin.json name differs")
        codex_entry = by_name["codex"].get(name, {})
        claude_entry = by_name["claude"].get(name, {})
        codex_source = codex_entry.get("source")
        if not isinstance(codex_source, dict) or codex_source.get("path") != source:
            problems.append(f"{name}: Codex source differs")
        if claude_entry.get("source") != source:
            problems.append(f"{name}: Claude Code source differs")
        claude_manifest = package / ".claude-plugin/plugin.json"
        claude_version = (json.loads(claude_manifest.read_text()).get("version")
                          if claude_manifest.is_file() else claude_entry.get("version"))
        versions = {manifest.get("version"), entry.get("version"), claude_version}
        if None in versions:
            problems.append(f"{name}: a required version is missing")
        elif len(versions) != 1:
            problems.append(f"{name}: versions differ {sorted(map(str, versions))}")
        for skill_md in sorted(package.glob("skills/*/SKILL.md")):
            skills.append(Skill(name, skill_md.parent.name, skill_md,
                                skill_body(skill_md.read_text(encoding="utf-8"))))
    results.append(Result("-", "catalogs", not problems, "; ".join(problems)))
    return omp["name"], names, skills, results


def check_format(skills: list[Skill]) -> list[Result]:
    if not shutil.which("uvx"):
        return [Result("-", "format", False, "uvx not found on PATH")]
    failed = []
    for skill in skills:
        proc = run(["uvx", "--from", SKILLS_REF, "skills-ref", "validate",
                    str(skill.path.parent)], timeout=300)
        if proc.returncode != 0:
            failed.append(f"{skill.plugin}:{skill.name}: {tail(proc)}")
    return [Result("-", "format", not failed, "; ".join(failed))]


def check_codex_size(skills: list[Skill]) -> Result:
    over = [f"{s.plugin}:{s.name} {s.path.stat().st_size} bytes"
            for s in skills if s.path.stat().st_size > CODEX_SKILL_BYTES]
    return Result("codex", "size", not over,
                  "; ".join(over) + (f" (limit {CODEX_SKILL_BYTES})" if over else ""))


def expect_once(found: list[str], wanted: list[str]) -> str:
    problems = []
    for name in wanted:
        hits = found.count(name)
        if hits != 1:
            problems.append(f"{name} found {hits}x")
    return "; ".join(problems)


def install_omp(root: Path, market: str, plugins: list[str], home: Path,
                target: Path) -> tuple[dict[str, str], list[str]]:
    (home / ".omp/agent").mkdir(parents=True, exist_ok=True)
    target.mkdir(parents=True, exist_ok=True)
    env = base_env(home)
    # Run every omp command from the temporary target: omp also discovers
    # project skills by walking up from the working directory.
    proc = run(["omp", "plugin", "marketplace", "add", str(root)], env, target)
    failures = [] if proc.returncode == 0 else [f"marketplace add: {tail(proc)}"]
    for plugin in plugins:
        proc = run(["omp", "plugin", "install", f"{plugin}@{market}"], env, target)
        if proc.returncode != 0:
            failures.append(f"{plugin}: {tail(proc)}")
    return env, failures


def install_codex(root: Path, market: str, plugins: list[str], home: Path,
                  target: Path) -> tuple[dict[str, str], list[str]]:
    codex_home = home / ".codex"
    codex_home.mkdir(parents=True, exist_ok=True)
    target.mkdir(parents=True, exist_ok=True)
    env = base_env(home, CODEX_HOME=str(codex_home))
    proc = run(["codex", "plugin", "marketplace", "add", str(root), "--json"], env, target)
    failures = [] if proc.returncode == 0 else [f"marketplace add: {tail(proc)}"]
    for plugin in plugins:
        proc = run(["codex", "plugin", "add", f"{plugin}@{market}", "--json"], env, target)
        if proc.returncode != 0:
            failures.append(f"{plugin}: {tail(proc)}")
    proc = run(["codex", "plugin", "list", "--marketplace", market, "--json"], env, target)
    try:
        installed = {p["name"]: p for p in json.loads(proc.stdout)["installed"]}
    except (ValueError, KeyError):
        installed = {}
        failures.append(f"plugin list: {tail(proc)}")
    for plugin in plugins:
        entry = installed.get(plugin)
        if not entry or not entry.get("installed") or not entry.get("enabled"):
            failures.append(f"{plugin} not installed and enabled")
    return env, failures


def install_claude(root: Path, market: str, plugins: list[str], home: Path,
                   target: Path) -> tuple[dict[str, str], list[str]]:
    config_dir = home / ".claude"
    config_dir.mkdir(parents=True, exist_ok=True)
    target.mkdir(parents=True, exist_ok=True)
    env = base_env(home, CLAUDE_CONFIG_DIR=str(config_dir))
    proc = run(["claude", "plugin", "marketplace", "add", str(root)], env, target)
    failures = [] if proc.returncode == 0 else [f"marketplace add: {tail(proc)}"]
    for plugin in plugins:
        proc = run(["claude", "plugin", "install", f"{plugin}@{market}"], env, target)
        if proc.returncode != 0:
            failures.append(f"{plugin}: {tail(proc)}")
    return env, failures


def check_omp(root: Path, market: str, plugins: list[str], skills: list[Skill],
              tmp: Path) -> list[Result]:
    target = tmp / "omp-target"
    agent_dir = tmp / "omp-home/.omp/agent"
    env, failures = install_omp(root, market, plugins, tmp / "omp-home", target)
    results = [Result("omp", "install", not failures, "; ".join(failures))]
    proc = run(["omp", "skill", "list"], env, target)
    text = proc.stdout + proc.stderr
    warnings = [line.strip() for line in text.splitlines() if "warning:" in line]
    # Each listing line starts with the skill name; warnings mention names too.
    listed = [line.split(None, 1)[0] for line in text.splitlines()
              if line.strip() and "warning:" not in line]
    names = [s.name for s in skills]
    problem = "; ".join(filter(None, [expect_once([n for n in listed if n in names], names),
                                      "; ".join(warnings)]))
    results.append(Result("omp", "discovery", proc.returncode == 0 and not problem,
                          problem or ("" if proc.returncode == 0 else tail(proc))))

    receiver = Receiver()
    try:
        (agent_dir / "models.yml").write_text(
            "providers:\n  check:\n"
            f"    baseUrl: http://127.0.0.1:{receiver.port}/v1\n"
            "    api: openai-completions\n    auth: none\n    models:\n"
            "      - id: check-model\n        name: check-model\n"
            "        contextWindow: 200000\n        maxTokens: 8000\n")
        (agent_dir / "config.yml").write_text("skills:\n  enableSkillCommands: true\n")
        missing = []
        for skill in skills:
            receiver.reset()
            marker = f"check-{uuid.uuid4().hex}"
            prompt = json.dumps({"id": "check", "type": "prompt",
                                 "message": f"/skill:{skill.name} {marker}"})
            child = subprocess.Popen(
                ["omp", "--mode", "rpc", "--no-session", "--model", "check/check-model"],
                env=env, cwd=target, stdin=subprocess.PIPE,
                stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL, text=True)
            try:
                child.stdin.write(prompt + "\n")
                child.stdin.flush()
                deadline = time.monotonic() + REQUEST_TIMEOUT
                while not receiver.contains(marker) and time.monotonic() < deadline:
                    if child.poll() is not None:
                        break
                    time.sleep(0.2)
            finally:
                child.kill()
                child.wait()
            if not receiver.request_contains(marker, skill.body):
                missing.append(f"{skill.name}"
                               + ("" if receiver.contains(marker) else " (no invocation request)"))
        results.append(Result("omp", "loading", not missing,
                              "incomplete body: " + ", ".join(missing) if missing else ""))
    finally:
        receiver.close()
    return results


def codex_skills_list(env: dict[str, str], target: Path) -> dict:
    child = subprocess.Popen(["codex", "app-server"], env=env, cwd=target,
                             stdin=subprocess.PIPE, stdout=subprocess.PIPE,
                             stderr=subprocess.DEVNULL, text=True)
    lines: queue.Queue[str] = queue.Queue()

    def pump() -> None:
        for line in child.stdout:
            lines.put(line)
        lines.put("")

    threading.Thread(target=pump, daemon=True).start()

    def send(message: dict) -> None:
        child.stdin.write(json.dumps(message) + "\n")
        child.stdin.flush()

    def receive(request_id: int) -> dict:
        deadline = time.monotonic() + REQUEST_TIMEOUT
        while (left := deadline - time.monotonic()) > 0:
            try:
                line = lines.get(timeout=left)
            except queue.Empty:
                break
            if not line:
                break
            message = json.loads(line)
            if message.get("id") == request_id:
                return message
        raise TimeoutError("codex app-server did not answer")

    try:
        send({"id": 1, "method": "initialize",
              "params": {"clientInfo": {"name": "check_plugins", "version": "0.1.0"}}})
        receive(1)
        send({"method": "initialized", "params": {}})
        send({"id": 2, "method": "skills/list",
              "params": {"cwds": [str(target)], "forceReload": True}})
        return receive(2)
    finally:
        child.kill()
        child.wait()


def check_codex(root: Path, market: str, plugins: list[str], skills: list[Skill],
                tmp: Path) -> list[Result]:
    codex_home = tmp / "codex-home/.codex"
    target = tmp / "codex-target"
    env, failures = install_codex(root, market, plugins, tmp / "codex-home", target)
    results = [Result("codex", "install", not failures, "; ".join(failures))]

    try:
        listing = codex_skills_list(env, target)
        data = listing["result"]["data"]
        errors = [str(e) for entry in data for e in entry.get("errors", [])]
        found = [s["name"] for entry in data for s in entry.get("skills", [])
                 if str(codex_home) in (s.get("path") or "") and s.get("enabled")]
        problem = "; ".join(filter(None, [
            expect_once(found, [f"{s.plugin}:{s.name}" for s in skills]),
            "; ".join(errors)]))
    except (TimeoutError, KeyError, ValueError) as exc:
        problem = f"skills/list failed: {exc}"
    results.append(Result("codex", "discovery", not problem, problem))

    receiver = Receiver()
    try:
        config = codex_home / "config.toml"
        existing = config.read_text() if config.exists() else ""
        # Top-level keys must precede every table, or TOML assigns them to it.
        config.write_text(
            'model = "check-model"\nmodel_provider = "check"\n\n' + existing
            + '\n[model_providers.check]\nname = "check"\n'
            f'base_url = "http://127.0.0.1:{receiver.port}/v1"\n'
            'wire_api = "responses"\nenv_key = "CHECK_KEY"\n'
            "request_max_retries = 0\nstream_max_retries = 0\n")
        run_env = dict(env, CHECK_KEY="placeholder")
        missing = []
        for skill in skills:
            receiver.reset()
            proc = run(["codex", "--no-daemon", "exec", "--json", "--skip-git-repo-check",
                        "--sandbox", "read-only", "-c", "features.apps=false",
                        f"${skill.plugin}:{skill.name} check"],
                       run_env, target, timeout=REQUEST_TIMEOUT)
            truncated = "exceeded the main prompt context limit" in proc.stdout
            if truncated or not receiver.contains(skill.body):
                missing.append(f"{skill.plugin}:{skill.name}"
                               + (" (truncated)" if truncated else "")
                               + ("" if receiver.count() else " (no request)"))
        results.append(Result("codex", "loading", not missing,
                              "incomplete body: " + ", ".join(missing) if missing else ""))
    finally:
        receiver.close()
    return results


def check_claude(root: Path, market: str, plugins: list[str], skills: list[Skill],
                 tmp: Path) -> list[Result]:
    target = tmp / "claude-target"
    env, failures = install_claude(root, market, plugins, tmp / "claude-home", target)
    paths = [root] + sorted(p.parent.parent for p in root.glob("plugins/*/.claude-plugin/plugin.json"))
    paths += sorted(p for p in root.glob("plugins/*/skills") if p.is_dir())
    invalid = []
    for path in paths:
        proc = run(["claude", "plugin", "validate", str(path), "--strict"], env, target)
        if proc.returncode != 0:
            invalid.append(f"{path.relative_to(root.parent)}: {tail(proc)}")
    results = [Result("claude", "validate", not invalid, "; ".join(invalid)),
               Result("claude", "install", not failures, "; ".join(failures))]

    receiver = Receiver()
    try:
        run_env = dict(env, ANTHROPIC_BASE_URL=f"http://127.0.0.1:{receiver.port}",
                       ANTHROPIC_API_KEY="placeholder")
        proc = run(["claude", "-p", "--output-format", "stream-json", "--verbose",
                    "List nothing."], run_env, target, timeout=REQUEST_TIMEOUT)
        init = next((json.loads(line) for line in proc.stdout.splitlines()
                     if '"subtype":"init"' in line.replace(" ", "")), None)
        if init is None:
            problem = f"no init event: {tail(proc)}"
        else:
            agent_names = {p.stem for p in root.glob("plugins/*/agents/*.md")}
            leaked = [a for a in init.get("agents", [])
                      if a.split(":")[-1] in agent_names]
            problem = "; ".join(filter(None, [
                expect_once(init.get("skills", []), [f"{s.plugin}:{s.name}" for s in skills]),
                f"marketplace agents loaded: {leaked}" if leaked else ""]))
        results.append(Result("claude", "discovery", not problem, problem))

        missing = []
        for skill in skills:
            receiver.reset()
            run(["claude", "-p", f"/{skill.plugin}:{skill.name} check",
                 "--output-format", "stream-json", "--verbose"],
                run_env, target, timeout=REQUEST_TIMEOUT)
            if not receiver.contains(skill.body):
                missing.append(f"{skill.plugin}:{skill.name}"
                               + ("" if receiver.count() else " (no request)"))
        results.append(Result("claude", "loading", not missing,
                              "incomplete body: " + ", ".join(missing) if missing else ""))
    finally:
        receiver.close()
    return results


CHECKERS = {"omp": check_omp, "codex": check_codex, "claude": check_claude}
CLI = {"omp": "omp", "codex": "codex", "claude": "claude"}


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("--root", type=Path, default=Path(__file__).resolve().parents[1],
                        help="marketplace root to check (default: this repository)")
    parser.add_argument("--clients", default=",".join(CLIENTS),
                        help="comma-separated subset of omp,codex,claude")
    parser.add_argument("--keep-temp", action="store_true",
                        help="keep temporary homes for inspection")
    args = parser.parse_args()
    root = args.root.resolve()
    clients = [c.strip() for c in args.clients.split(",") if c.strip()]
    unknown = [c for c in clients if c not in CLIENTS]
    if unknown or not clients:
        parser.error(f"unknown clients: {', '.join(unknown)}" if unknown
                     else "--clients needs at least one client")

    market, plugins, skills, results = load_marketplace(root)
    results += check_format(skills)
    if "codex" in clients:
        results.append(check_codex_size(skills))

    tmp = Path(tempfile.mkdtemp(prefix="check-plugins-"))
    try:
        jobs = {}
        with ThreadPoolExecutor(max_workers=len(clients) or 1) as pool:
            for client in clients:
                if not shutil.which(CLI[client]):
                    results.append(Result(client, "install", False,
                                          f"{CLI[client]} not found on PATH"))
                    continue
                jobs[client] = pool.submit(CHECKERS[client], root, market, plugins,
                                           skills, tmp)
            for client, job in jobs.items():
                try:
                    results += job.result()
                except Exception as exc:  # report, do not hide, unexpected failures
                    results.append(Result(client, "error", False, repr(exc)))
    finally:
        if args.keep_temp:
            print(f"temporary homes kept in {tmp}")
        else:
            shutil.rmtree(tmp, ignore_errors=True)

    print(f"{len(skills)} skills in {len(plugins)} plugins from {root}")
    for result in results:
        status = "PASS" if result.ok else "FAIL"
        line = f"{status}  {result.client:<7} {result.check:<10}"
        print(line + (f" {result.detail}" if result.detail else ""))
    return 0 if all(r.ok for r in results) else 1


if __name__ == "__main__":
    sys.exit(main())
