"""Boundary tests for the read-only plan structure validator."""
import json
from pathlib import Path
import subprocess
import sys
import tempfile
import textwrap
import unittest


SCRIPT = Path(__file__).resolve().parents[1] / "scripts" / "validate_plan.py"
HEADER = "| 흐름 | 요구사항 | 입력과 결과 | 파일과 책임 | 작업과 의존 관계 | 검증과 이유 |\n| --- | --- | --- | --- | --- | --- |"


def plan(flows, rows, tasks, extra=""):
    return "\n".join(["# 계획", "", *flows, "", extra, "", HEADER, *rows, "", *tasks, ""])


def task(number, flows, *files):
    lines = [f"### Task {number}: 산출물 {number}", f"**Flows:** {flows}", "**Files:**"]
    lines += [f"- {action}: `{path}`" for action, path in files]
    lines += ["", "**Verification:** existing_check"]
    return "\n".join(lines)


class ValidatePlan(unittest.TestCase):
    def setUp(self):
        temp = tempfile.TemporaryDirectory()
        self.addCleanup(temp.cleanup)
        self.root = Path(temp.name) / "repo"
        (self.root / "src").mkdir(parents=True)
        (self.root / "tests").mkdir()
        (self.root / "src" / "app.py").write_text("print('app')\n")
        (self.root / "tests" / "test_app.py").write_text("")
        self.plan_path = Path(temp.name) / "plan.md"

    def run_plan(self, text, root=None):
        self.plan_path.write_text(text, encoding="utf-8")
        result = subprocess.run(
            [sys.executable, "-B", str(SCRIPT), str(self.plan_path), "--root", str(root or self.root)],
            capture_output=True, text=True, check=False)
        return result.returncode, json.loads(result.stdout)

    def codes(self, report):
        return sorted(error["code"] for error in report["errors"])

    def test_valid_plan_allows_declared_new_file_and_ignores_non_flow_text(self):
        text = plan(
            ["```text", "FLOW F1: 내보내기", "  OUTPUT: CSV", "```", "FLOW F3: 오류 거부"],
            ["| `F1` | REQ-F1 | 날짜 → CSV | `src/app.py`: 필터 | Task 1; 없음 | 테스트 |",
             "| F3 | - | 잘못된 날짜 → 2 | `src/app.py`: 검증 | Task 1, Task 4; F1 | 새 파일 |"],
            [task(1, "`F1`, `F3`", ("Modify", "src/app.py:12-20"), ("Create", "tests/test_new.py"),
                  ("Verify", "tests/test_new.py")),
             task(4, "F3", ("Verify", "tests/test_app.py")),
             "```python\nFLOW F9: sample code\nTask 99\n```"],
            "`src/F7.py`는 경로이며 흐름이 아니다.")
        code, report = self.run_plan(text)
        self.assertEqual((code, report["status"], report["errors"]), (0, "valid", []))
        self.assertEqual(report["flows"], ["F1", "F3"])
        self.assertEqual(report["tasks"], ["1", "4"])
        created = [entry for entry in report["files"] if entry["path"] == "tests/test_new.py"]
        self.assertEqual([(e["action"], e["exists"], e["planned_new"]) for e in created],
                         [("Create", False, True), ("Verify", False, True)])
        self.assertEqual(report["files"][0]["path"], "src/app.py")
        self.assertFalse((self.root / "tests" / "test_new.py").exists())

    def test_duplicate_definitions_references_and_mappings(self):
        text = plan(
            ["FLOW F1: 첫째", "FLOW F1: 다시"],
            ["| F1 | - | a → b | x | Task 1 | y |", "| F1 | - | a → b | x | Task 1 | y |"],
            [task(1, "F1, F1", ("Modify", "src/app.py"), ("Modify", "src/app.py")),
             task(1, "F1", ("Modify", "src/app.py"))])
        code, report = self.run_plan(text)
        self.assertEqual(code, 1)
        for expected in ("duplicate_flow", "duplicate_task", "duplicate_mapping", "duplicate_reference", "duplicate_file"):
            self.assertIn(expected, self.codes(report))

    def test_dangling_flow_and_task_references(self):
        text = plan(
            ["FLOW F1: 첫째"],
            ["| F1 | - | a → b | x | Task 1; Task 9 | F2 회귀 |"],
            [task(1, "F1, F5", ("Modify", "src/app.py"))])
        code, report = self.run_plan(text)
        self.assertEqual(code, 1)
        dangling = {(e["code"], e["message"].split()[-1]) for e in report["errors"] if e["code"].startswith("dangling")}
        self.assertEqual(dangling, {("dangling_flow", "F2"), ("dangling_flow", "F5"), ("dangling_task", "9")})

    def test_missing_and_inconsistent_mappings(self):
        text = plan(
            ["FLOW F1: 첫째", "FLOW F2: 둘째"],
            ["| F1 | - | a → b | x | Task 1 | y |", "| F1 | - | a → b | x | Task 2 | y |"],
            [task(1, "F1, F2", ("Modify", "src/app.py")), task(2, "F2", ("Modify", "src/app.py")),
             task(3, "F2", ("Modify", "src/app.py"))])
        code, report = self.run_plan(text)
        self.assertEqual(code, 1)
        messages = {(e["code"], e["message"]) for e in report["errors"]}
        self.assertIn(("unmapped_flow", "F2 has no task mapping"), messages)
        self.assertIn(("unmapped_task", "Task 3 has no flow mapping"), messages)
        self.assertIn(("missing_mapping", "F2 / Task 1 is absent from mapping table"), messages)
        self.assertIn(("mapping_not_in_task", "Task 2 does not declare F1"), messages)

    def test_empty_structure_and_malformed_fields(self):
        code, report = self.run_plan("# 계획\n\n**Flows:** F1\n### Task one\n| F1 | x |\n```text\n")
        self.assertEqual(code, 1)
        for expected in ("missing_flows", "missing_tasks", "missing_mappings", "flows_without_task",
                         "invalid_task", "unclosed_fence"):
            self.assertIn(expected, self.codes(report))
        text = plan(["FLOW F1: 첫째"], ["| F1 | | a | x | 담당 없음 | y |"],
                    [task(1, "F1 and more", ("Modify", "src/app.py")) + "\n**Files:**\n- Change: src/app.py"])
        code, report = self.run_plan(text)
        self.assertEqual(code, 1)
        for expected in ("invalid_mapping", "invalid_flows", "invalid_file_declaration"):
            self.assertIn(expected, self.codes(report))

    def test_absent_files_require_explicit_create_and_paths_stay_in_root(self):
        outside = self.root.parent / "outside.py"
        outside.write_text("")
        (self.root / "link.py").symlink_to(outside)
        text = plan(
            ["FLOW F1: 첫째"],
            ["| F1 | - | a → b | x | Task 1 | y |"],
            [task(1, "F1", ("Modify", "src/missing.py"), ("Verify", "tests/test_missing.py"),
                  ("Modify", "../outside.py"), ("Modify", "link.py"), ("Modify", "src"),
                  ("Create", "src/new.py"))])
        code, report = self.run_plan(text)
        self.assertEqual(code, 1)
        errors = [(e["code"], e["message"].rsplit(" ", 1)[-1]) for e in report["errors"]]
        self.assertIn(("missing_file", "src/missing.py"), errors)
        self.assertIn(("missing_file", "tests/test_missing.py"), errors)
        self.assertIn(("invalid_path", "../outside.py"), errors)
        self.assertIn(("invalid_path", "link.py"), errors)
        self.assertIn(("not_a_file", "src"), errors)
        self.assertNotIn("src/new.py", [path for _, path in errors])

    def test_input_errors_exit_two(self):
        missing_root = self.root.parent / "absent"
        code, report = self.run_plan("FLOW F1: x\n", root=missing_root)
        self.assertEqual((code, report["status"]), (2, "input_error"))
        self.plan_path.write_bytes(b"\xff\xfe")
        result = subprocess.run([sys.executable, "-B", str(SCRIPT), str(self.plan_path), "--root", str(self.root)],
                                capture_output=True, text=True, check=False)
        self.assertEqual((result.returncode, json.loads(result.stdout)["status"]), (2, "input_error"))
        usage = subprocess.run([sys.executable, "-B", str(SCRIPT), str(self.plan_path)],
                               capture_output=True, text=True, check=False)
        self.assertEqual((usage.returncode, usage.stdout), (2, ""))


if __name__ == "__main__":
    unittest.main()
