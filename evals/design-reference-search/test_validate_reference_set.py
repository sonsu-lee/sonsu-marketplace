from __future__ import annotations

import copy
import json
import re
import subprocess
import tempfile
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
VALIDATOR = ROOT / "plugins" / "design" / "scripts" / "validate_design_quality.py"
SHARED = ROOT / "shared" / "design-quality"
CONTRACT_DOC = ROOT / "plugins" / "design" / "references" / "reference-search.md"


def found_reference(**overrides: object) -> dict:
    reference = {
        "id": "ref-1",
        "origin": "agent_found",
        "provider": "mobbin",
        "query_id": "q-flow",
        "locator": "https://mobbin.com/flows/signup-1",
        "title": "Example app sign-up",
        "source_kind": "shipped_product",
        "platform": "ios",
        "layer": "flow",
        "inspection": "image",
        "observed": "The code screen offers resend and edit-email side by side.",
        "relevance": "Our flow loses users at the same verification step.",
        "borrow": ["resend and edit-email pairing"],
        "do_not_borrow": ["brand illustration"],
        "attribution": "Example app via Mobbin",
        "retrieved_at": "2026-09-29T09:00:00Z",
    }
    reference.update(overrides)
    return reference


def valid_reference_set() -> dict:
    return {
        "schema_version": "design-reference-set-v1",
        "id": "signup-ios-references",
        "created_at": "2026-09-29T09:05:00Z",
        "brief": "iOS sign-up recovery patterns",
        "status": "selected",
        "providers": [
            {"name": "mobbin", "status": "used"},
            {"name": "refero", "status": "unauthorized", "note": "connector not signed in"},
        ],
        "queries": [
            {"id": "q-flow", "layer": "flow", "provider": "mobbin", "text": "sign up flow with email verification"}
        ],
        "primary_id": "ref-1",
        "items": [
            found_reference(),
            {
                "id": "ref-2",
                "origin": "user_supplied",
                "provider": "user",
                "locator": "references/current-competitor.png",
                "title": "Competitor sign-up supplied by the user",
                "source_kind": "unknown",
                "platform": "ios",
                "layer": "screen",
                "inspection": "image",
                "observed": "Progress is shown as a numbered stepper.",
                "relevance": "The user wants to compare progress indication.",
                "borrow": ["numbered progress"],
                "do_not_borrow": [],
                "attribution": "Provided by the user",
                "retrieved_at": "2026-09-29T09:00:00Z",
            },
        ],
    }


class ReferenceSetValidatorTests(unittest.TestCase):
    def run_validator(self, payload: object, *records: str) -> subprocess.CompletedProcess[str]:
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "references.json"
            path.write_text(json.dumps(payload), encoding="utf-8")
            arguments = ["python3", str(VALIDATOR), "references", str(path)]
            for index, record in enumerate(records):
                record_path = Path(tmp) / f"record-{index}.txt"
                record_path.write_text(record, encoding="utf-8")
                arguments += ["--provenance", str(record_path)]
            return subprocess.run(arguments, cwd=ROOT, text=True, capture_output=True, check=False)

    def assert_accepted(self, payload: object, *records: str) -> None:
        result = self.run_validator(payload, *records)
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)

    def assert_rejected(self, payload: object, message: str, *records: str) -> None:
        result = self.run_validator(payload, *records)
        self.assertEqual(result.returncode, 1, result.stdout + result.stderr)
        self.assertIn(message, result.stdout)
        self.assertNotIn("Traceback", result.stderr)

    def test_valid_reference_set_passes(self) -> None:
        self.assert_accepted(valid_reference_set())

    def test_documented_example_passes(self) -> None:
        example = re.search(r"```json\n(.*?)\n```", CONTRACT_DOC.read_text(encoding="utf-8"), re.S)
        self.assertIsNotNone(example)
        self.assert_accepted(json.loads(example.group(1)))

    def test_found_reference_requires_a_used_provider(self) -> None:
        payload = valid_reference_set()
        payload["providers"][0]["status"] = "failed"
        self.assert_rejected(payload, "items[0].provider must name a provider with status used")

    def test_found_reference_requires_a_recorded_query_from_the_same_provider(self) -> None:
        payload = valid_reference_set()
        payload["items"][0]["query_id"] = "q-unknown"
        self.assert_rejected(payload, "items[0].query_id references an unknown query")
        payload = valid_reference_set()
        payload["queries"][0]["provider"] = "refero"
        self.assert_rejected(payload, "does not match the provider of query q-flow")

    def test_user_supplied_reference_uses_the_reserved_provider(self) -> None:
        payload = valid_reference_set()
        payload["items"][1]["provider"] = "mobbin"
        self.assert_rejected(payload, "items[1].provider must be 'user'")
        payload = valid_reference_set()
        payload["providers"].append({"name": "user", "status": "used"})
        self.assert_rejected(payload, "is reserved for user-supplied references")

    def test_found_reference_locator_must_be_a_url_or_provider_id(self) -> None:
        for locator in ("references/local.png", "file:///tmp/shot.png", "C:\\shots\\a.png", "https://"):
            payload = valid_reference_set()
            payload["items"][0]["locator"] = locator
            self.assert_rejected(payload, "items[0].locator must be an http(s) URL, a provider-scoped id")
        payload = valid_reference_set()
        payload["items"][0]["locator"] = "mobbin:flow/signup-1"
        self.assert_accepted(payload)

    def test_found_reference_provider_id_must_use_its_provider_scheme(self) -> None:
        payload = valid_reference_set()
        payload["items"][0]["locator"] = "refero:screen/stolen"
        self.assert_rejected(payload, "items[0].locator scheme must match its provider")
        payload["items"][0]["locator"] = "MOBBIN:screen/signup-1"
        self.assert_accepted(payload)

    def test_locator_with_lone_surrogate_is_rejected_without_traceback(self) -> None:
        for locator in (
            "https://mobbin.com/flows/signup-1?screen=\ud800",
            "https://mobbin.com/flows/signup-1?\udfff=screen",
        ):
            with self.subTest(locator=ascii(locator)):
                payload = valid_reference_set()
                payload["items"][0]["locator"] = locator
                self.assert_rejected(payload, "items[0].locator must be")

    def test_reference_timestamps_require_rfc3339_grammar(self) -> None:
        for field in ("retrieved_at", "created_at"):
            for value in (
                "2026-09-29\U0001f60009:00:00Z",
                "20260929T090000Z",
                "2026-09-29T09:00Z",
                "2026-09-29T09:00:00+0900",
                "2026-09-29T09:00:00+09:00:30",
            ):
                with self.subTest(field=field, value=value):
                    payload = valid_reference_set()
                    target = payload["items"][0] if field == "retrieved_at" else payload
                    target[field] = value
                    self.assert_rejected(payload, f"{field} must be")

    def test_reference_timestamps_accept_rfc3339_case_and_offsets(self) -> None:
        for value in (
            "2026-09-29t09:00:00z",
            "2026-09-29T09:00:00.123456Z",
            "2026-09-29t09:00:00+09:00",
            "2026-09-29T09:00:00-00:00",
        ):
            with self.subTest(value=value):
                payload = valid_reference_set()
                payload["items"][0]["retrieved_at"] = value
                payload["created_at"] = value
                self.assert_accepted(payload)

    def test_duplicate_locators_are_detected_after_normalization(self) -> None:
        payload = valid_reference_set()
        payload["primary_id"] = "ref-1"
        payload["items"][1] = found_reference(
            id="ref-3",
            locator="https://www.Mobbin.com:443/flows/signup-1/?utm_source=feed&ref=home#top",
            borrow=[],
        )
        self.assert_rejected(payload, "items[1].locator duplicates ref-1 after normalization")

    def test_primary_reference_must_be_inspected_and_borrowed(self) -> None:
        payload = valid_reference_set()
        payload["items"][0]["inspection"] = "metadata_only"
        payload["items"][0]["borrow"] = []
        self.assert_rejected(payload, "primary_id cannot reference a metadata_only reference")
        payload = valid_reference_set()
        payload["items"][0]["borrow"] = []
        self.assert_rejected(payload, "primary reference ref-1 must declare what to borrow")
        payload = valid_reference_set()
        del payload["primary_id"]
        self.assert_rejected(payload, "primary_id must reference an item when status is selected")

    def test_metadata_only_reference_cannot_be_borrowed(self) -> None:
        payload = valid_reference_set()
        payload["items"][1]["inspection"] = "metadata_only"
        self.assert_rejected(payload, "items[1].borrow must be empty for metadata_only references")

    def test_secondary_reference_borrow_is_bounded(self) -> None:
        payload = valid_reference_set()
        payload["items"][1]["borrow"] = ["stepper", "button shape", "copy tone"]
        self.assert_rejected(payload, "items ref-2 borrows more than 2 details")
        payload["primary_id"] = "ref-2"
        payload["items"][0]["borrow"] = ["one detail"]
        self.assert_accepted(payload)

    def test_no_verified_match_reports_attempts_without_found_references(self) -> None:
        payload = valid_reference_set()
        payload.update(
            {
                "status": "no_verified_match",
                "providers": [
                    {"name": "mobbin", "status": "unavailable"},
                    {"name": "web", "status": "used"},
                ],
                "queries": [{"id": "q-web", "layer": "screen", "provider": "web", "text": "passkey sign in screen"}],
                "items": [],
            }
        )
        del payload["primary_id"]
        self.assert_accepted(payload)
        invented = copy.deepcopy(payload)
        invented["items"] = [found_reference(provider="web", query_id="q-web")]
        self.assert_rejected(invented, "cannot contain agent_found references when status is no_verified_match")
        with_primary = copy.deepcopy(payload)
        with_primary["primary_id"] = "ref-1"
        self.assert_rejected(with_primary, "primary_id is only valid when status is selected")
        silent = copy.deepcopy(payload)
        silent["providers"] = []
        silent["queries"] = []
        self.assert_rejected(silent, "providers must record the attempted paths")

    def test_no_verified_match_requires_a_non_skipped_attempt(self) -> None:
        payload = valid_reference_set()
        payload.update(status="no_verified_match", items=[], queries=[])
        del payload["primary_id"]
        for status in ("skipped", "used"):
            with self.subTest(status=status):
                payload["providers"] = [{"name": "mobbin", "status": status}]
                self.assert_rejected(payload, "providers must record the attempted paths")
        for status in ("unavailable", "unauthorized", "failed"):
            with self.subTest(status=status):
                payload["providers"] = [{"name": "mobbin", "status": status}]
                self.assert_accepted(payload)
        payload["providers"] = [{"name": "mobbin", "status": "skipped"}]
        payload["queries"] = valid_reference_set()["queries"]
        self.assert_rejected(payload, "providers must record the attempted paths")

    def test_provenance_accepts_locators_seen_in_tool_output(self) -> None:
        record = "search_screens -> https://www.mobbin.com/flows/signup-1?utm_campaign=mcp."
        self.assert_accepted(valid_reference_set(), record)

    def test_provenance_preserves_valid_locator_punctuation(self) -> None:
        for locator in (
            "https://mobbin.com/flows/sign,up",
            "https://mobbin.com/flows/signup_(ios)",
            "https://mobbin.com/flows/signup!",
            "mobbin:flow/sign,up_(ios)!",
        ):
            with self.subTest(locator=locator):
                payload = valid_reference_set()
                payload["items"][0]["locator"] = locator
                self.assert_accepted(payload, f"search_screens -> {locator}")
                self.assert_accepted(payload, f"[{locator}]({locator})")
                self.assert_accepted(payload, f'{{"locator": "{locator}"}}')
                self.assert_accepted(payload, f"result ({locator}).")
        payload = valid_reference_set()
        payload["items"][0]["locator"] = "https://mobbin.com/flows/sign,up_(ios)!"
        self.assert_accepted(
            payload,
            "https://www.Mobbin.com:443/flows/sign,up_(ios)!/?utm_source=mcp#top",
        )

    def test_provenance_rejects_locators_missing_from_tool_output(self) -> None:
        record = "search_screens -> https://mobbin.com/flows/other-flow"
        self.assert_rejected(
            valid_reference_set(),
            "items[0].locator does not appear in the provenance record: https://mobbin.com/flows/signup-1",
            record,
        )

    def test_provenance_rejects_a_locator_that_only_prefixes_a_seen_url(self) -> None:
        for record in (
            "search_screens -> https://mobbin.com/flows/signup-12 (Example app)",
            "[Example app](https://mobbin.com/flows/signup-12)",
            "result (https://mobbin.com/flows/signup-12).",
            "https://mobbin.com/flows/signup-12?utm_source=mcp",
            "https://mobbin.com/flows/signup-1,2",
            "https://mobbin.com/flows/signup-1(ios)",
        ):
            with self.subTest(record=record):
                self.assert_rejected(
                    valid_reference_set(),
                    "items[0].locator does not appear in the provenance record",
                    record,
                )

    def test_provenance_does_not_require_user_supplied_locators(self) -> None:
        record = "https://mobbin.com/flows/signup-1"
        self.assertNotIn("current-competitor", record)
        self.assert_accepted(valid_reference_set(), record)

    def test_malformed_values_fail_without_traceback(self) -> None:
        for mutate in (
            lambda payload: payload.update({"items": [1, None]}),
            lambda payload: payload.update({"providers": "mobbin"}),
            lambda payload: payload.update({"queries": [{"id": ["q"], "provider": {"x": 1}}]}),
            lambda payload: payload["items"][0].update({"locator": 5, "borrow": None, "task_ids": "t"}),
            lambda payload: payload["items"][0].update({"provider": ["mobbin"], "query_id": {"a": 1}}),
            lambda payload: payload.update({"primary_id": ["ref-1"]}),
        ):
            payload = valid_reference_set()
            mutate(payload)
            result = self.run_validator(payload)
            self.assertEqual(result.returncode, 1, result.stdout + result.stderr)
            self.assertNotIn("Traceback", result.stderr)
        result = self.run_validator(["not", "an", "object"])
        self.assertEqual(result.returncode, 1)
        self.assertIn("reference set must be a JSON object", result.stdout)

    def test_standalone_schema_matches_contract_reference_definitions(self) -> None:
        contract = json.loads((SHARED / "design-decision-contract.schema.json").read_text(encoding="utf-8"))
        standalone = json.loads((SHARED / "design-reference-set.schema.json").read_text(encoding="utf-8"))
        self.assertEqual(
            contract["$defs"]["contractExtensions"]["properties"]["references"],
            {"$ref": "#/$defs/referenceSet"},
        )
        for name, definition in standalone["$defs"].items():
            self.assertEqual(definition, contract["$defs"][name], name)
        reference_set = contract["$defs"]["referenceSet"]
        for field, definition in reference_set["properties"].items():
            self.assertEqual(standalone["properties"][field], definition, field)
        for keyword in ("if", "then", "else"):
            self.assertEqual(standalone[keyword], reference_set[keyword], keyword)
        self.assertEqual(standalone["properties"]["schema_version"], {"const": "design-reference-set-v1"})


if __name__ == "__main__":
    unittest.main()
