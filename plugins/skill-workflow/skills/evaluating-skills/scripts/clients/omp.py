"""omp adapter: runs tasks, detects skill loads, and makes tool-less calls."""

from __future__ import annotations

import json
import os
import re
import shutil
import subprocess
import tempfile
from pathlib import Path
from typing import Optional

from scripts.clients.base import (
    ERROR, NOT_TRIGGERED, TRIGGERED, Arm, RunResult, Settings, check_prompt,
    client_env, copy_skill, name_matches, stream, strip_selector, truncate,
)
from scripts.utils import parse_skill_md

LIST_TIMEOUT = 120


def text_content(value) -> str:
    if isinstance(value, str):
        return value
    if isinstance(value, list):
        return "\n".join(text_content(v) for v in value)
    if isinstance(value, dict):
        return text_content(value.get("text", value.get("content", "")))
    return ""


def base_command(settings: Settings, slow: bool = True) -> list:
    cmd = ["omp", "-p", "--mode", "json", "--no-session", "--no-title",
           "--no-context-files", "--no-rules", "--no-extensions",
           "--model", settings.model]
    if slow:
        cmd += ["--slow", settings.model]
    return cmd + ["--thinking", settings.effort]


def _assistant_text(message: dict) -> str:
    return "".join(block.get("text", "") for block in message.get("content") or []
                   if isinstance(block, dict) and block.get("type") == "text")


def parse_run(lines: list) -> RunResult:
    """Turn omp JSON events into a run result and a readable transcript."""
    result = RunResult(raw_lines=list(lines))
    sections: list = []
    names: dict = {}
    assistant_seen = False
    for line in lines:
        try:
            event = json.loads(line)
        except json.JSONDecodeError:
            continue
        if not isinstance(event, dict):
            continue
        kind = event.get("type")
        if kind == "tool_execution_start":
            name = str(event.get("toolName") or "unknown")
            names[event.get("toolCallId")] = name
            result.tool_calls[name] = result.tool_calls.get(name, 0) + 1
            args = truncate(json.dumps(event.get("args") or {}, ensure_ascii=False), 2000)
            sections.append(f"### Tool call: {name}\n\n````json\n{args}\n````")
        elif kind == "tool_execution_end":
            name = names.get(event.get("toolCallId")) or str(event.get("toolName") or "unknown")
            failed = bool(event.get("isError"))
            if failed:
                result.tool_errors += 1
            raw = event.get("result")
            if isinstance(raw, str):
                text = raw
            else:
                text = text_content((raw or {}).get("content") if isinstance(raw, dict) else raw)
                if not text:
                    text = json.dumps(raw, ensure_ascii=False)
            label = f"### Tool result: {name}" + (" (error)" if failed else "")
            sections.append(f"{label}\n\n````text\n{truncate(text, 4000)}\n````")
        elif kind == "message_end":
            message = event.get("message") or {}
            if message.get("role") != "assistant":
                continue
            assistant_seen = True
            usage = message.get("usage") or {}
            total = usage.get("totalTokens")
            if total is None:
                total = sum(int(usage.get(k) or 0) for k in ("input", "output", "cacheRead", "cacheWrite"))
            result.total_tokens += int(total or 0)
            result.model = message.get("model") or result.model
            effort = ((message.get("requestControls") or {}).get("effort") or {}).get("topLevel")
            result.effort = effort or result.effort
            text = _assistant_text(message)
            if text.strip():
                sections.append(f"### Assistant\n\n{text}")
                result.final_text = text
            if message.get("stopReason") == "error":
                result.error = message.get("errorMessage") or "assistant error"
    if not assistant_seen:
        result.error = result.error or "no assistant message"
    result.transcript = "\n\n".join(sections)
    return result


class TriggerDetector:
    """Decide from omp events whether the candidate skill was loaded."""

    def __init__(self, name: str, skill_md: Path, workdir: Path, max_tool_calls: int):
        self.name = name
        self.skill_md = os.path.realpath(skill_md)
        self.workdir = Path(workdir)
        self.max_tool_calls = max_tool_calls
        self.count = 0
        self.error: Optional[str] = None
        self.skill_uri = re.compile(r"^skill://" + re.escape(name) + r"(/SKILL\.md)?(:[^/]*)?/?$")
        self.skill_prefix = f"skill://{name}/"

    def feed(self, event: dict) -> Optional[str]:
        kind = event.get("type")
        if kind == "message_end":
            message = event.get("message") or {}
            if message.get("role") == "assistant" and message.get("stopReason") == "error":
                self.error = message.get("errorMessage") or "assistant error"
                return ERROR
            return None
        if kind != "tool_execution_start":
            return None
        tool = event.get("toolName")
        args = event.get("args") or {}
        if tool == "todo":
            return None
        if tool == "read":
            path = str(args.get("path", ""))
            if self.skill_uri.match(path):
                return TRIGGERED
            if path.startswith(self.skill_prefix):
                return None
            if not path.startswith("skill://"):
                local = Path(strip_selector(path)).expanduser()
                if not local.is_absolute():
                    local = self.workdir / local
                if os.path.realpath(local) == self.skill_md:
                    return TRIGGERED
        elif tool == "bash":
            command = str(args.get("command", ""))
            if f".omp/skills/{self.name}/SKILL.md" in command or f"skill://{self.name}" in command:
                return TRIGGERED
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


def _ignore_plugin(directory: str, names: list) -> set:
    skipped = {"__pycache__"}
    if Path(directory).parent.name == "skills":
        skipped.add("evals")
    return {name for name in names if name in skipped or name.endswith("-workspace")}


class OmpClient:
    name = "omp"

    def env(self, settings: Settings) -> dict:
        return client_env(settings.home)

    def prepare_arm(self, config: str, source: Optional[Path], tmp: Path,
                    plugin_dir: Optional[Path]) -> Arm:
        if source is None:
            return Arm(config, None, None)
        source = Path(source)
        # The snapshot directory is not named after the skill, so read the name.
        name = parse_skill_md(source)[0] or source.name
        if plugin_dir is not None:
            # Every arm loads its own copy of the same plugin, so agents and
            # sibling resources resolve and only the evaluated skill differs:
            # without_skill drops it, the other arms swap in their version.
            plugin_copy = Path(tmp) / config / Path(plugin_dir).name
            shutil.copytree(plugin_dir, plugin_copy, ignore=_ignore_plugin)
            skill_dir = plugin_copy / "skills" / name
            shutil.rmtree(skill_dir, ignore_errors=True)
            if config == "without_skill":
                return Arm(config, None, plugin_copy)
            copy_skill(source, skill_dir)
            return Arm(config, skill_dir, plugin_copy)
        if config == "without_skill":
            return Arm(config, None, None)
        return Arm(config, copy_skill(source, Path(tmp) / config / name), None)

    def run_task(self, brief: str, workdir: Path, outputs_dir: Path, arm: Arm,
                 settings: Settings) -> RunResult:
        check_prompt(brief)
        cmd = base_command(settings) + ["--approval-mode", "yolo"]
        cmd += ["--plugin-dir", str(arm.plugin_dir)] if arm.plugin_dir else ["--no-skills"]
        code, timed_out, _, stderr, lines, duration = stream(
            cmd + [brief], self.env(settings), workdir, settings.timeout)
        result = parse_run(lines)
        result.duration_ms = duration
        if timed_out:
            result.error = f"timed out after {settings.timeout}s"
        elif code != 0 and not result.error:
            result.error = f"omp exited {code}: {stderr.strip()[-500:]}"
        return result

    def place_trigger_skill(self, workdir: Path, skill_dir: Path, name: str,
                            description: str) -> Path:
        target = copy_skill(skill_dir, Path(workdir) / ".omp" / "skills" / name, description)
        return target / "SKILL.md"

    def list_skills(self, cwd: Path, settings: Settings) -> list:
        try:
            proc = subprocess.run(["omp", "skill", "list"], env=self.env(settings), cwd=cwd,
                                  capture_output=True, text=True, timeout=LIST_TIMEOUT,
                                  stdin=subprocess.DEVNULL)
        except (OSError, subprocess.TimeoutExpired) as error:
            raise RuntimeError(str(error)) from None
        if proc.returncode != 0:
            raise RuntimeError((proc.stderr or proc.stdout).strip()[-500:] or f"exit {proc.returncode}")
        text = proc.stdout + proc.stderr
        # Each listing line starts with the skill name; warnings mention names too.
        return [(line.split(None, 1)[0], None) for line in text.splitlines()
                if line.strip() and "warning:" not in line]

    def check_trigger_setup(self, workdir: Path, name: str, settings: Settings) -> Optional[str]:
        try:
            listed = self.list_skills(workdir, settings)
        except RuntimeError as error:
            return f"could not list omp skills: {error}"
        found = [entry[0] for entry in listed if name_matches(entry[0], name)]
        if found != [name]:
            return f"expected exactly one omp skill named {name}, found: {', '.join(found) or 'none'}"
        return None

    def detect_trigger(self, query: str, workdir: Path, name: str, skill_md: Path,
                       settings: Settings, max_tool_calls: int) -> tuple:
        check_prompt(query)
        detector = TriggerDetector(name, skill_md, workdir, max_tool_calls)
        cmd = base_command(settings) + ["--approval-mode", "always-ask", "--skills", name, query]
        code, timed_out, decision, stderr, _, _ = stream(
            cmd, self.env(settings), workdir, settings.timeout, detector.feed)
        status = decision or detector.finish(code, timed_out)
        if status != ERROR:
            return status, None
        error = detector.error or stderr.strip()[-500:] or (
            "timed out before any tool call" if timed_out else f"omp exited {code}")
        return status, error

    def complete(self, prompt: str, settings: Settings) -> str:
        check_prompt(prompt)
        workdir = Path(tempfile.mkdtemp(prefix="skill-eval-complete-"))
        cmd = base_command(settings, slow=False) + ["--no-tools", "--no-skills", prompt]
        try:
            code, timed_out, _, stderr, lines, _ = stream(cmd, self.env(settings), workdir,
                                                          settings.timeout)
        finally:
            shutil.rmtree(workdir, ignore_errors=True)
        result = parse_run(lines)
        if timed_out:
            raise RuntimeError(f"omp completion timed out after {settings.timeout}s")
        if result.error or code != 0:
            raise RuntimeError(result.error or f"omp exited {code}: {stderr.strip()[-500:]}")
        if not result.final_text.strip():
            raise RuntimeError("omp returned an empty response")
        return result.final_text
