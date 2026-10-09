"""Codex and Claude Code marketplace packaging contracts."""
import json
import contextlib
import importlib.util
import io
import os
from pathlib import Path
import re
import shutil
import subprocess
import sys
import tempfile
import unittest
from unittest import mock
import xml.etree.ElementTree as ET


ROOT = Path(__file__).resolve().parents[2]
CATALOG = ROOT / ".agents/plugins/marketplace.json"
CLAUDE_ROOT_PACKAGES = {"memory-manager", "worklog"}


def read_skill_name(path):
    lines = path.read_text(encoding="utf-8").splitlines()
    if not lines or lines[0] != "---":
        raise AssertionError(f"{path} has no frontmatter")
    for line in lines[1:]:
        if line == "---":
            break
        key, separator, value = line.partition(":")
        if key == "name" and separator:
            return value.strip().strip("\"'")
    raise AssertionError(f"{path} has no skill name")


class CodexPackagingTests(unittest.TestCase):
    def test_claude_catalog_matches_codex_and_generated_manifests(self):
        codex = json.loads(CATALOG.read_text(encoding="utf-8"))
        claude = json.loads((ROOT / ".claude-plugin/marketplace.json").read_text(encoding="utf-8"))
        self.assertEqual(claude["name"], codex["name"])
        self.assertEqual([entry["name"] for entry in claude["plugins"]],
                         [entry["name"] for entry in codex["plugins"]])
        for entry in claude["plugins"]:
            with self.subTest(plugin=entry["name"]):
                expected = entry["name"] + ("/claude" if entry["name"] in CLAUDE_ROOT_PACKAGES else "")
                self.assertEqual(entry["source"], f"./plugins/{expected}")
                package = ROOT / "plugins" / expected
                source = json.loads((ROOT / "plugins" / entry["name"] / ".codex-plugin/plugin.json").read_text(encoding="utf-8"))
                generated = json.loads((package / ".claude-plugin/plugin.json").read_text(encoding="utf-8"))
                self.assertEqual(generated["name"], source["name"])
                self.assertEqual(generated["version"], source["version"])
                self.assertEqual(entry["version"], source["version"])
                self.assertTrue((package / "skills").is_dir())

    def test_memory_manager_host_specific_invocation_policy(self):
        for name in ("memory-recall", "memory-capture", "memory-maintain", "memory-promote"):
            with self.subTest(skill=name):
                source = ROOT / "plugins/memory-manager/skills" / name / "SKILL.md"
                generated = ROOT / "plugins/memory-manager/claude/skills" / name / "SKILL.md"
                codex = source.read_text(encoding="utf-8")
                claude = generated.read_text(encoding="utf-8")
                self.assertNotIn("disable-model-invocation:", codex)
                if name in ("memory-maintain", "memory-promote"):
                    codex = codex.replace("\n---\n", "\ndisable-model-invocation: true\n---\n", 1)
                self.assertEqual(claude, codex)
                self.assertEqual(read_skill_name(generated), name)
        self.assertFalse((ROOT / "plugins/memory-manager/claude/skills/memory-manager").exists())
        self.assertFalse((ROOT / "plugins/memory-manager-claude").exists())
        manifest = json.loads((ROOT / "plugins/memory-manager/.codex-plugin/plugin.json").read_text())
        self.assertEqual(manifest["skills"], "./skills/")
        for relative in ("scripts/memory_store.py", "hooks/capture.py", "hooks/hooks.json"):
            self.assertEqual((ROOT / "plugins/memory-manager" / relative).read_bytes(),
                             (ROOT / "plugins/memory-manager/claude" / relative).read_bytes())

    def test_worklog_claude_root_copies_host_hooks(self):
        package = ROOT / "plugins/worklog"
        for source, generated in (("hooks/claude-hooks.json", "claude/hooks/hooks.json"),
                                  ("scripts/worklog.py", "claude/scripts/worklog.py")):
            with self.subTest(file=generated):
                self.assertEqual((package / generated).read_bytes(), (package / source).read_bytes())
        self.assertFalse((package / ".claude-plugin").exists())
        skill = package / "claude/skills/worklog-diagnose/SKILL.md"
        self.assertEqual(skill.read_bytes(), (package / "skills/worklog-diagnose/SKILL.md").read_bytes())

    def test_memory_manager_readme_links_diagrams_and_entrypoints(self):
        package = ROOT / "plugins/memory-manager"
        readme = (package / "README.md").read_text(encoding="utf-8")
        for target in re.findall(r"!?\[[^]]+\]\(([^)]+)\)", readme):
            if target.startswith(("http://", "https://")):
                continue
            with self.subTest(link=target):
                self.assertTrue((package / target).is_file())
        for name in ("memory-architecture", "memory-lifecycle"):
            self.assertTrue((package / "assets" / (name + ".drawio.png")).read_bytes().startswith(b"\x89PNG\r\n\x1a\n"))
            ET.parse(package / "assets" / (name + ".drawio"))

    def test_generated_claude_hook_stages_only_candidate(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory).resolve()
            project = root / "project"
            project.mkdir()
            package = ROOT / "plugins/memory-manager/claude"
            env = os.environ.copy()
            env["SONSU_MEMORY_HOME"] = str(root / "memory")
            store = package / "scripts/memory_store.py"
            hook = package / "hooks/capture.py"
            subprocess.run([sys.executable, str(store), "capture", "on", "--cwd", str(project)],
                           check=True, env=env, capture_output=True)
            event = {"hook_event_name": "UserPromptSubmit", "cwd": str(project),
                     "prompt": "기억해 줘: 검증 후 저장할 후보"}
            called = subprocess.run([sys.executable, "-B", str(hook)], input=json.dumps(event),
                                    text=True, capture_output=True, env=env)
            self.assertEqual(called.returncode, 0)
            self.assertEqual(called.stdout, "")
            pending = subprocess.run([sys.executable, str(store), "pending", "--cwd", str(project)],
                                     check=True, env=env, capture_output=True, text=True)
            self.assertEqual(len(json.loads(pending.stdout)["results"]), 1)
            self.assertFalse((root / "memory/notes").exists())

    def test_hook_packages_use_default_discovery_path(self):
        catalog = json.loads(CATALOG.read_text(encoding="utf-8"))
        for entry in catalog["plugins"]:
            package = ROOT / "plugins" / entry["name"]
            hook_file = package / "hooks/hooks.json"
            if not hook_file.is_file():
                continue
            with self.subTest(plugin=entry["name"]):
                codex = json.loads((package / ".codex-plugin/plugin.json").read_text(encoding="utf-8"))
                claude_package = package / "claude" if entry["name"] in CLAUDE_ROOT_PACKAGES else package
                claude = json.loads((claude_package / ".claude-plugin/plugin.json").read_text(encoding="utf-8"))
                self.assertNotIn("hooks", codex)
                self.assertNotIn("hooks", claude)
                self.assertIn("hooks", json.loads(hook_file.read_text(encoding="utf-8")))

    def test_public_skill_names_match_directories(self):
        catalog = json.loads(CATALOG.read_text(encoding="utf-8"))
        for entry in catalog["plugins"]:
            package = ROOT / "plugins" / entry["name"]
            manifest = json.loads((package / ".codex-plugin/plugin.json").read_text())
            root = package / manifest["skills"]
            for skill_path in sorted(root.glob("*/SKILL.md")):
                with self.subTest(plugin=entry["name"], skill=skill_path.parent.name):
                    self.assertEqual(read_skill_name(skill_path), skill_path.parent.name)

    def test_catalog_entries_reference_matching_plugin_manifests(self):
        catalog = json.loads(CATALOG.read_text(encoding="utf-8"))
        names = set()

        for entry in catalog["plugins"]:
            with self.subTest(plugin=entry["name"]):
                self.assertNotIn(entry["name"], names)
                names.add(entry["name"])
                self.assertEqual(entry["source"]["source"], "local")
                self.assertEqual(entry["source"]["path"], f"./plugins/{entry['name']}")

                manifest_path = ROOT / "plugins" / entry["name"] / ".codex-plugin/plugin.json"
                manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
                self.assertEqual(manifest["name"], entry["name"])

    def test_declared_package_paths_stay_inside_each_plugin(self):
        catalog = json.loads(CATALOG.read_text(encoding="utf-8"))

        for entry in catalog["plugins"]:
            package_root = (ROOT / "plugins" / entry["name"]).resolve()
            manifest = json.loads(
                (package_root / ".codex-plugin/plugin.json").read_text(encoding="utf-8")
            )
            for field in ("skills", "hooks", "apps"):
                if field not in manifest:
                    continue
                with self.subTest(plugin=entry["name"], field=field):
                    target = (package_root / manifest[field]).resolve()
                    self.assertTrue(target.is_relative_to(package_root))
                    self.assertTrue(target.exists())

    def test_output_parent_symlink_cannot_overwrite_codex_manifest(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            (root / ".agents/plugins").mkdir(parents=True)
            plugin = root / "plugins/demo"
            (plugin / ".codex-plugin").mkdir(parents=True)
            (plugin / ".claude-plugin").symlink_to(".codex-plugin", target_is_directory=True)
            (root / ".agents/plugins/marketplace.json").write_text(json.dumps({
                "name": "fixture-marketplace",
                "plugins": [{"name": "demo", "source": {"source": "local", "path": "./plugins/demo"}}],
            }))
            codex_manifest = plugin / ".codex-plugin/plugin.json"
            codex_manifest.write_text(json.dumps({"name": "demo", "version": "1.0.0"}))
            original = codex_manifest.read_bytes()

            result = subprocess.run(
                [sys.executable, str(ROOT / "scripts/render-claude-compat.py"), "--root", str(root)],
                capture_output=True,
                text=True,
            )

            self.assertNotEqual(result.returncode, 0, result.stdout)
            self.assertEqual(codex_manifest.read_bytes(), original)

    def test_memory_manager_removed_generated_file_fails_check_and_is_removed(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            (root / ".agents/plugins").mkdir(parents=True)
            (root / ".agents/plugins/marketplace.json").write_text(json.dumps({
                "name": "fixture", "plugins": [{"name": "memory-manager",
                "source": {"source": "local", "path": "./plugins/memory-manager"}}],
            }))
            shutil.copytree(ROOT / "plugins/memory-manager", root / "plugins/memory-manager")
            command = [sys.executable, str(ROOT / "scripts/render-claude-compat.py"), "--root", str(root)]
            self.assertEqual(subprocess.run(command, capture_output=True).returncode, 0)
            cache = root / "plugins/memory-manager/claude/scripts/__pycache__"
            cache.mkdir()
            (cache / "memory_store.cpython-39.pyc").write_bytes(b"runtime cache")
            self.assertEqual(subprocess.run(command + ["--check"], capture_output=True).returncode, 0)
            obsolete = root / "plugins/memory-manager/claude/skills/old-memory/SKILL.md"
            obsolete.parent.mkdir()
            obsolete.write_text("obsolete")
            checked = subprocess.run(command + ["--check"], capture_output=True, text=True)
            self.assertEqual(checked.returncode, 1)
            self.assertIn("obsolete:", checked.stdout)
            self.assertEqual(subprocess.run(command, capture_output=True).returncode, 0)
            self.assertFalse(obsolete.exists())

    def test_removed_memory_manager_cleans_nested_claude_manifest(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            catalog_path = root / ".agents/plugins/marketplace.json"
            catalog_path.parent.mkdir(parents=True)
            memory_entry = {"name": "memory-manager", "source": {
                "source": "local", "path": "./plugins/memory-manager"}}
            demo_entry = {"name": "demo", "source": {"source": "local", "path": "./plugins/demo"}}
            catalog_path.write_text(json.dumps({
                "name": "fixture", "plugins": [memory_entry, demo_entry]}))
            shutil.copytree(ROOT / "plugins/memory-manager", root / "plugins/memory-manager")
            demo_manifest = root / "plugins/demo/.codex-plugin/plugin.json"
            demo_manifest.parent.mkdir(parents=True)
            demo_manifest.write_text(json.dumps({"name": "demo", "version": "1.0.0"}))
            command = [sys.executable, str(ROOT / "scripts/render-claude-compat.py"), "--root", str(root)]
            self.assertEqual(subprocess.run(command, capture_output=True).returncode, 0)
            generated_manifest = root / "plugins/memory-manager/claude/.claude-plugin/plugin.json"
            self.assertTrue(generated_manifest.is_file())

            catalog_path.write_text(json.dumps({"name": "fixture", "plugins": [demo_entry]}))
            checked = subprocess.run(command + ["--check"], capture_output=True, text=True)
            self.assertEqual(checked.returncode, 1)
            self.assertIn("obsolete: plugins/memory-manager/claude/.claude-plugin/plugin.json", checked.stdout)
            self.assertEqual(subprocess.run(command, capture_output=True).returncode, 0)
            self.assertFalse(generated_manifest.exists())
            self.assertEqual(subprocess.run(command + ["--check"], capture_output=True).returncode, 0)

    def test_omp_catalog_exposes_default_six_and_optin_worklog(self):
        codex = json.loads(CATALOG.read_text(encoding="utf-8"))
        omp = json.loads((ROOT / ".omp-plugin/marketplace.json").read_text(encoding="utf-8"))
        self.assertEqual(omp["name"], codex["name"])
        self.assertEqual([entry["name"] for entry in omp["plugins"]],
                         ["workflow", "fluent-korean", "fluent-english", "fluent-japanese", "design", "career", "worklog"])
        for entry in omp["plugins"]:
            with self.subTest(plugin=entry["name"]):
                suffix = "/omp" if entry["name"] in ("workflow", "design", "fluent-korean", "worklog") else ""
                self.assertEqual(entry["source"], f"./plugins/{entry['name']}{suffix}")
                package = ROOT / entry["source"]
                manifest = json.loads((package / ".claude-plugin/plugin.json").read_text())
                self.assertEqual(manifest["name"], entry["name"])
                self.assertEqual(manifest["version"], entry["version"])
                self.assertTrue((package / "skills").is_dir())
                if entry["name"] == "worklog":
                    runtime = json.loads((package / "package.json").read_text())
                    self.assertEqual(runtime["omp"]["extensions"], ["./extension/worklog.ts"])
                    self.assertTrue((package / "extension/worklog.ts").is_file())
                    self.assertFalse((package / "hooks").exists())
                    continue
                for forbidden in ("hooks", "extension.ts", "omp/extension.ts",
                                  "scripts/task-continuity.py", "scripts/evidence-gates.py"):
                    self.assertFalse((package / forbidden).exists(), forbidden)

    def test_omp_isolated_skills_resolve_local_resources(self):
        for name in ("workflow", "design", "fluent-korean", "worklog"):
            package = ROOT / "plugins" / name / "omp"
            with tempfile.TemporaryDirectory() as directory:
                installed = Path(directory).resolve() / name
                shutil.copytree(package, installed)
                for subtree in ("skills", "references"):
                    for document in (installed / subtree).rglob("*.md"):
                        prose = re.sub(r"(?ms)^```[^\n]*\n.*?^```\s*$|`[^`\n]+`", "", document.read_text())
                        for target in re.findall(r"!?\[[^]]+\]\(([^)]+)\)", prose):
                            target = target.split("#", 1)[0]
                            if not target or re.match(r"[a-zA-Z][a-zA-Z0-9+.-]*:", target):
                                continue
                            with self.subTest(document=document.relative_to(installed), link=target):
                                resolved = (document.parent / target).resolve()
                                self.assertTrue(resolved.is_relative_to(installed))
                                self.assertTrue(resolved.exists())
                if name == "design":
                    for script in ("scripts/design_md.mjs", "scripts/validate_design_quality.py",
                                   "scripts/validate_operations_contracts.py",
                                   "figma-plugin/package.json", "references/migration.md"):
                        self.assertTrue((installed / script).is_file())
                    companion = json.loads((installed / "figma-plugin/manifest.json").read_text())
                    self.assertTrue((installed / "figma-plugin/src").is_dir())
                    self.assertIn("main", companion)

    def omp_fixture(self, root):
        names = ("workflow", "fluent-korean", "fluent-english", "fluent-japanese", "design", "career")
        catalog_path = root / ".agents/plugins/marketplace.json"
        catalog_path.parent.mkdir(parents=True)
        catalog_path.write_text(json.dumps({"name": "fixture", "plugins": [
            {"name": name, "source": {"source": "local", "path": f"./plugins/{name}"}} for name in names]}))
        for name in names:
            manifest = root / f"plugins/{name}/.codex-plugin/plugin.json"
            manifest.parent.mkdir(parents=True)
            manifest.write_text(json.dumps({"name": name, "version": "1.0.0"}))
        for name in ("workflow", "design"):
            plugin = root / "plugins" / name
            skill = plugin / "skills/example/SKILL.md"
            skill.parent.mkdir(parents=True)
            skill.write_text("---\nname: example\n---\n")
            for relative in ("hooks/hooks.json", "scripts/task-continuity.py", "scripts/evidence-gates.py"):
                path = plugin / relative
                path.parent.mkdir(parents=True, exist_ok=True)
                path.write_text("legacy runtime")
            executable = plugin / "scripts/tool.py"
            executable.write_text("#!/usr/bin/env python3\nprint('ok')\n")
            executable.chmod(0o755)
        korean = root / "plugins/fluent-korean"
        for subtree in ("codex", "skills", "agents"):
            shutil.copytree(ROOT / "plugins/fluent-korean" / subtree, korean / subtree)
        shutil.copytree(ROOT / "plugins/fluent-korean/.claude-plugin", korean / ".claude-plugin")
        for name in ("verify_change_rate.py", "console.py"):
            target = korean / "scripts" / name
            target.parent.mkdir(exist_ok=True)
            shutil.copyfile(ROOT / "plugins/fluent-korean/scripts" / name, target)
        shutil.copyfile(ROOT / "plugins/fluent-korean/UPSTREAM.md", korean / "UPSTREAM.md")
        source = root / "shared/omp-runtime"
        source.mkdir(parents=True)
        for name in ("continuity.md", "migration.md"):
            shutil.copyfile(ROOT / "shared/omp-runtime" / name, source / name)
        return [sys.executable, str(ROOT / "scripts/render-omp-compat.py"), "--root", str(root)]

    def run_renderer(self, command, expected=0):
        result = subprocess.run(command, capture_output=True, text=True)
        self.assertEqual(result.returncode, expected, result.stdout + result.stderr)
        return result

    def test_omp_korean_standalone_single_call_preserves_sources_and_rules(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            command = self.omp_fixture(root)
            korean = root / "plugins/fluent-korean"
            originals = {path: path.read_bytes() for path in korean.rglob("*") if path.is_file()}
            self.run_renderer(command)
            entry = next(entry for entry in json.loads((root / ".omp-plugin/marketplace.json").read_text())["plugins"]
                         if entry["name"] == "fluent-korean")
            self.assertEqual(entry["source"], "./plugins/fluent-korean/omp")
            installed = root.resolve() / "installed-korean"
            shutil.copytree(root / entry["source"], installed)
            skill = installed / "skills/fluent-korean/SKILL.md"
            text = skill.read_text()
            self.assertEqual(read_skill_name(skill), "fluent-korean")
            self.assertIn("(OMP)", text)
            self.assertIn("현재 호스트 모델", text)
            self.assertIn("OMP에서는 제공하지 않는다", text)
            for forbidden in ("CLAUDE_SKILL_DIR", "humanize-monolith", "humanize-diagnostician",
                              "humanize-finalizer", "claude-opus", "Task("):
                self.assertNotIn(forbidden, text)
            source = korean / "codex/skills/fluent-korean"
            original = (source / "SKILL.md").read_text()
            rules = original.split("## 윤문 철칙", 1)[1].split("## 파일·정량 윤문 절차", 1)[0]
            for rule in rules.splitlines():
                if rule and not rule.startswith("5."):
                    self.assertIn(rule, text)
            self.assertIn("30% 이상", text)
            self.assertIn("50% 이상", text)
            self.assertIn("01_input.txt", text)
            self.assertIn("../../scripts/verify_change_rate.py", text)
            self.assertIn("realpath skill://fluent-korean", text)
            self.assertNotIn("skill://fluent-korean/../", text)
            for code in range(4):
                self.assertIn(f"exit {code}", text)
            self.assertIn("채택 금지", text)
            self.assertIn("완료로 보고하지", text)
            for reference in (source / "references").iterdir():
                projected = skill.parent / "references" / reference.name
                if reference.name in ("quick-rules.md", "quick-rules.header.md", "quick-rules.footer.md"):
                    source_lines = reference.read_text().splitlines()
                    projected_lines = projected.read_text().splitlines()
                    for prefix in ("- **", "**Do-NOT", "**서법 보존", "**내용 앵커",
                                   "1. **고유명사", "3. **장르", "4. **register", "5. **잔존", "6. **인공"):
                        protected = [line for line in source_lines if line.startswith(prefix)]
                        if prefix == "- **":
                            protected = [line for line in protected if re.match(r"- \*\*[A-J]-\d", line)]
                        observed = [line for line in projected_lines if line.startswith(prefix)]
                        if prefix == "- **":
                            observed = [line for line in observed if re.match(r"- \*\*[A-J]-\d", line)]
                        self.assertEqual(observed, protected)
                    for forbidden in ("humanize-monolith", "monolith", "Phase 2.5", "strict 모드 권고"):
                        self.assertNotIn(forbidden, projected.read_text())
                    for target in re.findall(r"!?\[[^]]+\]\(([^)]+)\)", projected.read_text()):
                        if target.endswith("verify_change_rate.py"):
                            self.assertTrue((projected.parent / target).is_file())
                else:
                    self.assertEqual(projected.read_bytes(), reference.read_bytes())
            for target in re.findall(r"`(references/[^`]+)`", text):
                self.assertTrue((skill.parent / target).resolve().is_relative_to(installed))
                self.assertTrue((skill.parent / target).is_file())
            upstream = (installed / "UPSTREAM.md").read_text().rsplit("\n\n", 1)[-1]
            self.assertIn("Codex single-call", upstream)
            self.assertNotIn("CLAUDE_SKILL_DIR", upstream)
            self.assertNotIn("task", upstream)
            self.assertEqual({path.name for path in (installed / "scripts").iterdir()},
                             {"verify_change_rate.py", "console.py"})
            for name in ("verify_change_rate.py", "console.py"):
                self.assertEqual((installed / "scripts" / name).read_bytes(),
                                 (korean / "scripts" / name).read_bytes())
            manifest = json.loads((installed / ".claude-plugin/plugin.json").read_text())
            self.assertNotIn("agents", manifest)
            self.assertNotIn("hooks", manifest)
            for forbidden in ("agents", "hooks", "extension.ts", "omp",
                              "scripts/task-continuity.py", "scripts/evidence-gates.py"):
                self.assertFalse((installed / forbidden).exists(), forbidden)
            for path, data in originals.items():
                self.assertEqual(path.read_bytes(), data)
            self.run_renderer(command + ["--check"])

    def test_omp_korean_installed_validator_exit_codes(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            command = self.omp_fixture(root)
            self.run_renderer(command)
            installed = root.resolve() / "installed-korean"
            shutil.copytree(root / "plugins/fluent-korean/omp", installed)
            validator = installed / "scripts/verify_change_rate.py"
            self.assertTrue(validator.is_file())
            before = root / "01_input.txt"
            after = root / "final.md"
            before.write_text("가나다라마바사아자차")
            for body, code, percent in (("가나다라마바사아자차", 0, "0.0%"),
                                        ("가나다라마바ABCZ", 1, "40.0%"),
                                        ("가나다라마바사ABC", 1, "30.0%"),
                                        ("가나다라마ABCDE", 2, "50.0%")):
                with self.subTest(code=code, percent=percent):
                    after.write_text(body + "\n\n<!-- HUMANIZE-SUMMARY metadata -->")
                    result = subprocess.run([sys.executable, "-B", str(validator),
                                             "--before", str(before), "--after", str(after)],
                                            cwd=installed, capture_output=True, text=True)
                    self.assertEqual(result.returncode, code, result.stdout + result.stderr)
                    self.assertIn(percent, result.stdout)
            after.unlink()
            result = subprocess.run([sys.executable, "-B", str(validator),
                                     "--before", str(before), "--after", str(after)],
                                    cwd=installed, capture_output=True, text=True)
            self.assertEqual(result.returncode, 3, result.stdout + result.stderr)
            self.assertIn("error:", result.stderr)

    def test_omp_continuity_has_no_removed_extension_claim(self):
        template = (ROOT / "shared/task-continuity/continuity.md.tmpl").read_text()
        profiles = json.loads((ROOT / "shared/task-continuity/profiles.json").read_text())
        for text in (template, *((ROOT / "plugins" / name / "references/continuity.md").read_text()
                                 for name in profiles)):
            self.assertNotIn("SONSU_OMP_SESSION_ID", text)
            self.assertNotIn("omp extension", text)
            self.assertIn("omp 순정 todo·session", text)
            self.assertIn("native session-ID", text)
            self.assertIn("blocked`/`not_run", text)

    def test_omp_direct_engineering_requires_native_session_evidence(self):
        tools = (ROOT / "plugins/engineering/references/omp-tools.md").read_text()
        self.assertNotIn("Sonsu omp extension", tools)
        self.assertNotIn("session_stop", tools)
        self.assertNotIn("SONSU_OMP_SESSION_ID", tools)
        self.assertIn("native session-ID", tools)
        profiles = (ROOT / "plugins/engineering/references/omp-model-profiles.md").read_text()
        self.assertIn("기본 5개", profiles)
        self.assertIn("직접 설치", profiles)

    def test_omp_renderer_cleans_owned_stale_files_without_mutating_sources(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            command = self.omp_fixture(root)
            originals = {path: path.read_bytes() for path in root.rglob("*") if path.is_file()}
            self.run_renderer(command)
            self.run_renderer(command + ["--check"])
            installed = root / "plugins/design/omp"
            self.assertEqual((installed / "scripts/tool.py").stat().st_mode & 0o777, 0o755)
            self.assertFalse((installed / "omp").exists())
            for path, data in originals.items():
                self.assertEqual(path.read_bytes(), data)
            user_file = installed / "personal.txt"
            user_file.write_text("keep")
            source = root / "plugins/design/scripts/tool.py"
            source.unlink()
            checked = self.run_renderer(command + ["--check"], expected=1)
            self.assertIn("obsolete: plugins/design/omp/scripts/tool.py", checked.stdout)
            self.assertTrue((installed / "scripts/tool.py").exists())
            self.run_renderer(command)
            self.assertFalse((installed / "scripts/tool.py").exists())
            self.assertEqual(user_file.read_text(), "keep")
            self.run_renderer(command + ["--check"])

    def test_omp_renderer_preserves_unowned_and_modified_generated_files(self):
        for existing in ("unowned", "modified"):
            with self.subTest(existing=existing), tempfile.TemporaryDirectory() as directory:
                root = Path(directory)
                command = self.omp_fixture(root)
                target = root / "plugins/design/omp/scripts/tool.py"
                if existing == "modified":
                    self.run_renderer(command)
                target.parent.mkdir(parents=True, exist_ok=True)
                target.write_text("user-owned")
                self.run_renderer(command, expected=2)
                self.assertEqual(target.read_text(), "user-owned")

    def test_omp_renderer_rejects_symlinks_before_mutating_other_packages(self):
        for location in ("source", "destination", "obsolete"):
            with self.subTest(location=location), tempfile.TemporaryDirectory() as directory:
                root = Path(directory)
                command = self.omp_fixture(root)
                outside = root / "outside"
                outside.mkdir()
                (outside / "keep").write_text("keep")
                if location == "source":
                    (root / "plugins/design/assets").symlink_to(outside, target_is_directory=True)
                elif location == "destination":
                    (root / "plugins/design/omp").symlink_to(outside, target_is_directory=True)
                else:
                    self.run_renderer(command)
                    target = root / "plugins/design/omp/scripts/tool.py"
                    target.unlink()
                    target.symlink_to(outside / "keep")
                    (root / "plugins/design/scripts/tool.py").unlink()
                before = {path: path.read_bytes() for path in root.rglob("*")
                          if path.is_file() and not path.is_symlink()}
                self.run_renderer(command, expected=2)
                for path, data in before.items():
                    self.assertEqual(path.read_bytes(), data)

    def test_omp_renderer_only_removes_identified_legacy_runtime(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            command = self.omp_fixture(root)
            legacy = root / "plugins/engineering"
            legacy.mkdir()
            package = legacy / "package.json"
            package.write_text(json.dumps({
                "name": "sonsu-marketplace-engineering", "version": "1.0.0",
                "private": True, "type": "module", "omp": {"extensions": ["./omp/extension.ts"]},
            }))
            extension = legacy / "omp/extension.ts"
            extension.parent.mkdir()
            extension.write_text("user-modified extension")
            self.run_renderer(command, expected=2)
            self.assertTrue(package.exists())
            self.assertEqual(extension.read_text(), "user-modified extension")
            extension.unlink()
            user_package = root / "plugins/custom/package.json"
            user_package.parent.mkdir()
            user_package.write_text('{"name":"custom"}')
            self.run_renderer(command)
            self.assertFalse(package.exists())
            self.assertEqual(user_package.read_text(), '{"name":"custom"}')

    def test_codex_primary_model_switch_round_trip_persists_in_all_profiles(self):
        spec = importlib.util.spec_from_file_location("render_agent_policy", ROOT / "scripts/render-agent-policy.py")
        renderer = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(renderer)
        primary_roles = {"implementation", "complex_design", "senior_review", "adjudication",
                         "complex_adjudication", "red_team"}
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            source = root / "shared/agent-policy"
            shutil.copytree(ROOT / "shared/agent-policy", source)
            original = json.loads((source / "profiles.json").read_text())
            original["roles"]["general_review"]["model"] = "gpt-6-astra"
            original["roles"]["implementation"]["model"] = "gpt-6-luna"
            (source / "profiles.json").write_text(json.dumps(original))
            with mock.patch.object(renderer, "ROOT", root), mock.patch.object(renderer, "SOURCE", source):
                with mock.patch.object(sys, "argv", ["render-agent-policy.py"]), contextlib.redirect_stdout(io.StringIO()):
                    self.assertEqual(renderer.main(), 0)
                preserved = {path: path.read_bytes() for path in root.rglob("*") if path.is_file()
                             and ("claude" in path.name or "omp" in path.name or path.parent.name == "agents")}
                for model in ("gpt-6-astra", "gpt-6.1-sol", "gpt-6-astra"):
                    with self.subTest(model=model):
                        expected = json.loads(json.dumps(original))
                        for role in primary_roles:
                            expected["roles"][role]["model"] = model
                        with mock.patch.object(sys, "argv", ["render-agent-policy.py", "--codex-primary-model", model]), contextlib.redirect_stdout(io.StringIO()):
                            self.assertEqual(renderer.main(), 0)
                        self.assertEqual(json.loads((source / "profiles.json").read_text()), expected)
                        packaged = root / "plugins/engineering/references/model-profiles.json"
                        self.assertEqual(json.loads(packaged.read_text()), expected)
                        for plugin in ("engineering", "prompting"):
                            document = (root / "plugins" / plugin / "references/model-profiles.md").read_text()
                            for role in primary_roles:
                                self.assertIn(f"| `{role}` | `{model}` |", document)
                        before = {path: path.read_bytes() for path in root.rglob("*") if path.is_file()}
                        for args in ([], ["--check"], ["--codex-primary-model", model]):
                            with mock.patch.object(sys, "argv", ["render-agent-policy.py", *args]), contextlib.redirect_stdout(io.StringIO()):
                                self.assertEqual(renderer.main(), 0)
                        self.assertEqual({path: path.read_bytes() for path in root.rglob("*") if path.is_file()}, before)
                self.assertTrue(all(path.read_bytes() == data for path, data in preserved.items()))

    def test_codex_model_switch_invalid_arguments_do_not_write(self):
        spec = importlib.util.spec_from_file_location("render_agent_policy", ROOT / "scripts/render-agent-policy.py")
        renderer = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(renderer)
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            source = root / "shared/agent-policy"
            shutil.copytree(ROOT / "shared/agent-policy", source)
            before = {path: path.read_bytes() for path in root.rglob("*") if path.is_file()}
            with mock.patch.object(renderer, "ROOT", root), mock.patch.object(renderer, "SOURCE", source):
                for args in (["--check", "--codex-primary-model", "gpt-6-astra"],
                             ["--codex-primary-model", "unknown-model"]):
                    with self.subTest(args=args), mock.patch.object(sys, "argv", ["render-agent-policy.py", *args]), contextlib.redirect_stderr(io.StringIO()):
                        with self.assertRaises(SystemExit) as error:
                            renderer.main()
                        self.assertEqual(error.exception.code, 2)
                        self.assertEqual({path: path.read_bytes() for path in root.rglob("*") if path.is_file()}, before)

    def test_codex_model_switch_io_failures_preserve_source_and_allow_recovery(self):
        spec = importlib.util.spec_from_file_location("render_agent_policy", ROOT / "scripts/render-agent-policy.py")
        renderer = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(renderer)
        for failure in ("generated", "temporary", "replace"):
            with self.subTest(failure=failure), tempfile.TemporaryDirectory() as directory:
                root = Path(directory)
                source = root / "shared/agent-policy"
                shutil.copytree(ROOT / "shared/agent-policy", source)
                profile_path = source / "profiles.json"
                source_before = profile_path.read_bytes()
                target = "gpt-6.1-sol" if json.loads(source_before)["roles"]["implementation"]["model"] == "gpt-6-astra" else "gpt-6-astra"
                with mock.patch.object(renderer, "ROOT", root), mock.patch.object(renderer, "SOURCE", source):
                    with mock.patch.object(sys, "argv", ["render-agent-policy.py"]), contextlib.redirect_stdout(io.StringIO()):
                        self.assertEqual(renderer.main(), 0)
                    before = {path: path.read_bytes() for path in root.rglob("*") if path.is_file()}
                    with contextlib.ExitStack() as stack:
                        if failure == "generated":
                            write_bytes = Path.write_bytes

                            def fail_generated_write(path, data):
                                if path == root / "plugins/prompting/references/model-profiles.md":
                                    raise PermissionError("injected generated write failure")
                                return write_bytes(path, data)

                            stack.enter_context(mock.patch.object(Path, "write_bytes", fail_generated_write))
                        elif failure == "temporary":
                            named_temporary_file = tempfile.NamedTemporaryFile

                            def interrupted_temporary_file(*args, **kwargs):
                                temporary = named_temporary_file(*args, **kwargs)

                                def fail_partial_write(data):
                                    temporary.file.write(data[:len(data) // 2])
                                    raise OSError("injected partial temporary write failure")

                                temporary.write = fail_partial_write
                                return temporary

                            stack.enter_context(mock.patch.object(tempfile, "NamedTemporaryFile", interrupted_temporary_file))
                        else:
                            stack.enter_context(mock.patch.object(os, "replace", side_effect=OSError("injected replace failure")))
                        with mock.patch.object(sys, "argv", ["render-agent-policy.py", "--codex-primary-model", target]), contextlib.redirect_stdout(io.StringIO()):
                            with self.assertRaisesRegex(OSError, "injected"):
                                renderer.main()
                    self.assertEqual(profile_path.read_bytes(), source_before)
                    self.assertEqual(json.loads(profile_path.read_bytes()), json.loads(source_before))
                    self.assertEqual({path for path in root.rglob("*") if path.is_file()}, set(before))
                    with mock.patch.object(sys, "argv", ["render-agent-policy.py"]), contextlib.redirect_stdout(io.StringIO()):
                        self.assertEqual(renderer.main(), 0)
                    self.assertEqual({path: path.read_bytes() for path in root.rglob("*") if path.is_file()}, before)
                    with mock.patch.object(sys, "argv", ["render-agent-policy.py", "--check"]), contextlib.redirect_stdout(io.StringIO()):
                        self.assertEqual(renderer.main(), 0)

    def test_removed_claude_role_fails_check_and_is_removed_by_render(self):
        spec = importlib.util.spec_from_file_location("render_agent_policy", ROOT / "scripts/render-agent-policy.py")
        renderer = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(renderer)
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            source = root / "shared/agent-policy"
            shutil.copytree(ROOT / "shared/agent-policy", source)
            with mock.patch.object(renderer, "ROOT", root), mock.patch.object(renderer, "SOURCE", source):
                with mock.patch.object(sys, "argv", ["render-agent-policy.py"]), contextlib.redirect_stdout(io.StringIO()):
                    self.assertEqual(renderer.main(), 0)
                profile_file = source / "claude-profiles.json"
                profiles = json.loads(profile_file.read_text())
                profiles["roles"].pop("red_team")
                profile_file.write_text(json.dumps(profiles))
                removed = [root / "plugins" / plugin / "agents/red_team.md"
                           for plugin in ("engineering", "prompting")]
                with mock.patch.object(sys, "argv", ["render-agent-policy.py", "--check"]), contextlib.redirect_stdout(io.StringIO()) as output:
                    self.assertEqual(renderer.main(), 1)
                for plugin in ("engineering", "prompting"):
                    self.assertIn(f"stale: plugins/{plugin}/agents/red_team.md", output.getvalue())
                with mock.patch.object(sys, "argv", ["render-agent-policy.py"]), contextlib.redirect_stdout(io.StringIO()):
                    self.assertEqual(renderer.main(), 0)
                self.assertTrue(all(not path.exists() for path in removed))
                with mock.patch.object(sys, "argv", ["render-agent-policy.py", "--check"]), contextlib.redirect_stdout(io.StringIO()):
                    self.assertEqual(renderer.main(), 0)


    def test_render_preserves_custom_codex_agent(self):
        spec = importlib.util.spec_from_file_location("render_agent_policy", ROOT / "scripts/render-agent-policy.py")
        renderer = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(renderer)
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            source = root / "shared/agent-policy"
            shutil.copytree(ROOT / "shared/agent-policy", source)
            custom = root / ".codex/agents/custom.toml"
            custom.parent.mkdir(parents=True)
            original = b'name = "custom"\ndescription = "User-owned"\ndeveloper_instructions = "Keep"\n'
            custom.write_bytes(original)
            with mock.patch.object(renderer, "ROOT", root), mock.patch.object(renderer, "SOURCE", source):
                with mock.patch.object(sys, "argv", ["render-agent-policy.py"]), contextlib.redirect_stdout(io.StringIO()):
                    self.assertEqual(renderer.main(), 0)
                with mock.patch.object(sys, "argv", ["render-agent-policy.py", "--check"]), contextlib.redirect_stdout(io.StringIO()):
                    self.assertEqual(renderer.main(), 0)
                profile_file = source / "profiles.json"
                profiles = json.loads(profile_file.read_text())
                profiles["roles"].pop("red_team")
                profile_file.write_text(json.dumps(profiles))
                with mock.patch.object(sys, "argv", ["render-agent-policy.py", "--check"]), contextlib.redirect_stdout(io.StringIO()) as output:
                    self.assertEqual(renderer.main(), 1)
                self.assertIn("stale: .codex/agents/red_team.toml", output.getvalue())
                with mock.patch.object(sys, "argv", ["render-agent-policy.py"]), contextlib.redirect_stdout(io.StringIO()):
                    self.assertEqual(renderer.main(), 0)
                self.assertFalse((root / ".codex/agents/red_team.toml").exists())
            self.assertEqual(custom.read_bytes(), original)

    def test_render_refuses_to_overwrite_custom_codex_role(self):
        spec = importlib.util.spec_from_file_location("render_agent_policy", ROOT / "scripts/render-agent-policy.py")
        renderer = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(renderer)
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            source = root / "shared/agent-policy"
            shutil.copytree(ROOT / "shared/agent-policy", source)
            custom = root / ".codex/agents/general_review.toml"
            custom.parent.mkdir(parents=True)
            original = b'name = "general_review"\ndescription = "Custom review role"\ndeveloper_instructions = "Keep local rules"\n'
            custom.write_bytes(original)
            profile_before = (source / "profiles.json").read_bytes()
            with mock.patch.object(renderer, "ROOT", root), mock.patch.object(renderer, "SOURCE", source):
                for args in ([], ["--codex-primary-model", "gpt-6.1-sol"]):
                    with self.subTest(args=args), mock.patch.object(sys, "argv", ["render-agent-policy.py", *args]), contextlib.redirect_stdout(io.StringIO()) as output:
                        self.assertEqual(renderer.main(), 1)
                    self.assertIn("conflict: .codex/agents/general_review.toml", output.getvalue())
                    self.assertEqual((source / "profiles.json").read_bytes(), profile_before)
            self.assertEqual(custom.read_bytes(), original)
            self.assertFalse((root / ".codex/agents/extraction.toml").exists())


if __name__ == "__main__":
    unittest.main()
