#!/usr/bin/env python3
"""Fail-open hook adapter. Never writes a long-term memory or emits hook context."""

import json
import os
import signal
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "scripts"))
from memory_store import hook_skip_status, project_key, root_path, stage_hook  # noqa: E402

# Leave room for subprocess cleanup and diagnostics before the host's 5s limit.
HOOK_SECONDS = 3
HOOK_CLEANUP_SECONDS = 0.25
HOOK_WRITE = os.write


class HookTimeout(Exception):
    pass


def hook_timeout(signum, frame):
    raise HookTimeout()


def failure_message(capture_state, error):
    # Report observed commit state, never prompt text or an assumed rollback.
    if capture_state.get("committed"):
        if not capture_state.get("durable"):
            return "memory-manager: candidate staged; durability confirmation incomplete (" + type(error).__name__ + ")"
    elif capture_state.get("commit_started"):
        return "memory-manager: candidate commit outcome unconfirmed (" + type(error).__name__ + ")"
    else:
        return "memory-manager: capture hook unavailable (" + type(error).__name__ + ")"
    return None


def best_effort_hook_output(fd, text):
    try:
        os.set_blocking(fd, False)
        HOOK_WRITE(fd, text.encode("utf-8"))
    except OSError:
        pass


def main():
    capture_state = {}

    def cleanup_timeout(signum, frame):
        try:
            message = failure_message(capture_state, HookTimeout())
            if message:
                best_effort_hook_output(2, message + "\n")
        finally:
            # End this hook only. OS teardown releases fds/locks; private scratch
            # can remain when its unlink is stalled. Never delete a committed candidate.
            os._exit(0)

    def operation_timeout(signum, frame):
        signal.signal(signal.SIGALRM, cleanup_timeout)
        signal.setitimer(signal.ITIMER_REAL, HOOK_CLEANUP_SECONDS)
        hook_timeout(signum, frame)

    previous = signal.signal(signal.SIGALRM, operation_timeout)
    signal.setitimer(signal.ITIMER_REAL, HOOK_SECONDS)
    try:
        event = json.load(sys.stdin)
        if not isinstance(event, dict):
            return 0
        skipped = hook_skip_status(event)
        if skipped:
            if skipped == "sensitive_content":
                best_effort_hook_output(2, "memory-manager: candidate skipped (sensitive content)\n")
            return 0
        cwd = event.get("cwd")
        if not isinstance(cwd, str) or not cwd:
            return 0
        stage_hook(root_path(), project_key(cwd), event, capture_state=capture_state)
    except Exception as error:
        # A hook must not block the host. Keep the diagnostic free of prompt text.
        try:
            message = failure_message(capture_state, error)
            if message:
                best_effort_hook_output(2, message + "\n")
        except HookTimeout:
            pass
    finally:
        signal.setitimer(signal.ITIMER_REAL, 0)
        signal.signal(signal.SIGALRM, previous)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
