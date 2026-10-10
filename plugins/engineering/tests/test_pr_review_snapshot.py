"""pr_review_snapshot.py가 PR 고정 SHA와 게시 전후 차이를 읽기 전용으로 판정하는지 확인한다."""
import json
import os
from pathlib import Path
import subprocess
import sys
import tempfile
import textwrap
import unittest


SCRIPT = Path(__file__).resolve().parents[1] / "scripts/pr_review_snapshot.py"
URL = "https://github.com/acme/catalog/pull/87"
IDENTITY = {
    "GIT_AUTHOR_NAME": "Test", "GIT_AUTHOR_EMAIL": "test@example.com",
    "GIT_COMMITTER_NAME": "Test", "GIT_COMMITTER_EMAIL": "test@example.com",
}
FAKE_GH = textwrap.dedent("""\
    #!{python}
    import json, os, sys
    line = " ".join(sys.argv[1:])
    with open(os.environ["FAKE_GH_LOG"], "a", encoding="utf-8") as log:
        log.write(line + "\\n")
    path = os.environ["FAKE_GH_STATE"]
    with open(path, encoding="utf-8") as stream:
        state = json.load(stream)
    for item in state:
        if line.startswith(item["prefix"]):
            queue = item["responses"]
            current = queue.pop(0) if len(queue) > 1 else queue[0]
            with open(path, "w", encoding="utf-8") as stream:
                json.dump(state, stream)
            sys.stdout.write(current.get("stdout", ""))
            sys.stderr.write(current.get("stderr", ""))
            sys.exit(current.get("code", 0))
    sys.stderr.write("unexpected gh call: " + line + "\\n")
    sys.exit(1)
""")


def ok(value):
    return {"stdout": json.dumps(value)}


class PrReviewSnapshotTest(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.tmp = Path(self.temp.name)
        bin_dir = self.tmp / "bin"
        bin_dir.mkdir()
        gh = bin_dir / "gh"
        gh.write_text(FAKE_GH.format(python=sys.executable), encoding="utf-8")
        gh.chmod(0o755)
        self.log = self.tmp / "gh.log"
        self.state = self.tmp / "gh.json"
        self.env = dict(os.environ, **IDENTITY, PATH=f"{bin_dir}{os.pathsep}{os.environ['PATH']}",
                        GIT_CONFIG_GLOBAL=os.devnull, GIT_CONFIG_NOSYSTEM="1",
                        FAKE_GH_LOG=str(self.log), FAKE_GH_STATE=str(self.state))
        self.repo = self.tmp / "repo"
        self.git(self.tmp, "init", "-q", "--initial-branch=main", str(self.repo))
        self.root_sha = self.commit("README.md", "root\n")
        self.git(self.repo, "checkout", "-q", "-b", "feature")
        self.head_sha = self.commit("feature.txt", "one\n")
        self.git(self.repo, "checkout", "-q", "main")
        self.base_sha = self.commit("main.txt", "main\n")
        self.git(self.repo, "checkout", "-q", "feature")
        self.moved_head = self.commit("feature.txt", "two\n")
        self.git(self.repo, "reset", "-q", "--hard", self.head_sha)

    def tearDown(self):
        self.temp.cleanup()

    def git(self, cwd, *args):
        return subprocess.run(["git", *args], cwd=cwd, env=self.env, capture_output=True, text=True,
                              check=True).stdout.strip()

    def commit(self, name, text):
        (self.repo / name).write_text(text, encoding="utf-8")
        self.git(self.repo, "add", name)
        self.git(self.repo, "commit", "-q", "-m", name)
        return self.git(self.repo, "rev-parse", "HEAD")

    def pr(self, head=None, state="open", merged=False, base_repo="acme/catalog", number=87):
        return {
            "number": number, "state": state, "merged": merged, "html_url": URL,
            "base": {"sha": self.base_sha, "ref": "main", "repo": {"full_name": base_repo}},
            "head": {"sha": head or self.head_sha, "ref": "feature", "repo": {"full_name": "fork/catalog"}},
        }

    def gh(self, pulls, reviews=((11, 4),), comments=((21,),), extra=()):
        def pages(groups):
            return [ok([[{"id": item} for item in group] for group in groups])]

        state = [{"prefix": "api repos/acme/catalog/pulls/87/reviews", "responses": pages(reviews)},
                 {"prefix": "api repos/acme/catalog/pulls/87/comments", "responses": pages(comments)},
                 {"prefix": "api repos/acme/catalog/pulls/87 ", "responses": [ok(item) for item in pulls]},
                 *extra]
        self.state.write_text(json.dumps(state), encoding="utf-8")

    def run_tool(self, *args, repo=None):
        result = subprocess.run([sys.executable, "-B", str(SCRIPT), *args, "--repo", str(repo or self.repo)],
                                env=self.env, capture_output=True, text=True, check=False)
        return result, json.loads(result.stdout) if result.stdout else None

    def calls(self):
        return self.log.read_text(encoding="utf-8").splitlines() if self.log.exists() else []

    def capture(self, path):
        self.gh([self.pr()])
        result, data = self.run_tool("capture", URL, "--output", str(path))
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
        return data

    def test_capture_fixes_exact_merge_base_ids_and_writes_only_requested_file(self):
        refs_before = self.git(self.repo, "for-each-ref")
        out = self.tmp / "before.json"
        data = self.capture(out)
        snapshot = data["snapshot"]
        self.assertEqual(data["status"], "ok")
        self.assertEqual(snapshot["fixed_shas"], {
            "base": self.base_sha, "head": self.head_sha, "merge_base": self.root_sha})
        self.assertEqual(snapshot["head"]["repository"], "fork/catalog")
        self.assertEqual(snapshot["existing_review_ids"], [4, 11])
        self.assertEqual(snapshot["existing_inline_comment_ids"], [21])
        self.assertTrue(snapshot["collection_stable"])
        self.assertEqual(json.loads(out.read_text(encoding="utf-8")), data)
        self.assertEqual(self.git(self.repo, "for-each-ref"), refs_before)
        self.assertEqual(self.git(self.repo, "status", "--porcelain"), "")
        for call in self.calls():
            self.assertIn("--method GET", call)
        self.assertTrue(any("--paginate --slurp" in call for call in self.calls()))

    def test_capture_reports_change_during_collection(self):
        self.gh([self.pr(), self.pr(head=self.moved_head)])
        result, data = self.run_tool("capture", URL)
        self.assertEqual(result.returncode, 1)
        self.assertEqual(data["status"], "changed")
        self.assertFalse(data["snapshot"]["collection_stable"])
        self.assertEqual(data["snapshot"]["observed_after"]["head"]["sha"], self.moved_head)

    def test_compare_keeps_ok_for_new_ids_and_flags_moved_head(self):
        before = self.tmp / "before.json"
        self.capture(before)

        self.gh([self.pr()], reviews=((4, 11, 30),), comments=((21, 31),))
        result, data = self.run_tool("compare", "--against", str(before))
        self.assertEqual(result.returncode, 0, result.stdout)
        self.assertTrue(data["comparison"]["unchanged"])
        self.assertEqual(data["comparison"]["new_review_ids"], [30])
        self.assertEqual(data["comparison"]["new_inline_comment_ids"], [31])

        self.gh([self.pr(head=self.moved_head)])
        result, data = self.run_tool("compare", "--against", str(before))
        self.assertEqual(result.returncode, 1)
        self.assertEqual(data["comparison"]["changed_fields"], ["head"])
        self.assertEqual(data["comparison"]["before"]["fixed_shas"]["head"], self.head_sha)
        self.assertEqual(data["comparison"]["after"]["fixed_shas"]["head"], self.moved_head)

        self.gh([self.pr(head="a" * 40)])
        result, data = self.run_tool("compare", "--against", str(before))
        self.assertEqual(result.returncode, 1, result.stdout)
        self.assertEqual(data["comparison"]["changed_fields"], ["head"])
        self.assertIsNone(data["snapshot"]["merge_base"])

    def test_compare_flags_closed_pr_and_rejects_unstable_snapshot(self):
        before = self.tmp / "before.json"
        self.capture(before)
        self.gh([self.pr(state="closed", merged=True)])
        result, data = self.run_tool("compare", "--against", str(before))
        self.assertEqual(result.returncode, 1)
        self.assertEqual(data["comparison"]["changed_fields"], ["state"])
        self.assertEqual(data["comparison"]["after"]["state"], "merged")

        saved = json.loads(before.read_text(encoding="utf-8"))
        saved["snapshot"]["fixed_shas"]["head"] = self.moved_head
        tampered = self.tmp / "tampered.json"
        tampered.write_text(json.dumps(saved), encoding="utf-8")
        result, data = self.run_tool("compare", "--against", str(tampered))
        self.assertEqual(result.returncode, 2)
        self.assertIn("inconsistent", data["error"])

    def test_missing_local_commit_and_shallow_history_block(self):
        self.gh([self.pr(head="f" * 40)])
        result, data = self.run_tool("capture", URL)
        self.assertEqual(result.returncode, 2)
        self.assertEqual(data["status"], "blocked")

        shallow = self.tmp / "shallow"
        self.git(self.tmp, "clone", "-q", "--depth", "1", "--branch", "main",
                 f"file://{self.repo}", str(shallow))
        self.gh([self.pr()])
        result, data = self.run_tool("capture", URL, repo=shallow)
        self.assertEqual(result.returncode, 2)
        self.assertIn("shallow", data["error"])

    def test_rejects_target_mismatch_and_existing_output_without_overwrite(self):
        result, data = self.run_tool("capture", URL, "--repository", "github.com/acme/other")
        self.assertEqual(result.returncode, 2)
        self.assertIn("disagree", data["error"])
        self.assertEqual(self.calls(), [])

        self.gh([self.pr(base_repo="acme/other")])
        result, data = self.run_tool("capture", URL)
        self.assertEqual(result.returncode, 2)
        self.assertIn("does not match", data["error"])

        existing = self.tmp / "existing.json"
        existing.write_text("keep\n", encoding="utf-8")
        result, _ = self.run_tool("capture", URL, "--output", str(existing))
        self.assertEqual(result.returncode, 2)
        self.assertEqual(existing.read_text(encoding="utf-8"), "keep\n")

    def test_current_branch_requires_exactly_one_open_pr(self):
        view = {"prefix": "repo view", "responses": [ok({"url": "https://github.com/acme/catalog"})]}
        many = {"prefix": "pr list --repo github.com/acme/catalog --state open --head feature",
                "responses": [ok([{"number": 87}, {"number": 88}])]}
        self.gh([self.pr()], extra=(view, many))
        result, data = self.run_tool("capture")
        self.assertEqual(result.returncode, 2)
        self.assertIn("exactly one", data["error"])

        one = dict(many, responses=[ok([{"number": 87}])])
        self.gh([self.pr()], extra=(view, one))
        result, data = self.run_tool("capture")
        self.assertEqual(result.returncode, 0, result.stdout)
        self.assertEqual(data["snapshot"]["number"], 87)


if __name__ == "__main__":
    unittest.main()
