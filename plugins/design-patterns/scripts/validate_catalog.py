#!/usr/bin/env python3
"""Validate the design-pattern catalog without third-party dependencies."""

import argparse
import hashlib
import json
from pathlib import Path
import re
import sys
from urllib.parse import urlparse


MATURITY = {
    "indexed",
    "normalized",
    "decision-ready",
    "contextual",
    "superseded",
}
RELATION_TYPES = {
    "alias-of",
    "same-name-different-scope",
    "specializes",
    "generalizes",
    "implements",
    "commonly-composed-with",
    "alternative-to",
    "conflicts-with",
    "supersedes",
}
LEVELS = {
    "code",
    "component",
    "application",
    "architecture",
    "domain",
    "integration",
    "distributed-system",
    "process",
    "test",
    "security",
}
BASE_FIELDS = {
    "id",
    "name",
    "aliases",
    "family",
    "level",
    "maturity",
    "sources",
}
DECISION_FIELDS = {
    "problem",
    "forces",
    "preconditions",
    "contraindications",
    "solution",
    "guarantees",
    "costs",
    "failure_modes",
    "language_realizations",
    "relations",
}
PATTERN_FIELDS = BASE_FIELDS | DECISION_FIELDS | {"source_path"}
FAMILY_DOCUMENT_FIELDS = {"schema_version", "family", "defaults", "patterns"}
FAMILY_METADATA_FIELDS = {"id", "name", "scope"}
OVERLAY_DIRECT_FIELDS = DECISION_FIELDS
OVERLAY_DEFAULT_FIELDS = {"maturity"}
OVERLAY_ENTRY_FIELDS = {"id", "maturity"} | DECISION_FIELDS
DECISION_READY_PER_FAMILY = 3
EXPECTED_TOTAL = 553
EXPECTED_FAMILIES = frozenset(
    {
        "object-oriented",
        "architecture",
        "domain-driven-design",
        "enterprise-application",
        "messaging-integration",
        "microservices",
        "cloud-resilience",
        "distributed-systems",
        "concurrency",
        "workflow",
        "testing",
        "security",
    }
)
EXPECTED_FAMILY_COUNTS = {
    "object-oriented": 23,
    "architecture": 8,
    "domain-driven-design": 45,
    "enterprise-application": 51,
    "messaging-integration": 65,
    "microservices": 53,
    "cloud-resilience": 44,
    "distributed-systems": 30,
    "concurrency": 17,
    "workflow": 126,
    "testing": 68,
    "security": 23,
}
EXPECTED_FAMILY_SNAPSHOTS = {
    "object-oriented": "e29bab7a117b607ab21ebe81bec0c7883216d4596b2b53d8254c3950d97a5fee",
    "architecture": "c5ce50c854e99326f9b202893c67a406815f3c9f02fdf6e55d3dcafb22fb351e",
    "domain-driven-design": "876d532e9ad7b9a9c9ac6aa6426bba8ef9d2429352bf9e04beac9996de7e9e51",
    "enterprise-application": "51ceba6d4380aa34c50f6b8a9be6b6a3878b23cf3f56c3f23fd0676a626533d4",
    "messaging-integration": "c9cbe98e826864a78a4d6c5b12d5238e508162d80b1c7832a3d24542fb515248",
    "microservices": "e66715927ec242489c4449e0c2e2296908f8aaa0a7ed0d81bb421ed5931f9075",
    "cloud-resilience": "6ef11adf358cff125726c8c8219ba4de4c21b888507d3d64cec6060471cd0e5d",
    "distributed-systems": "2197933a60a6b3a6560c05c1563515f373fb0d7b8850a12068b50aacb9e2b5ac",
    "concurrency": "d7674786f8cbd55fb9ced57bd53239dddb3710d0eaa2fc1e2e8eac24b045be35",
    "workflow": "6aa52a169d1b553ae20e4db66df1c767d4dc0813a033b3e90664211d0c0766c7",
    "testing": "30c89a0a99a5c6fe1fcc02e1cae45876e398c94bff4be5c60c860ea9f98ca20e",
    "security": "550ca6f2187f57d2ed35f979ad30fd76d6b2d51c8d1f4518df2ec9a60b1cc720",
}
REQUIRE_SOURCE_MANIFEST = True
EXPECTED_SOURCE_MANIFEST_SHA256 = (
    "de13f71ae7875090e23c11adcd649033948631eedbaec1984d784d67c5779140"
)
ID = re.compile(r"[a-z0-9]+(?:-[a-z0-9]+)*\Z")


class CatalogError(ValueError):
    pass


def load_json(path):
    try:
        with path.open(encoding="utf-8") as stream:
            return json.load(stream)
    except FileNotFoundError as exc:
        raise CatalogError(f"missing file: {path}") from exc
    except json.JSONDecodeError as exc:
        raise CatalogError(f"invalid JSON in {path}: {exc}") from exc


def require_object(value, label):
    if not isinstance(value, dict):
        raise CatalogError(f"{label} must be an object")


def require_string(value, label):
    if not isinstance(value, str) or not value.strip():
        raise CatalogError(f"{label} must be a non-empty string")


def require_string_list(value, label, *, allow_empty=False):
    if not isinstance(value, list) or (not value and not allow_empty):
        raise CatalogError(f"{label} must be a {'possibly empty ' if allow_empty else 'non-empty '}list")
    for item in value:
        require_string(item, f"{label} item")


def reject_unsupported_fields(value, allowed, label):
    unsupported = sorted(set(value) - allowed)
    if unsupported:
        raise CatalogError(
            f"{label} contains unsupported fields: {', '.join(unsupported)}"
        )


def normalize_pattern_name(name):
    return re.sub(r"[^a-z0-9]+", "", name.casefold())


def validate_source(source, label):
    require_object(source, label)
    if not {"title", "url", "type"}.issubset(source) or set(source) - {
        "title",
        "url",
        "type",
        "transport",
    }:
        raise CatalogError(f"{label} contains unsupported or missing source fields")
    require_string(source["title"], f"{label}.title")
    require_string(source["url"], f"{label}.url")
    parsed = urlparse(source["url"])
    if not parsed.netloc or parsed.scheme not in {"http", "https"}:
        raise CatalogError(f"{label}.url must be an absolute HTTP(S) URL")
    if parsed.scheme == "http" and source.get("transport") != "legacy-http":
        raise CatalogError(f"{label} HTTP sources must declare transport=legacy-http")
    if parsed.scheme == "https" and "transport" in source:
        raise CatalogError(f"{label}.transport is only valid for legacy HTTP sources")
    if source["type"] not in {"official", "primary", "secondary"}:
        raise CatalogError(f"{label}.type is invalid: {source['type']}")


def validate_pattern(pattern, family_id, location):
    require_object(pattern, location)
    missing = sorted(BASE_FIELDS - set(pattern))
    if missing:
        raise CatalogError(f"{location} is missing: {', '.join(missing)}")

    pattern_id = pattern["id"]
    require_string(pattern_id, f"{location}.id")
    if not ID.fullmatch(pattern_id):
        raise CatalogError(f"invalid pattern id: {pattern_id}")
    family_prefix = f"{family_id}-"
    if not pattern_id.startswith(family_prefix):
        raise CatalogError(
            f"pattern id {pattern_id} must start with family prefix {family_prefix}"
        )
    require_string(pattern["name"], f"pattern {pattern_id}.name")
    require_string_list(pattern["aliases"], f"pattern {pattern_id}.aliases", allow_empty=True)
    if len(pattern["aliases"]) != len(set(pattern["aliases"])):
        raise CatalogError(f"pattern {pattern_id} has duplicate aliases")
    if pattern["family"] != family_id:
        raise CatalogError(
            f"pattern {pattern_id} declares family {pattern['family']} but is stored in {family_id}"
        )
    if pattern["level"] not in LEVELS:
        raise CatalogError(f"pattern {pattern_id} has invalid level: {pattern['level']}")
    if pattern["maturity"] not in MATURITY:
        raise CatalogError(f"pattern {pattern_id} has invalid maturity: {pattern['maturity']}")
    if not isinstance(pattern["sources"], list) or not pattern["sources"]:
        raise CatalogError(f"pattern {pattern_id}.sources must be a non-empty list")
    for index, source in enumerate(pattern["sources"]):
        validate_source(source, f"pattern {pattern_id}.sources[{index}]")

    if pattern["maturity"] == "decision-ready":
        missing = sorted(DECISION_FIELDS - set(pattern))
        if missing:
            raise CatalogError(
                f"decision-ready pattern {pattern_id} is missing: {', '.join(missing)}"
            )
        for field in ("problem", "solution"):
            require_string(pattern[field], f"pattern {pattern_id}.{field}")
        for field in (
            "forces",
            "preconditions",
            "contraindications",
            "guarantees",
            "costs",
            "failure_modes",
        ):
            require_string_list(pattern[field], f"pattern {pattern_id}.{field}")
        require_object(pattern["language_realizations"], f"pattern {pattern_id}.language_realizations")
        if not pattern["language_realizations"]:
            raise CatalogError(f"pattern {pattern_id}.language_realizations must not be empty")
        for language, realization in pattern["language_realizations"].items():
            require_string(language, f"pattern {pattern_id}.language_realizations key")
            require_string(realization, f"pattern {pattern_id}.language_realizations.{language}")
        if not isinstance(pattern["relations"], list):
            raise CatalogError(f"pattern {pattern_id}.relations must be a list")

    if "relations" in pattern:
        if not isinstance(pattern["relations"], list):
            raise CatalogError(f"pattern {pattern_id}.relations must be a list")
        for index, relation in enumerate(pattern["relations"]):
            require_object(relation, f"pattern {pattern_id}.relations[{index}]")
            if set(relation) != {"type", "target"}:
                raise CatalogError(
                    f"pattern {pattern_id}.relations[{index}] must contain exactly type and target"
                )
            if relation["type"] not in RELATION_TYPES:
                raise CatalogError(
                    f"pattern {pattern_id} has invalid relation type: {relation['type']}"
                )
            require_string(relation["target"], f"pattern {pattern_id}.relations[{index}].target")

    return pattern_id


def validate_source_manifest(catalog, index, patterns_by_family):
    manifest_path = catalog / "source-manifest.json"
    if not REQUIRE_SOURCE_MANIFEST and not manifest_path.exists():
        return
    manifest = load_json(manifest_path)
    require_object(manifest, "source manifest")
    if set(manifest) != {"schema_version", "observed_at", "scope", "families"}:
        raise CatalogError("source manifest contains unsupported or missing fields")
    if manifest["schema_version"] != 1:
        raise CatalogError("source manifest schema_version must be 1")
    if manifest["observed_at"] != index.get("observed_at"):
        raise CatalogError("source manifest observed_at must match catalog index")
    require_string(manifest["scope"], "source manifest.scope")
    families = manifest["families"]
    if not isinstance(families, list):
        raise CatalogError("source manifest families must be a list")

    manifest_family_ids = set()
    for position, family in enumerate(families):
        label = f"source manifest families[{position}]"
        require_object(family, label)
        expected_fields = {
            "id",
            "source",
            "source_locator",
            "verification_method",
            "observed_count",
            "limitations",
            "entries",
        }
        if set(family) != expected_fields:
            raise CatalogError(f"{label} contains unsupported or missing fields")
        family_id = family["id"]
        require_string(family_id, f"{label}.id")
        if family_id in manifest_family_ids:
            raise CatalogError(f"duplicate source manifest family: {family_id}")
        manifest_family_ids.add(family_id)
        if family_id not in patterns_by_family:
            raise CatalogError(f"unknown source manifest family: {family_id}")
        validate_source(family["source"], f"{label}.source")
        require_string(family["source_locator"], f"{label}.source_locator")
        require_string(family["verification_method"], f"{label}.verification_method")
        require_string(family["limitations"], f"{label}.limitations")
        entries = family["entries"]
        if not isinstance(entries, list):
            raise CatalogError(f"{label}.entries must be a list")
        if type(family["observed_count"]) is not int or family["observed_count"] < 0:
            raise CatalogError(f"{label}.observed_count must be a non-negative integer")
        if family["observed_count"] != len(entries):
            raise CatalogError(
                f"source manifest family {family_id} observed_count does not match entries"
            )

        actual_patterns = patterns_by_family[family_id]
        if actual_patterns and any(
            pattern["sources"][0] != family["source"] for pattern in actual_patterns
        ):
            raise CatalogError(
                f"source manifest source does not match family {family_id}"
            )
        actual_mapping = sorted(
            (
                pattern["id"],
                pattern["name"],
                pattern.get("source_path"),
            )
            for pattern in actual_patterns
        )
        manifest_mapping = []
        manifest_entry_ids = set()
        for entry_position, entry in enumerate(entries):
            entry_label = f"{label}.entries[{entry_position}]"
            require_object(entry, entry_label)
            if set(entry) != {
                "id",
                "source_name",
                "name",
                "source_path",
                "normalization_note",
            }:
                raise CatalogError(f"{entry_label} contains unsupported or missing fields")
            require_string(entry["id"], f"{entry_label}.id")
            require_string(entry["source_name"], f"{entry_label}.source_name")
            require_string(entry["name"], f"{entry_label}.name")
            if entry["source_path"] is not None:
                require_string(entry["source_path"], f"{entry_label}.source_path")
            if entry["normalization_note"] is not None:
                require_string(
                    entry["normalization_note"],
                    f"{entry_label}.normalization_note",
                )
            if entry["id"] in manifest_entry_ids:
                raise CatalogError(f"duplicate source manifest entry: {entry['id']}")
            manifest_entry_ids.add(entry["id"])
            manifest_mapping.append(
                (entry["id"], entry["name"], entry["source_path"])
            )
        if sorted(manifest_mapping) != actual_mapping:
            raise CatalogError(
                f"source manifest mapping does not match family {family_id}"
            )

    if manifest_family_ids != set(patterns_by_family):
        raise CatalogError("source manifest family set does not match catalog index")

    if EXPECTED_SOURCE_MANIFEST_SHA256 is not None:
        canonical = json.dumps(
            manifest,
            ensure_ascii=False,
            sort_keys=True,
            separators=(",", ":"),
        ).encode("utf-8")
        digest = hashlib.sha256(canonical).hexdigest()
        if digest != EXPECTED_SOURCE_MANIFEST_SHA256:
            raise CatalogError(
                "source manifest digest does not match the approved provenance snapshot"
            )


def validate(root):
    catalog = root / "catalog"
    index = load_json(catalog / "index.json")
    require_object(index, "catalog index")
    if index.get("schema_version") != 1:
        raise CatalogError("catalog index schema_version must be 1")
    if index.get("maturity") != [
        "indexed",
        "normalized",
        "decision-ready",
        "contextual",
        "superseded",
    ]:
        raise CatalogError("catalog index maturity order is invalid")
    families = index.get("families")
    if not isinstance(families, list) or not families:
        raise CatalogError("catalog index families must be a non-empty list")
    expected_total = index.get("expected_total_count")
    if type(expected_total) is not int or expected_total < 0:
        raise CatalogError("catalog expected_total_count must be a non-negative integer")
    if EXPECTED_TOTAL is not None and expected_total != EXPECTED_TOTAL:
        raise CatalogError(
            f"catalog expected_total_count must be {EXPECTED_TOTAL} but found {expected_total}"
        )

    family_ids = set()
    pattern_ids = set()
    patterns_by_id = {}
    patterns_by_family = {}
    total = 0
    listed_files = set()

    for family_entry in families:
        require_object(family_entry, "family index entry")
        required = {"id", "file", "expected_count", "decision_ready_count"}
        if not required.issubset(family_entry):
            raise CatalogError(
                "family index entry requires id, file, expected_count and decision_ready_count"
            )
        family_id = family_entry["id"]
        require_string(family_id, "family id")
        if not ID.fullmatch(family_id):
            raise CatalogError(f"invalid family id: {family_id}")
        if family_id in family_ids:
            raise CatalogError(f"duplicate family id: {family_id}")
        family_ids.add(family_id)
        filename = family_entry["file"]
        if not isinstance(filename, str) or Path(filename).name != filename or not filename.endswith(".json"):
            raise CatalogError(f"invalid family file: {filename}")
        listed_files.add(filename)
        family_document = load_json(catalog / filename)
        require_object(family_document, f"family document {filename}")
        reject_unsupported_fields(
            family_document,
            FAMILY_DOCUMENT_FIELDS,
            f"family document {filename}",
        )
        if family_document.get("schema_version") != 1:
            raise CatalogError(f"family document {filename} schema_version must be 1")
        metadata = family_document.get("family")
        require_object(metadata, f"family metadata {filename}")
        reject_unsupported_fields(
            metadata,
            FAMILY_METADATA_FIELDS,
            f"family metadata {filename}",
        )
        if metadata.get("id") != family_id:
            raise CatalogError(f"family file {filename} does not declare {family_id}")
        require_string(metadata.get("name"), f"family {family_id}.name")
        require_string(metadata.get("scope"), f"family {family_id}.scope")
        patterns = family_document.get("patterns")
        if not isinstance(patterns, list):
            raise CatalogError(f"family {family_id}.patterns must be a list")
        defaults = family_document.get("defaults", {})
        require_object(defaults, f"family {family_id}.defaults")
        reject_unsupported_fields(
            defaults,
            PATTERN_FIELDS,
            f"family {family_id}.defaults",
        )
        expected_count = family_entry["expected_count"]
        if type(expected_count) is not int or expected_count < 0:
            raise CatalogError(f"family {family_id}.expected_count must be a non-negative integer")
        if (
            EXPECTED_FAMILY_COUNTS is not None
            and family_id in EXPECTED_FAMILY_COUNTS
            and expected_count != EXPECTED_FAMILY_COUNTS[family_id]
        ):
            raise CatalogError(
                f"family {family_id} expected_count must be "
                f"{EXPECTED_FAMILY_COUNTS[family_id]} but found {expected_count}"
            )
        if len(patterns) != expected_count:
            raise CatalogError(
                f"family {family_id} expected {expected_count} patterns but found {len(patterns)}"
            )
        expected_ready = family_entry["decision_ready_count"]
        if type(expected_ready) is not int or expected_ready < 0:
            raise CatalogError(
                f"family {family_id}.decision_ready_count must be a non-negative integer"
            )
        if (
            DECISION_READY_PER_FAMILY is not None
            and expected_ready != DECISION_READY_PER_FAMILY
        ):
            raise CatalogError(
                f"family {family_id} decision_ready_count must be "
                f"{DECISION_READY_PER_FAMILY} but found {expected_ready}"
            )

        family_snapshot = []
        patterns_by_family[family_id] = []
        for position, pattern in enumerate(patterns):
            require_object(pattern, f"{filename}.patterns[{position}]")
            reject_unsupported_fields(
                pattern,
                PATTERN_FIELDS,
                f"{filename}.patterns[{position}]",
            )
            effective_pattern = {**defaults, **pattern}
            if effective_pattern.get("maturity") == "decision-ready":
                raise CatalogError(
                    f"family pattern {effective_pattern.get('id')} must be promoted "
                    "through decision-ready.json"
                )
            pattern_id = validate_pattern(
                effective_pattern, family_id, f"{filename}.patterns[{position}]"
            )
            if pattern_id in pattern_ids:
                raise CatalogError(f"duplicate pattern id: {pattern_id}")
            pattern_ids.add(pattern_id)
            patterns_by_id[pattern_id] = effective_pattern
            patterns_by_family[family_id].append(effective_pattern)
            family_snapshot.append(
                {
                    field: effective_pattern.get(field)
                    for field in ("id", "name", "source_path", "sources")
                }
            )
        if (
            EXPECTED_FAMILY_SNAPSHOTS is not None
            and family_id in EXPECTED_FAMILY_SNAPSHOTS
        ):
            snapshot_payload = json.dumps(
                sorted(family_snapshot, key=lambda entry: entry["id"]),
                ensure_ascii=False,
                sort_keys=True,
                separators=(",", ":"),
            ).encode("utf-8")
            snapshot_digest = hashlib.sha256(snapshot_payload).hexdigest()
            if snapshot_digest != EXPECTED_FAMILY_SNAPSHOTS[family_id]:
                raise CatalogError(
                    f"family {family_id} snapshot digest does not match the approved catalog"
                )
        total += len(patterns)

    if EXPECTED_FAMILIES is not None and family_ids != EXPECTED_FAMILIES:
        missing_families = sorted(EXPECTED_FAMILIES - family_ids)
        extra_families = sorted(family_ids - EXPECTED_FAMILIES)
        details = []
        if missing_families:
            details.append(f"missing: {', '.join(missing_families)}")
        if extra_families:
            details.append(f"unexpected: {', '.join(extra_families)}")
        raise CatalogError(
            "catalog family set must contain the 12 approved families"
            + (f" ({'; '.join(details)})" if details else "")
        )

    extra_family_files = {
        path.name
        for path in catalog.glob("*.json")
        if path.name not in {
            "index.json",
            "schema.json",
            "decision-ready.json",
            "source-manifest.json",
        }
        and path.name not in listed_files
    }
    if extra_family_files:
        raise CatalogError(f"unindexed catalog files: {', '.join(sorted(extra_family_files))}")

    validate_source_manifest(catalog, index, patterns_by_family)

    overlay_path = catalog / "decision-ready.json"
    if overlay_path.exists():
        overlay = load_json(overlay_path)
        require_object(overlay, "decision-ready overlay")
        if overlay.get("schema_version") != 1:
            raise CatalogError("decision-ready overlay schema_version must be 1")
        overlay_defaults = overlay.get("defaults", {})
        require_object(overlay_defaults, "decision-ready overlay defaults")
        unsupported_defaults = sorted(set(overlay_defaults) - OVERLAY_DEFAULT_FIELDS)
        if unsupported_defaults:
            raise CatalogError(
                "decision-ready overlay defaults contains unsupported fields: "
                f"{', '.join(unsupported_defaults)}"
            )
        overlay_patterns = overlay.get("patterns")
        if not isinstance(overlay_patterns, list):
            raise CatalogError("decision-ready overlay patterns must be a list")
        overlay_ids = set()
        for position, entry in enumerate(overlay_patterns):
            require_object(entry, f"decision-ready.json.patterns[{position}]")
            pattern_id = entry.get("id")
            require_string(pattern_id, f"decision-ready.json.patterns[{position}].id")
            if pattern_id not in patterns_by_id:
                raise CatalogError(f"decision-ready overlay id is not indexed: {pattern_id}")
            if pattern_id in overlay_ids:
                raise CatalogError(f"duplicate decision-ready overlay id: {pattern_id}")
            overlay_ids.add(pattern_id)
            unsupported_fields = sorted(set(entry) - OVERLAY_ENTRY_FIELDS)
            if unsupported_fields:
                raise CatalogError(
                    f"decision-ready overlay {pattern_id} contains unsupported fields: "
                    f"{', '.join(unsupported_fields)}"
                )
            missing_direct = sorted(OVERLAY_DIRECT_FIELDS - set(entry))
            if missing_direct:
                raise CatalogError(
                    f"decision-ready overlay {pattern_id} must declare directly: "
                    f"{', '.join(missing_direct)}"
                )
            effective_pattern = {
                **patterns_by_id[pattern_id],
                **overlay_defaults,
                **entry,
            }
            if effective_pattern.get("maturity") != "decision-ready":
                raise CatalogError(
                    f"decision-ready overlay {pattern_id} must set maturity to decision-ready"
                )
            validate_pattern(
                effective_pattern,
                patterns_by_id[pattern_id]["family"],
                f"decision-ready.json.patterns[{position}]",
            )
            patterns_by_id[pattern_id] = effective_pattern


    actual_ready_by_family = {family_id: 0 for family_id in family_ids}
    for pattern in patterns_by_id.values():
        if pattern["maturity"] == "decision-ready":
            actual_ready_by_family[pattern["family"]] += 1
    for family_entry in families:
        family_id = family_entry["id"]
        expected_ready = family_entry["decision_ready_count"]
        actual_ready = actual_ready_by_family[family_id]
        if expected_ready != actual_ready:
            raise CatalogError(
                f"family {family_id} expected {expected_ready} decision-ready patterns but found {actual_ready}"
            )

    expected_ready_total = index.get("expected_decision_ready_count")
    if type(expected_ready_total) is not int or expected_ready_total < 0:
        raise CatalogError(
            "catalog expected_decision_ready_count must be a non-negative integer"
        )
    actual_ready_total = sum(actual_ready_by_family.values())
    if expected_ready_total != actual_ready_total:
        raise CatalogError(
            f"catalog expected {expected_ready_total} decision-ready patterns but found {actual_ready_total}"
        )

    relations = [
        (pattern["id"], relation["type"], relation["target"])
        for pattern in patterns_by_id.values()
        for relation in pattern.get("relations", [])
    ]
    for source, relation_type, target in relations:
        if target not in pattern_ids:
            raise CatalogError(
                f"pattern {source} relation target does not exist: {target}"
            )
        if relation_type == "same-name-different-scope":
            source_pattern = patterns_by_id[source]
            target_pattern = patterns_by_id[target]
            if source_pattern["family"] == target_pattern["family"]:
                raise CatalogError(
                    "same-name-different-scope relation must cross families: "
                    f"{source} -> {target}"
                )
            if normalize_pattern_name(source_pattern["name"]) != normalize_pattern_name(
                target_pattern["name"]
            ):
                raise CatalogError(
                    "same-name-different-scope relation requires matching normalized names: "
                    f"{source} -> {target}"
                )

    same_name_edges = {
        frozenset((source, target))
        for source, relation_type, target in relations
        if relation_type == "same-name-different-scope"
    }
    patterns_by_normalized_name = {}
    for pattern in patterns_by_id.values():
        normalized_name = normalize_pattern_name(pattern["name"])
        patterns_by_normalized_name.setdefault(normalized_name, []).append(pattern)
    for same_name_patterns in patterns_by_normalized_name.values():
        cross_family = sorted(
            same_name_patterns,
            key=lambda pattern: pattern["id"],
        )
        for left_position, left in enumerate(cross_family):
            for right in cross_family[left_position + 1 :]:
                if left["family"] == right["family"]:
                    continue
                pair = frozenset((left["id"], right["id"]))
                if pair not in same_name_edges:
                    raise CatalogError(
                        "same normalized name requires same-name-different-scope "
                        f"relation: {left['id']} <-> {right['id']}"
                    )

    if expected_total != total:
        raise CatalogError(f"catalog expected {expected_total} patterns but found {total}")

    return total, len(families)


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--root",
        type=Path,
        default=Path(__file__).resolve().parents[1],
        help="design-patterns plugin root (defaults to this script's plugin)",
    )
    args = parser.parse_args(argv)
    try:
        total, families = validate(args.root.resolve())
    except (CatalogError, OSError) as exc:
        print(f"catalog validation failed: {exc}", file=sys.stderr)
        return 1
    print(f"catalog valid: {total} patterns across {families} families")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
