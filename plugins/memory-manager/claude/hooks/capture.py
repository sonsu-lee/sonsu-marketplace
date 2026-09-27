#!/usr/bin/env python3
"""Fail-open hook adapter. Never writes a long-term memory or emits hook context."""

import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "scripts"))
from memory_store import project_key, root_path, stage_hook  # noqa: E402


def main():
    try:
        event = json.load(sys.stdin)
        if not isinstance(event, dict):
            return 0
        cwd = event.get("cwd")
        if not isinstance(cwd, str) or not cwd:
            return 0
        result = stage_hook(root_path(), project_key(cwd), event)
        if result.get("status") == "sensitive_content":
            print("memory-manager: candidate skipped (sensitive content)", file=sys.stderr)
    except Exception as error:
        # A hook must not block the host. Keep the diagnostic free of prompt text.
        print("memory-manager: capture hook unavailable (" + type(error).__name__ + ")", file=sys.stderr)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
