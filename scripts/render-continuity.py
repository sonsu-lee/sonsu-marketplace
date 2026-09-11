#!/usr/bin/env python3
"""Render self-contained continuity skills/helpers/hooks; --check never writes."""
import argparse
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SOURCE = ROOT / "shared/task-continuity"


def outputs():
    profiles = json.loads((SOURCE / "profiles.json").read_text())
    template = (SOURCE / "SKILL.md.tmpl").read_text()
    helper = (SOURCE / "task_continuity.py").read_bytes()
    for plugin, profile in profiles.items():
        root = ROOT / "plugins" / plugin
        skill = template
        for key, value in {"DESCRIPTION": json.dumps(profile["trigger"], ensure_ascii=False),
                           "LABEL": profile["label"], "PLUGIN": plugin,
                           "EXAMPLE_SKILL": profile["example_skill"], "DETAILS": profile["details"]}.items():
            skill = skill.replace("@@" + key + "@@", value)
        yield root / "skills/task-continuity/SKILL.md", skill.encode()
        yield root / "scripts/task-continuity.py", helper
        hooks = {"hooks": {"SessionStart": [{"matcher": "^(compact|resume)$", "hooks": [{
            "type": "command",
            "command": ('plugin_root="${CLAUDE_PLUGIN_ROOT:-${PLUGIN_ROOT:-}}" && '
                        'test -n "$plugin_root" && '
                        'python3 "$plugin_root/scripts/task-continuity.py" hook'),
            "timeout": 5, "additionalContextLimit": 600}]}]}}
        if plugin == "engineering":
            hooks["hooks"]["Stop"] = [{"hooks": [{
                "type": "command",
                "command": ('plugin_root="${CLAUDE_PLUGIN_ROOT:-${PLUGIN_ROOT:-}}" && '
                            'test -n "$plugin_root" && '
                            'python3 "$plugin_root/scripts/evidence-gates.py" hook'),
                "timeout": 10}]}]
        yield root / "hooks/hooks.json", (json.dumps(hooks, indent=2) + "\n").encode()


def main():
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("--check", action="store_true")
    args = p.parse_args()
    stale = []
    for target, data in outputs():
        if target.exists() and target.read_bytes() == data:
            continue
        stale.append(str(target.relative_to(ROOT)))
        if not args.check:
            target.parent.mkdir(parents=True, exist_ok=True)
            target.write_bytes(data)
    for target in stale:
        print(("stale: " if args.check else "rendered: ") + target)
    return int(args.check and bool(stale))


if __name__ == "__main__":
    raise SystemExit(main())
