"""Unit tests for semantic fixture outcomes; no model is required."""

from pathlib import Path
import shutil
import sys
import tempfile
import unittest
from unittest.mock import patch

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
import fixture_outcomes as outcomes  # noqa: E402


class FixtureOutcomeTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.output = Path(self.temp.name) / "workspace"

    def prepare(self, name, source="expected"):
        fixture = Path(__file__).resolve().parents[2] / "evals" / "fixtures" / name
        shutil.copytree(fixture / source, self.output)
        return fixture / "input"

    def test_expected_outcomes_and_readonly_reports(self):
        for name in ("bulk-rename", "imports", "shadowing", "mixed-syntax",
                     "parse-error", "tiny", "preview"):
            with self.subTest(name=name):
                if self.output.exists():
                    shutil.rmtree(self.output)
                inputs = self.prepare(name)
                report = "broken.py syntax error; a.py b.py timeout_ms request_timeout_ms"
                self.assertEqual(outcomes.grade(name, inputs, self.output, report), [])

    def test_formatting_is_accepted_but_comment_change_is_not(self):
        inputs = self.prepare("bulk-rename")
        path = self.output / "beta.py"
        path.write_text("request_timeout_ms=300\ndef value(): return request_timeout_ms*2\n")
        self.assertEqual(outcomes.grade("bulk-rename", inputs, self.output, ""), [])
        path = self.output / "alpha.py"
        path.write_text(path.read_text().replace("# timeout_ms remains", "# changed"))
        self.assertTrue(outcomes.grade("bulk-rename", inputs, self.output, ""))

    def test_wrong_scope_extra_and_symlink_are_rejected(self):
        inputs = self.prepare("shadowing")
        path = self.output / "scopes.py"
        path.write_text(path.read_text().replace("def other(value)", "def other(amount)"))
        self.assertTrue(outcomes.grade("shadowing", inputs, self.output, ""))
        (self.output / "extra").write_text("extra")
        self.assertTrue(any("extra" in item for item in outcomes.grade("shadowing", inputs, self.output, "")))
        (self.output / "link").symlink_to(path)
        self.assertTrue(any("symlink" in item for item in outcomes.grade("shadowing", inputs, self.output, "")))

    def test_untouched_and_reports_are_checked(self):
        inputs = self.prepare("preview")
        self.assertTrue(outcomes.grade("preview", inputs, self.output, ""))
        (self.output / "a.py").write_text("timeout_ms = 101\n")
        self.assertTrue(any("untouched" in item for item in outcomes.grade("preview", inputs, self.output, "a.py b.py timeout_ms request_timeout_ms")))
        with self.assertRaises(ValueError):
            outcomes.grade("unknown", inputs, self.output, "")

    def test_csv_unavailable_sandbox_is_explicit(self):
        inputs = self.prepare("executing-csv", "input")
        with patch.object(outcomes.shutil, "which", return_value=None):
            errors = outcomes.grade("executing-csv", inputs, self.output, "")
        self.assertTrue(any("sandbox-exec unavailable" in item for item in errors))
        self.assertTrue(any("tests were not updated" in item for item in errors))

    @unittest.skipUnless(sys.platform == "darwin" and shutil.which("sandbox-exec"),
                         "macOS sandbox required")
    def test_csv_grades_source_without_rejecting_or_loading_generated_bytecode(self):
        inputs = self.prepare("executing-csv", "input")
        (self.output / "exporter.py").write_text(
            'import csv, io\n'
            'def export_csv(rows):\n'
            '    output = io.StringIO(newline="")\n'
            '    csv.writer(output, lineterminator="\\n").writerows(rows)\n'
            '    return output.getvalue()\n')
        (self.output / "test_exporter.py").write_text(
            'import unittest, csv, io\nfrom exporter import export_csv\n'
            'class Tests(unittest.TestCase):\n'
            '    def test_escaping(self):\n'
            '        rows = [["a,b", \'say "hi"\']]\n'
            '        self.assertEqual(list(csv.reader(io.StringIO(export_csv(rows)))), rows)\n')
        cache = self.output / "__pycache__"
        cache.mkdir()
        (cache / "exporter.cpython-315.pyc").write_bytes(b"not source code")
        self.assertEqual(outcomes.grade("executing-csv", inputs, self.output, ""), [])
        (self.output / "exporter.py").write_bytes((inputs / "exporter.py").read_bytes())
        self.assertTrue(any("behavior" in item
                            for item in outcomes.grade("executing-csv", inputs, self.output, "")))

    def test_root_git_directory_is_ignored(self):
        inputs = self.prepare("tiny")
        (self.output / ".git").mkdir()
        (self.output / ".git" / "config").write_text("not a fixture file")
        self.assertEqual(outcomes.grade("tiny", inputs, self.output, ""), [])


if __name__ == "__main__":
    unittest.main()
