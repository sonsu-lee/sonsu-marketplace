from __future__ import annotations

import importlib.util
import base64
import json
import subprocess
import tempfile
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[3]
PLUGIN_ROOT = ROOT / "plugins" / "operations-ui"
VALIDATOR = PLUGIN_ROOT / "scripts" / "validate_contracts.py"
HELPERS_PATH = ROOT / "evals" / "design-quality" / "test_validate_design_quality.py"

spec = importlib.util.spec_from_file_location("design_quality_test_helpers", HELPERS_PATH)
assert spec and spec.loader
helpers = importlib.util.module_from_spec(spec)
spec.loader.exec_module(helpers)


# A valid 1x1 RGBA PNG. Runtime evidence must point to a real image, not a text placeholder.
PNG_1X1 = base64.b64decode(
    "iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAQAAAC1HAwCAAAAC0lEQVR42mNk+A8AAQUBAScY42YAAAAASUVORK5CYII="
)


def valid_evals() -> dict:
    return {
        "schema_version": "operations-ui-evals-v2",
        "cases": [
            {
                "id": "redesign-implementation",
                "prompt": "Redesign and implement an existing queue console.",
                "expected": {
                    "select": ["operations-ui:redesign-operations-ui"],
                    "must_not_select": [],
                    "profile": "operations-ui",
                    "artifact_scope": "implementation",
                    "mode": "redesign",
                    "requirements": [
                        "build-design-decision-contract",
                        "inventory-current-behavior",
                        "map-change-contract",
                        "run-dq0-dq7",
                        "collect-browser-receipts",
                    ],
                    "prohibitions": ["claim-end-to-end-before-live-evidence"],
                },
            },
            {
                "id": "read-only-audit",
                "prompt": "Audit this live operations screen without changing it.",
                "expected": {
                    "select": ["operations-ui:audit-operations-ui"],
                    "must_not_select": [],
                    "profile": "operations-ui",
                    "artifact_scope": "live",
                    "mode": "audit",
                    "requirements": [
                        "build-design-decision-contract",
                        "run-dq0-dq8",
                        "collect-browser-receipts",
                        "collect-risk-appropriate-user-evidence",
                    ],
                    "prohibitions": ["mutate-target", "claim-validation-without-user-evidence"],
                },
            },
        ],
    }


class OperationsContractValidatorTests(unittest.TestCase):
    def run_validator(
        self,
        command: str,
        *payloads: dict,
        create_screenshot: bool = False,
        corrupt_screenshot: bool = False,
        fake_magic_screenshot: bool = False,
    ) -> subprocess.CompletedProcess[str]:
        with tempfile.TemporaryDirectory() as tmp:
            base = Path(tmp)
            paths: list[str] = []
            for index, payload in enumerate(payloads):
                path = base / f"payload-{index}.json"
                path.write_text(json.dumps(payload), encoding="utf-8")
                paths.append(str(path))
                helpers.DesignQualityValidatorTests.materialize_evidence(base, payload)
            screenshot = base / "evidence" / "queue-triage.png"
            if not create_screenshot and screenshot.exists():
                screenshot.unlink()
            if create_screenshot:
                evidence = base / "evidence"
                evidence.mkdir(exist_ok=True)
                if fake_magic_screenshot:
                    data = (
                        b"\x89PNG\r\n\x1a\n"
                        + b"\x00\x00\x00\x0dIHDR"
                        + b"\x00\x00\x00\x01\x00\x00\x00\x01"
                        + b"\x08\x06\x00\x00\x00"
                        + b"\x00\x00\x00\x00"
                        + b"\x00\x00\x00\x00IEND\xaeB`\x82"
                    )
                else:
                    data = b"not-an-image" if corrupt_screenshot else PNG_1X1
                screenshot.write_bytes(data)
            return subprocess.run(
                ["python3", str(VALIDATOR), command, *paths],
                cwd=ROOT,
                text=True,
                capture_output=True,
                check=False,
            )

    def test_screen_contract_accepts_common_v2_operations_profile(self) -> None:
        result = self.run_validator("screen-contract", helpers.valid_operations_contract())
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)

    def test_screen_contract_rejects_legacy_v1(self) -> None:
        contract = helpers.valid_operations_contract()
        contract["schema_version"] = "operations-ui-screen-contract-v1"
        result = self.run_validator("screen-contract", contract)
        self.assertNotEqual(result.returncode, 0)
        self.assertIn("design-decision-contract-v1", result.stdout)

    def test_screen_contract_rejects_another_profile(self) -> None:
        result = self.run_validator("screen-contract", helpers.valid_contract())
        self.assertNotEqual(result.returncode, 0)
        self.assertIn("profile must be operations-ui", result.stdout)

    def test_quality_report_accepts_real_runtime_screenshot(self) -> None:
        contract = helpers.valid_operations_contract()
        report = helpers.valid_report(contract)
        result = self.run_validator(
            "quality-report", report, contract, create_screenshot=True
        )
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)

    def test_quality_report_rejects_missing_runtime_screenshot(self) -> None:
        contract = helpers.valid_operations_contract()
        report = helpers.valid_report(contract)
        result = self.run_validator("quality-report", report, contract)
        self.assertNotEqual(result.returncode, 0)
        self.assertIn("screenshot does not exist", result.stdout)

    def test_quality_report_rejects_text_file_named_png(self) -> None:
        contract = helpers.valid_operations_contract()
        report = helpers.valid_report(contract)
        result = self.run_validator(
            "quality-report",
            report,
            contract,
            create_screenshot=True,
            corrupt_screenshot=True,
        )
        self.assertNotEqual(result.returncode, 0)
        self.assertIn("valid PNG, JPEG, or WebP", result.stdout)

    def test_quality_report_rejects_magic_bytes_without_valid_png_structure(self) -> None:
        contract = helpers.valid_operations_contract()
        report = helpers.valid_report(contract)
        result = self.run_validator(
            "quality-report",
            report,
            contract,
            create_screenshot=True,
            fake_magic_screenshot=True,
        )
        self.assertNotEqual(result.returncode, 0)
        self.assertIn("valid PNG, JPEG, or WebP", result.stdout)

    def test_quality_report_rejects_nul_screenshot_path_without_traceback(self) -> None:
        contract = helpers.valid_operations_contract()
        report = helpers.valid_report(contract)
        report["extensions"]["operations"]["browser_receipts"][0]["screenshots"] = [
            "evidence/queue\x00triage.png"
        ]
        result = self.run_validator("quality-report", report, contract)
        self.assertNotEqual(result.returncode, 0)
        self.assertIn("relative paths", result.stdout)
        self.assertNotIn("Traceback", result.stderr)

    def test_evals_accept_v2_semantic_cases(self) -> None:
        result = self.run_validator("evals", valid_evals())
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)

    def test_evals_reject_v1_contract(self) -> None:
        payload = valid_evals()
        payload["schema_version"] = "operations-ui-evals-v1"
        result = self.run_validator("evals", payload)
        self.assertNotEqual(result.returncode, 0)
        self.assertIn("operations-ui-evals-v2", result.stdout)

    def test_malformed_json_fails_cleanly(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "broken.json"
            path.write_text("{", encoding="utf-8")
            result = subprocess.run(
                ["python3", str(VALIDATOR), "screen-contract", str(path)],
                cwd=ROOT,
                text=True,
                capture_output=True,
                check=False,
            )
        self.assertNotEqual(result.returncode, 0)
        self.assertIn("invalid JSON", result.stdout)


if __name__ == "__main__":
    unittest.main()
