"""Codex adapter: run a task, detect a skill load, and make a tool-less call."""

from __future__ import annotations

import json
import os
import shutil
import subprocess
import tempfile
import threading
from pathlib import Path
from typing import Optional

from scripts.clients.base import (
    ERROR, NOT_TRIGGERED, TRIGGERED, Arm, RunResult, Settings, client_env,
    copy_skill, name_matches, stream, truncate,
)
from scripts.utils import parse_skill_md

TOOL_ITEMS = ("command_execution", "file_change", "mcp_tool_call", "web_search")


def base_command(settings: Settings, workdir: Path) -> list:
    # --no-daemon keeps runs off a running Codex daemon; account apps and
    # browser or computer use stay off so only the shell and files are tools.
    return ["codex", "--no-daemon", "exec", "--json", "--skip-git-repo-check",
            "-C", str(workdir), "-c", 'approval_policy="never"',
            "-c", "features.apps=false", "-c", "features.browser_use=false",
            "-c", "features.computer_use=false", "-m", settings.model,
            "-c", f'model_reasoning_effort="{settings.effort}"']


def turn_context(codex_home: Path, thread_id: Optional[str]) -> dict:
    """Return the last turn_context of the thread's session rollout.

    Codex events do not report the model or effort; the rollout does.
    """
    rollout = next((Path(codex_home) / "sessions").rglob(f"*{thread_id}.jsonl"), None)
    if not thread_id or rollout is None:
        return {}
    items = [json.loads(line) for line in rollout.read_text().splitlines() if line]
    contexts = [item["payload"] for item in items if item.get("type") == "turn_context"]
    return contexts[-1] if contexts else {}


def parse_run(lines: list, codex_home: Path) -> RunResult:
    """Turn Codex JSON events into a run result and a readable transcript."""
    result = RunResult(raw_lines=list(lines))
    sections, thread_id, completed = [], None, False
    for line in lines:
        event = json.loads(line) if line.startswith("{") else {}
        kind = event.get("type")
        if kind == "thread.started":
            thread_id = event.get("thread_id")
        elif kind == "turn.completed":
            completed = True
            usage = event.get("usage") or {}
            result.total_tokens += usage.get("input_tokens", 0) + usage.get("output_tokens", 0)
        elif kind == "turn.failed":
            result.error = (event.get("error") or {}).get("message") or "turn failed"
        elif kind == "error":
            result.error = event.get("message") or "error"
        elif kind == "item.completed":
            item = event["item"]
            typ = item.get("type")
            if typ == "agent_message":
                sections.append(f"### Assistant\n\n{item.get('text', '')}")
                result.final_text = item.get("text", "")
            elif typ in TOOL_ITEMS:
                result.tool_calls[typ] = result.tool_calls.get(typ, 0) + 1
                if typ == "command_execution":
                    code = item.get("exit_code")
                    result.tool_errors += code not in (0, None)
                    output = truncate(item.get("aggregated_output") or "", 4000)
                    sections.append(f"### Command\n\n````text\n$ {item.get('command')}\n"
                                    f"exit code: {code}\n{output}\n````")
                else:
                    detail = truncate(json.dumps(item, ensure_ascii=False), 2000)
                    sections.append(f"### {typ}\n\n````json\n{detail}\n````")
    if not completed and result.error is None:
        result.error = "turn did not complete"
    context = turn_context(codex_home, thread_id)
    result.model, result.effort = context.get("model"), context.get("effort")
    result.transcript = "\n\n".join(sections)
    return result


class TriggerDetector:
    """Judge the first tool call, as skill-creator does.

    It is a trigger when that call names the placed .agents/skills/<name> path.
    """

    def __init__(self, name: str):
        self.marker = f".agents/skills/{name}"
        self.error: Optional[str] = None

    def feed(self, event: dict) -> Optional[str]:
        kind = event.get("type")
        item = event.get("item") or {}
        if kind == "item.started" and item.get("type") in TOOL_ITEMS:
            return TRIGGERED if self.marker in json.dumps(item) else NOT_TRIGGERED
        if kind == "turn.completed":
            return NOT_TRIGGERED
        if kind in ("turn.failed", "error"):
            self.error = (event.get("error") or {}).get("message") or event.get("message") or kind
            return ERROR
        return None

    def finish(self, returncode: Optional[int], timed_out: bool) -> str:
        return NOT_TRIGGERED if returncode == 0 and not timed_out else ERROR


class CodexClient:
    name = "codex"

    def codex_home(self, settings: Settings) -> Path:
        return Path(settings.home) / ".codex"

    def env(self, settings: Settings) -> dict:
        return client_env(settings.home, CODEX_HOME=str(self.codex_home(settings)))

    def prepare_arm(self, config: str, source: Optional[Path], tmp: Path,
                    plugin_dir: Optional[Path]) -> Arm:
        """Codex gets the skill only through its path in the brief."""
        if config == "without_skill":
            return Arm(config, None, None)
        name = parse_skill_md(Path(source))[0]
        return Arm(config, copy_skill(source, Path(tmp) / config / name), None)

    def run_task(self, brief: str, workdir: Path, outputs_dir: Path, arm: Arm,
                 settings: Settings) -> RunResult:
        cmd = base_command(settings, workdir) + [
            "--sandbox", "workspace-write", "--add-dir", str(outputs_dir), brief]
        code, timed_out, _, stderr, lines, duration = stream(
            cmd, self.env(settings), workdir, settings.timeout)
        result = parse_run(lines, self.codex_home(settings))
        result.duration_ms = duration
        if timed_out:
            result.error = f"timed out after {settings.timeout}s"
        elif code != 0 and result.error is None:
            result.error = f"codex exited {code}: {stderr.strip()[-500:]}"
        return result

    def place_trigger_skill(self, workdir: Path, skill_dir: Path, name: str,
                            description: str) -> None:
        copy_skill(skill_dir, Path(workdir) / ".agents" / "skills" / name, description)

    def list_skills(self, cwd: Path, settings: Settings) -> list:
        """Ask `codex app-server` which skills it discovers from cwd."""
        requests = [
            {"id": 1, "method": "initialize",
             "params": {"clientInfo": {"name": "evaluating-skills", "version": "0.1.0"}}},
            {"method": "initialized", "params": {}},
            {"id": 2, "method": "skills/list", "params": {"cwds": [str(cwd)], "forceReload": True}},
        ]
        child = subprocess.Popen(["codex", "app-server"], env=self.env(settings), cwd=cwd,
                                 stdin=subprocess.PIPE, stdout=subprocess.PIPE,
                                 stderr=subprocess.DEVNULL, text=True)
        # A server that never answers would otherwise block the run forever.
        timer = threading.Timer(90, child.kill)
        timer.start()
        try:
            child.stdin.write("".join(json.dumps(r) + "\n" for r in requests))
            child.stdin.flush()
            for line in child.stdout:
                message = json.loads(line)
                if message.get("id") == 2:
                    break
            else:
                raise RuntimeError("codex app-server ended without answering skills/list")
        finally:
            timer.cancel()
            child.kill()
            child.wait()
        if "result" not in message:
            raise RuntimeError(json.dumps(message.get("error"))[:500])
        return [(s["name"], s.get("path")) for entry in message["result"]["data"]
                for s in entry.get("skills", []) if s.get("enabled", True)]

    def check_trigger_setup(self, workdir: Path, name: str, settings: Settings) -> Optional[str]:
        found = [(n, p) for n, p in self.list_skills(workdir, settings) if name_matches(n, name)]
        root = os.path.realpath(workdir) + os.sep
        if len(found) != 1 or not os.path.realpath(found[0][1]).startswith(root):
            listed = ", ".join(f"{n} ({p})" for n, p in found) or "none"
            return f"expected one Codex skill named {name} under {workdir}, found: {listed}"
        return None

    def detect_trigger(self, query: str, workdir: Path, name: str,
                       settings: Settings) -> tuple:
        detector = TriggerDetector(name)
        cmd = base_command(settings, workdir) + ["--sandbox", "read-only", query]
        code, timed_out, decision, stderr, _, _ = stream(
            cmd, self.env(settings), workdir, settings.timeout, detector.feed)
        status = decision or detector.finish(code, timed_out)
        if status != ERROR:
            return status, None
        return status, detector.error or stderr.strip()[-500:] or f"codex exited {code}"

    def complete(self, prompt: str, settings: Settings) -> str:
        workdir = Path(tempfile.mkdtemp(prefix="skill-eval-complete-"))
        cmd = base_command(settings, workdir) + ["--ephemeral", "--sandbox", "read-only", prompt]
        try:
            code, timed_out, _, stderr, lines, _ = stream(cmd, self.env(settings), workdir,
                                                          settings.timeout)
        finally:
            shutil.rmtree(workdir, ignore_errors=True)
        result = parse_run(lines, self.codex_home(settings))
        if timed_out or code != 0 or result.error or not result.final_text.strip():
            raise RuntimeError(result.error or f"codex exited {code}: {stderr.strip()[-500:]}")
        return result.final_text
