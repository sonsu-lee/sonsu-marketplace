"""Cross-runtime packaging contracts for Codex and Claude Code plugins."""
import json
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest


ROOT = Path(__file__).resolve().parents[2]
RENDERER = ROOT / "scripts/render-claude-compat.py"


class ClaudeCompatibilityTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        self.root = Path(self.tmp.name)
        marketplace_dir = self.root / ".agents/plugins"
        plugin_dir = self.root / "plugins/example/.codex-plugin"
        marketplace_dir.mkdir(parents=True)
        plugin_dir.mkdir(parents=True)
        (marketplace_dir / "marketplace.json").write_text(
            json.dumps(
                {
                    "name": "fixture-marketplace",
                    "interface": {"displayName": "Fixture Marketplace"},
                    "plugins": [
                        {
                            "name": "example",
                            "source": {"source": "local", "path": "./plugins/example"},
                            "policy": {
                                "installation": "AVAILABLE",
                                "authentication": "ON_INSTALL",
                            },
                            "category": "Developer Tools",
                        }
                    ],
                }
            )
            + "\n"
        )
        (plugin_dir / "plugin.json").write_text(
            json.dumps(
                {
                    "name": "example",
                    "version": "1.2.3",
                    "description": "Fixture plugin",
                    "author": {"name": "Fixture", "url": "https://example.invalid"},
                    "license": "MIT",
                    "keywords": ["fixture", "skills"],
                    "skills": "./skills/",
                    "hooks": "./hooks/hooks.json",
                    "apps": "./.app.json",
                    "interface": {
                        "displayName": "Example Plugin",
                        "shortDescription": "Codex-only UI metadata",
                    },
                }
            )
            + "\n"
        )

    def run_renderer(self, *args):
        self.assertTrue(RENDERER.is_file(), "Claude compatibility renderer is missing")
        return subprocess.run(
            [sys.executable, str(RENDERER), "--root", str(self.root), *args],
            text=True,
            capture_output=True,
            timeout=15,
        )

    def test_renders_native_claude_catalog_and_plugin_manifest(self):
        result = self.run_renderer()
        self.assertEqual(result.returncode, 0, result.stderr)

        marketplace = json.loads(
            (self.root / ".claude-plugin/marketplace.json").read_text()
        )
        self.assertEqual(
            marketplace,
            {
                "name": "fixture-marketplace",
                "owner": {"name": "sonsu-lee", "url": "https://github.com/sonsu-lee"},
                "description": "Codex와 Claude Code에서 사용하는 재사용 가능한 에이전트 플러그인 모음입니다.",
                "plugins": [
                    {
                        "name": "example",
                        "source": "./plugins/example",
                        "description": "Fixture plugin",
                        "version": "1.2.3",
                        "category": "Developer Tools",
                    }
                ],
            },
        )

        manifest = json.loads(
            (self.root / "plugins/example/.claude-plugin/plugin.json").read_text()
        )
        self.assertEqual(
            manifest,
            {
                "$schema": "https://json.schemastore.org/claude-code-plugin-manifest.json",
                "name": "example",
                "displayName": "Example Plugin",
                "version": "1.2.3",
                "description": "Fixture plugin",
                "author": {"name": "Fixture", "url": "https://example.invalid"},
                "license": "MIT",
                "keywords": ["fixture", "skills"],
                "skills": "./skills/",
            },
        )
        self.assertNotIn("hooks", manifest)

    def test_check_detects_and_then_accepts_generated_outputs(self):
        stale = self.run_renderer("--check")
        self.assertEqual(stale.returncode, 1)
        self.assertIn(".claude-plugin/marketplace.json", stale.stdout)
        self.assertIn("plugins/example/.claude-plugin/plugin.json", stale.stdout)

        rendered = self.run_renderer()
        self.assertEqual(rendered.returncode, 0, rendered.stderr)
        current = self.run_renderer("--check")
        self.assertEqual(current.returncode, 0, current.stdout + current.stderr)
        self.assertEqual(current.stdout, "")

    def test_rejects_a_source_outside_the_named_plugin_directory(self):
        marketplace_path = self.root / ".agents/plugins/marketplace.json"
        marketplace = json.loads(marketplace_path.read_text())
        marketplace["plugins"][0]["source"]["path"] = "./plugins/example/../other"
        marketplace_path.write_text(json.dumps(marketplace) + "\n")

        result = self.run_renderer()

        self.assertEqual(result.returncode, 2)
        self.assertIn("invalid local plugin path", result.stderr)
        self.assertFalse((self.root / ".claude-plugin/marketplace.json").exists())


if __name__ == "__main__":
    unittest.main()
