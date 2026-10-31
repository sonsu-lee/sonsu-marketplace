"""Pieces shared by the omp and Codex adapters."""

from __future__ import annotations

import json
import os
import shutil
import signal
import subprocess
import tempfile
import threading
import time
from dataclasses import dataclass, field
from pathlib import Path
from typing import Callable, Optional

# Only these variables reach a client, so shell tokens and provider keys do not.
PASS_ENV = ("PATH", "LANG", "LC_ALL", "TMPDIR", "USER", "LOGNAME", "SHELL", "TERM")
TRIGGERED, NOT_TRIGGERED, ERROR = "triggered", "not_triggered", "error"


@dataclass(frozen=True)
class Settings:
    model: str
    effort: str
    home: Path
    timeout: int


@dataclass
class Arm:
    """One configuration: the skill copy to name in the brief, and for omp the
    plugin copy to load."""
    config: str
    skill_dir: Optional[Path]
    plugin_dir: Optional[Path]


@dataclass
class RunResult:
    final_text: str = ""
    transcript: str = ""
    tool_calls: dict = field(default_factory=dict)
    tool_errors: int = 0
    total_tokens: int = 0
    model: Optional[str] = None
    effort: Optional[str] = None
    error: Optional[str] = None
    duration_ms: int = 0
    raw_lines: list = field(default_factory=list)


def client_env(home: Path, **extra: str) -> dict:
    env = {key: os.environ[key] for key in PASS_ENV if key in os.environ}
    env["HOME"] = str(home)
    env.update(extra)
    return env


def _skip_copied(directory: str, names: list) -> set:
    return {n for n in names if n in ("evals", "__pycache__") or n.endswith("-workspace")}


def copy_skill(src: Path, dst: Path, description: Optional[str] = None) -> Path:
    """Copy a skill without evals/, so runs cannot read assertions."""
    shutil.copytree(src, dst, ignore=_skip_copied)
    if description is not None:
        skill_md = Path(dst) / "SKILL.md"
        skill_md.write_text(replace_description(skill_md.read_text(encoding="utf-8"), description),
                            encoding="utf-8")
    return Path(dst)


def replace_description(text: str, description: str) -> str:
    """Replace the frontmatter description and its indented continuation lines."""
    lines = text.splitlines(keepends=True)
    end = next(i for i in range(1, len(lines)) if lines[i].strip() == "---")
    for index in range(1, end):
        if lines[index].startswith("description:"):
            stop = index + 1
            while stop < end and lines[stop].startswith((" ", "\t")):
                stop += 1
            replacement = f"description: {json.dumps(description, ensure_ascii=False)}\n"
            return "".join(lines[:index] + [replacement] + lines[stop:])
    raise ValueError("SKILL.md frontmatter has no description")


def plugin_root(skill_dir: Path) -> Optional[Path]:
    """Return the plugin that contains skill_dir, if it is plugins/<p>/skills/<s>."""
    skill_dir = Path(skill_dir).resolve()
    if skill_dir.parent.name == "skills" and (skill_dir.parent.parent / "plugin.json").is_file():
        return skill_dir.parent.parent
    return None


def init_workdir(prefix: str) -> Path:
    """Create an empty temporary git repository for one run."""
    path = Path(tempfile.mkdtemp(prefix=prefix))
    subprocess.run(["git", "init", "-q"], cwd=path, check=True)
    return path


# Clients run in their own process groups so that a timeout or an early
# trigger decision can end them with their tool processes. A terminal
# interrupt therefore reaches only Python, and stop_all() ends them instead.
_ACTIVE: set = set()
_ACTIVE_LOCK = threading.Lock()
INTERRUPTED = threading.Event()


def _kill_group(proc: subprocess.Popen) -> None:
    try:
        os.killpg(proc.pid, signal.SIGKILL)
    except ProcessLookupError:
        pass


def stop_all() -> None:
    INTERRUPTED.set()
    with _ACTIVE_LOCK:
        for proc in list(_ACTIVE):
            _kill_group(proc)


def stream(cmd: list, env: dict, cwd: Path, timeout: int,
           on_event: Optional[Callable[[dict], Optional[str]]] = None):
    """Run cmd, parsing each stdout line as JSON as it arrives.

    Returns (returncode, timed_out, decision, stderr_tail, lines, duration_ms).
    The first non-None value on_event returns becomes the decision and ends
    the client. Raises RuntimeError("interrupted") after stop_all().
    """
    start = time.monotonic()
    with _ACTIVE_LOCK:
        if INTERRUPTED.is_set():
            raise RuntimeError("interrupted")
        proc = subprocess.Popen(cmd, env=env, cwd=cwd, stdin=subprocess.DEVNULL,
                                stdout=subprocess.PIPE, stderr=subprocess.PIPE,
                                text=True, encoding="utf-8", errors="replace",
                                start_new_session=True)
        _ACTIVE.add(proc)
    stderr = []
    reader = threading.Thread(target=lambda: stderr.extend(proc.stderr), daemon=True)
    reader.start()
    timer = threading.Timer(timeout, _kill_group, [proc])
    timer.start()
    lines, decision = [], None
    for line in proc.stdout:
        line = line.strip()
        if not line:
            continue
        lines.append(line)
        if on_event is None or decision is not None:
            continue
        try:
            event = json.loads(line)
        except json.JSONDecodeError:
            continue
        if isinstance(event, dict):
            decision = on_event(event)
            if decision is not None:
                _kill_group(proc)
    proc.wait()
    timed_out = not timer.is_alive() and decision is None
    timer.cancel()
    _kill_group(proc)
    with _ACTIVE_LOCK:
        _ACTIVE.discard(proc)
    reader.join(timeout=2)
    proc.stdout.close()
    proc.stderr.close()
    if INTERRUPTED.is_set():
        raise RuntimeError("interrupted")
    duration_ms = int((time.monotonic() - start) * 1000)
    return proc.returncode, timed_out, decision, "".join(stderr)[-2000:], lines, duration_ms


def model_matches(requested: str, observed: str) -> bool:
    """Compare model names without a provider prefix such as anthropic/."""
    return requested.rsplit("/", 1)[-1] == observed.rsplit("/", 1)[-1]


def truncate(text: str, limit: int) -> str:
    if len(text) <= limit:
        return text
    return text[:limit] + f"…[truncated {len(text) - limit} chars]"


def name_matches(listed: str, name: str) -> bool:
    """True for name, omp's <namespace>/name, or Codex's <plugin>:name."""
    return listed == name or listed.endswith("/" + name) or listed.endswith(":" + name)


def check_home(client, settings: Settings, name: str) -> Optional[str]:
    """Return a problem when the home already has the skill.

    An installed copy can load in the baseline runs too.
    """
    probe = Path(tempfile.mkdtemp(prefix="skill-eval-home-"))
    try:
        listed = client.list_skills(probe, settings)
    except RuntimeError as error:
        return f"could not list skills in {settings.home}: {error}"
    finally:
        shutil.rmtree(probe, ignore_errors=True)
    found = [n for n, _ in listed if name_matches(n, name)]
    if found:
        return (f"{settings.home} already has a skill named {name} ({', '.join(found)}); "
                "use a home where it is not installed")
    return None
