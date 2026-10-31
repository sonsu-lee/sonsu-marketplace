"""omp adapter: run a task, detect a skill load, and make a tool-less call."""

from __future__ import annotations

import json
import shutil
import subprocess
import tempfile
from pathlib import Path
from typing import Optional

from scripts.clients.base import (
    ERROR, NOT_TRIGGERED, TRIGGERED, Arm, RunResult, Settings, client_env,
    copy_skill, name_matches, stream, truncate,
)
from scripts.utils import parse_skill_md


def base_command(settings: Settings) -> list:
    return ["omp", "-p", "--mode", "json", "--no-session", "--no-title",
            "--no-context-files", "--no-rules", "--no-extensions",
            "--model", settings.model, "--slow", settings.model,
            "--thinking", settings.effort]


def text_content(value) -> str:
    if isinstance(value, str):
        return value
    if isinstance(value, list):
        return "\n".join(text_content(v) for v in value)
    if isinstance(value, dict):
        return text_content(value.get("text", value.get("content", "")))
    return ""


def parse_run(lines: list) -> RunResult:
    """Turn omp JSON events into a run result and a readable transcript."""
    result = RunResult(raw_lines=list(lines))
    sections, names = [], {}
    for line in lines:
        event = json.loads(line) if line.startswith("{") else {}
        kind = event.get("type")
        if kind == "tool_execution_start":
            name = event.get("toolName", "unknown")
            names[event.get("toolCallId")] = name
            result.tool_calls[name] = result.tool_calls.get(name, 0) + 1
            args = truncate(json.dumps(event.get("args") or {}, ensure_ascii=False), 2000)
            sections.append(f"### Tool call: {name}\n\n````json\n{args}\n````")
        elif kind == "tool_execution_end":
            name = names.get(event.get("toolCallId"), "unknown")
            failed = bool(event.get("isError"))
            result.tool_errors += failed
            text = text_content((event.get("result") or {}).get("content"))
            label = f"### Tool result: {name}" + (" (error)" if failed else "")
            sections.append(f"{label}\n\n````text\n{truncate(text, 4000)}\n````")
        elif kind == "message_end" and event["message"].get("role") == "assistant":
            message = event["message"]
            result.total_tokens += (message.get("usage") or {}).get("totalTokens", 0)
            result.model = message.get("model") or result.model
            result.effort = ((message.get("requestControls") or {}).get("effort") or {}).get(
                "topLevel") or result.effort
            text = "".join(b.get("text", "") for b in message.get("content", [])
                           if b.get("type") == "text")
            if text.strip():
                sections.append(f"### Assistant\n\n{text}")
                result.final_text = text
            if message.get("stopReason") == "error":
                result.error = message.get("errorMessage") or "assistant error"
    if result.model is None and result.error is None:
        result.error = "no assistant message"
    result.transcript = "\n\n".join(sections)
    return result


class TriggerDetector:
    """Judge the first tool call other than todo, as skill-creator does.

    It is a trigger when that call reads the skill, by skill://<name> or by
    the placed .omp/skills/<name> path.
    """

    def __init__(self, name: str):
        self.markers = (f"skill://{name}", f".omp/skills/{name}/")
        self.error: Optional[str] = None

    def feed(self, event: dict) -> Optional[str]:
        kind = event.get("type")
        if kind == "tool_execution_start" and event.get("toolName") != "todo":
            args = json.dumps(event.get("args") or {})
            return TRIGGERED if any(m in args for m in self.markers) else NOT_TRIGGERED
        message = event.get("message") or {}
        if kind == "message_end" and message.get("stopReason") == "error":
            self.error = message.get("errorMessage") or "assistant error"
            return ERROR
        return None

    def finish(self, returncode: Optional[int], timed_out: bool) -> str:
        # Answering without any tool call means the skill was not used.
        return NOT_TRIGGERED if returncode == 0 and not timed_out else ERROR


class OmpClient:
    name = "omp"

    def env(self, settings: Settings) -> dict:
        return client_env(settings.home)

    def prepare_arm(self, config: str, source: Optional[Path], tmp: Path,
                    plugin_dir: Optional[Path]) -> Arm:
        """Prepare one configuration.

        source is the arm's skill version; without_skill passes the evaluated
        skill so it can be left out of the plugin copy. A plugin skill runs
        inside a copy of its plugin, so the plugin's agents and sibling skills
        are present in every arm and only the evaluated skill differs.
        """
        name = parse_skill_md(Path(source))[0]
        if plugin_dir is None:
            if config == "without_skill":
                return Arm(config, None, None)
            return Arm(config, copy_skill(source, Path(tmp) / config / name), None)
        plugin_copy = Path(tmp) / config / Path(plugin_dir).name
        shutil.copytree(plugin_dir, plugin_copy,
                        ignore=lambda d, names: {n for n in names if n in ("evals", "__pycache__")})
        skill_dir = plugin_copy / "skills" / name
        shutil.rmtree(skill_dir)
        if config == "without_skill":
            return Arm(config, None, plugin_copy)
        copy_skill(source, skill_dir)
        return Arm(config, skill_dir, plugin_copy)

    def run_task(self, brief: str, workdir: Path, outputs_dir: Path, arm: Arm,
                 settings: Settings) -> RunResult:
        cmd = base_command(settings) + ["--approval-mode", "yolo"]
        cmd += ["--plugin-dir", str(arm.plugin_dir)] if arm.plugin_dir else ["--no-skills"]
        code, timed_out, _, stderr, lines, duration = stream(
            cmd + [brief], self.env(settings), workdir, settings.timeout)
        result = parse_run(lines)
        result.duration_ms = duration
        if timed_out:
            result.error = f"timed out after {settings.timeout}s"
        elif code != 0 and result.error is None:
            result.error = f"omp exited {code}: {stderr.strip()[-500:]}"
        return result

    def place_trigger_skill(self, workdir: Path, skill_dir: Path, name: str,
                            description: str) -> None:
        copy_skill(skill_dir, Path(workdir) / ".omp" / "skills" / name, description)

    def list_skills(self, cwd: Path, settings: Settings) -> list:
        proc = subprocess.run(["omp", "skill", "list"], env=self.env(settings), cwd=cwd,
                              capture_output=True, text=True, stdin=subprocess.DEVNULL)
        if proc.returncode != 0:
            raise RuntimeError(proc.stderr.strip()[-500:] or f"exit {proc.returncode}")
        # Each line starts with the skill name; warning lines mention names too.
        return [(line.split(None, 1)[0], None) for line in proc.stdout.splitlines()
                if line.strip() and "warning:" not in line]

    def check_trigger_setup(self, workdir: Path, name: str, settings: Settings) -> Optional[str]:
        found = [n for n, _ in self.list_skills(workdir, settings) if name_matches(n, name)]
        if found != [name]:
            return f"expected one omp skill named {name}, found: {', '.join(found) or 'none'}"
        return None

    def detect_trigger(self, query: str, workdir: Path, name: str,
                       settings: Settings) -> tuple:
        detector = TriggerDetector(name)
        cmd = base_command(settings) + ["--approval-mode", "always-ask", "--skills", name, query]
        code, timed_out, decision, stderr, _, _ = stream(
            cmd, self.env(settings), workdir, settings.timeout, detector.feed)
        status = decision or detector.finish(code, timed_out)
        if status != ERROR:
            return status, None
        return status, detector.error or stderr.strip()[-500:] or f"omp exited {code}"

    def complete(self, prompt: str, settings: Settings) -> str:
        workdir = Path(tempfile.mkdtemp(prefix="skill-eval-complete-"))
        cmd = ["omp", "-p", "--mode", "json", "--no-session", "--no-title",
               "--no-context-files", "--no-rules", "--no-extensions", "--no-tools",
               "--no-skills", "--model", settings.model, "--thinking", settings.effort, prompt]
        try:
            code, timed_out, _, stderr, lines, _ = stream(cmd, self.env(settings), workdir,
                                                          settings.timeout)
        finally:
            shutil.rmtree(workdir, ignore_errors=True)
        result = parse_run(lines)
        if timed_out or code != 0 or result.error or not result.final_text.strip():
            raise RuntimeError(result.error or f"omp exited {code}: {stderr.strip()[-500:]}")
        return result.final_text
