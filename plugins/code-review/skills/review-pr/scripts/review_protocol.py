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
    locked_sha = state.get("locked_sha")
    current_sha = state.get("current_sha")
    if not isinstance(locked_sha, str) or not locked_sha:
        raise ValueError("locked_sha must be a non-empty string")
    if not isinstance(current_sha, str) or not current_sha:
        raise ValueError("current_sha must be a non-empty string")
    if locked_sha != current_sha:
        return _result("abort_stale")

    reviewers = state.get("reviewers")
    if not isinstance(reviewers, list) or len(reviewers) != 3:
        raise ValueError("reviewers must contain exactly three entries")

    failed: list[dict[str, Any]] = []
    for reviewer in reviewers:
        if not isinstance(reviewer, dict):
            raise ValueError("each reviewer must be an object")
        status = reviewer.get("status")
        if status in {"pending", "running"}:
            return _result("wait_reviewers")
        if status == "failed":
            failed.append(reviewer)
        elif status != "complete":
            raise ValueError(f"unsupported reviewer status: {status!r}")

    if failed:
        retryable = [
            reviewer
            for reviewer in failed
            if reviewer.get("failure_kind") == "transient"
            and reviewer.get("attempt_count") == 1
        ]
        if len(failed) == 1 and retryable:
            return _result("retry_reviewer_once")
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


def _result(action: str, *, publish_allowed: bool = False) -> dict[str, Any]:
    if action not in _ACTIONS:
        raise AssertionError(f"unknown action: {action}")
    return {"action": action, "publish_allowed": publish_allowed}


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
