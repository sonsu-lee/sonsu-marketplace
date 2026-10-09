"""validate_refactor_inventory.py가 누락·낡은 기록·잘못된 필드를 찾아내는지 확인한다."""
import hashlib
import json
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest


ROOT = Path(__file__).resolve().parents[2]
SCRIPT = ROOT / "scripts/validate_refactor_inventory.py"
INVENTORY = "docs/research/refactor-inventory"


def digest(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def write(path, text):
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text, encoding="utf-8")


def write_json(path, value):
    write(path, json.dumps(value, ensure_ascii=False, indent=2) + "\n")


class FixtureRepository:
    def __init__(self, root):
        self.root = root
        write_json(root / ".agents/plugins/marketplace.json",
                   {"plugins": [{"name": "demo"}, {"name": "other"}]})
        for name, skill in (("demo", "alpha"), ("other", "gamma")):
            write_json(root / f"plugins/{name}/.codex-plugin/plugin.json", {"name": name, "skills": "./skills/"})
            write(root / f"plugins/{name}/skills/{skill}/SKILL.md", f"---\nname: {skill}\n---\n\n# {skill}\n\n본문\n")
        write(root / "plugins/demo/scripts/tool.py", "print('tool')\n")
        write(root / "plugins/demo/scripts/task-continuity.py", "# generated\n")
        write(root / "plugins/demo/scripts/design_md.mjs", "// generated\n")
        write(root / "scripts/render-omp-compat.py", "OMP_PLUGINS = set()\nOMP_OPTIN_PLUGINS = set()\n")
        write(root / "evals/demo/README.md", "demo\n")
        write(root / "shared/x/README.md", "x\n")
        self.write_inventory()

    def path(self, relative):
        return self.root / relative

    def skill_entry(self, path, **overrides):
        entry = {
            "path": path,
            "sha256": digest(self.path(path)),
            "problem": "문제",
            "outcome": "결과",
            "ai_judgment": "판단",
            "mechanical": [{"step": "단계", "location": f"{path}:1-3", "existing_tool": None, "proposal": "none"}],
            "unique_value": "가치",
            "overlaps": [{"target": "omp:todo", "note": "겹침"}],
            "verdict": "keep",
            "verdict_target": "",
            "reason": "근거",
            "doc_findings": [{"kind": "structure", "location": f"{path}:5", "note": "지적"}],
            "example": "missing",
        }
        entry.update(overrides)
        return entry

    def plugin_inventory(self, name, skills, scripts=()):
        return {
            "schema_version": 1,
            "plugin": name,
            "manifest_sha256": digest(self.path(f"plugins/{name}/.codex-plugin/plugin.json")),
            "problem": "문제",
            "outcome": "결과",
            "omp": {"current": "not-distributed", "proposal": "not-distributed", "reason": "근거"},
            "verdict": "keep",
            "verdict_target": "",
            "reason": "근거",
            "skills": [self.skill_entry(path) for path in skills],
            "scripts": [
                {"path": path, "sha256": digest(self.path(path)), "role": "역할", "verdict": "keep",
                 "verdict_target": "", "reason": "근거"}
                for path in scripts
            ],
        }

    def write_inventory(self):
        inventory = self.root / INVENTORY
        write_json(inventory / "demo.json", self.plugin_inventory(
            "demo", ["plugins/demo/skills/alpha/SKILL.md"], ["plugins/demo/scripts/tool.py"]))
        write_json(inventory / "other.json", self.plugin_inventory("other", ["plugins/other/skills/gamma/SKILL.md"]))
        write_json(inventory / "repository.json", {
            "schema_version": 1,
            "scripts": [{"path": "scripts/render-omp-compat.py",
                         "sha256": digest(self.path("scripts/render-omp-compat.py")), "role": "생성기",
                         "verdict": "keep", "verdict_target": "", "reason": "근거"}],
            "shared": [{"path": "shared/x", "role": "공유", "verdict": "keep", "verdict_target": "",
                        "reason": "근거"}],
            "evals": [{"path": "evals/demo", "covers": ["demo", "other"], "role": "평가"}],
        })

    def edit_inventory(self, name, change):
        path = self.root / INVENTORY / f"{name}.json"
        data = json.loads(path.read_text(encoding="utf-8"))
        change(data)
        write_json(path, data)


class ValidateRefactorInventoryTest(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.repo = FixtureRepository(Path(self.temp.name))

    def tearDown(self):
        self.temp.cleanup()

    def run_tool(self, *args):
        return subprocess.run(
            [sys.executable, str(SCRIPT), args[0], "--root", str(self.repo.root), *args[1:]],
            capture_output=True, text=True, check=False,
        )

    def assert_violation(self, result, code, where=""):
        self.assertEqual(result.returncode, 1, result.stdout + result.stderr)
        self.assertIn(f"violation: {code} {where}", result.stdout)

    def test_complete_inventory_passes(self):
        result = self.run_tool("check")
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
        self.assertTrue(result.stdout.endswith("violations: 0\n"))

    def test_removed_skill_entry_is_missing(self):
        self.repo.edit_inventory("demo", lambda data: data["skills"].clear())
        self.assert_violation(self.run_tool("check"), "missing-entry", "plugins/demo/skills/alpha/SKILL.md")

    def test_skill_changed_after_inventory_is_stale(self):
        with self.repo.path("plugins/demo/skills/alpha/SKILL.md").open("a", encoding="utf-8") as file:
            file.write("추가\n")
        self.assert_violation(self.run_tool("check"), "stale", "plugins/demo/skills/alpha/SKILL.md")

    def test_location_beyond_file_length(self):
        self.repo.edit_inventory("demo", lambda data: data["skills"][0]["mechanical"][0].update(
            location="plugins/demo/skills/alpha/SKILL.md:1-99"))
        self.assert_violation(self.run_tool("check"), "invalid-location")

    def test_merge_without_target(self):
        self.repo.edit_inventory("demo", lambda data: data["skills"][0].update(verdict="merge", verdict_target=""))
        self.assert_violation(self.run_tool("check"), "invalid-field")

    def test_null_string_existing_tool(self):
        self.repo.edit_inventory("demo", lambda data: data["skills"][0]["mechanical"][0].update(existing_tool="null"))
        self.assert_violation(self.run_tool("check"), "invalid-field")

    def test_new_tool_without_tool_proposal(self):
        self.repo.edit_inventory("demo", lambda data: data["skills"][0].update(verdict="new-tool"))
        self.assert_violation(self.run_tool("check"), "invalid-field")

    def test_deleted_plugin_file_is_missing(self):
        self.repo.path(f"{INVENTORY}/other.json").unlink()
        self.assert_violation(self.run_tool("check"), "missing-entry", "other.json")

    def test_corrupt_plugin_file_stops_analysis(self):
        write(self.repo.path(f"{INVENTORY}/other.json"), "{")
        self.assertEqual(self.run_tool("check").returncode, 2)

    def test_single_plugin_check_ignores_other_files(self):
        self.repo.path(f"{INVENTORY}/other.json").unlink()
        result = self.run_tool("check", "--plugin", "demo")
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
        write(self.repo.path(f"{INVENTORY}/other.json"), "{")
        result = self.run_tool("check", "--plugin", "demo")
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)

    def test_scan_reads_codex_and_claude_skill_roots(self):
        write_json(self.repo.path("plugins/demo/.codex-plugin/plugin.json"), {"name": "demo", "skills": "./codex/skills/"})
        write_json(self.repo.path("plugins/demo/.claude-plugin/plugin.json"), {"name": "demo"})
        write(self.repo.path("plugins/demo/codex/skills/alpha/SKILL.md"), "codex\n")
        write(self.repo.path("plugins/demo/skills/beta/SKILL.md"), "claude\n")
        result = self.run_tool("scan")
        self.assertEqual(result.returncode, 0, result.stderr)
        demo = json.loads(result.stdout)["plugins"][0]
        self.assertEqual([skill["path"] for skill in demo["skills"]], [
            "plugins/demo/codex/skills/alpha/SKILL.md",
            "plugins/demo/skills/alpha/SKILL.md",
            "plugins/demo/skills/beta/SKILL.md",
        ])

    def test_scan_excludes_generated_scripts(self):
        result = self.run_tool("scan")
        scripts = [script["path"] for script in json.loads(result.stdout)["plugins"][0]["scripts"]]
        self.assertEqual(scripts, ["plugins/demo/scripts/tool.py"])

    def test_recorded_omp_state_must_match_render_constants(self):
        self.repo.edit_inventory("demo", lambda data: data["omp"].update(current="default"))
        self.assert_violation(self.run_tool("check"), "omp-mismatch")

    def test_removed_eval_entry_is_missing(self):
        self.repo.edit_inventory("repository", lambda data: data["evals"].clear())
        self.assert_violation(self.run_tool("check"), "missing-entry", "evals/demo")

    def test_report_block_must_match_report_output(self):
        report = self.run_tool("report").stdout
        path = self.repo.path("docs/research/refactor-assessment.md")
        block = f"<!-- inventory-report:start -->\n{report}<!-- inventory-report:end -->\n"
        write(path, f"# 판정\n\n{block}")
        result = self.run_tool("check")
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
        write(path, f"# 판정\n\n{block.replace('demo', 'changed', 1)}")
        self.assert_violation(self.run_tool("check"), "stale-report")
        write(path, f"# 판정\n\n{block}\n{block}")
        self.assert_violation(self.run_tool("check"), "stale-report")

    def test_unknown_plugin_argument_stops_analysis(self):
        self.assertEqual(self.run_tool("check", "--plugin", "nope").returncode, 2)


if __name__ == "__main__":
    unittest.main()
