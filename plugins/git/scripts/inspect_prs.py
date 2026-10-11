#!/usr/bin/env python3
"""GitHub PR 상태 근거를 원격 쓰기 없이 수집해 JSON으로 출력한다.

사용: inspect_prs.py --host HOST --repo OWNER/REPO (--open | --pr NUMBER ...) [--include-reactions]
종료 코드 0: 요청한 관찰을 모두 수집했고 마지막 head가 처음과 같다. 병합 승인이나 필수 check 완전성 판정은 아니다.
종료 코드 1: 일부·전체 조회 실패, head 변경 또는 마지막 head 미확인. JSON에 확인한 근거와 오류를 남긴다.
종료 코드 2: 인자 오류(stderr) 또는 gh·인증 전제 조건 실패(JSON).
표준 라이브러리와 gh만 사용하며 설치·로그인·계정 전환을 하지 않는다.
"""

import argparse
from datetime import datetime, timezone
import json
import os
import re
import subprocess


GH_TIMEOUT = 30
COMMENT_ID = re.compile(r"[1-9][0-9]*")
METADATA_FIELDS = (
    "number,title,url,state,isDraft,baseRefName,baseRefOid,headRefName,headRefOid,"
    "headRepository,headRepositoryOwner,isCrossRepository,mergeStateStatus,reviewDecision,reviewRequests"
)
THREADS_QUERY = """query InspectThreads($owner:String!,$name:String!,$number:Int!,$cursor:String) {
  repository(owner:$owner,name:$name) { pullRequest(number:$number) {
    reviewThreads(first:100,after:$cursor) {
      nodes { id isResolved isOutdated path line originalLine startLine diffSide }
      pageInfo { hasNextPage endCursor }
    }
  } }
}"""
COMMENTS_QUERY = """query InspectComments($id:ID!,$cursor:String) {
  node(id:$id) { ... on PullRequestReviewThread {
    comments(first:100,after:$cursor) {
      nodes { id fullDatabaseId url body createdAt updatedAt author { login }
        commit { oid } originalCommit { oid } pullRequestReview { id } }
      pageInfo { hasNextPage endCursor }
    }
  } }
}"""
REVIEW_REQUESTS_QUERY = """query InspectReviewRequests($owner:String!,$name:String!,$number:Int!,$cursor:String) {
  repository(owner:$owner,name:$name) { pullRequest(number:$number) {
    timelineItems(itemTypes:[REVIEW_REQUESTED_EVENT],first:100,after:$cursor) {
      nodes { ... on ReviewRequestedEvent { id createdAt requestedReviewer { __typename ... on User { login } ... on Team { slug } ... on Bot { login } ... on Mannequin { login } } } }
      pageInfo { hasNextPage endCursor }
    }
  } }
}"""


def now():
    return datetime.now(timezone.utc).isoformat().replace("+00:00", "Z")


def observation(head=None, listing=False):
    result = {"status": "complete", "head_sha": head, "queried_at": now(),
              "completed_at": None, "pages": 0, "errors": []}
    result["items" if listing else "data"] = [] if listing else None
    return result


def finish(result):
    if result["errors"]:
        result["status"] = "partial" if result["pages"] else "failed"
    result["completed_at"] = now()
    return result


def error(result, kind, message, **details):
    result["errors"].append({"kind": kind, "message": message, **details})


def check_state(item):
    status = str(item.get("status", "")).lower()
    conclusion = str(item.get("conclusion") or "").lower()
    if status in ("queued", "in_progress", "waiting", "pending", "requested"):
        return "pending"
    if status != "completed":
        return "unknown"
    if conclusion == "success":
        return "success"
    if conclusion in ("failure", "timed_out", "cancelled", "action_required", "startup_failure", "stale"):
        return "failure"
    return conclusion if conclusion in ("skipped", "neutral") else "unknown"


def status_state(item):
    state = str(item.get("state", "")).lower()
    if state in ("error", "failure"):
        return "failure"
    return state if state in ("success", "pending") else "unknown"


class Collector:
    def __init__(self, args):
        self.args = args
        self.owner, self.name = args.repo.split("/")
        self.prefix = f"repos/{args.repo}"
        self.env = dict(os.environ, GH_HOST=args.host, GH_PROMPT_DISABLED="1")

    def run(self, args):
        try:
            return subprocess.run(["gh", *args], env=self.env, stdin=subprocess.DEVNULL, capture_output=True,
                                  text=True, errors="replace", timeout=GH_TIMEOUT, check=False)
        except OSError as exc:
            return subprocess.CompletedProcess(["gh", *args], 127, "", str(exc))
        except subprocess.TimeoutExpired:
            return subprocess.CompletedProcess(["gh", *args], 124, "", f"gh: timed out after {GH_TIMEOUT}s")

    def request(self, args, result, location, graphql=False):
        process = self.run(args)
        if process.returncode:
            message = next((line.strip() for line in process.stderr.splitlines() if line.strip()),
                           f"gh exited {process.returncode}")
            error(result, "command", message, exit_code=process.returncode, **location)
            if not graphql:
                return None
        try:
            payload = json.loads(process.stdout)
        except json.JSONDecodeError:
            error(result, "response", "invalid JSON response", **location)
            return None
        if graphql and isinstance(payload, dict) and payload.get("errors"):
            error(result, "graphql", "GraphQL returned errors", details=payload["errors"], **location)
        return payload

    def metadata(self, number, final=False):
        result = observation(None)
        fields = "headRefOid" if final else METADATA_FIELDS
        payload = self.request(["pr", "view", str(number), "--repo",
                                f"{self.args.host}/{self.args.repo}", "--json", fields], result, {})
        if payload is not None:
            if not isinstance(payload, dict) or not isinstance(payload.get("headRefOid"), str) or not payload["headRefOid"]:
                error(result, "response", "missing PR headRefOid")
            else:
                result["data"] = payload
                result["head_sha"] = payload["headRefOid"]
                result["pages"] = 1
        return finish(result)

    def rest(self, endpoint, head=None, key=None):
        result = observation(head, listing=True)
        page = 1
        while True:
            separator = "&" if "?" in endpoint else "?"
            url = f"{endpoint}{separator}per_page=100&page={page}"
            payload = self.request(["api", "--hostname", self.args.host, "--method", "GET", url],
                                   result, {"page": page})
            if payload is None:
                break
            items = payload.get(key) if key and isinstance(payload, dict) else payload if not key else None
            if not isinstance(items, list) or any(not isinstance(item, dict) for item in items):
                error(result, "response", "expected an object list", page=page)
                break
            result["items"].extend(items)
            result["pages"] += 1
            if len(items) < 100:
                break
            page += 1
        return finish(result)

    def connection(self, query, variables, path, head):
        result = observation(head, listing=True)
        cursor = None
        seen = set()
        while True:
            args = ["api", "--hostname", self.args.host, "graphql", "-f", f"query={query}"]
            for key, value in variables.items():
                args.extend(["-F" if isinstance(value, int) else "-f", f"{key}={value}"])
            if cursor is not None:
                args.extend(["-f", f"cursor={cursor}"])
            payload = self.request(args, result, {"cursor": cursor}, graphql=True)
            if payload is None:
                break
            connection = payload
            for key in ("data", *path):
                connection = connection.get(key) if isinstance(connection, dict) else None
            if not isinstance(connection, dict) or not isinstance(connection.get("nodes"), list):
                error(result, "response", "missing GraphQL connection", cursor=cursor)
                break
            nodes = connection["nodes"]
            valid = [node for node in nodes if isinstance(node, dict) and node.get("id")]
            result["items"].extend(valid)
            result["pages"] += 1
            if len(valid) != len(nodes):
                error(result, "response", "missing GraphQL node", cursor=cursor)
            info = connection.get("pageInfo")
            if not isinstance(info, dict) or not isinstance(info.get("hasNextPage"), bool):
                error(result, "pagination", "missing pageInfo", cursor=cursor)
                break
            if not info["hasNextPage"]:
                break
            following = info.get("endCursor")
            if not isinstance(following, str) or not following or following in seen:
                error(result, "pagination", "missing or repeated endCursor", cursor=cursor)
                break
            seen.add(following)
            cursor = following
        return finish(result)

    def inspect(self, number):
        metadata = self.metadata(number)
        head = metadata["head_sha"]
        result = {"number": number, "metadata": metadata, "head_sha": head,
                  "required_checks": {"status": "unverified", "reason": "branch protection and rulesets not collected"}}
        observations = [metadata]
        if head:
            reviews = self.rest(f"{self.prefix}/pulls/{number}/reviews", head)
            for review in reviews["items"]:
                review["matches_head"] = review.get("commit_id") == head if review.get("commit_id") else None
            checks = self.rest(f"{self.prefix}/commits/{head}/check-runs?filter=latest", head, "check_runs")
            for check in checks["items"]:
                check["normalized_state"] = check_state(check)
            statuses = self.rest(f"{self.prefix}/commits/{head}/statuses", head)
            contexts = set()
            for status in statuses["items"]:
                status["normalized_state"] = status_state(status)
                context = status.get("context")
                status["latest_for_context"] = context not in contexts if context else None
                if context:
                    contexts.add(context)
            threads = self.connection(THREADS_QUERY, {"owner": self.owner, "name": self.name, "number": number},
                                      ("repository", "pullRequest", "reviewThreads"), head)
            requests = self.connection(REVIEW_REQUESTS_QUERY, {"owner": self.owner, "name": self.name, "number": number},
                                       ("repository", "pullRequest", "timelineItems"), head)
            observations.extend([reviews, checks, statuses, threads, requests])
            for thread in threads["items"]:
                comments = self.connection(COMMENTS_QUERY, {"id": thread["id"]}, ("node", "comments"), head)
                thread["comments"] = comments
                observations.append(comments)
                if self.args.include_reactions:
                    for comment in comments["items"]:
                        comment_id = comment.get("fullDatabaseId")
                        if isinstance(comment_id, str) and COMMENT_ID.fullmatch(comment_id):
                            reactions = self.rest(f"{self.prefix}/pulls/comments/{comment_id}/reactions", head)
                        else:
                            reactions = observation(head, listing=True)
                            error(reactions, "response", "missing comment fullDatabaseId for reactions")
                            finish(reactions)
                        comment["reactions"] = reactions
                        observations.append(reactions)
            result.update(reviews=reviews, check_runs=checks, statuses=statuses, review_threads=threads)
            result["review_request_events"] = requests
            result["ci_states"] = {
                "check_runs": [item["normalized_state"] for item in checks["items"]],
                "latest_statuses": [item["normalized_state"] for item in statuses["items"]
                                    if item["latest_for_context"] is not False],
            }
            if self.args.include_reactions:
                reactions = self.rest(f"{self.prefix}/issues/{number}/reactions", head)
                observations.append(reactions)
                result["body_reactions"] = reactions
            else:
                result["body_reactions"] = {"status": "not_requested"}
        else:
            for name in ("reviews", "check_runs", "statuses", "review_threads", "review_request_events", "body_reactions"):
                result[name] = {"status": "skipped", "reason": "initial head unavailable"}
            result["ci_states"] = None
        final = self.metadata(number, final=True)
        observations.append(final)
        result["final_head"] = final
        result["head_changed"] = head != final["head_sha"] if head and final["head_sha"] else None
        result["status"] = "complete" if (all(item["status"] == "complete" for item in observations)
                                               and result["head_changed"] is False) else "partial"
        return result

    def collect(self):
        result = {"schema_version": 1, "host": self.args.host, "repository": self.args.repo,
                  "scope": "open" if self.args.open else "specified", "queried_at": now(),
                  "completed_at": None, "status": "complete", "count": 0, "pull_requests": []}
        auth = observation()
        process = self.run(["auth", "status", "--active", "--hostname", self.args.host])
        if process.returncode:
            message = next((line.strip() for line in process.stderr.splitlines() if line.strip()),
                           f"gh exited {process.returncode}")
            error(auth, "prerequisite", message, exit_code=process.returncode)
        else:
            auth["pages"] = 1
            auth["data"] = {"authenticated": True}
        result["auth"] = finish(auth)
        if auth["status"] != "complete":
            result.update(status="failed", completed_at=now(), selection={"status": "skipped", "reason": "auth unavailable"})
            return result, 2
        if self.args.open:
            selection = self.rest(f"{self.prefix}/pulls?state=open")
            numbers = []
            for item in selection["items"]:
                number = item.get("number")
                if isinstance(number, int) and not isinstance(number, bool) and number > 0:
                    numbers.append(number)
                else:
                    error(selection, "response", "missing PR number in open list")
            finish(selection)
            result["selection"] = selection
        else:
            numbers = self.args.pr
            result["selection"] = {"status": "complete", "numbers": numbers}
        for number in dict.fromkeys(numbers):
            result["pull_requests"].append(self.inspect(number))
        if result["selection"]["status"] != "complete" or any(pr["status"] != "complete" for pr in result["pull_requests"]):
            result["status"] = "partial"
        result["count"] = len(result["pull_requests"])
        result["completed_at"] = now()
        return result, 0 if result["status"] == "complete" else 1


def positive_number(value):
    if not value.isdigit() or int(value) < 1:
        raise argparse.ArgumentTypeError("PR number must be a positive integer")
    return int(value)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--host", required=True, help="GitHub hostname, without scheme or path")
    parser.add_argument("--repo", required=True, help="OWNER/REPO on the selected host")
    scope = parser.add_mutually_exclusive_group(required=True)
    scope.add_argument("--open", action="store_true", help="collect every page of open PRs")
    scope.add_argument("--pr", type=positive_number, action="append", help="PR number; repeat for several PRs")
    parser.add_argument("--include-reactions", action="store_true", help="collect PR-body and review-thread-comment reactions")
    args = parser.parse_args()
    if not re.fullmatch(r"[A-Za-z0-9](?:[A-Za-z0-9.-]*[A-Za-z0-9])?", args.host):
        parser.error("--host must be a hostname without scheme or path")
    if not re.fullmatch(r"[A-Za-z0-9_.-]+/[A-Za-z0-9_.-]+", args.repo) or any(part in (".", "..") for part in args.repo.split("/")):
        parser.error("--repo must be OWNER/REPO")
    result, code = Collector(args).collect()
    print(json.dumps(result, ensure_ascii=False, indent=2))
    return code


if __name__ == "__main__":
    raise SystemExit(main())
