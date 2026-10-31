"""Client-independent pieces shared by the omp and Codex adapters."""

from __future__ import annotations

import json
import os
import re
import shutil
import signal
import subprocess
import tempfile
import threading
import time
from dataclasses import dataclass, field
from pathlib import Path
from typing import Callable, Optional, Protocol

PASS_ENV = ("PATH", "LANG", "LC_ALL", "TMPDIR", "USER", "LOGNAME", "SHELL", "TERM")
TRIGGERED, NOT_TRIGGERED, ERROR = "triggered", "not_triggered", "error"
# Prompts travel in argv; Linux limits a single argument to 128 KiB.
MAX_PROMPT_BYTES = 100_000
STDERR_TAIL = 2000


@dataclass(frozen=True)
class Settings:
    model: str
    effort: str
    home: Path
    timeout: int


@dataclass
class Arm:
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
    """Environment for a client run: no tokens or provider keys from the shell."""
    env = {key: os.environ[key] for key in PASS_ENV if key in os.environ}
    env["HOME"] = str(home)
    env.update(extra)
    return env


def _ignore(directory: str, names: list) -> set:
    skipped = {"evals", "__pycache__"}
    return {name for name in names if name in skipped or name.endswith("-workspace")}


def copy_skill(src: Path, dst: Path, description: Optional[str] = None) -> Path:
    """Copy a skill without its evals or workspaces, which would leak answers."""
    shutil.copytree(src, dst, ignore=_ignore)
    if description is not None:
        skill_md = Path(dst) / "SKILL.md"
        skill_md.write_text(replace_description(skill_md.read_text(encoding="utf-8"), description),
                            encoding="utf-8")
    return Path(dst)


def replace_description(text: str, description: str) -> str:
    """Replace the frontmatter description, leaving every other byte unchanged."""
    lines = text.splitlines(keepends=True)
    if not lines or lines[0].strip() != "---":
        raise ValueError("SKILL.md missing frontmatter")
    end = next((i for i in range(1, len(lines)) if lines[i].strip() == "---"), None)
    if end is None:
        raise ValueError("SKILL.md missing frontmatter end")
    for index in range(1, end):
        if not lines[index].startswith("description:"):
            continue
        stop = index + 1
        # Continuation lines of a block or folded value are indented; blank
        # lines belong to the value only when an indented line follows them.
        scan = stop
        while scan < end and (lines[scan].startswith((" ", "\t")) or not lines[scan].strip()):
            scan += 1
            if lines[scan - 1].strip():
                stop = scan
        newline = "\r\n" if lines[index].endswith("\r\n") else "\n"
        replacement = f"description: {json.dumps(description, ensure_ascii=False)}{newline}"
        return "".join(lines[:index] + [replacement] + lines[stop:])
    raise ValueError("SKILL.md frontmatter has no description")


def plugin_root(skill_dir: Path) -> Optional[Path]:
    """Return the plugin directory that contains skill_dir, if any."""
    skill_dir = Path(skill_dir).resolve()
    if skill_dir.parent.name == "skills" and (skill_dir.parent.parent / "plugin.json").is_file():
        return skill_dir.parent.parent
    return None


def init_workdir(prefix: str) -> Path:
    """Create a temporary git repository to run one task or query in."""
    if shutil.which("git") is None:
        raise RuntimeError("git is required to create evaluation working directories")
    path = Path(tempfile.mkdtemp(prefix=prefix))
    subprocess.run(["git", "init", "-q"], cwd=path, check=True)
    return path


def _kill_group(proc: subprocess.Popen) -> None:
    try:
        os.killpg(proc.pid, signal.SIGKILL)
    except (ProcessLookupError, PermissionError):
        pass


# Client sessions run in their own process groups, so a terminal interrupt
# reaches only Python; stop_all() lets an interrupted script end them.
_ACTIVE: set = set()
_ACTIVE_LOCK = threading.Lock()
INTERRUPTED = threading.Event()


def stop_all() -> None:
    """Mark the run interrupted and kill every client session still running."""
    INTERRUPTED.set()
    with _ACTIVE_LOCK:
        procs = list(_ACTIVE)
    for proc in procs:
        _kill_group(proc)


def stream(cmd: list, env: dict, cwd: Path, timeout: int,
           on_event: Optional[Callable[[dict], Optional[str]]] = None):
    """Run cmd and parse its JSON lines as they arrive.

    Returns (returncode, timed_out, decision, stderr_tail, lines, duration_ms).
    A non-None decision from on_event stops the whole process group early.
    """
    if INTERRUPTED.is_set():
        raise RuntimeError("interrupted")
    start = time.monotonic()
    proc = subprocess.Popen(cmd, env=env, cwd=cwd, stdin=subprocess.DEVNULL,
                            stdout=subprocess.PIPE, stderr=subprocess.PIPE,
                            text=True, encoding="utf-8", errors="replace",
                            start_new_session=True)
    with _ACTIVE_LOCK:
        _ACTIVE.add(proc)
        # An interrupt between the check above and registration would miss
        # this session, so check again now that stop_all() can see it.
        if INTERRUPTED.is_set():
            _kill_group(proc)
    stderr: list = [""]

    def drain() -> None:
        for chunk in proc.stderr:
            stderr[0] = (stderr[0] + chunk)[-STDERR_TAIL:]

    reader = threading.Thread(target=drain, daemon=True)
    reader.start()
    deadline = start + timeout
    timed_out = [False]

    def watchdog() -> None:
        while proc.poll() is None:
            if time.monotonic() >= deadline:
                timed_out[0] = True
                _kill_group(proc)
                return
            time.sleep(0.2)

    threading.Thread(target=watchdog, daemon=True).start()
    lines: list = []
    decision = None
    for line in proc.stdout:
        line = line.rstrip("\n")
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
    _kill_group(proc)
    with _ACTIVE_LOCK:
        _ACTIVE.discard(proc)
    reader.join(timeout=2)
    proc.stdout.close()
    proc.stderr.close()
    if INTERRUPTED.is_set():
        raise RuntimeError("interrupted")
    duration_ms = int((time.monotonic() - start) * 1000)
    return proc.returncode, timed_out[0] and decision is None, decision, stderr[0], lines, duration_ms


def model_matches(requested: str, observed: str) -> bool:
    return requested.rsplit("/", 1)[-1] == observed.rsplit("/", 1)[-1]


def truncate(text: str, limit: int) -> str:
    if len(text) <= limit:
        return text
    return text[:limit] + f"…[truncated {len(text) - limit} chars]"


def check_prompt(prompt: str) -> None:
    if len(prompt.encode("utf-8")) > MAX_PROMPT_BYTES:
        raise ValueError(f"prompt exceeds {MAX_PROMPT_BYTES} bytes")


def strip_selector(path: str) -> str:
    """Drop an omp line selector such as ':1-80' from a path argument."""
    return re.sub(r":[^/]*$", "", path)


class Client(Protocol):
    name: str

    def prepare_arm(self, config: str, source: Optional[Path], tmp: Path,
                    plugin_dir: Optional[Path]) -> Arm:
        """Prepare one configuration under tmp.

        source is the skill version for the arm; for without_skill it is the
        evaluated skill, which the arm must leave out. plugin_dir is the
        plugin that contains the evaluated skill, if any.
        """

    def run_task(self, brief: str, workdir: Path, outputs_dir: Path, arm: Arm,
                 settings: Settings) -> RunResult: ...

    def place_trigger_skill(self, workdir: Path, skill_dir: Path, name: str,
                            description: str) -> Path: ...

    def check_trigger_setup(self, workdir: Path, name: str,
                            settings: Settings) -> Optional[str]: ...

    def detect_trigger(self, query: str, workdir: Path, name: str, skill_md: Path,
                       settings: Settings, max_tool_calls: int) -> tuple: ...

    def complete(self, prompt: str, settings: Settings) -> str: ...

    def list_skills(self, cwd: Path, settings: Settings) -> list: ...


def name_matches(listed: str, name: str) -> bool:
    """True for the bare name or a namespaced form (omp `ns/name`, Codex `plugin:name`)."""
    return listed == name or listed.endswith("/" + name) or listed.endswith(":" + name)


def check_home(client: Client, settings: Settings, name: str) -> Optional[str]:
    """Reject a home where the evaluated skill is already installed.

    An installed copy can load in the without_skill and old_skill runs too,
    which would contaminate the baseline.
    """
    # 1. List from an empty directory so only home-level skills appear.
    probe = Path(tempfile.mkdtemp(prefix="skill-eval-home-"))
    try:
        # 2. A home that cannot be listed cannot be checked.
        try:
            listed = client.list_skills(probe, settings)
        except RuntimeError as error:
            return f"could not list skills in {settings.home}: {error}"
    finally:
        shutil.rmtree(probe, ignore_errors=True)
    # 3. Any match, namespaced or not, means the skill is installed.
    found = [entry[0] for entry in listed if name_matches(entry[0], name)]
    if found:
        return (f"{settings.home} already has a skill named {name} ({', '.join(found)}); "
                "use a home where it is not installed")
    return None
