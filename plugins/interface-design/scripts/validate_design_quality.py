#!/usr/bin/env python3
"""Validate shared design decision contracts and dimension-floor quality reports."""

from __future__ import annotations

import argparse
import hashlib
import json
import math
import re
import subprocess
import sys
from datetime import datetime
from pathlib import Path
from typing import Any


CONTRACT_FIELDS = {
    "schema_version",
    "id",
    "profile",
    "artifact_scope",
    "mode",
    "revision",
    "locked_at",
    "actors",
    "contexts",
    "environments",
    "primary_question",
    "intended_outcome",
    "risk_profile",
    "task_scenarios",
    "information_requirements",
    "representation_map",
    "states",
    "metric_targets",
    "outcome_plan",
    "unresolved_decisions",
    "exclusions",
    "extensions",
}
REQUIRED_CONTRACT_FIELDS = CONTRACT_FIELDS - {"extensions"}
ENVIRONMENT_FIELDS = {
    "id",
    "platform",
    "width",
    "height",
    "input_methods",
    "locale",
    "writing_mode",
    "accessibility_profile",
}
TASK_FIELDS = {
    "id",
    "actor",
    "starting_context",
    "task",
    "correct_outcome",
    "wrong_outcome",
    "wrong_outcome_cost",
    "information_ids",
    "representation_ids",
    "environment_ids",
    "observable_success",
    "requirement_ids",
    "actions",
    "coverage",
}
REQUIRED_TASK_FIELDS = {
    "id",
    "actor",
    "starting_context",
    "task",
    "correct_outcome",
    "wrong_outcome",
    "wrong_outcome_cost",
    "information_ids",
    "representation_ids",
    "environment_ids",
    "observable_success",
}
INFORMATION_FIELDS = {
    "id",
    "role",
    "meaning",
    "source",
    "freshness",
    "uncertainty",
    "task_ids",
}
REPRESENTATION_FIELDS = {
    "id",
    "information_ids",
    "kind",
    "semantic_role",
    "non_color_signals",
    "rationale",
    "task_ids",
}
STATE_FIELDS = {"id", "applicable", "reason", "reachability_evidence"}
METRIC_TARGET_FIELDS = {"id", "kind", "role", "operator", "target", "unit", "rationale"}
UNRESOLVED_FIELDS = {"id", "severity", "reason", "evidence_needed", "gate_ids"}
EXCLUSION_FIELDS = {"id", "check_ids", "reason"}
REPORT_FIELDS = {
    "schema_version",
    "contract_id",
    "contract_revision",
    "contract_digest",
    "profile",
    "artifact",
    "scope_status",
    "end_to_end_status",
    "claim_level",
    "gates",
    "evaluator_runs",
    "metric_results",
    "outcome_evidence",
    "findings",
    "extensions",
}
REQUIRED_REPORT_FIELDS = REPORT_FIELDS - {"extensions"}
ARTIFACT_FIELDS = {"scope", "revision", "locators"}
GATE_FIELDS = {"id", "required", "status", "score", "evidence", "checks"}
CHECK_FIELDS = {"id", "status", "evidence", "exclusion_id"}
EVALUATOR_FIELDS = {
    "evaluator_id",
    "relationship",
    "evaluated_at",
    "artifact_revision",
    "contract_digest",
    "scores",
    "evidence",
}
METRIC_RESULT_FIELDS = {
    "metric_id",
    "run_id",
    "observed_at",
    "artifact_revision",
    "observed",
    "status",
    "evidence",
}
OUTCOME_FIELDS = {
    "id",
    "run_id",
    "observed_at",
    "artifact_revision",
    "kind",
    "status",
    "participant_count",
    "plan_id",
    "scenario_ids",
    "metric_ids",
    "participant_criteria",
    "planned_participant_count",
    "protocol",
    "evidence",
}
OUTCOME_PLAN_FIELDS = {
    "id",
    "scenario_ids",
    "metric_ids",
    "participant_criteria",
    "planned_participant_count",
    "protocol",
    "rationale",
}
FINDING_FIELDS = {"id", "gate_id", "severity", "status", "summary", "evidence"}
OPERATIONS_REPORT_EXTENSION_FIELDS = {"design_system_mapping", "browser_receipts"}
INTERFACE_REPORT_EXTENSION_FIELDS = {"runtime_receipts"}
FIGMA_REPORT_EXTENSION_FIELDS = {"native_receipts"}
DESIGN_SYSTEM_MAPPING_FIELDS = {"system_id", "token_source", "mappings"}
TOKEN_MAPPING_FIELDS = {"representation_ids", "semantic_role", "token_id", "evidence"}
BROWSER_RECEIPT_FIELDS = {
    "scenario_id",
    "environment_id",
    "command",
    "build_or_revision",
    "url",
    "status",
    "actions",
    "expected",
    "observed",
    "screenshots",
    "console_runtime_errors",
}
INTERFACE_RUNTIME_RECEIPT_FIELDS = {
    "scenario_id",
    "environment_id",
    "command",
    "build_or_revision",
    "url",
    "status",
    "steps",
    "expected",
    "observed",
    "screenshots",
    "console_runtime_errors",
}
FIGMA_NATIVE_RECEIPT_FIELDS = {
    "scenario_id",
    "environment_id",
    "artifact_revision",
    "status",
    "node_ids",
    "capabilities",
    "structure_observed",
    "resize_scenario_ids",
    "prototype_scenario_ids",
    "evidence",
}
FIGMA_SCENARIO_FIELDS = {"id", "scenario_id", "environment_id", "expectation"}
STATUSES = {
    "passed",
    "failed",
    "blocked",
    "inconclusive",
    "not_run",
    "not_applicable",
    "accepted_risk",
}
PASSING_CHECK_STATUSES = {"passed", "not_applicable"}
SCOPE_ORDER = {"proposal": 6, "figma": 7, "implementation": 7, "live": 8}
RISK_ORDER = {"low": 0, "medium": 1, "high": 2}
OPERATIONS_EXTENSION_FIELDS = {
    "surface",
    "jobs",
    "entities",
    "lifecycle",
    "actions",
    "permissions",
    "risks",
    "requirements",
    "current_behavior_inventory",
    "change_contract",
}
FIGMA_EXTENSION_FIELDS = {
    "target",
    "required_capabilities",
    "component_strategy",
    "resize_scenarios",
    "prototype_scenarios",
}


def _policy_path() -> Path:
    here = Path(__file__).resolve().parent
    local = here / "policy.json"
    if local.exists():
        return local
    return here.parent / "assets" / "design-quality" / "policy.json"


def load_policy() -> dict[str, Any]:
    return json.loads(_policy_path().read_text(encoding="utf-8"))


POLICY = load_policy()
GATE_IDS = [gate["id"] for gate in POLICY["gates"]]
GATE_CHECKS = {gate["id"]: gate["checks"] for gate in POLICY["gates"]}
SUBJECTIVE_GATES = {gate["id"] for gate in POLICY["gates"] if gate["rubric_required"]}
ALL_CHECK_IDS = {check for checks in GATE_CHECKS.values() for check in checks}
HIGH_RISK_FACTORS = set(POLICY["high_risk_factors"])
MEDIUM_RISK_FACTORS = set(POLICY["medium_risk_factors"])
EXCLUDABLE_CHECKS = set(POLICY.get("excludable_checks", []))
CSS_NAMED_COLORS = {
    "aliceblue", "aqua", "aquamarine", "azure", "beige", "black", "blue", "brown",
    "chocolate", "coral", "crimson", "cyan", "darkblue", "darkgray", "darkgreen",
    "darkgrey", "fuchsia", "gold", "gray", "green", "grey", "indigo", "ivory",
    "khaki", "lavender", "lime", "magenta", "maroon", "navy", "olive", "orange",
    "orchid", "pink", "plum", "purple", "red", "salmon", "silver", "snow", "tan",
    "teal", "tomato", "transparent", "turquoise", "violet", "wheat", "white", "yellow",
}
COLOR_ONLY_SIGNAL_NAMES = CSS_NAMED_COLORS | {
    "color", "colour", "hue", "fill", "background-color", "foreground-color",
    "색", "색상", "빨강", "노랑", "초록", "파랑",
}


def load_json(path: Path, errors: list[str]) -> Any:
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except OSError as error:
        errors.append(f"{path}: unable to read: {error}")
    except json.JSONDecodeError as error:
        errors.append(f"{path}: invalid JSON: {error}")
    return None


def canonical_digest(value: Any) -> str:
    encoded = json.dumps(
        value, ensure_ascii=False, sort_keys=True, separators=(",", ":")
    ).encode("utf-8")
    return "sha256:" + hashlib.sha256(encoded).hexdigest()


def non_empty_string(value: Any) -> bool:
    return isinstance(value, str) and bool(value.strip())


def choice(value: Any, allowed: set[str]) -> bool:
    return isinstance(value, str) and value in allowed


def safe_string_set(value: Any) -> set[str]:
    if not isinstance(value, list):
        return set()
    return {item for item in value if non_empty_string(item)}


def non_empty_string_list(value: Any) -> bool:
    return (
        isinstance(value, list)
        and bool(value)
        and all(non_empty_string(item) for item in value)
        and len(set(value)) == len(value)
    )


def string_list(value: Any) -> bool:
    return (
        isinstance(value, list)
        and all(non_empty_string(item) for item in value)
        and len(set(value)) == len(value)
    )


def number(value: Any) -> bool:
    if not isinstance(value, (int, float)) or isinstance(value, bool):
        return False
    try:
        return math.isfinite(value)
    except OverflowError:
        return False


def positive_integer(value: Any) -> bool:
    return isinstance(value, int) and not isinstance(value, bool) and value > 0


def parsed_timestamp(value: Any) -> datetime | None:
    if not non_empty_string(value):
        return None
    try:
        parsed = datetime.fromisoformat(value.replace("Z", "+00:00"))
    except ValueError:
        return None
    if parsed.tzinfo is None:
        return None
    return parsed


def timestamp(value: Any) -> bool:
    return parsed_timestamp(value) is not None


def relative_path(value: Any) -> bool:
    if not non_empty_string(value):
        return False
    if "\x00" in value:
        return False
    normalized = value.replace("\\", "/")
    return not (
        normalized.startswith("/")
        or re.match(r"^[A-Za-z]:/", normalized)
        or "://" in normalized
        or ".." in normalized.split("/")
    )


def token_identifier(value: Any) -> bool:
    if not non_empty_string(value):
        return False
    if value != value.strip():
        return False
    candidate = value
    if candidate.casefold() in CSS_NAMED_COLORS:
        return False
    if candidate.startswith("#"):
        return False
    if re.match(r"^(?:rgb|rgba|hsl|hsla|oklch|oklab|color)\(", candidate, re.IGNORECASE):
        return False
    if re.fullmatch(r"-?\d+(?:\.\d+)?(?:px|rem|em|%|vh|vw)?", candidate, re.IGNORECASE):
        return False
    return re.fullmatch(
        r"(?:--[A-Za-z_][A-Za-z0-9_.:/-]*|"
        r"[A-Za-z_][A-Za-z0-9_]*(?:[._:/-][A-Za-z0-9_]+)+)",
        candidate,
    ) is not None


def validate_evidence_paths(
    values: Any,
    context: str,
    report_directory: Path | None,
    errors: list[str],
) -> None:
    if not isinstance(values, list):
        return
    for index, value in enumerate(values):
        item_context = f"{context}[{index}]"
        if not relative_path(value):
            errors.append(f"{item_context} must be a relative path without traversal")
            continue
        if report_directory is None:
            continue
        try:
            base = report_directory.resolve()
            candidate = base / value
            resolved = candidate.resolve(strict=True)
            resolved.relative_to(base)
        except (OSError, RuntimeError, ValueError):
            errors.append(f"{item_context} does not identify a file inside the report directory: {value}")
            continue
        if not resolved.is_file():
            errors.append(f"{item_context} must identify a file: {value}")
            continue
        try:
            if resolved.stat().st_size == 0:
                errors.append(f"{item_context} must identify a non-empty evidence file: {value}")
        except OSError as error:
            errors.append(f"{item_context} cannot be read: {error}")


def reject_unknown_fields(value: dict[str, Any], allowed: set[str], context: str, errors: list[str]) -> None:
    unknown = sorted(set(value) - allowed)
    if unknown:
        errors.append(f"{context} has unknown fields: {unknown}")


def require_fields(value: dict[str, Any], required: set[str], context: str, errors: list[str]) -> None:
    missing = sorted(required - set(value))
    if missing:
        errors.append(f"{context} missing required fields: {missing}")


def unique_object_ids(value: Any, context: str, errors: list[str]) -> tuple[list[dict[str, Any]], set[str]]:
    if not isinstance(value, list) or not value:
        errors.append(f"{context} must be a non-empty array")
        return [], set()
    objects: list[dict[str, Any]] = []
    ids: set[str] = set()
    for index, item in enumerate(value):
        if not isinstance(item, dict):
            errors.append(f"{context}[{index}] must be an object")
            continue
        item_id = item.get("id")
        if not non_empty_string(item_id):
            errors.append(f"{context}[{index}].id must be a non-empty string")
        elif item_id in ids:
            errors.append(f"duplicate {context} id: {item_id}")
        else:
            ids.add(item_id)
        objects.append(item)
    return objects, ids


def validate_environment(item: dict[str, Any], index: int, errors: list[str]) -> None:
    context = f"environments[{index}]"
    reject_unknown_fields(item, ENVIRONMENT_FIELDS, context, errors)
    required = {"id", "platform", "input_methods", "locale", "writing_mode", "accessibility_profile"}
    require_fields(item, required, context, errors)
    if not choice(item.get("platform"), {"web", "ios", "android", "desktop", "other"}):
        errors.append(f"{context}.platform is invalid")
    for field in ("width", "height"):
        if field in item and not positive_integer(item[field]):
            errors.append(f"{context}.{field} must be a positive integer")
    if not non_empty_string_list(item.get("input_methods")):
        errors.append(f"{context}.input_methods must be a non-empty unique string array")
    for field in ("locale", "accessibility_profile"):
        if not non_empty_string(item.get(field)):
            errors.append(f"{context}.{field} must be a non-empty string")
    if not choice(item.get("writing_mode"), {"horizontal-tb", "vertical-rl", "vertical-lr"}):
        errors.append(f"{context}.writing_mode is invalid")


def required_risk_level(factors: set[str]) -> str:
    if factors & HIGH_RISK_FACTORS:
        return "high"
    if factors & MEDIUM_RISK_FACTORS:
        return "medium"
    return "low"


def validate_operations_extension(
    extension: Any,
    contract: dict[str, Any],
    scenario_ids: set[str],
    state_ids: set[str],
    contract_directory: Path | None,
    errors: list[str],
) -> None:
    if not isinstance(extension, dict):
        errors.append("extensions.operations must be an object for operations-ui")
        return
    reject_unknown_fields(extension, OPERATIONS_EXTENSION_FIELDS, "extensions.operations", errors)
    required = {
        "surface",
        "jobs",
        "entities",
        "lifecycle",
        "actions",
        "permissions",
        "risks",
        "requirements",
    }
    require_fields(extension, required, "extensions.operations", errors)
    if not choice(extension.get("surface"), {"standalone-console", "embedded-view"}):
        errors.append("extensions.operations.surface is invalid")
    for field in ("jobs", "entities", "lifecycle", "actions", "permissions", "risks"):
        if not non_empty_string_list(extension.get(field)):
            errors.append(f"extensions.operations.{field} must be a non-empty unique string array")

    requirements, requirement_ids = unique_object_ids(
        extension.get("requirements"), "extensions.operations.requirements", errors
    )
    requirement_to_scenarios: dict[str, set[str]] = {}
    for index, requirement in enumerate(requirements):
        context = f"extensions.operations.requirements[{index}]"
        reject_unknown_fields(requirement, {"id", "text", "scenario_ids"}, context, errors)
        require_fields(requirement, {"id", "text", "scenario_ids"}, context, errors)
        if not non_empty_string(requirement.get("text")):
            errors.append(f"{context}.text must be a non-empty string")
        linked = requirement.get("scenario_ids")
        if not non_empty_string_list(linked):
            errors.append(f"{context}.scenario_ids must be a non-empty unique string array")
            linked = []
        unknown = sorted(safe_string_set(linked) - scenario_ids)
        if unknown:
            errors.append(f"{context} references unknown scenario ids: {unknown}")
        if non_empty_string(requirement.get("id")):
            requirement_to_scenarios[requirement["id"]] = safe_string_set(linked)

    declared = {
        "jobs": safe_string_set(extension.get("jobs")),
        "entities": safe_string_set(extension.get("entities")),
        "lifecycle": safe_string_set(extension.get("lifecycle")),
        "actions": safe_string_set(extension.get("actions")),
        "permissions": safe_string_set(extension.get("permissions")),
        "risks": safe_string_set(extension.get("risks")),
        "states": state_ids,
    }
    covered = {key: set() for key in declared}
    raw_scenarios = contract.get("task_scenarios")
    if not isinstance(raw_scenarios, list):
        raw_scenarios = []
    scenario_map = {
        item.get("id"): item
        for item in raw_scenarios
        if isinstance(item, dict) and non_empty_string(item.get("id"))
    }
    for scenario_id, scenario in scenario_map.items():
        context = f"task_scenarios[{scenario_id}]"
        requirement_links = scenario.get("requirement_ids")
        if not non_empty_string_list(requirement_links):
            errors.append(f"{context}.requirement_ids is required for operations-ui")
            requirement_links = []
        unknown_requirements = sorted(set(requirement_links) - requirement_ids)
        if unknown_requirements:
            errors.append(f"{context} references unknown requirement ids: {unknown_requirements}")
        for requirement_id in requirement_links:
            if scenario_id not in requirement_to_scenarios.get(requirement_id, set()):
                errors.append(
                    f"requirement/scenario edges must be reciprocal: {requirement_id} -> {scenario_id}"
                )
        actions = scenario.get("actions")
        if not non_empty_string_list(actions):
            errors.append(f"{context}.actions must be a non-empty unique string array")
            actions = []
        coverage = scenario.get("coverage")
        if not isinstance(coverage, dict):
            errors.append(f"{context}.coverage must be an object")
            continue
        reject_unknown_fields(coverage, set(declared), f"{context}.coverage", errors)
        require_fields(coverage, set(declared), f"{context}.coverage", errors)
        for dimension, allowed in declared.items():
            values = coverage.get(dimension)
            if not string_list(values):
                errors.append(f"{context}.coverage.{dimension} must be a unique string array")
                continue
            unknown_values = sorted(safe_string_set(values) - allowed)
            if unknown_values:
                errors.append(f"{context}.coverage.{dimension} has unknown values: {unknown_values}")
            covered[dimension].update(safe_string_set(values))
        uncovered_actions = sorted(
            safe_string_set(coverage.get("actions")) - safe_string_set(actions)
        )
        if uncovered_actions:
            errors.append(f"{context} covers actions it does not exercise: {uncovered_actions}")
        uncovered_executed_actions = sorted(
            safe_string_set(actions) - safe_string_set(coverage.get("actions"))
        )
        if uncovered_executed_actions:
            errors.append(
                f"{context} executes actions it does not cover: {uncovered_executed_actions}"
            )
        unknown_actions = sorted(safe_string_set(actions) - declared["actions"])
        if unknown_actions:
            errors.append(f"{context}.actions has undeclared operations actions: {unknown_actions}")

    for requirement_id, linked_scenarios in requirement_to_scenarios.items():
        for scenario_id in linked_scenarios:
            scenario = scenario_map.get(scenario_id, {})
            if requirement_id not in safe_string_set(scenario.get("requirement_ids")):
                errors.append(
                    f"requirement/scenario edges must be reciprocal: {scenario_id} -> {requirement_id}"
                )
    for dimension, declared_values in declared.items():
        missing = sorted(declared_values - covered[dimension])
        if missing:
            errors.append(f"operations scenarios do not cover {dimension}: {missing}")

    inventory = extension.get("current_behavior_inventory")
    changes = extension.get("change_contract")
    if contract.get("mode") == "redesign":
        inventory_objects, inventory_ids = unique_object_ids(
            inventory, "extensions.operations.current_behavior_inventory", errors
        )
        change_objects, change_ids = unique_object_ids(
            changes, "extensions.operations.change_contract", errors
        )
        del change_ids
        inventory_scenarios: dict[str, set[str]] = {}
        for index, item in enumerate(inventory_objects):
            context = f"extensions.operations.current_behavior_inventory[{index}]"
            allowed = {
                "id", "kind", "observed", "evidence", "decision", "reason",
                "implementation_target", "scenario_ids",
            }
            reject_unknown_fields(item, allowed, context, errors)
            require_fields(item, allowed, context, errors)
            if not choice(item.get("kind"), {"feature", "state", "action", "permission", "data-shape"}):
                errors.append(f"{context}.kind is invalid")
            if not choice(item.get("decision"), {"preserve", "change"}):
                errors.append(f"{context}.decision is invalid")
            for field in ("observed", "reason", "implementation_target"):
                if not non_empty_string(item.get(field)):
                    errors.append(f"{context}.{field} must be a non-empty string")
            if not non_empty_string_list(item.get("evidence")):
                errors.append(f"{context}.evidence must be a non-empty unique string array")
            validate_evidence_paths(
                item.get("evidence"),
                f"{context}.evidence",
                contract_directory,
                errors,
            )
            linked = item.get("scenario_ids")
            if not non_empty_string_list(linked):
                errors.append(f"{context}.scenario_ids must be a non-empty unique string array")
                linked = []
            unknown = sorted(safe_string_set(linked) - scenario_ids)
            if unknown:
                errors.append(f"{context} references unknown scenario ids: {unknown}")
            if non_empty_string(item.get("id")):
                inventory_scenarios[item["id"]] = safe_string_set(linked)
        owners: dict[str, int] = {}
        for index, item in enumerate(change_objects):
            context = f"extensions.operations.change_contract[{index}]"
            allowed = {"id", "inventory_ids", "requirement_ids", "description"}
            reject_unknown_fields(item, allowed, context, errors)
            require_fields(item, allowed, context, errors)
            if not non_empty_string(item.get("description")):
                errors.append(f"{context}.description must be a non-empty string")
            linked_inventory = item.get("inventory_ids")
            linked_requirements = item.get("requirement_ids")
            if not non_empty_string_list(linked_inventory):
                errors.append(f"{context}.inventory_ids must be a non-empty unique string array")
                linked_inventory = []
            if not non_empty_string_list(linked_requirements):
                errors.append(f"{context}.requirement_ids must be a non-empty unique string array")
                linked_requirements = []
            unknown_inventory = sorted(safe_string_set(linked_inventory) - inventory_ids)
            unknown_requirements = sorted(safe_string_set(linked_requirements) - requirement_ids)
            if unknown_inventory:
                errors.append(f"{context} references unknown inventory ids: {unknown_inventory}")
            if unknown_requirements:
                errors.append(f"{context} references unknown requirement ids: {unknown_requirements}")
            members: list[set[str]] = []
            for inventory_id in linked_inventory:
                if inventory_id in owners:
                    errors.append(
                        f"inventory id {inventory_id} is mapped by multiple change contracts: "
                        f"{owners[inventory_id]} and {index}"
                    )
                owners[inventory_id] = index
                members.append(inventory_scenarios.get(inventory_id, set()))
            for requirement_id in linked_requirements:
                members.append(requirement_to_scenarios.get(requirement_id, set()))
            if members and not set.intersection(*members):
                errors.append(f"{context} must have one scenario shared by every member")
        missing_inventory = sorted(inventory_ids - set(owners))
        if missing_inventory:
            errors.append(f"redesign change_contract does not map inventory ids: {missing_inventory}")
    else:
        if (
            "current_behavior_inventory" in extension
            or "change_contract" in extension
        ):
            errors.append("current_behavior_inventory and change_contract are only valid for redesign mode")


def validate_figma_extension(
    extension: Any,
    scenario_ids: set[str],
    environment_ids: set[str],
    scenario_environments: dict[str, set[str]],
    errors: list[str],
) -> None:
    if not isinstance(extension, dict):
        errors.append("extensions.figma must be an object for figma-workflow")
        return
    reject_unknown_fields(extension, FIGMA_EXTENSION_FIELDS, "extensions.figma", errors)
    required = FIGMA_EXTENSION_FIELDS
    require_fields(extension, required, "extensions.figma", errors)
    if not non_empty_string(extension.get("target")):
        errors.append("extensions.figma.target must be a non-empty string")
    if not non_empty_string_list(extension.get("required_capabilities")):
        errors.append("extensions.figma.required_capabilities must be a non-empty unique string array")
    if not non_empty_string(extension.get("component_strategy")):
        errors.append("extensions.figma.component_strategy must be a non-empty string")
    for field in ("resize_scenarios", "prototype_scenarios"):
        items = extension.get(field)
        if not isinstance(items, list):
            errors.append(f"extensions.figma.{field} must be an array")
            continue
        if field == "resize_scenarios" and not items:
            errors.append("extensions.figma.resize_scenarios must not be empty")
        seen: set[str] = set()
        for index, item in enumerate(items):
            context = f"extensions.figma.{field}[{index}]"
            if not isinstance(item, dict):
                errors.append(f"{context} must be an object")
                continue
            reject_unknown_fields(item, FIGMA_SCENARIO_FIELDS, context, errors)
            require_fields(item, FIGMA_SCENARIO_FIELDS, context, errors)
            item_id = item.get("id")
            if not non_empty_string(item_id):
                errors.append(f"{context}.id must be a non-empty string")
            elif item_id in seen:
                errors.append(f"duplicate {field} id: {item_id}")
            else:
                seen.add(item_id)
            scenario_id = item.get("scenario_id")
            environment_id = item.get("environment_id")
            if not non_empty_string(scenario_id) or scenario_id not in scenario_ids:
                errors.append(f"{context}.scenario_id references an unknown task scenario")
            if not non_empty_string(environment_id) or environment_id not in environment_ids:
                errors.append(f"{context}.environment_id references an unknown environment")
            elif (
                non_empty_string(scenario_id)
                and scenario_id in scenario_ids
                and environment_id not in scenario_environments.get(scenario_id, set())
            ):
                errors.append(
                    f"{context}.environment_id {environment_id} does not belong to task scenario "
                    f"{scenario_id}"
                )
            if not non_empty_string(item.get("expectation")):
                errors.append(f"{context}.expectation must be a non-empty string")


def validate_contract(
    payload: Any,
    contract_directory: Path | None = None,
) -> list[str]:
    errors: list[str] = []
    if not isinstance(payload, dict):
        return ["design contract must be a JSON object"]
    reject_unknown_fields(payload, CONTRACT_FIELDS, "design contract", errors)
    require_fields(payload, REQUIRED_CONTRACT_FIELDS, "design contract", errors)
    if payload.get("schema_version") != POLICY["contract_schema_version"]:
        errors.append(f"schema_version must be {POLICY['contract_schema_version']}")
    if not non_empty_string(payload.get("id")):
        errors.append("id must be a non-empty string")
    profile = payload.get("profile")
    if not choice(profile, set(POLICY["profiles"])):
        errors.append(f"profile must be one of {POLICY['profiles']}")
    scope = payload.get("artifact_scope")
    if not choice(scope, set(SCOPE_ORDER)):
        errors.append(f"artifact_scope must be one of {sorted(SCOPE_ORDER)}")
    if not choice(payload.get("mode"), {"greenfield", "redesign", "audit"}):
        errors.append("mode must be greenfield, redesign, or audit")
    if not non_empty_string(payload.get("revision")):
        errors.append("revision must be a non-empty string")
    if not timestamp(payload.get("locked_at")):
        errors.append("locked_at must be an ISO-8601 date-time")
    for field in ("actors", "contexts"):
        if not non_empty_string_list(payload.get(field)):
            errors.append(f"{field} must be a non-empty unique string array")
    for field in ("primary_question", "intended_outcome"):
        if not non_empty_string(payload.get(field)):
            errors.append(f"{field} must be a non-empty string")

    environments, environment_ids = unique_object_ids(payload.get("environments"), "environments", errors)
    for index, item in enumerate(environments):
        validate_environment(item, index, errors)

    risk = payload.get("risk_profile")
    if not isinstance(risk, dict):
        errors.append("risk_profile must be an object")
    else:
        reject_unknown_fields(risk, {"level", "factors", "rationale"}, "risk_profile", errors)
        require_fields(risk, {"level", "factors", "rationale"}, "risk_profile", errors)
        level = risk.get("level")
        factors = risk.get("factors")
        if not choice(level, set(RISK_ORDER)):
            errors.append("risk_profile.level must be low, medium, or high")
        if not string_list(factors):
            errors.append("risk_profile.factors must be a unique string array")
            factors = []
        known_factors = HIGH_RISK_FACTORS | MEDIUM_RISK_FACTORS
        unknown = sorted(safe_string_set(factors) - known_factors)
        if unknown:
            errors.append(f"risk_profile.factors has unknown values: {unknown}")
        minimum = required_risk_level(safe_string_set(factors))
        if choice(level, set(RISK_ORDER)) and RISK_ORDER[level] < RISK_ORDER[minimum]:
            errors.append(f"risk_profile.level must be at least {minimum} for the declared factors")
        if not non_empty_string(risk.get("rationale")):
            errors.append("risk_profile.rationale must be a non-empty string")

    scenarios, scenario_ids = unique_object_ids(payload.get("task_scenarios"), "task_scenarios", errors)
    information, information_ids = unique_object_ids(
        payload.get("information_requirements"), "information_requirements", errors
    )
    representations, representation_ids = unique_object_ids(
        payload.get("representation_map"), "representation_map", errors
    )
    states, state_ids = unique_object_ids(payload.get("states"), "states", errors)
    metrics, metric_ids = unique_object_ids(payload.get("metric_targets"), "metric_targets", errors)

    actors = safe_string_set(payload.get("actors"))
    operations_task_fields = {"requirement_ids", "actions", "coverage"}
    for index, item in enumerate(scenarios):
        context = f"task_scenarios[{index}]"
        reject_unknown_fields(item, TASK_FIELDS, context, errors)
        require_fields(item, REQUIRED_TASK_FIELDS, context, errors)
        if profile == "operations-ui":
            require_fields(
                item,
                operations_task_fields,
                f"{context} for operations-ui",
                errors,
            )
        else:
            unexpected_operations_fields = sorted(operations_task_fields & set(item))
            if unexpected_operations_fields:
                errors.append(
                    f"{context} fields are only valid for operations-ui: "
                    f"{unexpected_operations_fields}"
                )
        for field in (
            "id", "actor", "starting_context", "task", "correct_outcome", "wrong_outcome",
            "wrong_outcome_cost", "observable_success",
        ):
            if not non_empty_string(item.get(field)):
                errors.append(f"{context}.{field} must be a non-empty string")
        if not non_empty_string(item.get("actor")) or item.get("actor") not in actors:
            errors.append(f"{context}.actor must reference actors")
        for field in ("information_ids", "representation_ids", "environment_ids"):
            if not non_empty_string_list(item.get(field)):
                errors.append(f"{context}.{field} must be a non-empty unique string array")
        scenario_information = safe_string_set(item.get("information_ids"))
        scenario_representations = safe_string_set(item.get("representation_ids"))
        scenario_environments = safe_string_set(item.get("environment_ids"))
        unknown_information = sorted(scenario_information - information_ids)
        unknown_representation = sorted(scenario_representations - representation_ids)
        unknown_environments = sorted(scenario_environments - environment_ids)
        if unknown_information:
            errors.append(f"{context} references unknown information ids: {unknown_information}")
        if unknown_representation:
            errors.append(f"{context} references unknown representation ids: {unknown_representation}")
        if unknown_environments:
            errors.append(f"{context} references unknown environment ids: {unknown_environments}")

    for index, item in enumerate(information):
        context = f"information_requirements[{index}]"
        reject_unknown_fields(item, INFORMATION_FIELDS, context, errors)
        require_fields(item, INFORMATION_FIELDS, context, errors)
        if not choice(item.get("role"), {"must_know", "supporting", "on_demand"}):
            errors.append(f"{context}.role is invalid")
        for field in ("id", "meaning", "source", "freshness", "uncertainty"):
            if not non_empty_string(item.get(field)):
                errors.append(f"{context}.{field} must be a non-empty string")
        if not non_empty_string_list(item.get("task_ids")):
            errors.append(f"{context}.task_ids must be a non-empty unique string array")
        unknown_tasks = sorted(safe_string_set(item.get("task_ids")) - scenario_ids)
        if unknown_tasks:
            errors.append(f"{context} references unknown task ids: {unknown_tasks}")
        information_id = item.get("id")
        if non_empty_string(information_id):
            for task_id in safe_string_set(item.get("task_ids")):
                scenario = next(
                    (candidate for candidate in scenarios if candidate.get("id") == task_id),
                    None,
                )
                if isinstance(scenario, dict) and information_id not in safe_string_set(
                    scenario.get("information_ids")
                ):
                    errors.append(
                        f"information/task edges must be reciprocal: {task_id} -> {information_id}"
                    )

    represented_information: set[str] = set()
    for index, item in enumerate(representations):
        context = f"representation_map[{index}]"
        reject_unknown_fields(item, REPRESENTATION_FIELDS, context, errors)
        require_fields(item, REPRESENTATION_FIELDS, context, errors)
        for field in ("id", "kind", "semantic_role", "rationale"):
            if not non_empty_string(item.get(field)):
                errors.append(f"{context}.{field} must be a non-empty string")
        for field in ("information_ids", "task_ids"):
            if not non_empty_string_list(item.get(field)):
                errors.append(f"{context}.{field} must be a non-empty unique string array")
        signals = item.get("non_color_signals")
        if not non_empty_string_list(signals):
            errors.append(
                f"{context}.non_color_signals must name at least one text, icon, shape, pattern, or position cue"
            )
        elif not any(signal.strip().casefold() not in COLOR_ONLY_SIGNAL_NAMES for signal in signals):
            errors.append(f"{context}.non_color_signals cannot contain only color names")
        linked_information = safe_string_set(item.get("information_ids"))
        represented_information.update(linked_information)
        unknown_information = sorted(linked_information - information_ids)
        linked_tasks = safe_string_set(item.get("task_ids"))
        unknown_tasks = sorted(linked_tasks - scenario_ids)
        if unknown_information:
            errors.append(f"{context} references unknown information ids: {unknown_information}")
        if unknown_tasks:
            errors.append(f"{context} references unknown task ids: {unknown_tasks}")
        representation_id = item.get("id")
        if non_empty_string(representation_id):
            for task_id in linked_tasks:
                scenario = next(
                    (candidate for candidate in scenarios if candidate.get("id") == task_id),
                    None,
                )
                if isinstance(scenario, dict) and representation_id not in safe_string_set(
                    scenario.get("representation_ids")
                ):
                    errors.append(
                        f"representation/task edges must be reciprocal: {task_id} -> {representation_id}"
                    )
    must_know = {
        item.get("id")
        for item in information
        if item.get("role") == "must_know" and non_empty_string(item.get("id"))
    }
    missing_representation = sorted(must_know - represented_information)
    if missing_representation:
        errors.append(f"must_know information lacks representation mapping: {missing_representation}")

    information_by_id = {
        item.get("id"): item
        for item in information
        if isinstance(item, dict) and non_empty_string(item.get("id"))
    }
    representation_by_id = {
        item.get("id"): item
        for item in representations
        if isinstance(item, dict) and non_empty_string(item.get("id"))
    }
    for scenario in scenarios:
        task_id = scenario.get("id")
        if not non_empty_string(task_id):
            continue
        for information_id in safe_string_set(scenario.get("information_ids")):
            linked = information_by_id.get(information_id)
            if isinstance(linked, dict) and task_id not in safe_string_set(linked.get("task_ids")):
                errors.append(
                    f"task/information edges must be reciprocal: {information_id} -> {task_id}"
                )
        for representation_id in safe_string_set(scenario.get("representation_ids")):
            linked = representation_by_id.get(representation_id)
            if isinstance(linked, dict) and task_id not in safe_string_set(linked.get("task_ids")):
                errors.append(
                    f"task/representation edges must be reciprocal: {representation_id} -> {task_id}"
                )
        represented_for_scenario: set[str] = set()
        for representation_id in safe_string_set(scenario.get("representation_ids")):
            linked = representation_by_id.get(representation_id)
            if isinstance(linked, dict):
                represented_for_scenario.update(safe_string_set(linked.get("information_ids")))
        missing_for_scenario = sorted(
            safe_string_set(scenario.get("information_ids")) - represented_for_scenario
        )
        if missing_for_scenario:
            errors.append(
                f"task scenario {task_id} information must be covered by its own representations: "
                f"{missing_for_scenario}"
            )

    applicable_states = 0
    for index, item in enumerate(states):
        context = f"states[{index}]"
        reject_unknown_fields(item, STATE_FIELDS, context, errors)
        require_fields(item, {"id", "applicable", "reason"}, context, errors)
        if not isinstance(item.get("applicable"), bool):
            errors.append(f"{context}.applicable must be boolean")
        elif item["applicable"]:
            applicable_states += 1
        if not non_empty_string(item.get("reason")):
            errors.append(f"{context}.reason must be a non-empty string")
        if "reachability_evidence" in item and not string_list(item["reachability_evidence"]):
            errors.append(f"{context}.reachability_evidence must be a unique string array")
    if states and applicable_states == 0:
        errors.append("states must declare at least one applicable state")

    for index, item in enumerate(metrics):
        context = f"metric_targets[{index}]"
        reject_unknown_fields(item, METRIC_TARGET_FIELDS, context, errors)
        require_fields(item, METRIC_TARGET_FIELDS, context, errors)
        if not choice(item.get("kind"), {"coverage", "count", "rate", "duration", "rubric"}):
            errors.append(f"{context}.kind is invalid")
        if not choice(item.get("role"), {"primary", "guardrail"}):
            errors.append(f"{context}.role is invalid")
        if not choice(item.get("operator"), {">=", ">", "<=", "<", "=="}):
            errors.append(f"{context}.operator is invalid")
        target = item.get("target")
        if not number(target):
            errors.append(f"{context}.target must be a finite number")
        else:
            kind = item.get("kind")
            if isinstance(kind, str) and not metric_value_in_domain(kind, target):
                if kind in {"coverage", "rate"}:
                    errors.append(f"{context}.{kind} target must be between 0 and 1")
                elif kind in {"count", "duration"}:
                    errors.append(f"{context}.{kind} target must be non-negative")
                elif kind == "rubric":
                    errors.append(f"{context}.rubric target must be between 0 and 4")
        for field in ("unit", "rationale"):
            if not non_empty_string(item.get(field)):
                errors.append(f"{context}.{field} must be a non-empty string")
    if metrics and not any(item.get("role") == "primary" for item in metrics):
        errors.append("metric_targets must contain a primary metric")
    critical_harm = next((item for item in metrics if item.get("id") == "critical-harm"), None)
    if critical_harm is None:
        errors.append("metric_targets must include critical-harm")
    elif (
        critical_harm.get("kind") != "count"
        or critical_harm.get("role") != "guardrail"
        or critical_harm.get("operator") != "=="
        or critical_harm.get("target") != 0
    ):
        errors.append("critical-harm must be a count guardrail with target == 0")

    outcome_plan = payload.get("outcome_plan")
    if not isinstance(outcome_plan, dict):
        errors.append("outcome_plan must be an object")
    else:
        reject_unknown_fields(outcome_plan, OUTCOME_PLAN_FIELDS, "outcome_plan", errors)
        require_fields(outcome_plan, OUTCOME_PLAN_FIELDS, "outcome_plan", errors)
        for field in ("id", "participant_criteria", "protocol", "rationale"):
            if not non_empty_string(outcome_plan.get(field)):
                errors.append(f"outcome_plan.{field} must be a non-empty string")
        planned_scenarios = outcome_plan.get("scenario_ids")
        planned_metrics = outcome_plan.get("metric_ids")
        if not non_empty_string_list(planned_scenarios):
            errors.append("outcome_plan.scenario_ids must be a non-empty unique string array")
        elif safe_string_set(planned_scenarios) != scenario_ids:
            errors.append("outcome_plan.scenario_ids must cover every task scenario")
        if not non_empty_string_list(planned_metrics):
            errors.append("outcome_plan.metric_ids must be a non-empty unique string array")
        elif safe_string_set(planned_metrics) != metric_ids:
            errors.append("outcome_plan.metric_ids must cover every metric target")
        if not positive_integer(outcome_plan.get("planned_participant_count")):
            errors.append("outcome_plan.planned_participant_count must be a positive integer")

    unresolved = payload.get("unresolved_decisions")
    if not isinstance(unresolved, list):
        errors.append("unresolved_decisions must be an array")
    else:
        seen: set[str] = set()
        for index, item in enumerate(unresolved):
            context = f"unresolved_decisions[{index}]"
            if not isinstance(item, dict):
                errors.append(f"{context} must be an object")
                continue
            reject_unknown_fields(item, UNRESOLVED_FIELDS, context, errors)
            require_fields(item, UNRESOLVED_FIELDS, context, errors)
            item_id = item.get("id")
            if not non_empty_string(item_id):
                errors.append(f"{context}.id must be a non-empty string")
            elif item_id in seen:
                errors.append(f"duplicate unresolved decision id: {item_id}")
            else:
                seen.add(item_id)
            if not choice(item.get("severity"), {"critical", "major", "minor"}):
                errors.append(f"{context}.severity is invalid")
            for field in ("reason", "evidence_needed"):
                if not non_empty_string(item.get(field)):
                    errors.append(f"{context}.{field} must be a non-empty string")
            if not non_empty_string_list(item.get("gate_ids")):
                errors.append(f"{context}.gate_ids must be a non-empty unique string array")
            unknown = sorted(safe_string_set(item.get("gate_ids")) - set(GATE_IDS))
            if unknown:
                errors.append(f"{context}.gate_ids has unknown values: {unknown}")

    exclusions = payload.get("exclusions")
    if not isinstance(exclusions, list):
        errors.append("exclusions must be an array")
    else:
        seen = set()
        for index, item in enumerate(exclusions):
            context = f"exclusions[{index}]"
            if not isinstance(item, dict):
                errors.append(f"{context} must be an object")
                continue
            reject_unknown_fields(item, EXCLUSION_FIELDS, context, errors)
            require_fields(item, EXCLUSION_FIELDS, context, errors)
            item_id = item.get("id")
            if not non_empty_string(item_id):
                errors.append(f"{context}.id must be a non-empty string")
            elif item_id in seen:
                errors.append(f"duplicate exclusion id: {item_id}")
            else:
                seen.add(item_id)
            if not non_empty_string_list(item.get("check_ids")):
                errors.append(f"{context}.check_ids must be a non-empty unique string array")
            check_ids = safe_string_set(item.get("check_ids"))
            unknown = sorted(check_ids - ALL_CHECK_IDS)
            if unknown:
                errors.append(f"{context}.check_ids has unknown values: {unknown}")
            forbidden = sorted(check_ids - EXCLUDABLE_CHECKS)
            if forbidden:
                errors.append(
                    f"{context}.check_ids cannot exclude mandatory checks: {forbidden}"
                )
            if not non_empty_string(item.get("reason")):
                errors.append(f"{context}.reason must be a non-empty string")

    extensions = payload.get("extensions", {})
    if not isinstance(extensions, dict):
        errors.append("extensions must be an object")
        extensions = {}
    reject_unknown_fields(extensions, {"operations", "figma"}, "extensions", errors)
    applicable_state_ids = {
        item.get("id")
        for item in states
        if isinstance(item, dict)
        and item.get("applicable") is True
        and non_empty_string(item.get("id"))
    }
    if profile == "operations-ui":
        validate_operations_extension(
            extensions.get("operations"),
            payload,
            scenario_ids,
            applicable_state_ids,
            contract_directory,
            errors,
        )
    elif "operations" in extensions:
        errors.append("extensions.operations is only valid for operations-ui")
    if scope == "figma" or profile == "figma-workflow":
        scenario_environments = {
            item.get("id"): safe_string_set(item.get("environment_ids"))
            for item in scenarios
            if non_empty_string(item.get("id"))
        }
        validate_figma_extension(
            extensions.get("figma"),
            scenario_ids,
            environment_ids,
            scenario_environments,
            errors,
        )
    elif "figma" in extensions:
        errors.append("extensions.figma is only valid for figma artifacts")

    del metric_ids
    return errors


def compare_metric(observed: float, operator: str, target: float) -> bool:
    return {
        ">=": observed >= target,
        ">": observed > target,
        "<=": observed <= target,
        "<": observed < target,
        "==": observed == target,
    }[operator]


def metric_value_in_domain(kind: Any, value: float) -> bool:
    if kind in {"coverage", "rate"}:
        return 0 <= value <= 1
    if kind in {"count", "duration"}:
        return value >= 0
    if kind == "rubric":
        return 0 <= value <= 4
    return False


def aggregate_status(required_statuses: list[str]) -> str:
    if required_statuses and all(status == "passed" for status in required_statuses):
        return "passed"
    for status in ("failed", "blocked", "inconclusive", "not_run", "accepted_risk"):
        if status in required_statuses:
            return status
    return "inconclusive"


def validate_operations_report_extension(
    extension: Any,
    contract: dict[str, Any],
    artifact: dict[str, Any],
    gate_statuses: dict[str, str],
    report_directory: Path | None,
    errors: list[str],
) -> None:
    if not isinstance(extension, dict):
        errors.append("extensions.operations must be an object for operations-ui reports")
        return
    reject_unknown_fields(
        extension,
        OPERATIONS_REPORT_EXTENSION_FIELDS,
        "extensions.operations",
        errors,
    )
    require_fields(
        extension,
        OPERATIONS_REPORT_EXTENSION_FIELDS,
        "extensions.operations",
        errors,
    )

    mapping = extension.get("design_system_mapping")
    if not isinstance(mapping, dict):
        errors.append("extensions.operations.design_system_mapping must be an object")
    else:
        context = "extensions.operations.design_system_mapping"
        reject_unknown_fields(mapping, DESIGN_SYSTEM_MAPPING_FIELDS, context, errors)
        require_fields(mapping, DESIGN_SYSTEM_MAPPING_FIELDS, context, errors)
        for field in ("system_id", "token_source"):
            if not non_empty_string(mapping.get(field)):
                errors.append(f"{context}.{field} must be a non-empty string")
        mappings = mapping.get("mappings")
        if not isinstance(mappings, list) or not mappings:
            errors.append(f"{context}.mappings must be a non-empty array")
            mappings = []
        semantic_roles: set[str] = set()
        representations = {
            item.get("id"): item
            for item in contract.get("representation_map", [])
            if isinstance(item, dict) and non_empty_string(item.get("id"))
        }
        covered_representations: set[str] = set()
        for index, item in enumerate(mappings):
            item_context = f"{context}.mappings[{index}]"
            if not isinstance(item, dict):
                errors.append(f"{item_context} must be an object")
                continue
            reject_unknown_fields(item, TOKEN_MAPPING_FIELDS, item_context, errors)
            require_fields(item, TOKEN_MAPPING_FIELDS, item_context, errors)
            role = item.get("semantic_role")
            if not non_empty_string(role):
                errors.append(f"{item_context}.semantic_role must be a non-empty string")
            elif role in semantic_roles:
                errors.append(f"duplicate design-system semantic role: {role}")
            else:
                semantic_roles.add(role)
            representation_ids = item.get("representation_ids")
            if not non_empty_string_list(representation_ids):
                errors.append(
                    f"{item_context}.representation_ids must be a non-empty unique string array"
                )
            unknown_representations = sorted(
                safe_string_set(representation_ids) - set(representations)
            )
            if unknown_representations:
                errors.append(
                    f"{item_context}.representation_ids references unknown representations: "
                    f"{unknown_representations}"
                )
            covered_representations.update(
                safe_string_set(representation_ids) & set(representations)
            )
            if not token_identifier(item.get("token_id")):
                errors.append(
                    f"{item_context}.token_id must be a semantic token identifier, not a literal value"
                )
            if not non_empty_string_list(item.get("evidence")):
                errors.append(f"{item_context}.evidence must be a non-empty unique string array")
            validate_evidence_paths(
                item.get("evidence"), f"{item_context}.evidence", report_directory, errors
            )
        missing_representations = sorted(
            set(representations) - covered_representations
        )
        if missing_representations:
            errors.append(
                "extensions.operations.design_system_mapping does not cover contract "
                f"representations: {missing_representations}"
            )

    receipts = extension.get("browser_receipts")
    if not isinstance(receipts, list):
        errors.append("extensions.operations.browser_receipts must be an array")
        receipts = []
    scenarios = {
        item.get("id"): item
        for item in contract.get("task_scenarios", [])
        if isinstance(item, dict) and non_empty_string(item.get("id"))
    }
    environments = {
        item.get("id")
        for item in contract.get("environments", [])
        if isinstance(item, dict) and non_empty_string(item.get("id"))
    }
    covered_pairs: set[tuple[str, str]] = set()
    seen_pairs: set[tuple[str, str]] = set()
    for index, item in enumerate(receipts):
        context = f"extensions.operations.browser_receipts[{index}]"
        if not isinstance(item, dict):
            errors.append(f"{context} must be an object")
            continue
        reject_unknown_fields(item, BROWSER_RECEIPT_FIELDS, context, errors)
        require_fields(item, BROWSER_RECEIPT_FIELDS, context, errors)
        scenario_id = item.get("scenario_id")
        environment_id = item.get("environment_id")
        valid_scenario = non_empty_string(scenario_id) and scenario_id in scenarios
        valid_environment = non_empty_string(environment_id) and environment_id in environments
        if not valid_scenario:
            errors.append(f"{context}.scenario_id references an unknown task scenario")
        if not valid_environment:
            errors.append(f"{context}.environment_id references an unknown environment")
        pair = (scenario_id, environment_id) if valid_scenario and valid_environment else None
        if pair is not None:
            if environment_id not in set(scenarios[scenario_id].get("environment_ids") or []):
                errors.append(
                    f"{context} scenario/environment pair is not bound to the task scenario"
                )
            if pair in seen_pairs:
                errors.append(f"duplicate browser receipt for scenario/environment: {pair}")
            else:
                seen_pairs.add(pair)
        for field in ("command", "build_or_revision", "url", "expected", "observed"):
            if not non_empty_string(item.get(field)):
                errors.append(f"{context}.{field} must be a non-empty string")
        if item.get("build_or_revision") != artifact.get("revision"):
            errors.append(f"{context}.build_or_revision must match artifact.revision")
        status = item.get("status")
        if not choice(status, STATUSES):
            errors.append(f"{context}.status is invalid")
        scenario = scenarios.get(scenario_id, {}) if valid_scenario else {}
        expected_actions = scenario.get("actions") or []
        if item.get("actions") != expected_actions:
            errors.append(f"{context}.actions must match the locked task scenario actions")
        if item.get("expected") != scenario.get("observable_success"):
            errors.append(f"{context}.expected must match the locked observable_success")
        screenshots = item.get("screenshots")
        if not non_empty_string_list(screenshots):
            errors.append(f"{context}.screenshots must be a non-empty unique string array")
        else:
            if not all(relative_path(path) for path in screenshots):
                errors.append(f"{context}.screenshots must use relative paths without traversal")
            validate_evidence_paths(
                screenshots,
                f"{context}.screenshots",
                report_directory,
                errors,
            )
        console_errors = item.get("console_runtime_errors")
        if not isinstance(console_errors, list) or not all(isinstance(value, str) for value in console_errors):
            errors.append(f"{context}.console_runtime_errors must be a string array")
            console_errors = []
        if status == "passed" and console_errors:
            errors.append(f"{context} cannot pass with console/runtime errors")
        if (
            status == "passed"
            and valid_scenario
            and valid_environment
            and environment_id in set(scenario.get("environment_ids") or [])
        ):
            covered_pairs.add((scenario_id, environment_id))

    artifact_scope = artifact.get("scope")
    if (
        isinstance(artifact_scope, str)
        and artifact_scope in {"implementation", "live"}
        and gate_statuses.get("DQ7") == "passed"
    ):
        required_pairs = {
            (scenario_id, environment_id)
            for scenario_id, scenario in scenarios.items()
            for environment_id in scenario.get("environment_ids", [])
        }
        missing_pairs = sorted(required_pairs - covered_pairs)
        if missing_pairs:
            errors.append(
                "DQ7 passed requires browser receipt scenario/environment coverage; "
                f"missing: {missing_pairs}"
            )


def contract_scenario_environment_pairs(
    contract: dict[str, Any],
) -> tuple[dict[str, dict[str, Any]], set[str], set[tuple[str, str]]]:
    raw_scenarios = contract.get("task_scenarios")
    raw_environments = contract.get("environments")
    scenarios = {
        item.get("id"): item
        for item in (raw_scenarios if isinstance(raw_scenarios, list) else []) if isinstance(item, dict)
        and non_empty_string(item.get("id"))
    }
    environments = {
        item.get("id")
        for item in (raw_environments if isinstance(raw_environments, list) else []) if isinstance(item, dict)
        and non_empty_string(item.get("id"))
    }
    pairs = {
        (scenario_id, environment_id)
        for scenario_id, scenario in scenarios.items()
        for environment_id in safe_string_set(scenario.get("environment_ids"))
        if environment_id in environments
    }
    return scenarios, environments, pairs


def validate_interface_report_extension(
    extension: Any,
    contract: dict[str, Any],
    artifact: dict[str, Any],
    gate_statuses: dict[str, str],
    report_directory: Path | None,
    errors: list[str],
) -> None:
    if not isinstance(extension, dict):
        errors.append("extensions.interface must be an object for interface-design implementation reports")
        return
    reject_unknown_fields(extension, INTERFACE_REPORT_EXTENSION_FIELDS, "extensions.interface", errors)
    require_fields(extension, INTERFACE_REPORT_EXTENSION_FIELDS, "extensions.interface", errors)
    receipts = extension.get("runtime_receipts")
    if not isinstance(receipts, list):
        errors.append("extensions.interface.runtime_receipts must be an array")
        receipts = []
    scenarios, environments, required_pairs = contract_scenario_environment_pairs(contract)
    covered_pairs: set[tuple[str, str]] = set()
    seen_pairs: set[tuple[str, str]] = set()
    for index, item in enumerate(receipts):
        context = f"extensions.interface.runtime_receipts[{index}]"
        if not isinstance(item, dict):
            errors.append(f"{context} must be an object")
            continue
        reject_unknown_fields(item, INTERFACE_RUNTIME_RECEIPT_FIELDS, context, errors)
        require_fields(item, INTERFACE_RUNTIME_RECEIPT_FIELDS, context, errors)
        scenario_id = item.get("scenario_id")
        environment_id = item.get("environment_id")
        pair = (scenario_id, environment_id)
        valid_pair = (
            non_empty_string(scenario_id)
            and non_empty_string(environment_id)
            and scenario_id in scenarios
            and environment_id in environments
            and pair in required_pairs
        )
        if not valid_pair:
            errors.append(f"{context} must reference a locked scenario/environment pair")
        elif pair in seen_pairs:
            errors.append(f"duplicate interface runtime receipt for scenario/environment: {pair}")
        else:
            seen_pairs.add(pair)
        for field in ("command", "url", "observed"):
            if not non_empty_string(item.get(field)):
                errors.append(f"{context}.{field} must be a non-empty string")
        if item.get("build_or_revision") != artifact.get("revision"):
            errors.append(f"{context}.build_or_revision must match artifact.revision")
        if not choice(item.get("status"), STATUSES):
            errors.append(f"{context}.status is invalid")
        if not non_empty_string_list(item.get("steps")):
            errors.append(f"{context}.steps must be a non-empty unique string array")
        expected = scenarios.get(scenario_id, {}).get("observable_success") if valid_pair else None
        if item.get("expected") != expected:
            errors.append(f"{context}.expected must match the locked observable_success")
        screenshots = item.get("screenshots")
        if not non_empty_string_list(screenshots):
            errors.append(f"{context}.screenshots must be a non-empty unique string array")
        validate_evidence_paths(screenshots, f"{context}.screenshots", report_directory, errors)
        console_errors = item.get("console_runtime_errors")
        if not isinstance(console_errors, list) or not all(isinstance(value, str) for value in console_errors):
            errors.append(f"{context}.console_runtime_errors must be a string array")
            console_errors = []
        if item.get("status") == "passed" and console_errors:
            errors.append(f"{context} cannot pass with console/runtime errors")
        if valid_pair and item.get("status") == "passed":
            covered_pairs.add(pair)
    if gate_statuses.get("DQ7") == "passed":
        missing = sorted(required_pairs - covered_pairs)
        if missing:
            errors.append(
                "DQ7 passed requires interface runtime receipt scenario/environment coverage; "
                f"missing: {missing}"
            )


def validate_figma_report_extension(
    extension: Any,
    contract: dict[str, Any],
    artifact: dict[str, Any],
    gate_statuses: dict[str, str],
    report_directory: Path | None,
    errors: list[str],
) -> None:
    if not isinstance(extension, dict):
        errors.append("extensions.figma must be an object for Figma DQ7 reports")
        return
    reject_unknown_fields(extension, FIGMA_REPORT_EXTENSION_FIELDS, "extensions.figma", errors)
    require_fields(extension, FIGMA_REPORT_EXTENSION_FIELDS, "extensions.figma", errors)
    receipts = extension.get("native_receipts")
    if not isinstance(receipts, list):
        errors.append("extensions.figma.native_receipts must be an array")
        receipts = []
    scenarios, environments, required_pairs = contract_scenario_environment_pairs(contract)
    figma_contract = contract.get("extensions", {}).get("figma", {})
    required_capabilities = safe_string_set(figma_contract.get("required_capabilities"))
    declared_resize = {
        item.get("id"): (item.get("scenario_id"), item.get("environment_id"))
        for item in (
            figma_contract.get("resize_scenarios")
            if isinstance(figma_contract.get("resize_scenarios"), list)
            else []
        )
        if isinstance(item, dict) and non_empty_string(item.get("id"))
    }
    declared_prototype = {
        item.get("id"): (item.get("scenario_id"), item.get("environment_id"))
        for item in (
            figma_contract.get("prototype_scenarios")
            if isinstance(figma_contract.get("prototype_scenarios"), list)
            else []
        )
        if isinstance(item, dict) and non_empty_string(item.get("id"))
    }
    covered_pairs: set[tuple[str, str]] = set()
    covered_resize: set[str] = set()
    covered_prototype: set[str] = set()
    seen_pairs: set[tuple[str, str]] = set()
    for index, item in enumerate(receipts):
        context = f"extensions.figma.native_receipts[{index}]"
        if not isinstance(item, dict):
            errors.append(f"{context} must be an object")
            continue
        reject_unknown_fields(item, FIGMA_NATIVE_RECEIPT_FIELDS, context, errors)
        require_fields(item, FIGMA_NATIVE_RECEIPT_FIELDS, context, errors)
        scenario_id = item.get("scenario_id")
        environment_id = item.get("environment_id")
        pair = (scenario_id, environment_id)
        valid_pair = (
            non_empty_string(scenario_id)
            and non_empty_string(environment_id)
            and scenario_id in scenarios
            and environment_id in environments
            and pair in required_pairs
        )
        if not valid_pair:
            errors.append(f"{context} must reference a locked scenario/environment pair")
        elif pair in seen_pairs:
            errors.append(f"duplicate Figma native receipt for scenario/environment: {pair}")
        else:
            seen_pairs.add(pair)
        if item.get("artifact_revision") != artifact.get("revision"):
            errors.append(f"{context}.artifact_revision must match artifact.revision")
        if not choice(item.get("status"), STATUSES):
            errors.append(f"{context}.status is invalid")
        if not non_empty_string_list(item.get("node_ids")):
            errors.append(f"{context}.node_ids must be a non-empty unique string array")
        capabilities = safe_string_set(item.get("capabilities"))
        if not non_empty_string_list(item.get("capabilities")):
            errors.append(f"{context}.capabilities must be a non-empty unique string array")
        missing_capabilities = sorted(required_capabilities - capabilities)
        if missing_capabilities:
            errors.append(f"{context}.capabilities are missing required values: {missing_capabilities}")
        if not non_empty_string(item.get("structure_observed")):
            errors.append(f"{context}.structure_observed must be a non-empty string")
        for field, declared, covered in (
            ("resize_scenario_ids", declared_resize, covered_resize),
            ("prototype_scenario_ids", declared_prototype, covered_prototype),
        ):
            values = item.get(field)
            if not string_list(values):
                errors.append(f"{context}.{field} must be a unique string array")
                continue
            for scenario_ref in safe_string_set(values):
                if declared.get(scenario_ref) != pair:
                    errors.append(f"{context}.{field} contains an unknown or mismatched scenario: {scenario_ref}")
                else:
                    covered.add(scenario_ref)
        evidence = item.get("evidence")
        if not non_empty_string_list(evidence):
            errors.append(f"{context}.evidence must be a non-empty unique string array")
        validate_evidence_paths(evidence, f"{context}.evidence", report_directory, errors)
        if valid_pair and item.get("status") == "passed":
            covered_pairs.add(pair)
    if gate_statuses.get("DQ7") == "passed":
        missing_pairs = sorted(required_pairs - covered_pairs)
        missing_resize = sorted(set(declared_resize) - covered_resize)
        missing_prototype = sorted(set(declared_prototype) - covered_prototype)
        if missing_pairs or missing_resize or missing_prototype:
            errors.append(
                "DQ7 passed requires Figma native scenario/environment, resize, and prototype coverage; "
                f"pairs={missing_pairs}, resize={missing_resize}, prototype={missing_prototype}"
            )


def validate_report(
    payload: Any,
    contract: Any,
    report_directory: Path | None = None,
    contract_directory: Path | None = None,
) -> list[str]:
    contract_errors = validate_contract(contract, contract_directory)
    if contract_errors:
        return [f"design contract: {error}" for error in contract_errors]
    errors: list[str] = []
    if not isinstance(payload, dict):
        return ["quality report must be a JSON object"]
    reject_unknown_fields(payload, REPORT_FIELDS, "quality report", errors)
    require_fields(payload, REQUIRED_REPORT_FIELDS, "quality report", errors)
    if payload.get("schema_version") != POLICY["report_schema_version"]:
        errors.append(f"schema_version must be {POLICY['report_schema_version']}")
    if payload.get("contract_id") != contract.get("id"):
        errors.append("contract_id must match design contract id")
    if payload.get("contract_revision") != contract.get("revision"):
        errors.append("contract_revision must match design contract revision")
    if payload.get("contract_digest") != canonical_digest(contract):
        errors.append("contract_digest must match the locked design contract")
    if payload.get("profile") != contract.get("profile"):
        errors.append("profile must match design contract profile")

    artifact = payload.get("artifact")
    if not isinstance(artifact, dict):
        errors.append("artifact must be an object")
        artifact = {}
    else:
        reject_unknown_fields(artifact, ARTIFACT_FIELDS, "artifact", errors)
        require_fields(artifact, ARTIFACT_FIELDS, "artifact", errors)
    scope = artifact.get("scope")
    if scope != contract.get("artifact_scope"):
        errors.append("artifact.scope must match design contract artifact_scope")
    if not non_empty_string(artifact.get("revision")):
        errors.append("artifact.revision must be a non-empty string")
    if not non_empty_string_list(artifact.get("locators")):
        errors.append("artifact.locators must be a non-empty unique string array")
    validate_evidence_paths(
        artifact.get("locators"), "artifact.locators", report_directory, errors
    )

    exclusions = {
        item.get("id"): set(item.get("check_ids") or [])
        for item in contract.get("exclusions", [])
        if isinstance(item, dict) and non_empty_string(item.get("id"))
    }
    evaluators = payload.get("evaluator_runs")
    if not isinstance(evaluators, list):
        errors.append("evaluator_runs must be an array")
        evaluators = []
    independent_scores: dict[str, list[int]] = {gate_id: [] for gate_id in SUBJECTIVE_GATES}
    evaluator_ids: set[str] = set()
    for index, item in enumerate(evaluators):
        context = f"evaluator_runs[{index}]"
        if not isinstance(item, dict):
            errors.append(f"{context} must be an object")
            continue
        reject_unknown_fields(item, EVALUATOR_FIELDS, context, errors)
        require_fields(item, EVALUATOR_FIELDS, context, errors)
        evaluator_id = item.get("evaluator_id")
        if not non_empty_string(evaluator_id):
            errors.append(f"{context}.evaluator_id must be a non-empty string")
        elif evaluator_id in evaluator_ids:
            errors.append(f"duplicate evaluator_id: {evaluator_id}")
        else:
            evaluator_ids.add(evaluator_id)
        relationship = item.get("relationship")
        if not choice(relationship, {"author", "independent"}):
            errors.append(f"{context}.relationship is invalid")
        evaluated_at = parsed_timestamp(item.get("evaluated_at"))
        if evaluated_at is None:
            errors.append(f"{context}.evaluated_at must be an ISO-8601 date-time")
        locked_at = parsed_timestamp(contract.get("locked_at"))
        if evaluated_at is not None and locked_at is not None and evaluated_at < locked_at:
            errors.append(f"{context}.evaluated_at must not precede contract.locked_at")
        if item.get("artifact_revision") != artifact.get("revision"):
            errors.append(f"{context}.artifact_revision must match artifact.revision")
        if item.get("contract_digest") != payload.get("contract_digest"):
            errors.append(f"{context}.contract_digest must match the quality report")
        if not non_empty_string_list(item.get("evidence")):
            errors.append(f"{context}.evidence must be a non-empty unique string array")
        validate_evidence_paths(
            item.get("evidence"), f"{context}.evidence", report_directory, errors
        )
        scores = item.get("scores")
        if not isinstance(scores, dict):
            errors.append(f"{context}.scores must be an object")
            continue
        unknown = sorted(set(scores) - SUBJECTIVE_GATES)
        if unknown:
            errors.append(f"{context}.scores has unknown gates: {unknown}")
        for gate_id, score in scores.items():
            if not isinstance(score, int) or isinstance(score, bool) or not 0 <= score <= 4:
                errors.append(f"{context}.scores.{gate_id} must be an integer from 0 to 4")
            elif relationship == "independent" and gate_id in independent_scores:
                independent_scores[gate_id].append(score)

    gates = payload.get("gates")
    if not isinstance(gates, list) or len(gates) != len(GATE_IDS):
        errors.append(f"gates must contain exact order {GATE_IDS}")
        gates = []
    actual_gate_ids = [gate.get("id") if isinstance(gate, dict) else None for gate in gates]
    if gates and actual_gate_ids != GATE_IDS:
        errors.append(f"gates must use exact order {GATE_IDS}")
    required_gate_ids = set(
        POLICY["artifact_scopes"].get(scope, []) if isinstance(scope, str) else []
    )
    gate_statuses: dict[str, str] = {}
    for index, gate in enumerate(gates):
        gate_id = GATE_IDS[index]
        context = gate_id
        if not isinstance(gate, dict):
            errors.append(f"gates[{index}] must be an object")
            continue
        reject_unknown_fields(gate, GATE_FIELDS, context, errors)
        require_fields(gate, GATE_FIELDS, context, errors)
        expected_required = gate_id in required_gate_ids
        if gate.get("required") is not expected_required:
            errors.append(f"{gate_id}.required must be {str(expected_required).lower()} for {scope}")
        status = gate.get("status")
        if not choice(status, STATUSES):
            errors.append(f"{gate_id}.status is invalid")
            status = "inconclusive"
        gate_statuses[gate_id] = status
        score = gate.get("score")
        if gate_id in SUBJECTIVE_GATES and expected_required and choice(
            status, {"passed", "failed", "inconclusive"}
        ):
            if not isinstance(score, int) or isinstance(score, bool) or not 0 <= score <= 4:
                errors.append(f"{gate_id}.score must be an integer from 0 to 4")
            scores = independent_scores[gate_id]
            if len(scores) < POLICY["independent_evaluators"]:
                errors.append(
                    f"{gate_id} {status} requires {POLICY['independent_evaluators']} independent evaluators"
                )
            else:
                minimum = min(scores)
                if score != minimum:
                    errors.append(f"{gate_id}.score must equal the minimum independent score {minimum}")
                if max(scores) - min(scores) > POLICY["maximum_score_divergence"]:
                    if status != "inconclusive":
                        errors.append(f"{gate_id} evaluator divergence requires inconclusive status")
                elif status == "passed" and minimum < POLICY["subjective_floor"]:
                    errors.append(
                        f"{gate_id} minimum independent score {minimum} is below floor {POLICY['subjective_floor']}"
                    )
        elif score is not None:
            errors.append(f"{gate_id}.score must be null when no required rubric is being decided")
        evidence = gate.get("evidence")
        if not string_list(evidence):
            errors.append(f"{gate_id}.evidence must be a unique string array")
        if status == "passed" and not evidence:
            errors.append(f"{gate_id} passed requires evidence")
        validate_evidence_paths(evidence, f"{gate_id}.evidence", report_directory, errors)
        checks = gate.get("checks")
        expected_checks = GATE_CHECKS[gate_id]
        if not isinstance(checks, list):
            errors.append(f"{gate_id}.checks must be an array")
            checks = []
        actual_checks = [check.get("id") if isinstance(check, dict) else None for check in checks]
        if actual_checks != expected_checks:
            errors.append(f"{gate_id}.checks must use exact order {expected_checks}")
        for check_index, check in enumerate(checks):
            check_context = f"{gate_id}.checks[{check_index}]"
            if not isinstance(check, dict):
                errors.append(f"{check_context} must be an object")
                continue
            reject_unknown_fields(check, CHECK_FIELDS, check_context, errors)
            require_fields(check, {"id", "status", "evidence"}, check_context, errors)
            check_status = check.get("status")
            if not choice(check_status, STATUSES):
                errors.append(f"{check_context}.status is invalid")
            check_evidence = check.get("evidence")
            if not string_list(check_evidence):
                errors.append(f"{check_context}.evidence must be a unique string array")
            if check_status == "passed" and not check_evidence:
                errors.append(f"{check_context} passed requires evidence")
            validate_evidence_paths(
                check_evidence, f"{check_context}.evidence", report_directory, errors
            )
            if check_status == "not_applicable":
                exclusion_id = check.get("exclusion_id")
                check_id = check.get("id")
                if (
                    not non_empty_string(exclusion_id)
                    or not non_empty_string(check_id)
                    or check_id not in exclusions.get(exclusion_id, set())
                ):
                    errors.append(f"{check_context} not_applicable requires a matching contract exclusion")
            elif "exclusion_id" in check:
                errors.append(f"{check_context}.exclusion_id is only valid for not_applicable")
        if expected_required and status == "passed":
            invalid_checks = [
                check.get("id")
                for check in checks
                if isinstance(check, dict)
                and not choice(check.get("status"), PASSING_CHECK_STATUSES)
            ]
            if invalid_checks:
                errors.append(f"{gate_id} passed while checks are not passing: {invalid_checks}")
            if not any(
                isinstance(check, dict) and check.get("status") == "passed"
                for check in checks
            ):
                errors.append(f"{gate_id} passed requires at least one executed passed check")
        if not expected_required and status not in {"not_run", "not_applicable"}:
            errors.append(f"{gate_id} is outside {scope} scope and must remain not_run or not_applicable")

    extensions = payload.get("extensions", {})
    if not isinstance(extensions, dict):
        errors.append("extensions must be an object")
        extensions = {}
    reject_unknown_fields(extensions, {"operations", "interface", "figma"}, "extensions", errors)
    if contract.get("profile") == "operations-ui":
        validate_operations_report_extension(
            extensions.get("operations"),
            contract,
            artifact,
            gate_statuses,
            report_directory,
            errors,
        )
    elif "operations" in extensions:
        errors.append("extensions.operations is only valid for operations-ui reports")
    if contract.get("profile") == "interface-design" and choice(
        scope, {"implementation", "live"}
    ):
        validate_interface_report_extension(
            extensions.get("interface"),
            contract,
            artifact,
            gate_statuses,
            report_directory,
            errors,
        )
    elif "interface" in extensions:
        errors.append(
            "extensions.interface is only valid for interface-design implementation or live reports"
        )
    if scope == "figma" or contract.get("profile") == "figma-workflow":
        validate_figma_report_extension(
            extensions.get("figma"),
            contract,
            artifact,
            gate_statuses,
            report_directory,
            errors,
        )
    elif "figma" in extensions:
        errors.append(
            "extensions.figma is only valid for Figma reports or figma-workflow profiles"
        )

    unresolved = contract.get("unresolved_decisions", [])
    for item in unresolved:
        if not isinstance(item, dict) or item.get("severity") != "critical":
            continue
        for gate_id in safe_string_set(item.get("gate_ids")) & required_gate_ids:
            if gate_statuses.get(gate_id) == "passed":
                errors.append(f"{gate_id} cannot pass with critical unresolved decision {item.get('id')}")

    findings = payload.get("findings")
    if not isinstance(findings, list):
        errors.append("findings must be an array")
        findings = []
    blocking_findings = []
    finding_ids: set[str] = set()
    for index, item in enumerate(findings):
        context = f"findings[{index}]"
        if not isinstance(item, dict):
            errors.append(f"{context} must be an object")
            continue
        reject_unknown_fields(item, FINDING_FIELDS, context, errors)
        require_fields(item, FINDING_FIELDS, context, errors)
        item_id = item.get("id")
        if not non_empty_string(item_id):
            errors.append(f"{context}.id must be a non-empty string")
        elif item_id in finding_ids:
            errors.append(f"duplicate finding id: {item_id}")
        else:
            finding_ids.add(item_id)
        if item.get("gate_id") not in GATE_IDS:
            errors.append(f"{context}.gate_id is invalid")
        if not choice(item.get("severity"), {"critical", "major", "minor"}):
            errors.append(f"{context}.severity is invalid")
        if not choice(item.get("status"), {"open", "resolved", "accepted_risk"}):
            errors.append(f"{context}.status is invalid")
        if not non_empty_string(item.get("summary")):
            errors.append(f"{context}.summary must be a non-empty string")
        if not non_empty_string_list(item.get("evidence")):
            errors.append(f"{context}.evidence must be a non-empty unique string array")
        validate_evidence_paths(
            item.get("evidence"), f"{context}.evidence", report_directory, errors
        )
        if (
            item.get("severity") in {"critical", "major"}
            and item.get("status") != "resolved"
        ):
            blocking_findings.append(item_id)

    targets = {
        item["id"]: item
        for item in contract.get("metric_targets", [])
        if isinstance(item, dict) and non_empty_string(item.get("id"))
    }
    metric_results = payload.get("metric_results")
    if not isinstance(metric_results, list):
        errors.append("metric_results must be an array")
        metric_results = []
    observed_metrics: set[str] = set()
    metric_run_ids: set[str] = set()
    metric_pass = True
    for index, item in enumerate(metric_results):
        context = f"metric_results[{index}]"
        if not isinstance(item, dict):
            errors.append(f"{context} must be an object")
            metric_pass = False
            continue
        reject_unknown_fields(item, METRIC_RESULT_FIELDS, context, errors)
        require_fields(item, METRIC_RESULT_FIELDS, context, errors)
        metric_id = item.get("metric_id")
        if not non_empty_string(metric_id):
            errors.append(f"{context}.metric_id must be a non-empty string")
            metric_pass = False
            continue
        if metric_id in observed_metrics:
            errors.append(f"duplicate metric result: {metric_id}")
        observed_metrics.add(metric_id)
        run_id = item.get("run_id")
        if not non_empty_string(run_id):
            errors.append(f"{context}.run_id must be a non-empty string")
        elif run_id in metric_run_ids:
            errors.append(f"duplicate metric run_id: {run_id}")
        else:
            metric_run_ids.add(run_id)
        observed_at = parsed_timestamp(item.get("observed_at"))
        if observed_at is None:
            errors.append(f"{context}.observed_at must be an ISO-8601 date-time")
        locked_at = parsed_timestamp(contract.get("locked_at"))
        if observed_at is not None and locked_at is not None and observed_at < locked_at:
            errors.append(f"{context}.observed_at must not precede contract.locked_at")
        if item.get("artifact_revision") != artifact.get("revision"):
            errors.append(f"{context}.artifact_revision must match artifact.revision")
        target = targets.get(metric_id)
        if target is None:
            errors.append(f"{context} references unknown metric target: {metric_id}")
            metric_pass = False
            continue
        observed = item.get("observed")
        if not number(observed):
            errors.append(f"{context}.observed must be a finite number")
            metric_pass = False
            continue
        metric_kind = target.get("kind")
        if not metric_value_in_domain(metric_kind, observed):
            if metric_kind in {"coverage", "rate"}:
                errors.append(f"{context}.{metric_kind} observed must be between 0 and 1")
            elif metric_kind in {"count", "duration"}:
                errors.append(f"{context}.{metric_kind} observed must be non-negative")
            elif metric_kind == "rubric":
                errors.append(f"{context}.rubric observed must be between 0 and 4")
            else:
                errors.append(f"{context}.observed has an unknown metric kind")
            metric_pass = False
            continue
        actual_pass = compare_metric(observed, target["operator"], target["target"])
        expected_status = "passed" if actual_pass else "failed"
        if item.get("status") != expected_status:
            errors.append(
                f"metric {metric_id} status must be {expected_status} for observed {observed} "
                f"{target['operator']} {target['target']}"
            )
        if not non_empty_string_list(item.get("evidence")):
            errors.append(f"{context}.evidence must be a non-empty unique string array")
        validate_evidence_paths(
            item.get("evidence"), f"{context}.evidence", report_directory, errors
        )
        metric_pass = metric_pass and actual_pass

    outcome = payload.get("outcome_evidence")
    if not isinstance(outcome, list):
        errors.append("outcome_evidence must be an array")
        outcome = []
    outcome_kinds: list[str] = []
    outcome_ids: set[str] = set()
    outcome_run_ids: set[str] = set()
    outcome_scenario_coverage: set[str] = set()
    outcome_metric_coverage: set[str] = set()
    passed_participants = 0
    outcome_plan = contract.get("outcome_plan", {})
    for index, item in enumerate(outcome):
        context = f"outcome_evidence[{index}]"
        if not isinstance(item, dict):
            errors.append(f"{context} must be an object")
            continue
        reject_unknown_fields(item, OUTCOME_FIELDS, context, errors)
        require_fields(item, OUTCOME_FIELDS, context, errors)
        item_id = item.get("id")
        if not non_empty_string(item_id):
            errors.append(f"{context}.id must be a non-empty string")
        elif item_id in outcome_ids:
            errors.append(f"duplicate outcome evidence id: {item_id}")
        else:
            outcome_ids.add(item_id)
        run_id = item.get("run_id")
        if not non_empty_string(run_id):
            errors.append(f"{context}.run_id must be a non-empty string")
        elif run_id in outcome_run_ids:
            errors.append(f"duplicate outcome run_id: {run_id}")
        else:
            outcome_run_ids.add(run_id)
        observed_at = parsed_timestamp(item.get("observed_at"))
        if observed_at is None:
            errors.append(f"{context}.observed_at must be an ISO-8601 date-time")
        locked_at = parsed_timestamp(contract.get("locked_at"))
        if observed_at is not None and locked_at is not None and observed_at < locked_at:
            errors.append(f"{context}.observed_at must not precede contract.locked_at")
        if item.get("artifact_revision") != artifact.get("revision"):
            errors.append(f"{context}.artifact_revision must match artifact.revision")
        kind = item.get("kind")
        if not choice(kind, {
            "independent-walkthrough",
            "representative-user-test",
            "production-behavior",
            "domain-safety-review",
        }):
            errors.append(f"{context}.kind is invalid")
        elif item.get("status") == "passed":
            outcome_kinds.append(kind)
        if not choice(item.get("status"), STATUSES):
            errors.append(f"{context}.status is invalid")
        if not positive_integer(item.get("participant_count")):
            errors.append(f"{context}.participant_count must be a positive integer")
        elif item.get("status") == "passed":
            passed_participants += item["participant_count"]
        if item.get("plan_id") != outcome_plan.get("id"):
            errors.append(f"{context}.plan_id must match outcome_plan.id")
        for field in ("participant_criteria", "protocol", "planned_participant_count"):
            if item.get(field) != outcome_plan.get(field):
                errors.append(f"{context}.{field} must match the locked outcome_plan")
        for field, coverage in (
            ("scenario_ids", outcome_scenario_coverage),
            ("metric_ids", outcome_metric_coverage),
        ):
            values = item.get(field)
            if not non_empty_string_list(values):
                errors.append(f"{context}.{field} must be a non-empty unique string array")
                continue
            allowed = safe_string_set(outcome_plan.get(field))
            unknown = sorted(safe_string_set(values) - allowed)
            if unknown:
                errors.append(f"{context}.{field} is outside outcome_plan: {unknown}")
            if item.get("status") == "passed":
                coverage.update(safe_string_set(values))
        if not non_empty_string_list(item.get("evidence")):
            errors.append(f"{context}.evidence must be a non-empty unique string array")
        validate_evidence_paths(
            item.get("evidence"), f"{context}.evidence", report_directory, errors
        )

    if scope == "live":
        if gate_statuses.get("DQ8") == "passed":
            missing_metrics = sorted(set(targets) - observed_metrics)
            if missing_metrics:
                errors.append(f"live report is missing metric results: {missing_metrics}")
                metric_pass = False
            missing_scenarios = sorted(
                safe_string_set(outcome_plan.get("scenario_ids")) - outcome_scenario_coverage
            )
            missing_outcome_metrics = sorted(
                safe_string_set(outcome_plan.get("metric_ids")) - outcome_metric_coverage
            )
            if missing_scenarios:
                errors.append(f"DQ8 outcome scenario coverage is missing: {missing_scenarios}")
            if missing_outcome_metrics:
                errors.append(f"DQ8 outcome metric coverage is missing: {missing_outcome_metrics}")
            planned_count = outcome_plan.get("planned_participant_count")
            if positive_integer(planned_count) and passed_participants < planned_count:
                errors.append(
                    "DQ8 passed participant count is below outcome_plan.planned_participant_count"
                )
            risk_level = contract["risk_profile"]["level"]
            strong_user_evidence = any(
                kind in {"representative-user-test", "production-behavior"} for kind in outcome_kinds
            )
            if risk_level == "low":
                evidence_pass = strong_user_evidence or outcome_kinds.count("independent-walkthrough") >= 2
                if not evidence_pass:
                    errors.append("low risk requires two independent walkthroughs or stronger user evidence")
            elif risk_level == "medium":
                evidence_pass = strong_user_evidence
                if not evidence_pass:
                    errors.append("medium risk requires representative-user-test or production-behavior evidence")
            else:
                evidence_pass = "representative-user-test" in outcome_kinds and "domain-safety-review" in outcome_kinds
                if not evidence_pass:
                    errors.append("high risk requires representative-user-test and domain-safety-review evidence")
            if not (
                metric_pass
                and evidence_pass
                and not missing_scenarios
                and not missing_outcome_metrics
                and (not positive_integer(planned_count) or passed_participants >= planned_count)
            ):
                errors.append("DQ8 cannot pass without passing metrics and risk-appropriate evidence")
    elif metric_results or outcome:
        errors.append("metric_results and outcome_evidence are only valid for live scope")

    required_statuses = [gate_statuses.get(gate_id, "inconclusive") for gate_id in GATE_IDS if gate_id in required_gate_ids]
    derived_scope = aggregate_status(required_statuses)
    if blocking_findings and payload.get("scope_status") == "passed":
        errors.append(
            f"scope_status cannot pass with unresolved blocking findings: {blocking_findings}"
        )
    if blocking_findings and derived_scope == "passed":
        derived_scope = "failed"
    if payload.get("scope_status") != derived_scope:
        errors.append(f"scope_status must be {derived_scope} for the required gate statuses")
    if scope == "live":
        expected_end_to_end = derived_scope
        if payload.get("end_to_end_status") != expected_end_to_end:
            errors.append(f"end_to_end_status must be {expected_end_to_end} for live scope")
    elif not choice(payload.get("end_to_end_status"), {"not_run", "inconclusive"}):
        errors.append("end_to_end_status cannot be passed before live scope")
    expected_claim = "validated" if scope == "live" and derived_scope == "passed" else "provisional"
    if payload.get("claim_level") != expected_claim:
        errors.append(f"claim_level must be {expected_claim}")
    if not choice(payload.get("scope_status"), STATUSES):
        errors.append("scope_status is invalid")
    if not choice(payload.get("end_to_end_status"), STATUSES):
        errors.append("end_to_end_status is invalid")
    return errors


DESIGN_MD_VERSION = "0.4.0"
DESIGN_MD_EXIT_CODES = {"passed": 0, "failed": 1, "blocked": 2, "needs_review": 3}


def check_design_md(path: Path) -> int:
    """Use the official parser/linter and emit a receipt for the exact input bytes."""
    receipt: dict[str, Any] = {
        "file": str(path.absolute()),
        "package": f"@google/design.md@{DESIGN_MD_VERSION}",
        "checked_at": datetime.now().astimezone().isoformat(),
    }

    def finish(status: str, rule: str, message: str) -> int:
        receipt.update(status=status, findings=[{
            "severity": "error", "rule": rule, "message": message,
        }])
        print(json.dumps(receipt, ensure_ascii=False))
        return DESIGN_MD_EXIT_CODES[status]

    try:
        content = path.read_bytes()
        text = content.decode("utf-8")
    except (OSError, UnicodeError, ValueError) as exc:
        return finish("failed", "input", str(exc))
    receipt["digest"] = "sha256:" + hashlib.sha256(content).hexdigest()
    command = [
        "npx", "--yes", f"--package=@google/design.md@{DESIGN_MD_VERSION}",
        "--", "node", str(Path(__file__).resolve().with_name("design_md.mjs")),
        DESIGN_MD_VERSION,
    ]
    receipt["command"] = command
    try:
        # Preserve the caller's npm project config. The adapter verifies the
        # loaded package version; stdin carries the exact input snapshot.
        run = subprocess.run(command, input=text, text=True, encoding="utf-8",
                             capture_output=True, timeout=120)
    except (OSError, subprocess.TimeoutExpired, UnicodeError) as exc:
        return finish("blocked", "runtime", str(exc))
    receipt["engine_exit_code"] = run.returncode
    try:
        result = json.loads(run.stdout)
        status = result["status"]
        if (not isinstance(result, dict) or status not in DESIGN_MD_EXIT_CODES
                or run.returncode != DESIGN_MD_EXIT_CODES[status]
                or not isinstance(result.get("findings"), list)):
            raise ValueError("invalid adapter result")
    except (ValueError, TypeError, KeyError):
        return finish("blocked", "runtime", "Invalid or missing linter JSON: " + run.stderr[-2000:])
    receipt.update(result)
    print(json.dumps(receipt, ensure_ascii=False))
    return DESIGN_MD_EXIT_CODES[status]


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    subparsers = parser.add_subparsers(dest="command", required=True)
    design_md = subparsers.add_parser("design-md", help="lint DESIGN.md with the pinned official engine")
    design_md.add_argument("file", type=Path)
    contract = subparsers.add_parser("contract")
    contract.add_argument("contract", type=Path)
    report = subparsers.add_parser("report")
    report.add_argument("report", type=Path)
    report.add_argument("contract", type=Path)
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    if args.command == "design-md":
        raise SystemExit(check_design_md(args.file))
    load_errors: list[str] = []
    if args.command == "contract":
        payload = load_json(args.contract, load_errors)
        errors = load_errors or validate_contract(
            payload, args.contract.resolve().parent
        )
    else:
        report = load_json(args.report, load_errors)
        contract = load_json(args.contract, load_errors)
        errors = list(load_errors)
        if not errors:
            errors.extend(
                validate_contract(contract, args.contract.resolve().parent)
            )
        if not errors:
            errors.extend(
                validate_report(
                    report,
                    contract,
                    args.report.resolve().parent,
                    args.contract.resolve().parent,
                )
            )
    if errors:
        for error in errors:
            print(f"ERROR: {error}")
        raise SystemExit(1)
    print(f"OK: {args.command}")


if __name__ == "__main__":
    main()
