#!/usr/bin/env python3
"""Fail-open hook adapter. Never writes a long-term memory or emits hook context."""

import json
import signal
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "scripts"))
from memory_store import hook_skip_status, project_key, root_path, stage_hook  # noqa: E402

# Leave room for subprocess cleanup and diagnostics before the host's 5s limit.
HOOK_SECONDS = 3


class HookTimeout(Exception):
    pass


def hook_timeout(signum, frame):
    raise HookTimeout()


def main():
    capture_state = {}
    previous = signal.signal(signal.SIGALRM, hook_timeout)
    signal.setitimer(signal.ITIMER_REAL, HOOK_SECONDS)
    try:
        event = json.load(sys.stdin)
        if not isinstance(event, dict):
            return 0
        skipped = hook_skip_status(event)
        if skipped:
            if skipped == "sensitive_content":
                print("memory-manager: candidate skipped (sensitive content)", file=sys.stderr)
            return 0
        cwd = event.get("cwd")
        if not isinstance(cwd, str) or not cwd:
            return 0
        stage_hook(root_path(), project_key(cwd), event, capture_state=capture_state)
    except Exception as error:
        # A hook must not block the host. Keep the diagnostic free of prompt text.
        if capture_state.get("committed"):
            if not capture_state.get("durable"):
                print("memory-manager: candidate staged; durability confirmation incomplete (" +
                      type(error).__name__ + ")", file=sys.stderr)
        elif capture_state.get("commit_started"):
            # The deadline can interrupt rename before its return value is known.
            print("memory-manager: candidate commit outcome unconfirmed (" +
                  type(error).__name__ + ")", file=sys.stderr)
        else:
            print("memory-manager: capture hook unavailable (" + type(error).__name__ + ")", file=sys.stderr)
    finally:
        signal.setitimer(signal.ITIMER_REAL, 0)
        signal.signal(signal.SIGALRM, previous)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
