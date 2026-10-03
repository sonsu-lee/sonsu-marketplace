from __future__ import annotations

import copy
import hashlib
import importlib.util
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
SPEC = importlib.util.spec_from_file_location("madia_catalog_validator", VALIDATOR)
validator = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(validator)


def coder_evidence(phase: str) -> dict:
    population_size = 20 if phase == "pilot" else 3
    record_count = 20 if phase == "pilot" else 2
    records = []
    for index in range(record_count):
        relevance = "direct_design_work" if index % 2 == 0 else "not_relevant"
        decision_stage = "information_priority" if index % 2 == 0 else "visual_system"
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
    project_id: str = "madia-proj-a",
) -> dict:
    return {
        "id": unit_id,
        "project_id": project_id,
        "timestamp_start": 10.0,
        "timestamp_end": 25.0,
        "problem": "Must-know information has no visible priority.",
        "action": "Reorders and groups the repeated item fields.",
        "rationale": ("[해석] " if kind == "inferred" else "") + "비교 전에 안정적인 읽기 순서가 필요하다.",
        "visible_effect": "The repeated item exposes the same priority across the list.",
        "user_task": "Compare repeated products.",
        "decision_stage": "information_priority",
        "evidence_kind": kind,
        "principle_candidate_ids": ["stable-repeated-unit"],
        "confidence": "high" if kind != "inferred" else "low",
        "source_locator": f"https://www.youtube.com/watch?v={unit_id.split(':')[0]}&t=10s",
        "speech_excerpt": None if kind == "inferred" else "비교할 때 순서가 같아야 편해요.",
        "context": {"platform": "web", "surface": "commerce"},
        "term_ids": [],
        "visual_evidence": [
            {"frame_time": 10.0, "role": "before" if kind == "demonstrated" else "context",
             "region": [0.1, 0.1, 0.8, 0.8], "observation": "상품 정보가 같은 순서로 배치되어 있다.",
             "legibility": "clear"},
        ] + ([
            {"frame_time": 24.0, "role": "after", "region": None,
             "observation": "상품 정보의 순서가 정리되었다.", "legibility": "clear"},
        ] if kind == "demonstrated" else []),
        "verification": {
            "status": "confirmed", "verifier": "pilot-verifier", "note": None,
            "checks": ["target", "attribution"] + ([] if kind == "inferred" else ["speech"])
            + (["change"] if kind == "demonstrated" else []),
        },
    }


def analysis_receipt() -> dict:
    return {
        "codebook_version": "codebook-v1",
        "coders": ["coder-a", "coder-b", "adjudicator"],
        "sessions": {"coder-a": "pilot-coder-a", "coder-b": "pilot-coder-b",
                     "adjudicator": "pilot-adjudicator", "verifier": "pilot-verifier"},
        "caption_source": "manual", "sheets_total": 2, "sheets_viewed": 2,
    }


def human_audit() -> dict:
    records = [
        {"target_type": "pilot_video", "target_id": f"video{index:06d}",
         "codebook_version": "codebook-v1", "verdict": "confirmed",
         "note": None, "audited_at": "2026-10-03"}
        for index in range(20)
    ]
    records += [
        {"target_type": "principle_occurrence",
         "target_id": f"stable-repeated-unit|video{index:06d}:001",
         "codebook_version": "codebook-v1", "verdict": "confirmed",
         "note": None, "audited_at": "2026-10-03"}
        for index in range(3)
    ]
    return {"schema_version": "madia-human-audit-v1", "auditor": "user", "records": records}


def analysis_bundle() -> dict:
    unit = evidence_unit("video000000:001", project_id="video000000:p1")
    del unit["verification"]
    unit["principle_candidate_ids"] = []
    return {
        "schema_version": "madia-video-analysis-v1", "video_id": "video000000",
        "coder": "coder-a", "session_id": "w01-coder-a-01", "codebook_version": "codebook-v1",
        "ratings": {"relevance": "direct_design_work", "decision_stage": "information_priority",
                    "evidence_kind": "verbalized"},
        "proposed_status": "analyzed", "reason": None, "sheets_total": 2, "sheets_viewed": 2,
        "caption_source": "manual", "frames_requested": [10.0], "evidence_units": [unit],
        "term_proposals": [],
    }


def verification_bundle(bundle: dict) -> dict:
    return {
        "schema_version": "madia-verification-v1", "video_id": bundle["video_id"],
        "verifier": "w01-verifier-01", "exclusion_confirmed": None, "exclusion_note": None,
        "units": [
            {"unit_id": unit["id"], "status": "confirmed", "checks": ["target", "attribution", "speech"],
             "corrections": {}, "note": None}
            for unit in bundle["evidence_units"]
        ],
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
                project_id=f"{video_id}:p1",
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
                "exclusion_reason": None if analyzed else "not_relevant: 인터페이스 판단이 없다.",
                "blocking_reason": None,
                "duplicate_of": None,
                "evidence_units": evidence_units,
                "analysis_receipt": analysis_receipt(),
            }
        )
    return {
        "schema_version": "madia-design-practice-catalog-v2",
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
                "independent_projects": 3,
                "durability": "contextual",
                "term_ids": [],
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
            {"id": gate_id, "status": "passed", "evidence": [f"evidence/{gate_id.lower()}.md"]
             + (["evidence/human-audit.json"] if gate_id in {"M3", "M8"} else [])}
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
        audit_payload: dict | None = None,
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
                                elif relative.endswith("human-audit.json"):
                                    evidence_path.write_text(json.dumps(audit_payload or human_audit()), encoding="utf-8")
                                elif relative.endswith("stable-repeated-unit-run-1.json"):
                                    principle = payload["principles"][0]
                                    fixture = principle["behavior_fixture"]
                                    text = {field: principle[field] for field in
                                            ("label", "trigger", "inspect", "decide", "act", "verify", "exceptions")}
                                    receipt = {
                                        "schema_version": "madia-behavior-receipt-v1",
                                        "fixture_id": fixture["fixture_id"], "run_id": fixture["run_id"],
                                        "artifact_revision": fixture["artifact_revision"],
                                        "principle_sha256": hashlib.sha256(json.dumps(text, ensure_ascii=False, sort_keys=True).encode()).hexdigest(),
                                        "scenario": "반복 상품을 비교할 수 있는 화면을 설계한다.",
                                        "output": "상품마다 판단에 필요한 정보와 순서를 먼저 정했다.",
                                        "behavior_options": fixture["expected"] + fixture["must_not"],
                                        "observed": fixture["observed"],
                                        "evaluator_notes": "출력에서 정보 순서를 먼저 정하는 행동을 확인했다.",
                                    }
                                    evidence_path.write_text(json.dumps(receipt), encoding="utf-8")
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

    def test_inferred_occurrences_cannot_reach_p1(self) -> None:
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
        payload["principles"][0]["independent_projects"] = 4
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

    def test_v1_catalog_is_rejected(self) -> None:
        payload = valid_catalog()
        payload["schema_version"] = "madia-design-practice-catalog-v1"
        self.assertNotEqual(self.run_validator(payload).returncode, 0)

    def test_visual_and_speech_evidence_requirements(self) -> None:
        cases = [
            ("missing after", lambda u: u["visual_evidence"].pop(), "before and after"),
            ("empty visual", lambda u: u.update(visual_evidence=[]), "requires visual evidence"),
            ("missing context", lambda u: u.pop("context"), ".context"),
            ("partial high confidence", lambda u: u["visual_evidence"][0].update(legibility="partial"), "clearly legible"),
            ("number without check", lambda u: u.update(visible_effect="속성 패널의 크기가 24 pt로 바뀐다."), "numbers"),
            ("inference attribution", lambda u: u.update(evidence_kind="inferred"), "inferred rationale"),
            ("missing speech", lambda u: u.update(speech_excerpt=None), "requires speech_excerpt"),
        ]
        for name, mutate, message in cases:
            with self.subTest(name=name):
                unit = evidence_unit("video000000:001", "demonstrated")
                self.assertEqual(self.unit_errors(unit), [])
                mutate(unit)
                self.assertTrue(any(message in error for error in self.unit_errors(unit)))

    def unit_errors(self, unit: dict, mode: str = "catalog") -> list[str]:
        errors = []
        validator.validate_evidence_unit(unit, "video000000", "unit", errors, mode=mode)
        return errors

    def test_region_time_and_excerpt_boundaries(self) -> None:
        unit = evidence_unit("video000000:001")
        for region in (None, [0, 0, 1, 1], [0.1, 0.2, 0.3, 0.4]):
            unit["visual_evidence"][0]["region"] = region
            self.assertEqual(self.unit_errors(unit), [])
        for region in ([0, 0, 0, 1], [-0.1, 0, 0.5, 1], [0.5, 0, 0.6, 1],
                       [0, 0, float("nan"), 1], [False, 0, 1, 1], [0, 1]):
            with self.subTest(region=region):
                unit["visual_evidence"][0]["region"] = region
                self.assertTrue(any(".region" in error for error in self.unit_errors(unit)))
        unit["visual_evidence"][0]["region"] = None
        for frame in (10, 25):
            unit["visual_evidence"][0]["frame_time"] = frame
            self.assertEqual(self.unit_errors(unit), [])
        for frame in (9.99, 25.01, float("inf"), True):
            unit["visual_evidence"][0]["frame_time"] = frame
            self.assertTrue(any(".frame_time" in error for error in self.unit_errors(unit)))
        unit["visual_evidence"][0]["frame_time"] = 10
        unit["speech_excerpt"] = "가" * 120
        self.assertEqual(self.unit_errors(unit), [])
        unit["speech_excerpt"] += "나"
        self.assertTrue(any("speech_excerpt" in error for error in self.unit_errors(unit)))

    def test_unit_identity_locator_project_and_term_contracts(self) -> None:
        cases = {
            "id": "video000001:001", "source_locator": "https://www.youtube.com/watch?v=video000000&t=11s",
            "project_id": "project-a", "term_ids": ["term.valid", "term.valid"],
            "decision_stage": "information", "evidence_kind": "metadata_only",
        }
        for field, value in cases.items():
            with self.subTest(field=field):
                unit = evidence_unit("video000000:001")
                unit[field] = value
                self.assertTrue(self.unit_errors(unit))
        bundle = analysis_bundle()
        self.assertEqual(validator.validate_analysis_bundle(bundle, set()), [])
        bundle["evidence_units"][0]["project_id"] = "madia-proj-linked"
        self.assertTrue(any("project_id" in error for error in validator.validate_analysis_bundle(bundle, set())))

    def test_receipt_requires_distinct_roles_complete_sheets_and_valid_status(self) -> None:
        for mutate in (
            lambda r: r["sessions"].update(verifier=r["sessions"]["coder-a"]),
            lambda r: r["sessions"].pop("adjudicator"),
            lambda r: r.update(coders=["coder-a", "coder-b"]),
            lambda r: r.update(sheets_viewed=1),
            lambda r: r.update(sheets_total=True, sheets_viewed=True),
            lambda r: r.update(codebook_version="v1"),
        ):
            video = valid_catalog()["videos"][0]
            mutate(video["analysis_receipt"])
            errors = []
            validator.validate_analysis_receipt(video, "video", errors)
            self.assertTrue(errors)
        for status, duplicate in (("pending", None), ("blocked", None), ("excluded", "video000001")):
            video = valid_catalog()["videos"][0]
            video.update(status=status, duplicate_of=duplicate)
            errors = []
            validator.validate_analysis_receipt(video, "video", errors)
            self.assertTrue(errors)
            video["analysis_receipt"] = None
            errors = []
            validator.validate_analysis_receipt(video, "video", errors)
            self.assertEqual(errors, [])

    def test_held_evidence_cannot_support_any_principle_tier(self) -> None:
        for tier in ("P0", "P1", "P2", "P3"):
            payload = valid_catalog()
            payload["principles"][0]["tier"] = tier
            payload["videos"][0]["evidence_units"][0]["verification"].update(status="held", note="대상이 흐리다.")
            result = self.run_validator(payload)
            self.assertNotEqual(result.returncode, 0)
            self.assertIn("cannot cite held", result.stdout)

    def test_era_specific_principles_stop_at_p2(self) -> None:
        payload = valid_catalog()
        payload["principles"][0]["durability"] = "era_specific"
        result = self.run_validator(payload)
        self.assertNotEqual(result.returncode, 0)
        self.assertIn("era_specific", result.stdout)
        payload["principles"][0]["tier"] = "P2"
        result = self.run_validator(payload)
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)

    def test_three_projects_in_two_videos_cannot_reach_p1(self) -> None:
        payload = valid_catalog()
        payload["principles"][0]["tier"] = "P1"
        unit = copy.deepcopy(payload["videos"][2]["evidence_units"][0])
        unit.update(id="video000000:002", project_id="video000000:p2",
                    source_locator="https://www.youtube.com/watch?v=video000000&t=10s")
        payload["videos"][0]["evidence_units"].append(unit)
        payload["principles"][0]["occurrence_ids"][2] = unit["id"]
        result = self.run_validator(payload)
        self.assertNotEqual(result.returncode, 0)
        self.assertIn("at least three videos", result.stdout)

    def test_linked_project_across_videos_counts_only_once(self) -> None:
        payload = valid_catalog()
        payload["principles"][0].update(tier="P1", independent_projects=2)
        for video in payload["videos"][:2]:
            video["evidence_units"][0]["project_id"] = "madia-proj-shared"
        result = self.run_validator(payload)
        self.assertNotEqual(result.returncode, 0)
        self.assertIn("independent recurrence", result.stdout)

    def test_negative_kappa_is_valid_but_cannot_pass_m3(self) -> None:
        payload = valid_catalog()
        payload["principles"][0]["tier"] = "P0"
        payload["quality_gates"][3].update(status="not_run", evidence=[])
        payload["reliability"].update(pilot_kappa=-1, production_kappa=-0.5)
        result = self.run_validator(payload)
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
        payload["quality_gates"][3].update(status="passed", evidence=["evidence/human-audit.json"])
        result = self.run_validator(payload)
        self.assertNotEqual(result.returncode, 0)
        self.assertIn("M3 requires pilot_kappa", result.stdout)

    def test_m3_requires_current_confirmed_pilot_audit(self) -> None:
        payload = valid_catalog()
        payload["quality_gates"][3]["evidence"] = ["evidence/m3.md"]
        result = self.run_validator(payload)
        self.assertNotEqual(result.returncode, 0)
        self.assertIn("human-audit.json", result.stdout)
        for changes in ({"verdict": "needs_correction", "note": "대상 확인 필요"},
                        {"codebook_version": "codebook-v2"}):
            audit = human_audit()
            latest = {**audit["records"][0], **changes}
            audit["records"].append(latest)
            result = self.run_validator(valid_catalog(), audit_payload=audit)
            self.assertNotEqual(result.returncode, 0)
            self.assertIn("M3", result.stdout)
            audit["records"].append(audit["records"][0].copy())
            result = self.run_validator(valid_catalog(), audit_payload=audit)
            self.assertEqual(result.returncode, 0, result.stdout + result.stderr)

    def test_m8_requires_each_p3_pair_and_two_p1_p2_pairs(self) -> None:
        for tier, retained in (("P3", 2), ("P2", 1), ("P1", 1)):
            payload = valid_catalog()
            payload["principles"][0]["tier"] = tier
            audit = human_audit()
            audit["records"] = audit["records"][:20 + retained]
            result = self.run_validator(payload, audit_payload=audit)
            self.assertNotEqual(result.returncode, 0)
            self.assertIn("M8", result.stdout)

    def test_removed_rejected_pair_no_longer_blocks_m8(self) -> None:
        payload = valid_catalog()
        payload["principles"][0]["tier"] = "P1"
        extra = copy.deepcopy(payload["videos"][0]["evidence_units"][0])
        extra["id"] = "video000000:002"
        payload["videos"][0]["evidence_units"].append(extra)
        payload["principles"][0]["occurrence_ids"].append(extra["id"])
        audit = human_audit()
        audit["records"].append({
            **audit["records"][-1], "target_id": f"stable-repeated-unit|{extra['id']}",
            "verdict": "rejected", "note": "조건에 맞지 않는다.",
        })
        result = self.run_validator(payload, audit_payload=audit)
        self.assertNotEqual(result.returncode, 0)
        self.assertIn("M8", result.stdout)
        payload["principles"][0]["occurrence_ids"].remove(extra["id"])
        extra["principle_candidate_ids"] = []
        result = self.run_validator(payload, audit_payload=audit)
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)

    def test_bundle_ratings_use_majority_and_tie_rules(self) -> None:
        bundle = analysis_bundle()
        first = bundle["evidence_units"][0]
        second = copy.deepcopy(first)
        second.update(id="video000000:002", decision_stage="visual_system",
                      evidence_kind="inferred", rationale="[해석] " + first["rationale"],
                      timestamp_start=5, timestamp_end=9, source_locator="https://www.youtube.com/watch?v=video000000&t=5s")
        second["visual_evidence"][0]["frame_time"] = 5
        bundle["evidence_units"].append(second)
        errors = validator.validate_analysis_bundle(bundle, set())
        self.assertTrue(any("tie rules" in error for error in errors))
        bundle["ratings"].update(decision_stage="visual_system", evidence_kind="inferred")
        self.assertEqual(validator.validate_analysis_bundle(bundle, set()), [])
        third = copy.deepcopy(first)
        third["id"] = "video000000:003"
        bundle["evidence_units"].append(third)
        self.assertTrue(validator.validate_analysis_bundle(bundle, set()))
        bundle["ratings"].update(decision_stage="information_priority", evidence_kind="verbalized")
        self.assertEqual(validator.validate_analysis_bundle(bundle, set()), [])

    def test_verification_requires_exact_units_and_independent_session(self) -> None:
        bundle = analysis_bundle()
        verification = verification_bundle(bundle)
        self.assertEqual(validator.validate_verification(verification, bundle, set()), [])
        for mutate, message in (
            (lambda v: v.update(units=[]), "unit_id set"),
            (lambda v: v["units"].append(copy.deepcopy(v["units"][0])), "unit_id set"),
            (lambda v: v.update(verifier=bundle["session_id"]), "distinct"),
        ):
            verification = verification_bundle(bundle)
            mutate(verification)
            self.assertTrue(any(message in error for error in validator.validate_verification(verification, bundle, set())))

    def test_verifier_corrections_are_scope_limited(self) -> None:
        bundle = analysis_bundle()
        original = bundle["evidence_units"][0]
        cases = {
            "evidence_kind": "demonstrated", "problem": "문제 수정",
            "rationale": "새 이유", "visual_evidence": [],
        }
        changed_roles = copy.deepcopy(original["visual_evidence"])
        changed_roles[0]["role"] = "during"
        for field, value in list(cases.items()) + [("visual_evidence", changed_roles)]:
            with self.subTest(field=field, value=value):
                verification = verification_bundle(bundle)
                verification["units"][0].update(status="corrected", note="프레임 대조", corrections={field: value})
                errors = validator.validate_verification(verification, bundle, set())
                self.assertTrue(any("exceed the verifier scope" in error for error in errors))
        original["confidence"] = "low"
        verification = verification_bundle(bundle)
        verification["units"][0].update(status="corrected", note="확신 상향", corrections={"confidence": "high"})
        self.assertTrue(any("scope" in error for error in validator.validate_verification(verification, bundle, set())))

    def test_corrections_revalidate_interval_checks_and_ledger(self) -> None:
        bundle = analysis_bundle()
        verification = verification_bundle(bundle)
        item = verification["units"][0]
        item.update(status="corrected", note="발화 구간 조정", corrections={"timestamp_start": 11})
        self.assertTrue(any("frame_time" in error for error in validator.validate_verification(verification, bundle, set())))
        visual = copy.deepcopy(bundle["evidence_units"][0]["visual_evidence"])
        visual[0]["frame_time"] = 11
        item["corrections"]["visual_evidence"] = visual
        self.assertEqual(validator.validate_verification(verification, bundle, set()), [])
        visual[0]["observation"] = "패널에 16 px가 보인다."
        self.assertTrue(any("numbers" in error for error in validator.validate_verification(verification, bundle, set())))
        item["checks"].append("numbers")
        item["corrections"]["term_ids"] = ["term.spacing"]
        self.assertTrue(any("ledger" in error for error in validator.validate_verification(verification, bundle, set())))
        self.assertEqual(validator.validate_verification(verification, bundle, {"term.spacing"}), [])
        self.assertEqual(bundle["evidence_units"][0]["timestamp_start"], 10)

    def test_allowed_downgrade_applies_inference_attribution(self) -> None:
        bundle = analysis_bundle()
        verification = verification_bundle(bundle)
        verification["units"][0].update(
            status="corrected", note="이유를 말하지 않아 추론으로 낮춤",
            corrections={"evidence_kind": "inferred", "confidence": "low",
                         "rationale": "[해석] " + bundle["evidence_units"][0]["rationale"]},
        )
        self.assertEqual(validator.validate_verification(verification, bundle, set()), [])

    def test_exclusion_disagreement_requires_reason(self) -> None:
        bundle = analysis_bundle()
        bundle.update(proposed_status="excluded", reason="not_relevant: 디자인 판단이 없다.",
                      evidence_units=[], frames_requested=[])
        bundle["ratings"].update(relevance="not_relevant", decision_stage="none", evidence_kind="none")
        self.assertEqual(validator.validate_analysis_bundle(bundle, set()), [])
        verification = verification_bundle(bundle)
        verification["exclusion_confirmed"] = False
        self.assertTrue(any("exclusion_note" in error for error in validator.validate_verification(verification, bundle, set())))
        verification["exclusion_note"] = "후반에 화면 비평이 있다."
        self.assertEqual(validator.validate_verification(verification, bundle, set()), [])
        verification.update(exclusion_confirmed=True, exclusion_note=None)
        self.assertEqual(validator.validate_verification(verification, bundle, set()), [])
        bundle["ratings"]["relevance"] = "design_explanation"
        self.assertTrue(any("relevance" in error for error in validator.validate_analysis_bundle(bundle, set())))

    def test_captionless_bundle_requires_inference_without_excerpt(self) -> None:
        bundle = analysis_bundle()
        bundle["caption_source"] = "none"
        self.assertTrue(any("without captions" in error for error in validator.validate_analysis_bundle(bundle, set())))
        unit = bundle["evidence_units"][0]
        unit.update(evidence_kind="inferred", speech_excerpt=None, rationale="[해석] " + unit["rationale"])
        bundle["ratings"]["evidence_kind"] = "inferred"
        self.assertEqual(validator.validate_analysis_bundle(bundle, set()), [])

    def test_bundle_cli_ledger_and_verification_modes(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            base = Path(tmp)
            bundle = analysis_bundle()
            bundle["evidence_units"][0]["term_ids"] = ["term.spacing"]
            bundle_path, ledger_path, verification_path = (base / name for name in ("bundle.json", "ledger.json", "verification.json"))
            bundle_path.write_text(json.dumps(bundle), encoding="utf-8")
            verification_path.write_text(json.dumps(verification_bundle(bundle)), encoding="utf-8")
            command = ["python3", str(VALIDATOR), "--bundle", str(bundle_path), "--ledger", str(ledger_path)]
            for status in ("candidate", "adopted", "held", "rejected", None):
                ledger = {"schema_version": "design-terminology-v1", "terms": [] if status is None else [{"id": "term.spacing", "status": status}]}
                ledger_path.write_text(json.dumps(ledger), encoding="utf-8")
                for extra in ([], ["--verification", str(verification_path)]):
                    result = subprocess.run(command + extra, text=True, capture_output=True, check=False)
                    if status in ("rejected", None):
                        self.assertNotEqual(result.returncode, 0)
                        self.assertIn("ledger", result.stdout)
                    else:
                        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
                        self.assertIn("OK: madia-verification" if extra else "OK: madia-video-analysis", result.stdout)
            for arguments in ([], ["--verification", str(verification_path)], [str(bundle_path), "--bundle", str(bundle_path)]):
                result = subprocess.run(["python3", str(VALIDATOR)] + arguments, text=True, capture_output=True, check=False)
                self.assertNotEqual(result.returncode, 0)
                self.assertNotIn("Traceback", result.stderr)

    def test_malformed_new_fields_return_validation_errors(self) -> None:
        cases = [
            ("frames_requested", [{}]), ("ratings", []), ("term_proposals", [None]),
            ("evidence_units", [None]), ("session_id", []),
        ]
        for field, value in cases:
            with self.subTest(field=field):
                bundle = analysis_bundle()
                bundle[field] = value
                self.assertTrue(validator.validate_analysis_bundle(bundle, set()))
        for field in ("evidence_kind", "confidence", "term_ids", "visual_evidence", "context", "verification"):
            with self.subTest(field=field):
                unit = evidence_unit("video000000:001")
                unit[field] = {"invalid": True}
                self.assertTrue(self.unit_errors(unit))

    def test_coder_ratings_reject_non_codebook_labels(self) -> None:
        for dimension in ("relevance", "decision_stage", "evidence_kind"):
            pilot = coder_evidence("pilot")
            pilot["records"][0]["ratings"][dimension]["coder-a"] = "legacy-label"
            result = self.run_validator(valid_catalog(), coder_evidence_payloads={"pilot": pilot})
            self.assertNotEqual(result.returncode, 0)
            self.assertIn(f"ratings.{dimension}", result.stdout)

    def test_verification_status_controls_corrections_and_notes(self) -> None:
        bundle = analysis_bundle()
        for status, corrections, note in (
            ("confirmed", {"confidence": "low"}, None),
            ("corrected", {}, "수정 내용 없음"),
            ("held", {}, None),
            ("rejected", {}, None),
        ):
            verification = verification_bundle(bundle)
            verification["units"][0].update(status=status, corrections=corrections, note=note)
            self.assertTrue(validator.validate_verification(verification, bundle, set()))
        verification = verification_bundle(bundle)
        verification["units"][0].update(status="rejected", note="원자료가 주장을 반박한다.")
        self.assertEqual(validator.validate_verification(verification, bundle, set()), [])


if __name__ == "__main__":
    unittest.main()
