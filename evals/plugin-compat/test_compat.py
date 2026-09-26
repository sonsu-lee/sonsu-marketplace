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
                expected = "memory-manager-claude" if entry["name"] == "memory-manager" else entry["name"]
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
                generated = ROOT / "plugins/memory-manager-claude/skills" / name / "SKILL.md"
                codex = source.read_text(encoding="utf-8")
                claude = generated.read_text(encoding="utf-8")
                self.assertNotIn("disable-model-invocation:", codex)
                if name in ("memory-maintain", "memory-promote"):
                    codex = codex.replace("\n---\n", "\ndisable-model-invocation: true\n---\n", 1)
                self.assertEqual(claude, codex)
                self.assertEqual(read_skill_name(generated), name)
        self.assertFalse((ROOT / "plugins/memory-manager-claude/skills/memory-manager").exists())
        for relative in ("scripts/memory_store.py", "hooks/capture.py", "hooks/hooks.json"):
            self.assertEqual((ROOT / "plugins/memory-manager" / relative).read_bytes(),
                             (ROOT / "plugins/memory-manager-claude" / relative).read_bytes())

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
        for name in ("README.md", "README.en.md", "README.ja.md"):
            with self.subTest(readme=name):
                text = (ROOT / name).read_text(encoding="utf-8")
                self.assertIn("$memory-capture", text)
                self.assertIn("/memory-manager:memory-capture", text)

    def test_generated_claude_hook_stages_only_candidate(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory).resolve()
            project = root / "project"
            project.mkdir()
            package = ROOT / "plugins/memory-manager-claude"
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
                claude_package = ROOT / "plugins" / ("memory-manager-claude" if entry["name"] == "memory-manager" else entry["name"])
                claude = json.loads((claude_package / ".claude-plugin/plugin.json").read_text(encoding="utf-8"))
                self.assertNotIn("hooks", codex)
                self.assertNotIn("hooks", claude)
                self.assertIn("hooks", json.loads(hook_file.read_text(encoding="utf-8")))

    def test_public_skill_names_match_directories(self):
        catalog = json.loads(CATALOG.read_text(encoding="utf-8"))
        for entry in catalog["plugins"]:
            root = ROOT / "plugins" / entry["name"] / "skills"
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
            cache = root / "plugins/memory-manager-claude/scripts/__pycache__"
            cache.mkdir()
            (cache / "memory_store.cpython-39.pyc").write_bytes(b"runtime cache")
            self.assertEqual(subprocess.run(command + ["--check"], capture_output=True).returncode, 0)
            obsolete = root / "plugins/memory-manager-claude/skills/old-memory/SKILL.md"
            obsolete.parent.mkdir()
            obsolete.write_text("obsolete")
            checked = subprocess.run(command + ["--check"], capture_output=True, text=True)
            self.assertEqual(checked.returncode, 1)
            self.assertIn("obsolete:", checked.stdout)
            self.assertEqual(subprocess.run(command, capture_output=True).returncode, 0)
            self.assertFalse(obsolete.exists())

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


if __name__ == "__main__":
    unittest.main()
