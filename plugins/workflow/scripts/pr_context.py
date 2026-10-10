#!/usr/bin/env python3
"""PR 초안·게시에 필요한 저장소 상태를 읽기 전용으로 수집해 JSON으로 출력한다."""

import argparse
import json
import os
from pathlib import Path
import re
import subprocess
import sys


BLOCKERS = ("detached-head", "operation-in-progress", "base-unresolved", "base-not-ancestor", "no-merge-base",
            "head-equals-base", "empty-range", "existing-pr")
UNVERIFIED = ("github-repository", "auth", "remote-head", "default-branch", "templates", "existing-prs")
OPERATIONS = (("MERGE_HEAD", "merge"), ("rebase-merge", "rebase"), ("rebase-apply", "rebase"),
              ("CHERRY_PICK_HEAD", "cherry-pick"), ("REVERT_HEAD", "revert"), ("BISECT_LOG", "bisect"))
REMOTE_URL = (
    re.compile(r"^git@([^:]+):([^/]+)/(.+?)(\.git)?$"),
    re.compile(r"^ssh://git@([^/]+)/([^/]+)/(.+?)(\.git)?$"),
    re.compile(r"^https://([^/]+)/([^/]+)/(.+?)(\.git)?/?$"),
)
URL_CREDENTIALS = re.compile(r"^(https?://)[^/]*@", re.IGNORECASE)
LOCAL_TIMEOUT = 120
NETWORK_TIMEOUT = 30
TEMPLATE = (
    re.compile(r"^(\.github/|docs/)?pull_request_template\.(md|txt)$", re.IGNORECASE),
    re.compile(r"^(\.github/|docs/)?pull_request_template/[^/]+\.(md|txt)$", re.IGNORECASE),
)


class LocalFailure(Exception):
    """로컬 필수 조건 실패. 메시지를 stderr에 쓰고 2로 종료한다."""


def run(args, cwd=None, env=None, timeout=LOCAL_TIMEOUT):
    try:
        return subprocess.run(args, cwd=cwd, env=env, stdin=subprocess.DEVNULL, capture_output=True, text=True,
                              errors="surrogateescape", timeout=timeout, check=False)
    except FileNotFoundError:
        return subprocess.CompletedProcess(args, 127, "", f"{args[0]}: command not found")
    except subprocess.TimeoutExpired:
        return subprocess.CompletedProcess(args, 124, "", f"{args[0]}: timed out after {timeout}s")


def first_line(result):
    for text in (result.stderr, result.stdout):
        for line in text.splitlines():
            if line.strip():
                return line.strip()
    return f"exit {result.returncode}"


def template_candidates(paths):
    """기본 본문이 되는 단일 파일을 위치 순서로 먼저, `PULL_REQUEST_TEMPLATE/` 양식을 그 뒤에 둔다."""
    def order(path):
        lower = path.lower()
        location = 0 if lower.startswith(".github/") else 2 if lower.startswith("docs/") else 1
        return ("pull_request_template/" in lower, location, lower, path)

    return sorted((path for path in paths if any(pattern.match(path) for pattern in TEMPLATE)), key=order)


class Collector:
    def __init__(self, repo, offline):
        self.offline = offline
        self.errors = []
        self.blockers = set()
        top = run(["git", "-C", str(repo), "rev-parse", "--show-toplevel"])
        if top.returncode:
            raise LocalFailure(f"not a git repository: {repo}")
        self.root = top.stdout.strip()

    def git(self, *args):
        return run(["git", "-C", self.root, *args])

    def git_out(self, *args):
        result = self.git(*args)
        return result.stdout.strip() if result.returncode == 0 else None

    def git_required(self, *args):
        result = self.git(*args)
        if result.returncode:
            raise LocalFailure(f"git failed: git {' '.join(args)}")
        return result.stdout

    def online_step(self, args, env=None, expected_failure=None):
        """온라인 명령을 실행하고 실패하면 errors에 기록한 뒤 None을 돌려준다.

        expected_failure가 실패 메시지에 들어 있으면 판정 결과로 보고 errors에 남기지 않는다.
        """
        result = run(args, cwd=self.root, env=env, timeout=NETWORK_TIMEOUT)
        if result.returncode:
            message = first_line(result)
            if not (expected_failure and expected_failure in message):
                self.errors.append({"step": " ".join(args[:3]), "message": message})
            return None, message
        return result, None

    def git_network_env(self):
        """원격 git이 자격 증명이나 SSH host key 확인을 묻지 않고 실패하게 한다. 사용자 SSH 명령 설정은 유지한다."""
        env = dict(os.environ, GIT_TERMINAL_PROMPT="0")
        if not (os.environ.get("GIT_SSH_COMMAND") or os.environ.get("GIT_SSH")
                or self.git_out("config", "core.sshCommand")):
            env["GIT_SSH_COMMAND"] = "ssh -o BatchMode=yes"
        return env

    def gh_json(self, github, endpoint, expected_failure=None):
        result, error = self.online_step(["gh", "api", endpoint, "--hostname", github["host"]],
                                         expected_failure=expected_failure)
        if result is None:
            return None, error
        try:
            return json.loads(result.stdout), None
        except json.JSONDecodeError:
            self.errors.append({"step": f"gh api {endpoint}", "message": "invalid JSON response"})
            return None, "invalid JSON response"

    # ------------------------------------------------------------ 로컬 상태

    def worktree_kind(self):
        git_dir = Path(self.root, self.git_out("rev-parse", "--git-dir")).resolve()
        common = Path(self.root, self.git_out("rev-parse", "--git-common-dir")).resolve()
        return git_dir, "main" if git_dir == common else "linked"

    def operation(self, git_dir):
        for marker, name in OPERATIONS:
            if (git_dir / marker).exists():
                self.blockers.add("operation-in-progress")
                return name
        return None

    def working_tree(self, operation):
        tokens = self.git_required("status", "--porcelain=v1", "-z", "--untracked-files=all").split("\0")
        state = {"operation": operation, "staged": [], "unstaged": [], "untracked": []}
        index = 0
        while index < len(tokens):
            entry = tokens[index]
            index += 1
            if len(entry) < 4:
                continue
            x, y, path = entry[0], entry[1], entry[3:]
            if "R" in (x, y) or "C" in (x, y):
                index += 1  # 원래 경로는 기록하지 않는다.
            if x == "?" and y == "?":
                state["untracked"].append(path)
                continue
            if x not in " ?":
                state["staged"].append(path)
            if y != " ":
                state["unstaged"].append(path)
        return state

    def head(self, requested):
        if requested is not None:
            sha = self.git_out("rev-parse", "--verify", "-q", f"refs/heads/{requested}^{{commit}}")
            if not sha:
                raise LocalFailure(f"unknown branch: {requested}")
            branch = requested
        else:
            branch = self.git_out("symbolic-ref", "-q", "--short", "HEAD") or None
            if branch is None:
                self.blockers.add("detached-head")
            sha = self.git_out("rev-parse", "--verify", "-q", "HEAD^{commit}")
        upstream = None
        if branch is not None:
            upstream = self.git_out("rev-parse", "--abbrev-ref", "--symbolic-full-name", f"{branch}@{{upstream}}")
        return {"branch": branch, "sha": sha, "upstream": upstream or None, "remote_sha": None}

    def remote(self, requested, branch):
        remotes = (self.git_out("remote") or "").split()
        if requested is not None:
            if requested not in remotes:
                raise LocalFailure(f"unknown remote: {requested}")
            name = requested
        else:
            configured = self.git_out("config", f"branch.{branch}.remote") if branch else None
            if configured in remotes:
                name = configured
            elif "origin" in remotes:
                name = "origin"
            else:
                name = remotes[0] if remotes else None
        if name is None:
            return None
        url = self.git_out("config", "--get", f"remote.{name}.url") or None
        return {"name": name, "url": URL_CREDENTIALS.sub(r"\1", url) if url else None}

    def github(self, remote):
        """remote url에서 GitHub 대상을 정한다. SSH 별칭은 ssh -G로 실제 host를 찾는다."""
        url = remote["url"] if remote else None
        for index, pattern in enumerate(REMOTE_URL):
            match = pattern.match(url or "")
            if match:
                break
        else:
            return None, False
        host, owner, name = match.group(1), match.group(2), match.group(3)
        unresolved = False
        if index < 2 and host != "github.com":
            result = run(["ssh", "-G", host])
            resolved = None
            if result.returncode == 0:
                for line in result.stdout.splitlines():
                    key, _, value = line.partition(" ")
                    if key.lower() == "hostname" and value.strip():
                        resolved = value.strip()
                        break
            if resolved:
                host = resolved
            else:
                unresolved = True
        return {"host": host, "owner": owner, "name": name, "url": None, "visibility": None,
                "default_branch": None, "parent": None}, unresolved

    # ------------------------------------------------------------ 범위

    def base(self, requested, branch, remote, default_branch):
        if requested is not None:
            ref, source = requested, "argument"
        elif branch and self.git_out("config", f"branch.{branch}.gh-merge-base"):
            ref, source = self.git_out("config", f"branch.{branch}.gh-merge-base"), "gh-merge-base"
        elif default_branch:
            ref, source = default_branch, "default-branch"
        else:
            ref, source = None, "unresolved"
        resolved = sha = None
        if ref is not None:
            candidates = [ref] if ref.startswith("refs/") else (
                ([f"refs/remotes/{remote['name']}/{ref}"] if remote else []) + [f"refs/heads/{ref}"])
            for candidate in candidates:
                sha = self.git_out("rev-parse", "--verify", "-q", f"{candidate}^{{commit}}")
                if sha:
                    resolved = candidate
                    break
        if sha is None:
            self.blockers.add("base-unresolved")
        elif branch and resolved in (f"refs/heads/{branch}", f"refs/remotes/{remote['name']}/{branch}" if remote
                                     else None):
            self.blockers.add("head-equals-base")  # 같은 branch: 미push commit이 있어도 PR 대상이 아니다.
        return {"ref": ref, "source": source, "resolved": resolved, "sha": sha}

    def range(self, base, head, requested_base):
        state = {"merge_base": None, "commits": [], "files": [], "added": 0, "deleted": 0}
        if not (base["sha"] and head["sha"]):
            return state
        if base["sha"] == head["sha"]:
            self.blockers.add("head-equals-base")
        merge_base = self.git_out("merge-base", base["sha"], head["sha"])
        if not merge_base:
            self.blockers.add("no-merge-base")
            return state
        state["merge_base"] = merge_base
        if requested_base and requested_base.startswith("refs/heads/") and merge_base != base["sha"]:
            self.blockers.add("base-not-ancestor")
        log = self.git_required("log", "--format=%H%x00%s", f"{merge_base}..{head['sha']}")
        for line in log.splitlines():
            sha, _, subject = line.partition("\0")
            state["commits"].append({"sha": sha, "subject": subject})
        if not state["commits"]:
            self.blockers.add("empty-range")
        counts = {}
        tokens = self.git_required("diff", "--numstat", "-z", merge_base, head["sha"]).split("\0")
        index = 0
        while index < len(tokens):
            fields = tokens[index].split("\t")
            index += 1
            if len(fields) != 3:
                continue
            added, deleted, path = fields
            if not path:  # rename·copy: 다음 두 토큰이 원래 경로와 새 경로다.
                path = tokens[index + 1]
                index += 2
            counts[path] = (None if added == "-" else int(added), None if deleted == "-" else int(deleted))
        tokens = self.git_required("diff", "--name-status", "-z", merge_base, head["sha"]).split("\0")
        index = 0
        while index < len(tokens) and tokens[index]:
            status = tokens[index]
            if status[0] in "RC":
                path = tokens[index + 2]
                index += 3
            else:
                path = tokens[index + 1]
                index += 2
            added, deleted = counts.get(path, (None, None))
            state["files"].append({"path": path, "status": status, "added": added, "deleted": deleted})
            state["added"] += added or 0
            state["deleted"] += deleted or 0
        return state

    # ------------------------------------------------------------ 템플릿·기존 PR

    def tree_candidates(self, github, owner_name, ref):
        """원격 tree에서 후보를 찾는다. 실패는 None, 잘린 응답은 'truncated'를 돌려준다."""
        data, _ = self.gh_json(github, f"repos/{owner_name}/git/trees/{ref}?recursive=1")
        if not isinstance(data, dict):
            return None
        if data.get("truncated") is True:
            return "truncated"
        return template_candidates(item.get("path", "") for item in data.get("tree", [])
                                   if isinstance(item, dict) and item.get("type") == "blob")

    def templates(self, github, remote, default_branch):
        if not self.offline and github and default_branch:
            repository = f"{github['owner']}/{github['name']}"
            candidates = self.tree_candidates(github, repository, default_branch)
            if candidates == "truncated":
                return {"status": "unverified", "source": None, "candidates": []}
            if candidates:
                return {"status": "found", "source": {"repository": repository, "ref": default_branch},
                        "candidates": candidates}
            if candidates is not None:
                account = f"{github['owner']}/.github"
                data, error = self.gh_json(github, f"repos/{account}", expected_failure="404")
                if data is None and error and "404" in error:
                    return {"status": "none", "source": None, "candidates": []}
                if isinstance(data, dict) and data.get("private") is True:
                    return {"status": "none", "source": None, "candidates": []}
                if isinstance(data, dict) and data.get("private") is False and data.get("default_branch"):
                    ref = data["default_branch"]
                    candidates = self.tree_candidates(github, account, ref)
                    if candidates == "truncated":
                        return {"status": "unverified", "source": None, "candidates": []}
                    if candidates:
                        return {"status": "account-default", "source": {"repository": account, "ref": ref},
                                "candidates": candidates}
                    if candidates is not None:
                        return {"status": "none", "source": None, "candidates": []}
        if remote and default_branch:
            listing = self.git("ls-tree", "-r", "--name-only", f"{remote['name']}/{default_branch}")
            if listing.returncode == 0:
                return {"status": "local-only", "source": None,
                        "candidates": template_candidates(listing.stdout.splitlines())}
        return {"status": "unverified", "source": None, "candidates": []}

    def existing_prs(self, github, branch):
        """push 대상 저장소의 같은 branch에서 열린 PR을 찾는다. fork는 PR이 parent에 있을 수 있어 확인하지 않는다."""
        if self.offline or not github or not branch or github["parent"]:
            return {"status": "unverified", "items": []}
        result, _ = self.online_step([
            "gh", "pr", "list", "--repo", f"{github['host']}/{github['owner']}/{github['name']}", "--head", branch,
            "--state", "open", "--json", "number,url,isDraft,baseRefName,headRefOid,isCrossRepository",
        ])
        try:
            items = json.loads(result.stdout) if result else None
        except json.JSONDecodeError:
            self.errors.append({"step": "gh pr list", "message": "invalid JSON response"})
            items = None
        if not isinstance(items, list):
            return {"status": "unverified", "items": []}
        # --head는 owner를 구분하지 않아 다른 fork의 같은 이름 branch PR도 돌려준다.
        items = [item for item in items if isinstance(item, dict) and item.get("isCrossRepository") is not True]
        if items:
            self.blockers.add("existing-pr")
        return {"status": "checked", "items": [
            {"number": item.get("number"), "url": item.get("url"), "is_draft": item.get("isDraft"),
             "base": item.get("baseRefName"), "head_sha": item.get("headRefOid")}
            for item in items
        ]}

    # ------------------------------------------------------------ 전체

    def collect(self, args):
        git_dir, worktree = self.worktree_kind()
        if not self.git_out("rev-parse", "--verify", "-q", "HEAD^{commit}"):
            raise LocalFailure("no commits on HEAD")
        operation = self.operation(git_dir)
        working_tree = self.working_tree(operation)
        head = self.head(args.head)
        remote = self.remote(args.remote, head["branch"])
        github, host_unresolved = self.github(remote) if remote else (None, False)

        repo_view_failed = ls_remote_failed = False
        default_branch = auth_login = None
        if not self.offline and github:
            env = dict(os.environ, GH_HOST=github["host"])
            view, _ = self.online_step(["gh", "repo", "view", f"{github['owner']}/{github['name']}", "--json",
                                        "name,owner,url,visibility,defaultBranchRef,isFork,parent"], env=env)
            try:
                data = json.loads(view.stdout) if view else None
            except json.JSONDecodeError:
                data = None
            if isinstance(data, dict):
                github["url"] = data.get("url")
                github["visibility"] = data.get("visibility")
                default_branch = (data.get("defaultBranchRef") or {}).get("name") or None
                if data.get("isFork") is True:
                    parent = data.get("parent") or {}
                    github["parent"] = {"owner": (parent.get("owner") or {}).get("login"), "name": parent.get("name")}
            else:
                repo_view_failed = True
            user, _ = self.gh_json(github, "user")
            if isinstance(user, dict):
                auth_login = user.get("login")
        if not self.offline and remote and head["branch"]:
            listing, _ = self.online_step(["git", "ls-remote", remote["name"], f"refs/heads/{head['branch']}"],
                                          env=self.git_network_env())
            if listing is None:
                ls_remote_failed = True
            elif listing.stdout.strip():
                head["remote_sha"] = listing.stdout.split()[0]
        if default_branch is None and remote:
            symbolic = self.git_out("symbolic-ref", "--short", f"refs/remotes/{remote['name']}/HEAD")
            if symbolic and symbolic.startswith(f"{remote['name']}/"):
                default_branch = symbolic[len(remote["name"]) + 1:]
        if github:
            github["default_branch"] = default_branch

        base = self.base(args.base, head["branch"], remote, default_branch)
        commit_range = self.range(base, head, args.base)
        templates = self.templates(github, remote, default_branch)
        existing = self.existing_prs(github, head["branch"])

        unverified = set()
        if github is None or host_unresolved or repo_view_failed or github["parent"]:
            unverified.add("github-repository")
        if auth_login is None:
            unverified.add("auth")
        if self.offline or remote is None or head["branch"] is None or ls_remote_failed:
            unverified.add("remote-head")
        if default_branch is None:
            unverified.add("default-branch")
        if templates["status"] in {"local-only", "unverified"}:
            unverified.add("templates")
        if existing["status"] == "unverified":
            unverified.add("existing-prs")

        return {
            "schema_version": 1,
            "repository": {"root": self.root, "worktree": worktree, "remote": remote, "github": github,
                           "auth_login": auth_login},
            "head": head,
            "base": base,
            "range": commit_range,
            "working_tree": working_tree,
            "templates": templates,
            "existing_prs": existing,
            "blockers": [name for name in BLOCKERS if name in self.blockers],
            "unverified": [name for name in UNVERIFIED if name in unverified],
            "errors": self.errors,
        }


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--repo", type=Path, default=Path("."))
    parser.add_argument("--head", help="대상 branch. 없으면 현재 branch")
    parser.add_argument("--base", help="base ref. stack 위층은 refs/heads/<아래 branch>")
    parser.add_argument("--remote", help="remote 이름. 없으면 branch 설정, origin, 첫 remote 순서")
    parser.add_argument("--offline", action="store_true", help="네트워크 조회를 하지 않는다")
    args = parser.parse_args()
    try:
        collector = Collector(args.repo, args.offline)
        result = collector.collect(args)
    except LocalFailure as error:
        print(error, file=sys.stderr)
        return 2
    # UTF-8이 아닌 경로는 surrogate로 남아 있으므로 JSON의 \udcXX escape로 바꿔 항상 유효한 UTF-8을 쓴다.
    text = json.dumps(result, ensure_ascii=False, indent=2) + "\n"
    sys.stdout.buffer.write(text.encode("utf-8", "backslashreplace"))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
