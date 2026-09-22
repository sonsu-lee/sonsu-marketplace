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

    def test_invalid_utf8_retains_input_digest(self) -> None:
        content = b"---\nname: Invalid\n---\n\xff"
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "DESIGN.md"
            path.write_bytes(content)
            run = self.run_command(path)
        self.assertEqual(run.returncode, 1, run.stderr)
        report = json.loads(run.stdout)
        self.assertEqual(report["status"], "failed")
        self.assertEqual(report["findings"][0]["rule"], "input")
        self.assertEqual(report.get("digest"), "sha256:" + hashlib.sha256(content).hexdigest())

    def test_missing_npm_is_blocked(self) -> None:
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
            subprocess.TimeoutExpired("node", 120),
        ]
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "DESIGN.md"
            path.write_text(VALID)
            for case in cases:
                with self.subTest(case=case), mock.patch.object(MODULE.subprocess, "run") as run:
                    run.side_effect = [subprocess.CompletedProcess([], 0, "{}", ""),
                                       subprocess.CompletedProcess([], 0, "", ""), case]
                    output = io.StringIO()
                    with contextlib.redirect_stdout(output):
                        self.assertEqual(MODULE.check_design_md(path), 2)
                    self.assertEqual(json.loads(output.getvalue())["status"], "blocked")
                    self.assertEqual(run.call_count, 3)

    def test_failed_install_never_runs_linter(self) -> None:
        import contextlib
        import io

        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "DESIGN.md"
            path.write_text(VALID)
            with mock.patch.object(MODULE.subprocess, "run", side_effect=[
                subprocess.CompletedProcess([], 0, "{}", ""),
                subprocess.CompletedProcess([], 1, "", "install failed"),
            ]) as run:
                output = io.StringIO()
                with contextlib.redirect_stdout(output):
                    self.assertEqual(MODULE.check_design_md(path), 2)
                self.assertEqual(json.loads(output.getvalue())["status"], "blocked")
                self.assertEqual(run.call_count, 2)

    def test_npm_config_failure_never_runs_linter(self) -> None:
        import contextlib
        import io

        cases = [
            subprocess.CompletedProcess([], 1, "", "npm config failed"),
            subprocess.CompletedProcess([], 0, "not JSON", ""),
            subprocess.CompletedProcess([], 0, "[]", ""),
        ]
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "DESIGN.md"
            path.write_text(VALID)
            for case in cases:
                with self.subTest(case=case), mock.patch.object(MODULE.subprocess, "run", return_value=case) as run:
                    output = io.StringIO()
                    with contextlib.redirect_stdout(output):
                        self.assertEqual(MODULE.check_design_md(path), 2)
                    self.assertEqual(json.loads(output.getvalue())["status"], "blocked")
                    self.assertEqual(run.call_count, 1)


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

    def test_same_version_local_package_cannot_replace_official_linter(self) -> None:
        for location in ("local", "workspace", "npx-cache"):
            with self.subTest(location=location), tempfile.TemporaryDirectory() as tmp:
                root = Path(tmp)
                installed = root / "node_modules/@google/design.md"
                if location == "npx-cache":
                    cache = root / "cache"
                    cache.mkdir()
                    actual_cache = Path(subprocess.check_output(
                        ["npm", "config", "get", "cache"], text=True, timeout=30).strip())
                    (cache / "_cacache").symlink_to(actual_cache / "_cacache", target_is_directory=True)
                    npx_hash = hashlib.sha512(b"@google/design.md@0.4.0").hexdigest()[:16]
                    installed = cache / "_npx" / npx_hash / "node_modules/@google/design.md"
                    (root / ".npmrc").write_text(f"cache={cache}\n")
                package = root / "packages/fake" if location == "workspace" else installed
                package.mkdir(parents=True)
                (package / "dist/linter").mkdir(parents=True)
                manifest = {"name": "fixture", "private": True,
                            "dependencies": {"@google/design.md": "0.4.0"}}
                if location == "workspace":
                    manifest["workspaces"] = ["packages/*"]
                    installed.parent.mkdir(parents=True)
                    installed.symlink_to(package, target_is_directory=True)
                (root / "package.json").write_text(json.dumps(manifest))
                if location == "npx-cache":
                    (installed.parents[2] / "package.json").write_text(json.dumps(manifest))
                (package / "package.json").write_text(json.dumps({
                    "name": "@google/design.md", "version": "0.4.0", "type": "module",
                    "bin": {"designmd": "./dist/index.js"},
                    "exports": {"./linter": {"import": "./dist/linter/index.js"}},
                }))
                (package / "dist/index.js").write_text("// fake CLI target\n")
                marker = root / "fake-linter-executed"
                (package / "dist/linter/index.js").write_text(
                    "import {writeFileSync} from 'node:fs';\n"
                    f"writeFileSync({json.dumps(str(marker))}, 'executed');\n"
                    "export function lint() { return {designSystem: {name:'Fake', "
                    "symbolTable:new Map([['spacing.zero',0]]), components:new Map()}, "
                    "findings:[], summary:{errors:0,warnings:0}}; }\n"
                )
                binaries = installed.parents[1] / ".bin"
                binaries.mkdir(parents=True)
                (binaries / "designmd").symlink_to(package / "dist/index.js")
                path = root / "DESIGN.md"
                path.write_text("## Overview\nMissing frontmatter\n")
                run = self.run_command(path, cwd=root)
                self.assertFalse(marker.exists(), "project-provided linter was executed")
                self.assertEqual(run.returncode, 1, run.stdout + run.stderr)
                report = json.loads(run.stdout)
                self.assertEqual(report["status"], "failed")
                self.assertIn("frontmatter", [f["rule"] for f in report["findings"]])

    def test_project_node_options_cannot_execute_code(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            (root / "package.json").write_text('{"name":"fixture","private":true}')
            marker = root / "node-options-executed"
            script = root / "injected.cjs"
            script.write_text(f"require('node:fs').writeFileSync({json.dumps(str(marker))}, 'executed');")
            (root / ".npmrc").write_text(f"node-options=--require={script}\n")
            path = root / "DESIGN.md"
            path.write_text(VALID)
            run = self.run_command(path, cwd=root)
            self.assertFalse(marker.exists(), "project node-options executed code")
            self.assertEqual(run.returncode, 0, run.stdout + run.stderr)
            self.assertEqual(json.loads(run.stdout)["status"], "passed")

    def test_array_proxy_and_ca_config_reaches_isolated_install(self) -> None:
        import contextlib
        import io

        run_subprocess = subprocess.run
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            (root / "package.json").write_text('{"name":"fixture","private":true}')
            ca = "-----BEGIN CERTIFICATE-----\nfixture\n-----END CERTIFICATE-----"
            (root / ".npmrc").write_text(
                'noproxy[]=internal.example\nnoproxy[]=registry.example\n'
                + "ca[]=" + json.dumps(ca) + '\ncert=fixture-cert\nkey=fixture-key\n'
            )
            path = root / "DESIGN.md"
            path.write_text(VALID)
            observed = {}

            def run(command, **kwargs):
                if command[:3] == ["npm", "config", "list"]:
                    return run_subprocess(command, cwd=root, **kwargs)
                if command[:2] == ["npm", "install"]:
                    config = run_subprocess(["npm", "config", "list", "--json"],
                                            cwd=kwargs["cwd"], env=kwargs["env"],
                                            text=True, capture_output=True, timeout=30)
                    self.assertEqual(config.returncode, 0, config.stderr)
                    observed.update(json.loads(config.stdout))
                    return subprocess.CompletedProcess(command, 0, "", "")
                return subprocess.CompletedProcess(command, 0, '{"status":"passed","findings":[]}', "")

            with mock.patch.object(MODULE.subprocess, "run", side_effect=run):
                with contextlib.redirect_stdout(io.StringIO()):
                    self.assertEqual(MODULE.check_design_md(path), 0)
            self.assertEqual(observed.get("noproxy"), ["internal.example", "registry.example"])
            self.assertEqual(observed.get("ca"), [ca])
            self.assertEqual(observed.get("cert"), "fixture-cert")
            self.assertEqual(observed.get("key"), "fixture-key")

    def test_custom_npm_user_config_path_is_preserved(self) -> None:
        import contextlib
        import io

        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "DESIGN.md"
            path.write_text(VALID)
            userconfig = Path(tmp) / "custom-user.npmrc"
            userconfig.write_text("//registry.npmjs.org/:_authToken=fixture-only\n")
            with mock.patch.dict(os.environ, {"NPM_CONFIG_USERCONFIG": str(userconfig)}), \
                    mock.patch.object(MODULE.subprocess, "run", side_effect=[
                        subprocess.CompletedProcess([], 0, "{}", ""),
                        subprocess.CompletedProcess([], 0, "", ""),
                        subprocess.CompletedProcess([], 0, '{"status":"passed","findings":[]}', ""),
                    ]) as run:
                with contextlib.redirect_stdout(io.StringIO()):
                    self.assertEqual(MODULE.check_design_md(path), 0)
            self.assertEqual(run.call_args_list[1].kwargs["env"]["NPM_CONFIG_USERCONFIG"], str(userconfig.resolve()))

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
