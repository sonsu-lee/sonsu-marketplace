"""Behavioral checks for quality gates without invoking a model."""
import json
from pathlib import Path
import random
import sys
import tempfile
import unittest
from unittest.mock import patch

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
import compare_skill as cs


class ComparisonTests(unittest.TestCase):
    def setUp(self):
        self.query = cs.ca.Query(id="q", prompt="request", expect="load", criteria=["first", "second"])
        self.answer = lambda side: cs.Answer(side, cs.ca.Trace(reached=True, loaded=True), side, Path(side))
        self.answers = {side: self.answer(side) for side in ("base", "head")}

    def grade(self, result, answers=None):
        with patch.object(cs, "judge", return_value=(result, "log")):
            return cs.compare(Path(), Path(), None, self.query, answers or self.answers,
                              random.Random(0), "run")

    def test_candidate_failure_not_hidden_by_winner(self):
        result = {"winner": "A", "reason": "preferred", "criteria": [
            {"n": 1, "A": True, "B": True, "reason": "met"},
            {"n": 2, "A": False, "B": True, "reason": "missing"}]}
        verdict = self.grade(result)
        self.assertEqual(verdict.a_side, "base")
        self.assertEqual(cs.exit_status([verdict], []), 0)
        result["criteria"][1].update(A=True, B=False)
        verdict = self.grade(result)
        self.assertEqual(cs.exit_status([verdict], []), 1)
        self.assertFalse(verdict.criteria[1]["head"])
        self.assertEqual(verdict.criteria[1]["reason"], "missing")

    def test_incomplete_or_malformed_is_error(self):
        for criteria in ([], [{"n": 1, "A": True, "B": False}],
                         [{"n": 1, "A": True, "B": False}, {"n": 1, "A": True, "B": True}],
                         [{"n": 1, "A": True, "B": False}, {"n": 2, "A": "true", "B": True}]):
            with self.subTest(criteria=criteria):
                verdict = self.grade({"winner": "tie", "criteria": criteria})
                self.assertEqual(cs.exit_status([verdict], []), 2)
        self.answers["head"].trace.loaded = False
        self.assertEqual(cs.exit_status([self.grade({})], []), 2)
        self.assertEqual(cs.exit_status([cs.Verdict(criteria=[{"head": False}]), cs.Verdict(error="incomplete")], []), 2)

    def test_single_answer_failure_rejects_candidate(self):
        result = {"criteria": [{"n": 1, "A": True, "reason": "first met"},
                               {"n": 2, "A": False, "reason": "second absent"}]}
        verdict = self.grade(result, {"head": self.answer("head")})
        self.assertEqual(cs.exit_status([verdict], []), 1)

    def test_missing_or_blank_evidence_invalidates_judgment(self):
        for evidence in (None, "", "   "):
            item = {"n": 1, "A": True}
            if evidence is not None:
                item["reason"] = evidence
            with self.subTest(evidence=evidence):
                verdict = self.grade({"criteria": [item,
                    {"n": 2, "A": True, "reason": "second met"}]},
                    {"head": self.answer("head")})
                self.assertEqual(cs.exit_status([verdict], []), 2)

    def test_calibration_detects_false_acceptance_and_rejection(self):
        cases = [(self.query, [{"id": "bad", "text": "bad", "expected": [False, True]},
                               {"id": "good", "text": "good", "expected": [True, True]}])]
        def fake_judge(base, root, pin, query, first, second, label):
            return {"criteria": [{"n": 1, "A": first.text == "bad", "reason": "first"},
                                 {"n": 2, "A": True, "reason": "second"}]}, "log"
        with patch.object(cs, "judge", side_effect=fake_judge):
            results = cs.calibrate(Path(), Path(), None, cases, "stamp")
        self.assertEqual([r["error"] for r in results], ["calibration misclassification"] * 2)
        self.assertEqual(cs.exit_status([], results), 2)

    def test_calibration_schema_rejects_invalid_labels_and_duplicates(self):
        case = {"id": "c", "prompt": "p", "criteria": ["criterion"],
                "examples": [{"id": "e", "text": "answer", "expected": [True]}]}
        with tempfile.TemporaryDirectory() as temp:
            path = Path(temp) / "calibration.json"
            path.write_text(json.dumps({"cases": [case]}))
            self.assertEqual(len(cs.load_calibration(path)), 1)
            case["examples"][0]["expected"] = [1]
            path.write_text(json.dumps({"cases": [case]}))
            with self.assertRaises(ValueError):
                cs.load_calibration(path)
            case["examples"][0]["expected"] = [False]
            path.write_text(json.dumps({"cases": [case, case]}))
            with self.assertRaises(ValueError):
                cs.load_calibration(path)


if __name__ == "__main__":
    unittest.main()
