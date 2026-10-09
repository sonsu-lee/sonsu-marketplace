#!/usr/bin/env python3
"""Read-only GitHub PR metadata and exact local Git revision snapshots.

capture [PR] [--repository HOST/OWNER/REPO] --repo PATH [--output FILE]
compare --against FILE --repo PATH [--output FILE]
JSON stdout: schema_version, status, snapshot, comparison (compare only).
Exit 0: stable open PR; 1: changed/closed PR; 2: input, Git, gh or data failure.
--output exclusively creates a JSON file; no source/ref/remote writes, fetch,
worktrees, diff packaging, review submission or publication confirmation.
"""

import argparse
import json
import os
from pathlib import Path
import re
import subprocess
import sys
from urllib.parse import urlsplit


SHA = re.compile(r"[0-9a-f]{40}(?:[0-9a-f]{24})?\Z")
REPOSITORY = re.compile(r"[A-Za-z0-9_.-]+/[A-Za-z0-9_.-]+\Z")
HOST = re.compile(r"[A-Za-z0-9][A-Za-z0-9.-]*(?::[0-9]+)?\Z")


class Failure(Exception):
    pass


def run(args, cwd):
    env = dict(os.environ, GIT_OPTIONAL_LOCKS="0", GIT_NO_LAZY_FETCH="1",
               GIT_NO_REPLACE_OBJECTS="1", GH_PROMPT_DISABLED="1")
    try:
        result = subprocess.run(args, cwd=cwd, env=env, capture_output=True,
                                text=True, check=False)
    except OSError as exc:
        raise Failure(f"{args[0]}: {exc}") from exc
    if result.returncode:
        detail = result.stderr.strip() or f"exit {result.returncode}"
        raise Failure(f"{' '.join(args[:3])}: {detail}")
    return result.stdout.strip()


def json_run(args, cwd):
    try:
        return json.loads(run(args, cwd))
    except json.JSONDecodeError as exc:
        raise Failure(f"{args[0]} returned invalid JSON") from exc


def repository_url(url, pr=False):
    if not isinstance(url, str):
        raise Failure("repository/PR URL must be a string")
    parsed = urlsplit(url)
    parts = parsed.path.strip("/").split("/")
    if (parsed.scheme != "https" or not HOST.fullmatch(parsed.netloc)
            or parsed.query or parsed.fragment or len(parts) != (4 if pr else 2)
            or not REPOSITORY.fullmatch("/".join(parts[:2]))):
        raise Failure("expected an HTTPS GitHub repository or PR URL")
    if pr and (parts[2] != "pull" or not parts[3].isdigit() or int(parts[3]) < 1):
        raise Failure("expected /OWNER/REPO/pull/NUMBER")
    return parsed.netloc.lower(), "/".join(parts[:2]), int(parts[3]) if pr else None


def repository_arg(value):
    parts = value.split("/", 1)
    if len(parts) != 2 or not HOST.fullmatch(parts[0]) or not REPOSITORY.fullmatch(parts[1]):
        raise Failure("--repository must be HOST/OWNER/REPO")
    return parts[0].lower(), parts[1]


def target(args, root):
    if args.pr and args.pr.startswith("https://"):
        host, repo, number = repository_url(args.pr, pr=True)
        if args.repository and repository_arg(args.repository) != (host, repo):
            raise Failure("PR URL and --repository disagree")
        return host, repo, number
    if args.repository:
        host, repo = repository_arg(args.repository)
    else:
        info = json_run(["gh", "repo", "view", "--json", "url"], root)
        host, repo, _ = repository_url(info["url"])
    if args.pr:
        if not args.pr.isdigit() or int(args.pr) < 1:
            raise Failure("PR must be a positive number or HTTPS PR URL")
        return host, repo, int(args.pr)
    branch = run(["git", "symbolic-ref", "--quiet", "--short", "HEAD"], root)
    prs = json_run(["gh", "pr", "list", "--repo", f"{host}/{repo}", "--state", "open",
                    "--head", branch, "--limit", "2", "--json", "number"], root)
    if not isinstance(prs, list) or len(prs) != 1:
        raise Failure("current branch must identify exactly one open PR; specify a PR URL")
    number = prs[0]["number"]
    if type(number) is not int or number < 1:
        raise Failure("invalid PR number returned by gh")
    return host, repo, number


def api(root, host, endpoint, pages=False):
    args = ["gh", "api", endpoint, "--hostname", host, "--method", "GET"]
    if pages:
        args += ["--paginate", "--slurp"]
    value = json_run(args, root)
    if not pages:
        return value
    if not isinstance(value, list) or any(not isinstance(page, list) for page in value):
        raise Failure("invalid paginated GitHub response")
    return [item for page in value for item in page]


def metadata(raw, host, repo, number):
    if raw["number"] != number or raw["base"]["repo"]["full_name"].lower() != repo.lower():
        raise Failure("PR response does not match requested base repository/number")
    url_host, url_repo, url_number = repository_url(raw["html_url"], pr=True)
    if (url_host, url_repo.lower(), url_number) != (host, repo.lower(), number):
        raise Failure("PR response URL does not match requested target")
    if raw["state"] not in ("open", "closed") or type(raw["merged"]) is not bool:
        raise Failure("invalid PR state")
    result = {"host": host, "repository": repo, "number": number,
              "url": raw["html_url"], "state": "merged" if raw["merged"] else raw["state"]}
    for side in ("base", "head"):
        node = raw[side]
        if not isinstance(node["sha"], str) or not SHA.fullmatch(node["sha"]):
            raise Failure(f"invalid {side} SHA")
        if not isinstance(node["ref"], str):
            raise Failure(f"invalid {side} ref")
        result[side] = {"sha": node["sha"], "ref": node["ref"],
                        "repository": node["repo"]["full_name"] if node["repo"] else None}
    return result


def ids(items):
    values = [item["id"] for item in items]
    if any(type(value) is not int or value < 1 for value in values):
        raise Failure("invalid review/comment ID")
    return sorted(set(values))


def collect(root, host, repo, number):
    endpoint = f"repos/{repo}/pulls/{number}"
    first = metadata(api(root, host, endpoint), host, repo, number)
    reviews = ids(api(root, host, f"{endpoint}/reviews?per_page=100", pages=True))
    comments = ids(api(root, host, f"{endpoint}/comments?per_page=100", pages=True))
    if run(["git", "rev-parse", "--is-shallow-repository"], root) != "false":
        raise Failure("shallow history cannot establish an exact merge base; prepare full history separately")
    fixed = {}
    for side in ("base", "head"):
        sha = first[side]["sha"]
        resolved = run(["git", "rev-parse", "--verify", f"{sha}^{{commit}}"], root)
        if resolved != sha:
            raise Failure(f"local {side} commit does not match GitHub SHA")
        fixed[side] = sha
    bases = run(["git", "merge-base", "--all", fixed["base"], fixed["head"]], root).splitlines()
    if len(bases) != 1 or not SHA.fullmatch(bases[0]):
        raise Failure("an unambiguous exact merge base is required")
    fixed["merge_base"] = bases[0]
    last = metadata(api(root, host, endpoint), host, repo, number)
    return {**first, "merge_base": bases[0], "fixed_shas": fixed,
            "existing_review_ids": reviews, "existing_inline_comment_ids": comments,
            "collection_stable": first == last, "observed_after": last}


def load_snapshot(path):
    try:
        data = json.loads(Path(path).read_text(encoding="utf-8"))
    except (OSError, UnicodeError, json.JSONDecodeError) as exc:
        raise Failure(f"cannot read snapshot: {exc}") from exc
    if not isinstance(data, dict) or data.get("schema_version") != 1:
        raise Failure("unsupported snapshot schema")
    snapshot = data["snapshot"]
    if (data.get("status") != "ok" or snapshot["collection_stable"] is not True
            or snapshot["state"] != "open" or snapshot["observed_after"]["state"] != "open"):
        raise Failure("comparison requires a successful stable open snapshot")
    host, repo, number = repository_url(snapshot["url"], pr=True)
    if (host, repo.lower(), number) != (snapshot["host"], snapshot["repository"].lower(), snapshot["number"]):
        raise Failure("snapshot target is inconsistent")
    for key in ("base", "head", "merge_base"):
        sha = snapshot["fixed_shas"][key]
        if not isinstance(sha, str) or not SHA.fullmatch(sha):
            raise Failure("snapshot contains an invalid fixed SHA")
        recorded = snapshot["merge_base"] if key == "merge_base" else snapshot[key]["sha"]
        if sha != recorded or (key != "merge_base" and sha != snapshot["observed_after"][key]["sha"]):
            raise Failure("snapshot fixed SHA is inconsistent")
    return snapshot


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    commands = parser.add_subparsers(dest="command", required=True)
    capture = commands.add_parser("capture", help="collect a new fixed metadata snapshot")
    capture.add_argument("pr", nargs="?", help="PR number or HTTPS URL; otherwise unique current-branch PR")
    capture.add_argument("--repository", help="HOST/OWNER/REPO; otherwise gh repo view")
    compare = commands.add_parser("compare", help="recollect the saved target and compare revisions")
    compare.add_argument("--against", required=True, type=Path)
    for command in (capture, compare):
        command.add_argument("--repo", type=Path, default=Path.cwd(), help="local Git checkout with exact history")
        command.add_argument("--output", type=Path, help="exclusively create a saved JSON result")
    args = parser.parse_args()
    try:
        if args.output and args.output.exists():
            raise Failure(f"output already exists: {args.output}")
        root = run(["git", "-C", str(args.repo), "rev-parse", "--show-toplevel"], None)
        before = load_snapshot(args.against) if args.command == "compare" else None
        identity = ((before["host"], before["repository"], before["number"])
                    if before else target(args, root))
        snapshot = collect(root, *identity)
        changed = not snapshot["collection_stable"] or snapshot["state"] != "open"
        result = {"schema_version": 1, "snapshot": snapshot}
        if before:
            changed_fields = [key for key in ("base", "head", "merge_base")
                              if before["fixed_shas"][key] != snapshot["fixed_shas"][key]]
            if before["state"] != snapshot["state"]:
                changed_fields.append("state")
            changed = changed or bool(changed_fields)
            result["comparison"] = {
                "unchanged": not changed, "changed_fields": changed_fields,
                "before": {"state": before["state"], "fixed_shas": before["fixed_shas"]},
                "after": {"state": snapshot["state"], "fixed_shas": snapshot["fixed_shas"]},
                "new_review_ids": sorted(set(snapshot["existing_review_ids"]) - set(before["existing_review_ids"])),
                "new_inline_comment_ids": sorted(set(snapshot["existing_inline_comment_ids"]) - set(before["existing_inline_comment_ids"]))}
        result["status"] = "changed" if changed else "ok"
        code = 1 if changed else 0
        text = json.dumps(result, ensure_ascii=True, indent=2) + "\n"
        if args.output:
            with args.output.open("x", encoding="utf-8") as stream:
                stream.write(text)
    except (Failure, OSError, ValueError, KeyError, TypeError) as exc:
        text = json.dumps({"schema_version": 1, "status": "blocked", "error": str(exc)}) + "\n"
        code = 2
    sys.stdout.write(text)
    return code


if __name__ == "__main__":
    sys.exit(main())
