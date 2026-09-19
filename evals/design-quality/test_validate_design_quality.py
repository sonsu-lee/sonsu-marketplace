from __future__ import annotations

import copy
import hashlib
import json
import subprocess
import tempfile
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
VALIDATOR = ROOT / "plugins" / "interface-design" / "scripts" / "validate_design_quality.py"
GATE_CHECKS = {
    "DQ0": ["contract-completeness", "traceability", "pre-registered-metrics"],
    "DQ1": ["user-context-task", "decision-and-error-cost"],
    "DQ2": ["information-priority", "representation-rationale"],
    "DQ3": ["design-system-mapping", "semantic-not-color-only"],
    "DQ4": ["applicable-states", "content-and-localization-resilience"],
    "DQ5": ["action-feedback", "safety-and-recovery"],
    "DQ6": ["adaptive-environments", "accessibility-profile"],
    "DQ7": ["artifact-provenance", "scenario-environment-coverage"],
    "DQ8": ["outcome-metrics", "risk-appropriate-user-evidence"],
}


def canonical_digest(value: dict) -> str:
    encoded = json.dumps(
        value, ensure_ascii=False, sort_keys=True, separators=(",", ":")
    ).encode("utf-8")
    return "sha256:" + hashlib.sha256(encoded).hexdigest()


def figma_contract_extension() -> dict:
    return {
        "target": "file/page/queue-frame",
        "required_capabilities": ["node-readback", "screenshot", "resize-readback"],
        "component_strategy": "Reuse the product library and create only repeated missing patterns.",
        "resize_scenarios": [
            {
                "id": "resize-triage-desktop",
                "scenario_id": "triage-case",
                "environment_id": "desktop-ko",
                "expectation": "must-know columns remain readable",
            }
        ],
        "prototype_scenarios": [],
    }


def valid_contract(scope: str = "proposal", risk: str = "low") -> dict:
    factors = []
    if risk == "medium":
        factors = ["workflow-disruption"]
    elif risk == "high":
        factors = ["financial"]
    contract = {
        "schema_version": "design-decision-contract-v1",
        "id": "service-queue",
        "profile": "interface-design",
        "artifact_scope": scope,
        "mode": "redesign",
        "revision": "r1",
        "locked_at": "2026-09-17T00:00:00Z",
        "actors": ["support operator"],
        "contexts": ["triage incoming cases during a busy shift"],
        "environments": [
            {
                "id": "desktop-ko",
                "platform": "web",
                "width": 1280,
                "height": 800,
                "input_methods": ["keyboard", "pointer"],
                "locale": "ko-KR",
                "writing_mode": "horizontal-tb",
                "accessibility_profile": "WCAG-2.2-AA",
            }
        ],
        "primary_question": "Which case needs attention first?",
        "intended_outcome": "The operator selects the highest-risk case without overlooking stale data.",
        "risk_profile": {
            "level": risk,
            "factors": factors,
            "rationale": "The declared factors determine the minimum evidence level.",
        },
        "task_scenarios": [
            {
                "id": "triage-case",
                "actor": "support operator",
                "starting_context": "three cases are waiting",
                "task": "select the case that needs attention first",
                "correct_outcome": "the overdue high-risk case is selected",
                "wrong_outcome": "a routine case is selected first",
                "wrong_outcome_cost": "the overdue case remains unresolved",
                "information_ids": ["case-risk", "case-age"],
                "representation_ids": ["priority-column"],
                "environment_ids": ["desktop-ko"],
                "observable_success": "the operator selects case A and explains the risk and age cues",
            }
        ],
        "information_requirements": [
            {
                "id": "case-risk",
                "role": "must_know",
                "meaning": "severity of customer impact",
                "source": "case service",
                "freshness": "current response",
                "uncertainty": "none when the service is current",
                "task_ids": ["triage-case"],
            },
            {
                "id": "case-age",
                "role": "must_know",
                "meaning": "elapsed wait time",
                "source": "case service",
                "freshness": "updated every minute",
                "uncertainty": "may be stale while offline",
                "task_ids": ["triage-case"],
            },
        ],
        "representation_map": [
            {
                "id": "priority-column",
                "information_ids": ["case-risk", "case-age"],
                "kind": "table-column",
                "semantic_role": "decision-priority",
                "non_color_signals": ["risk label", "elapsed-time text", "sort position"],
                "rationale": "supports comparison without relying on color alone",
                "task_ids": ["triage-case"],
            }
        ],
        "states": [
            {"id": "loaded", "applicable": True, "reason": "primary task state"},
            {"id": "stale", "applicable": True, "reason": "network data can age"},
        ],
        "metric_targets": [
            {
                "id": "task-success",
                "kind": "rate",
                "role": "primary",
                "operator": ">=",
                "target": 0.8,
                "unit": "ratio",
                "rationale": "set before evaluation from the current baseline and error cost",
            },
            {
                "id": "critical-harm",
                "kind": "count",
                "role": "guardrail",
                "operator": "==",
                "target": 0,
                "unit": "events",
                "rationale": "critical harm is never averaged away",
            },
        ],
        "outcome_plan": {
            "id": "queue-triage-evaluation-v1",
            "scenario_ids": ["triage-case"],
            "metric_ids": ["task-success", "critical-harm"],
            "participant_criteria": "Support operators who triage queues at least weekly.",
            "planned_participant_count": 2 if risk == "low" else 5,
            "protocol": "Run the locked triage scenario without coaching and record outcomes.",
            "rationale": "The sample and protocol are fixed before observing results.",
        },
        "unresolved_decisions": [],
        "exclusions": [],
    }
    if scope == "figma":
        contract["extensions"] = {"figma": figma_contract_extension()}
    return contract


def valid_operations_contract(scope: str = "implementation") -> dict:
    contract = valid_contract(scope)
    contract["profile"] = "operations-ui"
    contract["task_scenarios"][0].update(
        {
            "requirement_ids": ["REQ-1"],
            "actions": ["select-case"],
            "coverage": {
                "jobs": ["triage cases"],
                "entities": ["case"],
                "lifecycle": ["waiting", "selected"],
                "actions": ["select-case"],
                "permissions": ["queue-read"],
                "risks": ["stale-priority"],
                "states": ["loaded", "stale"],
            },
        }
    )
    contract.setdefault("extensions", {})["operations"] = {
            "surface": "standalone-console",
            "jobs": ["triage cases"],
            "entities": ["case"],
            "lifecycle": ["waiting", "selected"],
            "actions": ["select-case"],
            "permissions": ["queue-read"],
            "risks": ["stale-priority"],
            "requirements": [
                {
                    "id": "REQ-1",
                    "text": "The highest-risk waiting case can be selected.",
                    "scenario_ids": ["triage-case"],
                }
            ],
            "current_behavior_inventory": [
                {
                    "id": "INV-1",
                    "kind": "feature",
                    "observed": "The queue exposes case risk and age.",
                    "evidence": ["evidence/current-queue.png"],
                    "decision": "preserve",
                    "reason": "These fields support the primary decision.",
                    "implementation_target": "queue priority columns",
                    "scenario_ids": ["triage-case"],
                }
            ],
            "change_contract": [
                {
                    "id": "CHANGE-1",
                    "inventory_ids": ["INV-1"],
                    "requirement_ids": ["REQ-1"],
                    "description": "Preserve risk and age while clarifying their priority.",
                }
            ],
    }
    return contract


def valid_figma_contract() -> dict:
    contract = valid_contract("figma")
    contract["profile"] = "figma-workflow"
    return contract


def evaluator(
    evaluator_id: str,
    relationship: str = "independent",
    score: int = 3,
    *,
    artifact_revision: str = "artifact-r1",
    contract_digest: str = "sha256:" + "0" * 64,
) -> dict:
    return {
        "evaluator_id": evaluator_id,
        "relationship": relationship,
        "evaluated_at": "2026-09-17T01:00:00Z",
        "artifact_revision": artifact_revision,
        "contract_digest": contract_digest,
        "scores": {f"DQ{index}": score for index in range(1, 7)},
        "evidence": [f"evidence/{evaluator_id}.md"],
    }


def valid_report(contract: dict) -> dict:
    scope = contract["artifact_scope"]
    last_required = {"proposal": 6, "figma": 7, "implementation": 7, "live": 8}[scope]
    gates = []
    for index in range(9):
        gate_id = f"DQ{index}"
        required = index <= last_required
        rubric_score = 3 if 1 <= index <= 6 and required else None
        gates.append(
            {
                "id": gate_id,
                "required": required,
                "status": "passed" if required else "not_run",
                "score": rubric_score,
                "evidence": [f"evidence/{gate_id.lower()}.md"] if required else [],
                "checks": [
                    {
                        "id": check_id,
                        "status": "passed" if required else "not_run",
                        "evidence": [f"evidence/{gate_id.lower()}-{check_id}.md"] if required else [],
                    }
                    for check_id in GATE_CHECKS[gate_id]
                ],
            }
        )
    outcome_evidence = []
    metric_results = []
    if scope == "live":
        plan = contract["outcome_plan"]
        outcome_binding = {
            "plan_id": plan["id"],
            "scenario_ids": plan["scenario_ids"],
            "metric_ids": plan["metric_ids"],
            "participant_criteria": plan["participant_criteria"],
            "planned_participant_count": plan["planned_participant_count"],
            "protocol": plan["protocol"],
        }
        risk = contract["risk_profile"]["level"]
        if risk == "low":
            outcome_evidence = [
                {
                    "id": "walkthrough-1",
                    "run_id": "walkthrough-run-1",
                    "observed_at": "2026-09-17T02:00:00Z",
                    "artifact_revision": "artifact-r1",
                    "kind": "independent-walkthrough",
                    "status": "passed",
                    "participant_count": 1,
                    "evidence": ["evidence/walkthrough-1.md"],
                    **outcome_binding,
                },
                {
                    "id": "walkthrough-2",
                    "run_id": "walkthrough-run-2",
                    "observed_at": "2026-09-17T02:30:00Z",
                    "artifact_revision": "artifact-r1",
                    "kind": "independent-walkthrough",
                    "status": "passed",
                    "participant_count": 1,
                    "evidence": ["evidence/walkthrough-2.md"],
                    **outcome_binding,
                },
            ]
        elif risk == "medium":
            outcome_evidence = [
                {
                    "id": "user-test",
                    "run_id": "user-test-run-1",
                    "observed_at": "2026-09-17T02:00:00Z",
                    "artifact_revision": "artifact-r1",
                    "kind": "representative-user-test",
                    "status": "passed",
                    "participant_count": 5,
                    "evidence": ["evidence/user-test.md"],
                    **outcome_binding,
                }
            ]
        else:
            outcome_evidence = [
                {
                    "id": "user-test",
                    "run_id": "user-test-run-1",
                    "observed_at": "2026-09-17T02:00:00Z",
                    "artifact_revision": "artifact-r1",
                    "kind": "representative-user-test",
                    "status": "passed",
                    "participant_count": 5,
                    "evidence": ["evidence/user-test.md"],
                    **outcome_binding,
                },
                {
                    "id": "safety-review",
                    "run_id": "safety-review-run-1",
                    "observed_at": "2026-09-17T02:30:00Z",
                    "artifact_revision": "artifact-r1",
                    "kind": "domain-safety-review",
                    "status": "passed",
                    "participant_count": 1,
                    "evidence": ["evidence/safety-review.md"],
                    **outcome_binding,
                },
            ]
        metric_results = [
            {
                "metric_id": "task-success",
                "run_id": "metric-task-success-run-1",
                "observed_at": "2026-09-17T03:00:00Z",
                "artifact_revision": "artifact-r1",
                "observed": 0.9,
                "status": "passed",
                "evidence": ["evidence/task-success.json"],
            },
            {
                "metric_id": "critical-harm",
                "run_id": "metric-critical-harm-run-1",
                "observed_at": "2026-09-17T03:00:00Z",
                "artifact_revision": "artifact-r1",
                "observed": 0,
                "status": "passed",
                "evidence": ["evidence/critical-harm.json"],
            },
        ]
    digest = canonical_digest(contract)
    report = {
        "schema_version": "design-quality-report-v1",
        "contract_id": contract["id"],
        "contract_revision": contract["revision"],
        "contract_digest": digest,
        "profile": contract["profile"],
        "artifact": {
            "scope": scope,
            "revision": "artifact-r1",
            "locators": ["artifacts/proposal.md"],
        },
        "scope_status": "passed",
        "end_to_end_status": "passed" if scope == "live" else "not_run",
        "claim_level": "validated" if scope == "live" else "provisional",
        "gates": gates,
        "evaluator_runs": [
            evaluator("reviewer-a", contract_digest=digest),
            evaluator("reviewer-b", contract_digest=digest),
        ],
        "metric_results": metric_results,
        "outcome_evidence": outcome_evidence,
        "findings": [],
    }
    extensions: dict = {}
    if contract["profile"] == "operations-ui":
        extensions["operations"] = {
                "design_system_mapping": {
                    "system_id": "product-design-system-v3",
                    "token_source": "src/tokens/semantic.ts",
                    "mappings": [
                        {
                            "representation_ids": ["priority-column"],
                            "semantic_role": "surface",
                            "token_id": "color.background.surface",
                            "evidence": ["evidence/token-map.md"],
                        },
                        {
                            "representation_ids": ["priority-column"],
                            "semantic_role": "primary-text",
                            "token_id": "color.text.primary",
                            "evidence": ["evidence/token-map.md"],
                        },
                    ],
                },
                "browser_receipts": [
                    {
                        "scenario_id": "triage-case",
                        "environment_id": "desktop-ko",
                        "command": "pnpm test:e2e -- queue-triage",
                        "build_or_revision": "artifact-r1",
                        "url": "http://127.0.0.1:3000/queue",
                        "status": "passed",
                        "actions": ["select-case"],
                        "expected": contract["task_scenarios"][0]["observable_success"],
                        "observed": "Case A was selected using its risk and age cues.",
                        "screenshots": ["evidence/queue-triage.png"],
                        "console_runtime_errors": [],
                    }
                ] if scope in {"implementation", "live"} else [],
        }
    if contract["profile"] == "interface-design" and scope in {"implementation", "live"}:
        extensions["interface"] = {
            "runtime_receipts": [
                {
                    "scenario_id": "triage-case",
                    "environment_id": "desktop-ko",
                    "command": "pnpm test:e2e -- queue-triage",
                    "build_or_revision": "artifact-r1",
                    "url": "http://127.0.0.1:3000/queue",
                    "status": "passed",
                    "steps": ["open queue", "compare risk and age", "select case A"],
                    "expected": contract["task_scenarios"][0]["observable_success"],
                    "observed": "Case A was selected using its risk and age cues.",
                    "screenshots": ["evidence/interface-queue-triage.png"],
                    "console_runtime_errors": [],
                }
            ]
        }
    if scope == "figma" or contract["profile"] == "figma-workflow":
        extensions["figma"] = {
            "native_receipts": [
                {
                    "scenario_id": "triage-case",
                    "environment_id": "desktop-ko",
                    "artifact_revision": "artifact-r1",
                    "status": "passed",
                    "node_ids": ["queue-frame", "priority-column"],
                    "capabilities": ["node-readback", "screenshot", "resize-readback"],
                    "structure_observed": "Frame hierarchy, components, variables and Auto Layout were read back.",
                    "resize_scenario_ids": ["resize-triage-desktop"],
                    "prototype_scenario_ids": [],
                    "evidence": ["evidence/figma-native-readback.md"],
                }
            ]
        }
    if extensions:
        report["extensions"] = extensions
    return report


class DesignQualityValidatorTests(unittest.TestCase):
    @staticmethod
    def materialize_evidence(base: Path, payload: object) -> None:
        if isinstance(payload, dict):
            for key, value in payload.items():
                if key in {"evidence", "locators", "screenshots"} and isinstance(value, list):
                    for relative in value:
                        if (
                            not isinstance(relative, str)
                            or "\x00" in relative
                            or "://" in relative
                            or ".." in relative.split("/")
                        ):
                            continue
                        path = base / relative
                        path.parent.mkdir(parents=True, exist_ok=True)
                        if not path.exists():
                            path.write_text("test evidence\n", encoding="utf-8")
                DesignQualityValidatorTests.materialize_evidence(base, value)
        elif isinstance(payload, list):
            for value in payload:
                DesignQualityValidatorTests.materialize_evidence(base, value)

    def run_validator(self, command: str, *payloads: dict) -> subprocess.CompletedProcess[str]:
        with tempfile.TemporaryDirectory() as tmp:
            paths = []
            for index, payload in enumerate(payloads):
                path = Path(tmp) / f"payload-{index}.json"
                path.write_text(json.dumps(payload), encoding="utf-8")
                paths.append(str(path))
                self.materialize_evidence(Path(tmp), payload)
            return subprocess.run(
                ["python3", str(VALIDATOR), command, *paths],
                cwd=ROOT,
                text=True,
                capture_output=True,
                check=False,
            )

    def test_proposal_can_pass_scope_without_claiming_end_to_end(self) -> None:
        contract = valid_contract()
        result = self.run_validator("report", valid_report(contract), contract)
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)

    def test_one_low_dimension_cannot_be_hidden_by_a_high_score(self) -> None:
        contract = valid_contract()
        report = valid_report(contract)
        report["evaluator_runs"][0]["scores"]["DQ2"] = 2
        report["evaluator_runs"][1]["scores"]["DQ2"] = 4
        report["gates"][2]["score"] = 3
        result = self.run_validator("report", report, contract)
        self.assertNotEqual(result.returncode, 0)
        self.assertIn("DQ2", result.stdout)
        self.assertIn("minimum independent score", result.stdout)

    def test_author_only_rubric_cannot_pass(self) -> None:
        contract = valid_contract()
        report = valid_report(contract)
        report["evaluator_runs"] = [evaluator("author", "author"), evaluator("author-2", "author")]
        result = self.run_validator("report", report, contract)
        self.assertNotEqual(result.returncode, 0)
        self.assertIn("independent evaluators", result.stdout)

    def test_unknown_evaluator_gate_is_a_validation_error_not_a_crash(self) -> None:
        contract = valid_contract()
        report = valid_report(contract)
        report["evaluator_runs"][0]["scores"]["DQ9"] = 4
        result = self.run_validator("report", report, contract)
        self.assertNotEqual(result.returncode, 0)
        self.assertIn("unknown gates", result.stdout)
        self.assertNotIn("Traceback", result.stderr)

    def test_report_validates_contract_before_using_metric_operators(self) -> None:
        contract = valid_contract("live")
        report = valid_report(contract)
        contract["metric_targets"][0]["operator"] = "approximately"
        report["contract_digest"] = canonical_digest(contract)
        result = self.run_validator("report", report, contract)
        self.assertNotEqual(result.returncode, 0)
        self.assertIn("operator is invalid", result.stdout)
        self.assertNotIn("Traceback", result.stderr)

    def test_evaluator_divergence_requires_adjudication(self) -> None:
        contract = valid_contract()
        report = valid_report(contract)
        report["evaluator_runs"][0]["scores"]["DQ3"] = 2
        report["evaluator_runs"][1]["scores"]["DQ3"] = 4
        report["gates"][3]["score"] = 2
        report["gates"][3]["status"] = "inconclusive"
        report["scope_status"] = "inconclusive"
        result = self.run_validator("report", report, contract)
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)

    def test_contract_digest_prevents_post_hoc_threshold_changes(self) -> None:
        contract = valid_contract()
        report = valid_report(contract)
        contract["metric_targets"][0]["target"] = 0.5
        result = self.run_validator("report", report, contract)
        self.assertNotEqual(result.returncode, 0)
        self.assertIn("contract_digest", result.stdout)

    def test_non_live_scope_cannot_claim_end_to_end_passed(self) -> None:
        contract = valid_contract("implementation")
        report = valid_report(contract)
        report["end_to_end_status"] = "passed"
        result = self.run_validator("report", report, contract)
        self.assertNotEqual(result.returncode, 0)
        self.assertIn("end_to_end_status", result.stdout)

    def test_stage_required_gates_are_derived_from_artifact_scope(self) -> None:
        contract = valid_contract("implementation")
        report = valid_report(contract)
        report["gates"][7]["required"] = False
        report["gates"][7]["status"] = "not_run"
        result = self.run_validator("report", report, contract)
        self.assertNotEqual(result.returncode, 0)
        self.assertIn("DQ7.required", result.stdout)

    def test_open_critical_finding_blocks_scope_pass(self) -> None:
        contract = valid_contract()
        report = valid_report(contract)
        report["findings"] = [
            {
                "id": "f1",
                "gate_id": "DQ2",
                "severity": "critical",
                "status": "open",
                "summary": "The primary decision is based on stale hidden data.",
                "evidence": ["evidence/f1.md"],
            }
        ]
        result = self.run_validator("report", report, contract)
        self.assertNotEqual(result.returncode, 0)
        self.assertIn("critical findings", result.stdout)

    def test_medium_risk_requires_representative_or_production_evidence(self) -> None:
        contract = valid_contract("live", "medium")
        report = valid_report(contract)
        plan = contract["outcome_plan"]
        report["outcome_evidence"] = [
            {
                "id": "walkthrough",
                "run_id": "walkthrough-run",
                "observed_at": "2026-09-17T02:00:00Z",
                "artifact_revision": "artifact-r1",
                "kind": "independent-walkthrough",
                "status": "passed",
                "participant_count": 2,
                "evidence": ["evidence/walkthrough.md"],
                "plan_id": plan["id"],
                "scenario_ids": plan["scenario_ids"],
                "metric_ids": plan["metric_ids"],
                "participant_criteria": plan["participant_criteria"],
                "planned_participant_count": plan["planned_participant_count"],
                "protocol": plan["protocol"],
            }
        ]
        result = self.run_validator("report", report, contract)
        self.assertNotEqual(result.returncode, 0)
        self.assertIn("medium risk", result.stdout)

    def test_high_risk_requires_user_test_and_domain_safety_review(self) -> None:
        contract = valid_contract("live", "high")
        report = valid_report(contract)
        report["outcome_evidence"] = report["outcome_evidence"][:1]
        result = self.run_validator("report", report, contract)
        self.assertNotEqual(result.returncode, 0)
        self.assertIn("domain-safety-review", result.stdout)

    def test_risk_cannot_be_underclassified(self) -> None:
        contract = valid_contract()
        contract["risk_profile"]["factors"] = ["financial"]
        result = self.run_validator("contract", contract)
        self.assertNotEqual(result.returncode, 0)
        self.assertIn("risk_profile.level", result.stdout)

    def test_traceability_requires_must_know_information_mapping(self) -> None:
        contract = valid_contract()
        contract["representation_map"][0]["information_ids"] = ["case-age"]
        result = self.run_validator("contract", contract)
        self.assertNotEqual(result.returncode, 0)
        self.assertIn("case-risk", result.stdout)
        self.assertIn("representation", result.stdout)

    def test_each_scenario_information_is_covered_by_its_own_representations(self) -> None:
        contract = valid_contract()
        contract["representation_map"][0]["information_ids"] = ["case-age"]
        contract["task_scenarios"].append(
            {
                "id": "review-risk",
                "actor": "support operator",
                "starting_context": "one escalated case is open",
                "task": "review the case risk",
                "correct_outcome": "the operator identifies the severe case",
                "wrong_outcome": "the operator overlooks the severe case",
                "wrong_outcome_cost": "the severe case remains unresolved",
                "information_ids": ["case-risk"],
                "representation_ids": ["risk-badge"],
                "environment_ids": ["desktop-ko"],
                "observable_success": "the operator identifies the severe case from its risk label",
            }
        )
        contract["information_requirements"][0]["task_ids"].append("review-risk")
        contract["representation_map"].append(
            {
                "id": "risk-badge",
                "information_ids": ["case-risk"],
                "kind": "text-label",
                "semantic_role": "risk-level",
                "non_color_signals": ["risk label"],
                "rationale": "makes the risk explicit in the review-risk scenario",
                "task_ids": ["review-risk"],
            }
        )
        contract["outcome_plan"]["scenario_ids"].append("review-risk")
        result = self.run_validator("contract", contract)
        self.assertNotEqual(result.returncode, 0)
        self.assertIn("triage-case", result.stdout)
        self.assertIn("case-risk", result.stdout)
        self.assertIn("own representations", result.stdout)

    def test_legacy_operations_schema_is_rejected(self) -> None:
        contract = valid_contract()
        contract["schema_version"] = "operations-ui-screen-contract-v1"
        result = self.run_validator("contract", contract)
        self.assertNotEqual(result.returncode, 0)
        self.assertIn("design-decision-contract-v1", result.stdout)

    def test_live_low_risk_report_can_pass_with_two_independent_walkthroughs(self) -> None:
        contract = valid_contract("live", "low")
        report = valid_report(contract)
        result = self.run_validator("report", report, contract)
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)

    def test_metric_status_is_checked_against_pre_registered_target(self) -> None:
        contract = valid_contract("live", "low")
        report = valid_report(contract)
        report["metric_results"][0]["observed"] = 0.4
        result = self.run_validator("report", report, contract)
        self.assertNotEqual(result.returncode, 0)
        self.assertIn("task-success", result.stdout)

    def test_metric_observations_use_the_declared_kind_domain(self) -> None:
        contract = valid_contract("live", "low")
        report = valid_report(contract)
        report["metric_results"][0]["observed"] = 2
        result = self.run_validator("report", report, contract)
        self.assertNotEqual(result.returncode, 0)
        self.assertIn("rate observed", result.stdout)

    def test_operations_report_can_use_product_design_system_and_runtime_receipts(self) -> None:
        contract = valid_operations_contract()
        report = valid_report(contract)
        result = self.run_validator("report", report, contract)
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)

    def test_operations_dq7_pass_requires_scenario_environment_receipts(self) -> None:
        contract = valid_operations_contract()
        report = valid_report(contract)
        report["extensions"]["operations"]["browser_receipts"] = []
        result = self.run_validator("report", report, contract)
        self.assertNotEqual(result.returncode, 0)
        self.assertIn("scenario/environment coverage", result.stdout)

    def test_operations_receipts_reject_absolute_screenshot_paths(self) -> None:
        contract = valid_operations_contract()
        report = valid_report(contract)
        report["extensions"]["operations"]["browser_receipts"][0]["screenshots"] = [
            "/tmp/queue-triage.png"
        ]
        result = self.run_validator("report", report, contract)
        self.assertNotEqual(result.returncode, 0)
        self.assertIn("relative paths", result.stdout)

    def test_operations_receipts_reject_nul_paths_without_traceback(self) -> None:
        contract = valid_operations_contract()
        report = valid_report(contract)
        with tempfile.TemporaryDirectory() as tmp:
            base = Path(tmp)
            self.materialize_evidence(base, contract)
            self.materialize_evidence(base, report)
            report["extensions"]["operations"]["browser_receipts"][0]["screenshots"] = [
                "evidence/queue\x00triage.png"
            ]
            report_path = base / "report.json"
            contract_path = base / "contract.json"
            report_path.write_text(json.dumps(report), encoding="utf-8")
            contract_path.write_text(json.dumps(contract), encoding="utf-8")
            result = subprocess.run(
                [
                    "python3",
                    str(VALIDATOR),
                    "report",
                    str(report_path),
                    str(contract_path),
                ],
                cwd=ROOT,
                text=True,
                capture_output=True,
                check=False,
            )
        self.assertNotEqual(result.returncode, 0)
        self.assertIn("relative paths", result.stdout)
        self.assertNotIn("Traceback", result.stderr)

    def test_report_extension_cannot_cross_profiles(self) -> None:
        contract = valid_contract("implementation")
        report = valid_report(contract)
        operations_contract = valid_operations_contract()
        report["extensions"] = valid_report(operations_contract)["extensions"]
        result = self.run_validator("report", report, contract)
        self.assertNotEqual(result.returncode, 0)
        self.assertIn("only valid for operations-ui", result.stdout)

    def test_operations_design_system_mapping_rejects_literal_values_as_tokens(self) -> None:
        contract = valid_operations_contract()
        report = valid_report(contract)
        report["extensions"]["operations"]["design_system_mapping"]["mappings"][0][
            "token_id"
        ] = "#FFFFFF"
        result = self.run_validator("report", report, contract)
        self.assertNotEqual(result.returncode, 0)
        self.assertIn("token identifier", result.stdout)

    def test_operations_design_system_mapping_links_every_representation(self) -> None:
        contract = valid_operations_contract()
        report = valid_report(contract)
        for mapping in report["extensions"]["operations"]["design_system_mapping"]["mappings"]:
            mapping.pop("representation_ids", None)
        result = self.run_validator("report", report, contract)
        self.assertNotEqual(result.returncode, 0)
        self.assertIn("representation", result.stdout)

    def test_operations_design_system_mapping_rejects_css_value_sequences(self) -> None:
        for literal in ("255, 255, 255", "0 0 0 / 50%"):
            with self.subTest(literal=literal):
                contract = valid_operations_contract()
                report = valid_report(contract)
                report["extensions"]["operations"]["design_system_mapping"]["mappings"][0][
                    "token_id"
                ] = literal
                result = self.run_validator("report", report, contract)
                self.assertNotEqual(result.returncode, 0)
                self.assertIn("token identifier", result.stdout)

    def test_figma_contract_requires_native_evidence_extension(self) -> None:
        contract = valid_figma_contract()
        result = self.run_validator("contract", contract)
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
        del contract["extensions"]
        result = self.run_validator("contract", contract)
        self.assertNotEqual(result.returncode, 0)
        self.assertIn("extensions.figma", result.stdout)

    def test_figma_scenario_environment_must_belong_to_the_task_scenario(self) -> None:
        contract = valid_figma_contract()
        second_environment = copy.deepcopy(contract["environments"][0])
        second_environment.update({"id": "mobile-ko", "width": 390, "height": 844})
        contract["environments"].append(second_environment)
        contract["extensions"]["figma"]["resize_scenarios"][0][
            "environment_id"
        ] = "mobile-ko"
        result = self.run_validator("contract", contract)
        self.assertNotEqual(result.returncode, 0)
        self.assertIn("mobile-ko", result.stdout)
        self.assertIn("triage-case", result.stdout)

    def test_live_not_run_can_honestly_omit_uncollected_outcome_data(self) -> None:
        contract = valid_contract("live")
        report = valid_report(contract)
        gate = report["gates"][8]
        gate.update({"status": "not_run", "evidence": []})
        for check in gate["checks"]:
            check.update({"status": "not_run", "evidence": []})
        report["metric_results"] = []
        report["outcome_evidence"] = []
        report["scope_status"] = "not_run"
        report["end_to_end_status"] = "not_run"
        report["claim_level"] = "provisional"
        result = self.run_validator("report", report, contract)
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)

    def test_failed_subjective_gate_still_requires_two_independent_scores(self) -> None:
        contract = valid_contract()
        report = valid_report(contract)
        report["gates"][1]["status"] = "failed"
        report["scope_status"] = "failed"
        for run in report["evaluator_runs"]:
            del run["scores"]["DQ1"]
        result = self.run_validator("report", report, contract)
        self.assertNotEqual(result.returncode, 0)
        self.assertIn("failed requires 2 independent evaluators", result.stdout)

    def test_color_only_representation_is_rejected(self) -> None:
        contract = valid_contract()
        contract["representation_map"][0]["non_color_signals"] = []
        result = self.run_validator("contract", contract)
        self.assertNotEqual(result.returncode, 0)
        self.assertIn("non_color_signals", result.stdout)
        contract = valid_contract()
        contract["representation_map"][0]["non_color_signals"] = ["red"]
        result = self.run_validator("contract", contract)
        self.assertNotEqual(result.returncode, 0)
        self.assertIn("only color names", result.stdout)

    def test_task_information_edges_must_be_reciprocal(self) -> None:
        contract = valid_contract()
        contract["information_requirements"][0]["task_ids"] = ["different-task"]
        result = self.run_validator("contract", contract)
        self.assertNotEqual(result.returncode, 0)
        self.assertIn("reciprocal", result.stdout)

    def test_mandatory_checks_cannot_be_excluded(self) -> None:
        contract = valid_contract()
        contract["exclusions"] = [
            {
                "id": "skip-trace",
                "check_ids": ["traceability"],
                "reason": "Attempted bypass",
            }
        ]
        result = self.run_validator("contract", contract)
        self.assertNotEqual(result.returncode, 0)
        self.assertIn("cannot exclude mandatory checks", result.stdout)

    def test_evaluator_is_bound_to_artifact_revision(self) -> None:
        contract = valid_contract()
        report = valid_report(contract)
        report["evaluator_runs"][0]["artifact_revision"] = "another-revision"
        result = self.run_validator("report", report, contract)
        self.assertNotEqual(result.returncode, 0)
        self.assertIn("artifact_revision", result.stdout)

    def test_observations_cannot_predate_the_locked_contract(self) -> None:
        contract = valid_contract("live")
        report = valid_report(contract)
        report["metric_results"][0]["observed_at"] = "2026-09-16T23:59:59Z"
        report["outcome_evidence"][0]["observed_at"] = "2026-09-16T23:59:59Z"
        result = self.run_validator("report", report, contract)
        self.assertNotEqual(result.returncode, 0)
        self.assertIn("must not precede contract.locked_at", result.stdout)

    def test_nonexistent_evidence_path_cannot_support_a_passed_report(self) -> None:
        contract = valid_contract()
        report = valid_report(contract)
        with tempfile.TemporaryDirectory() as tmp:
            report_path = Path(tmp) / "report.json"
            contract_path = Path(tmp) / "contract.json"
            report_path.write_text(json.dumps(report), encoding="utf-8")
            contract_path.write_text(json.dumps(contract), encoding="utf-8")
            result = subprocess.run(
                ["python3", str(VALIDATOR), "report", str(report_path), str(contract_path)],
                cwd=ROOT,
                text=True,
                capture_output=True,
                check=False,
            )
        self.assertNotEqual(result.returncode, 0)
        self.assertIn("does not identify a file", result.stdout)

    def test_malformed_nested_values_fail_without_traceback(self) -> None:
        contract = valid_contract()
        contract["risk_profile"]["level"] = {"bad": True}
        result = self.run_validator("contract", contract)
        self.assertNotEqual(result.returncode, 0)
        self.assertIn("risk_profile.level", result.stdout)
        self.assertNotIn("Traceback", result.stderr)

    def test_very_large_numbers_fail_without_traceback(self) -> None:
        contract = valid_contract()
        contract["metric_targets"][0]["target"] = 10**1000
        result = self.run_validator("contract", contract)
        self.assertNotEqual(result.returncode, 0)
        self.assertIn("finite number", result.stdout)
        self.assertNotIn("Traceback", result.stderr)

    def test_malformed_operations_scenarios_fail_without_traceback(self) -> None:
        contract = valid_operations_contract()
        contract["task_scenarios"] = None
        result = self.run_validator("contract", contract)
        self.assertNotEqual(result.returncode, 0)
        self.assertIn("task_scenarios", result.stdout)
        self.assertNotIn("Traceback", result.stderr)

    def test_malformed_operations_report_scope_fails_without_traceback(self) -> None:
        contract = valid_operations_contract()
        report = valid_report(contract)
        report["artifact"]["scope"] = []
        result = self.run_validator("report", report, contract)
        self.assertNotEqual(result.returncode, 0)
        self.assertIn("artifact.scope", result.stdout)
        self.assertNotIn("Traceback", result.stderr)

    def test_figma_dq7_requires_typed_native_receipts(self) -> None:
        contract = valid_figma_contract()
        report = valid_report(contract)
        del report["extensions"]["figma"]
        result = self.run_validator("report", report, contract)
        self.assertNotEqual(result.returncode, 0)
        self.assertIn("extensions.figma", result.stdout)

    def test_figma_profile_requires_native_receipts_outside_figma_scope(self) -> None:
        contract = valid_figma_contract()
        contract["artifact_scope"] = "implementation"
        report = valid_report(contract)
        report.pop("extensions", None)
        result = self.run_validator("report", report, contract)
        self.assertNotEqual(result.returncode, 0)
        self.assertIn("extensions.figma", result.stdout)

    def test_redesign_current_behavior_evidence_must_exist(self) -> None:
        contract = valid_operations_contract()
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "screen-contract.json"
            path.write_text(json.dumps(contract), encoding="utf-8")
            result = subprocess.run(
                ["python3", str(VALIDATOR), "contract", str(path)],
                cwd=ROOT,
                text=True,
                capture_output=True,
                check=False,
            )
        self.assertNotEqual(result.returncode, 0)
        self.assertIn("current_behavior_inventory", result.stdout)
        self.assertIn("does not identify a file", result.stdout)

    def test_interface_implementation_dq7_requires_runtime_receipts(self) -> None:
        contract = valid_contract("implementation")
        report = valid_report(contract)
        del report["extensions"]["interface"]
        result = self.run_validator("report", report, contract)
        self.assertNotEqual(result.returncode, 0)
        self.assertIn("extensions.interface", result.stdout)

    def test_live_failed_dq8_can_retain_observed_evidence(self) -> None:
        contract = valid_contract("live")
        report = valid_report(contract)
        report["gates"][8]["status"] = "failed"
        report["metric_results"][0].update({"observed": 0.5, "status": "failed"})
        report["scope_status"] = "failed"
        report["end_to_end_status"] = "failed"
        report["claim_level"] = "provisional"
        result = self.run_validator("report", report, contract)
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)

    def test_metric_target_domains_are_kind_specific(self) -> None:
        contract = valid_contract()
        contract["metric_targets"][0]["target"] = -1
        result = self.run_validator("contract", contract)
        self.assertNotEqual(result.returncode, 0)
        self.assertIn("rate target", result.stdout)

        contract = valid_contract()
        contract["metric_targets"][1]["kind"] = "rubric"
        result = self.run_validator("contract", contract)
        self.assertNotEqual(result.returncode, 0)
        self.assertIn("critical-harm", result.stdout)

    def test_outcome_evidence_must_match_preregistered_plan(self) -> None:
        contract = valid_contract("live")
        report = valid_report(contract)
        report["outcome_evidence"][0]["protocol"] = "Changed after seeing the result."
        result = self.run_validator("report", report, contract)
        self.assertNotEqual(result.returncode, 0)
        self.assertIn("outcome_plan", result.stdout)

    def test_dq8_pass_requires_registered_scenario_and_metric_coverage(self) -> None:
        contract = valid_contract("live")
        report = valid_report(contract)
        for item in report["outcome_evidence"]:
            item["metric_ids"] = ["task-success"]
        result = self.run_validator("report", report, contract)
        self.assertNotEqual(result.returncode, 0)
        self.assertIn("metric coverage", result.stdout)

    def test_operations_domain_dimensions_are_covered_by_scenarios(self) -> None:
        contract = valid_operations_contract()
        contract["task_scenarios"][0]["coverage"].update(
            {
                "jobs": ["triage cases"],
                "entities": ["case"],
                "lifecycle": ["waiting", "selected"],
            }
        )
        result = self.run_validator("contract", contract)
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)

        contract["task_scenarios"][0]["coverage"]["jobs"] = []
        result = self.run_validator("contract", contract)
        self.assertNotEqual(result.returncode, 0)
        self.assertIn("do not cover jobs", result.stdout)

    def test_json_schemas_match_semantic_validator_shapes(self) -> None:
        contract_schema = json.loads(
            (ROOT / "shared" / "design-quality" / "design-decision-contract.schema.json").read_text()
        )
        report_schema = json.loads(
            (ROOT / "shared" / "design-quality" / "design-quality-report.schema.json").read_text()
        )
        eval_schema = json.loads((ROOT / "evals" / "operations-ui" / "cases.schema.json").read_text())

        self.assertFalse(contract_schema["$defs"]["taskScenario"]["additionalProperties"])
        self.assertNotIn("allOf", contract_schema["$defs"]["information"])
        self.assertIn("allOf", contract_schema["$defs"]["metricTarget"])
        self.assertNotIn(
            "remove",
            contract_schema["$defs"]["currentBehavior"]["properties"]["decision"]["enum"],
        )
        extension_properties = report_schema["properties"]["extensions"]["properties"]
        self.assertIn("interface", extension_properties)
        self.assertIn("figma", extension_properties)
        self.assertNotIn(
            "minItems",
            report_schema["$defs"]["interfaceExtension"]["properties"]["runtime_receipts"],
        )
        self.assertNotIn(
            "minItems",
            report_schema["$defs"]["figmaReportExtension"]["properties"]["native_receipts"],
        )
        self.assertEqual(report_schema["$defs"]["gate"]["properties"]["id"]["type"], "string")
        self.assertEqual(report_schema["$defs"]["finding"]["properties"]["gate_id"]["type"], "string")
        self.assertIn(
            "representation_ids",
            report_schema["$defs"]["operationsExtension"]["properties"]
            ["design_system_mapping"]["properties"]["mappings"]["items"]["required"],
        )
        self.assertIn("allOf", eval_schema["properties"]["cases"]["items"]["properties"]["expected"])

        operations_rule = next(
            rule
            for rule in contract_schema["allOf"]
            if rule.get("if", {}).get("properties", {}).get("profile", {}).get("const")
            == "operations-ui"
            and "mode" not in rule.get("if", {}).get("properties", {})
        )
        operations_task_items = operations_rule["then"]["properties"]["task_scenarios"][
            "items"
        ]
        self.assertTrue(
            {"requirement_ids", "actions", "coverage"}.issubset(
                operations_task_items["required"]
            )
        )
        self.assertIn("else", operations_rule)

        figma_rule = next(
            rule
            for rule in contract_schema["allOf"]
            if "anyOf" in rule.get("if", {})
        )
        self.assertIn("else", figma_rule)

        for extension_name in ("operations", "interface", "figma"):
            matching_rules = [
                rule
                for rule in report_schema["allOf"]
                if extension_name
                in rule.get("then", {})
                .get("properties", {})
                .get("extensions", {})
                .get("required", [])
            ]
            self.assertTrue(matching_rules, extension_name)
            self.assertTrue(all("else" in rule for rule in matching_rules), extension_name)

    def test_non_operations_profiles_reject_operations_scenario_fields(self) -> None:
        contract = valid_contract()
        contract["task_scenarios"][0].update(
            {
                "requirement_ids": [123],
                "actions": [{}],
                "coverage": [],
            }
        )
        result = self.run_validator("contract", contract)
        self.assertNotEqual(result.returncode, 0)
        self.assertIn("only valid for operations-ui", result.stdout)

    def test_figma_operations_report_does_not_require_browser_receipts(self) -> None:
        contract = valid_operations_contract("figma")
        report = valid_report(contract)
        report["extensions"]["operations"]["browser_receipts"] = []
        result = self.run_validator("report", report, contract)
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)

    def test_named_css_color_is_not_a_semantic_token(self) -> None:
        contract = valid_operations_contract()
        report = valid_report(contract)
        report["extensions"]["operations"]["design_system_mapping"]["mappings"][0][
            "token_id"
        ] = "red"
        result = self.run_validator("report", report, contract)
        self.assertNotEqual(result.returncode, 0)
        self.assertIn("token identifier", result.stdout)

    def test_operations_coverage_ignores_explicitly_inapplicable_states(self) -> None:
        contract = valid_operations_contract()
        contract["states"].append(
            {"id": "offline", "applicable": False, "reason": "The product has no offline mode."}
        )
        result = self.run_validator("contract", contract)
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)

    def test_operations_scenario_actions_must_be_declared(self) -> None:
        contract = valid_operations_contract()
        contract["task_scenarios"][0]["actions"] = ["undeclared-action"]
        result = self.run_validator("contract", contract)
        self.assertNotEqual(result.returncode, 0)
        self.assertIn("undeclared operations actions", result.stdout)

    def test_operations_actions_must_be_covered_by_the_scenario_that_executes_them(self) -> None:
        contract = valid_operations_contract()
        second = copy.deepcopy(contract["task_scenarios"][0])
        second.update(
            {
                "id": "approve-case-scenario",
                "actions": ["approve-case"],
                "requirement_ids": ["REQ-2"],
            }
        )
        second["coverage"]["actions"] = ["approve-case"]
        contract["task_scenarios"].append(second)
        contract["task_scenarios"][0]["actions"].append("approve-case")
        contract["outcome_plan"]["scenario_ids"].append("approve-case-scenario")
        for item in contract["information_requirements"]:
            item["task_ids"].append("approve-case-scenario")
        for item in contract["representation_map"]:
            item["task_ids"].append("approve-case-scenario")
        operations = contract["extensions"]["operations"]
        operations["actions"].append("approve-case")
        operations["requirements"].append(
            {
                "id": "REQ-2",
                "text": "The selected case can be approved.",
                "scenario_ids": ["approve-case-scenario"],
            }
        )
        operations["current_behavior_inventory"][0]["scenario_ids"].append(
            "approve-case-scenario"
        )
        operations["change_contract"].append(
            {
                "id": "CHANGE-2",
                "inventory_ids": ["INV-1"],
                "requirement_ids": ["REQ-2"],
                "description": "Preserve approval while clarifying the selected case state.",
            }
        )
        result = self.run_validator("contract", contract)
        self.assertNotEqual(result.returncode, 0)
        self.assertIn("executes actions it does not cover", result.stdout)

    def test_additional_malformed_hash_membership_inputs_fail_without_traceback(self) -> None:
        contract = valid_contract()
        contract["metric_targets"][0]["kind"] = []
        result = self.run_validator("contract", contract)
        self.assertNotEqual(result.returncode, 0)
        self.assertNotIn("Traceback", result.stderr)

        contract = valid_figma_contract()
        contract["extensions"]["figma"]["resize_scenarios"][0]["scenario_id"] = []
        result = self.run_validator("contract", contract)
        self.assertNotEqual(result.returncode, 0)
        self.assertNotIn("Traceback", result.stderr)

        contract = valid_contract("implementation")
        report = valid_report(contract)
        report["artifact"]["scope"] = []
        result = self.run_validator("report", report, contract)
        self.assertNotEqual(result.returncode, 0)
        self.assertNotIn("Traceback", result.stderr)

        contract = valid_contract()
        report = valid_report(contract)
        report["gates"][0]["checks"][0].update(
            {"id": [], "status": "not_applicable", "exclusion_id": "missing"}
        )
        result = self.run_validator("report", report, contract)
        self.assertNotEqual(result.returncode, 0)
        self.assertNotIn("Traceback", result.stderr)

    def test_behavior_fixture_has_actionable_expectations_and_prohibitions(self) -> None:
        fixture = json.loads((ROOT / "evals" / "design-quality" / "cases.json").read_text())
        self.assertEqual(fixture["schema_version"], "design-quality-behavior-v1")
        self.assertGreaterEqual(len(fixture["cases"]), 7)
        case_ids = [case["id"] for case in fixture["cases"]]
        self.assertEqual(len(case_ids), len(set(case_ids)))
        for case in fixture["cases"]:
            self.assertEqual(set(case), {"id", "scenario", "expected", "must_not"})
            self.assertTrue(case["scenario"].strip())
            self.assertTrue(case["expected"])
            self.assertTrue(case["must_not"])
            self.assertEqual(len(case["expected"]), len(set(case["expected"])))
            self.assertEqual(len(case["must_not"]), len(set(case["must_not"])))


if __name__ == "__main__":
    unittest.main()
