#!/usr/bin/env python3
"""Validate design terminology and its catalog evidence; optionally prune orphan links."""
from __future__ import annotations

import argparse
import importlib.util
import json
import os
import re
import tempfile
from datetime import date
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
SPEC = importlib.util.spec_from_file_location("madia_catalog_validator", ROOT / "scripts/validate_madia_design_catalog.py")
assert SPEC is not None and SPEC.loader is not None
CATALOG_VALIDATOR = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(CATALOG_VALIDATOR)
TERM_ID_RE = CATALOG_VALIDATOR.TERM_ID_RE
TERM_FIELDS = {"id", "ko", "en", "label_status", "definition", "includes", "excludes", "visual_signals",
               "relations", "sources", "observed_expressions", "status", "status_reason", "review_by"}
RELATION_TYPES = {"synonym", "broader", "narrower", "related", "confused_with"}
TERM_STATUSES = {"candidate", "adopted", "held", "rejected"}
OCCURRENCE_RE = re.compile(r"^[A-Za-z0-9_-]{11}:[0-9]{3}$")


def iso_date(value: Any):
    if not isinstance(value, str):
        return None
    try:
        result = date.fromisoformat(value)
    except ValueError:
        return None
    return result if result.isoformat() == value else None


def exact_fields(value: Any, fields: set[str], context: str, errors: list[str]) -> bool:
    if not isinstance(value, dict):
        errors.append(f"{context} must be an object")
        return False
    if set(value) != fields:
        errors.append(f"{context} must contain exact fields: {sorted(fields)}")
    return True


def catalog_units(catalog: Any) -> dict[str, dict]:
    if not isinstance(catalog, dict) or not isinstance(catalog.get("videos"), list):
        raise ValueError("catalog must contain a videos array")
    units = {}
    for video in catalog["videos"]:
        if not isinstance(video, dict) or not isinstance(video.get("evidence_units"), list):
            raise ValueError("catalog videos must contain evidence_units arrays")
        for unit in video["evidence_units"]:
            if not isinstance(unit, dict) or not isinstance(unit.get("id"), str) or not CATALOG_VALIDATOR.unique_string_list(unit.get("term_ids"), allow_empty=True):
                raise ValueError("catalog evidence units must contain ids and unique term_ids")
            if unit["id"] in units:
                raise ValueError(f"duplicate catalog occurrence: {unit['id']}")
            units[unit["id"]] = unit
    return units


def validate_ledger(payload: Any, catalog: Any = None) -> list[str]:
    errors: list[str] = []
    if not exact_fields(payload, {"schema_version", "as_of", "terms"}, "ledger", errors):
        return errors
    if payload.get("schema_version") != "design-terminology-v1":
        errors.append("schema_version must be design-terminology-v1")
    as_of = iso_date(payload.get("as_of"))
    if as_of is None:
        errors.append("as_of must be an ISO date")
    terms = payload.get("terms")
    if not isinstance(terms, list):
        return errors + ["terms must be an array"]
    by_id = {}
    names = set()
    for index, term in enumerate(terms):
        context = f"terms[{index}]"
        if not exact_fields(term, TERM_FIELDS, context, errors):
            continue
        term_id = term.get("id")
        if not isinstance(term_id, str) or not TERM_ID_RE.fullmatch(term_id):
            errors.append(f"{context}.id is invalid")
        elif term_id in by_id:
            errors.append(f"{context}.id is duplicated: {term_id}")
        else:
            by_id[term_id] = term
        for field in ("ko", "en"):
            if not CATALOG_VALIDATOR.non_empty_string(term.get(field)):
                errors.append(f"{context}.{field} must be a non-empty string")
        ko = term.get("ko")
        if term.get("status") != "rejected" and isinstance(ko, str):
            if ko in names:
                errors.append(f"{context}.ko duplicates a non-rejected term")
            names.add(ko)
        for field in ("definition", "status_reason"):
            if not isinstance(term.get(field), str):
                errors.append(f"{context}.{field} must be a string")
        if not CATALOG_VALIDATOR.choice(term.get("label_status"), {"official", "internal_preferred"}):
            errors.append(f"{context}.label_status is invalid")
        if not CATALOG_VALIDATOR.choice(term.get("status"), TERM_STATUSES):
            errors.append(f"{context}.status is invalid")
        review_by = iso_date(term.get("review_by"))
        if review_by is None:
            errors.append(f"{context}.review_by must be an ISO date")
        for field in ("includes", "excludes", "visual_signals"):
            value = term.get(field)
            if not isinstance(value, list) or not all(CATALOG_VALIDATOR.non_empty_string(item) for item in value):
                errors.append(f"{context}.{field} must be a string array")
        sources = term.get("sources")
        if not isinstance(sources, list):
            errors.append(f"{context}.sources must be an array")
            sources = []
        for source_index, source in enumerate(sources):
            source_context = f"{context}.sources[{source_index}]"
            if not exact_fields(source, {"id", "title", "url", "source_type"}, source_context, errors):
                continue
            if not all(CATALOG_VALIDATOR.non_empty_string(source.get(key)) for key in ("id", "title")):
                errors.append(f"{source_context} requires non-empty id and title")
            if not CATALOG_VALIDATOR.verifiable_https_url(source.get("url")):
                errors.append(f"{source_context}.url must be a verifiable HTTPS URL")
            if not CATALOG_VALIDATOR.choice(source.get("source_type"), {"standard", "research", "product"}):
                errors.append(f"{source_context}.source_type is invalid")
        if term.get("label_status") == "official" and not sources:
            errors.append(f"{context} official terms require sources")
        if term.get("status") in ("held", "rejected") and not CATALOG_VALIDATOR.non_empty_string(term.get("status_reason")):
            errors.append(f"{context} held/rejected terms require status_reason")
        expressions = term.get("observed_expressions")
        if not isinstance(expressions, list):
            errors.append(f"{context}.observed_expressions must be an array")
            expressions = []
        observations = set()
        video_ids = set()
        for expression_index, expression in enumerate(expressions):
            expression_context = f"{context}.observed_expressions[{expression_index}]"
            if not exact_fields(expression, {"text", "occurrence_id"}, expression_context, errors):
                continue
            text, occurrence = expression.get("text"), expression.get("occurrence_id")
            if not CATALOG_VALIDATOR.non_empty_string(text) or len(text) > 120:
                errors.append(f"{expression_context}.text must contain 1–120 characters")
            if not isinstance(occurrence, str) or not OCCURRENCE_RE.fullmatch(occurrence):
                errors.append(f"{expression_context}.occurrence_id must be a catalog unit ID")
            else:
                video_ids.add(occurrence.split(":")[0])
            if isinstance(text, str) and isinstance(occurrence, str):
                pair = (text, occurrence)
                if pair in observations:
                    errors.append(f"{expression_context} repeats the same observed expression")
                observations.add(pair)
        if term.get("status") == "adopted":
            if not CATALOG_VALIDATOR.non_empty_string(term.get("definition")):
                errors.append(f"{context} adopted terms require definition")
            for field in ("includes", "excludes"):
                if not term.get(field):
                    errors.append(f"{context} adopted terms require {field}")
            if not sources and not (term.get("label_status") == "internal_preferred" and CATALOG_VALIDATOR.non_empty_string(term.get("status_reason"))):
                errors.append(f"{context} adopted terms require sources or a justified internal label")
            if len(observations) < 3 or len(video_ids) < 2:
                errors.append(f"{context} adopted terms require three expressions across at least two videos")
            if as_of is not None and review_by is not None and review_by < as_of:
                errors.append(f"{context} adopted review_by must not precede as_of")
    for index, term in enumerate(terms):
        if not isinstance(term, dict):
            continue
        relations = term.get("relations")
        if not isinstance(relations, list):
            errors.append(f"terms[{index}].relations must be an array")
            continue
        seen = set()
        for relation_index, relation in enumerate(relations):
            context = f"terms[{index}].relations[{relation_index}]"
            if not exact_fields(relation, {"type", "term_id"}, context, errors):
                continue
            relation_type, target = relation.get("type"), relation.get("term_id")
            if not CATALOG_VALIDATOR.choice(relation_type, RELATION_TYPES):
                errors.append(f"{context}.type is invalid")
            if not isinstance(target, str) or target not in by_id:
                errors.append(f"{context}.term_id must reference an existing term")
            elif target == term.get("id"):
                errors.append(f"{context} cannot relate a term to itself")
            if isinstance(relation_type, str) and isinstance(target, str):
                pair = (relation_type, target)
                if pair in seen:
                    errors.append(f"{context} duplicates a relation")
                seen.add(pair)
    if catalog is not None:
        try:
            units = catalog_units(catalog)
        except ValueError as error:
            return errors + [str(error)]
        for unit_id, unit in units.items():
            for term_id in unit["term_ids"]:
                if term_id not in by_id or by_id[term_id].get("status") == "rejected":
                    errors.append(f"{unit_id}: term_ids must reference non-rejected ledger terms: {term_id}")
        for term_id, term in by_id.items():
            for expression in CATALOG_VALIDATOR.safe_list(term.get("observed_expressions")):
                if not isinstance(expression, dict) or not isinstance(expression.get("occurrence_id"), str):
                    continue
                occurrence = expression["occurrence_id"]
                unit = units.get(occurrence)
                if unit is None or term_id not in unit["term_ids"]:
                    errors.append(f"{term_id}: observed expression must reference a unit assigned this term: {occurrence}")
                elif term.get("status") == "adopted":
                    verification = unit.get("verification")
                    if not isinstance(verification, dict) or verification.get("status") not in ("confirmed", "corrected"):
                        errors.append(f"{term_id}: adopted expression requires verified evidence: {occurrence}")
    return errors


def prune_orphans(payload: dict, catalog: dict) -> int:
    units = catalog_units(catalog)
    removed = 0
    for term in payload["terms"]:
        kept = []
        for expression in term["observed_expressions"]:
            occurrence = expression.get("occurrence_id")
            unit = units.get(occurrence) if isinstance(occurrence, str) else None
            if unit is not None and term["id"] in unit["term_ids"]:
                kept.append(expression)
            else:
                removed += 1
        term["observed_expressions"] = kept
    return removed


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("ledger", type=Path)
    parser.add_argument("--catalog", type=Path)
    parser.add_argument("--prune-orphans", action="store_true")
    args = parser.parse_args()
    if args.prune_orphans and args.catalog is None:
        parser.error("--prune-orphans requires --catalog")
    try:
        payload = json.loads(args.ledger.read_text(encoding="utf-8"))
        catalog = json.loads(args.catalog.read_text(encoding="utf-8")) if args.catalog else None
        if args.prune_orphans:
            # Reject malformed entries before a mutation; adoption may become invalid after pruning.
            errors = validate_ledger(payload)
            if errors:
                raise ValueError("\n".join(errors))
            removed = prune_orphans(payload, catalog)
            temporary = None
            try:
                with tempfile.NamedTemporaryFile("w", encoding="utf-8", dir=args.ledger.parent, delete=False) as handle:
                    json.dump(payload, handle, ensure_ascii=False, indent=2)
                    handle.write("\n")
                    temporary = Path(handle.name)
                os.replace(temporary, args.ledger)
            finally:
                if temporary is not None:
                    temporary.unlink(missing_ok=True)
            print(f"PRUNED: {removed}")
        errors = validate_ledger(payload, catalog)
        if errors:
            raise ValueError("\n".join(errors))
    except (OSError, ValueError) as error:
        print(f"ERROR: {error}")
        return 1
    print("OK: design-terminology")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
