from __future__ import annotations

import hashlib
import importlib.util
import json
import os
import shutil
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest
from unittest import mock


ROOT = Path(__file__).resolve().parents[2]
VALIDATOR = ROOT / "shared/design-quality/validate_design_quality.py"
SPEC = importlib.util.spec_from_file_location("design_quality", VALIDATOR)
MODULE = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(MODULE)
VALID = """---
name: Example
colors:
  primary: "#111111"
  on-primary: "#ffffff"
typography:
  body:
    fontFamily: sans-serif
    fontSize: 16px
spacing:
  md: 16px
rounded:
  sm: 4px
components:
  button:
    backgroundColor: "{colors.primary}"
    textColor: "{colors.on-primary}"
---
## Overview
Example design for tests.
## Colors
Paired foreground and background.
## Typography
Body text.
## Layout
Use spacing tokens.
## Elevation & Depth
No elevation.
"""


class DesignMdCommandTests(unittest.TestCase):
    def run_command(self, path: Path, **kwargs: object) -> subprocess.CompletedProcess:
        return subprocess.run(
            [sys.executable, str(VALIDATOR), "design-md", str(path)],
            capture_output=True, text=True, timeout=150, **kwargs,
        )

    def test_missing_file_returns_json_failure(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            run = self.run_command(Path(tmp) / "missing.md")
        self.assertEqual(run.returncode, 1, run.stderr)
        report = json.loads(run.stdout)
        self.assertEqual(report["status"], "failed")
        self.assertEqual(report["findings"][0]["rule"], "input")

    def test_missing_npx_is_blocked(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "DESIGN.md"
            path.write_text(VALID)
            run = self.run_command(path, env={**os.environ, "PATH": tmp})
        self.assertEqual(run.returncode, 2, run.stderr)
        self.assertEqual(json.loads(run.stdout)["status"], "blocked")

    def test_runtime_failure_and_corrupt_output_never_pass(self) -> None:
        import contextlib
        import io

        cases = [
            subprocess.CompletedProcess([], 1, "", "npm failed"),
            subprocess.CompletedProcess([], 0, "not JSON", ""),
            subprocess.CompletedProcess([], 0, '{"status":"passed"}', ""),
            subprocess.CompletedProcess([], 1, '{"status":"passed","findings":[]}', ""),
            subprocess.TimeoutExpired("npx", 120),
        ]
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "DESIGN.md"
            path.write_text(VALID)
            for case in cases:
                with self.subTest(case=case), mock.patch.object(MODULE.subprocess, "run") as run:
                    if isinstance(case, Exception):
                        run.side_effect = case
                    else:
                        run.return_value = case
                    output = io.StringIO()
                    with contextlib.redirect_stdout(output):
                        self.assertEqual(MODULE.check_design_md(path), 2)
                    self.assertEqual(json.loads(output.getvalue())["status"], "blocked")


@unittest.skipUnless(os.environ.get("DESIGN_MD_INTEGRATION") == "1",
                     "set DESIGN_MD_INTEGRATION=1 to run the pinned npm package")
class DesignMdIntegrationTests(DesignMdCommandTests):
    def check_document(self, content: str, status: str, exit_code: int,
                       rule: str | None = None, validator: Path = VALIDATOR) -> dict:
        with tempfile.TemporaryDirectory() as tmp:
            # Spaces and shell punctuation must be treated as a literal path.
            path = Path(tmp) / "design $(literal).md"
            path.write_text(content, encoding="utf-8")
            run = subprocess.run(
                [sys.executable, str(validator), "design-md", str(path)],
                text=True, capture_output=True, timeout=150,
            )
            self.assertEqual(path.read_text(), content)
        self.assertEqual(run.returncode, exit_code, run.stderr + run.stdout)
        report = json.loads(run.stdout)
        self.assertEqual(report["status"], status)
        self.assertEqual(report["package"], "@google/design.md@0.4.0")
        self.assertEqual(report["digest"], "sha256:" + hashlib.sha256(content.encode()).hexdigest())
        if rule:
            self.assertIn(rule, [f["rule"] for f in report["findings"]])
        return report

    def test_valid_and_official_aliases_pass(self) -> None:
        self.check_document(VALID, "passed", 0)
        self.check_document(VALID.replace("## Overview", "## Brand & Style")
                            .replace("## Layout", "## Layout & Spacing")
                            .replace("## Elevation & Depth", "## Elevation"), "passed", 0)

    def test_structural_failures_block_even_when_upstream_only_warns(self) -> None:
        for text, rule in [
            ("## Overview\nNo YAML", "frontmatter"),
            (VALID.replace("name: Example", "name: [unfinished"), "parse"),
            (VALID.replace("name: Example\n", ""), "name"),
            (VALID.replace("name: Example", "name: 123"), "name"),
            ("---\nname: Empty\n---\n## Overview\nEmpty tokens", "tokens"),
            (VALID.replace("{colors.primary}", "{colors.missing}"), "broken-ref"),
            (VALID.replace("## Overview", "## Typography").replace("## Typography\nBody", "## Overview\nBody"), "section-order"),
            (VALID.replace("colors:\n", "colours:\n"), "unknown-key"),
        ]:
            with self.subTest(rule=rule, text=text[:50]):
                self.check_document(text, "failed", 1, rule)

    def test_fenced_yaml_cannot_supply_required_frontmatter_tokens(self) -> None:
        document = "---\nname: Empty\n---\n```yaml\nspacing:\n  md: 16px\n```\n"
        self.check_document(document, "failed", 1, "tokens")

    def test_empty_token_definitions_do_not_satisfy_required_tokens(self) -> None:
        for group in ("typography", "components"):
            with self.subTest(group=group):
                self.check_document(f"---\nname: Empty\n{group}:\n  empty: {{}}\n---\n",
                                    "failed", 1, "tokens")

    def test_numeric_spacing_is_a_token(self) -> None:
        self.check_document("---\nname: Spacing\nspacing:\n  zero: 0\n---\n## Layout\nSpacing.\n",
                            "passed", 0)

    def test_standalone_missing_and_circular_references_fail(self) -> None:
        for group in ("colors", "spacing", "rounded"):
            for tokens in (f'  primary: "{{{group}.missing}}"',
                           f'  primary: "{{{group}.other}}"\n  other: "{{{group}.primary}}"'):
                with self.subTest(group=group, tokens=tokens):
                    self.check_document(f"---\nname: Broken\n{group}:\n{tokens}\n---\n",
                                        "failed", 1, "broken-ref")

    def test_reference_to_numeric_spacing_passes(self) -> None:
        self.check_document('---\nname: Spacing\nspacing:\n  zero: 0\n  alias: "{spacing.zero}"\n---\n',
                            "passed", 0)

    def test_caller_npm_project_config_is_preserved(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            (root / "package.json").write_text('{"name":"fixture","private":true}')
            (root / ".npmrc").write_text(f"offline=true\ncache={root / 'empty-cache'}\n")
            path = root / "DESIGN.md"
            path.write_text(VALID)
            env = {key: value for key, value in os.environ.items()
                   if key.lower() not in {"npm_config_cache", "npm_config_offline"}}
            run = self.run_command(path, cwd=root, env=env)
            # The project's empty, offline cache must block installation even if
            # the default npm cache already contains the pinned package.
            self.assertEqual(run.returncode, 2, run.stdout + run.stderr)
            self.assertEqual(json.loads(run.stdout)["status"], "blocked")

    def test_contrast_warning_requires_context_review(self) -> None:
        self.check_document(VALID.replace("#111111", "#eeeeee"), "needs_review", 3, "contrast-ratio")

    def test_each_generated_plugin_runs_in_isolation(self) -> None:
        for plugin in ("interface-design", "operations-ui", "figma-workflow"):
            with self.subTest(plugin=plugin), tempfile.TemporaryDirectory() as tmp:
                source = ROOT / "plugins" / plugin
                for directory in ("scripts", "assets"):
                    shutil.copytree(source / directory, Path(tmp) / directory)
                self.check_document(VALID, "passed", 0,
                                    validator=Path(tmp) / "scripts/validate_design_quality.py")


if __name__ == "__main__":
    unittest.main()
