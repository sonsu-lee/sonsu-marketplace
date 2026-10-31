"""Codex adapter: runs tasks, detects skill loads, and makes tool-less calls."""

from __future__ import annotations

import json
import os
import queue
import shutil
import subprocess
import sys
import tempfile
import threading
import time
from pathlib import Path
from typing import Optional

from scripts.clients.base import (
    ERROR, NOT_TRIGGERED, TRIGGERED, Arm, RunResult, Settings, check_prompt,
    client_env, copy_skill, name_matches, stream, truncate,
)
from scripts.utils import parse_skill_md

REQUEST_TIMEOUT = 90
COUNTED_ITEMS = {"file_change", "mcp_tool_call", "web_search", "collab_tool_call"}


def base_command(settings: Settings, workdir: Path) -> list:
    return ["codex", "--no-daemon", "exec", "--json", "--skip-git-repo-check",
            "-C", str(workdir), "-c", 'approval_policy="never"',
            "-c", "features.apps=false", "-c", "features.browser_use=false",
            "-c", "features.computer_use=false", "-m", settings.model,
            "-c", f'model_reasoning_effort="{settings.effort}"']


def _command_text(command) -> str:
    return " ".join(str(part) for part in command) if isinstance(command, list) else str(command or "")


def rollout_context(codex_home: Path, thread_id: Optional[str]) -> dict:
    """Return the last turn_context payload of a thread's rollout, if recorded."""
    if not thread_id:
        return {}
    sessions = Path(codex_home) / "sessions"
    rollout = next(sessions.rglob(f"*{thread_id}.jsonl"), None) if sessions.is_dir() else None
    if rollout is None:
        return {}
    context: dict = {}
    for line in rollout.read_text(encoding="utf-8", errors="replace").splitlines():
        try:
            item = json.loads(line)
        except json.JSONDecodeError:
            continue
        if isinstance(item, dict) and item.get("type") == "turn_context":
            context = item.get("payload") or {}
    return context


def parse_run(lines: list, codex_home: Path) -> RunResult:
    """Turn Codex JSON events into a run result and a readable transcript."""
    result = RunResult(raw_lines=list(lines))
    sections: list = []
    thread_id = None
    completed = False
    for line in lines:
        try:
            event = json.loads(line)
        except json.JSONDecodeError:
            continue
        if not isinstance(event, dict):
            continue
        kind = event.get("type")
        if kind == "thread.started":
            thread_id = event.get("thread_id")
        elif kind == "turn.completed":
            completed = True
            usage = event.get("usage") or {}
            result.total_tokens += int(usage.get("input_tokens") or 0) + int(usage.get("output_tokens") or 0)
        elif kind == "turn.failed":
            result.error = str((event.get("error") or {}).get("message") or "turn failed")
        elif kind == "error":
            result.error = str(event.get("message") or (event.get("error") or {}).get("message") or "error")
        elif kind == "item.completed":
            item = event.get("item") or {}
            typ = item.get("type")
            if typ == "agent_message":
                text = str(item.get("text") or "")
                sections.append(f"### Assistant\n\n{text}")
                result.final_text = text
            elif typ == "reasoning":
                sections.append(f"### Reasoning\n\n{truncate(str(item.get('text') or ''), 2000)}")
            elif typ == "command_execution":
                result.tool_calls["command_execution"] = result.tool_calls.get("command_execution", 0) + 1
                code = item.get("exit_code")
                if (code is not None and code != 0) or item.get("status") == "failed":
                    result.tool_errors += 1
                output = truncate(str(item.get("aggregated_output") or ""), 4000)
                sections.append(f"### Command\n\n````text\n$ {_command_text(item.get('command'))}\n"
                                f"exit code: {code}\n{output}\n````")
            elif typ == "file_change":
                result.tool_calls["file_change"] = result.tool_calls.get("file_change", 0) + 1
                changes = "\n".join(f"- {c.get('kind')}: {c.get('path')}" for c in item.get("changes") or [])
                sections.append(f"### File change\n\n{changes}")
            elif typ in ("mcp_tool_call", "web_search"):
                result.tool_calls[typ] = result.tool_calls.get(typ, 0) + 1
                summary = truncate(json.dumps({k: v for k, v in item.items() if k not in ("id", "result")},
                                              ensure_ascii=False), 2000)
                sections.append(f"### {typ}\n\n````json\n{summary}\n````")
    if not completed and not result.error:
        result.error = "turn did not complete"
    context = rollout_context(codex_home, thread_id)
    result.model = context.get("model")
    result.effort = context.get("effort")
    result.transcript = "\n\n".join(sections)
    return result


class TriggerDetector:
    """Decide from Codex events whether the candidate skill was loaded."""

    def __init__(self, name: str, max_tool_calls: int):
        self.skill_md = f".agents/skills/{name}/SKILL.md"
        self.skill_dir = f".agents/skills/{name}"
        self.max_tool_calls = max_tool_calls
        self.count = 0
        self.seen: set = set()
        self.error: Optional[str] = None

    def feed(self, event: dict) -> Optional[str]:
        kind = event.get("type")
        if kind == "turn.completed":
            return NOT_TRIGGERED
        if kind == "turn.failed":
            self.error = str((event.get("error") or {}).get("message") or "turn failed")
            return ERROR
        if kind == "error":
            self.error = str(event.get("message") or "error")
            return ERROR
        if kind not in ("item.started", "item.completed"):
            return None
        item = event.get("item") or {}
        key = item.get("id")
        if kind == "item.completed" and key in self.seen:
            return None
        self.seen.add(key)
        typ = item.get("type")
        if typ == "command_execution":
            command = _command_text(item.get("command"))
            if self.skill_md in command:
                return TRIGGERED
            if self.skill_dir in command:
                return None
        elif typ not in COUNTED_ITEMS:
            return None
        self.count += 1
        if self.count >= self.max_tool_calls:
            return NOT_TRIGGERED
        return None

    def finish(self, returncode: Optional[int], timed_out: bool) -> str:
        if timed_out:
            return NOT_TRIGGERED if self.count > 0 else ERROR
        if returncode == 0:
            return NOT_TRIGGERED
        return ERROR


class CodexClient:
    name = "codex"

    def codex_home(self, settings: Settings) -> Path:
        return Path(settings.home) / ".codex"

    def env(self, settings: Settings) -> dict:
        return client_env(settings.home, CODEX_HOME=str(self.codex_home(settings)))

    def prepare_arm(self, config: str, source: Optional[Path], tmp: Path,
                    plugin_dir: Optional[Path]) -> Arm:
        # Codex receives the skill only through its path in the brief.
        if config == "without_skill" or source is None:
            return Arm(config, None, None)
        name = parse_skill_md(Path(source))[0] or Path(source).name
        return Arm(config, copy_skill(source, Path(tmp) / config / name), None)

    def run_task(self, brief: str, workdir: Path, outputs_dir: Path, arm: Arm,
                 settings: Settings) -> RunResult:
        check_prompt(brief)
        cmd = base_command(settings, workdir) + [
            "--sandbox", "workspace-write", "--add-dir", str(outputs_dir), brief]
        code, timed_out, _, stderr, lines, duration = stream(
            cmd, self.env(settings), workdir, settings.timeout)
        result = parse_run(lines, self.codex_home(settings))
        result.duration_ms = duration
        if timed_out:
            result.error = f"timed out after {settings.timeout}s"
        elif code != 0 and not result.error:
            result.error = f"codex exited {code}: {stderr.strip()[-500:]}"
        return result

    def place_trigger_skill(self, workdir: Path, skill_dir: Path, name: str,
                            description: str) -> Path:
        target = copy_skill(skill_dir, Path(workdir) / ".agents" / "skills" / name, description)
        return target / "SKILL.md"

    def list_skills(self, cwd: Path, settings: Settings) -> list:
        try:
            child = subprocess.Popen(["codex", "app-server"], env=self.env(settings), cwd=cwd,
                                     stdin=subprocess.PIPE, stdout=subprocess.PIPE,
                                     stderr=subprocess.DEVNULL, text=True)
        except OSError as error:
            raise RuntimeError(str(error)) from None
        lines: queue.Queue = queue.Queue()

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
            while True:
                left = deadline - time.monotonic()
                if left <= 0:
                    break
                try:
                    line = lines.get(timeout=left)
                except queue.Empty:
                    break
                if not line:
                    break
                try:
                    message = json.loads(line)
                except json.JSONDecodeError:
                    continue
                if message.get("id") == request_id:
                    return message
            raise RuntimeError("codex app-server did not answer")

        try:
            send({"id": 1, "method": "initialize",
                  "params": {"clientInfo": {"name": "evaluating-skills", "version": "0.1.0"}}})
            receive(1)
            send({"method": "initialized", "params": {}})
            send({"id": 2, "method": "skills/list",
                  "params": {"cwds": [str(cwd)], "forceReload": True}})
            response = receive(2)
        except (BrokenPipeError, OSError) as error:
            raise RuntimeError(f"codex app-server failed: {error}") from None
        finally:
            child.kill()
            child.wait()
        data = (response.get("result") or {}).get("data")
        if data is None:
            raise RuntimeError(f"skills/list returned no data: {json.dumps(response)[:500]}")
        skills = []
        for entry in data:
            if entry.get("errors"):
                print(f"warning: codex skills/list errors: {json.dumps(entry['errors'])[:500]}",
                      file=sys.stderr)
            for skill in entry.get("skills") or []:
                if skill.get("enabled", True):
                    skills.append((skill.get("name"), skill.get("path")))
        return skills

    def check_trigger_setup(self, workdir: Path, name: str, settings: Settings) -> Optional[str]:
        try:
            listed = self.list_skills(workdir, settings)
        except RuntimeError as error:
            return f"could not list Codex skills: {error}"
        found = [entry for entry in listed if name_matches(str(entry[0]), name)]
        root = os.path.realpath(workdir)
        if (len(found) != 1 or found[0][0] != name or not found[0][1]
                or not os.path.realpath(found[0][1]).startswith(root + os.sep)):
            described = ", ".join(f"{n} ({p})" for n, p in found) or "none"
            return f"expected exactly one Codex skill named {name} under {workdir}, found: {described}"
        return None

    def detect_trigger(self, query: str, workdir: Path, name: str, skill_md: Path,
                       settings: Settings, max_tool_calls: int) -> tuple:
        check_prompt(query)
        detector = TriggerDetector(name, max_tool_calls)
        cmd = base_command(settings, workdir) + ["--sandbox", "read-only", query]
        code, timed_out, decision, stderr, _, _ = stream(
            cmd, self.env(settings), workdir, settings.timeout, detector.feed)
        status = decision or detector.finish(code, timed_out)
        if status != ERROR:
            return status, None
        error = detector.error or stderr.strip()[-500:] or (
            "timed out before any tool call" if timed_out else f"codex exited {code}")
        return status, error

    def complete(self, prompt: str, settings: Settings) -> str:
        check_prompt(prompt)
        workdir = Path(tempfile.mkdtemp(prefix="skill-eval-complete-"))
        cmd = base_command(settings, workdir) + ["--ephemeral", "--sandbox", "read-only", prompt]
        try:
            code, timed_out, _, stderr, lines, _ = stream(cmd, self.env(settings), workdir,
                                                          settings.timeout)
        finally:
            shutil.rmtree(workdir, ignore_errors=True)
        if timed_out:
            raise RuntimeError(f"codex completion timed out after {settings.timeout}s")
        result = parse_run(lines, self.codex_home(settings))
        if result.error or code != 0:
            raise RuntimeError(result.error or f"codex exited {code}: {stderr.strip()[-500:]}")
        if not result.final_text.strip():
            raise RuntimeError("codex returned an empty response")
        return result.final_text
