#!/usr/bin/env python3
"""Validate the Madia Designer public-video research catalog and promotion gates."""

from __future__ import annotations

import argparse
import json
import math
import re
from urllib.parse import parse_qs, urlparse
from datetime import datetime
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[1]
SOURCE_MANIFEST_PATH = ROOT / "shared" / "design-quality" / "madia-source-manifest.json"
SOURCE_MANIFEST = json.loads(SOURCE_MANIFEST_PATH.read_text(encoding="utf-8"))
CANONICAL_CHANNEL = SOURCE_MANIFEST["channel"]
CANONICAL_PLAYLISTS = SOURCE_MANIFEST["playlists"]
CANONICAL_DISCOVERY_SOURCES = [
    f"uploads-playlist:{CANONICAL_PLAYLISTS['uploads']}",
    *[
        f"playlist:{name}:{playlist_id}"
        for name, playlist_id in CANONICAL_PLAYLISTS.items()
        if name != "uploads"
    ],
    f"channel-feed:{CANONICAL_CHANNEL['id']}",
]
TOP_LEVEL_FIELDS = {
    "schema_version",
    "as_of",
    "channel",
    "scope",
    "source_policy",
    "copyright",
    "inventory",
    "reliability",
    "videos",
    "principles",
    "quality_gates",
}
VIDEO_FIELDS = {
    "video_id",
    "title",
    "url",
    "published_at",
    "content_type",
    "playlist_ids",
    "status",
    "exclusion_reason",
    "blocking_reason",
    "duplicate_of",
    "evidence_units",
}
EVIDENCE_FIELDS = {
    "id",
    "project_id",
    "timestamp_start",
    "timestamp_end",
    "problem",
    "action",
    "rationale",
    "visible_effect",
    "user_task",
    "decision_stage",
    "evidence_kind",
    "principle_candidate_ids",
    "confidence",
    "source_locator",
}
PRINCIPLE_FIELDS = {
    "id",
    "label",
    "tier",
    "occurrence_ids",
    "independent_projects",
    "external_sources",
    "validation_status",
    "behavior_fixture",
    "trigger",
    "inspect",
    "decide",
    "act",
    "verify",
    "exceptions",
}
EXTERNAL_SOURCE_FIELDS = {"id", "title", "url", "source_type"}
BEHAVIOR_FIXTURE_FIELDS = {
    "fixture_id",
    "run_id",
    "artifact_revision",
    "status",
    "expected",
    "must_not",
    "observed",
    "evidence",
}
QUALITY_GATE_FIELDS = {"id", "status", "evidence"}
GATE_IDS = [f"M{index}" for index in range(9)]
GATE_STATUSES = {
    "passed",
    "failed",
    "blocked",
    "inconclusive",
    "not_run",
    "accepted_risk",
}
VIDEO_STATUSES = {"analyzed", "excluded", "blocked", "pending"}
VIDEO_ID_RE = re.compile(r"^[A-Za-z0-9_-]{11}$")
CODER_EVIDENCE_FIELDS = {
    "schema_version",
    "phase",
    "coders",
    "population_size",
    "records",
}
CODER_RECORD_FIELDS = {"unit_id", "ratings"}
CODER_DIMENSIONS = {"relevance", "decision_stage", "evidence_kind"}


def non_empty_string(value: Any) -> bool:
    return isinstance(value, str) and bool(value.strip())


def choice(value: Any, allowed: set[str]) -> bool:
    return isinstance(value, str) and value in allowed


def safe_string_set(value: Any) -> set[str]:
    if not isinstance(value, list):
        return set()
    return {item for item in value if non_empty_string(item)}


def safe_list_length(value: Any) -> int:
    return len(value) if isinstance(value, list) else 0


def safe_list(value: Any) -> list[Any]:
    return value if isinstance(value, list) else []


def unique_string_list(value: Any, *, allow_empty: bool = False) -> bool:
    return (
        isinstance(value, list)
        and (allow_empty or bool(value))
        and all(non_empty_string(item) for item in value)
        and len(value) == len(set(value))
    )


def finite_number(value: Any) -> bool:
    if not isinstance(value, (int, float)) or isinstance(value, bool):
        return False
    try:
        return math.isfinite(value)
    except OverflowError:
        return False


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


def validate_evidence_files(
    values: Any,
    context: str,
    catalog_directory: Path | None,
    errors: list[str],
) -> None:
    if not isinstance(values, list):
        return
    for index, value in enumerate(values):
        item_context = f"{context}[{index}]"
        if not relative_path(value):
            errors.append(f"{item_context} must be a relative path without traversal")
            continue
        if catalog_directory is None:
            continue
        try:
            base = catalog_directory.resolve()
            resolved = (base / value).resolve(strict=True)
            resolved.relative_to(base)
        except (OSError, RuntimeError, ValueError):
            errors.append(f"{item_context} does not identify a file inside the catalog directory: {value}")
            continue
        if not resolved.is_file() or resolved.stat().st_size == 0:
            errors.append(f"{item_context} must identify a non-empty file: {value}")


def resolve_catalog_file(
    value: Any,
    context: str,
    catalog_directory: Path | None,
    errors: list[str],
) -> Path | None:
    if not relative_path(value):
        errors.append(f"{context} must be a relative path without traversal")
        return None
    if catalog_directory is None:
        errors.append(f"{context} cannot be checked without a catalog directory")
        return None
    try:
        base = catalog_directory.resolve()
        resolved = (base / value).resolve(strict=True)
        resolved.relative_to(base)
    except (OSError, RuntimeError, ValueError):
        errors.append(f"{context} does not identify a file inside the catalog directory: {value}")
        return None
    if not resolved.is_file() or resolved.stat().st_size == 0:
        errors.append(f"{context} must identify a non-empty file: {value}")
        return None
    return resolved


def cohen_kappa(first: list[str], second: list[str]) -> float | None:
    if not first or len(first) != len(second):
        return None
    total = len(first)
    observed_agreement = sum(left == right for left, right in zip(first, second)) / total
    labels = set(first) | set(second)
    expected_agreement = sum(
        (first.count(label) / total) * (second.count(label) / total)
        for label in labels
    )
    if math.isclose(expected_agreement, 1.0, abs_tol=1e-12):
        return None
    return (observed_agreement - expected_agreement) / (1 - expected_agreement)


def load_coder_evidence(
    values: Any,
    phase: str,
    catalog_directory: Path | None,
    sampling_unit_ids: set[str],
    expected_population_size: int,
    errors: list[str],
) -> dict[str, Any] | None:
    context = f"reliability.{phase}_evidence"
    if not unique_string_list(values):
        errors.append(f"{context} must identify structured coder evidence files")
        return None
    expected_coders: list[str] | None = None
    declared_population: int | None = None
    records: list[dict[str, Any]] = []
    seen_units: set[str] = set()
    for index, relative in enumerate(values):
        file_context = f"{context}[{index}]"
        path = resolve_catalog_file(relative, file_context, catalog_directory, errors)
        if path is None:
            continue
        try:
            evidence = json.loads(path.read_text(encoding="utf-8"))
        except (OSError, UnicodeDecodeError, json.JSONDecodeError) as error:
            errors.append(f"{file_context} must be structured coder evidence JSON: {error}")
            continue
        if not isinstance(evidence, dict):
            errors.append(f"{file_context} coder evidence must be a JSON object")
            continue
        reject_unknown_fields(evidence, CODER_EVIDENCE_FIELDS, file_context, errors)
        require_fields(evidence, CODER_EVIDENCE_FIELDS, file_context, errors)
        if evidence.get("schema_version") != "madia-coder-evidence-v1":
            errors.append(f"{file_context}.schema_version must be madia-coder-evidence-v1")
        if evidence.get("phase") != phase:
            errors.append(f"{file_context}.phase must be {phase}")
        coders = evidence.get("coders")
        if not unique_string_list(coders) or len(coders) != 2:
            errors.append(f"{file_context}.coders must contain exactly two unique coder ids")
            continue
        population = evidence.get("population_size")
        if not isinstance(population, int) or isinstance(population, bool) or population < 1:
            errors.append(f"{file_context}.population_size must be a positive integer")
            continue
        if population != expected_population_size:
            errors.append(
                f"{file_context}.population_size must equal the catalog {phase} population "
                f"({expected_population_size})"
            )
        if expected_coders is None:
            expected_coders = coders
            declared_population = population
        elif coders != expected_coders or population != declared_population:
            errors.append(
                f"{file_context} must use the same coders and population_size as other {phase} files"
            )
            continue
        raw_records = evidence.get("records")
        if not isinstance(raw_records, list) or not raw_records:
            errors.append(f"{file_context}.records must be a non-empty array")
            continue
        for record_index, record in enumerate(raw_records):
            record_context = f"{file_context}.records[{record_index}]"
            if not isinstance(record, dict):
                errors.append(f"{record_context} must be an object")
                continue
            reject_unknown_fields(record, CODER_RECORD_FIELDS, record_context, errors)
            require_fields(record, CODER_RECORD_FIELDS, record_context, errors)
            unit_id = record.get("unit_id")
            if not non_empty_string(unit_id):
                errors.append(f"{record_context}.unit_id must be a non-empty string")
            elif unit_id in seen_units:
                errors.append(f"duplicate coder evidence unit_id: {unit_id}")
            else:
                seen_units.add(unit_id)
                if unit_id not in sampling_unit_ids:
                    errors.append(
                        f"{record_context}.unit_id is outside the catalog sampling population: "
                        f"{unit_id}"
                    )
            ratings = record.get("ratings")
            if not isinstance(ratings, dict) or set(ratings) != CODER_DIMENSIONS:
                errors.append(
                    f"{record_context}.ratings must contain exact dimensions "
                    f"{sorted(CODER_DIMENSIONS)}"
                )
                continue
            valid_record = True
            for dimension in CODER_DIMENSIONS:
                dimension_ratings = ratings.get(dimension)
                if not isinstance(dimension_ratings, dict) or set(dimension_ratings) != set(coders):
                    errors.append(
                        f"{record_context}.ratings.{dimension} must contain both coder ids"
                    )
                    valid_record = False
                    continue
                if not all(non_empty_string(value) for value in dimension_ratings.values()):
                    errors.append(
                        f"{record_context}.ratings.{dimension} values must be non-empty strings"
                    )
                    valid_record = False
            if valid_record and non_empty_string(unit_id):
                records.append(record)

    if expected_coders is None or declared_population is None or not records:
        return None
    if expected_population_size < 1:
        errors.append(f"{context} has no catalog {phase} population to sample")
        return None
    if len(records) > expected_population_size:
        errors.append(
            f"{context} contains {len(records)} records for catalog population_size "
            f"{expected_population_size}"
        )
        return None
    kappas: dict[str, float] = {}
    first_coder, second_coder = expected_coders
    for dimension in sorted(CODER_DIMENSIONS):
        first = [record["ratings"][dimension][first_coder] for record in records]
        second = [record["ratings"][dimension][second_coder] for record in records]
        value = cohen_kappa(first, second)
        if value is None:
            errors.append(
                f"{context} cannot compute Cohen's kappa for {dimension}; ratings need variation"
            )
        else:
            kappas[dimension] = value
    if set(kappas) != CODER_DIMENSIONS:
        return None
    return {
        "record_count": len(records),
        "population_size": expected_population_size,
        "minimum_kappa": min(kappas.values()),
        "kappas": kappas,
    }


def verifiable_https_url(value: Any) -> bool:
    if not non_empty_string(value):
        return False
    try:
        parsed = urlparse(value)
    except ValueError:
        return False
    host = (parsed.hostname or "").casefold()
    return (
        parsed.scheme == "https"
        and bool(host)
        and "." in host
        and not host.endswith(".invalid")
        and host not in {"localhost", "127.0.0.1"}
    )


def timestamp(value: Any) -> bool:
    if not non_empty_string(value):
        return False
    try:
        datetime.fromisoformat(value.replace("Z", "+00:00"))
    except ValueError:
        return False
    return True


def youtube_video_id(value: Any) -> str | None:
    if not non_empty_string(value):
        return None
    try:
        parsed = urlparse(value)
    except ValueError:
        return None
    if parsed.scheme != "https":
        return None
    host = (parsed.hostname or "").casefold()
    if host == "youtu.be":
        candidate = parsed.path.strip("/").split("/", 1)[0]
        return candidate if VIDEO_ID_RE.fullmatch(candidate) else None
    if host not in {"youtube.com", "www.youtube.com", "m.youtube.com"}:
        return None
    if parsed.path == "/watch":
        values = parse_qs(parsed.query).get("v", [])
        return values[0] if len(values) == 1 and VIDEO_ID_RE.fullmatch(values[0]) else None
    parts = [part for part in parsed.path.split("/") if part]
    if len(parts) == 2 and parts[0] in {"shorts", "live", "embed"} and VIDEO_ID_RE.fullmatch(parts[1]):
        return parts[1]
    return None


def reject_unknown_fields(value: dict[str, Any], allowed: set[str], context: str, errors: list[str]) -> None:
    unknown = sorted(set(value) - allowed)
    if unknown:
        errors.append(f"{context} has unknown fields: {unknown}")


def require_fields(value: dict[str, Any], required: set[str], context: str, errors: list[str]) -> None:
    missing = sorted(required - set(value))
    if missing:
        errors.append(f"{context} missing required fields: {missing}")


def validate_catalog(payload: Any, catalog_directory: Path | None = None) -> list[str]:
    errors: list[str] = []
    if not isinstance(payload, dict):
        return ["catalog must be a JSON object"]
    reject_unknown_fields(payload, TOP_LEVEL_FIELDS, "catalog", errors)
    require_fields(payload, TOP_LEVEL_FIELDS, "catalog", errors)
    if payload.get("schema_version") != "madia-design-practice-catalog-v1":
        errors.append("schema_version must be madia-design-practice-catalog-v1")
    as_of = payload.get("as_of")
    if not non_empty_string(as_of):
        errors.append("as_of must be a non-empty date string")
    else:
        try:
            datetime.fromisoformat(as_of)
        except ValueError:
            errors.append("as_of must use ISO date format")
    if not non_empty_string(payload.get("scope")):
        errors.append("scope must be a non-empty string")

    channel = payload.get("channel")
    if not isinstance(channel, dict):
        errors.append("channel must be an object")
    else:
        reject_unknown_fields(channel, {"id", "title", "url"}, "channel", errors)
        require_fields(channel, {"id", "title", "url"}, "channel", errors)
        if channel != CANONICAL_CHANNEL:
            errors.append("channel must match the canonical source manifest")

    source_policy = payload.get("source_policy")
    expected_source_policy = {
        "public_only": True,
        "paid_or_membership_excluded": True,
        "metadata_is_not_principle_evidence": True,
    }
    if source_policy != expected_source_policy:
        errors.append("source_policy must keep public-only, paid exclusion, and metadata evidence limits")
    copyright_policy = payload.get("copyright")
    if not isinstance(copyright_policy, dict):
        errors.append("copyright must be an object")
    else:
        reject_unknown_fields(
            copyright_policy, {"stores_full_transcripts", "stores_media"}, "copyright", errors
        )
        if copyright_policy.get("stores_full_transcripts") is not False:
            errors.append("catalog must not store full transcripts")
        if copyright_policy.get("stores_media") is not False:
            errors.append("catalog must not store copied video or image media")

    videos = payload.get("videos")
    if not isinstance(videos, list):
        errors.append("videos must be an array")
        videos = []
    video_ids: set[str] = set()
    evidence_by_id: dict[str, dict[str, Any]] = {}
    evidence_video_ids: dict[str, str] = {}
    status_counts = {status: 0 for status in VIDEO_STATUSES}
    pending_video_ids: list[str] = []
    for index, video in enumerate(videos):
        context = f"videos[{index}]"
        if not isinstance(video, dict):
            errors.append(f"{context} must be an object")
            continue
        reject_unknown_fields(video, VIDEO_FIELDS, context, errors)
        require_fields(video, VIDEO_FIELDS, context, errors)
        video_id = video.get("video_id")
        if not isinstance(video_id, str) or not VIDEO_ID_RE.fullmatch(video_id):
            errors.append(f"{context}.video_id must be an 11-character YouTube video id")
        elif video_id in video_ids:
            errors.append(f"duplicate video_id: {video_id}")
        else:
            video_ids.add(video_id)
        if not non_empty_string(video.get("title")):
            errors.append(f"{context}.title must be a non-empty string")
        if youtube_video_id(video.get("url")) != video_id:
            errors.append(f"{context}.url must identify its video_id")
        if video.get("published_at") is not None and not timestamp(video.get("published_at")):
            errors.append(f"{context}.published_at must be null or an ISO-8601 date-time")
        if not choice(video.get("content_type"), {"long-form", "short", "live", "unknown"}):
            errors.append(f"{context}.content_type is invalid")
        if not unique_string_list(video.get("playlist_ids"), allow_empty=True):
            errors.append(f"{context}.playlist_ids must be a unique string array")
        status = video.get("status")
        if not choice(status, VIDEO_STATUSES):
            errors.append(f"{context}.status is invalid")
        else:
            status_counts[status] += 1
            if status == "pending":
                pending_video_ids.append(video_id)
        units = video.get("evidence_units")
        if not isinstance(units, list):
            errors.append(f"{context}.evidence_units must be an array")
            units = []
        if status == "analyzed" and not units:
            errors.append(f"{context} is analyzed but has no timestamped evidence_units")
        if status != "analyzed" and units:
            errors.append(f"{context} may contain evidence_units only when analyzed")
        if status == "excluded" and not non_empty_string(video.get("exclusion_reason")):
            errors.append(f"{context}.exclusion_reason is required for excluded videos")
        if status != "excluded" and video.get("exclusion_reason") is not None:
            errors.append(f"{context}.exclusion_reason is only valid for excluded videos")
        if status == "blocked" and not non_empty_string(video.get("blocking_reason")):
            errors.append(f"{context}.blocking_reason is required for blocked videos")
        if status != "blocked" and video.get("blocking_reason") is not None:
            errors.append(f"{context}.blocking_reason is only valid for blocked videos")
        duplicate_of = video.get("duplicate_of")
        if duplicate_of is not None and not VIDEO_ID_RE.fullmatch(str(duplicate_of)):
            errors.append(f"{context}.duplicate_of must be null or a YouTube video id")
        unit_ids: set[str] = set()
        for unit_index, unit in enumerate(units):
            unit_context = f"{context}.evidence_units[{unit_index}]"
            if not isinstance(unit, dict):
                errors.append(f"{unit_context} must be an object")
                continue
            reject_unknown_fields(unit, EVIDENCE_FIELDS, unit_context, errors)
            require_fields(unit, EVIDENCE_FIELDS, unit_context, errors)
            unit_id = unit.get("id")
            if not non_empty_string(unit_id):
                errors.append(f"{unit_context}.id must be a non-empty string")
            elif unit_id in unit_ids or unit_id in evidence_by_id:
                errors.append(f"duplicate evidence unit id: {unit_id}")
            else:
                unit_ids.add(unit_id)
                evidence_by_id[unit_id] = unit
                if isinstance(video_id, str):
                    evidence_video_ids[unit_id] = video_id
            start = unit.get("timestamp_start")
            end = unit.get("timestamp_end")
            if not finite_number(start) or start < 0:
                errors.append(f"{unit_context}.timestamp_start must be a non-negative number")
            if not finite_number(end) or not finite_number(start) or end <= start:
                errors.append(f"{unit_context}.timestamp_end must be greater than timestamp_start")
            for field in (
                "project_id", "problem", "action", "rationale", "visible_effect", "user_task",
                "decision_stage", "source_locator",
            ):
                if not non_empty_string(unit.get(field)):
                    errors.append(f"{unit_context}.{field} must be a non-empty string")
            if youtube_video_id(unit.get("source_locator")) != video_id:
                errors.append(f"{unit_context}.source_locator must identify the source video")
            if not choice(unit.get("evidence_kind"), {
                "verbalized", "demonstrated", "inferred", "metadata_only"
            }):
                errors.append(f"{unit_context}.evidence_kind is invalid")
            if not choice(unit.get("confidence"), {"high", "medium", "low"}):
                errors.append(f"{unit_context}.confidence is invalid")
            if not unique_string_list(unit.get("principle_candidate_ids"), allow_empty=True):
                errors.append(f"{unit_context}.principle_candidate_ids must be a unique string array")

    for index, video in enumerate(videos):
        if not isinstance(video, dict):
            continue
        duplicate_of = video.get("duplicate_of")
        if duplicate_of is not None:
            if (
                not isinstance(duplicate_of, str)
                or duplicate_of == video.get("video_id")
                or duplicate_of not in video_ids
            ):
                errors.append(f"videos[{index}].duplicate_of must reference a different catalog video")
            if video.get("status") != "excluded":
                errors.append(f"videos[{index}] duplicates must be excluded to avoid double counting")

    inventory = payload.get("inventory")
    if not isinstance(inventory, dict):
        errors.append("inventory must be an object")
        inventory = {}
    else:
        allowed = {
            "discovery_complete", "discovery_sources", "discovered_unique_videos",
            "analyzed", "excluded", "blocked", "pending", "corpus_coverage",
        }
        reject_unknown_fields(inventory, allowed, "inventory", errors)
        require_fields(inventory, allowed, "inventory", errors)
    if not isinstance(inventory.get("discovery_complete"), bool):
        errors.append("inventory.discovery_complete must be boolean")
    if not unique_string_list(inventory.get("discovery_sources")):
        errors.append("inventory.discovery_sources must be a non-empty unique string array")
    elif inventory.get("discovery_sources") != CANONICAL_DISCOVERY_SOURCES:
        errors.append("inventory.discovery_sources must match the canonical source manifest")
    expected_count = len(video_ids)
    if inventory.get("discovered_unique_videos") != expected_count:
        errors.append("inventory.discovered_unique_videos must equal unique videos length")
    for status in VIDEO_STATUSES:
        if inventory.get(status) != status_counts[status]:
            errors.append(f"inventory.{status} must equal the number of {status} videos")
    covered = status_counts["analyzed"] + status_counts["excluded"] + status_counts["blocked"]
    expected_coverage = covered / expected_count if expected_count else 0.0
    actual_coverage = inventory.get("corpus_coverage")
    if not finite_number(actual_coverage) or not math.isclose(actual_coverage, expected_coverage, abs_tol=1e-9):
        errors.append(f"inventory.corpus_coverage must equal {expected_coverage}")

    principles = payload.get("principles")
    if not isinstance(principles, list):
        errors.append("principles must be an array")
        principles = []
    principle_ids: set[str] = set()
    promoted_principles: list[dict[str, Any]] = []
    for index, principle in enumerate(principles):
        context = f"principles[{index}]"
        if not isinstance(principle, dict):
            errors.append(f"{context} must be an object")
            continue
        reject_unknown_fields(principle, PRINCIPLE_FIELDS, context, errors)
        require_fields(principle, PRINCIPLE_FIELDS, context, errors)
        principle_id = principle.get("id")
        if not non_empty_string(principle_id):
            errors.append(f"{context}.id must be a non-empty string")
        elif principle_id in principle_ids:
            errors.append(f"duplicate principle id: {principle_id}")
        else:
            principle_ids.add(principle_id)
        if not non_empty_string(principle.get("label")):
            errors.append(f"{context}.label must be a non-empty string")
        tier = principle.get("tier")
        if not choice(tier, {"P0", "P1", "P2", "P3"}):
            errors.append(f"{context}.tier is invalid")
            continue
        occurrences = principle.get("occurrence_ids")
        if not unique_string_list(occurrences):
            errors.append(f"{context}.occurrence_ids must be a non-empty unique string array")
            occurrences = []
        unknown_occurrences = sorted(safe_string_set(occurrences) - set(evidence_by_id))
        if unknown_occurrences:
            errors.append(f"{context} references unknown occurrence ids: {unknown_occurrences}")
        linked_occurrences = [
            item
            for item in occurrences
            if item in evidence_by_id
        ]
        for occurrence_id in linked_occurrences:
            if (
                non_empty_string(principle_id)
                and principle_id
                not in safe_string_set(
                    evidence_by_id[occurrence_id].get("principle_candidate_ids")
                )
            ):
                errors.append(
                    f"{context} occurrence {occurrence_id} must list the principle in "
                    "principle_candidate_ids"
                )
        direct_occurrence_ids = [
            item
            for item in linked_occurrences
            if choice(
                evidence_by_id[item].get("evidence_kind"),
                {"verbalized", "demonstrated"},
            )
        ]
        direct_occurrences = [evidence_by_id[item] for item in direct_occurrence_ids]
        independent_recurrences = {
            (evidence_video_ids.get(item), evidence_by_id[item].get("project_id"))
            for item in direct_occurrence_ids
            if non_empty_string(evidence_video_ids.get(item))
            and non_empty_string(evidence_by_id[item].get("project_id"))
        }
        projects = principle.get("independent_projects")
        if not isinstance(projects, int) or isinstance(projects, bool) or projects < 1:
            errors.append(f"{context}.independent_projects must be a positive integer")
        observed_projects = {
            item.get("project_id")
            for item in direct_occurrences
            if non_empty_string(item.get("project_id"))
        }
        if isinstance(projects, int) and not isinstance(projects, bool) and projects != len(observed_projects):
            errors.append(
                f"{context}.independent_projects must equal direct evidence project ids ({len(observed_projects)})"
            )
        external_sources = principle.get("external_sources")
        if not isinstance(external_sources, list):
            errors.append(f"{context}.external_sources must be an array")
            external_sources = []
        external_source_ids: set[str] = set()
        for source_index, source in enumerate(external_sources):
            source_context = f"{context}.external_sources[{source_index}]"
            if not isinstance(source, dict):
                errors.append(f"{source_context} must be a verifiable https source record")
                continue
            reject_unknown_fields(source, EXTERNAL_SOURCE_FIELDS, source_context, errors)
            require_fields(source, EXTERNAL_SOURCE_FIELDS, source_context, errors)
            source_id = source.get("id")
            if not non_empty_string(source_id):
                errors.append(f"{source_context}.id must be a non-empty string")
            elif source_id in external_source_ids:
                errors.append(f"duplicate external source id: {source_id}")
            else:
                external_source_ids.add(source_id)
            if not non_empty_string(source.get("title")):
                errors.append(f"{source_context}.title must be a non-empty string")
            if not verifiable_https_url(source.get("url")):
                errors.append(f"{source_context}.url must be a verifiable https URL")
            source_video_id = youtube_video_id(source.get("url"))
            if source_video_id in video_ids:
                errors.append(
                    f"{source_context}.url must be independent from catalog video evidence"
                )
            if not choice(source.get("source_type"), {"standard", "research", "product"}):
                errors.append(f"{source_context}.source_type is invalid")
        if not choice(principle.get("validation_status"), GATE_STATUSES):
            errors.append(f"{context}.validation_status is invalid")
        if tier in {"P1", "P2", "P3"}:
            promoted_principles.append(principle)
            if len(occurrences) < 3:
                errors.append(f"{context} {tier} requires at least three nonduplicate occurrences")
            if not isinstance(projects, int) or projects < 2:
                errors.append(f"{context} {tier} requires at least two projects")
            if len(direct_occurrences) < 3:
                errors.append(f"{context} {tier} requires direct observation, not inferred or metadata-only evidence")
            if len(independent_recurrences) < 3:
                errors.append(
                    f"{context} {tier} requires at least three independent recurrence cases "
                    "after deduplicating the same video and project"
                )
            if len(observed_projects) < 2:
                errors.append(f"{context} {tier} requires direct evidence from at least two project ids")
        if tier in {"P2", "P3"} and not principle.get("external_sources"):
            errors.append(f"{context} {tier} requires external_sources")
        operational_fields = ("trigger", "inspect", "decide", "act", "verify")
        for field in operational_fields:
            if tier == "P3" and not non_empty_string(principle.get(field)):
                errors.append(f"{context} P3 requires non-empty {field}")
        if tier == "P3":
            if principle.get("validation_status") != "passed":
                errors.append(f"{context} P3 requires passed behavior validation")
            if not unique_string_list(principle.get("exceptions")):
                errors.append(f"{context} P3 requires at least one exception")
        fixture = principle.get("behavior_fixture")
        if fixture is None:
            if tier == "P3":
                errors.append(f"{context} P3 requires a behavior_fixture execution receipt")
        elif not isinstance(fixture, dict):
            errors.append(f"{context}.behavior_fixture must be an object or null")
        else:
            fixture_context = f"{context}.behavior_fixture"
            reject_unknown_fields(fixture, BEHAVIOR_FIXTURE_FIELDS, fixture_context, errors)
            require_fields(fixture, BEHAVIOR_FIXTURE_FIELDS, fixture_context, errors)
            for field in ("fixture_id", "run_id", "artifact_revision"):
                if not non_empty_string(fixture.get(field)):
                    errors.append(f"{fixture_context}.{field} must be a non-empty string")
            if not choice(fixture.get("status"), GATE_STATUSES):
                errors.append(f"{fixture_context}.status is invalid")
            if fixture.get("status") != principle.get("validation_status"):
                errors.append(f"{fixture_context}.status must match validation_status")
            for field in ("expected", "must_not", "observed", "evidence"):
                if not unique_string_list(fixture.get(field)):
                    errors.append(f"{fixture_context}.{field} must be a non-empty unique string array")
            expected = safe_string_set(fixture.get("expected"))
            prohibited = safe_string_set(fixture.get("must_not"))
            observed = safe_string_set(fixture.get("observed"))
            if fixture.get("status") == "passed":
                missing_expected = sorted(expected - observed)
                observed_prohibited = sorted(prohibited & observed)
                if missing_expected:
                    errors.append(
                        f"{fixture_context} is missing expected observations: {missing_expected}"
                    )
                if observed_prohibited:
                    errors.append(
                        f"{fixture_context} contains prohibited observations: {observed_prohibited}"
                    )
            validate_evidence_files(
                fixture.get("evidence"),
                f"{fixture_context}.evidence",
                catalog_directory,
                errors,
            )

    gates = payload.get("quality_gates")
    if not isinstance(gates, list) or len(gates) != len(GATE_IDS):
        errors.append(f"quality_gates must contain exact order {GATE_IDS}")
        gates = []
    actual_gate_ids = [gate.get("id") if isinstance(gate, dict) else None for gate in gates]
    if gates and actual_gate_ids != GATE_IDS:
        errors.append(f"quality_gates must use exact order {GATE_IDS}")
    gate_status: dict[str, str] = {}
    for index, gate in enumerate(gates):
        context = f"quality_gates[{index}]"
        if not isinstance(gate, dict):
            errors.append(f"{context} must be an object")
            continue
        reject_unknown_fields(gate, QUALITY_GATE_FIELDS, context, errors)
        require_fields(gate, QUALITY_GATE_FIELDS, context, errors)
        status = gate.get("status")
        if not choice(status, GATE_STATUSES):
            errors.append(f"{context}.status is invalid")
        if non_empty_string(gate.get("id")):
            gate_status[gate["id"]] = status
        if not unique_string_list(gate.get("evidence"), allow_empty=status != "passed"):
            errors.append(f"{context}.evidence must match its status")
        validate_evidence_files(
            gate.get("evidence"), f"{context}.evidence", catalog_directory, errors
        )

    reliability = payload.get("reliability")
    if not isinstance(reliability, dict):
        errors.append("reliability must be an object")
        reliability = {}
    else:
        fields = {
            "pilot_sample_size", "pilot_kappa", "pilot_evidence",
            "production_double_coded_ratio", "production_kappa", "production_evidence",
        }
        reject_unknown_fields(reliability, fields, "reliability", errors)
        require_fields(reliability, fields, "reliability", errors)
        for field in ("pilot_evidence", "production_evidence"):
            if not unique_string_list(reliability.get(field), allow_empty=True):
                errors.append(f"reliability.{field} must be a unique string array")
            validate_evidence_files(
                reliability.get(field), f"reliability.{field}", catalog_directory, errors
            )
        sample = reliability.get("pilot_sample_size")
        if sample is not None and (
            not isinstance(sample, int) or isinstance(sample, bool) or sample < 1
        ):
            errors.append("reliability.pilot_sample_size must be null or a positive integer")
        for field in (
            "pilot_kappa",
            "production_double_coded_ratio",
            "production_kappa",
        ):
            value = reliability.get(field)
            if value is not None and (
                not finite_number(value) or not 0 <= value <= 1
            ):
                errors.append(f"reliability.{field} must be null or a finite number between 0 and 1")

    for evidence_id, unit in evidence_by_id.items():
        unknown_candidates = sorted(
            safe_string_set(unit.get("principle_candidate_ids")) - principle_ids
        )
        if unknown_candidates:
            errors.append(
                f"evidence unit {evidence_id} references unknown principle candidate ids: {unknown_candidates}"
            )

    required_milestones = {
        "P1": {f"M{index}" for index in range(5)},
        "P2": {f"M{index}" for index in range(6)},
        "P3": set(GATE_IDS),
    }
    for index, principle in enumerate(principles):
        if not isinstance(principle, dict):
            continue
        tier = principle.get("tier")
        required = required_milestones.get(tier, set()) if isinstance(tier, str) else set()
        missing = sorted(gate_id for gate_id in required if gate_status.get(gate_id) != "passed")
        if missing:
            errors.append(
                f"principles[{index}] {tier} requires passed research milestones: {missing}"
            )

    if gate_status.get("M0") == "passed":
        if not inventory.get("discovery_complete") or pending_video_ids or expected_coverage != 1.0:
            errors.append("M0 cannot pass until discovery is complete, pending is zero, and corpus coverage is 100%")
    if gate_status.get("M1") == "passed":
        if any(
            video.get("status") == "analyzed" and not video.get("evidence_units")
            for video in videos if isinstance(video, dict)
        ):
            errors.append("M1 cannot pass without timestamped evidence for every analyzed video")
    if gate_status.get("M2") == "passed":
        if any(
            unit.get("evidence_kind") == "metadata_only"
            for unit in evidence_by_id.values()
        ):
            errors.append("M2 cannot pass when analyzed evidence is metadata_only")
    if gate_status.get("M3") == "passed":
        sample = reliability.get("pilot_sample_size")
        pilot = reliability.get("pilot_kappa")
        ratio = reliability.get("production_double_coded_ratio")
        production = reliability.get("production_kappa")
        if not isinstance(sample, int) or isinstance(sample, bool) or sample < 20:
            errors.append("M3 requires pilot_sample_size >= 20")
        if not finite_number(pilot) or not 0.70 <= pilot <= 1:
            errors.append("M3 requires pilot_kappa between 0.70 and 1")
        if not finite_number(ratio) or not 0.20 <= ratio <= 1:
            errors.append("M3 requires production_double_coded_ratio between 0.20 and 1")
        if not finite_number(production) or not 0.75 <= production <= 1:
            errors.append("M3 requires production_kappa between 0.75 and 1")
        if not reliability.get("pilot_evidence") or not reliability.get("production_evidence"):
            errors.append("M3 requires pilot and production coder evidence artifacts")
        pilot_summary = load_coder_evidence(
            reliability.get("pilot_evidence"),
            "pilot",
            catalog_directory,
            set(video_ids),
            len(video_ids),
            errors,
        )
        analyzed_video_ids = {
            video.get("video_id")
            for video in videos
            if isinstance(video, dict)
            and video.get("status") == "analyzed"
            and non_empty_string(video.get("video_id"))
        }
        production_summary = load_coder_evidence(
            reliability.get("production_evidence"),
            "production",
            catalog_directory,
            analyzed_video_ids,
            len(analyzed_video_ids),
            errors,
        )
        if pilot_summary is not None:
            computed_sample = pilot_summary["record_count"]
            computed_kappa = pilot_summary["minimum_kappa"]
            if sample != computed_sample:
                errors.append(
                    "reliability.pilot_sample_size must equal the computed coder evidence "
                    f"record count ({computed_sample})"
                )
            if not finite_number(pilot) or not math.isclose(
                pilot, computed_kappa, abs_tol=1e-9
            ):
                errors.append(
                    "reliability.pilot_kappa must equal the computed minimum dimension kappa "
                    f"({computed_kappa})"
                )
            if computed_sample < 20 or computed_kappa < 0.70:
                errors.append("M3 computed pilot coder evidence does not meet its thresholds")
        if production_summary is not None:
            computed_ratio = (
                production_summary["record_count"]
                / production_summary["population_size"]
            )
            computed_kappa = production_summary["minimum_kappa"]
            if not finite_number(ratio) or not math.isclose(
                ratio, computed_ratio, abs_tol=1e-9
            ):
                errors.append(
                    "reliability.production_double_coded_ratio must equal the computed coder "
                    f"evidence ratio ({computed_ratio})"
                )
            if not finite_number(production) or not math.isclose(
                production, computed_kappa, abs_tol=1e-9
            ):
                errors.append(
                    "reliability.production_kappa must equal the computed minimum dimension kappa "
                    f"({computed_kappa})"
                )
            if computed_ratio < 0.20 or computed_kappa < 0.75:
                errors.append("M3 computed production coder evidence does not meet its thresholds")
    if gate_status.get("M4") == "passed" and any(
        safe_list_length(item.get("occurrence_ids")) < 3
        or not isinstance(item.get("independent_projects"), int)
        or isinstance(item.get("independent_projects"), bool)
        or item.get("independent_projects") < 2
        for item in promoted_principles
    ):
        errors.append("M4 cannot pass while promoted recurrence requirements fail")
    if gate_status.get("M5") == "passed" and any(
        choice(item.get("tier"), {"P2", "P3"}) and not item.get("external_sources")
        for item in principles if isinstance(item, dict)
    ):
        errors.append("M5 cannot pass while P2/P3 triangulation is missing")
    if gate_status.get("M6") == "passed" and any(
        item.get("tier") == "P3"
        and any(not non_empty_string(item.get(field)) for field in ("trigger", "inspect", "decide", "act", "verify"))
        for item in principles if isinstance(item, dict)
    ):
        errors.append("M6 cannot pass while P3 operational fields are missing")
    if gate_status.get("M7") == "passed" and any(
        item.get("tier") == "P3" and item.get("validation_status") != "passed"
        for item in principles if isinstance(item, dict)
    ):
        errors.append("M7 cannot pass while P3 behavior validation is not passed")
    if gate_status.get("M8") == "passed" and any(
        choice(item.get("tier"), {"P1", "P2", "P3"})
        and all(
            choice(
                evidence_by_id.get(occurrence_id, {}).get("evidence_kind"),
                {"inferred", "metadata_only"},
            )
            for occurrence_id in safe_string_set(item.get("occurrence_ids"))
        )
        for item in principles if isinstance(item, dict)
    ):
        errors.append("M8 cannot pass when promoted principles misrepresent inference as direct evidence")
    return errors


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("catalog", type=Path)
    args = parser.parse_args()
    try:
        payload = json.loads(args.catalog.read_text(encoding="utf-8"))
    except OSError as error:
        print(f"ERROR: unable to read {args.catalog}: {error}")
        raise SystemExit(1)
    except json.JSONDecodeError as error:
        print(f"ERROR: invalid JSON: {error}")
        raise SystemExit(1)
    errors = validate_catalog(payload, args.catalog.resolve().parent)
    if errors:
        for error in errors:
            print(f"ERROR: {error}")
        raise SystemExit(1)
    print("OK: madia-design-practice-catalog")


if __name__ == "__main__":
    main()
