#!/usr/bin/env python3
"""Shared work log for Claude Code, Codex and omp. Hooks never emit stdout or context."""

import argparse
from datetime import datetime, timedelta, timezone
import fcntl
import hashlib
import json
import os
from pathlib import Path
import re
import shutil
import signal
import subprocess
import sys
import tempfile


SCHEMA = "worklog-v1"
HOSTS = ("claude", "codex", "omp")
RETENTION_DAYS = 90
PRUNE_INTERVAL = timedelta(hours=24)
TRANSCRIPT_SCAN_BYTES = 2 * 1024 * 1024
FIRST_LINE_BYTES = 1024 * 1024
PROMPT_EXCERPT = 160
ERROR_EXCERPT = 300
INPUT_EXCERPT = 200
COMMAND_EXCERPT = 160
SUMMARY_FAILURES = 50
OFF_VALUES = {"off", "0", "false"}
SESSION_RE = re.compile(r"[A-Za-z0-9._-]{1,128}\Z")
DATE_RE = re.compile(r"\d{4}-\d{2}-\d{2}\Z")
EXIT_RE = re.compile(r"^Exit code (\d+)")
CORRECTION_RE = re.compile(
    r"(아니(?:야|라|요|고)|그게 아니|그거 말고|다시 해|잘못|틀렸|되돌려|원래대로|wrong|that's not|not what i|undo|revert)",
    re.I,
)
# copied from memory-manager; plugins stay independent (ADR 0003)
SECRET_RE = re.compile(
    r"-----BEGIN [A-Z0-9 ]*PRIVATE KEY(?: BLOCK)?-----|"
    r"\b(?:[a-z0-9]+[_-])*(?:api[_-]?key|access[_-]?token|password|secret|token|"
    r"client[_-]?secret|aws[_-]?secret[_-]?access[_-]?key|private[_-]?key)"
    r"(?:\\*[\"'])?\s*[:=]\s*\S+|"
    r"\b(?:password|passphrase|api[ _-]?key|access[ _-]?token|secret|token)"
    r"\s+(?:is|was|are)\s+\S+|"
    r"(?:비밀번호|암호|비밀[ _-]?키|API[ _-]?키|토큰)"
    r"\s*(?:은|는|이|가|:|=)\s*\S+|"
    r"\bauthorization\s*:\s*(?:bearer|basic)\s+\S+|"
    r"\b(?:sk-|ghp_|github_pat_)[A-Za-z0-9_-]{20,}|"
    r"\bAKIA[0-9A-Z]{16}\b", re.I
)

# Hook budgets stay below each host's timeout, leaving room for cleanup.
HOOK_SECONDS = {"SessionEnd": 1.0, "Interrupt": 2.0, "Stop": 8.0}
HOOK_DEFAULT_SECONDS = 3.0
HOOK_READ_SECONDS = 1.0
HOOK_CLEANUP_SECONDS = 0.25
HOOK_WRITE = os.write


class WorklogError(Exception):
    def __init__(self, code):
        self.code = code
        super().__init__(code)


class HookTimeout(Exception):
    pass


def utc_now():
    return datetime.now(timezone.utc)


def iso(moment):
    return moment.isoformat(timespec="milliseconds").replace("+00:00", "Z")


def parse_ts(value):
    try:
        return datetime.fromisoformat(value.replace("Z", "+00:00"))
    except (AttributeError, ValueError):
        return None


def digest(data):
    return hashlib.sha256(data).hexdigest()


def root_path():
    override = os.environ.get("SONSU_WORKLOG_HOME")
    root = Path(override).expanduser() if override else Path.home() / ".sonsu" / "worklog"
    if not root.is_absolute():
        raise WorklogError("unsafe_path")
    for component in (root, *root.parents):
        if component.is_symlink():
            raise WorklogError("unsafe_path")
    return root


# copied from memory-manager project_key(); plugins stay independent (ADR 0003).
# The identity is split out so project.json can record the same path.
def project_identity(cwd):
    location = Path(cwd).expanduser().resolve(strict=True)
    if not location.is_dir():
        raise WorklogError("invalid_project")
    git_config_files = {"GIT_CONFIG_GLOBAL", "GIT_CONFIG_SYSTEM", "GIT_CONFIG_NOSYSTEM"}
    git_env = {
        name: value for name, value in os.environ.items()
        if name not in {
            "GIT_ALTERNATE_OBJECT_DIRECTORIES", "GIT_CEILING_DIRECTORIES", "GIT_COMMON_DIR",
            "GIT_CONFIG", "GIT_DIR", "GIT_DISCOVERY_ACROSS_FILESYSTEM", "GIT_IMPLICIT_WORK_TREE",
            "GIT_INDEX_FILE", "GIT_NAMESPACE", "GIT_OBJECT_DIRECTORY", "GIT_PREFIX",
            "GIT_WORK_TREE",
        } and (not name.startswith("GIT_CONFIG_") or name in git_config_files)
    }
    result = subprocess.run(
        ["git", "-C", str(location), "rev-parse", "--git-common-dir"],
        capture_output=True, text=True, check=False, env=git_env,
    )
    common_dir = result.stdout.strip()
    return (location / common_dir).resolve() if result.returncode == 0 and common_dir else location


def project_key(cwd):
    return digest(str(project_identity(cwd)).encode("utf-8"))[:20]


def logging_disabled():
    return os.environ.get("SONSU_WORKLOG", "").strip().lower() in OFF_VALUES


def session_name(value):
    if not isinstance(value, str) or not value:
        return "unknown"
    if SESSION_RE.fullmatch(value):
        return value
    return digest(value.encode("utf-8"))[:32]


def redact(text):
    return SECRET_RE.sub("[redacted]", text)


def clip(text, limit):
    if not isinstance(text, str):
        return None
    return redact(text)[:limit]


def first_line(text):
    if not isinstance(text, str):
        return None
    for line in text.splitlines():
        if line.strip():
            return line.strip()
    return None


def excerpt(text, limit):
    line = first_line(text)
    return clip(line, limit) if line is not None else None


def text_value(value):
    return value if isinstance(value, str) else None


def int_value(value):
    return value if isinstance(value, int) and not isinstance(value, bool) else None


def ensure_dir(path):
    path.mkdir(mode=0o700, parents=True, exist_ok=True)
    if path.is_symlink() or not path.is_dir():
        raise WorklogError("unsafe_path")


def write_new(path, data):
    try:
        fd = os.open(path, os.O_WRONLY | os.O_CREAT | os.O_EXCL, 0o600)
    except FileExistsError:
        return
    try:
        os.write(fd, data)
    finally:
        os.close(fd)


def write_atomic(path, data):
    fd, temporary = tempfile.mkstemp(dir=path.parent, prefix="." + path.name + ".")
    try:
        with os.fdopen(fd, "wb") as handle:
            handle.write(data)
        os.replace(temporary, path)
    except BaseException:
        try:
            os.unlink(temporary)
        except OSError:
            pass
        raise


def append_line(path, record):
    data = (json.dumps(record, ensure_ascii=False, separators=(",", ":")) + "\n").encode("utf-8")
    fd = os.open(path, os.O_WRONLY | os.O_APPEND | os.O_CREAT, 0o600)
    try:
        while data:
            data = data[os.write(fd, data):]
    finally:
        os.close(fd)


def project_dir(root, cwd):
    identity = project_identity(cwd)
    key = digest(str(identity).encode("utf-8"))[:20]
    return root / key, key, identity


def ensure_project(directory, identity):
    ensure_dir(directory)
    marker = directory / "project.json"
    if not marker.exists():
        write_new(marker, (json.dumps({"identity": str(identity), "created": iso(utc_now())},
                                      ensure_ascii=False) + "\n").encode("utf-8"))


def prune_host(host_dir, days, today):
    cutoff = (today - timedelta(days=days)).isoformat()
    removed = 0
    if not host_dir.is_dir() or host_dir.is_symlink():
        return removed
    for entry in sorted(host_dir.iterdir()):
        if DATE_RE.fullmatch(entry.name) and entry.name < cutoff and entry.is_dir() and not entry.is_symlink():
            shutil.rmtree(entry, ignore_errors=True)
            removed += 1
    return removed


def maybe_prune(host_dir):
    state_dir = host_dir / ".state"
    marker = state_dir / "last-prune"
    now = utc_now()
    try:
        last = parse_ts(marker.read_text(encoding="utf-8").strip())
    except OSError:
        last = None
    if last is not None and now - last < PRUNE_INTERVAL:
        return
    prune_host(host_dir, RETENTION_DAYS, now.date())
    ensure_dir(state_dir)
    write_atomic(marker, (iso(now) + "\n").encode("utf-8"))


class Session:
    """One host session. State reads/writes and log appends happen under one flock."""

    def __init__(self, root, cwd, host, session_id):
        self.directory, self.key, self.identity = project_dir(root, cwd)
        self.cwd = os.path.abspath(cwd)
        self.host = host
        self.session_id = session_name(session_id)
        self.host_dir = self.directory / host
        self.state_dir = self.host_dir / ".state"
        self.state_path = self.state_dir / (self.session_id + ".json")
        self.lock_fd = None
        self.state = {}

    def disabled(self):
        return (self.directory / "disabled").exists()

    def __enter__(self):
        ensure_project(self.directory, self.identity)
        ensure_dir(self.state_dir)
        self.lock_fd = os.open(self.state_dir / (self.session_id + ".lock"), os.O_RDWR | os.O_CREAT, 0o600)
        fcntl.flock(self.lock_fd, fcntl.LOCK_EX)
        try:
            state = json.loads(self.state_path.read_text(encoding="utf-8"))
        except (OSError, ValueError):
            state = {}
        self.state = {
            "date": state.get("date") if isinstance(state.get("date"), str) and DATE_RE.fullmatch(state["date"]) else None,
            "host_version": text_value(state.get("host_version")),
            "transcript_path": text_value(state.get("transcript_path")),
            "rollout_offset": int_value(state.get("rollout_offset")) or 0,
            "context_scanned": state.get("context_scanned") is True,
        }
        return self

    def __exit__(self, *exc):
        try:
            if self.state["date"] is not None:
                write_atomic(self.state_path, (json.dumps(self.state, ensure_ascii=False) + "\n").encode("utf-8"))
        finally:
            os.close(self.lock_fd)
        return False

    def write(self, event, signal_source, data, turn_id=None):
        now = utc_now()
        if self.state["date"] is None:
            self.state["date"] = now.date().isoformat()
        day = self.host_dir / self.state["date"]
        ensure_dir(day)
        append_line(day / (self.session_id + ".jsonl"), {
            "schema": SCHEMA, "ts": iso(now), "host": self.host,
            "host_version": self.state["host_version"], "session_id": self.session_id,
            "project_key": self.key, "cwd": self.cwd, "turn_id": turn_id,
            "event": event, "signal_source": signal_source, "data": data,
        })


def read_first_line(path):
    with open(path, "rb") as handle:
        return handle.readline(FIRST_LINE_BYTES)


def codex_cli_version(path):
    if not path:
        return None
    try:
        record = json.loads(read_first_line(path))
    except (OSError, ValueError):
        return None
    if isinstance(record, dict) and record.get("type") == "session_meta":
        payload = record.get("payload")
        if isinstance(payload, dict):
            return text_value(payload.get("cli_version"))
    return None


def attachment_chars(attachment):
    value = attachment.get("stdout")
    if not isinstance(value, str) or not value:
        value = attachment.get("content")
    if isinstance(value, str):
        return len(value)
    return len(json.dumps(value, ensure_ascii=False))


def scan_claude_transcript(session, path):
    """Record SessionStart hook outputs from the first 2 MB of a Claude transcript once."""
    try:
        with open(path, "rb") as handle:
            data = handle.read(TRANSCRIPT_SCAN_BYTES)
    except OSError:
        return
    complete = data[:data.rfind(b"\n") + 1] if len(data) == TRANSCRIPT_SCAN_BYTES else data
    loads = []
    for raw in complete.splitlines():
        try:
            record = json.loads(raw)
        except ValueError:
            continue
        if not isinstance(record, dict):
            continue
        if session.state["host_version"] is None and isinstance(record.get("version"), str):
            session.state["host_version"] = record["version"]
        attachment = record.get("attachment")
        if (record.get("type") == "attachment" and isinstance(attachment, dict) and
                attachment.get("type") in ("hook_success", "hook_additional_context") and
                attachment.get("hookEvent") == "SessionStart"):
            command = text_value(attachment.get("command"))
            loads.append({"kind": "hook_output", "hook_name": text_value(attachment.get("hookName")),
                          "command": command[:COMMAND_EXCERPT] if command is not None else None,
                          "chars": attachment_chars(attachment)})
    for entry in loads:
        session.write("context_load", "transcript:attachment", entry)
    session.state["context_scanned"] = True


def codex_failed_items(session, path):
    """Read complete rollout lines after the saved offset and record failed items."""
    offset = session.state["rollout_offset"]
    try:
        with open(path, "rb") as handle:
            if offset > os.fstat(handle.fileno()).st_size:
                offset = 0
            handle.seek(offset)
            data = handle.read()
    except OSError:
        return
    end = data.rfind(b"\n") + 1
    for raw in data[:end].splitlines():
        if b"item_completed" not in raw or b"failed" not in raw:
            continue
        try:
            record = json.loads(raw)
        except ValueError:
            continue
        payload = record.get("payload") if isinstance(record, dict) else None
        if not (record.get("type") == "event_msg" and isinstance(payload, dict) and
                payload.get("type") == "item_completed"):
            continue
        item = payload.get("item")
        if not isinstance(item, dict) or item.get("status") != "failed":
            continue
        error = None
        for field in ("aggregated_output", "stderr", "stdout"):
            error = first_line(item.get(field))
            if error is not None:
                break
        command = item.get("command")
        if isinstance(command, list):
            command = command[-1] if command else None
        duration = item.get("duration")
        duration_ms = None
        if isinstance(duration, dict) and int_value(duration.get("secs")) is not None:
            duration_ms = duration["secs"] * 1000 + (int_value(duration.get("nanos")) or 0) // 1_000_000
        session.write("tool_result", "rollout:item_completed", {
            "outcome": "failed", "tool_name": text_value(item.get("type")),
            "tool_use_id": text_value(item.get("id")), "exit_code": int_value(item.get("exit_code")),
            "error": clip(error, ERROR_EXCERPT), "is_interrupt": None, "duration_ms": duration_ms,
            "input_excerpt": clip(text_value(command), INPUT_EXCERPT),
        }, turn_id=text_value(payload.get("turn_id")))
    session.state["rollout_offset"] = offset + end


def tool_input_excerpt(event):
    tool_input = event.get("tool_input")
    if not isinstance(tool_input, dict):
        return None
    value = tool_input.get("command")
    if not isinstance(value, str):
        value = tool_input.get("file_path")
    return clip(text_value(value), INPUT_EXCERPT)


def session_start_data(event):
    return {"source": text_value(event.get("source")), "transcript_path": text_value(event.get("transcript_path")),
            "model": text_value(event.get("model")), "agent_kind": text_value(event.get("agent_type"))}


def prompt_data(event):
    prompt = event.get("prompt") if isinstance(event.get("prompt"), str) else ""
    data = {"chars": len(prompt)}
    if os.environ.get("SONSU_WORKLOG_PROMPTS", "").strip().lower() not in OFF_VALUES:
        data["excerpt"] = clip(" ".join(prompt.split()), PROMPT_EXCERPT)
    data["correction_hint"] = bool(CORRECTION_RE.search(prompt))
    return data


def stop_data(event):
    message = event.get("last_assistant_message")
    return {"last_message_chars": len(message) if isinstance(message, str) else None}


def handle_claude(session, name, event, source):
    if name == "SessionStart":
        session.state["transcript_path"] = text_value(event.get("transcript_path"))
        session.write("session_start", source, session_start_data(event))
        maybe_prune(session.host_dir)
    elif name == "InstructionsLoaded":
        path = text_value(event.get("file_path"))
        try:
            size = os.path.getsize(path) if path else None
        except OSError:
            size = None
        session.write("context_load", source, {
            "kind": "instructions", "file_path": path, "memory_type": text_value(event.get("memory_type")),
            "load_reason": text_value(event.get("load_reason")), "bytes": size})
    elif name == "UserPromptSubmit":
        session.write("user_prompt", source, prompt_data(event))
    elif name == "PostToolUse":
        session.write("tool_result", source, {
            "outcome": "ok", "tool_name": text_value(event.get("tool_name")),
            "tool_use_id": text_value(event.get("tool_use_id")),
            "exit_code": None, "error": None, "is_interrupt": None,
            "duration_ms": int_value(event.get("duration_ms")), "input_excerpt": tool_input_excerpt(event)})
    elif name == "PostToolUseFailure":
        lines = [line.strip() for line in (text_value(event.get("error")) or "").splitlines() if line.strip()]
        exit_code = None
        if lines:
            matched = EXIT_RE.match(lines[0])
            if matched:
                exit_code = int(matched.group(1))
                lines = lines[1:]
        is_interrupt = event.get("is_interrupt")
        session.write("tool_result", source, {
            "outcome": "failed", "tool_name": text_value(event.get("tool_name")),
            "tool_use_id": text_value(event.get("tool_use_id")), "exit_code": exit_code,
            "error": clip(lines[0], ERROR_EXCERPT) if lines else None,
            "is_interrupt": is_interrupt if isinstance(is_interrupt, bool) else None,
            "duration_ms": int_value(event.get("duration_ms")), "input_excerpt": tool_input_excerpt(event)})
    elif name == "PermissionDenied":
        session.write("permission_denied", source, {
            "tool_name": text_value(event.get("tool_name")), "tool_use_id": text_value(event.get("tool_use_id")),
            "reason": clip(text_value(event.get("reason")), ERROR_EXCERPT)})
    elif name == "Stop":
        if not session.state["context_scanned"]:
            path = text_value(event.get("transcript_path")) or session.state["transcript_path"]
            if path:
                scan_claude_transcript(session, path)
        session.write("stop", source, stop_data(event))
    elif name == "StopFailure":
        session.write("stop_failure", source, {
            "error": clip(text_value(event.get("error")), ERROR_EXCERPT),
            "error_details": clip(text_value(event.get("error_details")), ERROR_EXCERPT)})
    else:
        handle_common(session, name, event, source)


def handle_codex(session, name, event, source):
    turn_id = text_value(event.get("turn_id"))
    if name == "SessionStart":
        path = text_value(event.get("transcript_path"))
        session.state["transcript_path"] = path
        session.state["host_version"] = codex_cli_version(path)
        session.write("session_start", source, session_start_data(event), turn_id)
        maybe_prune(session.host_dir)
    elif name == "UserPromptSubmit":
        session.write("user_prompt", source, prompt_data(event), turn_id)
    elif name == "PostToolUse":
        # Codex reports failed shell commands here too, without an exit code.
        session.write("tool_result", source, {
            "outcome": "unknown", "tool_name": text_value(event.get("tool_name")),
            "tool_use_id": text_value(event.get("tool_use_id")), "exit_code": None,
            "error": None, "is_interrupt": None, "duration_ms": None,
            "input_excerpt": tool_input_excerpt(event)}, turn_id)
    elif name == "Stop":
        path = text_value(event.get("transcript_path")) or session.state["transcript_path"]
        if path:
            session.state["transcript_path"] = path
            if session.state["host_version"] is None:
                session.state["host_version"] = codex_cli_version(path)
            codex_failed_items(session, path)
        session.write("stop", source, stop_data(event), turn_id)
    elif name == "Interrupt":
        session.write("interrupt", source, {}, turn_id)
    else:
        handle_common(session, name, event, source, turn_id)


def handle_common(session, name, event, source, turn_id=None):
    if name == "SubagentStop":
        session.write("subagent_stop", source, {
            "agent_id": text_value(event.get("agent_id")), "agent_type": text_value(event.get("agent_type")),
            "agent_transcript_path": text_value(event.get("agent_transcript_path"))}, turn_id)
    elif name == "PreCompact":
        session.write("compact", source, {"trigger": text_value(event.get("trigger"))}, turn_id)
    elif name == "SessionEnd":
        session.write("session_end", source, {"reason": text_value(event.get("reason"))}, turn_id)


HANDLERS = {"claude": handle_claude, "codex": handle_codex}
CLAUDE_EVENTS = {"SessionStart", "InstructionsLoaded", "UserPromptSubmit", "PostToolUse", "PostToolUseFailure",
                 "PermissionDenied", "Stop", "StopFailure", "SubagentStop", "PreCompact", "SessionEnd"}
CODEX_EVENTS = {"SessionStart", "UserPromptSubmit", "PostToolUse", "Stop", "SubagentStop", "PreCompact",
                "Interrupt", "SessionEnd"}
HOST_EVENTS = {"claude": CLAUDE_EVENTS, "codex": CODEX_EVENTS}


def record_hook(host, event):
    name = event.get("hook_event_name")
    cwd = event.get("cwd")
    if name not in HOST_EVENTS[host] or not isinstance(cwd, str) or not cwd:
        return
    root = root_path()
    session = Session(root, cwd, host, event.get("session_id"))
    if session.disabled():
        return
    with session:
        HANDLERS[host](session, name, event, "hook:" + name)


def best_effort_hook_output(fd, text):
    try:
        os.set_blocking(fd, False)
        HOOK_WRITE(fd, text.encode("utf-8"))
    except OSError:
        pass


def run_hook(host):
    """Fail-open hook entry (structure follows memory-manager hooks/capture.py)."""

    def cleanup_timeout(signum, frame):
        try:
            best_effort_hook_output(2, "worklog: hook timed out\n")
        finally:
            os._exit(0)

    def operation_timeout(signum, frame):
        signal.signal(signal.SIGALRM, cleanup_timeout)
        signal.setitimer(signal.ITIMER_REAL, HOOK_CLEANUP_SECONDS)
        raise HookTimeout()

    started = utc_now()
    previous = signal.signal(signal.SIGALRM, operation_timeout)
    signal.setitimer(signal.ITIMER_REAL, HOOK_READ_SECONDS)
    try:
        if logging_disabled():
            return 0
        try:
            event = json.load(sys.stdin)
        except ValueError:
            return 0
        if not isinstance(event, dict):
            return 0
        budget = HOOK_SECONDS.get(event.get("hook_event_name"), HOOK_DEFAULT_SECONDS)
        remaining = budget - (utc_now() - started).total_seconds()
        if remaining <= 0:
            raise HookTimeout()
        signal.setitimer(signal.ITIMER_REAL, remaining)
        record_hook(host, event)
    except Exception as error:
        # A hook must not block the host. Keep the diagnostic free of prompt text.
        try:
            best_effort_hook_output(2, "worklog: hook unavailable (" + type(error).__name__ + ")\n")
        except HookTimeout:
            pass
    finally:
        signal.setitimer(signal.ITIMER_REAL, 0)
        signal.signal(signal.SIGALRM, previous)
    return 0


def iter_records(directory, hosts, since):
    """Yield (record, log_path, line, transcript_path) newer than `since` for the given hosts."""
    for host in hosts:
        host_dir = directory / host
        if not host_dir.is_dir() or host_dir.is_symlink():
            continue
        for day in sorted(host_dir.iterdir()):
            if not DATE_RE.fullmatch(day.name) or not day.is_dir() or day.is_symlink():
                continue
            for log in sorted(day.glob("*.jsonl")):
                if not log.is_file() or log.stat().st_mtime < since.timestamp():
                    continue
                parsed = []
                transcript = None
                with open(log, encoding="utf-8", errors="replace") as handle:
                    for number, raw in enumerate(handle, 1):
                        try:
                            record = json.loads(raw)
                        except ValueError:
                            continue
                        if not isinstance(record, dict) or record.get("schema") != SCHEMA:
                            continue
                        data = record.get("data") if isinstance(record.get("data"), dict) else {}
                        if record.get("event") == "session_start" and transcript is None:
                            transcript = text_value(data.get("transcript_path"))
                        parsed.append((record, number))
                for record, number in parsed:
                    moment = parse_ts(record.get("ts"))
                    if moment is not None and moment >= since:
                        yield record, str(log), number, transcript


def is_failure(record):
    event = record.get("event")
    data = record.get("data") if isinstance(record.get("data"), dict) else {}
    if event == "tool_result":
        return data.get("outcome") == "failed"
    if event == "user_prompt":
        return data.get("correction_hint") is True
    return event in ("stop_failure", "permission_denied", "interrupt")


def failure_entry(record, transcript):
    data = record.get("data") if isinstance(record.get("data"), dict) else {}
    return {
        "ts": record.get("ts"), "host": record.get("host"), "session_id": record.get("session_id"),
        "event": record.get("event"), "tool_name": data.get("tool_name") or record.get("event"),
        "exit_code": data.get("exit_code"), "error": data.get("error") or data.get("reason"),
        "transcript_path": transcript, "tool_use_id": data.get("tool_use_id"),
    }


def summarize(directory, days, host):
    since = utc_now() - timedelta(days=days)
    hosts = (host,) if host else HOSTS
    sessions = {}
    counts = {}
    corrections = 0
    failures = []
    for record, _, _, transcript in iter_records(directory, hosts, since):
        sessions.setdefault(record.get("host"), set()).add(record.get("session_id"))
        event = record.get("event")
        data = record.get("data") if isinstance(record.get("data"), dict) else {}
        key = f"tool_result {data.get('outcome')}" if event == "tool_result" else event
        counts[key] = counts.get(key, 0) + 1
        if event == "user_prompt" and data.get("correction_hint") is True:
            corrections += 1
        elif is_failure(record):
            failures.append(failure_entry(record, transcript))
    failures.sort(key=lambda entry: entry["ts"] or "", reverse=True)
    return {
        "dir": str(directory), "days": days,
        "sessions": {name: len(ids) for name, ids in sorted(sessions.items())},
        "counts": dict(sorted(counts.items())), "corrections": corrections,
        "failures": failures[:SUMMARY_FAILURES],
    }


def summary_text(summary):
    lines = [f"worklog {summary['dir']} (last {summary['days']} days)"]
    sessions = " ".join(f"{host}={count}" for host, count in summary["sessions"].items())
    lines.append("sessions: " + (sessions or "none"))
    lines.append("events:")
    for key, count in summary["counts"].items():
        suffix = f" (corrections {summary['corrections']})" if key == "user_prompt" else ""
        lines.append(f"  {key} {count}{suffix}")
    lines.append(f"failures (latest first, max {SUMMARY_FAILURES}):")
    for entry in summary["failures"]:
        exit_code = "-" if entry["exit_code"] is None else entry["exit_code"]
        error = json.dumps(entry["error"] or "", ensure_ascii=False)
        lines.append(f"  {entry['ts']} {entry['host']} {(entry['session_id'] or '')[:8]} {entry['tool_name']} "
                     f"exit={exit_code} {error} transcript={entry['transcript_path'] or '-'} "
                     f"tool_use_id={entry['tool_use_id'] or '-'}")
    return "\n".join(lines)


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    commands = parser.add_subparsers(dest="command", required=True)
    hook = commands.add_parser("hook", help="record one host hook event from stdin")
    hook.add_argument("--host", choices=tuple(HANDLERS), required=True)
    location = argparse.ArgumentParser(add_help=False)
    location.add_argument("--cwd", default=os.getcwd())
    commands.add_parser("where", parents=[location], help="print this project's log directory")
    summary = commands.add_parser("summary", parents=[location], help="summarize recent records")
    summary.add_argument("--days", type=int, default=7)
    summary.add_argument("--host", choices=HOSTS)
    summary.add_argument("--format", choices=("text", "json"), default="text")
    failures = commands.add_parser("failures", parents=[location], help="print failure records as JSON lines")
    failures.add_argument("--days", type=int, default=14)
    failures.add_argument("--format", choices=("jsonl",), default="jsonl")
    prune = commands.add_parser("prune", parents=[location], help="remove expired date directories")
    prune.add_argument("--days", type=int, default=RETENTION_DAYS)
    args = parser.parse_args(argv)

    if args.command == "hook":
        return run_hook(args.host)
    try:
        directory = root_path() / project_key(args.cwd)
    except (OSError, WorklogError) as error:
        parser.error(getattr(error, "code", None) or str(error))
    if args.command == "where":
        print(directory)
    elif args.command == "summary":
        result = summarize(directory, args.days, args.host)
        print(json.dumps(result, ensure_ascii=False, indent=2) if args.format == "json" else summary_text(result))
    elif args.command == "failures":
        since = utc_now() - timedelta(days=args.days)
        selected = []
        for record, log_path, line, transcript in iter_records(directory, HOSTS, since):
            if is_failure(record):
                selected.append(dict(record, log_path=log_path, line=line, transcript_path=transcript))
        selected.sort(key=lambda entry: entry.get("ts") or "", reverse=True)
        for entry in selected:
            print(json.dumps(entry, ensure_ascii=False))
    elif args.command == "prune":
        today = utc_now().date()
        print(sum(prune_host(directory / host, args.days, today) for host in HOSTS))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
