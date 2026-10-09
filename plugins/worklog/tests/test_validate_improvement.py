"""Frozen evaluation records and acceptance decisions through the public CLI."""
import copy
import hashlib
import json
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest


SCRIPT = Path(__file__).resolve().parents[1] / "scripts/validate_improvement.py"


def digest(value):
    return hashlib.sha256(json.dumps(value, ensure_ascii=False, sort_keys=True,
                                     separators=(",", ":")).encode()).hexdigest()


class ImprovementTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        self.path = Path(self.tmp.name) / "record.json"
        self.serial = 0
        self.fixed = {
            "revision": "a" * 40,
            "instructions": {"skills/demo/SKILL.md": "Use known facts.\n"},
            "configuration": {"model": "fixture-model", "settings": {"temperature": 0},
                              "command": "executor INPUT", "environment": {"host": "fixture"}},
            "case": {"id": "new", "input": "request", "fixtures": {}, "expected": ["observable"]},
            "regressions": [{"id": i, "input": i, "fixtures": {}, "expected": ["observable"]}
                            for i in ("A", "B")],
        }
        self.record = {"schema_version": 1, "fixed": self.fixed,
                       "baseline": self.bundle(self.fixed["instructions"], ["fail"] * 3, ["pass", "fail"]),
                       "candidates": []}
        self.record["candidates"].append(self.candidate())

    def run_record(self, state, case, instructions):
        self.serial += 1
        return {"revision": self.fixed["revision"],
                "configuration": copy.deepcopy(self.fixed["configuration"]),
                "case_sha256": digest(case), "instructions_sha256": digest(instructions),
                "context": f"context-{self.serial}", "output": "captured response",
                "verdicts": [state]}

    def bundle(self, instructions, states, regressions):
        return {"runs": [self.run_record(s, self.fixed["case"], instructions) for s in states],
                "regressions": {c["id"]: self.run_record(s, c, instructions)
                                for c, s in zip(self.fixed["regressions"], regressions)}}

    def candidate(self, states=None, regression_states=None, extra=1, identifier="candidate-1"):
        instructions = {p: s + "Verify sources.\n" * extra for p, s in self.fixed["instructions"].items()}
        return {"id": identifier, "parent": "baseline", "base_revision": self.fixed["revision"],
                "base_instructions_sha256": digest(self.fixed["instructions"]),
                "instructions": instructions, "net_lines": extra, "approval": None,
                **self.bundle(instructions, states or ["pass", "pass", "fail"],
                              regression_states or ["pass", "fail"])}

    def cli(self, code=0):
        self.path.write_text(json.dumps(self.record), encoding="utf-8")
        result = subprocess.run([sys.executable, "-B", str(SCRIPT), str(self.path)],
                                capture_output=True, text=True)
        self.assertEqual(result.returncode, code, result.stdout + result.stderr)
        return json.loads(result.stdout)

    def test_accepts_two_of_three_and_preserves_each_pass(self):
        result = self.cli()
        self.assertEqual(result["status"], "pass")
        self.assertEqual(result["baseline"]["n_of_3"], "0/3")
        self.assertEqual(result["candidates"][0]["n_of_3"], "2/3")

    def test_swapped_regression_passes_fail(self):
        self.record["candidates"] = [self.candidate(regression_states=["fail", "pass"])]
        result = self.cli()
        self.assertEqual(result["status"], "fail")
        self.assertEqual(result["candidates"][0]["lost_regression_ids"], ["A"])

    def test_equal_baseline_or_less_than_two_fails(self):
        for baseline, candidate in ((2, 2), (0, 1)):
            with self.subTest(baseline=baseline, candidate=candidate):
                self.record["baseline"] = self.bundle(self.fixed["instructions"],
                                                      ["pass"] * baseline + ["fail"] * (3 - baseline),
                                                      ["pass", "fail"])
                self.record["candidates"] = [self.candidate(["pass"] * candidate + ["fail"] * (3 - candidate))]
                self.assertEqual(self.cli()["status"], "fail")

    def test_unknown_and_unexecuted_are_separate(self):
        for state in ("not_run", "inconclusive"):
            with self.subTest(state=state):
                self.record["candidates"] = [self.candidate(["pass", "pass", state])]
                result = self.cli()
                self.assertEqual(result["status"], state)
                self.assertEqual(result["candidates"][0][state], 1)

    def test_unknown_regression_stops_even_when_baseline_failed(self):
        self.record["candidates"] = [self.candidate(regression_states=["pass", "inconclusive"])]
        self.assertEqual(self.cli()["status"], "inconclusive")

    def test_zero_regressions_is_limit_not_regression_pass(self):
        self.fixed["regressions"] = []
        self.record["baseline"]["regressions"] = {}
        self.record["candidates"][0]["regressions"] = {}
        result = self.cli()
        self.assertEqual(result["status"], "pass")
        self.assertEqual(result["limitations"], ["no-regression-cases"])

    def test_record_invariants(self):
        original = copy.deepcopy(self.record)
        mutations = [
            lambda d: d["baseline"]["runs"].pop(),
            lambda d: d["baseline"]["runs"].append(copy.deepcopy(d["baseline"]["runs"][0])),
            lambda d: d["candidates"][0].update(parent="candidate-0"),
            lambda d: d["candidates"][0].update(base_revision="b" * 40),
            lambda d: d["candidates"][0].update(net_lines=2),
            lambda d: d["candidates"][0]["regressions"].pop("A"),
            lambda d: d["candidates"][0]["runs"][0].update(revision="b" * 40),
            lambda d: d["candidates"][0]["runs"][0].update(case_sha256="0" * 64),
            lambda d: d["candidates"][0]["runs"][0].update(instructions_sha256="0" * 64),
            lambda d: d["candidates"][0]["runs"][0]["configuration"].update(model="other"),
            lambda d: d["candidates"][0]["runs"][0]["configuration"].update(settings={}),
            lambda d: d["candidates"][0]["runs"][0].update(context=d["baseline"]["runs"][0]["context"]),
            lambda d: d["fixed"]["case"].update(expected=["weaker"]),
            lambda d: d["fixed"]["instructions"].update({"skills/demo/SKILL.md": "changed"}),
            lambda d: d["fixed"]["regressions"].reverse(),
            lambda d: d["fixed"].update(revision="main"),
        ]
        for index, mutate in enumerate(mutations):
            with self.subTest(index=index):
                self.record = copy.deepcopy(original)
                mutate(self.record)
                self.assertFalse(self.cli(1)["valid"])

    def test_line_limit_requires_approval(self):
        self.record["candidates"] = [self.candidate(extra=16)]
        self.assertEqual(self.cli()["status"], "approval_required")
        self.record["candidates"][0]["approval"] = "user message authorizing this diff"
        self.assertEqual(self.cli()["status"], "pass")
        self.record["candidates"] = [self.candidate(extra=15)]
        self.assertEqual(self.cli()["status"], "pass")

    def test_net_lines_subtracts_deletions(self):
        candidate = self.candidate()
        candidate["instructions"] = {"skills/demo/SKILL.md": "Check claims.\n"}
        candidate["net_lines"] = 0
        candidate.update(self.bundle(candidate["instructions"], ["pass"] * 3, ["pass", "fail"]))
        self.record["candidates"] = [candidate]
        result = self.cli()["candidates"][0]
        self.assertEqual((result["added"], result["deleted"], result["net_lines"]), (1, 1, 0))

    def test_stops_after_pass_or_unresolved_baseline(self):
        self.record["candidates"].append(self.candidate(identifier="candidate-2"))
        self.cli(1)
        self.record["candidates"] = []
        for state in ("pass", "not_run", "inconclusive"):
            self.record["baseline"] = self.bundle(self.fixed["instructions"], [state] * 3, ["pass", "fail"])
            self.assertEqual(self.cli()["status"], "inconclusive" if state == "pass" else state)
            self.record["candidates"] = [self.candidate()]
            self.cli(1)
            self.record["candidates"] = []

    def test_three_independent_failures_allowed_fourth_rejected(self):
        self.record["candidates"] = [self.candidate(["fail"] * 3, identifier=f"candidate-{n}") for n in range(3)]
        self.assertEqual(self.cli()["status"], "fail")
        self.record["candidates"].append(self.candidate(["fail"] * 3, identifier="fourth"))
        self.cli(1)

    def test_malformed_shapes_are_contract_errors(self):
        for value in (None, [], {"schema_version": True}, {"schema_version": 1, "fixed": []}):
            self.record = value
            self.cli(1)

    def test_bad_json_and_missing_file(self):
        self.path.write_text("{", encoding="utf-8")
        for path in (self.path, self.path.parent / "missing"):
            result = subprocess.run([sys.executable, "-B", str(SCRIPT), str(path)], capture_output=True, text=True)
            self.assertEqual(result.returncode, 2)
            self.assertEqual(json.loads(result.stdout)["status"], "unreadable")


if __name__ == "__main__":
    unittest.main()
