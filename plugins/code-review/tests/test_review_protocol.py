from __future__ import annotations

import importlib.util
import unittest
from pathlib import Path


SCRIPT = (
    Path(__file__).parents[1]
    / "skills"
    / "review-pr"
    / "scripts"
    / "review_protocol.py"
)
SPEC = importlib.util.spec_from_file_location("review_protocol", SCRIPT)
assert SPEC and SPEC.loader
MODULE = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(MODULE)


class ReviewProtocolTest(unittest.TestCase):
    def state(self) -> dict:
        return {
            "locked_sha": "abc123",
            "current_sha": "abc123",
            "reviewers": [
                {"status": "complete", "attempt_count": 1},
                {"status": "complete", "attempt_count": 1},
                {"status": "complete", "attempt_count": 1},
            ],
            "publish": {"attempted": False},
        }

    def assert_action(self, state: dict, action: str, allowed: bool = False) -> None:
        self.assertEqual(
            MODULE.decide(state),
            {"action": action, "publish_allowed": allowed},
        )

    def test_wait_reviewers(self) -> None:
        state = self.state()
        state["reviewers"][1]["status"] = "running"
        self.assert_action(state, "wait_reviewers")

    def test_retry_transient_reviewer_once(self) -> None:
        state = self.state()
        state["reviewers"][0] = {
            "status": "failed",
            "failure_kind": "transient",
            "attempt_count": 1,
        }
        self.assert_action(state, "retry_reviewer_once")

    def test_abort_non_transient_or_exhausted_reviewer(self) -> None:
        for failure_kind, attempt_count in (("non_transient", 1), ("transient", 2)):
            with self.subTest(failure_kind=failure_kind, attempt_count=attempt_count):
                state = self.state()
                state["reviewers"][0] = {
                    "status": "failed",
                    "failure_kind": failure_kind,
                    "attempt_count": attempt_count,
                }
                self.assert_action(state, "abort_reviewer_failed")

    def test_abort_stale_before_waiting_or_posting(self) -> None:
        state = self.state()
        state["current_sha"] = "def456"
        state["reviewers"][0]["status"] = "running"
        self.assert_action(state, "abort_stale")

    def test_post_once_after_three_completed_reviewers(self) -> None:
        self.assert_action(self.state(), "post_once", allowed=True)

    def test_complete_from_matching_readback(self) -> None:
        state = self.state()
        state["publish"]["attempted"] = True
        state["readback"] = {
            "complete": True,
            "marker_matches": True,
            "author_matches": True,
            "commit_matches": True,
            "payload_matches": True,
        }
        self.assert_action(state, "complete_from_readback")

    def test_fail_ambiguous_without_complete_exact_readback(self) -> None:
        for readback in (
            {"complete": False},
            {
                "complete": True,
                "marker_matches": True,
                "author_matches": True,
                "commit_matches": True,
                "payload_matches": False,
            },
        ):
            with self.subTest(readback=readback):
                state = self.state()
                state["publish"]["attempted"] = True
                state["readback"] = readback
                self.assert_action(state, "fail_ambiguous")


if __name__ == "__main__":
    unittest.main()
