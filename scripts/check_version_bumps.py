#!/usr/bin/env python3
"""Fail when a plugin changed since a base revision without a version bump.

`AGENTS.md` requires raising a plugin's version with every change to it.
`check_plugins.py` already checks that the manifests and catalogs agree, so
comparing the root `plugin.json` with the base revision is enough here. A
plugin that does not exist at the base is new and needs no bump.
"""

from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path

import check_plugins as cp

ROOT = Path(__file__).resolve().parents[1]


def git(*args: str) -> subprocess.CompletedProcess[str]:
    return subprocess.run(["git", *args], cwd=ROOT, capture_output=True, text=True)


def newer(after: str, before: str) -> bool:
    """Whether a dotted numeric version is higher; other forms only must differ."""
    try:
        return tuple(map(int, after.split("."))) > tuple(map(int, before.split(".")))
    except (AttributeError, ValueError):
        return after != before


def main() -> int:
    if len(sys.argv) != 2:
        print("usage: check_version_bumps.py <base revision>")
        return 2
    base = sys.argv[1]
    # Without renames, a file moved out of a plugin still lists its old path;
    # -z keeps unusual names unquoted.
    diff = git("diff", "--no-renames", "--name-only", "-z", base, "HEAD")
    if diff.returncode != 0:
        print(f"cannot diff against {base}: {diff.stderr.strip()}")
        return 2
    changed = [path for path in diff.stdout.split("\0") if path]
    plugins = cp.load_marketplace(ROOT)[1]
    failed = False
    for plugin in plugins:
        prefix = f"plugins/{plugin}/"
        if not any(path.startswith(prefix) for path in changed):
            continue
        old = git("show", f"{base}:{prefix}plugin.json")
        if old.returncode != 0:
            print(f"PASS  {plugin}: new plugin")
            continue
        before = json.loads(old.stdout).get("version")
        after = json.loads((ROOT / prefix / "plugin.json").read_text()).get("version")
        if not newer(after, before):
            print(f"FAIL  {plugin}: files changed but version {before} -> {after} is not higher")
            failed = True
        else:
            print(f"PASS  {plugin}: {before} -> {after}")
    if not failed and not any(path.startswith("plugins/") for path in changed):
        print("no plugin changed")
    return 1 if failed else 0


if __name__ == "__main__":
    sys.exit(main())
