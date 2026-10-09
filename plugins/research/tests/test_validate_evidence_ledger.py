"""Subprocess contract tests for structural evidence validation."""

import copy
import json
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest


SCRIPT = Path(__file__).resolve().parents[1] / "scripts/validate_evidence_ledger.py"


def ledger():
    return {
        "claims": [{"claim_id": "C1", "claim": "Archive retains seven revisions.", "claim_kind": "fact", "coverage_status": "supported"}],
        "evidence": [{
            "claim_id": "C1",
            "source": {"url": "https://example.org/archive", "title": "Archive manual", "author_or_org": "Archive team"},
            "source_identity": {"kind": "public_url", "value": "https://example.org/archive"},
            "access_scope": "public", "version_or_content_hash": "v3", "reopen_method": "open canonical URL",
            "version_or_commit": "v3", "locator": "Retention, paragraph 2", "support_relation": "direct",
            "source_role": "product manual", "independence": "vendor", "limitations": "", "conflicts": "",
            "confidence": "medium", "verified": True,
        }],
    }


class EvidenceLedgerTests(unittest.TestCase):
    def run_ledger(self, data):
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "ledger.json"
            path.write_text(json.dumps(data), encoding="utf-8")
            result = subprocess.run([sys.executable, "-B", str(SCRIPT), str(path)], capture_output=True, text=True)
            return result.returncode, json.loads(result.stdout)

    def assert_violation(self, data, code):
        status, result = self.run_ledger(data)
        self.assertEqual(status, 1)
        self.assertFalse(result["valid"])
        self.assertIn(code, [item["code"] for item in result["violations"]])

    def test_valid_multiple_sources_and_explicit_unsupported_claim(self):
        data = ledger()
        other = copy.deepcopy(data["evidence"][0])
        other["support_relation"] = "opposes"
        other["verified"] = False
        data["evidence"].append(other)
        data["claims"].append({"claim_id": "C2", "claim": "Unverified scale limit", "claim_kind": "inference", "coverage_status": "unsupported"})
        status, result = self.run_ledger(data)
        self.assertEqual(status, 0)
        self.assertEqual((result["claims"], result["evidence"]), (2, 2))

    def test_required_fields(self):
        for section in ("claims", "evidence"):
            for field in ledger()[section][0]:
                with self.subTest(section=section, field=field):
                    data = ledger()
                    del data[section][0][field]
                    status, _ = self.run_ledger(data)
                    self.assertEqual(status, 1)

    def test_enums(self):
        for section, fields in (("claims", ("claim_kind", "coverage_status")), ("evidence", ("access_scope", "support_relation", "confidence"))):
            for field in fields:
                for value in ("invalid", None, [], {}):
                    with self.subTest(field=field, value=value):
                        data = ledger()
                        data[section][0][field] = value
                        self.assert_violation(data, "invalid-enum")

    def test_claim_links_and_duplicates(self):
        data = ledger()
        data["evidence"][0]["claim_id"] = "C9"
        self.assert_violation(data, "unknown-claim")
        self.assert_violation(data, "missing-evidence")
        data = ledger()
        data["claims"].append(copy.deepcopy(data["claims"][0]))
        self.assert_violation(data, "duplicate-claim")

    def test_locator_and_verified_types(self):
        for locator in (None, "", "  ", []):
            data = ledger()
            data["evidence"][0]["locator"] = locator
            self.assert_violation(data, "missing-locator")
        for value in (1, "true", None):
            data = ledger()
            data["evidence"][0]["verified"] = value
            self.assert_violation(data, "invalid-field")

    def test_private_and_local_sources_need_no_public_url(self):
        for scope, kind in (("private", "connector_item_id"), ("local", "local_path_content_hash"), ("local", "repository_commit_path")):
            data = ledger()
            entry = data["evidence"][0]
            entry["access_scope"] = scope
            entry["source"]["url"] = None
            entry["source_identity"] = {"kind": kind, "value": "safe-internal-locator"}
            self.assertEqual(self.run_ledger(data)[0], 0)
        data = ledger()
        data["evidence"][0]["source"]["url"] = None
        self.assert_violation(data, "invalid-field")

    def test_source_identity_and_dates(self):
        data = ledger()
        data["evidence"][0]["source_identity"]["kind"] = "title"
        self.assert_violation(data, "invalid-enum")
        for date in (None, "", 42):
            data = ledger()
            data["evidence"][0]["version_or_commit"] = date
            self.assert_violation(data, "missing-date-or-version")
        data = ledger()
        del data["evidence"][0]["version_or_commit"]
        data["evidence"][0]["accessed_at"] = "2026-01-10"
        self.assertEqual(self.run_ledger(data)[0], 0)

    def test_malformed_shapes(self):
        for data in (None, [], {}, {"claims": {}, "evidence": []}, {"claims": [1], "evidence": [None]}):
            self.assert_violation(data, "invalid-field")

    def test_source_truth_is_outside_validator(self):
        data = ledger()
        data["claims"][0]["claim"] = "This deliberately unrelated claim is not semantically checked."
        self.assertEqual(self.run_ledger(data)[0], 0)

    def test_stdin_and_read_errors(self):
        result = subprocess.run([sys.executable, "-B", str(SCRIPT), "-"], input=json.dumps(ledger()), capture_output=True, text=True)
        self.assertEqual(result.returncode, 0)
        result = subprocess.run([sys.executable, "-B", str(SCRIPT), "-"], input="{", capture_output=True, text=True)
        self.assertEqual(result.returncode, 2)
        self.assertEqual(result.stdout, "")
        with tempfile.TemporaryDirectory() as directory:
            result = subprocess.run([sys.executable, "-B", str(SCRIPT), str(Path(directory) / "absent")], capture_output=True, text=True)
            self.assertEqual(result.returncode, 2)


if __name__ == "__main__":
    unittest.main()
