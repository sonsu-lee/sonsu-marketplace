"""pr_context.py가 PR 게시 판단에 필요한 상태를 정확히 수집하는지 확인한다."""
import importlib.util
import json
import os
from pathlib import Path
import subprocess
import sys
import tempfile
import textwrap
import unittest


SCRIPT = Path(__file__).resolve().parents[1] / "scripts/pr_context.py"
GITHUB_URL = "git@github.com:o/r.git"
IDENTITY = {
    "GIT_AUTHOR_NAME": "Test", "GIT_AUTHOR_EMAIL": "test@example.com",
    "GIT_COMMITTER_NAME": "Test", "GIT_COMMITTER_EMAIL": "test@example.com",
}
REPO_VIEW = {"name": "r", "owner": {"login": "o"}, "url": "https://github.com/o/r", "visibility": "PUBLIC",
             "defaultBranchRef": {"name": "main"}, "isFork": False, "parent": None}
FAKE_COMMAND = textwrap.dedent("""\
    #!{python}
    import json, os, sys
    line = " ".join(sys.argv[1:])
    with open(os.environ["{log}"], "a", encoding="utf-8") as log:
        log.write(line + "\\n")
    for item in json.loads(os.environ.get("{responses}", "[]")):
        if line.startswith(item["prefix"]):
            sys.stdout.write(item.get("stdout", ""))
            sys.stderr.write(item.get("stderr", ""))
            sys.exit(item.get("code", 0))
    sys.stderr.write("unexpected\\n")
    sys.exit(1)
""")


def response(prefix, stdout="", stderr="", code=0):
    return {"prefix": prefix, "stdout": stdout if isinstance(stdout, str) else json.dumps(stdout),
            "stderr": stderr, "code": code}


def default_responses():
    return [
        response("repo view o/r", REPO_VIEW),
        response("api user", {"login": "me"}),
        response("api repos/o/r/git/trees/main", {"tree": [
            {"path": ".github/PULL_REQUEST_TEMPLATE.md", "type": "blob"},
            {"path": "docs/guide.md", "type": "blob"},
        ], "truncated": False}),
        response("pr list", []),
    ]


class PrContextTest(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.tmp = Path(self.temp.name)
        self.bin = self.tmp / "bin"
        self.bin.mkdir()
        self.gh_log = self.tmp / "gh.log"
        self.ssh_log = self.tmp / "ssh.log"
        self.write_fake("gh", "FAKE_GH_LOG", "FAKE_GH_RESPONSES")
        self.write_fake("ssh", "FAKE_SSH_LOG", "FAKE_SSH_RESPONSES")
        self.env = dict(os.environ, **IDENTITY, PATH=f"{self.bin}{os.pathsep}{os.environ['PATH']}",
                        GIT_CONFIG_GLOBAL=os.devnull, GIT_CONFIG_NOSYSTEM="1",
                        FAKE_GH_LOG=str(self.gh_log), FAKE_SSH_LOG=str(self.ssh_log))
        self.origin = self.tmp / "origin.git"
        self.git(self.tmp, "init", "-q", "--bare", "--initial-branch=main", str(self.origin))
        work = self.tmp / "work"
        self.git(self.tmp, "init", "-q", "--initial-branch=main", str(work))
        self.commit(work, "README.md", "readme\n", "Initial commit")
        self.git(work, "push", "-q", str(self.origin), "main")
        self.clone = self.make_clone("clone", rewrite=True)

    def tearDown(self):
        self.temp.cleanup()

    def write_fake(self, name, log, responses):
        path = self.bin / name
        path.write_text(FAKE_COMMAND.format(python=sys.executable, log=log, responses=responses), encoding="utf-8")
        path.chmod(0o755)

    def git(self, cwd, *args, check=True):
        return subprocess.run(["git", *args], cwd=cwd, env=self.env, capture_output=True, text=True, check=check)

    def commit(self, repo, name, text, message):
        (repo / name).write_text(text, encoding="utf-8")
        self.git(repo, "add", name)
        self.git(repo, "commit", "-q", "-m", message)

    def make_clone(self, name, rewrite):
        clone = self.tmp / name
        self.git(self.tmp, "clone", "-q", str(self.origin), str(clone))
        if rewrite:
            self.point_origin(clone, GITHUB_URL)
        self.git(clone, "checkout", "-q", "-b", "feature")
        self.commit(clone, "a.txt", "a\n", "Add a")
        self.commit(clone, "b.txt", "b\n", "Add b")
        return clone

    def point_origin(self, clone, url):
        self.git(clone, "remote", "set-url", "origin", url)
        self.git(clone, "config", f"url.{self.origin}.insteadOf", url)

    def run_tool(self, *args, repo=None, responses=None, ssh=None):
        env = dict(self.env, FAKE_GH_RESPONSES=json.dumps(default_responses() if responses is None else responses),
                   FAKE_SSH_RESPONSES=json.dumps(ssh or []))
        result = subprocess.run([sys.executable, str(SCRIPT), "--repo", str(repo or self.clone), *args],
                                env=env, capture_output=True, text=True, check=False)
        data = json.loads(result.stdout) if result.returncode == 0 else None
        return result, data

    def assert_ok(self, *args, **kwargs):
        result, data = self.run_tool(*args, **kwargs)
        self.assertEqual(result.returncode, 0, result.stderr)
        return data

    def test_online_feature_branch(self):
        data = self.assert_ok()
        self.assertEqual(data["base"]["source"], "default-branch")
        self.assertEqual(len(data["range"]["commits"]), 2)
        self.assertEqual(data["templates"]["candidates"], [".github/PULL_REQUEST_TEMPLATE.md"])
        self.assertEqual(data["templates"]["status"], "found")
        self.assertIsNone(data["head"]["remote_sha"])
        self.assertEqual(data["blockers"], [])
        self.assertEqual(data["unverified"], [])

    def test_pushed_branch_reports_remote_sha(self):
        self.git(self.clone, "push", "-q", "origin", "feature")
        data = self.assert_ok()
        self.assertEqual(data["head"]["remote_sha"], data["head"]["sha"])

    def test_existing_pr_blocks(self):
        responses = [response("pr list", [{"number": 7, "url": "https://github.com/o/r/pull/7", "isDraft": True,
                                           "baseRefName": "main", "headRefOid": "abc",
                                           "isCrossRepository": False}])] + default_responses()
        self.assertIn("existing-pr", self.assert_ok(responses=responses)["blockers"])

    def test_cross_repository_pr_with_same_branch_name_does_not_block(self):
        responses = [response("pr list", [{"number": 8, "url": "https://github.com/o/r/pull/8", "isDraft": False,
                                           "baseRefName": "main", "headRefOid": "def",
                                           "isCrossRepository": True}])] + default_responses()
        data = self.assert_ok(responses=responses)
        self.assertNotIn("existing-pr", data["blockers"])
        self.assertEqual(data["existing_prs"], {"status": "checked", "items": []})
        self.assertIn("isCrossRepository", self.gh_log.read_text(encoding="utf-8"))

    def test_fork_leaves_target_and_existing_prs_unverified(self):
        fork = dict(REPO_VIEW, isFork=True, parent={"id": "x", "name": "r", "owner": {"id": "y", "login": "up"}})
        data = self.assert_ok(responses=[response("repo view o/r", fork)] + default_responses())
        self.assertEqual(data["repository"]["github"]["parent"], {"owner": "up", "name": "r"})
        self.assertEqual(data["existing_prs"], {"status": "unverified", "items": []})
        self.assertEqual(data["unverified"], ["github-repository", "existing-prs"])
        self.assertNotIn("pr list", self.gh_log.read_text(encoding="utf-8"))

    def test_offline_makes_no_gh_calls(self):
        data = self.assert_ok("--offline")
        self.assertFalse(self.gh_log.exists())
        self.assertEqual(data["unverified"], ["auth", "remote-head", "templates", "existing-prs"])
        self.assertEqual(data["base"]["source"], "default-branch")
        self.assertEqual(data["templates"]["status"], "local-only")

    def test_detached_head(self):
        self.git(self.clone, "checkout", "-q", "--detach")
        data = self.assert_ok()
        self.assertIsNone(data["head"]["branch"])
        self.assertIn("detached-head", data["blockers"])

    def test_running_on_base_branch(self):
        self.git(self.clone, "checkout", "-q", "main")
        blockers = self.assert_ok()["blockers"]
        self.assertIn("head-equals-base", blockers)
        self.assertIn("empty-range", blockers)

    def test_unpushed_commit_on_base_branch(self):
        self.git(self.clone, "checkout", "-q", "main")
        self.commit(self.clone, "c.txt", "c\n", "Add c")
        data = self.assert_ok()
        self.assertEqual(len(data["range"]["commits"]), 1)
        self.assertIn("head-equals-base", data["blockers"])

    def test_non_utf8_path_is_escaped(self):
        name = os.fsdecode(b"caf\xe9.txt")
        blob = self.git(self.clone, "hash-object", "-w", "a.txt").stdout.strip()
        self.git(self.clone, "update-index", "--add", "--cacheinfo", f"100644,{blob},{name}")
        self.git(self.clone, "commit", "-q", "-m", "Add non-UTF-8 path")
        result = subprocess.run([sys.executable, str(SCRIPT), "--repo", str(self.clone), "--offline"],
                                env=self.env, capture_output=True, check=False)
        self.assertEqual(result.returncode, 0, result.stderr)
        data = json.loads(result.stdout.decode("utf-8"))
        self.assertIn(name, [item["path"] for item in data["range"]["files"]])

    def test_base_precedence(self):
        self.git(self.clone, "config", "branch.feature.gh-merge-base", "main")
        self.assertEqual(self.assert_ok()["base"]["source"], "gh-merge-base")
        self.assertEqual(self.assert_ok("--base", "main")["base"]["source"], "argument")

    def stack(self, diverge):
        self.git(self.clone, "checkout", "-q", "-b", "lower", "main")
        self.commit(self.clone, "lower.txt", "old\n", "Lower")
        self.git(self.clone, "push", "-q", "origin", "lower")
        self.commit(self.clone, "lower.txt", "new\n", "Lower")
        self.git(self.clone, "commit", "-q", "--amend", "-m", "Lower")
        self.git(self.clone, "checkout", "-q", "-b", "upper")
        self.commit(self.clone, "upper.txt", "upper\n", "Upper")
        if diverge:
            self.git(self.clone, "checkout", "-q", "lower")
            self.git(self.clone, "commit", "-q", "--amend", "-m", "Lower rewritten")
            self.git(self.clone, "checkout", "-q", "upper")
        return self.assert_ok("--base", "refs/heads/lower")

    def test_linear_stack_layer(self):
        data = self.stack(diverge=False)
        self.assertEqual(len(data["range"]["commits"]), 1)
        self.assertEqual(data["blockers"], [])

    def test_diverged_stack_layer(self):
        self.assertIn("base-not-ancestor", self.stack(diverge=True)["blockers"])

    def test_merge_in_progress(self):
        self.git(self.clone, "checkout", "-q", "main")
        self.commit(self.clone, "README.md", "main side\n", "Main change")
        self.git(self.clone, "checkout", "-q", "feature")
        self.commit(self.clone, "README.md", "feature side\n", "Feature change")
        self.assertNotEqual(self.git(self.clone, "merge", "main", check=False).returncode, 0)
        data = self.assert_ok()
        self.assertEqual(data["working_tree"]["operation"], "merge")
        self.assertIn("operation-in-progress", data["blockers"])

    def test_working_tree_classification(self):
        (self.clone / "a.txt").write_text("staged\n", encoding="utf-8")
        self.git(self.clone, "add", "a.txt")
        (self.clone / "b.txt").write_text("unstaged\n", encoding="utf-8")
        (self.clone / "new.txt").write_text("new\n", encoding="utf-8")
        tree = self.assert_ok()["working_tree"]
        self.assertEqual((tree["staged"], tree["unstaged"], tree["untracked"]), (["a.txt"], ["b.txt"], ["new.txt"]))

    def account_responses(self, account):
        return [
            response("api repos/o/r/git/trees/main", {"tree": [{"path": "README.md", "type": "blob"}],
                                                      "truncated": False}),
            response("api repos/o/.github/git/trees/main", {"tree": [
                {"path": "PULL_REQUEST_TEMPLATE.md", "type": "blob"}], "truncated": False}),
            response("api repos/o/.github ", account),
        ] + default_responses()

    def test_public_account_default_template(self):
        templates = self.assert_ok(responses=self.account_responses({"private": False,
                                                                     "default_branch": "main"}))["templates"]
        self.assertEqual(templates["status"], "account-default")
        self.assertEqual(templates["source"]["repository"], "o/.github")

    def test_private_account_repository_has_no_default(self):
        templates = self.assert_ok(responses=self.account_responses({"private": True}))["templates"]
        self.assertEqual(templates["status"], "none")

    def test_missing_account_repository_has_no_default(self):
        responses = [
            response("api repos/o/r/git/trees/main", {"tree": [{"path": "README.md", "type": "blob"}],
                                                      "truncated": False}),
            response("api repos/o/.github ", stderr="gh: Not Found (HTTP 404)\n", code=1),
        ] + default_responses()
        data = self.assert_ok(responses=responses)
        self.assertEqual(data["templates"]["status"], "none")
        self.assertEqual(data["errors"], [])
        self.assertNotIn("templates", data["unverified"])

    def test_truncated_tree_is_unverified(self):
        responses = [response("api repos/o/r/git/trees/main", {"tree": [], "truncated": True})] + default_responses()
        data = self.assert_ok(responses=responses)
        self.assertEqual(data["templates"]["status"], "unverified")
        self.assertIn("templates", data["unverified"])

    def test_failed_pr_lookup_is_unverified(self):
        responses = [response("pr list", stderr="boom\n", code=1)] + default_responses()
        data = self.assert_ok(responses=responses)
        self.assertIn("existing-prs", data["unverified"])
        self.assertIn({"step": "gh pr list", "message": "boom"}, data["errors"])

    def test_ssh_alias_resolves_host(self):
        self.point_origin(self.clone, "git@gh-alias:o/r.git")
        data = self.assert_ok(ssh=[response("-G gh-alias", "hostname github.com\nuser git\n")])
        self.assertEqual(data["repository"]["github"]["host"], "github.com")
        self.assertEqual(data["repository"]["github"]["owner"], "o")

    def test_https_credentials_are_removed(self):
        self.point_origin(self.clone, "https://x-access-token:ghp_SECRET123@github.com/o/r.git")
        result, data = self.run_tool()
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertEqual(data["repository"]["remote"]["url"], "https://github.com/o/r.git")
        self.assertEqual(data["repository"]["github"]["host"], "github.com")
        self.assertNotIn("SECRET", result.stdout)
        self.assertNotIn("SECRET", self.gh_log.read_text(encoding="utf-8"))

    def test_not_a_repository(self):
        plain = self.tmp / "plain"
        plain.mkdir()
        result, _ = self.run_tool(repo=plain)
        self.assertEqual(result.returncode, 2)
        self.assertTrue(result.stderr.startswith("not a git repository:"), result.stderr)

    def test_without_remote(self):
        self.git(self.clone, "remote", "remove", "origin")
        data = self.assert_ok()
        self.assertFalse(self.gh_log.exists())
        self.assertIsNone(data["repository"]["github"])
        self.assertEqual(data["base"]["source"], "unresolved")
        self.assertIn("base-unresolved", data["blockers"])
        self.assertEqual(data["unverified"],
                         ["github-repository", "auth", "remote-head", "default-branch", "templates", "existing-prs"])

    def test_local_path_remote(self):
        data = self.assert_ok(repo=self.make_clone("local", rewrite=False))
        self.assertFalse(self.gh_log.exists())
        self.assertIsNone(data["repository"]["github"])
        self.assertIsNone(data["head"]["remote_sha"])
        self.assertEqual(data["templates"]["status"], "local-only")
        self.assertEqual(data["unverified"], ["github-repository", "auth", "templates", "existing-prs"])


class HelperTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        spec = importlib.util.spec_from_file_location("pr_context", SCRIPT)
        cls.module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(cls.module)

    def test_single_templates_precede_directory_templates(self):
        paths = [".github/PULL_REQUEST_TEMPLATE/bug.md", "docs/pull_request_template.md",
                 ".github/pull_request_template/feature.md", "pull_request_template.md",
                 ".github/pull_request_template.md"]
        self.assertEqual(self.module.template_candidates(paths), [
            ".github/pull_request_template.md", "pull_request_template.md", "docs/pull_request_template.md",
            ".github/PULL_REQUEST_TEMPLATE/bug.md", ".github/pull_request_template/feature.md",
        ])

    def test_timeout_is_failure_result(self):
        result = self.module.run([sys.executable, "-c", "import time; time.sleep(5)"], timeout=0.2)
        self.assertEqual(result.returncode, 124)
        self.assertIn("timed out", result.stderr)


if __name__ == "__main__":
    unittest.main()
