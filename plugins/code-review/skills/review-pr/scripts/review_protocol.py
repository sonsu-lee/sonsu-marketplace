#!/usr/bin/env python3
"""Pure publication-state decision for the explicit review-pr workflow."""

from __future__ import annotations

import json
import sys
from typing import Any

_ACTIONS = {
    "wait_reviewers",
    "retry_reviewer_once",
    "abort_reviewer_failed",
    "abort_stale",
    "post_once",
    "complete_from_readback",
    "fail_ambiguous",
}


def decide(state: dict[str, Any]) -> dict[str, Any]:
    """Return the next action without performing I/O or retaining state."""
    locked_base_sha = state.get("locked_base_sha")
    current_base_sha = state.get("current_base_sha")
    if not isinstance(locked_base_sha, str) or not locked_base_sha:
        raise ValueError("locked_base_sha must be a non-empty string")
    if not isinstance(current_base_sha, str) or not current_base_sha:
        raise ValueError("current_base_sha must be a non-empty string")
    locked_sha = state.get("locked_sha")
    current_sha = state.get("current_sha")
    if not isinstance(locked_sha, str) or not locked_sha:
        raise ValueError("locked_sha must be a non-empty string")
    if not isinstance(current_sha, str) or not current_sha:
        raise ValueError("current_sha must be a non-empty string")
    if locked_base_sha != current_base_sha or locked_sha != current_sha:
        return _result("abort_stale")

    reviewers = state.get("reviewers")
    if not isinstance(reviewers, list) or len(reviewers) != 3:
        raise ValueError("reviewers must contain exactly three entries")

    reviewer_ids: list[str] = []
    checkout_receipts: list[str] = []
    failed: list[dict[str, Any]] = []
    for reviewer in reviewers:
        if not isinstance(reviewer, dict):
            raise ValueError("each reviewer must be an object")
        reviewer_id = reviewer.get("id")
        if not isinstance(reviewer_id, str) or not reviewer_id:
            raise ValueError("each reviewer.id must be a non-empty string")
        reviewer_ids.append(reviewer_id)
        if reviewer.get("locked_sha") != locked_sha:
            raise ValueError("each reviewer.locked_sha must match locked_sha")
        checkout_receipt = reviewer.get("checkout_receipt")
        if not isinstance(checkout_receipt, str) or not checkout_receipt:
            raise ValueError("each reviewer.checkout_receipt must be a non-empty string")
        checkout_receipts.append(checkout_receipt)
        attempt_count = reviewer.get("attempt_count")
        if type(attempt_count) is not int or attempt_count not in {1, 2}:
            raise ValueError("each reviewer.attempt_count must be 1 or 2")
        status = reviewer.get("status")
        if status in {"pending", "running"}:
            return _result("wait_reviewers")
        if status == "failed":
            failed.append(reviewer)
        elif status != "complete":
            raise ValueError(f"unsupported reviewer status: {status!r}")

    if len(set(reviewer_ids)) != 3:
        raise ValueError("reviewer.id values must be unique")
    if len(set(checkout_receipts)) != 3:
        raise ValueError("reviewer.checkout_receipt values must be unique")

    if failed:
        retryable = [
            reviewer
            for reviewer in failed
            if reviewer.get("failure_kind") == "transient"
            and reviewer["attempt_count"] == 1
        ]
        if len(retryable) == len(failed):
            return _result(
                "retry_reviewer_once",
                reviewer_ids=[reviewer["id"] for reviewer in retryable],
            )
        return _result("abort_reviewer_failed")

    publish = state.get("publish")
    if not isinstance(publish, dict):
        raise ValueError("publish must be an object")
    attempted = publish.get("attempted")
    if attempted is False:
        return _result("post_once", publish_allowed=True)
    if attempted is not True:
        raise ValueError("publish.attempted must be a boolean")

    readback = state.get("readback")
    if not isinstance(readback, dict):
        raise ValueError("readback must be an object after a publish attempt")
    matching = all(
        readback.get(field) is True
        for field in ("complete", "marker_matches", "author_matches", "commit_matches", "payload_matches")
    )
    if matching:
        return _result("complete_from_readback")
    return _result("fail_ambiguous")


def _result(
    action: str,
    *,
    publish_allowed: bool = False,
    reviewer_ids: list[str] | None = None,
) -> dict[str, Any]:
    if action not in _ACTIONS:
        raise AssertionError(f"unknown action: {action}")
    result: dict[str, Any] = {"action": action, "publish_allowed": publish_allowed}
    if reviewer_ids is not None:
        result["reviewer_ids"] = reviewer_ids
    return result


def main() -> int:
    try:
        state = json.load(sys.stdin)
        if not isinstance(state, dict):
            raise ValueError("input must be a JSON object")
        result = decide(state)
    except (json.JSONDecodeError, ValueError) as error:
        json.dump({"error": str(error)}, sys.stdout, sort_keys=True)
        sys.stdout.write("\n")
        return 2
    json.dump(result, sys.stdout, sort_keys=True)
    sys.stdout.write("\n")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
