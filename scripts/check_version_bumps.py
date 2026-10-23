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


def main() -> int:
    if len(sys.argv) != 2:
        print("usage: check_version_bumps.py <base revision>")
        return 2
    base = sys.argv[1]
    diff = git("diff", "--name-only", base, "HEAD")
    if diff.returncode != 0:
        print(f"cannot diff against {base}: {diff.stderr.strip()}")
        return 2
    changed = diff.stdout.splitlines()
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
        if before == after:
            print(f"FAIL  {plugin}: files changed but version is still {after}")
            failed = True
        else:
            print(f"PASS  {plugin}: {before} -> {after}")
    if not failed and not any(path.startswith("plugins/") for path in changed):
        print("no plugin changed")
    return 1 if failed else 0


if __name__ == "__main__":
    sys.exit(main())
