"""Codex and Claude Code marketplace packaging contracts."""
import json
from pathlib import Path
import unittest


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
                self.assertEqual(entry["source"], f"./plugins/{entry['name']}")
                package = ROOT / "plugins" / entry["name"]
                source = json.loads((package / ".codex-plugin/plugin.json").read_text(encoding="utf-8"))
                generated = json.loads((package / ".claude-plugin/plugin.json").read_text(encoding="utf-8"))
                self.assertEqual(generated["name"], source["name"])
                self.assertEqual(generated["version"], source["version"])
                self.assertEqual(entry["version"], source["version"])
                self.assertTrue((package / "skills").is_dir())

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


if __name__ == "__main__":
    unittest.main()
