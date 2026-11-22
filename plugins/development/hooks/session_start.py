#!/usr/bin/env python3
"""Provide local workflow guidance to supported session-start hooks."""

import json
import sys
from pathlib import Path


def main() -> None:
    event = json.load(sys.stdin)
    if event.get("agent_id"):
        return
    if event.get("source") not in {"startup", "clear", "compact"}:
        return
    skill = Path(__file__).resolve().parent.parent / "skills/working-on-tasks/SKILL.md"
    context = skill.read_text(encoding="utf-8")
    print(json.dumps({"hookSpecificOutput": {
        "hookEventName": "SessionStart",
        "additionalContext": context,
    }}))


if __name__ == "__main__":
    main()
