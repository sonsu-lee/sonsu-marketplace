#!/usr/bin/env python3
"""Validate Operations UI v2 contracts, reports, runtime evidence, and eval cases."""

from __future__ import annotations

import argparse
import json
import sys
import zlib
from pathlib import Path
from typing import Any

import validate_design_quality as design_quality


EVAL_SCHEMA_VERSION = "operations-ui-evals-v2"
KNOWN_SKILL_IDS = {
    "operations-ui:design-operations-ui",
    "operations-ui:redesign-operations-ui",
    "operations-ui:audit-operations-ui",
    "operations-ui:figma-operations-flow",
}
KNOWN_REQUIREMENTS = {
    "build-design-decision-contract",
    "inventory-current-behavior",
    "map-change-contract",
    "run-dq0-dq6",
    "run-dq0-dq7",
    "run-dq0-dq8",
    "collect-browser-receipts",
    "collect-risk-appropriate-user-evidence",
    "map-native-figma-structure",
    "validate-prototype-scenarios",
    "document-unresolved-decisions",
    "use-product-design-system",
    "preserve-requirement-scenario-traceability",
}
EVAL_FIELDS = {"schema_version", "cases"}
CASE_FIELDS = {"id", "prompt", "expected"}
EXPECTED_FIELDS = {
    "select",
    "must_not_select",
    "profile",
    "artifact_scope",
    "mode",
    "requirements",
    "prohibitions",
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


def unique_string_list(value: Any, *, allow_empty: bool = False) -> bool:
    return (
        isinstance(value, list)
        and (allow_empty or bool(value))
        and all(non_empty_string(item) for item in value)
        and len(value) == len(set(value))
    )


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
        0xC0, 0xC1, 0xC2, 0xC3, 0xC5, 0xC6, 0xC7,
        0xC9, 0xCA, 0xCB, 0xCD, 0xCE, 0xCF,
    }
    while offset < len(data):
        if data[offset] != 0xFF:
            return False
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
        elif chunk_type == b"VP8X" and len(chunk_data) != 10:
            return False
        offset = padded_end
    return saw_image_chunk and offset == len(data)


def valid_image(data: bytes) -> bool:
    return is_valid_png(data) or is_valid_jpeg(data) or is_valid_webp(data)


def validate_runtime_files(report: Any, report_path: Path) -> list[str]:
    errors: list[str] = []
    if not isinstance(report, dict):
        return errors
    extensions = report.get("extensions")
    if not isinstance(extensions, dict):
        return errors
    operations = extensions.get("operations")
    if not isinstance(operations, dict):
        return errors
    receipts = operations.get("browser_receipts")
    if not isinstance(receipts, list):
        return errors
    base = report_path.resolve().parent
    for receipt_index, receipt in enumerate(receipts):
        if not isinstance(receipt, dict) or not isinstance(receipt.get("screenshots"), list):
            continue
        for screenshot_index, relative in enumerate(receipt["screenshots"]):
            context = (
                f"extensions.operations.browser_receipts[{receipt_index}]"
                f".screenshots[{screenshot_index}]"
            )
            if not design_quality.relative_path(relative):
                continue
            path = base / relative
            try:
                resolved = path.resolve(strict=True)
            except (OSError, ValueError, RuntimeError):
                errors.append(f"{context}: screenshot does not exist: {relative}")
                continue
            try:
                resolved.relative_to(base)
            except ValueError:
                errors.append(f"{context}: screenshot escapes the report directory")
                continue
            try:
                data = resolved.read_bytes()
            except OSError as error:
                errors.append(f"{context}: unable to read screenshot: {error}")
                continue
            if not valid_image(data):
                errors.append(f"{context}: screenshot must be a valid PNG, JPEG, or WebP image")
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
        context = f"cases[{index}]"
        if not isinstance(case, dict):
            errors.append(f"{context} must be an object")
            continue
        reject_unknown_fields(case, CASE_FIELDS, context, errors)
        if set(case) != CASE_FIELDS:
            errors.append(f"{context} must contain exactly {sorted(CASE_FIELDS)}")
        case_id = case.get("id")
        if not non_empty_string(case_id):
            errors.append(f"{context}.id must be a non-empty string")
        elif case_id in case_ids:
            errors.append(f"duplicate case id: {case_id}")
        else:
            case_ids.add(case_id)
        if not non_empty_string(case.get("prompt")):
            errors.append(f"{context}.prompt must be a non-empty string")
        expected = case.get("expected")
        if not isinstance(expected, dict):
            errors.append(f"{context}.expected must be an object")
            continue
        expected_context = f"{context}.expected"
        reject_unknown_fields(expected, EXPECTED_FIELDS, expected_context, errors)
        if set(expected) != EXPECTED_FIELDS:
            errors.append(f"{expected_context} must contain exactly {sorted(EXPECTED_FIELDS)}")
        selected = expected.get("select")
        rejected = expected.get("must_not_select")
        if not unique_string_list(selected, allow_empty=True):
            errors.append(f"{expected_context}.select must be a unique string array")
            selected = []
        if not unique_string_list(rejected, allow_empty=True):
            errors.append(f"{expected_context}.must_not_select must be a unique string array")
            rejected = []
        if not selected and not rejected:
            errors.append(f"{expected_context} must select or reject at least one skill")
        unknown_skills = sorted((set(selected) | set(rejected)) - KNOWN_SKILL_IDS)
        if unknown_skills:
            errors.append(f"{expected_context} references unknown skills: {unknown_skills}")
        overlap = sorted(set(selected) & set(rejected))
        if overlap:
            errors.append(f"{expected_context} selects and rejects the same skills: {overlap}")
        if expected.get("profile") != "operations-ui":
            errors.append(f"{expected_context}.profile must be operations-ui")
        scope = expected.get("artifact_scope")
        if scope not in {"proposal", "figma", "implementation", "live"}:
            errors.append(f"{expected_context}.artifact_scope is invalid")
        mode = expected.get("mode")
        if mode not in {"greenfield", "redesign", "audit"}:
            errors.append(f"{expected_context}.mode is invalid")
        requirements = expected.get("requirements")
        if not unique_string_list(requirements):
            errors.append(f"{expected_context}.requirements must be a non-empty unique string array")
            requirements = []
        unknown_requirements = sorted(set(requirements) - KNOWN_REQUIREMENTS)
        if unknown_requirements:
            errors.append(f"{expected_context}.requirements has unknown values: {unknown_requirements}")
        prohibitions = expected.get("prohibitions")
        if not unique_string_list(prohibitions):
            errors.append(f"{expected_context}.prohibitions must be a non-empty unique string array")
            prohibitions = []
        required_gate_run = {
            "proposal": "run-dq0-dq6",
            "figma": "run-dq0-dq7",
            "implementation": "run-dq0-dq7",
            "live": "run-dq0-dq8",
        }.get(scope)
        if required_gate_run and required_gate_run not in requirements:
            errors.append(f"{expected_context}.requirements must include {required_gate_run}")
        if scope in {"implementation", "live"} and "collect-browser-receipts" not in requirements:
            errors.append(f"{expected_context} must require browser receipts for {scope}")
        if scope == "live" and "collect-risk-appropriate-user-evidence" not in requirements:
            errors.append(f"{expected_context} must require risk-appropriate user evidence for live scope")
        if mode == "redesign":
            for requirement in ("inventory-current-behavior", "map-change-contract"):
                if requirement not in requirements:
                    errors.append(f"{expected_context} redesign must require {requirement}")
        if mode == "audit" and "mutate-target" not in prohibitions:
            errors.append(f"{expected_context} audit must prohibit mutate-target")
    return errors


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    subparsers = parser.add_subparsers(dest="command", required=True)
    for name in ("screen-contract", "contract"):
        command = subparsers.add_parser(name)
        command.add_argument("contract", type=Path)
    for name in ("quality-report", "report"):
        command = subparsers.add_parser(name)
        command.add_argument("report", type=Path)
        command.add_argument("contract", type=Path)
    evals = subparsers.add_parser("evals")
    evals.add_argument("fixture", type=Path)
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    errors: list[str] = []
    if args.command in {"screen-contract", "contract"}:
        contract = load_json(args.contract, errors)
        if not errors:
            errors.extend(
                design_quality.validate_contract(
                    contract, args.contract.resolve().parent
                )
            )
            if isinstance(contract, dict) and contract.get("profile") != "operations-ui":
                errors.append("profile must be operations-ui")
    elif args.command in {"quality-report", "report"}:
        report = load_json(args.report, errors)
        contract = load_json(args.contract, errors)
        if not errors:
            errors.extend(
                design_quality.validate_contract(
                    contract, args.contract.resolve().parent
                )
            )
        if not errors:
            errors.extend(
                design_quality.validate_report(
                    report,
                    contract,
                    args.report.resolve().parent,
                    args.contract.resolve().parent,
                )
            )
            if isinstance(contract, dict) and contract.get("profile") != "operations-ui":
                errors.append("contract profile must be operations-ui")
            if isinstance(report, dict) and report.get("profile") != "operations-ui":
                errors.append("report profile must be operations-ui")
            errors.extend(validate_runtime_files(report, args.report))
    else:
        payload = load_json(args.fixture, errors)
        if not errors:
            errors.extend(validate_evals(payload))

    if errors:
        print("Validation failed:")
        for error in errors:
            print(f"- {error}")
        raise SystemExit(1)
    print("Validation passed.")


if __name__ == "__main__":
    main()
