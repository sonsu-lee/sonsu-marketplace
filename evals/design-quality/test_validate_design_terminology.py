from __future__ import annotations

import copy
import importlib.util
import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
SCRIPT = ROOT / "scripts/validate_design_terminology.py"
SPEC = importlib.util.spec_from_file_location("design_terminology_validator", SCRIPT)
MODULE = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(MODULE)


def ledger():
    return {"schema_version": "design-terminology-v1", "as_of": "2026-10-03", "terms": [{
        "id": "term.spacing", "ko": "간격", "en": "Spacing", "label_status": "internal_preferred",
        "definition": "요소 사이의 거리.", "includes": ["같은 그룹 안의 간격"], "excludes": ["입력 대상 크기"],
        "visual_signals": ["인접한 요소의 경계"], "relations": [], "sources": [],
        "observed_expressions": [{"text": "간격", "occurrence_id": "video000001:001"},
                                 {"text": "사이 간격", "occurrence_id": "video000001:002"},
                                 {"text": "그룹 간격", "occurrence_id": "video000002:001"}],
        "status": "adopted", "status_reason": "공식 정의 미확인: W3C", "review_by": "2027-10-03",
    }]}


def catalog():
    return {"videos": [
        {"video_id": video_id, "evidence_units": [
            {"id": video_id + suffix, "term_ids": ["term.spacing"], "verification": {"status": "confirmed"}}
            for suffix in suffixes
        ]} for video_id, suffixes in [("video000001", [":001", ":002"]), ("video000002", [":001"])]
    ]}


class TerminologyTests(unittest.TestCase):
    def test_adoption_requires_definition_boundaries_justification_and_current_review(self):
        self.assertEqual(MODULE.validate_ledger(ledger(), catalog()), [])
        for field, value in [("definition", ""), ("definition", "   "), ("includes", []), ("excludes", []),
                             ("status_reason", ""), ("review_by", "2026-10-02")]:
            with self.subTest(field=field, value=value):
                payload = ledger()
                payload["terms"][0][field] = value
                self.assertTrue(MODULE.validate_ledger(payload, catalog()))

    def test_adoption_requires_three_distinct_expressions_in_two_videos(self):
        for change in ("two-expressions", "one-video", "duplicate"):
            with self.subTest(change=change):
                payload = ledger()
                expressions = payload["terms"][0]["observed_expressions"]
                if change == "two-expressions":
                    expressions.pop()
                elif change == "one-video":
                    expressions[-1]["occurrence_id"] = "video000001:003"
                else:
                    expressions[1] = copy.deepcopy(expressions[0])
                self.assertTrue(MODULE.validate_ledger(payload))

    def test_official_candidate_requires_https_source(self):
        payload = ledger()
        term = payload["terms"][0]
        term["status"] = "candidate"
        term["label_status"] = "official"
        self.assertTrue(MODULE.validate_ledger(payload))
        term["sources"] = [{"id": "wcag", "title": "Understanding target size", "url": "https://www.w3.org/WAI/WCAG22/Understanding/target-size-minimum.html", "source_type": "standard"}]
        self.assertEqual(MODULE.validate_ledger(payload), [])
        term["sources"][0]["url"] = "http://www.w3.org/"
        self.assertTrue(MODULE.validate_ledger(payload))

    def test_relations_reject_self_missing_and_duplicate_targets(self):
        for relations in [[{"type": "related", "term_id": "term.spacing"}],
                          [{"type": "related", "term_id": "term.unknown"}]]:
            payload = ledger()
            payload["terms"][0]["relations"] = relations
            self.assertTrue(MODULE.validate_ledger(payload))
        payload = ledger()
        second = copy.deepcopy(payload["terms"][0])
        second.update(id="term.alignment", ko="정렬", en="Alignment")
        payload["terms"].append(second)
        payload["terms"][0]["relations"] = [{"type": "related", "term_id": "term.alignment"}] * 2
        self.assertTrue(MODULE.validate_ledger(payload))

    def test_rejected_names_may_repeat_but_active_names_and_ids_are_unique(self):
        payload = ledger()
        duplicate = copy.deepcopy(payload["terms"][0])
        duplicate["ko"] = "예전 간격"
        payload["terms"].append(duplicate)
        self.assertTrue(MODULE.validate_ledger(payload))
        duplicate["id"] = "term.old-spacing"
        self.assertEqual(MODULE.validate_ledger(payload), [])
        duplicate["ko"] = "간격"
        self.assertTrue(MODULE.validate_ledger(payload))
        duplicate["status"] = "rejected"
        self.assertEqual(MODULE.validate_ledger(payload), [])
        duplicate["status_reason"] = ""
        self.assertTrue(MODULE.validate_ledger(payload))
        duplicate["status"] = "held"
        duplicate["ko"] = "예전 간격"
        self.assertTrue(MODULE.validate_ledger(payload))

    def test_catalog_requires_nonrejected_terms_and_matching_assignments(self):
        for change in ("unknown-term", "rejected-term", "missing-unit", "missing-assignment", "held-unit"):
            with self.subTest(change=change):
                payload, corpus = ledger(), catalog()
                unit = corpus["videos"][0]["evidence_units"][0]
                if change == "unknown-term":
                    unit["term_ids"].append("term.unknown")
                elif change == "rejected-term":
                    payload["terms"][0]["status"] = "rejected"
                elif change == "missing-unit":
                    corpus["videos"][0]["evidence_units"].pop(0)
                elif change == "missing-assignment":
                    unit["term_ids"] = []
                else:
                    unit["verification"]["status"] = "held"
                self.assertTrue(MODULE.validate_ledger(payload, corpus))

    def test_prune_removes_only_orphans_and_revalidates_adoption(self):
        with tempfile.TemporaryDirectory() as tmp:
            path, corpus_path = Path(tmp) / "ledger.json", Path(tmp) / "catalog.json"
            payload, corpus = ledger(), catalog()
            corpus["videos"][0]["evidence_units"].pop(0)
            corpus["videos"][1]["evidence_units"][0]["term_ids"] = []
            path.write_text(json.dumps(payload), encoding="utf-8")
            corpus_path.write_text(json.dumps(corpus), encoding="utf-8")
            command = [sys.executable, str(SCRIPT), str(path), "--catalog", str(corpus_path), "--prune-orphans"]
            result = subprocess.run(command, capture_output=True, text=True)
            self.assertNotEqual(result.returncode, 0)
            self.assertIn("PRUNED: 2", result.stdout)
            remaining = json.loads(path.read_text())["terms"][0]
            self.assertEqual(remaining["observed_expressions"], [payload["terms"][0]["observed_expressions"][1]])
            # Candidate terms may retain sparse evidence after a re-merge.
            pruned = json.loads(path.read_text())
            pruned["terms"][0]["status"] = "candidate"
            path.write_text(json.dumps(pruned), encoding="utf-8")
            result = subprocess.run(command, capture_output=True, text=True)
            self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
            self.assertIn("PRUNED: 0", result.stdout)

    def test_prune_requires_catalog_without_mutating_ledger(self):
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "ledger.json"
            before = json.dumps(ledger())
            path.write_text(before, encoding="utf-8")
            result = subprocess.run([sys.executable, str(SCRIPT), str(path), "--prune-orphans"], capture_output=True, text=True)
            self.assertNotEqual(result.returncode, 0)
            self.assertEqual(path.read_text(), before)


if __name__ == "__main__":
    unittest.main()
