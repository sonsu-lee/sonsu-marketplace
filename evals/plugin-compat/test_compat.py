"""Codex and OMP marketplace packaging contracts."""
import json
from pathlib import Path
import unittest


ROOT = Path(__file__).resolve().parents[2]
CATALOG = ROOT / ".agents/plugins/marketplace.json"
OMP_CATALOG = ROOT / ".omp-plugin/marketplace.json"


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
