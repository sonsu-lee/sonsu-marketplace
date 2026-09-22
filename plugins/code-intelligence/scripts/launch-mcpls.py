#!/usr/bin/env python3
"""Launch an already-installed, exact-version mcpls without network bootstrap."""

from __future__ import annotations

import os
from pathlib import Path
import shutil
import subprocess
import sys

REQUIRED_VERSION = "0.6.0"


def fail(message: str) -> "NoReturn":
    print(f"code-intelligence: {message}", file=sys.stderr)
    raise SystemExit(2)


def main() -> None:
    try:
        workspace = Path.cwd().resolve(strict=True)
    except OSError as error:
        fail(f"cannot resolve session cwd: {error}")
    if not workspace.is_dir():
        fail(f"session cwd is not a directory: {workspace}")

    binary = shutil.which("mcpls")
    if binary is None:
        fail(f"mcpls {REQUIRED_VERSION} is required on PATH; no download was attempted")

    try:
        completed = subprocess.run(
            [binary, "--version"],
            check=False,
            capture_output=True,
            text=True,
            timeout=10,
        )
    except (OSError, subprocess.SubprocessError) as error:
        fail(f"could not query mcpls version: {error}")
    version_output = (completed.stdout or completed.stderr).strip()
    if completed.returncode != 0 or version_output != f"mcpls {REQUIRED_VERSION}":
        fail(
            f"expected mcpls {REQUIRED_VERSION}, got "
            f"{version_output or f'exit {completed.returncode}'}; no download was attempted"
        )

    plugin_root = Path(__file__).resolve().parents[1]
    config = (plugin_root / "config" / "mcpls.toml").resolve(strict=True)
    environment = os.environ.copy()
    environment.update(
        {
            "MCPLS_CONFIG": str(config),
            "MCPLS_TRUST_PROJECT_CONFIG": "false",
            "MCPLS_LOG": "warn",
            "MCPLS_LOG_JSON": "true",
        }
    )
    os.execve(binary, [binary], environment)


if __name__ == "__main__":
    main()
