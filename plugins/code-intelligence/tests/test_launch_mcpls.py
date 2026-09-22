from __future__ import annotations

import json
import os
from pathlib import Path
import subprocess
import sys
import tempfile
import textwrap
import unittest


ROOT = Path(__file__).parents[1]
LAUNCHER = ROOT / "scripts" / "launch-mcpls.py"
CONFIG = (ROOT / "config" / "mcpls.toml").resolve()


class LaunchMcplsTest(unittest.TestCase):
    def make_mcpls(self, directory: Path, version: str) -> Path:
        executable = directory / "mcpls"
        executable.write_text(
            textwrap.dedent(
                f"""\
                #!/bin/sh
                if [ "$1" = "--version" ]; then
                  echo "mcpls {version}"
                  exit 0
                fi
                printf '{{"cwd":"%s","config":"%s","trust":"%s","log":"%s","json":"%s"}}\\n' \\
                  "$PWD" "$MCPLS_CONFIG" "$MCPLS_TRUST_PROJECT_CONFIG" "$MCPLS_LOG" "$MCPLS_LOG_JSON"
                """
            ),
            encoding="utf-8",
        )
        executable.chmod(0o755)
        return executable

    def run_launcher(self, workspace: Path, binary_dir: Path) -> subprocess.CompletedProcess[str]:
        environment = os.environ.copy()
        environment["PATH"] = os.pathsep.join([str(binary_dir), "/usr/bin", "/bin"])
        return subprocess.run(
            [sys.executable, str(LAUNCHER)],
            cwd=workspace,
            env=environment,
            capture_output=True,
            text=True,
            timeout=10,
            check=False,
        )

    def test_exact_version_execs_with_inherited_cwd_and_owned_config(self) -> None:
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            workspace = root / "workspace"
            binary_dir = root / "bin"
            workspace.mkdir()
            binary_dir.mkdir()
            self.make_mcpls(binary_dir, "0.6.0")
            completed = self.run_launcher(workspace, binary_dir)

        self.assertEqual(completed.returncode, 0, completed.stderr)
        self.assertEqual(
            json.loads(completed.stdout),
            {
                "cwd": str(workspace.resolve()),
                "config": str(CONFIG),
                "trust": "false",
                "log": "warn",
                "json": "true",
            },
        )

    def test_wrong_version_fails_without_running_server(self) -> None:
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            workspace = root / "workspace"
            binary_dir = root / "bin"
            workspace.mkdir()
            binary_dir.mkdir()
            self.make_mcpls(binary_dir, "0.6.1")
            completed = self.run_launcher(workspace, binary_dir)

        self.assertEqual(completed.returncode, 2)
        self.assertIn("expected mcpls 0.6.0", completed.stderr)
        self.assertIn("no download was attempted", completed.stderr)
        self.assertEqual(completed.stdout, "")

    def test_missing_binary_fails_without_download(self) -> None:
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            workspace = root / "workspace"
            binary_dir = root / "bin"
            workspace.mkdir()
            binary_dir.mkdir()
            completed = self.run_launcher(workspace, binary_dir)

        self.assertEqual(completed.returncode, 2)
        self.assertIn("mcpls 0.6.0 is required on PATH", completed.stderr)
        self.assertIn("no download was attempted", completed.stderr)


if __name__ == "__main__":
    unittest.main()
