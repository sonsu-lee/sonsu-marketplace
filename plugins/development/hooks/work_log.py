#!/usr/bin/env python3
"""Record observed lifecycle events only when a local directory is selected."""

import datetime
import hashlib
import json
import os
import stat
import sys
from pathlib import Path

try:
    import fcntl
except ImportError:
    fcntl = None

EVENTS = {
    "SessionStart": "session_started",
    "SessionEnd": "session_ended",
    "SubagentStart": "subagent_started",
    "SubagentStop": "subagent_stopped",
    "TaskCreated": "task_creation_requested",
    "StopFailure": "turn_failed",
    "Interrupt": "turn_interrupted",
    "TaskCompleted": "task_completion_requested",
}


def identifier(value):
    if not isinstance(value, str) or not value:
        return None
    return hashlib.sha256(value.encode("utf-8")).hexdigest()


def record(client, event):
    directory = os.environ.get("SONSU_WORK_LOG_DIR")
    if not directory:
        return
    if fcntl is None:
        raise OSError("work logging requires a POSIX file lock")
    if not isinstance(event, dict):
        raise ValueError("hook event must be an object")
    kind = EVENTS.get(event.get("hook_event_name"))
    if kind is None or client not in {"omp", "claude", "codex"}:
        return
    root = Path(directory)
    if not root.is_absolute():
        raise ValueError("SONSU_WORK_LOG_DIR must be absolute")
    root.mkdir(mode=0o700, parents=True, exist_ok=True)
    entry = {
        "version": 1,
        "time": datetime.datetime.now(datetime.timezone.utc).isoformat(),
        "client": client,
        "event": kind,
        "session": identifier(event.get("session_id")),
        "agent": identifier(event.get("agent_id")),
        "task": identifier(event.get("task_id")),
    }
    flags = os.O_WRONLY | os.O_CREAT | os.O_APPEND | getattr(os, "O_NOFOLLOW", 0)
    fd = os.open(root / "events.jsonl", flags, 0o600)
    try:
        info = os.fstat(fd)
        if not stat.S_ISREG(info.st_mode) or info.st_uid != os.getuid() or info.st_mode & 0o077:
            raise PermissionError("work log must be a private file owned by the current user")
        payload = (json.dumps(entry, separators=(",", ":")) + "\n").encode("utf-8")
        fcntl.flock(fd, fcntl.LOCK_EX)
        try:
            while payload:
                written = os.write(fd, payload)
                if written <= 0:
                    raise OSError("work log write failed")
                payload = payload[written:]
        finally:
            fcntl.flock(fd, fcntl.LOCK_UN)
    finally:
        os.close(fd)


def main():
    client = sys.argv[1] if len(sys.argv) > 1 else None
    try:
        if os.environ.get("SONSU_WORK_LOG_DIR"):
            record(client, json.load(sys.stdin))
    except (OSError, ValueError, TypeError) as error:
        print(f"work log unavailable: {error}", file=sys.stderr)
    finally:
        if client == "codex":
            print("{}")


if __name__ == "__main__":
    main()
