"""Static contracts for the thin Codex and OMP capability-pack catalogs."""

import importlib.util
import json
import os
from pathlib import Path
import re
import sys
import tempfile
import unittest
from unittest import mock


ROOT = Path(__file__).resolve().parents[2]
CODEX_CATALOG = ROOT / ".agents/plugins/marketplace.json"
OMP_CATALOG = ROOT / ".omp-plugin/marketplace.json"
VERSION = "1.0.0"
EXPECTED = {
    "code-review": {
        "review-pr", "review-failure-modes", "review-maintainability",
        "review-operability", "review-overengineering", "audit-overengineering",
    },
    "code-intelligence": {"semantic-code-intelligence"},
    "workflow": {"inspect-prs", "repair-pr", "to-ticket", "ticket-lifecycle", "to-pr"},
    "developer-writing": {"write-developer-blog"},
    "prompting": {"prompt-builder"},
    "product": {
        "product-discovery", "synthesize-product-evidence", "product-domain-discovery",
        "design-product-test", "assess-product-test", "to-prd",
    },
    "figma-workflow": {"figma-product-design", "figma-prototype-flow", "figma-design-audit"},
    "interface-design": {"design-interface", "redesign-interface"},
    "operations-ui": {
        "design-operations-ui", "redesign-operations-ui", "audit-operations-ui",
        "figma-operations-flow",
    },
    "design-patterns": {"select-design-patterns", "review-pattern-usage"},
}
REMOVED = {
    "engineering", "research", "fluent-languages", "memory-manager", "writing",
}

NATIVE_PROBE_PATH = ROOT / "evals/plugin-compat/native_probe.py"
NATIVE_PROBE_SPEC = importlib.util.spec_from_file_location("native_probe", NATIVE_PROBE_PATH)
assert NATIVE_PROBE_SPEC and NATIVE_PROBE_SPEC.loader
NATIVE_PROBE = importlib.util.module_from_spec(NATIVE_PROBE_SPEC)
NATIVE_PROBE_SPEC.loader.exec_module(NATIVE_PROBE)


def load(path: Path):
    return json.loads(path.read_text(encoding="utf-8"))


def frontmatter(path: Path):
    text = path.read_text(encoding="utf-8")
    if not text.startswith("---\n"):
        raise AssertionError(f"{path} has no frontmatter")
    block = text.split("---\n", 2)[1]
    result = {}
    for line in block.splitlines():
        if ":" in line:
            key, value = line.split(":", 1)
            result[key.strip()] = value.strip().strip("\"'")
    return result


class ThinCatalogContractTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.codex = load(CODEX_CATALOG)
        cls.omp = load(OMP_CATALOG)
        cls.codex_entries = {entry["name"]: entry for entry in cls.codex["plugins"]}
        cls.omp_entries = {entry["name"]: entry for entry in cls.omp["plugins"]}

    def test_exact_plugin_inventory_and_order(self):
        expected = list(EXPECTED)
        self.assertEqual([entry["name"] for entry in self.codex["plugins"]], expected)
        self.assertEqual([entry["name"] for entry in self.omp["plugins"]], expected)
        self.assertEqual(len(expected), 10)
        self.assertTrue(REMOVED.isdisjoint(self.codex_entries))

    def test_catalog_identity_path_and_version_parity(self):
        plugin_root = (ROOT / self.omp["metadata"]["pluginRoot"]).resolve()
        for name in EXPECTED:
            with self.subTest(plugin=name):
                codex_entry = self.codex_entries[name]
                omp_entry = self.omp_entries[name]
                package = ROOT / "plugins" / name
                manifest = load(package / ".codex-plugin/plugin.json")
                self.assertEqual(codex_entry["source"], {
                    "source": "local", "path": f"./plugins/{name}",
                })
                self.assertEqual(omp_entry["source"], f"./{name}")
                self.assertEqual((plugin_root / omp_entry["source"]).resolve(), package.resolve())
                self.assertEqual(manifest["name"], name)
                self.assertEqual(manifest["version"], VERSION)
                self.assertEqual(omp_entry["version"], VERSION)
                self.assertEqual(codex_entry["policy"]["installation"], "AVAILABLE")

    def test_exact_31_globally_unique_skill_names(self):
        owners = {}
        for plugin, expected_skills in EXPECTED.items():
            package = ROOT / "plugins" / plugin
            paths = sorted((package / "skills").glob("*/SKILL.md"))
            actual = set()
            for path in paths:
                metadata = frontmatter(path)
                name = metadata.get("name")
                self.assertEqual(name, path.parent.name, path)
                self.assertNotIn(name, owners, f"{name}: {owners.get(name)} and {path}")
                owners[name] = plugin
                actual.add(name)
            self.assertEqual(actual, expected_skills, plugin)
        self.assertEqual(len(owners), 31)

    def test_manifest_targets_exist_and_stay_inside_package(self):
        for plugin in EXPECTED:
            package = (ROOT / "plugins" / plugin).resolve()
            manifest = load(package / ".codex-plugin/plugin.json")
            for key in ("skills", "apps", "mcpServers"):
                value = manifest.get(key)
                if value is None:
                    continue
                values = value if isinstance(value, list) else [value]
                for relative in values:
                    target = (package / relative).resolve()
                    self.assertTrue(target.is_relative_to(package), (plugin, key, relative))
                    self.assertTrue(target.exists(), (plugin, key, relative))

    def test_no_marketplace_owned_hooks_or_removed_packages(self):
        for plugin in EXPECTED:
            package = ROOT / "plugins" / plugin
            manifest = load(package / ".codex-plugin/plugin.json")
            self.assertNotIn("hooks", manifest, plugin)
            self.assertFalse((package / "hooks").exists(), plugin)
            self.assertFalse((package / "skills" / "task-continuity").exists(), plugin)
        for name in REMOVED:
            self.assertFalse((ROOT / "plugins" / name).exists(), name)

    def test_legacy_engineering_artifacts_remain_ignored(self):
        ignore_rules = (ROOT / ".gitignore").read_text(encoding="utf-8").splitlines()
        self.assertIn(".engineering/", ignore_rules)

    def test_review_pr_is_explicit_only(self):
        metadata = frontmatter(ROOT / "plugins/code-review/skills/review-pr/SKILL.md")
        self.assertEqual(metadata.get("allow_implicit_invocation"), "false")

    def test_host_specific_connector_metadata(self):
        manifests = {
            name: load(ROOT / "plugins" / name / ".codex-plugin/plugin.json")
            for name in EXPECTED
        }
        self.assertEqual(manifests["figma-workflow"].get("apps"), "./.app.json")
        self.assertEqual(manifests["code-intelligence"].get("mcpServers"), "./codex-mcp.json")
        self.assertEqual(load(ROOT / "plugins/figma-workflow/.app.json"), {
            "apps": {
                "figma": {
                    "id": "connector_68df038e0ba48191908c8434991bbac2",
                    "required": True,
                }
            }
        })
        for name, manifest in manifests.items():
            if name != "figma-workflow":
                self.assertNotIn("apps", manifest, name)
            if name != "code-intelligence":
                self.assertNotIn("mcpServers", manifest, name)
        forbidden = {"mcp", "mcpServers", "lsp", "lspServers", "apps", "hooks"}
        for entry in self.omp["plugins"]:
            self.assertTrue(forbidden.isdisjoint(entry), entry["name"])

    def test_code_intelligence_config_is_pinned_and_secret_free(self):
        mcp = load(ROOT / "plugins/code-intelligence/codex-mcp.json")
        self.assertEqual(mcp, {
            "mcpServers": {
                "mcpls": {
                    "command": "python3",
                    "args": ["scripts/launch-mcpls.py"],
                    "cwd": ".",
                }
            }
        })
        serialized = json.dumps(mcp)
        self.assertIsNone(re.search(r"(?i)(token|api[_-]?key|secret|password)", serialized))
        launcher = (ROOT / "plugins/code-intelligence/scripts/launch-mcpls.py").read_text(encoding="utf-8")
        self.assertIn('REQUIRED_VERSION = "0.6.0"', launcher)
        self.assertIn('"MCPLS_TRUST_PROJECT_CONFIG": "false"', launcher)
        self.assertNotRegex(launcher, r"curl|wget|pip install|cargo install|brew install")
        config = (ROOT / "plugins/code-intelligence/config/mcpls.toml").read_text(encoding="utf-8")
        self.assertIn('tool_prefix = "lsp"', config)
        self.assertIn("roots = []", config)


class NativeProbeIsolationTests(unittest.TestCase):
    def test_scrubbed_environment_drops_external_omp_profile(self):
        with mock.patch.dict(
            os.environ,
            {
                "PI_CODING_AGENT_DIR": "/real/user/profile",
                "OPENAI_API_KEY": "must-not-survive",
            },
            clear=False,
        ):
            env = NATIVE_PROBE.scrubbed_env(Path("/tmp/disposable-home"))

        self.assertNotIn("PI_CODING_AGENT_DIR", env)
        self.assertNotIn("OPENAI_API_KEY", env)
        self.assertEqual(env["HOME"], "/tmp/disposable-home")

    def test_rpc_client_reads_buffered_notification_and_response(self):
        server = (
            "import json, sys\n"
            "request = json.loads(sys.stdin.readline())\n"
            "sys.stderr.write('x' * 200000)\n"
            "sys.stderr.flush()\n"
            "print(json.dumps({'jsonrpc': '2.0', 'method': 'ready'}))\n"
            "print(json.dumps({'jsonrpc': '2.0', 'id': request['id'], "
            "'result': {'ok': True}}), flush=True)\n"
        )
        client = NATIVE_PROBE.RpcClient(
            [sys.executable, "-c", server],
            cwd=ROOT,
            env=os.environ.copy(),
        )
        stderr = ""
        try:
            self.assertEqual(client.request("probe", {}, timeout=2), {"ok": True})
            self.assertEqual(
                [message.get("method") for message in client.notifications],
                ["ready"],
            )
        finally:
            stderr = client.close()
        self.assertEqual(len(stderr), 200000)

    def test_marketplace_skills_allow_missing_plugin_id(self):
        with tempfile.TemporaryDirectory() as directory:
            codex_home = Path(directory) / "codex-home"
            cache = codex_home / "plugins/cache/sonsu-marketplace/code-review/1.0.0"
            valid = cache / "skills/review-pr/SKILL.md"
            valid.parent.mkdir(parents=True)
            valid.write_text("review skill", encoding="utf-8")
            unrelated = Path(directory) / "unrelated/SKILL.md"
            unrelated.parent.mkdir()
            unrelated.write_text("unrelated skill", encoding="utf-8")
            skills = [
                {
                    "name": "code-review:review-pr",
                    "path": str(valid),
                },
                {
                    "name": "code-review:review-pr",
                    "path": str(unrelated),
                },
            ]
            catalog = NATIVE_PROBE.marketplace_skill_catalog(
                skills,
                codex_home,
                {"code-review:review-pr"},
            )

        self.assertEqual(catalog, skills[:1])


if __name__ == "__main__":
    unittest.main()
