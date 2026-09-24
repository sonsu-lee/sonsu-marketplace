"""Codex, OMP, and Claude Code marketplace packaging contracts."""
import importlib.util
import json
from pathlib import Path
import re
import subprocess
import sys
import tempfile
import unittest


ROOT = Path(__file__).resolve().parents[2]
CATALOG = ROOT / ".agents/plugins/marketplace.json"
OMP_CATALOG = ROOT / ".omp-plugin/marketplace.json"
CLAUDE_CATALOG = ROOT / ".claude-plugin/marketplace.json"

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


def omp_skills():
    catalog = json.loads(OMP_CATALOG.read_text(encoding="utf-8"))
    plugin_root = (ROOT / catalog["metadata"]["pluginRoot"]).resolve()
    for entry in catalog["plugins"]:
        package_root = (plugin_root / entry["source"]).resolve()
        for skill_path in sorted((package_root / "skills").glob("*/SKILL.md")):
            yield entry["name"], skill_path, read_skill_name(skill_path)


class CodexPackagingTests(unittest.TestCase):
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

    def test_omp_catalog_projects_codex_plugin_identity(self):
        codex_catalog = json.loads(CATALOG.read_text(encoding="utf-8"))
        omp_catalog = json.loads(OMP_CATALOG.read_text(encoding="utf-8"))
        codex_names = {entry["name"] for entry in codex_catalog["plugins"]}
        omp_entries = {entry["name"]: entry for entry in omp_catalog["plugins"]}

        self.assertEqual(omp_catalog["owner"]["name"], "sonsu-lee")
        self.assertEqual(omp_catalog["metadata"]["pluginRoot"], "./plugins")
        self.assertEqual(set(omp_entries), codex_names)

        for name, entry in omp_entries.items():
            with self.subTest(plugin=name):
                manifest = json.loads(
                    (ROOT / "plugins" / name / ".codex-plugin/plugin.json").read_text(
                        encoding="utf-8"
                    )
                )
                self.assertEqual(entry["source"], f"./{name}")
                self.assertEqual(entry["version"], manifest["version"])

    def test_omp_skill_names_are_unique(self):
        owners = {}

        for plugin, skill_path, skill_name in omp_skills():
            with self.subTest(plugin=plugin, skill=skill_name):
                self.assertNotIn(
                    skill_name,
                    owners,
                    f"OMP skill {skill_name!r} conflicts between "
                    f"{owners.get(skill_name)} and {skill_path}",
                )
                owners[skill_name] = skill_path

    def test_runtime_skill_references_resolve_for_omp(self):
        skill_names = {skill_name for _, _, skill_name in omp_skills()}
        plugin_names = {
            entry["name"]
            for entry in json.loads(OMP_CATALOG.read_text(encoding="utf-8"))["plugins"]
        }
        reference = re.compile(
            r"`(?P<plugin>" + "|".join(re.escape(name) for name in sorted(plugin_names)) +
            r"):(?P<skill>[a-z][a-z0-9-]*)`"
        )

        for _, skill_path, _ in omp_skills():
            text = skill_path.read_text(encoding="utf-8")
            for match in reference.finditer(text):
                paragraph_start = text.rfind("\n\n", 0, match.start()) + 2
                paragraph_end = text.find("\n\n", match.end())
                paragraph = text[paragraph_start:paragraph_end if paragraph_end >= 0 else None]
                skill_name = match.group("skill")
                with self.subTest(path=skill_path, reference=match.group(0)):
                    self.assertIn(skill_name, skill_names)
                    self.assertIn(f"`skill://{skill_name}`", paragraph)

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

    def test_claude_catalog_and_manifests_match_codex_and_omp(self):
        codex = json.loads(CATALOG.read_text(encoding="utf-8"))
        omp = json.loads(OMP_CATALOG.read_text(encoding="utf-8"))
        claude = json.loads(CLAUDE_CATALOG.read_text(encoding="utf-8"))
        self.assertEqual(len(codex["plugins"]), 12)
        self.assertEqual(claude["name"], codex["name"])
        self.assertEqual(claude["name"], omp["name"])
        self.assertEqual(
            [entry["name"] for entry in claude["plugins"]],
            [entry["name"] for entry in codex["plugins"]],
        )
        omp_entries = {entry["name"]: entry for entry in omp["plugins"]}
        for entry in claude["plugins"]:
            name = entry["name"]
            with self.subTest(plugin=name):
                self.assertEqual(entry["source"], f"./plugins/{name}")
                manifest = json.loads((ROOT / "plugins" / name / ".claude-plugin/plugin.json").read_text())
                codex_manifest = json.loads((ROOT / "plugins" / name / ".codex-plugin/plugin.json").read_text())
                self.assertEqual(manifest["name"], name)
                self.assertEqual(manifest["version"], entry["version"])
                self.assertEqual(entry["version"], codex_manifest["version"])
                self.assertEqual(entry["version"], omp_entries[name]["version"])
                self.assertTrue((ROOT / "plugins" / name / "skills").is_dir())

    def test_claude_renderer_detects_stale_and_invalid_source(self):
        renderer = ROOT / "scripts/render-claude-compat.py"
        result = subprocess.run([sys.executable, str(renderer), "--check"], capture_output=True, text=True)
        self.assertEqual(result.returncode, 0, result.stderr + result.stdout)

        spec = importlib.util.spec_from_file_location("render_claude_compat", renderer)
        module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(module)
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            (root / ".agents/plugins").mkdir(parents=True)
            (root / ".omp-plugin").mkdir()
            (root / "plugins/engineering/.codex-plugin").mkdir(parents=True)
            (root / ".agents/plugins/marketplace.json").write_text(json.dumps({
                "name": "test", "plugins": [{"name": "engineering", "source": {"source": "local", "path": "../escape"}}],
            }))
            (root / ".omp-plugin/marketplace.json").write_text(json.dumps({
                "name": "test", "metadata": {"pluginRoot": "./plugins"},
                "plugins": [{"name": "engineering", "source": "./engineering", "version": "1.0.0"}],
            }))
            (root / "plugins/engineering/.codex-plugin/plugin.json").write_text(json.dumps({
                "name": "engineering", "version": "1.0.0",
            }))
            with self.assertRaisesRegex(ValueError, "invalid local plugin path"):
                module.rendered_outputs(root)


if __name__ == "__main__":
    unittest.main()
