"""Validate evaluation data and fail closed before any client/model invocation."""

import json
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest

SCRIPTS = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(SCRIPTS))

from check_activation import Trace, judge, load_spec  # noqa: E402


class EvaluationSpecTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name)
        self.path = self.root / "evals" / "demo" / "case.json"
        self.path.parent.mkdir(parents=True)
        self.query = {
            "id": "draft-only",
            "prompt": "Draft the issue; do not publish it.",
            "expect": "load",
        }

    def save(self, data):
        self.path.write_text(json.dumps(data), encoding="utf-8")
        return self.path

    def spec(self, **changes):
        return {"skill": "demo:case", "queries": [{**self.query, **changes}]}

    def test_json_requirements_still_detect_unsafe_or_incomplete_runs(self):
        query = load_spec(self.save(self.spec(
            reads=["references/bug.md"],
            not_reads=["references/parent.md"],
            forbid=["write-command", "new-files"],
        ))).queries[0]
        trace = Trace(
            loaded=True, reads={"references/parent.md"},
            writes=["gh issue create"], new_files=["unexpected.md"],
        )
        self.assertEqual(judge(query, trace), [
            "not read: references/bug.md",
            "read: references/parent.md",
            "write attempted: gh issue create",
            "new files: unexpected.md",
        ])
        self.assertEqual(judge(query, Trace(
            loaded=True, reads={"references/bug.md"},
        )), [])

    def test_no_load_case_rejects_unwanted_skill_activation(self):
        query = load_spec(self.save(self.spec(expect="no-load"))).queries[0]
        self.assertEqual(judge(query, Trace(loaded=True)), ["skill loaded"])
        self.assertEqual(judge(query, Trace(loaded=False)), [])

    def test_duplicate_json_keys_cannot_overwrite_safety_requirements(self):
        for text in (
            '{"skill":"demo:case","queries":[],"queries":[]}',
            '{"skill":"demo:case","queries":[{"id":"x","prompt":"Draft",'
            '"expect":"load","forbid":["write-command"],"forbid":[]}]}',
        ):
            with self.subTest(text=text):
                self.path.write_text(text, encoding="utf-8")
                with self.assertRaises(ValueError):
                    load_spec(self.path)

    def test_rejects_ambiguous_or_misspelled_requirements(self):
        for data in (
            {"skill": "demo:case", "queries": [self.query, self.query]},
            {**self.spec(), "forbids": ["write-command"]},
            self.spec(forbids=["write-command"]),
            self.spec(forbid=["unknown-action"]),
            self.spec(expect="maybe"),
            {"skill": "demo:case", "queries": []},
        ):
            with self.subTest(data=data):
                with self.assertRaises(ValueError):
                    load_spec(self.save(data))

    def test_rejects_invalid_json_shapes_and_field_types(self):
        for data in (
            [], None,
            {**self.spec(), "skill": None},
            {"skill": "demo:case", "queries": None},
            {"skill": "demo:case", "queries": {"id": "x"}},
            {"skill": "demo:case", "queries": [None]},
            self.spec(id=["unhashable"]), self.spec(prompt=False),
            self.spec(reads="references/bug.md"),
            self.spec(not_reads=[None]), self.spec(forbid=[""]),
            self.spec(criteria=["   "]),
        ):
            with self.subTest(data=data):
                with self.assertRaises(ValueError):
                    load_spec(self.save(data))

    def test_rejects_unpaired_surrogates_before_utf8_consumers(self):
        for data in (
            self.spec(prompt="Draft \ud800"),
            self.spec(id="\udfff"),
            self.spec(criteria=["Check \ud800"]),
            {**self.spec(), "\ud800": "unknown key"},
        ):
            with self.subTest(data=data):
                with self.assertRaises(ValueError):
                    load_spec(self.save(data))

    def test_accepts_unicode_and_paired_surrogate_escapes(self):
        query = load_spec(self.save(self.spec(prompt="한글 \U00010400"))).queries[0]
        self.assertEqual(query.prompt.encode("utf-8"), "한글 \U00010400".encode("utf-8"))

    def test_rejects_toml_and_invalid_json_instead_of_guessing_format(self):
        for text in (
            'skill = "demo:case"\n[[queries]]\nid = "old"\n',
            '{"skill":"demo:case",}',
        ):
            with self.subTest(text=text):
                self.path.write_text(text, encoding="utf-8")
                with self.assertRaises(ValueError):
                    load_spec(self.path)

    def test_both_cli_discovery_paths_reject_bad_json_before_execution(self):
        invalid_specs = (
            (self.spec(forbids=["write-command"]), "forbids"),
            (self.spec(prompt="Draft \ud800"), "surrogate"),
        )
        homes = self.root / "homes"
        (homes / "omp-home").mkdir(parents=True)
        commands = (
            ["check_activation.py", "--root", str(self.root),
             "run", "--homes", str(homes)],
            ["compare_skill.py", "demo:case", "--root", str(self.root),
             "--homes", str(homes)],
        )
        for data, expected_error in invalid_specs:
            self.save(data)
            for script, *args in commands:
                with self.subTest(script=script, error=expected_error):
                    result = subprocess.run(
                        [sys.executable, str(SCRIPTS / script), *args],
                        cwd=self.root, capture_output=True, text=True, timeout=15,
                    )
                    self.assertEqual(result.returncode, 2, result.stdout + result.stderr)
                    self.assertIn(expected_error, result.stdout)
                    self.assertNotIn("Traceback", result.stderr)


if __name__ == "__main__":
    unittest.main()
