#!/usr/bin/env python3
"""Request host confirmation for recognized sensitive tool actions."""

from __future__ import annotations

import json
import os
import re
import sys
from pathlib import Path

sys.dont_write_bytecode = True

from evidence import gate_event


POLICY = json.loads((Path(__file__).parent / "policy.json").read_text(encoding="utf-8"))
SHELL_PATTERNS = [re.compile(pattern, re.IGNORECASE) for pattern in POLICY["shellPatterns"]]
REMOTE_MUTATION = re.compile(POLICY["remoteMutationPattern"], re.IGNORECASE)


def reason_for(event: dict) -> str | None:
    name = str(event.get("tool_name", ""))
    data = event.get("tool_input")
    data = data if isinstance(data, dict) else {}
    if REMOTE_MUTATION.search(name):
        return "Remote mutation requires explicit approval."
    if name.lower() in {"bash", "shell", "exec_command"}:
        command = data.get("command", "")
        if isinstance(command, str) and any(p.search(command) for p in SHELL_PATTERNS):
            return "Commit, publication, merge, deployment, or destructive action requires explicit approval."
    if name.lower() in {"write", "edit", "notebookedit", "apply_patch"}:
        paths = [data.get("file_path") or data.get("path") or data.get("notebook_path")]
        patch = data.get("command") or data.get("input")
        if isinstance(patch, str):
            paths.extend(re.findall(r"^\*\*\* (?:(?:Add|Update|Delete) File|Move to): (.+)$", patch, re.MULTILINE))
        root = Path(event.get("cwd") or os.getcwd()).resolve()
        for path in paths:
            if not isinstance(path, str):
                continue
            if REMOTE_MUTATION.search(path) or re.match(r"^(ssh|cfg|issue|pr)://", path, re.IGNORECASE):
                return "Remote mutation requires explicit approval."
            target = Path(path).expanduser()
            if "://" not in path and not (root / target).resolve().is_relative_to(root):
                return "A write outside the current workspace requires explicit approval."
    return None


def main() -> None:
    event = json.load(sys.stdin)
    reason = reason_for(event)
    if not reason:
        return
    # Codex は PreToolUse で確認できないため、証拠の有無に関係なく拒否する。
    decision = "deny"
    if sys.argv[1:] == ["--client", "claude"]:
        evidence = gate_event(event)
        if evidence["state"] == "blocked":
            reason = evidence["reason"]
        else:
            decision = "ask"
            if evidence["state"] == "pass":
                reason += f" Verified tree {evidence['tree']}; checks: {json.dumps(evidence['checks'])}."
            elif evidence["state"] == "unverified":
                reason += f" {evidence['reason']}"
    else:
        reason += " This client cannot prompt from this hook. Do not retry through another tool or command; only the user can perform the action separately."
    print(json.dumps({"hookSpecificOutput": {
        "hookEventName": "PreToolUse",
        "permissionDecision": decision,
        "permissionDecisionReason": reason,
    }}))


if __name__ == "__main__":
    main()
