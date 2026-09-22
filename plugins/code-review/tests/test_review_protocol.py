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
            "locked_base_sha": "base123",
            "current_base_sha": "base123",
            "locked_sha": "abc123",
            "current_sha": "abc123",
            "reviewers": [
                {
                    "id": f"reviewer-{index}",
                    "locked_sha": "abc123",
                    "checkout_receipt": f"checkout-{index}",
                    "status": "complete",
                    "attempt_count": 1,
                }
                for index in range(1, 4)
            ],
            "publish": {"attempted": False},
        }

    def assert_action(
        self,
        state: dict,
        action: str,
        allowed: bool = False,
        reviewer_ids: list[str] | None = None,
    ) -> None:
        expected = {"action": action, "publish_allowed": allowed}
        if reviewer_ids is not None:
            expected["reviewer_ids"] = reviewer_ids
        self.assertEqual(MODULE.decide(state), expected)

    def test_wait_reviewers(self) -> None:
        state = self.state()
        state["reviewers"][1]["status"] = "running"
        self.assert_action(state, "wait_reviewers")

    def test_retry_transient_reviewers_once(self) -> None:
        state = self.state()
        for index in (0, 1):
            state["reviewers"][index].update(
                status="failed",
                failure_kind="transient",
            )
        self.assert_action(
            state,
            "retry_reviewer_once",
            reviewer_ids=["reviewer-1", "reviewer-2"],
        )

    def test_abort_non_transient_or_exhausted_reviewer(self) -> None:
        for failure_kind, attempt_count in (("non_transient", 1), ("transient", 2)):
            with self.subTest(failure_kind=failure_kind, attempt_count=attempt_count):
                state = self.state()
                state["reviewers"][0].update(
                    status="failed",
                    failure_kind=failure_kind,
                    attempt_count=attempt_count,
                )
                self.assert_action(state, "abort_reviewer_failed")

    def test_abort_when_any_failure_is_not_retryable(self) -> None:
        state = self.state()
        state["reviewers"][0].update(status="failed", failure_kind="transient")
        state["reviewers"][1].update(status="failed", failure_kind="non_transient")
        self.assert_action(state, "abort_reviewer_failed")

    def test_abort_stale_before_waiting_or_posting(self) -> None:
        for field in ("current_sha", "current_base_sha"):
            with self.subTest(field=field):
                state = self.state()
                state[field] = "def456"
                state["reviewers"][0]["status"] = "running"
                self.assert_action(state, "abort_stale")

    def test_reject_duplicate_reviewer_identity_or_checkout(self) -> None:
        for field in ("id", "checkout_receipt"):
            with self.subTest(field=field):
                state = self.state()
                state["reviewers"][1][field] = state["reviewers"][0][field]
                with self.assertRaisesRegex(ValueError, "must be unique"):
                    MODULE.decide(state)

    def test_reject_reviewer_for_different_locked_sha(self) -> None:
        state = self.state()
        state["reviewers"][2]["locked_sha"] = "def456"
        with self.assertRaisesRegex(ValueError, "must match locked_sha"):
            MODULE.decide(state)

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
