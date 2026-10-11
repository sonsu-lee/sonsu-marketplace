"""inspect_prs.py가 페이지·부분 실패·head 변경·상태 구분을 보존하는지 fake gh로 확인한다."""

import json
import os
from pathlib import Path
import subprocess
import sys
import tempfile
import textwrap
import unittest


SCRIPT = Path(__file__).resolve().parents[1] / "scripts/inspect_prs.py"
HOST = "github.acme.test"
REPO = "tools/widget"
HEAD = "a" * 40
NEW_HEAD = "b" * 40
PREFIX = f"repos/{REPO}"
FAKE_COMMAND = textwrap.dedent("""\
    #!{python}
    import json, os, sys
    args = sys.argv[1:]
    if args[0] == "auth":
        key = "auth"
    elif args[:2] == ["pr", "view"]:
        key = ("final:" if args[-1] == "headRefOid" else "metadata:") + args[2]
    elif "graphql" in args:
        fields = dict(arg.split("=", 1) for arg in args if "=" in arg)
        cursor = fields.get("cursor", "first")
        if "InspectThreads" in fields["query"]:
            key = "threads:" + fields["number"] + ":" + cursor
        elif "InspectReviewRequests" in fields["query"]:
            key = "requests:" + fields["number"] + ":" + cursor
        else:
            key = "comments:" + fields["id"] + ":" + cursor
    else:
        key = args[-1]
    with open(os.environ["FAKE_GH_LOG"], "a", encoding="utf-8") as log:
        log.write(json.dumps({{"args": args, "host": os.environ.get("GH_HOST"), "key": key}}) + "\\n")
    item = json.loads(os.environ["FAKE_GH_RESPONSES"]).get(key)
    if item is None:
        sys.stderr.write("unexpected command: " + key)
        sys.exit(9)
    sys.stdout.write(item.get("stdout", ""))
    sys.stderr.write(item.get("stderr", ""))
    sys.exit(item.get("code", 0))
""")


def response(data=None, *, raw=None, code=0, stderr=""):
    return {"stdout": json.dumps(data) if raw is None else raw, "code": code, "stderr": stderr}


def connection(nodes, *, more=False, cursor=None, comments=False, requests=False, errors=None):
    value = {"nodes": nodes, "pageInfo": {"hasNextPage": more, "endCursor": cursor}}
    if comments:
        data = {"node": {"comments": value}}
    else:
        data = {"repository": {"pullRequest": {"timelineItems" if requests else "reviewThreads": value}}}
    payload = {"data": data}
    if errors:
        payload["errors"] = errors
    return response(payload)


def default_responses(number=31):
    return {
        "auth": response({}),
        f"metadata:{number}": response({
            "number": number, "title": "Update widget schema", "url": f"https://{HOST}/{REPO}/pull/{number}",
            "state": "OPEN", "isDraft": True, "baseRefName": "release", "baseRefOid": "c" * 40,
            "headRefName": "schema-update", "headRefOid": HEAD, "mergeStateStatus": "CLEAN",
            "reviewDecision": "REVIEW_REQUIRED", "isCrossRepository": True,
            "headRepository": {"name": "widget"}, "headRepositoryOwner": {"login": "contributor"},
        }),
        f"final:{number}": response({"headRefOid": HEAD}),
        f"{PREFIX}/pulls/{number}/reviews?per_page=100&page=1": response([]),
        f"{PREFIX}/commits/{HEAD}/check-runs?filter=latest&per_page=100&page=1": response({"check_runs": []}),
        f"{PREFIX}/commits/{HEAD}/statuses?per_page=100&page=1": response([]),
        f"threads:{number}:first": connection([]),
        f"requests:{number}:first": connection([], requests=True),
    }


class InspectPrsTest(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.tmp = Path(self.temp.name)
        self.bin = self.tmp / "bin"
        self.bin.mkdir()
        fake = self.bin / "gh"
        fake.write_text(FAKE_COMMAND.format(python=sys.executable), encoding="utf-8")
        fake.chmod(0o755)
        self.log = self.tmp / "gh.jsonl"
        self.env = dict(os.environ, PATH=f"{self.bin}{os.pathsep}{os.environ['PATH']}",
                        FAKE_GH_LOG=str(self.log))

    def tearDown(self):
        self.temp.cleanup()

    def run_tool(self, responses=None, *scope, extra=()):
        env = dict(self.env, FAKE_GH_RESPONSES=json.dumps(default_responses() if responses is None else responses))
        process = subprocess.run([sys.executable, "-B", str(SCRIPT), "--host", HOST, "--repo", REPO,
                                  *(scope or ("--pr", "31")), *extra], cwd=self.tmp,
                                 env=env, capture_output=True, text=True, check=False)
        data = json.loads(process.stdout) if process.stdout else None
        calls = [json.loads(line) for line in self.log.read_text().splitlines()] if self.log.exists() else []
        return process, data, calls

    def test_empty_observations_are_not_ci_success_or_merge_approval(self):
        process, data, calls = self.run_tool()
        self.assertEqual(process.returncode, 0, process.stderr)
        pr = data["pull_requests"][0]
        self.assertEqual(pr["ci_states"], {"check_runs": [], "latest_statuses": []})
        self.assertEqual(pr["required_checks"]["status"], "unverified")
        self.assertEqual(pr["metadata"]["data"]["mergeStateStatus"], "CLEAN")
        self.assertTrue(pr["metadata"]["data"]["isDraft"])
        self.assertFalse(pr["head_changed"])
        self.assertEqual(pr["body_reactions"]["status"], "not_requested")
        for name in ("metadata", "reviews", "check_runs", "statuses", "review_threads", "review_request_events",
                     "final_head"):
            self.assertEqual(pr[name]["status"], "complete")
            self.assertEqual(pr[name]["head_sha"], HEAD)
            self.assertTrue(pr[name]["queried_at"].endswith("Z"))
            self.assertTrue(pr[name]["completed_at"].endswith("Z"))
        for call in calls:
            args = call["args"]
            self.assertEqual(call["host"], HOST)
            if args[0] == "api":
                self.assertEqual(args[args.index("--hostname") + 1], HOST)
                if "graphql" in args:
                    self.assertIn("query=", " ".join(args))
                    self.assertNotIn("mutation", " ".join(args))
                else:
                    self.assertEqual(args[args.index("--method") + 1], "GET")
                    self.assertTrue(args[-1].startswith(PREFIX + "/"))
            elif args[0] == "pr":
                self.assertEqual(args[args.index("--repo") + 1], f"{HOST}/{REPO}")
            else:
                self.assertEqual(args, ["auth", "status", "--active", "--hostname", HOST])

    def test_all_rest_lists_are_paginated_and_status_history_is_retained(self):
        replies = default_responses()
        replies.update(default_responses(32))
        replies[f"{PREFIX}/pulls?state=open&per_page=100&page=1"] = response([{"number": 31}] * 100)
        replies[f"{PREFIX}/pulls?state=open&per_page=100&page=2"] = response([{"number": 32}])
        reviews = f"{PREFIX}/pulls/31/reviews?per_page=100&page="
        replies[reviews + "1"] = response([{"id": i, "commit_id": NEW_HEAD, "state": "APPROVED"} for i in range(100)])
        replies[reviews + "2"] = response([{"id": 101, "commit_id": HEAD, "state": "COMMENTED"}])
        checks = f"{PREFIX}/commits/{HEAD}/check-runs?filter=latest&per_page=100&page="
        replies[checks + "1"] = response({"check_runs": [{"id": i, "status": "completed", "conclusion": "success"} for i in range(100)]})
        replies[checks + "2"] = response({"check_runs": [{"id": 101, "status": "queued"}]})
        statuses = f"{PREFIX}/commits/{HEAD}/statuses?per_page=100&page="
        replies[statuses + "1"] = response([{"id": 200 - i, "context": "external", "state": "pending"} for i in range(100)])
        replies[statuses + "2"] = response([{"id": 1, "context": "external", "state": "success"}])
        process, data, _ = self.run_tool(replies, "--open")
        self.assertEqual(process.returncode, 0, process.stderr)
        self.assertEqual(data["count"], 2)
        self.assertEqual(data["selection"]["pages"], 2)
        pr = data["pull_requests"][0]
        for name in ("reviews", "check_runs", "statuses"):
            self.assertEqual(pr[name]["pages"], 2)
            self.assertEqual(len(pr[name]["items"]), 101)
        self.assertFalse(pr["reviews"]["items"][0]["matches_head"])
        self.assertTrue(pr["reviews"]["items"][-1]["matches_head"])
        self.assertEqual(pr["ci_states"]["latest_statuses"], ["pending"])
        self.assertFalse(pr["statuses"]["items"][-1]["latest_for_context"])

    def test_threads_comments_and_optional_reactions_each_paginate(self):
        replies = default_responses()
        replies["threads:31:first"] = connection([{"id": "T1", "isResolved": False, "isOutdated": True}], more=True, cursor="threads-next")
        replies["threads:31:threads-next"] = connection([{"id": "T2", "isResolved": True}])
        replies["comments:T1:first"] = connection([{"id": "C1", "fullDatabaseId": "4194331938", "body": "Inspect this",
                                                    "commit": {"oid": HEAD}}],
                                                  more=True, cursor="comments-next", comments=True)
        replies["comments:T1:comments-next"] = connection([{"id": "C2", "fullDatabaseId": "502"}], comments=True)
        replies["comments:T2:first"] = connection([], comments=True)
        for endpoint in ("issues/31/reactions", "pulls/comments/4194331938/reactions", "pulls/comments/502/reactions"):
            replies[f"{PREFIX}/{endpoint}?per_page=100&page=1"] = response([{"id": i, "content": "+1"} for i in range(100)])
            replies[f"{PREFIX}/{endpoint}?per_page=100&page=2"] = response([{"id": 101, "content": "eyes"}])
        process, data, _ = self.run_tool(replies, extra=("--include-reactions",))
        self.assertEqual(process.returncode, 0, process.stderr)
        pr = data["pull_requests"][0]
        self.assertEqual(pr["review_threads"]["pages"], 2)
        thread = pr["review_threads"]["items"][0]
        self.assertFalse(thread["isResolved"])
        self.assertTrue(thread["isOutdated"])
        self.assertEqual(thread["comments"]["pages"], 2)
        self.assertEqual(thread["comments"]["items"][0]["reactions"]["pages"], 2)
        self.assertEqual(len(pr["body_reactions"]["items"]), 101)

    def test_state_normalization_preserves_neutral_skipped_and_unknown(self):
        replies = default_responses()
        values = [("completed", "success"), ("completed", "failure"), ("in_progress", None),
                  ("queued", None), ("completed", "skipped"), ("completed", "neutral"),
                  ("completed", None), ("mystery", "success"), ("completed", "cancelled"),
                  ("completed", "timed_out"), ("completed", "action_required")]
        replies[f"{PREFIX}/commits/{HEAD}/check-runs?filter=latest&per_page=100&page=1"] = response({
            "check_runs": [{"status": status, "conclusion": conclusion} for status, conclusion in values]})
        replies[f"{PREFIX}/commits/{HEAD}/statuses?per_page=100&page=1"] = response([
            {"context": str(i), "state": state} for i, state in enumerate(["success", "error", "failure", "pending", "neutral", ""])])
        process, data, _ = self.run_tool(replies)
        self.assertEqual(process.returncode, 0)
        self.assertEqual(data["pull_requests"][0]["ci_states"], {
            "check_runs": ["success", "failure", "pending", "pending", "skipped", "neutral", "unknown", "unknown", "failure", "failure", "failure"],
            "latest_statuses": ["success", "failure", "failure", "pending", "unknown", "unknown"],
        })

    def test_rest_failure_after_page_preserves_evidence_and_other_prs(self):
        replies = default_responses()
        replies[f"{PREFIX}/pulls?state=open&per_page=100&page=1"] = response([{"number": 31}] * 100)
        replies[f"{PREFIX}/pulls?state=open&per_page=100&page=2"] = response(code=1, stderr="HTTP 403")
        endpoint = f"{PREFIX}/pulls/31/reviews?per_page=100&page="
        replies[endpoint + "1"] = response([{"id": i} for i in range(100)])
        replies[endpoint + "2"] = response(code=1, stderr="HTTP 502")
        process, data, _ = self.run_tool(replies, "--open")
        self.assertEqual(process.returncode, 1)
        self.assertEqual(data["selection"]["status"], "partial")
        self.assertEqual(data["selection"]["errors"][0]["page"], 2)
        pr = data["pull_requests"][0]
        self.assertEqual(pr["reviews"]["status"], "partial")
        self.assertEqual(len(pr["reviews"]["items"]), 100)
        self.assertEqual(pr["check_runs"]["status"], "complete")
        self.assertFalse(pr["head_changed"])

    def test_failed_first_page_differs_from_empty_list(self):
        replies = default_responses()
        replies[f"{PREFIX}/commits/{HEAD}/check-runs?filter=latest&per_page=100&page=1"] = response(code=1, stderr="HTTP 403")
        process, data, _ = self.run_tool(replies)
        self.assertEqual(process.returncode, 1)
        pr = data["pull_requests"][0]
        self.assertEqual(pr["check_runs"]["status"], "failed")
        self.assertEqual(pr["check_runs"]["items"], [])
        self.assertEqual(pr["statuses"]["status"], "complete")
        self.assertEqual(pr["statuses"]["items"], [])

    def test_graphql_partial_data_survives_errors_and_comment_failure(self):
        replies = default_responses()
        replies["threads:31:first"] = connection([{"id": "T1"}], more=True, cursor="next", errors=[{"message": "restricted field"}])
        replies["threads:31:next"] = connection([{"id": "T2"}])
        replies["comments:T1:first"] = connection([{"id": "C1"}], more=True, cursor="next", comments=True)
        replies["comments:T1:next"] = response({"data": {"node": None}, "errors": [{"message": "denied"}]}, code=1)
        replies["comments:T2:first"] = connection([], comments=True)
        process, data, _ = self.run_tool(replies)
        self.assertEqual(process.returncode, 1)
        threads = data["pull_requests"][0]["review_threads"]
        self.assertEqual(threads["status"], "partial")
        self.assertEqual(len(threads["items"]), 2)
        comments = threads["items"][0]["comments"]
        self.assertEqual(comments["status"], "partial")
        self.assertEqual(comments["items"], [{"id": "C1"}])
        self.assertEqual(comments["errors"][0]["cursor"], "next")

    def test_review_request_events_are_collected_with_requested_reviewer(self):
        replies = default_responses()
        replies["requests:31:first"] = connection([{
            "id": "RRE1", "createdAt": "2026-10-05T09:00:00Z",
            "requestedReviewer": {"__typename": "User", "login": "alice"},
        }], requests=True)
        process, data, _ = self.run_tool(replies)
        self.assertEqual(process.returncode, 0, process.stderr)
        pr = data["pull_requests"][0]
        events = pr["review_request_events"]
        self.assertEqual(events["status"], "complete")
        self.assertEqual(events["items"][0]["requestedReviewer"]["login"], "alice")
        self.assertEqual(events["items"][0]["createdAt"], "2026-10-05T09:00:00Z")
        self.assertEqual(pr["status"], "complete")

    def test_review_request_query_error_marks_pr_partial(self):
        replies = default_responses()
        replies["requests:31:first"] = response({"data": {"repository": {"pullRequest": None}},
                                                 "errors": [{"message": "Resource not accessible"}]}, code=1)
        process, data, _ = self.run_tool(replies)
        self.assertEqual(process.returncode, 1)
        pr = data["pull_requests"][0]
        events = pr["review_request_events"]
        self.assertEqual(events["status"], "failed")
        self.assertIn("graphql", [item["kind"] for item in events["errors"]])
        self.assertEqual(pr["review_threads"]["status"], "complete")
        self.assertEqual(pr["status"], "partial")

    def test_repeated_cursor_is_partial_not_an_infinite_loop(self):
        replies = default_responses()
        replies["threads:31:first"] = connection([], more=True, cursor="same")
        replies["threads:31:same"] = connection([], more=True, cursor="same")
        process, data, calls = self.run_tool(replies)
        self.assertEqual(process.returncode, 1)
        threads = data["pull_requests"][0]["review_threads"]
        self.assertEqual(threads["errors"][0]["kind"], "pagination")
        self.assertEqual(sum(call["key"] == "threads:31:same" for call in calls), 1)

    def test_final_head_change_marks_mixed_observations_without_relabeling(self):
        replies = default_responses()
        replies["final:31"] = response({"headRefOid": NEW_HEAD})
        process, data, _ = self.run_tool(replies)
        self.assertEqual(process.returncode, 1)
        pr = data["pull_requests"][0]
        self.assertTrue(pr["head_changed"])
        self.assertEqual(pr["head_sha"], HEAD)
        self.assertEqual(pr["reviews"]["head_sha"], HEAD)
        self.assertEqual(pr["final_head"]["head_sha"], NEW_HEAD)
        self.assertEqual(pr["status"], "partial")

    def test_unconfirmed_final_head_is_unknown_not_unchanged(self):
        replies = default_responses()
        replies["final:31"] = response(code=1, stderr="network unavailable")
        process, data, _ = self.run_tool(replies)
        self.assertEqual(process.returncode, 1)
        self.assertIsNone(data["pull_requests"][0]["head_changed"])
        self.assertEqual(data["pull_requests"][0]["final_head"]["status"], "failed")

    def test_missing_initial_head_skips_sha_queries_but_continues_other_prs(self):
        replies = default_responses()
        replies.update(default_responses(32))
        replies["metadata:31"] = response({"number": 31})
        process, data, calls = self.run_tool(replies, "--pr", "31", "--pr", "32")
        self.assertEqual(process.returncode, 1)
        self.assertEqual(data["pull_requests"][0]["reviews"]["status"], "skipped")
        self.assertEqual(data["pull_requests"][1]["status"], "complete")
        self.assertFalse(any("/commits/None/" in call["key"] for call in calls))

    def test_invalid_json_is_structured_not_empty(self):
        replies = default_responses()
        replies[f"{PREFIX}/pulls/31/reviews?per_page=100&page=1"] = response(raw="not JSON")
        process, data, _ = self.run_tool(replies)
        self.assertEqual(process.returncode, 1)
        reviews = data["pull_requests"][0]["reviews"]
        self.assertEqual(reviews["status"], "failed")
        self.assertEqual(reviews["errors"][0]["kind"], "response")

    def test_open_empty_is_complete_but_failed_selection_is_partial(self):
        replies = {"auth": response({}), f"{PREFIX}/pulls?state=open&per_page=100&page=1": response([])}
        process, data, _ = self.run_tool(replies, "--open")
        self.assertEqual(process.returncode, 0)
        self.assertEqual(data["pull_requests"], [])
        self.assertEqual(data["selection"]["status"], "complete")
        replies[f"{PREFIX}/pulls?state=open&per_page=100&page=1"] = response(code=1, stderr="HTTP 404")
        process, data, _ = self.run_tool(replies, "--open")
        self.assertEqual(process.returncode, 1)
        self.assertEqual(data["selection"]["status"], "failed")
        self.assertEqual(data["pull_requests"], [])

    def test_auth_failure_is_prerequisite_error_without_api_calls(self):
        process, data, calls = self.run_tool({"auth": response(code=1, stderr="not authenticated")})
        self.assertEqual(process.returncode, 2)
        self.assertEqual(data["status"], "failed")
        self.assertEqual(data["auth"]["errors"][0]["kind"], "prerequisite")
        self.assertEqual([call["key"] for call in calls], ["auth"])

    def test_argument_errors_do_not_call_gh(self):
        for extra in (("--host", "https://github.acme.test"), ("--repo", "other/owner/repo"),
                      ("--pr", "0"), ("--open",)):
            with self.subTest(extra=extra):
                process, data, calls = self.run_tool(extra=extra)
                self.assertEqual(process.returncode, 2)
                self.assertIsNone(data)
                self.assertEqual(calls, [])


if __name__ == "__main__":
    unittest.main()
