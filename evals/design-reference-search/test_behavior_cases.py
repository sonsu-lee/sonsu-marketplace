from __future__ import annotations

import json
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
CASES = Path(__file__).resolve().parent / "cases.json"
ROUTING_CASES = ROOT / "evals" / "skill-routing" / "cases.json"
SKILL = ROOT / "plugins" / "design" / "skills" / "find-references" / "SKILL.md"


class BehaviorCaseTests(unittest.TestCase):
    def setUp(self) -> None:
        self.payload = json.loads(CASES.read_text(encoding="utf-8"))
        self.cases = self.payload["cases"]

    def test_cases_have_unique_ids_and_both_splits(self) -> None:
        self.assertEqual(self.payload["schema_version"], "design-reference-search-behavior-v1")
        ids = [case["id"] for case in self.cases]
        self.assertEqual(len(ids), len(set(ids)))
        self.assertEqual({case["split"] for case in self.cases}, {"calibration", "held_out"})
        for case in self.cases:
            with self.subTest(case=case["id"]):
                self.assertEqual(
                    set(case) - {"fixture"},
                    {"id", "split", "installed_plugins", "prompt", "expected", "must_not"},
                )
                self.assertTrue(case["prompt"].strip())
                for field in ("expected", "must_not"):
                    self.assertTrue(case[field])
                    self.assertEqual(len(case[field]), len(set(case[field])))

    def test_routing_fixtures_resolve_to_behavior_cases(self) -> None:
        ids = {case["id"] for case in self.cases}
        routing = json.loads(ROUTING_CASES.read_text(encoding="utf-8"))["cases"]
        linked = [
            case["fixture"]["case"]
            for case in routing
            if case.get("fixture", {}).get("suite") == "design-reference-search"
        ]
        self.assertTrue(linked)
        self.assertEqual(sorted(set(linked) - ids), [])

    def test_routing_cases_select_the_packaged_skill(self) -> None:
        self.assertTrue(SKILL.read_text(encoding="utf-8").startswith("---\nname: find-references\n"))
        routing = json.loads(ROUTING_CASES.read_text(encoding="utf-8"))["cases"]
        selected = [case for case in routing if "design:find-references" in case["expected_sequence"]]
        excluded = [case for case in routing if "design:find-references" in case.get("must_not_select", [])]
        self.assertGreaterEqual(len(selected), 3)
        self.assertGreaterEqual(len(excluded), 3)


if __name__ == "__main__":
    unittest.main()
