"""Codex and OMP marketplace packaging contracts."""
import json
from pathlib import Path
import re
import unittest


ROOT = Path(__file__).resolve().parents[2]
CATALOG = ROOT / ".agents/plugins/marketplace.json"
OMP_CATALOG = ROOT / ".omp-plugin/marketplace.json"

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


if __name__ == "__main__":
    unittest.main()
