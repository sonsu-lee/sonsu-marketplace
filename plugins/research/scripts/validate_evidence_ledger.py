#!/usr/bin/env python3
"""Validate evidence-policy JSON structure, never source truth or authority.

Usage: validate_evidence_ledger.py LEDGER (use - for stdin).
Print JSON {valid, claims, evidence, violations: [{code, location, message}]}.
Exit 0: structurally valid; 1: contract violations; 2: unreadable/invalid JSON.
No network calls or writes. Unknown extension fields are preserved/ignored.
"""

import argparse
import json
from pathlib import Path
import sys


CLAIM_ENUMS = {
    "claim_kind": ("fact", "inference", "recommendation"),
    "coverage_status": ("open", "supported", "partial", "contradicted", "unsupported", "blocked"),
}
EVIDENCE_ENUMS = {
    "access_scope": ("public", "private", "local"),
    "support_relation": ("direct", "partial", "opposes"),
    "confidence": ("high", "medium", "low"),
}
IDENTITIES = ("public_url", "connector_item_id", "repository_commit_path", "local_path_content_hash")
DATES = ("published_or_updated", "version_or_commit", "accessed_at")


def validate(data):
    violations = []

    def fail(code, location, message):
        violations.append({"code": code, "location": location, "message": message})

    def text(obj, key, location, allow_empty=False):
        value = obj.get(key)
        if not isinstance(value, str) or (not allow_empty and not value.strip()):
            fail("invalid-field", f"{location}.{key}", "expected a string" if allow_empty else "expected a nonempty string")
            return False
        return True

    def enums(obj, fields, location):
        for key, choices in fields.items():
            if obj.get(key) not in choices:
                fail("invalid-enum", f"{location}.{key}", "expected " + " | ".join(choices))

    def rows(key):
        value = data.get(key)
        if not isinstance(value, list):
            fail("invalid-field", key, "expected an array")
            return []
        return value

    if not isinstance(data, dict):
        fail("invalid-field", "$", "expected an object")
        return {"valid": False, "claims": 0, "evidence": 0, "violations": violations}
    claims, evidence = rows("claims"), rows("evidence")
    ids = {}
    for index, claim in enumerate(claims):
        location = f"claims[{index}]"
        if not isinstance(claim, dict):
            fail("invalid-field", location, "expected an object")
            continue
        valid_id = text(claim, "claim_id", location)
        text(claim, "claim", location)
        enums(claim, CLAIM_ENUMS, location)
        if valid_id:
            claim_id = claim["claim_id"]
            if claim_id in ids:
                fail("duplicate-claim", location + ".claim_id", "claim_id must be unique")
            else:
                ids[claim_id] = (index, claim)

    linked = set()
    for index, entry in enumerate(evidence):
        location = f"evidence[{index}]"
        if not isinstance(entry, dict):
            fail("invalid-field", location, "expected an object")
            continue
        if text(entry, "claim_id", location):
            claim_id = entry["claim_id"]
            if claim_id not in ids:
                fail("unknown-claim", location + ".claim_id", "no matching claim")
            else:
                linked.add(claim_id)
        enums(entry, EVIDENCE_ENUMS, location)
        for key in ("reopen_method", "source_role", "independence"):
            text(entry, key, location)
        version = entry.get("version_or_content_hash")
        if "version_or_content_hash" not in entry or (version is not None and (not isinstance(version, str) or not version.strip())):
            fail("invalid-field", location + ".version_or_content_hash", "expected a nonempty string or null")
        for key in ("limitations", "conflicts"):
            text(entry, key, location, allow_empty=True)
        if not isinstance(entry.get("locator"), str) or not entry["locator"].strip():
            fail("missing-locator", location + ".locator", "expected an exact passage, table, figure, dataset cell or file:symbol")
        if type(entry.get("verified")) is not bool:
            fail("invalid-field", location + ".verified", "expected a boolean")
        source = entry.get("source")
        if not isinstance(source, dict):
            fail("invalid-field", location + ".source", "expected an object")
        else:
            for key in ("title", "author_or_org"):
                text(source, key, location + ".source")
            url = source.get("url")
            if "url" not in source or (url is not None and (not isinstance(url, str) or not url.strip())):
                fail("invalid-field", location + ".source.url", "expected a nonempty string or null")
            elif entry.get("access_scope") == "public" and url is None:
                fail("invalid-field", location + ".source.url", "public sources require a canonical URL")
        identity = entry.get("source_identity")
        if not isinstance(identity, dict):
            fail("invalid-field", location + ".source_identity", "expected an object")
        else:
            enums(identity, {"kind": IDENTITIES}, location + ".source_identity")
            text(identity, "value", location + ".source_identity")
        dated = False
        for key in DATES:
            if key not in entry:
                continue
            value = entry[key]
            if value is not None:
                if text(entry, key, location):
                    dated = True
        if not dated:
            fail("missing-date-or-version", location, "provide published_or_updated, version_or_commit or accessed_at")

    for claim_id, (index, claim) in ids.items():
        if claim.get("coverage_status") in ("supported", "partial", "contradicted") and claim_id not in linked:
            fail("missing-evidence", f"claims[{index}].claim_id", "this coverage status requires a linked evidence entry")
    return {"valid": not violations, "claims": len(claims), "evidence": len(evidence), "violations": violations}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("ledger", help="JSON ledger path, or - for stdin")
    args = parser.parse_args()
    try:
        raw = sys.stdin.read() if args.ledger == "-" else Path(args.ledger).read_text(encoding="utf-8")
        data = json.loads(raw)
    except (OSError, UnicodeError, ValueError) as exc:
        print(f"cannot read ledger: {exc}", file=sys.stderr)
        return 2
    result = validate(data)
    print(json.dumps(result, ensure_ascii=False))
    return 0 if result["valid"] else 1


if __name__ == "__main__":
    sys.exit(main())
