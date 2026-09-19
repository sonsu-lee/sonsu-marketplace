from __future__ import annotations

import copy
import json
import subprocess
import tempfile
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
VALIDATOR = ROOT / "scripts" / "validate_madia_design_catalog.py"
GATE_IDS = [f"M{index}" for index in range(9)]
CANONICAL_DISCOVERY_SOURCES = [
    "uploads-playlist:UUxRnfrmJAkRLarzeBJETB5g",
    "playlist:uxui:PLs8gZ5b9piXWi8j1bKnmMhTw7J39R2UzQ",
    "playlist:viewer-review:PLs8gZ5b9piXXortysLEQsFhWIA_lT3X7K",
    "playlist:follow-along:PLs8gZ5b9piXUuczVc_m-2ZJ5zcMMuJRLz",
    "playlist:design-information:PLs8gZ5b9piXUV9PMXNx6rbdFEfi_-JYgc",
    "playlist:design-tools:PLs8gZ5b9piXXqyPn0ruAStd5XPCPlcIMW",
    "channel-feed:UCxRnfrmJAkRLarzeBJETB5g",
]


def coder_evidence(phase: str) -> dict:
    population_size = 20 if phase == "pilot" else 3
    record_count = 20 if phase == "pilot" else 2
    records = []
    for index in range(record_count):
        relevance = "relevant" if index % 2 == 0 else "not_relevant"
        decision_stage = "information" if index % 2 == 0 else "interaction"
        evidence_kind = "verbalized" if index % 2 == 0 else "demonstrated"
        records.append(
            {
                "unit_id": f"video{index:06d}",
                "ratings": {
                    "relevance": {"coder-a": relevance, "coder-b": relevance},
                    "decision_stage": {
                        "coder-a": decision_stage,
                        "coder-b": decision_stage,
                    },
                    "evidence_kind": {
                        "coder-a": evidence_kind,
                        "coder-b": evidence_kind,
                    },
                },
            }
        )
    return {
        "schema_version": "madia-coder-evidence-v1",
        "phase": phase,
        "coders": ["coder-a", "coder-b"],
        "population_size": population_size,
        "records": records,
    }


def evidence_unit(
    unit_id: str,
    kind: str = "verbalized",
    project_id: str = "project-a",
) -> dict:
    return {
        "id": unit_id,
        "project_id": project_id,
        "timestamp_start": 10.0,
        "timestamp_end": 25.0,
        "problem": "Must-know information has no visible priority.",
        "action": "Reorders and groups the repeated item fields.",
        "rationale": "The viewer needs a stable order before comparing products.",
        "visible_effect": "The repeated item exposes the same priority across the list.",
        "user_task": "Compare repeated products.",
        "decision_stage": "information-and-representation",
        "evidence_kind": kind,
        "principle_candidate_ids": ["stable-repeated-unit"],
        "confidence": "high" if kind != "inferred" else "low",
        "source_locator": "https://www.youtube.com/watch?v=video000001&t=10s",
    }


def valid_catalog() -> dict:
    videos = []
    for index in range(20):
        video_id = f"video{index:06d}"
        analyzed = index < 3
        evidence_units = []
        if analyzed:
            unit = evidence_unit(
                f"{video_id}:001",
                project_id="project-a" if index < 2 else "project-b",
            )
            unit["source_locator"] = f"https://www.youtube.com/watch?v={video_id}&t=10s"
            evidence_units = [unit]
        videos.append(
            {
                "video_id": video_id,
                "title": f"Video {index}",
                "url": f"https://www.youtube.com/watch?v={video_id}",
                "published_at": "2026-09-17T00:00:00Z",
                "content_type": "long-form",
                "playlist_ids": ["uxui"],
                "status": "analyzed" if analyzed else "excluded",
                "exclusion_reason": None if analyzed else "Outside the UI/UX analysis scope.",
                "blocking_reason": None,
                "duplicate_of": None,
                "evidence_units": evidence_units,
            }
        )
    return {
        "schema_version": "madia-design-practice-catalog-v1",
        "as_of": "2026-09-17",
        "channel": {
            "id": "UCxRnfrmJAkRLarzeBJETB5g",
            "title": "Madia Designer",
            "url": "https://www.youtube.com/@uxuidesign",
        },
        "scope": "Every discovered public channel video is inventoried; UI/UX-relevant videos are analyzed.",
        "source_policy": {
            "public_only": True,
            "paid_or_membership_excluded": True,
            "metadata_is_not_principle_evidence": True,
        },
        "copyright": {"stores_full_transcripts": False, "stores_media": False},
        "inventory": {
            "discovery_complete": True,
            "discovery_sources": CANONICAL_DISCOVERY_SOURCES,
            "discovered_unique_videos": 20,
            "analyzed": 3,
            "excluded": 17,
            "blocked": 0,
            "pending": 0,
            "corpus_coverage": 1.0,
        },
        "reliability": {
            "pilot_sample_size": 20,
            "pilot_kappa": 1.0,
            "pilot_evidence": ["evidence/pilot-coder-records.json"],
            "production_double_coded_ratio": 2 / 3,
            "production_kappa": 1.0,
            "production_evidence": ["evidence/production-coder-records.json"],
        },
        "videos": videos,
        "principles": [
            {
                "id": "stable-repeated-unit",
                "label": "Define the repeated comparison unit before composing the full list.",
                "tier": "P3",
                "occurrence_ids": [f"video{index:06d}:001" for index in range(3)],
                "independent_projects": 2,
                "external_sources": [
                    {
                        "id": "wcag-info-relationships",
                        "title": "Understanding Info and Relationships",
                        "url": "https://www.w3.org/WAI/WCAG22/Understanding/info-and-relationships.html",
                        "source_type": "standard",
                    }
                ],
                "validation_status": "passed",
                "behavior_fixture": {
                    "fixture_id": "stable-repeated-unit-v1",
                    "run_id": "stable-repeated-unit-run-1",
                    "artifact_revision": "design-quality-behavior-v1",
                    "status": "passed",
                    "expected": ["Inspect must-know fields before composing repeated units."],
                    "must_not": ["Promote visual consistency without task evidence."],
                    "observed": ["Inspect must-know fields before composing repeated units."],
                    "evidence": ["evidence/stable-repeated-unit-run-1.json"],
                },
                "trigger": "A screen repeats comparable entities.",
                "inspect": "Check whether every item exposes the same must-know fields and order.",
                "decide": "Choose the smallest stable unit that supports the primary comparison.",
                "act": "Align field order, hierarchy and states in the repeated unit before composing the page.",
                "verify": "Run the declared comparison task with extreme and localized content.",
                "exceptions": ["Do not force identical units when entity types have different decision-critical fields."],
            }
        ],
        "quality_gates": [
            {"id": gate_id, "status": "passed", "evidence": [f"evidence/{gate_id.lower()}.md"]}
            for gate_id in GATE_IDS
        ],
    }


class MadiaCatalogValidatorTests(unittest.TestCase):
    def run_validator(
        self,
        payload: dict,
        *,
        materialize_evidence: bool = True,
        plain_coder_evidence: bool = False,
        coder_evidence_payloads: dict[str, dict] | None = None,
    ) -> subprocess.CompletedProcess[str]:
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "catalog.json"
            path.write_text(json.dumps(payload), encoding="utf-8")
            if materialize_evidence:
                def materialize(value: object, key: str | None = None) -> None:
                    if isinstance(value, dict):
                        for child_key, child in value.items():
                            materialize(child, child_key)
                    elif isinstance(value, list):
                        if key in {"evidence", "pilot_evidence", "production_evidence"}:
                            for relative in value:
                                if not isinstance(relative, str):
                                    continue
                                evidence_path = Path(tmp) / relative
                                evidence_path.parent.mkdir(parents=True, exist_ok=True)
                                if key in {"pilot_evidence", "production_evidence"}:
                                    if plain_coder_evidence:
                                        evidence_path.write_text("test evidence\n", encoding="utf-8")
                                    else:
                                        phase = "pilot" if key == "pilot_evidence" else "production"
                                        evidence_path.write_text(
                                            json.dumps(
                                                (coder_evidence_payloads or {}).get(
                                                    phase, coder_evidence(phase)
                                                )
                                            ),
                                            encoding="utf-8",
                                        )
                                else:
                                    evidence_path.write_text("test evidence\n", encoding="utf-8")
                        else:
                            for child in value:
                                materialize(child)

                materialize(payload)
            return subprocess.run(
                ["python3", str(VALIDATOR), str(path)],
                cwd=ROOT,
                text=True,
                capture_output=True,
                check=False,
            )

    def test_complete_supported_catalog_passes(self) -> None:
        result = self.run_validator(valid_catalog())
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)

    def test_m0_cannot_pass_with_pending_videos(self) -> None:
        payload = valid_catalog()
        payload["videos"][0]["status"] = "pending"
        payload["videos"][0]["evidence_units"] = []
        payload["inventory"].update(
            {"analyzed": 2, "excluded": 17, "pending": 1, "corpus_coverage": 19 / 20}
        )
        result = self.run_validator(payload)
        self.assertNotEqual(result.returncode, 0)
        self.assertIn("M0", result.stdout)

    def test_analyzed_video_requires_timestamped_evidence(self) -> None:
        payload = valid_catalog()
        payload["videos"][0]["evidence_units"] = []
        result = self.run_validator(payload)
        self.assertNotEqual(result.returncode, 0)
        self.assertIn("analyzed", result.stdout)

    def test_excluded_video_requires_reason(self) -> None:
        payload = valid_catalog()
        payload["videos"][0]["status"] = "excluded"
        payload["videos"][0]["evidence_units"] = []
        payload["inventory"].update({"analyzed": 2, "excluded": 18})
        result = self.run_validator(payload)
        self.assertNotEqual(result.returncode, 0)
        self.assertIn("exclusion_reason", result.stdout)

    def test_inferred_or_metadata_only_occurrences_cannot_reach_p1(self) -> None:
        payload = valid_catalog()
        for video in payload["videos"]:
            if not video["evidence_units"]:
                continue
            video["evidence_units"][0]["evidence_kind"] = "inferred"
            video["evidence_units"][0]["confidence"] = "low"
        payload["principles"][0]["tier"] = "P1"
        payload["principles"][0]["external_sources"] = []
        payload["principles"][0]["validation_status"] = "not_run"
        result = self.run_validator(payload)
        self.assertNotEqual(result.returncode, 0)
        self.assertIn("direct observation", result.stdout)

    def test_p1_requires_three_nonduplicate_occurrences_and_two_projects(self) -> None:
        payload = valid_catalog()
        principle = payload["principles"][0]
        principle["tier"] = "P1"
        principle["occurrence_ids"] = principle["occurrence_ids"][:2]
        principle["independent_projects"] = 1
        principle["external_sources"] = []
        principle["validation_status"] = "not_run"
        result = self.run_validator(payload)
        self.assertNotEqual(result.returncode, 0)
        self.assertIn("three", result.stdout)
        self.assertIn("two projects", result.stdout)

    def test_p2_requires_external_source(self) -> None:
        payload = valid_catalog()
        payload["principles"][0]["tier"] = "P2"
        payload["principles"][0]["external_sources"] = []
        payload["principles"][0]["validation_status"] = "not_run"
        result = self.run_validator(payload)
        self.assertNotEqual(result.returncode, 0)
        self.assertIn("external_sources", result.stdout)

    def test_p3_requires_passed_behavior_validation_and_operational_fields(self) -> None:
        payload = valid_catalog()
        payload["principles"][0]["validation_status"] = "not_run"
        payload["principles"][0]["verify"] = ""
        result = self.run_validator(payload)
        self.assertNotEqual(result.returncode, 0)
        self.assertIn("P3", result.stdout)

    def test_m3_requires_declared_reliability_thresholds(self) -> None:
        payload = valid_catalog()
        payload["reliability"]["pilot_kappa"] = 0.5
        result = self.run_validator(payload)
        self.assertNotEqual(result.returncode, 0)
        self.assertIn("M3", result.stdout)

    def test_m3_rejects_impossible_reliability_values(self) -> None:
        payload = valid_catalog()
        payload["reliability"].update(
            {
                "pilot_kappa": 2.0,
                "production_double_coded_ratio": 2.0,
                "production_kappa": 2.0,
            }
        )
        result = self.run_validator(payload)
        self.assertNotEqual(result.returncode, 0)
        self.assertIn("between", result.stdout)

    def test_passed_milestone_evidence_must_exist(self) -> None:
        result = self.run_validator(valid_catalog(), materialize_evidence=False)
        self.assertNotEqual(result.returncode, 0)
        self.assertIn("does not identify a file", result.stdout)

    def test_external_sources_must_be_verifiable_https_records(self) -> None:
        payload = valid_catalog()
        payload["principles"][0]["external_sources"] = ["not-a-source"]
        result = self.run_validator(payload)
        self.assertNotEqual(result.returncode, 0)
        self.assertIn("external_sources", result.stdout)

    def test_external_source_must_be_independent_from_catalog_videos(self) -> None:
        payload = valid_catalog()
        payload["principles"][0]["external_sources"][0]["url"] = payload["videos"][0]["url"]
        result = self.run_validator(payload)
        self.assertNotEqual(result.returncode, 0)
        self.assertIn("independent", result.stdout)

        payload = valid_catalog()
        video_id = payload["videos"][0]["video_id"]
        payload["principles"][0]["external_sources"][0][
            "url"
        ] = f"https://www.youtube.com/embed/{video_id}"
        result = self.run_validator(payload)
        self.assertNotEqual(result.returncode, 0)
        self.assertIn("independent", result.stdout)

    def test_principle_occurrence_must_link_back_to_the_candidate(self) -> None:
        payload = valid_catalog()
        payload["videos"][0]["evidence_units"][0]["principle_candidate_ids"] = []
        result = self.run_validator(payload)
        self.assertNotEqual(result.returncode, 0)
        self.assertIn("principle_candidate_ids", result.stdout)

    def test_same_video_and_project_edits_are_one_recurrence_case(self) -> None:
        payload = valid_catalog()
        duplicate = copy.deepcopy(payload["videos"][0]["evidence_units"][0])
        duplicate["id"] = "video000000:002"
        payload["videos"][0]["evidence_units"].append(duplicate)
        payload["principles"][0]["occurrence_ids"] = [
            "video000000:001",
            "video000000:002",
            "video000002:001",
        ]
        result = self.run_validator(payload)
        self.assertNotEqual(result.returncode, 0)
        self.assertIn("independent recurrence", result.stdout)

    def test_reliability_shape_is_validated_before_m3_runs(self) -> None:
        payload = valid_catalog()
        payload["principles"][0]["tier"] = "P0"
        payload["quality_gates"][3] = {"id": "M3", "status": "not_run", "evidence": []}
        payload["reliability"]["pilot_sample_size"] = {"unexpected": "object"}
        result = self.run_validator(payload)
        self.assertNotEqual(result.returncode, 0)
        self.assertIn("reliability.pilot_sample_size", result.stdout)

    def test_behavior_fixture_observations_must_satisfy_the_oracle(self) -> None:
        payload = valid_catalog()
        fixture = payload["principles"][0]["behavior_fixture"]
        fixture["observed"] = ["An unrelated behavior occurred."]
        result = self.run_validator(payload)
        self.assertNotEqual(result.returncode, 0)
        self.assertIn("expected observations", result.stdout)

        payload = valid_catalog()
        fixture = payload["principles"][0]["behavior_fixture"]
        fixture["observed"].append(fixture["must_not"][0])
        result = self.run_validator(payload)
        self.assertNotEqual(result.returncode, 0)
        self.assertIn("prohibited observations", result.stdout)

    def test_p3_requires_behavior_fixture_execution_receipt(self) -> None:
        payload = valid_catalog()
        payload["principles"][0]["behavior_fixture"] = None
        result = self.run_validator(payload)
        self.assertNotEqual(result.returncode, 0)
        self.assertIn("behavior_fixture", result.stdout)

    def test_m3_requires_coder_level_evidence_artifacts(self) -> None:
        payload = valid_catalog()
        payload["reliability"]["pilot_evidence"] = []
        payload["reliability"]["production_evidence"] = []
        result = self.run_validator(payload)
        self.assertNotEqual(result.returncode, 0)
        self.assertIn("coder evidence", result.stdout)

    def test_m3_rejects_unstructured_coder_evidence(self) -> None:
        result = self.run_validator(valid_catalog(), plain_coder_evidence=True)
        self.assertNotEqual(result.returncode, 0)
        self.assertIn("coder evidence", result.stdout)

    def test_m3_recomputes_declared_kappa_and_double_coded_ratio(self) -> None:
        payload = valid_catalog()
        payload["reliability"]["pilot_kappa"] = 0.9
        payload["reliability"]["production_kappa"] = 0.9
        payload["reliability"]["production_double_coded_ratio"] = 0.3
        result = self.run_validator(payload)
        self.assertNotEqual(result.returncode, 0)
        self.assertIn("computed", result.stdout)

    def test_m3_coder_units_are_bound_to_catalog_videos(self) -> None:
        pilot = coder_evidence("pilot")
        pilot["records"][0]["unit_id"] = "foreign-video"
        result = self.run_validator(
            valid_catalog(),
            coder_evidence_payloads={
                "pilot": pilot,
                "production": coder_evidence("production"),
            },
        )
        self.assertNotEqual(result.returncode, 0)
        self.assertIn("outside the catalog sampling population", result.stdout)

    def test_m3_population_size_is_recomputed_from_catalog(self) -> None:
        payload = valid_catalog()
        production = coder_evidence("production")
        production["population_size"] = 4
        payload["reliability"]["production_double_coded_ratio"] = 0.5
        result = self.run_validator(
            payload,
            coder_evidence_payloads={
                "pilot": coder_evidence("pilot"),
                "production": production,
            },
        )
        self.assertNotEqual(result.returncode, 0)
        self.assertIn("population_size must equal", result.stdout)

    def test_symlink_loop_evidence_path_fails_without_traceback(self) -> None:
        payload = valid_catalog()
        payload["quality_gates"][0]["evidence"] = ["evidence/loop-a"]
        with tempfile.TemporaryDirectory() as tmp:
            base = Path(tmp)
            evidence = base / "evidence"
            evidence.mkdir()
            (evidence / "loop-a").symlink_to("loop-b")
            (evidence / "loop-b").symlink_to("loop-a")
            path = base / "catalog.json"
            path.write_text(json.dumps(payload), encoding="utf-8")
            result = subprocess.run(
                ["python3", str(VALIDATOR), str(path)],
                cwd=ROOT,
                text=True,
                capture_output=True,
                check=False,
            )
        self.assertNotEqual(result.returncode, 0)
        self.assertIn("inside the catalog directory", result.stdout)
        self.assertNotIn("Traceback", result.stderr)

    def test_failed_behavior_fixture_preserves_observed_failure_receipt(self) -> None:
        payload = valid_catalog()
        principle = payload["principles"][0]
        principle["tier"] = "P2"
        principle["validation_status"] = "failed"
        fixture = principle["behavior_fixture"]
        fixture["status"] = "failed"
        fixture["observed"] = ["The repeated unit remained ambiguous."]
        result = self.run_validator(payload)
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)

    def test_channel_and_discovery_sources_are_bound_to_canonical_manifest(self) -> None:
        payload = valid_catalog()
        payload["channel"]["url"] = "https://www.youtube.com/@another-channel"
        result = self.run_validator(payload)
        self.assertNotEqual(result.returncode, 0)
        self.assertIn("canonical source manifest", result.stdout)

        payload = valid_catalog()
        payload["inventory"]["discovery_sources"] = ["uploads-playlist"]
        result = self.run_validator(payload)
        self.assertNotEqual(result.returncode, 0)
        self.assertIn("canonical source manifest", result.stdout)

    def test_full_transcripts_and_media_must_not_be_stored(self) -> None:
        payload = valid_catalog()
        payload["copyright"]["stores_full_transcripts"] = True
        result = self.run_validator(payload)
        self.assertNotEqual(result.returncode, 0)
        self.assertIn("full transcripts", result.stdout)

    def test_video_url_must_be_a_supported_youtube_video_url(self) -> None:
        payload = valid_catalog()
        video_id = payload["videos"][0]["video_id"]
        payload["videos"][0]["url"] = f"https://example.com/watch/{video_id}"
        result = self.run_validator(payload)
        self.assertNotEqual(result.returncode, 0)
        self.assertIn("url must identify", result.stdout)

    def test_promoted_principle_requires_its_research_milestones(self) -> None:
        payload = valid_catalog()
        payload["quality_gates"][7] = {"id": "M7", "status": "not_run", "evidence": []}
        result = self.run_validator(payload)
        self.assertNotEqual(result.returncode, 0)
        self.assertIn("requires passed research milestones", result.stdout)

    def test_independent_project_count_is_derived_from_evidence(self) -> None:
        payload = valid_catalog()
        payload["principles"][0]["independent_projects"] = 3
        result = self.run_validator(payload)
        self.assertNotEqual(result.returncode, 0)
        self.assertIn("project ids", result.stdout)

    def test_unknown_principle_candidate_is_rejected(self) -> None:
        payload = valid_catalog()
        payload["videos"][0]["evidence_units"][0]["principle_candidate_ids"] = ["unknown"]
        result = self.run_validator(payload)
        self.assertNotEqual(result.returncode, 0)
        self.assertIn("unknown principle candidate", result.stdout)

    def test_malformed_nested_values_fail_without_traceback(self) -> None:
        payload = valid_catalog()
        payload["videos"][0]["evidence_units"][0]["evidence_kind"] = {"bad": True}
        result = self.run_validator(payload)
        self.assertNotEqual(result.returncode, 0)
        self.assertIn("evidence_kind", result.stdout)
        self.assertNotIn("Traceback", result.stderr)

    def test_very_large_numbers_fail_without_traceback(self) -> None:
        payload = valid_catalog()
        payload["reliability"]["pilot_kappa"] = 10**1000
        result = self.run_validator(payload)
        self.assertNotEqual(result.returncode, 0)
        self.assertIn("M3", result.stdout)
        self.assertNotIn("Traceback", result.stderr)

    def test_malformed_urls_fail_without_traceback(self) -> None:
        payload = valid_catalog()
        payload["videos"][0]["url"] = "https://[::1"
        result = self.run_validator(payload)
        self.assertNotEqual(result.returncode, 0)
        self.assertNotIn("Traceback", result.stderr)

        payload = valid_catalog()
        payload["principles"][0]["external_sources"][0]["url"] = "https://[::1"
        result = self.run_validator(payload)
        self.assertNotEqual(result.returncode, 0)
        self.assertNotIn("Traceback", result.stderr)


if __name__ == "__main__":
    unittest.main()
