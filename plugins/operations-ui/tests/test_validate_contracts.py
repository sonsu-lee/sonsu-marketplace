from __future__ import annotations

import base64
import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path


PLUGIN_ROOT = Path(__file__).resolve().parents[1]
VALIDATOR = PLUGIN_ROOT / "scripts" / "validate_contracts.py"
GATE_IDS = [f"G{index}" for index in range(8)]
CHECK_IDS = {
    "G0": ["contract-artifact", "requirement-scenario-coverage"],
    "G1": ["pattern-decision", "information-hierarchy", "actual-wide-render"],
    "G2": ["token-mapping", "shell-and-navigation", "semantic-color", "density-and-components"],
    "G3": ["state-matrix", "loading-empty-error-permission", "zero-one-many", "long-localized-overflow"],
    "G4": ["primary-secondary-actions", "bulk-destructive-actions", "feedback-and-selection"],
    "G5": ["wide-viewport", "narrow-or-excluded", "overflow-and-detail-access"],
    "G6": ["keyboard-focus", "names-roles-states", "non-color-status", "contrast"],
    "G7": ["actual-app-provenance", "required-scenario-coverage", "screenshots", "console-runtime"],
}
PNG_BYTES = base64.b64decode(
    "iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAADUlEQVR4nGNgYGD4DwABBAEAX+XDSwAAAABJRU5ErkJggg=="
)


def valid_screen_contract() -> dict:
    return {
        "schema_version": "operations-ui-screen-contract-v1",
        "id": "service-queue",
        "mode": "greenfield",
        "surface": "standalone-console",
        "actors": ["support-agent"],
        "jobs": ["triage-open-cases"],
        "entities": ["case"],
        "lifecycle": ["new", "assigned", "resolved"],
        "primary_decision": "which case needs attention next",
        "actions": ["assign", "resolve"],
        "permissions": ["case:read", "case:update"],
        "risks": ["resolving the wrong case"],
        "view_states": [
            "loading",
            "empty",
            "error",
            "permission-denied",
            "zero",
            "one",
            "many",
            "long-localized",
        ],
        "viewports": [
            {"id": "wide", "width": 1440, "height": 900},
            {"id": "narrow", "width": 768, "height": 1024},
        ],
        "requirements": [
            {"id": "R1", "text": "Agents can triage cases", "scenario_ids": ["S1"]}
        ],
        "evidence_scenarios": [
            {
                "id": "S1",
                "requirement_ids": ["R1"],
                "initial_state": "many",
                "actions": ["assign", "resolve"],
                "expected": "case detail is visible",
                "required_viewports": ["wide", "narrow"],
                "coverage": {
                    "actions": ["assign", "resolve"],
                    "permissions": ["case:read", "case:update"],
                    "risks": ["resolving the wrong case"],
                    "view_states": [
                        "loading",
                        "empty",
                        "error",
                        "permission-denied",
                        "zero",
                        "one",
                        "many",
                        "long-localized",
                    ],
                },
            }
        ],
        "exclusions": [],
        "unresolved_decisions": [],
    }


def valid_quality_report() -> dict:
    return {
        "schema_version": "operations-ui-quality-report-v1",
        "screen_contract_id": "service-queue",
        "overall": "passed",
        "design_profile": {
            "name": "precision-operations-console-v1",
            "canvas": "#F4F6F8",
            "surface": "#FFFFFF",
            "sidebar": "#1D2B3C",
            "primary": "#356BD6",
            "sidebar_width": 240,
            "topbar_height": 48,
            "content_padding": 24,
            "section_gap": 16,
            "control_height": 36,
            "table_row_height": 48,
            "radius": 10,
        },
        "gates": [
            {
                "id": gate_id,
                "required": True,
                "status": "passed",
                "evidence": [f"evidence/{gate_id}.json"],
                "checks": [
                    {
                        "id": check_id,
                        "status": "passed",
                        "evidence": [f"evidence/{gate_id}-{check_id}.json"],
                    }
                    for check_id in CHECK_IDS[gate_id]
                ],
            }
            for gate_id in GATE_IDS
        ],
        "browser_receipts": [
            {
                "scenario_id": "S1",
                "command": "npm run dev",
                "build_or_revision": "working-tree:abc123",
                "url": "http://127.0.0.1:3000/cases",
                "viewport_id": "wide",
                "status": "passed",
                "actions": ["assign", "resolve"],
                "expected": "case detail is visible",
                "observed": "case detail is visible",
                "screenshots": ["evidence/S1-wide.png"],
                "console_runtime_errors": [],
            },
            {
                "scenario_id": "S1",
                "command": "npm run dev",
                "build_or_revision": "working-tree:abc123",
                "url": "http://127.0.0.1:3000/cases",
                "viewport_id": "narrow",
                "status": "passed",
                "actions": ["assign", "resolve"],
                "expected": "case detail is visible",
                "observed": "case detail is visible",
                "screenshots": ["evidence/S1-narrow.png"],
                "console_runtime_errors": [],
            },
        ],
    }


def valid_redesign_contract() -> dict:
    payload = valid_screen_contract()
    payload["mode"] = "redesign"
    payload["current_behavior_inventory"] = [
        {
            "id": "CB1",
            "kind": "action",
            "observed": "agent opens a case from the queue",
            "evidence": ["src/CaseQueue.tsx:42"],
            "decision": "preserve",
            "reason": "required primary workflow",
            "implementation_target": "src/CaseQueue.tsx",
            "scenario_ids": ["S1"],
        }
    ]
    payload["change_contract"] = [
        {
            "id": "CC1",
            "inventory_ids": ["CB1"],
            "requirement_ids": ["R1"],
            "description": "preserve opening a case while changing its layout",
        }
    ]
    return payload


def not_run_quality_report() -> dict:
    payload = valid_quality_report()
    payload["overall"] = "not_run"
    for gate in payload["gates"]:
        gate["status"] = "not_run"
        for check in gate["checks"]:
            check["status"] = "not_run"
    payload["browser_receipts"] = []
    return payload


class ValidatorCliTests(unittest.TestCase):
    def run_validator(self, *args: str) -> subprocess.CompletedProcess[str]:
        return subprocess.run(
            [sys.executable, str(VALIDATOR), *args],
            text=True,
            capture_output=True,
            check=False,
        )

    def write_json(self, directory: Path, name: str, payload: object) -> Path:
        if (
            isinstance(payload, dict)
            and payload.get("schema_version") == "operations-ui-quality-report-v1"
            and payload.get("overall") == "passed"
        ):
            evidence_paths = []
            for gate in payload.get("gates", []):
                if isinstance(gate.get("evidence"), list):
                    evidence_paths.extend(gate["evidence"])
                for check in gate.get("checks", []):
                    if isinstance(check.get("evidence"), list):
                        evidence_paths.extend(check["evidence"])
            for receipt in payload.get("browser_receipts", []):
                if isinstance(receipt.get("screenshots"), list):
                    evidence_paths.extend(receipt["screenshots"])
            for relative_path in evidence_paths:
                evidence_path = directory / relative_path
                if relative_path.endswith("/"):
                    evidence_path.mkdir(parents=True, exist_ok=True)
                    continue
                evidence_path.parent.mkdir(parents=True, exist_ok=True)
                evidence_path.write_bytes(
                    PNG_BYTES if relative_path.endswith(".png") else b"evidence"
                )
        path = directory / name
        path.write_text(json.dumps(payload), encoding="utf-8")
        return path

    def test_valid_screen_and_quality_report_pass(self) -> None:
        with tempfile.TemporaryDirectory() as raw_directory:
            directory = Path(raw_directory)
            screen = self.write_json(directory, "screen.json", valid_screen_contract())
            report = self.write_json(directory, "report.json", valid_quality_report())

            result = self.run_validator("quality-report", str(report), str(screen))

            self.assertEqual(result.returncode, 0, result.stderr + result.stdout)

    def test_missing_required_screen_field_fails(self) -> None:
        with tempfile.TemporaryDirectory() as raw_directory:
            directory = Path(raw_directory)
            payload = valid_screen_contract()
            del payload["primary_decision"]
            screen = self.write_json(directory, "screen.json", payload)

            result = self.run_validator("screen-contract", str(screen))

            self.assertNotEqual(result.returncode, 0)
            self.assertIn("primary_decision", result.stdout)

    def test_required_not_run_gate_cannot_claim_passed(self) -> None:
        with tempfile.TemporaryDirectory() as raw_directory:
            directory = Path(raw_directory)
            screen = self.write_json(directory, "screen.json", valid_screen_contract())
            payload = valid_quality_report()
            payload["gates"][7]["status"] = "not_run"
            report = self.write_json(directory, "report.json", payload)

            result = self.run_validator("quality-report", str(report), str(screen))

            self.assertNotEqual(result.returncode, 0)
            self.assertIn("overall=passed", result.stdout)

    def test_changed_design_profile_cannot_claim_passed(self) -> None:
        with tempfile.TemporaryDirectory() as raw_directory:
            directory = Path(raw_directory)
            screen = self.write_json(directory, "screen.json", valid_screen_contract())
            payload = valid_quality_report()
            payload["design_profile"]["primary"] = "#7C3AED"
            report = self.write_json(directory, "report.json", payload)

            result = self.run_validator("quality-report", str(report), str(screen))

            self.assertNotEqual(result.returncode, 0)
            self.assertIn("design_profile.primary", result.stdout)

    def test_runtime_errors_cannot_claim_passed(self) -> None:
        with tempfile.TemporaryDirectory() as raw_directory:
            directory = Path(raw_directory)
            screen = self.write_json(directory, "screen.json", valid_screen_contract())
            payload = valid_quality_report()
            payload["browser_receipts"][0]["console_runtime_errors"] = ["TypeError"]
            report = self.write_json(directory, "report.json", payload)

            result = self.run_validator("quality-report", str(report), str(screen))

            self.assertNotEqual(result.returncode, 0)
            self.assertIn("console/runtime", result.stdout)

    def test_failed_browser_receipt_cannot_claim_passed(self) -> None:
        with tempfile.TemporaryDirectory() as raw_directory:
            directory = Path(raw_directory)
            screen = self.write_json(directory, "screen.json", valid_screen_contract())
            payload = valid_quality_report()
            payload["browser_receipts"][0]["status"] = "failed"
            report = self.write_json(directory, "report.json", payload)

            result = self.run_validator("quality-report", str(report), str(screen))

            self.assertNotEqual(result.returncode, 0)
            self.assertIn("receipt status", result.stdout)

    def test_missing_fixed_gate_check_cannot_pass(self) -> None:
        with tempfile.TemporaryDirectory() as raw_directory:
            directory = Path(raw_directory)
            screen = self.write_json(directory, "screen.json", valid_screen_contract())
            payload = valid_quality_report()
            payload["gates"][3]["checks"].pop()
            report = self.write_json(directory, "report.json", payload)

            result = self.run_validator("quality-report", str(report), str(screen))

            self.assertNotEqual(result.returncode, 0)
            self.assertIn("G3.checks", result.stdout)

    def test_nonpassing_report_can_record_no_browser_receipts(self) -> None:
        with tempfile.TemporaryDirectory() as raw_directory:
            directory = Path(raw_directory)
            screen = self.write_json(directory, "screen.json", valid_screen_contract())
            payload = not_run_quality_report()
            report = self.write_json(directory, "report.json", payload)

            result = self.run_validator("quality-report", str(report), str(screen))

            self.assertEqual(result.returncode, 0, result.stdout + result.stderr)

    def test_example_placeholder_cannot_claim_passed(self) -> None:
        with tempfile.TemporaryDirectory() as raw_directory:
            directory = Path(raw_directory)
            screen = self.write_json(directory, "screen.json", valid_screen_contract())
            payload = valid_quality_report()
            payload["browser_receipts"][0]["command"] = "EXAMPLE_ONLY npm run dev"
            report = self.write_json(directory, "report.json", payload)

            result = self.run_validator("quality-report", str(report), str(screen))

            self.assertNotEqual(result.returncode, 0)
            self.assertIn("placeholder", result.stdout)

    def test_passed_report_requires_existing_evidence_files(self) -> None:
        with tempfile.TemporaryDirectory() as raw_directory:
            directory = Path(raw_directory)
            screen = self.write_json(directory, "screen.json", valid_screen_contract())
            payload = valid_quality_report()
            report = self.write_json(directory, "report.json", payload)
            (directory / "evidence" / "S1-wide.png").unlink()

            result = self.run_validator("quality-report", str(report), str(screen))

            self.assertNotEqual(result.returncode, 0)
            self.assertIn("missing evidence file", result.stdout)

    def test_passed_report_rejects_non_image_screenshot_content(self) -> None:
        with tempfile.TemporaryDirectory() as raw_directory:
            directory = Path(raw_directory)
            screen = self.write_json(directory, "screen.json", valid_screen_contract())
            report = self.write_json(directory, "report.json", valid_quality_report())
            (directory / "evidence" / "S1-wide.png").write_bytes(b"not an image")

            result = self.run_validator("quality-report", str(report), str(screen))

            self.assertNotEqual(result.returncode, 0)
            self.assertIn("unsupported screenshot content", result.stdout)

    def test_passed_report_rejects_truncated_png_signature(self) -> None:
        with tempfile.TemporaryDirectory() as raw_directory:
            directory = Path(raw_directory)
            screen = self.write_json(directory, "screen.json", valid_screen_contract())
            report = self.write_json(directory, "report.json", valid_quality_report())
            (directory / "evidence" / "S1-wide.png").write_bytes(
                b"\x89PNG\r\n\x1a\n"
            )

            result = self.run_validator("quality-report", str(report), str(screen))

            self.assertNotEqual(result.returncode, 0)
            self.assertIn("unsupported screenshot content", result.stdout)

    def test_passed_report_rejects_webp_without_image_payload(self) -> None:
        with tempfile.TemporaryDirectory() as raw_directory:
            directory = Path(raw_directory)
            screen = self.write_json(directory, "screen.json", valid_screen_contract())
            report = self.write_json(directory, "report.json", valid_quality_report())
            extended_header = b"VP8X" + (10).to_bytes(4, "little") + bytes(10)
            webp = (
                b"RIFF"
                + (len(extended_header) + 4).to_bytes(4, "little")
                + b"WEBP"
                + extended_header
            )
            (directory / "evidence" / "S1-wide.png").write_bytes(webp)

            result = self.run_validator("quality-report", str(report), str(screen))

            self.assertNotEqual(result.returncode, 0)
            self.assertIn("unsupported screenshot content", result.stdout)

    def test_passed_report_rejects_absolute_evidence_paths(self) -> None:
        with tempfile.TemporaryDirectory() as raw_directory:
            directory = Path(raw_directory)
            screen = self.write_json(directory, "screen.json", valid_screen_contract())
            payload = valid_quality_report()
            absolute_evidence = str((directory / "outside-evidence").resolve())
            for gate in payload["gates"]:
                gate["evidence"] = [absolute_evidence]
                for check in gate["checks"]:
                    check["evidence"] = [absolute_evidence]
            for receipt in payload["browser_receipts"]:
                receipt["screenshots"] = [absolute_evidence]
            report = directory / "report.json"
            report.write_text(json.dumps(payload), encoding="utf-8")

            result = self.run_validator("quality-report", str(report), str(screen))

            self.assertNotEqual(result.returncode, 0)
            self.assertIn("report-relative", result.stdout)

    def test_redesign_requires_inventory_and_change_contract(self) -> None:
        with tempfile.TemporaryDirectory() as raw_directory:
            directory = Path(raw_directory)
            payload = valid_screen_contract()
            payload["mode"] = "redesign"
            screen = self.write_json(directory, "screen.json", payload)

            result = self.run_validator("screen-contract", str(screen))

            self.assertNotEqual(result.returncode, 0)
            self.assertIn("current_behavior_inventory", result.stdout)
            self.assertIn("change_contract", result.stdout)

    def test_redesign_requires_complete_inventory_mapping(self) -> None:
        with tempfile.TemporaryDirectory() as raw_directory:
            directory = Path(raw_directory)
            payload = valid_redesign_contract()
            payload["current_behavior_inventory"].append(
                {
                    "id": "CB2",
                    "kind": "permission",
                    "observed": "supervisor can resolve cases",
                    "evidence": ["src/permissions.ts:8"],
                    "decision": "preserve",
                    "reason": "authorization boundary",
                    "implementation_target": "src/permissions.ts",
                    "scenario_ids": ["S1"],
                }
            )
            screen = self.write_json(directory, "screen.json", payload)

            result = self.run_validator("screen-contract", str(screen))

            self.assertNotEqual(result.returncode, 0)
            self.assertIn("100%", result.stdout)

    def test_inventory_id_cannot_map_to_multiple_change_contracts(self) -> None:
        with tempfile.TemporaryDirectory() as raw_directory:
            directory = Path(raw_directory)
            payload = valid_redesign_contract()
            payload["change_contract"].append(
                {
                    "id": "CC2",
                    "inventory_ids": ["CB1"],
                    "requirement_ids": ["R1"],
                    "description": "replace the preserved workflow with another contract",
                }
            )
            screen = self.write_json(directory, "screen.json", payload)

            result = self.run_validator("screen-contract", str(screen))

            self.assertNotEqual(result.returncode, 0)
            self.assertIn("mapped by multiple change contracts", result.stdout)

    def test_greenfield_rejects_null_unresolved_decisions(self) -> None:
        with tempfile.TemporaryDirectory() as raw_directory:
            directory = Path(raw_directory)
            payload = valid_screen_contract()
            payload["unresolved_decisions"] = None
            screen = self.write_json(directory, "screen.json", payload)

            result = self.run_validator("screen-contract", str(screen))

            self.assertNotEqual(result.returncode, 0)
            self.assertIn("unresolved_decisions must be an empty array", result.stdout)

    def test_screen_contract_rejects_null_exclusions(self) -> None:
        with tempfile.TemporaryDirectory() as raw_directory:
            directory = Path(raw_directory)
            payload = valid_screen_contract()
            payload["exclusions"] = None
            screen = self.write_json(directory, "screen.json", payload)

            result = self.run_validator("screen-contract", str(screen))

            self.assertNotEqual(result.returncode, 0)
            self.assertIn("exclusions must be an array", result.stdout)

    def test_quality_report_handles_null_exclusions_without_traceback(self) -> None:
        with tempfile.TemporaryDirectory() as raw_directory:
            directory = Path(raw_directory)
            screen_payload = valid_screen_contract()
            screen_payload["exclusions"] = None
            screen = self.write_json(directory, "screen.json", screen_payload)
            report_payload = valid_quality_report()
            check = report_payload["gates"][5]["checks"][1]
            check["status"] = "not_applicable"
            check["exclusion_id"] = "EX1"
            check["not_applicable_reason"] = "desktop-only workflow"
            report = self.write_json(directory, "report.json", report_payload)

            result = self.run_validator("quality-report", str(report), str(screen))

            self.assertNotEqual(result.returncode, 0)
            self.assertIn("exclusions must be an array", result.stdout)
            self.assertNotIn("Traceback", result.stderr)

    def test_valid_redesign_traceability_passes(self) -> None:
        with tempfile.TemporaryDirectory() as raw_directory:
            directory = Path(raw_directory)
            screen = self.write_json(directory, "screen.json", valid_redesign_contract())

            result = self.run_validator("screen-contract", str(screen))

            self.assertEqual(result.returncode, 0, result.stdout + result.stderr)

    def test_browser_receipt_must_match_scenario_actions_and_expected(self) -> None:
        with tempfile.TemporaryDirectory() as raw_directory:
            directory = Path(raw_directory)
            screen = self.write_json(directory, "screen.json", valid_screen_contract())
            payload = valid_quality_report()
            payload["browser_receipts"][0]["actions"] = ["delete case"]
            payload["browser_receipts"][0]["expected"] = "case is deleted"
            report = self.write_json(directory, "report.json", payload)

            result = self.run_validator("quality-report", str(report), str(screen))

            self.assertNotEqual(result.returncode, 0)
            self.assertIn("actions must match", result.stdout)
            self.assertIn("expected must match", result.stdout)

    def test_browser_receipt_rejects_unknown_scenario_viewport_pair(self) -> None:
        with tempfile.TemporaryDirectory() as raw_directory:
            directory = Path(raw_directory)
            screen = self.write_json(directory, "screen.json", valid_screen_contract())
            payload = valid_quality_report()
            extra = dict(payload["browser_receipts"][0])
            extra["scenario_id"] = "UNKNOWN"
            payload["browser_receipts"].append(extra)
            report = self.write_json(directory, "report.json", payload)

            result = self.run_validator("quality-report", str(report), str(screen))

            self.assertNotEqual(result.returncode, 0)
            self.assertIn("unknown or unrequired", result.stdout)

    def test_audit_can_record_structured_unknowns_when_not_run(self) -> None:
        with tempfile.TemporaryDirectory() as raw_directory:
            directory = Path(raw_directory)
            payload = valid_screen_contract()
            payload["mode"] = "audit"
            payload["unresolved_decisions"] = [
                {
                    "id": "U1",
                    "area": "permission",
                    "reason": "read-only session cannot enter supervisor state",
                    "evidence_needed": "authorized supervisor observation",
                    "gate_ids": ["G3", "G4", "G7"],
                }
            ]
            screen = self.write_json(directory, "screen.json", payload)
            report = self.write_json(directory, "report.json", not_run_quality_report())

            result = self.run_validator("quality-report", str(report), str(screen))

            self.assertEqual(result.returncode, 0, result.stdout + result.stderr)

    def test_audit_with_unknowns_cannot_claim_passed(self) -> None:
        with tempfile.TemporaryDirectory() as raw_directory:
            directory = Path(raw_directory)
            payload = valid_screen_contract()
            payload["mode"] = "audit"
            payload["unresolved_decisions"] = [
                {
                    "id": "U1",
                    "area": "state",
                    "reason": "error state was not observable",
                    "evidence_needed": "non-mutating error-state fixture",
                    "gate_ids": ["G3", "G7"],
                }
            ]
            screen = self.write_json(directory, "screen.json", payload)
            report = self.write_json(directory, "report.json", valid_quality_report())

            result = self.run_validator("quality-report", str(report), str(screen))

            self.assertNotEqual(result.returncode, 0)
            self.assertIn("audit unresolved_decisions", result.stdout)

    def test_malformed_nested_values_return_validation_errors_not_tracebacks(self) -> None:
        malformed_screens = []
        states = valid_screen_contract()
        states["view_states"] = [{"bad": "shape"}]
        malformed_screens.append(states)
        viewports = valid_screen_contract()
        viewports["evidence_scenarios"][0]["required_viewports"] = None
        malformed_screens.append(viewports)
        requirement_edges = valid_screen_contract()
        requirement_edges["requirements"][0]["scenario_ids"] = [{"bad": "edge"}]
        malformed_screens.append(requirement_edges)
        scenario_edges = valid_screen_contract()
        scenario_edges["evidence_scenarios"][0]["requirement_ids"] = [
            {"bad": "edge"}
        ]
        malformed_screens.append(scenario_edges)

        with tempfile.TemporaryDirectory() as raw_directory:
            directory = Path(raw_directory)
            for index, payload in enumerate(malformed_screens):
                screen = self.write_json(directory, f"screen-{index}.json", payload)
                result = self.run_validator("screen-contract", str(screen))
                self.assertNotEqual(result.returncode, 0)
                self.assertNotIn("Traceback", result.stderr)

            screen = self.write_json(directory, "screen-valid.json", valid_screen_contract())
            report_payload = valid_quality_report()
            report_payload["browser_receipts"][0]["screenshots"] = None
            report = self.write_json(directory, "report-invalid.json", report_payload)
            result = self.run_validator("quality-report", str(report), str(screen))
            self.assertNotEqual(result.returncode, 0)
            self.assertNotIn("Traceback", result.stderr)

    def test_not_applicable_check_requires_matching_allowed_exclusion(self) -> None:
        with tempfile.TemporaryDirectory() as raw_directory:
            directory = Path(raw_directory)
            screen_payload = valid_screen_contract()
            screen_payload["exclusions"] = [
                {
                    "id": "EX1",
                    "kind": "desktop-only",
                    "check_ids": ["narrow-or-excluded"],
                    "reason": "workstations have a fixed supported minimum width",
                    "minimum_viewport": {"width": 1280, "height": 720},
                    "operational_reason": "operators use fixed warehouse workstations",
                }
            ]
            screen = self.write_json(directory, "screen.json", screen_payload)
            report_payload = valid_quality_report()
            check = report_payload["gates"][0]["checks"][0]
            check["status"] = "not_applicable"
            check["exclusion_id"] = "EX1"
            check["not_applicable_reason"] = "incorrect reuse"
            report = self.write_json(directory, "report.json", report_payload)

            result = self.run_validator("quality-report", str(report), str(screen))

            self.assertNotEqual(result.returncode, 0)
            self.assertIn("cannot be not_applicable", result.stdout)

    def test_screen_contract_requires_exact_wide_viewport(self) -> None:
        with tempfile.TemporaryDirectory() as raw_directory:
            directory = Path(raw_directory)
            payload = valid_screen_contract()
            payload["viewports"][0] = {"id": "wide", "width": 1280, "height": 720}
            screen = self.write_json(directory, "screen.json", payload)

            result = self.run_validator("screen-contract", str(screen))

            self.assertNotEqual(result.returncode, 0)
            self.assertIn("wide viewport must be 1440x900", result.stdout)

    def test_missing_narrow_viewport_requires_desktop_only_exclusion(self) -> None:
        with tempfile.TemporaryDirectory() as raw_directory:
            directory = Path(raw_directory)
            payload = valid_screen_contract()
            payload["viewports"] = [payload["viewports"][0]]
            payload["evidence_scenarios"][0]["required_viewports"] = ["wide"]
            screen = self.write_json(directory, "screen.json", payload)

            result = self.run_validator("screen-contract", str(screen))

            self.assertNotEqual(result.returncode, 0)
            self.assertIn("desktop-only exclusion", result.stdout)

    def test_desktop_only_exclusion_can_cover_only_the_narrow_check(self) -> None:
        with tempfile.TemporaryDirectory() as raw_directory:
            directory = Path(raw_directory)
            screen_payload = valid_screen_contract()
            screen_payload["viewports"] = [screen_payload["viewports"][0]]
            screen_payload["evidence_scenarios"][0]["required_viewports"] = ["wide"]
            screen_payload["exclusions"] = [
                {
                    "id": "EX-DESKTOP",
                    "kind": "desktop-only",
                    "check_ids": ["narrow-or-excluded"],
                    "reason": "the supported workstation has a fixed minimum width",
                    "minimum_viewport": {"width": 1280, "height": 720},
                    "operational_reason": "operators use fixed control-room workstations",
                }
            ]
            screen = self.write_json(directory, "screen.json", screen_payload)
            report_payload = valid_quality_report()
            report_payload["browser_receipts"] = [
                receipt
                for receipt in report_payload["browser_receipts"]
                if receipt["viewport_id"] == "wide"
            ]
            narrow_check = report_payload["gates"][5]["checks"][1]
            narrow_check["status"] = "not_applicable"
            narrow_check["exclusion_id"] = "EX-DESKTOP"
            narrow_check["not_applicable_reason"] = "desktop-only contract"
            report = self.write_json(directory, "report.json", report_payload)

            result = self.run_validator("quality-report", str(report), str(screen))

            self.assertEqual(result.returncode, 0, result.stdout + result.stderr)

    def test_requirement_scenario_edges_must_be_reciprocal(self) -> None:
        with tempfile.TemporaryDirectory() as raw_directory:
            directory = Path(raw_directory)
            payload = valid_screen_contract()
            payload["requirements"].append(
                {"id": "R2", "text": "Second behavior", "scenario_ids": ["S1"]}
            )
            payload["evidence_scenarios"][0]["requirement_ids"] = ["R1"]
            screen = self.write_json(directory, "screen.json", payload)

            result = self.run_validator("screen-contract", str(screen))

            self.assertNotEqual(result.returncode, 0)
            self.assertIn("reciprocal", result.stdout)

    def test_scenarios_must_cover_every_contract_dimension(self) -> None:
        with tempfile.TemporaryDirectory() as raw_directory:
            directory = Path(raw_directory)
            payload = valid_screen_contract()
            payload["evidence_scenarios"][0]["coverage"] = {
                "actions": ["assign"],
                "permissions": ["case:read"],
                "risks": [],
                "view_states": ["many"],
            }
            screen = self.write_json(directory, "screen.json", payload)

            result = self.run_validator("screen-contract", str(screen))

            self.assertNotEqual(result.returncode, 0)
            self.assertIn("scenario coverage missing actions", result.stdout)
            self.assertIn("scenario coverage missing permissions", result.stdout)
            self.assertIn("scenario coverage missing risks", result.stdout)
            self.assertIn("scenario coverage missing view_states", result.stdout)

    def test_covered_actions_must_be_exercised_by_the_scenario(self) -> None:
        with tempfile.TemporaryDirectory() as raw_directory:
            directory = Path(raw_directory)
            payload = valid_screen_contract()
            payload["evidence_scenarios"][0]["actions"] = ["assign"]
            screen = self.write_json(directory, "screen.json", payload)

            result = self.run_validator("screen-contract", str(screen))

            self.assertNotEqual(result.returncode, 0)
            self.assertIn("coverage.actions must be exercised", result.stdout)

    def test_change_contract_bundle_must_share_a_scenario(self) -> None:
        with tempfile.TemporaryDirectory() as raw_directory:
            directory = Path(raw_directory)
            payload = valid_redesign_contract()
            payload["requirements"].append(
                {"id": "R2", "text": "Second behavior", "scenario_ids": ["S2"]}
            )
            payload["evidence_scenarios"].append(
                {
                    "id": "S2",
                    "requirement_ids": ["R2"],
                    "initial_state": "many",
                    "actions": ["resolve case"],
                    "expected": "case is resolved",
                    "required_viewports": ["wide", "narrow"],
                    "coverage": {
                        "actions": [],
                        "permissions": [],
                        "risks": [],
                        "view_states": [],
                    },
                }
            )
            payload["change_contract"][0]["requirement_ids"] = ["R2"]
            screen = self.write_json(directory, "screen.json", payload)

            result = self.run_validator("screen-contract", str(screen))

            self.assertNotEqual(result.returncode, 0)
            self.assertIn("common scenario", result.stdout)

    def test_every_inventory_item_in_change_bundle_must_share_a_scenario(self) -> None:
        with tempfile.TemporaryDirectory() as raw_directory:
            directory = Path(raw_directory)
            payload = valid_redesign_contract()
            payload["requirements"].append(
                {"id": "R2", "text": "Second behavior", "scenario_ids": ["S2"]}
            )
            payload["evidence_scenarios"].append(
                {
                    "id": "S2",
                    "requirement_ids": ["R2"],
                    "initial_state": "many",
                    "actions": ["resolve case"],
                    "expected": "case is resolved",
                    "required_viewports": ["wide", "narrow"],
                    "coverage": {
                        "actions": [],
                        "permissions": [],
                        "risks": [],
                        "view_states": [],
                    },
                }
            )
            payload["current_behavior_inventory"].append(
                {
                    "id": "CB2",
                    "kind": "permission",
                    "observed": "supervisor resolves a case",
                    "evidence": ["src/permissions.ts:8"],
                    "decision": "preserve",
                    "reason": "authorization boundary",
                    "implementation_target": "src/permissions.ts",
                    "scenario_ids": ["S2"],
                }
            )
            payload["change_contract"][0]["inventory_ids"] = ["CB1", "CB2"]
            screen = self.write_json(directory, "screen.json", payload)

            result = self.run_validator("screen-contract", str(screen))

            self.assertNotEqual(result.returncode, 0)
            self.assertIn("inventory CB2 must share a common scenario", result.stdout)

    def test_change_bundle_requires_one_scenario_shared_by_every_member(self) -> None:
        with tempfile.TemporaryDirectory() as raw_directory:
            directory = Path(raw_directory)
            payload = valid_redesign_contract()
            payload["requirements"].append(
                {"id": "R2", "text": "Second behavior", "scenario_ids": ["S2"]}
            )
            payload["evidence_scenarios"].append(
                {
                    "id": "S2",
                    "requirement_ids": ["R2"],
                    "initial_state": "many",
                    "actions": ["resolve case"],
                    "expected": "case is resolved",
                    "required_viewports": ["wide", "narrow"],
                    "coverage": {
                        "actions": [],
                        "permissions": [],
                        "risks": [],
                        "view_states": [],
                    },
                }
            )
            payload["current_behavior_inventory"].append(
                {
                    "id": "CB2",
                    "kind": "permission",
                    "observed": "supervisor resolves a case",
                    "evidence": ["src/permissions.ts:8"],
                    "decision": "preserve",
                    "reason": "authorization boundary",
                    "implementation_target": "src/permissions.ts",
                    "scenario_ids": ["S2"],
                }
            )
            payload["change_contract"][0]["inventory_ids"] = ["CB1", "CB2"]
            payload["change_contract"][0]["requirement_ids"] = ["R1", "R2"]
            screen = self.write_json(directory, "screen.json", payload)

            result = self.run_validator("screen-contract", str(screen))

            self.assertNotEqual(result.returncode, 0)
            self.assertIn("one scenario shared by every member", result.stdout)

    def test_unhashable_enum_and_gate_ids_return_errors_not_tracebacks(self) -> None:
        with tempfile.TemporaryDirectory() as raw_directory:
            directory = Path(raw_directory)
            malformed_screens = []
            mode = valid_screen_contract()
            mode["mode"] = []
            malformed_screens.append(mode)
            surface = valid_screen_contract()
            surface["surface"] = {"bad": "surface"}
            malformed_screens.append(surface)
            exclusion = valid_screen_contract()
            exclusion["exclusions"] = [
                {
                    "id": "EX1",
                    "kind": [],
                    "check_ids": ["narrow-or-excluded"],
                    "reason": "bad kind shape",
                }
            ]
            malformed_screens.append(exclusion)
            for index, payload in enumerate(malformed_screens):
                screen = self.write_json(directory, f"enum-{index}.json", payload)
                result = self.run_validator("screen-contract", str(screen))
                self.assertNotEqual(result.returncode, 0)
                self.assertNotIn("Traceback", result.stderr)

            screen = self.write_json(directory, "screen.json", valid_screen_contract())
            report_payload = valid_quality_report()
            report_payload["gates"][0]["id"] = []
            report = self.write_json(directory, "report.json", report_payload)
            result = self.run_validator("quality-report", str(report), str(screen))
            self.assertNotEqual(result.returncode, 0)
            self.assertNotIn("Traceback", result.stderr)

    def test_audit_unknowns_forbid_individual_required_gate_passes(self) -> None:
        with tempfile.TemporaryDirectory() as raw_directory:
            directory = Path(raw_directory)
            payload = valid_screen_contract()
            payload["mode"] = "audit"
            payload["unresolved_decisions"] = [
                {
                    "id": "U1",
                    "area": "permission",
                    "reason": "supervisor view unavailable",
                    "evidence_needed": "authorized observation",
                    "gate_ids": ["G3"],
                }
            ]
            screen = self.write_json(directory, "screen.json", payload)
            report_payload = not_run_quality_report()
            report_payload["overall"] = "inconclusive"
            report_payload["gates"][3]["status"] = "passed"
            for check in report_payload["gates"][3]["checks"]:
                check["status"] = "passed"
            report = self.write_json(directory, "report.json", report_payload)

            result = self.run_validator("quality-report", str(report), str(screen))

            self.assertNotEqual(result.returncode, 0)
            self.assertIn("audit unresolved_decisions forbid passed gates", result.stdout)

    def test_audit_unknown_forbids_its_declared_visual_gate(self) -> None:
        with tempfile.TemporaryDirectory() as raw_directory:
            directory = Path(raw_directory)
            payload = valid_screen_contract()
            payload["mode"] = "audit"
            payload["unresolved_decisions"] = [
                {
                    "id": "U1",
                    "area": "contrast",
                    "reason": "contrast tooling was unavailable",
                    "evidence_needed": "contrast measurement",
                    "gate_ids": ["G6"],
                }
            ]
            screen = self.write_json(directory, "screen.json", payload)
            report_payload = not_run_quality_report()
            report_payload["overall"] = "inconclusive"
            report_payload["gates"][6]["status"] = "passed"
            for check in report_payload["gates"][6]["checks"]:
                check["status"] = "passed"
            report = self.write_json(directory, "report.json", report_payload)

            result = self.run_validator("quality-report", str(report), str(screen))

            self.assertNotEqual(result.returncode, 0)
            self.assertIn("G6", result.stdout)

    def test_boolean_viewport_dimensions_are_rejected(self) -> None:
        with tempfile.TemporaryDirectory() as raw_directory:
            directory = Path(raw_directory)
            payload = valid_screen_contract()
            payload["viewports"][1] = {"id": "narrow", "width": True, "height": True}
            screen = self.write_json(directory, "screen.json", payload)

            result = self.run_validator("screen-contract", str(screen))

            self.assertNotEqual(result.returncode, 0)
            self.assertIn("positive integer", result.stdout)

    def test_console_runtime_errors_require_string_items(self) -> None:
        with tempfile.TemporaryDirectory() as raw_directory:
            directory = Path(raw_directory)
            screen = self.write_json(directory, "screen.json", valid_screen_contract())
            payload = not_run_quality_report()
            payload["browser_receipts"] = [valid_quality_report()["browser_receipts"][0]]
            payload["browser_receipts"][0]["status"] = "failed"
            payload["browser_receipts"][0]["console_runtime_errors"] = [{"bad": "error"}]
            report = self.write_json(directory, "report.json", payload)

            result = self.run_validator("quality-report", str(report), str(screen))

            self.assertNotEqual(result.returncode, 0)
            self.assertIn("array of strings", result.stdout)

    def test_desktop_only_requires_structured_minimum_viewport(self) -> None:
        with tempfile.TemporaryDirectory() as raw_directory:
            directory = Path(raw_directory)
            payload = valid_screen_contract()
            payload["viewports"] = [payload["viewports"][0]]
            payload["evidence_scenarios"][0]["required_viewports"] = ["wide"]
            payload["exclusions"] = [
                {
                    "id": "EX-DESKTOP",
                    "kind": "desktop-only",
                    "check_ids": ["narrow-or-excluded"],
                    "reason": "x",
                }
            ]
            screen = self.write_json(directory, "screen.json", payload)

            result = self.run_validator("screen-contract", str(screen))

            self.assertNotEqual(result.returncode, 0)
            self.assertIn("minimum_viewport", result.stdout)
            self.assertIn("operational_reason", result.stdout)

    def test_common_placeholder_sentinels_cannot_claim_passed(self) -> None:
        for sentinel in ("TBD", "replace-me", "N/A"):
            with self.subTest(sentinel=sentinel), tempfile.TemporaryDirectory() as raw_directory:
                directory = Path(raw_directory)
                screen = self.write_json(directory, "screen.json", valid_screen_contract())
                payload = valid_quality_report()
                payload["browser_receipts"][0]["observed"] = sentinel
                report = self.write_json(directory, "report.json", payload)

                result = self.run_validator("quality-report", str(report), str(screen))

                self.assertNotEqual(result.returncode, 0)
                self.assertIn("placeholder", result.stdout)

    def test_unknown_contract_and_report_fields_fail(self) -> None:
        with tempfile.TemporaryDirectory() as raw_directory:
            directory = Path(raw_directory)
            screen_payload = valid_screen_contract()
            screen_payload["typo_field"] = "ignored"
            screen = self.write_json(directory, "screen.json", screen_payload)

            screen_result = self.run_validator("screen-contract", str(screen))

            self.assertNotEqual(screen_result.returncode, 0)
            self.assertIn("unknown fields", screen_result.stdout)

            valid_screen = self.write_json(
                directory, "valid-screen.json", valid_screen_contract()
            )
            report_payload = not_run_quality_report()
            report_payload["gates"][0]["typo_field"] = "ignored"
            report = self.write_json(directory, "report.json", report_payload)

            report_result = self.run_validator(
                "quality-report", str(report), str(valid_screen)
            )

            self.assertNotEqual(report_result.returncode, 0)
            self.assertIn("unknown fields", report_result.stdout)

    def test_eval_expected_contract_rejects_unknown_keys_and_skills(self) -> None:
        with tempfile.TemporaryDirectory() as raw_directory:
            directory = Path(raw_directory)
            payload = {
                "schema_version": "operations-ui-evals-v1",
                "cases": [
                    {
                        "id": "bad-expectation",
                        "prompt": "design an operations screen",
                        "expected": {"selcet": ["made-up:skill"]},
                    }
                ],
            }
            cases = self.write_json(directory, "cases.json", payload)

            result = self.run_validator("evals", str(cases))

            self.assertNotEqual(result.returncode, 0)
            self.assertIn("unknown fields", result.stdout)

            payload["cases"][0]["expected"] = {"select": ["made-up:skill"]}
            cases = self.write_json(directory, "unknown-skill.json", payload)

            result = self.run_validator("evals", str(cases))

            self.assertNotEqual(result.returncode, 0)
            self.assertIn("unknown skill ids", result.stdout)

    def test_eval_expected_contract_rejects_selection_conflicts(self) -> None:
        with tempfile.TemporaryDirectory() as raw_directory:
            directory = Path(raw_directory)
            skill_id = "operations-ui:design-operations-ui"
            payload = {
                "schema_version": "operations-ui-evals-v1",
                "cases": [
                    {
                        "id": "conflict",
                        "prompt": "design an operations screen",
                        "expected": {
                            "select": [skill_id],
                            "must_not_select": [skill_id],
                        },
                    }
                ],
            }
            cases = self.write_json(directory, "cases.json", payload)

            result = self.run_validator("evals", str(cases))

            self.assertNotEqual(result.returncode, 0)
            self.assertIn("both select and must_not_select", result.stdout)

    def test_eval_expected_enum_shape_returns_error_not_traceback(self) -> None:
        with tempfile.TemporaryDirectory() as raw_directory:
            directory = Path(raw_directory)
            payload = {
                "schema_version": "operations-ui-evals-v1",
                "cases": [
                    {
                        "id": "bad-mode-shape",
                        "prompt": "audit this operations screen",
                        "expected": {"mode": []},
                    }
                ],
            }
            cases = self.write_json(directory, "cases.json", payload)

            result = self.run_validator("evals", str(cases))

            self.assertNotEqual(result.returncode, 0)
            self.assertNotIn("Traceback", result.stderr)
            self.assertIn("expected.mode", result.stdout)

    def test_duplicate_eval_case_id_fails(self) -> None:
        with tempfile.TemporaryDirectory() as raw_directory:
            directory = Path(raw_directory)
            payload = {
                "schema_version": "operations-ui-evals-v1",
                "cases": [
                    {"id": "duplicate", "prompt": "one", "expected": {}},
                    {"id": "duplicate", "prompt": "two", "expected": {}},
                ],
            }
            cases = self.write_json(directory, "cases.json", payload)

            result = self.run_validator("evals", str(cases))

            self.assertNotEqual(result.returncode, 0)
            self.assertIn("duplicate", result.stdout)


if __name__ == "__main__":
    unittest.main()
