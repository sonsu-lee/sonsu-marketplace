#!/usr/bin/env python3
"""Validate Operations UI screen contracts, quality reports, and eval fixtures."""

from __future__ import annotations

import argparse
import json
import re
import sys
import zlib
from pathlib import Path
from typing import Any


SCREEN_SCHEMA_VERSION = "operations-ui-screen-contract-v1"
REPORT_SCHEMA_VERSION = "operations-ui-quality-report-v1"
EVAL_SCHEMA_VERSION = "operations-ui-evals-v1"
GATE_IDS = [f"G{index}" for index in range(8)]
GATE_CHECK_IDS = {
    "G0": ["contract-artifact", "requirement-scenario-coverage"],
    "G1": ["pattern-decision", "information-hierarchy", "actual-wide-render"],
    "G2": [
        "token-mapping",
        "shell-and-navigation",
        "semantic-color",
        "density-and-components",
    ],
    "G3": [
        "state-matrix",
        "loading-empty-error-permission",
        "zero-one-many",
        "long-localized-overflow",
    ],
    "G4": [
        "primary-secondary-actions",
        "bulk-destructive-actions",
        "feedback-and-selection",
    ],
    "G5": ["wide-viewport", "narrow-or-excluded", "overflow-and-detail-access"],
    "G6": ["keyboard-focus", "names-roles-states", "non-color-status", "contrast"],
    "G7": [
        "actual-app-provenance",
        "required-scenario-coverage",
        "screenshots",
        "console-runtime",
    ],
}
GATE_STATUSES = (
    "passed",
    "failed",
    "blocked",
    "inconclusive",
    "not_run",
)
CHECK_STATUSES = GATE_STATUSES + ("not_applicable",)
SCREEN_MODES = ("greenfield", "redesign", "audit")
SCREEN_SURFACES = ("standalone-console", "embedded-view")
INVENTORY_KINDS = ("feature", "state", "action", "permission", "data-shape")
INVENTORY_DECISIONS = ("preserve", "change")
EXCLUSION_CHECKS = {
    "embedded-shell": {"shell-and-navigation"},
    "desktop-only": {"narrow-or-excluded"},
    "capability-absent": {"bulk-destructive-actions"},
}
REQUIRED_SCREEN_FIELDS = {
    "id",
    "mode",
    "surface",
    "actors",
    "jobs",
    "entities",
    "lifecycle",
    "primary_decision",
    "actions",
    "permissions",
    "risks",
    "view_states",
    "viewports",
    "requirements",
    "evidence_scenarios",
    "exclusions",
    "unresolved_decisions",
}
SCREEN_FIELDS = REQUIRED_SCREEN_FIELDS | {
    "schema_version",
    "current_behavior_inventory",
    "change_contract",
}
VIEWPORT_FIELDS = {"id", "width", "height"}
REQUIREMENT_FIELDS = {"id", "text", "scenario_ids"}
SCENARIO_FIELDS = {
    "id",
    "requirement_ids",
    "initial_state",
    "actions",
    "expected",
    "required_viewports",
    "coverage",
}
SCENARIO_COVERAGE_FIELDS = {"actions", "permissions", "risks", "view_states"}
EXCLUSION_FIELDS = {
    "id",
    "kind",
    "check_ids",
    "reason",
    "minimum_viewport",
    "operational_reason",
}
UNRESOLVED_DECISION_FIELDS = {
    "id",
    "area",
    "reason",
    "evidence_needed",
    "gate_ids",
}
INVENTORY_FIELDS = {
    "id",
    "kind",
    "observed",
    "evidence",
    "decision",
    "reason",
    "implementation_target",
    "scenario_ids",
}
CHANGE_CONTRACT_FIELDS = {"id", "inventory_ids", "requirement_ids", "description"}
REPORT_FIELDS = {
    "schema_version",
    "screen_contract_id",
    "overall",
    "design_profile",
    "gates",
    "browser_receipts",
}
GATE_FIELDS = {"id", "required", "status", "evidence", "checks"}
CHECK_FIELDS = {
    "id",
    "status",
    "evidence",
    "exclusion_id",
    "not_applicable_reason",
}
EVAL_FIELDS = {"schema_version", "cases"}
EVAL_CASE_FIELDS = {"id", "prompt", "expected"}
EVAL_EXPECTED_FIELDS = {
    "select",
    "must_not_select",
    "must_build_screen_contract",
    "must_require_browser_gate",
    "must_inventory_current_behavior",
    "must_require_mapping_coverage",
    "mode",
    "must_not_mutate",
    "reason",
    "must_map_scenarios",
    "figma_does_not_replace_browser_gate",
    "when_official_capability_missing",
    "must_not_claim_canvas_mutation",
    "must_not_claim",
    "gate_G7",
    "must_use_domain_neutral_contract",
    "must_decide",
    "must_not_add_false_click_affordance",
    "required_checks",
}
EVAL_BOOLEAN_FIELDS = {
    "must_build_screen_contract",
    "must_require_browser_gate",
    "must_inventory_current_behavior",
    "must_not_mutate",
    "must_map_scenarios",
    "figma_does_not_replace_browser_gate",
    "must_not_claim_canvas_mutation",
    "must_use_domain_neutral_contract",
    "must_not_add_false_click_affordance",
}
EVAL_STRING_FIELDS = {"reason", "must_not_claim", "must_decide"}
KNOWN_SKILL_IDS = {
    "operations-ui:design-operations-ui",
    "operations-ui:redesign-operations-ui",
    "operations-ui:audit-operations-ui",
    "operations-ui:figma-operations-flow",
}
REQUIRED_BROWSER_FIELDS = {
    "scenario_id",
    "command",
    "build_or_revision",
    "url",
    "viewport_id",
    "status",
    "actions",
    "expected",
    "observed",
    "screenshots",
    "console_runtime_errors",
}
DESIGN_PROFILE = {
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
}


def load_json(path: Path, errors: list[str]) -> Any:
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except OSError as error:
        errors.append(f"{path}: unable to read: {error}")
    except json.JSONDecodeError as error:
        errors.append(f"{path}: invalid JSON: {error}")
    return None


def non_empty_string(value: Any) -> bool:
    return isinstance(value, str) and bool(value.strip())


def non_empty_string_list(value: Any) -> bool:
    return (
        isinstance(value, list)
        and bool(value)
        and all(non_empty_string(item) for item in value)
    )


def string_items(value: Any) -> list[str]:
    if not isinstance(value, list):
        return []
    return [item for item in value if isinstance(item, str)]


def string_list(value: Any) -> bool:
    return isinstance(value, list) and all(non_empty_string(item) for item in value)


def reject_unknown_fields(
    value: dict[str, Any], allowed: set[str], context: str, errors: list[str]
) -> None:
    unknown = sorted(set(value) - allowed)
    if unknown:
        errors.append(f"{context} has unknown fields: {unknown}")


def is_valid_png(data: bytes) -> bool:
    if not data.startswith(b"\x89PNG\r\n\x1a\n"):
        return False
    offset = 8
    saw_header = False
    saw_image_data = False
    while offset < len(data):
        if len(data) - offset < 12:
            return False
        length = int.from_bytes(data[offset : offset + 4], "big")
        chunk_type = data[offset + 4 : offset + 8]
        chunk_end = offset + 12 + length
        if chunk_end > len(data):
            return False
        chunk_data = data[offset + 8 : offset + 8 + length]
        expected_crc = int.from_bytes(data[offset + 8 + length : chunk_end], "big")
        if zlib.crc32(chunk_type + chunk_data) & 0xFFFFFFFF != expected_crc:
            return False
        if not saw_header:
            if chunk_type != b"IHDR" or length != 13:
                return False
            width = int.from_bytes(chunk_data[0:4], "big")
            height = int.from_bytes(chunk_data[4:8], "big")
            if width == 0 or height == 0:
                return False
            saw_header = True
        elif chunk_type == b"IHDR":
            return False
        if chunk_type == b"IDAT" and length > 0:
            saw_image_data = True
        if chunk_type == b"IEND":
            return length == 0 and saw_header and saw_image_data and chunk_end == len(data)
        offset = chunk_end
    return False


def is_valid_jpeg(data: bytes) -> bool:
    if len(data) < 4 or not data.startswith(b"\xff\xd8"):
        return False
    offset = 2
    saw_frame = False
    saw_scan = False
    frame_markers = {
        0xC0,
        0xC1,
        0xC2,
        0xC3,
        0xC5,
        0xC6,
        0xC7,
        0xC9,
        0xCA,
        0xCB,
        0xCD,
        0xCE,
        0xCF,
    }
    while offset < len(data):
        if data[offset] != 0xFF:
            return False
        marker_start = offset
        while offset < len(data) and data[offset] == 0xFF:
            offset += 1
        if offset >= len(data):
            return False
        marker = data[offset]
        offset += 1
        if marker == 0xD9:
            return saw_frame and saw_scan and offset == len(data)
        if marker == 0x00 or marker == 0xD8:
            return False
        if marker == 0x01 or 0xD0 <= marker <= 0xD7:
            continue
        if len(data) - offset < 2:
            return False
        segment_length = int.from_bytes(data[offset : offset + 2], "big")
        if segment_length < 2 or offset + segment_length > len(data):
            return False
        segment = data[offset + 2 : offset + segment_length]
        if marker in frame_markers:
            if len(segment) < 6:
                return False
            height = int.from_bytes(segment[1:3], "big")
            width = int.from_bytes(segment[3:5], "big")
            if width == 0 or height == 0:
                return False
            saw_frame = True
        offset += segment_length
        if marker != 0xDA:
            continue
        saw_scan = True
        while offset < len(data):
            marker_start = data.find(b"\xff", offset)
            if marker_start < 0:
                return False
            marker_offset = marker_start + 1
            while marker_offset < len(data) and data[marker_offset] == 0xFF:
                marker_offset += 1
            if marker_offset >= len(data):
                return False
            marker = data[marker_offset]
            if marker == 0x00 or 0xD0 <= marker <= 0xD7:
                offset = marker_offset + 1
                continue
            offset = marker_start
            break
    return False


def is_valid_webp(data: bytes) -> bool:
    if (
        len(data) < 20
        or data[0:4] != b"RIFF"
        or data[8:12] != b"WEBP"
        or int.from_bytes(data[4:8], "little") + 8 != len(data)
    ):
        return False
    offset = 12
    saw_image_chunk = False
    while offset < len(data):
        if len(data) - offset < 8:
            return False
        chunk_type = data[offset : offset + 4]
        chunk_size = int.from_bytes(data[offset + 4 : offset + 8], "little")
        chunk_end = offset + 8 + chunk_size
        padded_end = chunk_end + (chunk_size % 2)
        if chunk_end > len(data) or padded_end > len(data):
            return False
        chunk_data = data[offset + 8 : chunk_end]
        if chunk_type == b"VP8 ":
            if (
                len(chunk_data) < 10
                or chunk_data[3:6] != b"\x9d\x01\x2a"
                or int.from_bytes(chunk_data[6:8], "little") & 0x3FFF == 0
                or int.from_bytes(chunk_data[8:10], "little") & 0x3FFF == 0
            ):
                return False
            saw_image_chunk = True
        elif chunk_type == b"VP8L":
            if len(chunk_data) < 5 or chunk_data[0] != 0x2F:
                return False
            saw_image_chunk = True
        elif chunk_type == b"VP8X":
            if len(chunk_data) != 10:
                return False
        offset = padded_end
    return saw_image_chunk and offset == len(data)


def is_supported_image(path: Path) -> bool:
    try:
        data = path.read_bytes()
    except OSError:
        return False
    return is_valid_png(data) or is_valid_jpeg(data) or is_valid_webp(data)


def is_placeholder(value: str) -> bool:
    normalized = re.sub(r"[^a-z0-9]+", " ", value.casefold()).strip()
    exact_sentinels = {
        "tbd",
        "n a",
        "na",
        "replace me",
        "fixme",
        "fix me",
        "changeme",
        "change me",
        "unknown",
        "pending",
    }
    phrase_sentinels = (
        "example only",
        "placeholder",
        "mock only",
        "replace me",
    )
    return (
        normalized in exact_sentinels
        or normalized.startswith("todo ")
        or normalized == "todo"
        or any(phrase in normalized for phrase in phrase_sentinels)
    )


def validate_screen_contract(payload: Any) -> list[str]:
    errors: list[str] = []
    if not isinstance(payload, dict):
        return ["screen contract must be a JSON object"]
    reject_unknown_fields(payload, SCREEN_FIELDS, "screen contract", errors)
    if payload.get("schema_version") != SCREEN_SCHEMA_VERSION:
        errors.append(f"schema_version must be {SCREEN_SCHEMA_VERSION}")

    for field in sorted(REQUIRED_SCREEN_FIELDS):
        if field not in payload:
            errors.append(f"missing required field: {field}")

    for field in (
        "id",
        "primary_decision",
    ):
        if field in payload and not non_empty_string(payload[field]):
            errors.append(f"{field} must be a non-empty string")

    mode = payload.get("mode")
    if not isinstance(mode, str) or mode not in SCREEN_MODES:
        errors.append(f"mode must be one of {sorted(SCREEN_MODES)}")
    surface = payload.get("surface")
    if not isinstance(surface, str) or surface not in SCREEN_SURFACES:
        errors.append(f"surface must be one of {sorted(SCREEN_SURFACES)}")

    for field in (
        "actors",
        "jobs",
        "entities",
        "lifecycle",
        "actions",
        "permissions",
        "risks",
        "view_states",
    ):
        if field in payload and not non_empty_string_list(payload[field]):
            errors.append(f"{field} must be a non-empty array of strings")

    unresolved = payload.get("unresolved_decisions")
    if not isinstance(unresolved, list):
        errors.append("unresolved_decisions must be an array")
    else:
        for index, unknown in enumerate(unresolved):
            if not isinstance(unknown, dict):
                errors.append(
                    f"unresolved_decisions[{index}] must be a structured object"
                )
                continue
            reject_unknown_fields(
                unknown,
                UNRESOLVED_DECISION_FIELDS,
                f"unresolved_decisions[{index}]",
                errors,
            )
            for field in ("id", "area", "reason", "evidence_needed"):
                if not non_empty_string(unknown.get(field)):
                    errors.append(
                        f"unresolved_decisions[{index}].{field} must be a non-empty string"
                    )
            gate_ids = unknown.get("gate_ids")
            if not non_empty_string_list(gate_ids):
                errors.append(
                    f"unresolved_decisions[{index}].gate_ids must be a non-empty array of strings"
                )
            else:
                invalid_gate_ids = sorted(set(gate_ids) - set(GATE_IDS))
                if invalid_gate_ids:
                    errors.append(
                        f"unresolved_decisions[{index}] has unknown gate_ids: {invalid_gate_ids}"
                    )

    exclusions = payload.get("exclusions")
    valid_exclusions: dict[str, dict[str, Any]] = {}
    if not isinstance(exclusions, list):
        errors.append("exclusions must be an array")
    else:
        for index, exclusion in enumerate(exclusions):
            if not isinstance(exclusion, dict):
                errors.append(f"exclusions[{index}] must be an object")
                continue
            reject_unknown_fields(
                exclusion, EXCLUSION_FIELDS, f"exclusions[{index}]", errors
            )
            if not non_empty_string(exclusion.get("id")):
                errors.append(f"exclusions[{index}].id must be a non-empty string")
            elif exclusion["id"] in valid_exclusions:
                errors.append(f"duplicate exclusion id: {exclusion['id']}")
            else:
                valid_exclusions[exclusion["id"]] = exclusion
            if not non_empty_string(exclusion.get("reason")):
                errors.append(f"exclusions[{index}].reason must be a non-empty string")
            kind = exclusion.get("kind")
            if not isinstance(kind, str) or kind not in EXCLUSION_CHECKS:
                errors.append(
                    f"exclusions[{index}].kind must be one of {sorted(EXCLUSION_CHECKS)}"
                )
            check_ids = exclusion.get("check_ids")
            if not non_empty_string_list(check_ids):
                errors.append(
                    f"exclusions[{index}].check_ids must be a non-empty array of strings"
                )
            elif isinstance(kind, str) and kind in EXCLUSION_CHECKS:
                invalid_checks = sorted(set(check_ids) - EXCLUSION_CHECKS[kind])
                if invalid_checks:
                    errors.append(
                        f"exclusions[{index}] kind {kind} cannot exclude checks: {invalid_checks}"
                    )
            if kind == "embedded-shell" and payload.get("surface") != "embedded-view":
                errors.append(
                    f"exclusions[{index}] embedded-shell requires surface=embedded-view"
                )
            if kind == "desktop-only":
                minimum_viewport = exclusion.get("minimum_viewport")
                if not isinstance(minimum_viewport, dict):
                    errors.append(
                        f"exclusions[{index}].minimum_viewport must be an object for desktop-only"
                    )
                else:
                    reject_unknown_fields(
                        minimum_viewport,
                        {"width", "height"},
                        f"exclusions[{index}].minimum_viewport",
                        errors,
                    )
                    for dimension, maximum in (("width", 1440), ("height", 900)):
                        value = minimum_viewport.get(dimension)
                        if type(value) is not int or value <= 0 or value > maximum:
                            errors.append(
                                f"exclusions[{index}].minimum_viewport.{dimension} must be a positive integer no greater than {maximum}"
                            )
                operational_reason = exclusion.get("operational_reason")
                if (
                    not non_empty_string(operational_reason)
                    or len(operational_reason.strip()) < 20
                ):
                    errors.append(
                        f"exclusions[{index}].operational_reason must be a specific string of at least 20 characters"
                    )

    viewport_ids: set[str] = set()
    viewports = payload.get("viewports")
    if not isinstance(viewports, list) or not viewports:
        errors.append("viewports must be a non-empty array")
    else:
        for index, viewport in enumerate(viewports):
            if not isinstance(viewport, dict):
                errors.append(f"viewports[{index}] must be an object")
                continue
            reject_unknown_fields(
                viewport, VIEWPORT_FIELDS, f"viewports[{index}]", errors
            )
            viewport_id = viewport.get("id")
            if not non_empty_string(viewport_id):
                errors.append(f"viewports[{index}].id must be a non-empty string")
            else:
                if viewport_id in viewport_ids:
                    errors.append(f"duplicate viewport id: {viewport_id}")
                viewport_ids.add(viewport_id)
            for dimension in ("width", "height"):
                if type(viewport.get(dimension)) is not int or viewport[dimension] <= 0:
                    errors.append(f"viewports[{index}].{dimension} must be a positive integer")

    viewport_by_id = {
        viewport.get("id"): viewport
        for viewport in viewports or []
        if isinstance(viewport, dict) and non_empty_string(viewport.get("id"))
    } if isinstance(viewports, list) else {}
    wide = viewport_by_id.get("wide")
    if not isinstance(wide, dict) or (wide.get("width"), wide.get("height")) != (1440, 900):
        errors.append("wide viewport must be 1440x900")
    narrow = viewport_by_id.get("narrow")
    desktop_only = any(
        exclusion.get("kind") == "desktop-only"
        and "narrow-or-excluded" in string_items(exclusion.get("check_ids"))
        for exclusion in valid_exclusions.values()
    )
    if narrow is None and not desktop_only:
        errors.append(
            "missing narrow viewport requires a desktop-only exclusion for narrow-or-excluded"
        )
    elif isinstance(narrow, dict) and isinstance(narrow.get("width"), int):
        if narrow["width"] >= 1440:
            errors.append("narrow viewport width must be less than 1440")

    scenario_ids: set[str] = set()
    covered_dimensions = {
        field: set() for field in sorted(SCENARIO_COVERAGE_FIELDS)
    }
    scenarios = payload.get("evidence_scenarios")
    if not isinstance(scenarios, list) or not scenarios:
        errors.append("evidence_scenarios must be a non-empty array")
    else:
        for index, scenario in enumerate(scenarios):
            if not isinstance(scenario, dict):
                errors.append(f"evidence_scenarios[{index}] must be an object")
                continue
            reject_unknown_fields(
                scenario,
                SCENARIO_FIELDS,
                f"evidence_scenarios[{index}]",
                errors,
            )
            scenario_id = scenario.get("id")
            if not non_empty_string(scenario_id):
                errors.append(f"evidence_scenarios[{index}].id must be a non-empty string")
            else:
                if scenario_id in scenario_ids:
                    errors.append(f"duplicate evidence scenario id: {scenario_id}")
                scenario_ids.add(scenario_id)
            for field in ("requirement_ids", "actions", "required_viewports"):
                if not non_empty_string_list(scenario.get(field)):
                    errors.append(
                        f"evidence_scenarios[{index}].{field} must be a non-empty array of strings"
                    )
            for field in ("initial_state", "expected"):
                if not non_empty_string(scenario.get(field)):
                    errors.append(
                        f"evidence_scenarios[{index}].{field} must be a non-empty string"
                    )
            coverage = scenario.get("coverage")
            if not isinstance(coverage, dict):
                errors.append(
                    f"evidence_scenarios[{index}].coverage must be an object"
                )
            else:
                reject_unknown_fields(
                    coverage,
                    SCENARIO_COVERAGE_FIELDS,
                    f"evidence_scenarios[{index}].coverage",
                    errors,
                )
                for field in sorted(SCENARIO_COVERAGE_FIELDS):
                    values = coverage.get(field)
                    if not string_list(values):
                        errors.append(
                            f"evidence_scenarios[{index}].coverage.{field} "
                            "must be an array of strings"
                        )
                        continue
                    if len(values) != len(set(values)):
                        errors.append(
                            f"evidence_scenarios[{index}].coverage.{field} "
                            "must not contain duplicates"
                        )
                    declared_values = set(string_items(payload.get(field)))
                    unknown_values = sorted(set(values) - declared_values)
                    if unknown_values:
                        errors.append(
                            f"evidence_scenarios[{index}].coverage.{field} "
                            f"references unknown values: {unknown_values}"
                        )
                    if field == "actions":
                        unexercised_actions = sorted(
                            set(values) - set(string_items(scenario.get("actions")))
                        )
                        if unexercised_actions:
                            errors.append(
                                f"evidence_scenarios[{index}].coverage.actions "
                                "must be exercised by scenario actions: "
                                f"{unexercised_actions}"
                            )
                    covered_dimensions[field].update(values)
            required_viewports = scenario.get("required_viewports")
            if isinstance(required_viewports, list):
                for viewport_id in required_viewports:
                    if not isinstance(viewport_id, str):
                        continue
                    if viewport_id not in viewport_ids:
                        errors.append(
                            f"evidence_scenarios[{index}] references unknown viewport: {viewport_id}"
                        )
                required_viewport_set = {
                    item for item in required_viewports if isinstance(item, str)
                }
                if "wide" not in required_viewport_set:
                    errors.append(
                        f"evidence_scenarios[{index}] must require the wide viewport"
                    )
                if narrow is not None and "narrow" not in required_viewport_set:
                    errors.append(
                        f"evidence_scenarios[{index}] must require the narrow viewport"
                    )

    for field in sorted(SCENARIO_COVERAGE_FIELDS):
        declared_values = set(string_items(payload.get(field)))
        missing_values = sorted(declared_values - covered_dimensions[field])
        if missing_values:
            errors.append(f"scenario coverage missing {field}: {missing_values}")

    requirement_ids: set[str] = set()
    requirements = payload.get("requirements")
    if not isinstance(requirements, list) or not requirements:
        errors.append("requirements must be a non-empty array")
    else:
        for index, requirement in enumerate(requirements):
            if not isinstance(requirement, dict):
                errors.append(f"requirements[{index}] must be an object")
                continue
            reject_unknown_fields(
                requirement,
                REQUIREMENT_FIELDS,
                f"requirements[{index}]",
                errors,
            )
            requirement_id = requirement.get("id")
            if not non_empty_string(requirement_id):
                errors.append(f"requirements[{index}].id must be a non-empty string")
            else:
                if requirement_id in requirement_ids:
                    errors.append(f"duplicate requirement id: {requirement_id}")
                requirement_ids.add(requirement_id)
            if not non_empty_string(requirement.get("text")):
                errors.append(f"requirements[{index}].text must be a non-empty string")
            if not non_empty_string_list(requirement.get("scenario_ids")):
                errors.append(
                    f"requirements[{index}].scenario_ids must be a non-empty array of strings"
                )
            linked_scenarios = requirement.get("scenario_ids")
            if isinstance(linked_scenarios, list):
                for scenario_id in linked_scenarios:
                    if not isinstance(scenario_id, str):
                        continue
                    if scenario_id not in scenario_ids:
                        errors.append(
                            f"requirements[{index}] references unknown scenario: {scenario_id}"
                        )

    valid_scenarios = scenarios if isinstance(scenarios, list) else []
    for index, scenario in enumerate(valid_scenarios):
        if not isinstance(scenario, dict):
            continue
        linked_requirements = scenario.get("requirement_ids")
        if isinstance(linked_requirements, list):
            for requirement_id in linked_requirements:
                if not isinstance(requirement_id, str):
                    continue
                if requirement_id not in requirement_ids:
                    errors.append(
                        f"evidence_scenarios[{index}] references unknown requirement: {requirement_id}"
                    )

    scenario_by_id = {
        scenario.get("id"): scenario
        for scenario in valid_scenarios
        if isinstance(scenario, dict) and non_empty_string(scenario.get("id"))
    }
    valid_requirements = requirements if isinstance(requirements, list) else []
    requirement_by_id = {
        requirement.get("id"): requirement
        for requirement in valid_requirements
        if isinstance(requirement, dict)
        and non_empty_string(requirement.get("id"))
    }
    for requirement_id, requirement in requirement_by_id.items():
        for scenario_id in string_items(requirement.get("scenario_ids")):
            scenario = scenario_by_id.get(scenario_id)
            if scenario is None:
                continue
            reverse_ids = scenario.get("requirement_ids")
            if isinstance(reverse_ids, list) and requirement_id not in reverse_ids:
                errors.append(
                    f"requirement/scenario mapping must be reciprocal: {requirement_id}->{scenario_id}"
                )
    for scenario_id, scenario in scenario_by_id.items():
        for requirement_id in string_items(scenario.get("requirement_ids")):
            requirement = requirement_by_id.get(requirement_id)
            if requirement is None:
                continue
            reverse_ids = requirement.get("scenario_ids")
            if isinstance(reverse_ids, list) and scenario_id not in reverse_ids:
                errors.append(
                    f"requirement/scenario mapping must be reciprocal: {scenario_id}->{requirement_id}"
                )

    if mode == "redesign":
        validate_redesign_traceability(
            payload,
            scenario_ids=scenario_ids,
            requirement_ids=requirement_ids,
            errors=errors,
        )
    return errors


def validate_redesign_traceability(
    payload: dict[str, Any],
    *,
    scenario_ids: set[str],
    requirement_ids: set[str],
    errors: list[str],
) -> None:
    inventory = payload.get("current_behavior_inventory")
    if not isinstance(inventory, list) or not inventory:
        errors.append(
            "redesign current_behavior_inventory must be a non-empty array"
        )
        inventory = []
    known_inventory_ids: set[str] = set()
    inventory_by_id: dict[str, dict[str, Any]] = {}
    for index, item in enumerate(inventory):
        if not isinstance(item, dict):
            errors.append(f"current_behavior_inventory[{index}] must be an object")
            continue
        reject_unknown_fields(
            item,
            INVENTORY_FIELDS,
            f"current_behavior_inventory[{index}]",
            errors,
        )
        inventory_id = item.get("id")
        if not non_empty_string(inventory_id):
            errors.append(
                f"current_behavior_inventory[{index}].id must be a non-empty string"
            )
        else:
            if inventory_id in known_inventory_ids:
                errors.append(f"duplicate current behavior inventory id: {inventory_id}")
            known_inventory_ids.add(inventory_id)
            inventory_by_id[inventory_id] = item
        item_kind = item.get("kind")
        if not isinstance(item_kind, str) or item_kind not in INVENTORY_KINDS:
            errors.append(
                f"current_behavior_inventory[{index}].kind must be one of {sorted(INVENTORY_KINDS)}"
            )
        decision = item.get("decision")
        if not isinstance(decision, str) or decision not in INVENTORY_DECISIONS:
            errors.append(
                f"current_behavior_inventory[{index}].decision must be preserve or change"
            )
        for field in ("observed", "reason", "implementation_target"):
            if not non_empty_string(item.get(field)):
                errors.append(
                    f"current_behavior_inventory[{index}].{field} must be a non-empty string"
                )
        if not non_empty_string_list(item.get("evidence")):
            errors.append(
                f"current_behavior_inventory[{index}].evidence must be a non-empty array of strings"
            )
        linked_scenarios = item.get("scenario_ids")
        if not non_empty_string_list(linked_scenarios):
            errors.append(
                f"current_behavior_inventory[{index}].scenario_ids must be a non-empty array of strings"
            )
        elif any(scenario_id not in scenario_ids for scenario_id in linked_scenarios):
            errors.append(
                f"current_behavior_inventory[{index}] references an unknown scenario"
            )

    change_contract = payload.get("change_contract")
    if not isinstance(change_contract, list) or not change_contract:
        errors.append("redesign change_contract must be a non-empty array")
        change_contract = []
    mapped_inventory_ids: set[str] = set()
    inventory_mapping_owner: dict[str, int] = {}
    change_contract_ids: set[str] = set()
    for index, item in enumerate(change_contract):
        if not isinstance(item, dict):
            errors.append(f"change_contract[{index}] must be an object")
            continue
        reject_unknown_fields(
            item, CHANGE_CONTRACT_FIELDS, f"change_contract[{index}]", errors
        )
        contract_id = item.get("id")
        if not non_empty_string(contract_id):
            errors.append(f"change_contract[{index}].id must be a non-empty string")
        else:
            if contract_id in change_contract_ids:
                errors.append(f"duplicate change contract id: {contract_id}")
            change_contract_ids.add(contract_id)
        if not non_empty_string(item.get("description")):
            errors.append(
                f"change_contract[{index}].description must be a non-empty string"
            )
        linked_inventory = item.get("inventory_ids")
        if not non_empty_string_list(linked_inventory):
            errors.append(
                f"change_contract[{index}].inventory_ids must be a non-empty array of strings"
            )
        else:
            for inventory_id in linked_inventory:
                previous_owner = inventory_mapping_owner.get(inventory_id)
                if previous_owner is not None and previous_owner != index:
                    errors.append(
                        f"inventory id {inventory_id} is mapped by multiple change contracts: "
                        f"change_contract[{previous_owner}] and change_contract[{index}]"
                    )
                else:
                    inventory_mapping_owner[inventory_id] = index
            mapped_inventory_ids.update(linked_inventory)
            unknown = sorted(set(linked_inventory) - known_inventory_ids)
            if unknown:
                errors.append(
                    f"change_contract[{index}] references unknown inventory ids: {unknown}"
                )
        linked_requirements = item.get("requirement_ids")
        if not non_empty_string_list(linked_requirements):
            errors.append(
                f"change_contract[{index}].requirement_ids must be a non-empty array of strings"
            )
        else:
            unknown = sorted(set(linked_requirements) - requirement_ids)
            if unknown:
                errors.append(
                    f"change_contract[{index}] references unknown requirement ids: {unknown}"
                )
        if non_empty_string_list(linked_inventory) and non_empty_string_list(
            linked_requirements
        ):
            inventory_scenarios_by_id = {
                inventory_id: set(
                    string_items(
                        inventory_by_id.get(inventory_id, {}).get("scenario_ids")
                    )
                )
                for inventory_id in linked_inventory
            }
            requirements_payload = payload.get("requirements")
            if not isinstance(requirements_payload, list):
                requirements_payload = []
            requirement_scenarios_by_id = {
                requirement_id: set(
                    string_items(
                    next(
                        (
                            requirement.get("scenario_ids")
                            for requirement in requirements_payload
                            if isinstance(requirement, dict)
                            and requirement.get("id") == requirement_id
                        ),
                        [],
                    )
                    )
                )
                for requirement_id in linked_requirements
            }
            inventory_scenarios = set().union(*inventory_scenarios_by_id.values())
            requirement_scenarios = set().union(
                *requirement_scenarios_by_id.values()
            )
            scenario_sets = [
                *inventory_scenarios_by_id.values(),
                *requirement_scenarios_by_id.values(),
            ]
            shared_by_every_member = (
                set.intersection(*scenario_sets) if scenario_sets else set()
            )
            if not inventory_scenarios.intersection(requirement_scenarios):
                errors.append(
                    f"change_contract[{index}] inventory and requirements must share a common scenario"
                )
            for inventory_id, linked_scenarios in inventory_scenarios_by_id.items():
                if not linked_scenarios.intersection(requirement_scenarios):
                    errors.append(
                        f"change_contract[{index}] inventory {inventory_id} must share a common scenario with its requirements"
                    )
            for requirement_id, linked_scenarios in requirement_scenarios_by_id.items():
                if not linked_scenarios.intersection(inventory_scenarios):
                    errors.append(
                        f"change_contract[{index}] requirement {requirement_id} must share a common scenario with its inventory"
                    )
            if not shared_by_every_member:
                errors.append(
                    f"change_contract[{index}] must have one scenario shared by every member"
                )

    if mapped_inventory_ids != known_inventory_ids:
        missing = sorted(known_inventory_ids - mapped_inventory_ids)
        extra = sorted(mapped_inventory_ids - known_inventory_ids)
        errors.append(
            "redesign inventory mapping must have 100% coverage; "
            f"missing={missing}, extra={extra}"
        )


def validate_quality_report(
    payload: Any, screen: Any, *, report_directory: Path | None = None
) -> list[str]:
    errors = validate_screen_contract(screen)
    if errors:
        return [f"screen contract: {error}" for error in errors]
    if not isinstance(payload, dict):
        return ["quality report must be a JSON object"]
    reject_unknown_fields(payload, REPORT_FIELDS, "quality report", errors)
    if payload.get("schema_version") != REPORT_SCHEMA_VERSION:
        errors.append(f"schema_version must be {REPORT_SCHEMA_VERSION}")
    if payload.get("screen_contract_id") != screen.get("id"):
        errors.append("screen_contract_id must match screen contract id")
    overall = payload.get("overall")
    if not isinstance(overall, str) or overall not in GATE_STATUSES:
        errors.append(f"overall must be one of {sorted(GATE_STATUSES)}")
    if (
        payload.get("overall") == "passed"
        and screen.get("unresolved_decisions")
    ):
        errors.append(
            "overall=passed is invalid while unresolved_decisions remain"
        )

    profile = payload.get("design_profile")
    if not isinstance(profile, dict):
        errors.append("design_profile must be an object")
    else:
        reject_unknown_fields(
            profile, set(DESIGN_PROFILE), "design_profile", errors
        )
        for field, expected in DESIGN_PROFILE.items():
            if profile.get(field) != expected:
                errors.append(
                    f"design_profile.{field} must be {expected!r}, got {profile.get(field)!r}"
                )

    gates = payload.get("gates")
    if not isinstance(gates, list):
        errors.append("gates must be an array")
        gates = []
    actual_gate_ids = [gate.get("id") for gate in gates if isinstance(gate, dict)]
    if actual_gate_ids != GATE_IDS:
        errors.append(f"gates must use exact order {GATE_IDS}")

    for index, gate in enumerate(gates):
        if not isinstance(gate, dict):
            errors.append(f"gates[{index}] must be an object")
            continue
        reject_unknown_fields(gate, GATE_FIELDS, f"gates[{index}]", errors)
        gate_id = gate.get("id", f"index-{index}")
        if not non_empty_string(gate_id):
            errors.append(f"gates[{index}].id must be a non-empty string")
            gate_id = f"index-{index}"
        if gate.get("required") is not True:
            errors.append(f"{gate_id}.required must be true")
        gate_status = gate.get("status")
        if not isinstance(gate_status, str) or gate_status not in GATE_STATUSES:
            errors.append(f"{gate_id}.status must be one of {sorted(GATE_STATUSES)}")
        if not non_empty_string_list(gate.get("evidence")):
            errors.append(f"{gate_id}.evidence must be a non-empty array of strings")
        checks = gate.get("checks")
        if not isinstance(checks, list) or not checks:
            errors.append(f"{gate_id}.checks must be a non-empty array")
            continue
        actual_check_ids = [
            check.get("id") for check in checks if isinstance(check, dict)
        ]
        expected_check_ids = GATE_CHECK_IDS.get(gate_id, [])
        if actual_check_ids != expected_check_ids:
            errors.append(
                f"{gate_id}.checks must use exact order {expected_check_ids}"
            )
        for check_index, check in enumerate(checks):
            if not isinstance(check, dict):
                errors.append(f"{gate_id}.checks[{check_index}] must be an object")
                continue
            reject_unknown_fields(
                check,
                CHECK_FIELDS,
                f"{gate_id}.checks[{check_index}]",
                errors,
            )
            status = check.get("status")
            if not isinstance(status, str) or status not in CHECK_STATUSES:
                errors.append(
                    f"{gate_id}.checks[{check_index}].status must be one of {sorted(CHECK_STATUSES)}"
                )
            if status == "not_applicable":
                reason = check.get("not_applicable_reason")
                exclusion_id = check.get("exclusion_id")
                if not non_empty_string(reason) or not non_empty_string(exclusion_id):
                    errors.append(
                        f"{gate_id}.checks[{check_index}] not_applicable requires reason and exclusion_id"
                    )
                known_exclusions = {
                    item.get("id"): item
                    for item in screen.get("exclusions", [])
                    if isinstance(item, dict)
                }
                if not non_empty_string(exclusion_id):
                    pass
                elif exclusion_id not in known_exclusions:
                    errors.append(
                        f"{gate_id}.checks[{check_index}] references unknown exclusion_id: {exclusion_id}"
                    )
                elif check.get("id") not in known_exclusions[exclusion_id].get(
                    "check_ids", []
                ):
                    errors.append(
                        f"{gate_id}.checks[{check_index}] {check.get('id')} cannot be not_applicable with exclusion {exclusion_id}"
                    )
            elif not non_empty_string_list(check.get("evidence")):
                errors.append(
                    f"{gate_id}.checks[{check_index}].evidence must be a non-empty array"
                )
        if gate.get("status") == "passed":
            non_passing_checks = [
                check.get("id")
                for check in checks
                if isinstance(check, dict)
                and check.get("status") not in ("passed", "not_applicable")
            ]
            if non_passing_checks:
                errors.append(
                    f"{gate_id}.status=passed is invalid because checks are not passed: {non_passing_checks}"
                )

    if screen.get("unresolved_decisions"):
        affected_gate_ids = {"G0"}
        for unknown in screen["unresolved_decisions"]:
            if isinstance(unknown, dict):
                affected_gate_ids.update(string_items(unknown.get("gate_ids")))
        passed_unknown_gates = [
            gate.get("id")
            for gate in gates
            if isinstance(gate, dict)
            and isinstance(gate.get("id"), str)
            and gate.get("id") in affected_gate_ids
            and gate.get("status") == "passed"
        ]
        if passed_unknown_gates:
            errors.append(
                "unresolved_decisions forbid passed gates: "
                f"{passed_unknown_gates}"
            )

    receipts = payload.get("browser_receipts")
    if not isinstance(receipts, list):
        errors.append("browser_receipts must be an array")
        receipts = []
    valid_scenarios = {
        scenario["id"]: scenario
        for scenario in screen.get("evidence_scenarios", [])
        if isinstance(scenario, dict)
        and non_empty_string(scenario.get("id"))
        and isinstance(scenario.get("required_viewports"), list)
    }
    expected_receipts = {
        (scenario_id, viewport_id)
        for scenario_id, scenario in valid_scenarios.items()
        for viewport_id in scenario["required_viewports"]
        if isinstance(viewport_id, str)
    }
    actual_receipts: set[tuple[str, str]] = set()
    for index, receipt in enumerate(receipts):
        if not isinstance(receipt, dict):
            errors.append(f"browser_receipts[{index}] must be an object")
            continue
        reject_unknown_fields(
            receipt,
            REQUIRED_BROWSER_FIELDS,
            f"browser_receipts[{index}]",
            errors,
        )
        for field in sorted(REQUIRED_BROWSER_FIELDS):
            if field not in receipt:
                errors.append(f"browser_receipts[{index}] missing field: {field}")
        for field in (
            "scenario_id",
            "command",
            "build_or_revision",
            "url",
            "viewport_id",
            "expected",
            "observed",
        ):
            if field in receipt and not non_empty_string(receipt[field]):
                errors.append(f"browser_receipts[{index}].{field} must be non-empty")
        receipt_status = receipt.get("status")
        if not isinstance(receipt_status, str) or receipt_status not in GATE_STATUSES:
            errors.append(
                f"browser_receipts[{index}].status must be one of {sorted(GATE_STATUSES)}"
            )
        elif payload.get("overall") == "passed" and receipt.get("status") != "passed":
            errors.append(
                f"browser_receipts[{index}] receipt status must be passed while overall=passed"
            )
        for field in ("actions", "screenshots"):
            if field in receipt and not non_empty_string_list(receipt[field]):
                errors.append(
                    f"browser_receipts[{index}].{field} must be a non-empty array of strings"
                )
        runtime_errors = receipt.get("console_runtime_errors")
        if "console_runtime_errors" in receipt and not isinstance(runtime_errors, list):
            errors.append(
                f"browser_receipts[{index}].console_runtime_errors must be an array"
            )
        elif isinstance(runtime_errors, list) and not all(
            non_empty_string(error) for error in runtime_errors
        ):
            errors.append(
                f"browser_receipts[{index}].console_runtime_errors must be an array of strings"
            )
        elif (
            payload.get("overall") == "passed"
            and runtime_errors
        ):
            errors.append(
                f"browser_receipts[{index}] has console/runtime errors while overall=passed"
            )
        key = (receipt.get("scenario_id"), receipt.get("viewport_id"))
        if all(non_empty_string(item) for item in key):
            if key in actual_receipts:
                errors.append(f"duplicate browser receipt: {key}")
            actual_receipts.add(key)
            if key not in expected_receipts:
                errors.append(
                    f"browser_receipts[{index}] has unknown or unrequired scenario/viewport pair: {key}"
                )
            scenario = valid_scenarios.get(receipt["scenario_id"])
            if scenario is not None:
                if receipt.get("actions") != scenario.get("actions"):
                    errors.append(
                        f"browser_receipts[{index}].actions must match scenario {receipt['scenario_id']}"
                    )
                if receipt.get("expected") != scenario.get("expected"):
                    errors.append(
                        f"browser_receipts[{index}].expected must match scenario {receipt['scenario_id']}"
                    )

        if payload.get("overall") == "passed":
            screenshot_values = receipt.get("screenshots")
            if not isinstance(screenshot_values, list):
                screenshot_values = []
            strings_to_check = [
                receipt.get("command"),
                receipt.get("build_or_revision"),
                receipt.get("url"),
                receipt.get("observed"),
                *screenshot_values,
            ]
            if any(
                isinstance(value, str) and is_placeholder(value)
                for value in strings_to_check
            ):
                errors.append(
                    f"browser_receipts[{index}] contains placeholder evidence while overall=passed"
                )

    missing_receipts = sorted(expected_receipts - actual_receipts)
    if payload.get("overall") == "passed" and missing_receipts:
        errors.append(f"missing required browser receipts: {missing_receipts}")

    if payload.get("overall") == "passed":
        non_passing = [
            gate.get("id")
            for gate in gates
            if isinstance(gate, dict) and gate.get("status") != "passed"
        ]
        if non_passing:
            errors.append(
                f"overall=passed is invalid because required gates are not passed: {non_passing}"
            )
        if missing_receipts:
            errors.append("overall=passed is invalid with missing browser evidence")
        if report_directory is not None:
            evidence_references: set[str] = set()
            screenshot_references: set[str] = set()
            for gate in gates:
                if not isinstance(gate, dict) or gate.get("status") != "passed":
                    continue
                gate_evidence = gate.get("evidence")
                if isinstance(gate_evidence, list):
                    evidence_references.update(
                        value for value in gate_evidence if isinstance(value, str)
                    )
                checks = gate.get("checks")
                if not isinstance(checks, list):
                    continue
                for check in checks:
                    if not isinstance(check, dict) or check.get("status") != "passed":
                        continue
                    check_evidence = check.get("evidence")
                    if isinstance(check_evidence, list):
                        evidence_references.update(
                            value for value in check_evidence if isinstance(value, str)
                        )
            for receipt in receipts:
                if not isinstance(receipt, dict):
                    continue
                screenshots = receipt.get("screenshots")
                if isinstance(screenshots, list):
                    screenshot_paths = {
                        value for value in screenshots if isinstance(value, str)
                    }
                    screenshot_references.update(screenshot_paths)
                    evidence_references.update(screenshot_paths)
            evidence_root = report_directory.resolve()
            for reference in sorted(evidence_references):
                evidence_path = Path(reference)
                if evidence_path.is_absolute():
                    errors.append(
                        f"evidence path must be report-relative for passed report: {reference}"
                    )
                    continue
                evidence_path = (evidence_root / evidence_path).resolve()
                try:
                    evidence_path.relative_to(evidence_root)
                except ValueError:
                    errors.append(
                        f"evidence path must stay within report directory: {reference}"
                    )
                    continue
                if not evidence_path.is_file() or evidence_path.stat().st_size == 0:
                    errors.append(f"missing evidence file for passed report: {reference}")
                elif reference in screenshot_references and not is_supported_image(
                    evidence_path
                ):
                    errors.append(
                        f"unsupported screenshot content for passed report: {reference}"
                    )
    return errors


def validate_evals(payload: Any) -> list[str]:
    errors: list[str] = []
    if not isinstance(payload, dict):
        return ["eval fixture must be a JSON object"]
    reject_unknown_fields(payload, EVAL_FIELDS, "eval fixture", errors)
    if payload.get("schema_version") != EVAL_SCHEMA_VERSION:
        errors.append(f"schema_version must be {EVAL_SCHEMA_VERSION}")
    cases = payload.get("cases")
    if not isinstance(cases, list) or not cases:
        return errors + ["cases must be a non-empty array"]
    case_ids: set[str] = set()
    for index, case in enumerate(cases):
        if not isinstance(case, dict):
            errors.append(f"cases[{index}] must be an object")
            continue
        reject_unknown_fields(case, EVAL_CASE_FIELDS, f"cases[{index}]", errors)
        case_id = case.get("id")
        if not non_empty_string(case_id):
            errors.append(f"cases[{index}].id must be a non-empty string")
        elif case_id in case_ids:
            errors.append(f"duplicate eval case id: {case_id}")
        else:
            case_ids.add(case_id)
        if not non_empty_string(case.get("prompt")):
            errors.append(f"cases[{index}].prompt must be a non-empty string")
        expected = case.get("expected")
        if not isinstance(expected, dict) or not expected:
            errors.append(f"cases[{index}].expected must be a non-empty object")
            continue
        reject_unknown_fields(
            expected, EVAL_EXPECTED_FIELDS, f"cases[{index}].expected", errors
        )
        selected_skills: dict[str, set[str]] = {}
        for field in ("select", "must_not_select"):
            if field not in expected:
                continue
            value = expected[field]
            if not non_empty_string_list(value):
                errors.append(
                    f"cases[{index}].expected.{field} must be a non-empty array of strings"
                )
                continue
            skill_ids = set(value)
            selected_skills[field] = skill_ids
            unknown_skills = sorted(skill_ids - KNOWN_SKILL_IDS)
            if unknown_skills:
                errors.append(
                    f"cases[{index}].expected.{field} has unknown skill ids: {unknown_skills}"
                )
        conflicts = sorted(
            selected_skills.get("select", set())
            & selected_skills.get("must_not_select", set())
        )
        if conflicts:
            errors.append(
                f"cases[{index}].expected cannot both select and must_not_select: {conflicts}"
            )
        for field in sorted(EVAL_BOOLEAN_FIELDS):
            if field in expected and type(expected[field]) is not bool:
                errors.append(f"cases[{index}].expected.{field} must be a boolean")
        for field in sorted(EVAL_STRING_FIELDS):
            if field in expected and not non_empty_string(expected[field]):
                errors.append(
                    f"cases[{index}].expected.{field} must be a non-empty string"
                )
        if "must_require_mapping_coverage" in expected:
            value = expected["must_require_mapping_coverage"]
            if type(value) not in (int, float) or not 0 <= value <= 1:
                errors.append(
                    f"cases[{index}].expected.must_require_mapping_coverage "
                    "must be a number from 0 to 1"
                )
        enum_fields = {
            "mode": {"read-only"},
            "when_official_capability_missing": {
                "blocked_if_required_otherwise_not_run"
            },
            "gate_G7": {"not_run_or_blocked"},
        }
        for field, allowed_values in enum_fields.items():
            value = expected.get(field)
            if field in expected and (
                not isinstance(value, str) or value not in allowed_values
            ):
                errors.append(
                    f"cases[{index}].expected.{field} must be one of {sorted(allowed_values)}"
                )
        if "required_checks" in expected:
            checks = expected["required_checks"]
            if not non_empty_string_list(checks):
                errors.append(
                    f"cases[{index}].expected.required_checks must be a non-empty array of strings"
                )
            else:
                known_checks = {
                    check_id for values in GATE_CHECK_IDS.values() for check_id in values
                }
                unknown_checks = sorted(set(checks) - known_checks)
                if unknown_checks:
                    errors.append(
                        f"cases[{index}].expected.required_checks "
                        f"has unknown check ids: {unknown_checks}"
                    )
    return errors


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    subparsers = parser.add_subparsers(dest="command", required=True)

    screen = subparsers.add_parser("screen-contract")
    screen.add_argument("screen_contract", type=Path)

    report = subparsers.add_parser("quality-report")
    report.add_argument("quality_report", type=Path)
    report.add_argument("screen_contract", type=Path)

    evals = subparsers.add_parser("evals")
    evals.add_argument("cases", type=Path)
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    load_errors: list[str] = []
    if args.command == "screen-contract":
        payload = load_json(args.screen_contract, load_errors)
        errors = load_errors or validate_screen_contract(payload)
    elif args.command == "quality-report":
        report = load_json(args.quality_report, load_errors)
        screen = load_json(args.screen_contract, load_errors)
        errors = load_errors or validate_quality_report(
            report, screen, report_directory=args.quality_report.resolve().parent
        )
    else:
        payload = load_json(args.cases, load_errors)
        errors = load_errors or validate_evals(payload)

    if errors:
        print("Validation failed:")
        for error in errors:
            print(f"- {error}")
        raise SystemExit(1)
    print(f"Validation passed: {args.command}")


if __name__ == "__main__":
    main()
