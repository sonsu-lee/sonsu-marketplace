import json
import subprocess
import tempfile
import unittest
from pathlib import Path


RUNNER = Path(__file__).resolve().parents[1] / "hooks/evidence.py"


class EvidenceGateTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory(prefix="workflow evidence ")
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name)
        self.git("init", "-q")
        self.git("config", "commit.gpgsign", "false")
        (self.root / "data.txt").write_text("initial\n", encoding="utf-8")
        (self.root / ".gitignore").write_text("failure-flag\n", encoding="utf-8")
        self.write_declaration(["python3", "-c", "import pathlib,sys; sys.exit(int(pathlib.Path('failure-flag').exists()))"])
        self.git("add", ".")
        self.git("-c", "user.name=Scenario", "-c", "user.email=scenario@example.invalid", "commit", "-qm", "baseline")

    def git(self, *args):
        return subprocess.run(["git", *args], cwd=self.root, text=True, capture_output=True, check=True)

    def write_declaration(self, argv):
        (self.root / ".workflow-checks.json").write_text(json.dumps({"checks": [
            {"id": "check", "argv": argv, "actions": ["commit", "push"]}
        ]}), encoding="utf-8")

    def runner(self, *args, event=None):
        return subprocess.run(["python3", str(RUNNER), *args], cwd=self.root, text=True,
                              input=json.dumps(event) if event is not None else None, capture_output=True)

    def gate(self, command):
        result = self.runner("gate", event={"cwd": str(self.root), "tool_name": "Bash", "tool_input": {"command": command}})
        self.assertEqual(result.returncode, 0, result.stderr)
        return json.loads(result.stdout)

    def test_chained_actions_cannot_skip_declared_push_check(self):
        path = self.root / ".workflow-checks.json"
        declaration = json.loads(path.read_text(encoding="utf-8"))
        declaration["checks"][0]["actions"] = ["push"]
        path.write_text(json.dumps(declaration), encoding="utf-8")
        self.git("add", ".")
        self.git("-c", "user.name=Scenario", "-c", "user.email=scenario@example.invalid",
                 "commit", "--amend", "--no-edit", "-q")
        for command in ("git commit -m change && git push", "git merge HEAD && git push",
                        "git merge HEAD\ngit push", "CI=1 git push", "env git push",
                        "if true; then git push; fi", "{ git push; }", "timeout 60 git push"):
            with self.subTest(command=command):
                self.assertEqual(self.gate(command)["state"], "blocked")

    def test_quoted_commit_message_is_not_an_additional_publication(self):
        path = self.root / ".workflow-checks.json"
        declaration = json.loads(path.read_text(encoding="utf-8"))
        declaration["checks"][0]["actions"].append("publish")
        path.write_text(json.dumps(declaration), encoding="utf-8")
        self.git("add", ".")
        self.assertEqual(self.runner("run", "check").returncode, 0)
        self.assertEqual(self.gate('git commit -m "update helm values"')["state"], "pass")

    def test_expanded_commit_arguments_cannot_claim_a_checked_tree(self):
        self.assertEqual(self.runner("run", "check").returncode, 0)
        for command in ("git commit -m b*", "git commit -m $MSG",
                        "git commit -m {fix,-a}", 'git commit -m "$(true)"'):
            with self.subTest(command=command):
                self.assertEqual(self.gate(command)["state"], "blocked")

    def test_hash_in_shell_word_does_not_hide_chained_push(self):
        self.assertEqual(self.runner("run", "check").returncode, 0)
        self.assertEqual(self.gate("git commit -m wip#1")["state"], "pass")
        self.assertEqual(self.gate("git commit -m wip#1 && git push")["state"], "blocked")
        self.assertEqual(self.gate("echo a#b; git push")["state"], "blocked")
        for command in ("git commit -m $'Don\\'t #42' && git push",
                        "git commit -m $'Don\\'t' && git push && echo It\\'s",
                        "echo $(true)#y; git push",
                        "git commit -m 修正　#12 && git push",
                        'git commit -m "$(printf "%s" "fix #1")" && git push',
                        'git commit -m "${v%% #*}" && git push'):
            with self.subTest(command=command):
                self.assertEqual(self.gate(command)["state"], "blocked")

    def test_shell_comments_do_not_change_command_boundaries(self):
        self.assertEqual(self.runner("run", "check").returncode, 0)
        self.assertEqual(self.gate("git commit -m msg # don't amend")["state"], "pass")
        self.assertEqual(self.gate("git commit -m msg # note\ngit push")["state"], "blocked")

    def test_receipt_matches_staged_tree_and_becomes_stale_after_change(self):
        self.assertEqual(self.gate("git commit -m change")["state"], "blocked")
        (self.root / "data.txt").write_text("changed\n", encoding="utf-8")
        self.assertEqual(self.runner("run", "check").returncode, 0)
        self.git("add", ".")
        self.assertEqual(self.gate("git commit -m change")["state"], "pass")
        (self.root / "data.txt").write_text("changed again\n", encoding="utf-8")
        self.git("add", ".")
        self.assertEqual(self.gate("git commit -m change")["state"], "blocked")

    def test_snapshot_reads_changed_content_even_when_index_marks_it_unchanged(self):
        self.git("update-index", "--assume-unchanged", "data.txt")
        (self.root / "data.txt").write_text("changed\n", encoding="utf-8")
        self.assertEqual(self.runner("run", "check").returncode, 0)
        self.git("update-index", "--no-assume-unchanged", "data.txt")
        self.git("add", "data.txt")
        self.assertEqual(self.gate("git commit -m change")["state"], "pass")

    def test_snapshot_reads_present_skip_worktree_changes(self):
        self.git("update-index", "--skip-worktree", "data.txt")
        (self.root / "data.txt").write_text("changed\n", encoding="utf-8")
        self.assertEqual(self.runner("run", "check").returncode, 0)
        self.assertEqual(self.gate("git commit -m change")["state"], "blocked")
        self.git("update-index", "--no-skip-worktree", "data.txt")
        self.git("add", "data.txt")
        self.assertEqual(self.gate("git commit -m change")["state"], "pass")

    def test_failed_rerun_invalidates_previous_receipt(self):
        self.assertEqual(self.runner("run", "check").returncode, 0)
        self.assertEqual(self.gate("git commit --allow-empty -m change")["state"], "pass")
        (self.root / "failure-flag").write_text("fail\n", encoding="utf-8")
        self.assertNotEqual(self.runner("run", "check").returncode, 0)
        self.assertEqual(self.gate("git commit --allow-empty -m change")["state"], "blocked")

    def test_removed_declaration_cannot_disable_a_committed_gate(self):
        self.assertEqual(self.gate("git commit -a -m change")["state"], "blocked")
        (self.root / ".workflow-checks.json").unlink()
        self.assertEqual(self.gate("git commit -m change")["state"], "blocked")

    def test_unbindable_git_c_command_uses_target_repository_declaration(self):
        with tempfile.TemporaryDirectory() as directory:
            event = {"cwd": directory, "tool_name": "Bash",
                     "tool_input": {"command": f'git -C "{self.root}" commit -a -m change'}}
            result = self.runner("gate", event=event)
            self.assertEqual(result.returncode, 0, result.stderr)
            self.assertEqual(json.loads(result.stdout)["state"], "blocked")

    def test_relative_git_c_is_resolved_once_for_checked_tree(self):
        self.assertEqual(self.runner("run", "check").returncode, 0)
        event = {"cwd": str(self.root.parent), "tool_name": "Bash",
                 "tool_input": {"command": f'git -C "{self.root.name}" commit -m change'}}
        result = self.runner("gate", event=event)
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertEqual(json.loads(result.stdout)["state"], "pass")
        event["tool_input"]["command"] = f'true && git -C "{self.root.name}" commit -m change'
        result = self.runner("gate", event=event)
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertEqual(json.loads(result.stdout)["state"], "blocked")

    def test_explicit_git_directory_uses_target_repository_declaration(self):
        with tempfile.TemporaryDirectory() as directory:
            commands = (
                f'git --git-dir "{self.root}/.git" --work-tree "{self.root}" commit -a -m change',
                f'git --git-dir="{self.root}/.git" --work-tree="{self.root}" commit -a -m change',
                f'cd "{self.root}" && git commit -a -m change',
                f'cd "{self.root}"; git commit -a -m change',
                f'CI=1 git -C "{self.root}" push',
                f'true && git -C "{self.root}" push',
                f'echo x; git -C "{self.root}" push',
                f'git --no-pager -C "{self.root}" push',
                f'cd "{self.root}"\ngit push',
                f'cd "{self.root}" &&\ngit push',
                f'# note\ncd "{self.root}" && git push',
                f'cd "{self.root}"\n\ngit push',
                f'cd "{self.root}"\n# note\ngit push',
            )
            for command in commands:
                event = {"cwd": directory, "tool_name": "Bash", "tool_input": {"command": command}}
                with self.subTest(command=command):
                    result = self.runner("gate", event=event)
                    self.assertEqual(result.returncode, 0, result.stderr)
                    self.assertEqual(json.loads(result.stdout)["state"], "blocked")

    def test_unresolvable_cd_does_not_bypass_a_declared_gate(self):
        (self.root / "loop").symlink_to("loop")
        result = self.gate("cd loop; git commit -m change")
        self.assertEqual(result["state"], "blocked")

    def test_unparseable_command_is_blocked_instead_of_unverified(self):
        result = self.gate('git commit -m "unterminated')
        self.assertEqual(result["state"], "blocked")

    def test_commit_cannot_remove_a_declared_push_requirement(self):
        path = self.root / ".workflow-checks.json"
        data = json.loads(path.read_text(encoding="utf-8"))
        data["checks"][0]["actions"] = ["commit"]
        path.write_text(json.dumps(data), encoding="utf-8")
        self.git("add", ".")
        self.assertEqual(self.runner("run", "check").returncode, 0)
        result = self.gate("git commit -m change")
        self.assertEqual(result["state"], "blocked")
        self.assertIn("removed or changed", result["reason"])

    def test_staged_declaration_removal_cannot_be_hidden_by_worktree(self):
        path = self.root / ".workflow-checks.json"
        data = json.loads(path.read_text(encoding="utf-8"))
        data["checks"][0]["actions"] = ["push"]
        path.write_text(json.dumps(data), encoding="utf-8")
        self.git("add", ".")
        self.git("-c", "user.name=Scenario", "-c", "user.email=scenario@example.invalid",
                 "commit", "--amend", "--no-edit", "-q")
        original = path.read_text(encoding="utf-8")
        path.unlink()
        self.git("add", ".workflow-checks.json")
        path.write_text(original, encoding="utf-8")
        result = self.gate("git commit -m weaken")
        self.assertEqual(result["state"], "blocked")
        self.assertIn("removed or changed", result["reason"])

    def test_remote_issue_and_pr_writes_respect_publish_declarations(self):
        path = self.root / ".workflow-checks.json"
        data = json.loads(path.read_text(encoding="utf-8"))
        data["checks"][0]["actions"] = ["publish"]
        path.write_text(json.dumps(data), encoding="utf-8")
        cases = [
            ("write", {"path": "pr://123"}),
            ("write", {"path": "issue://123"}),
            ("write", {"path": "PR://123"}),
            ("write", {"path": "[pr://123#ab12]"}),
            ("edit", {"paths": ["inside.txt", "pr://123"]}),
            ("edit", {"path": "inside.txt", "edits": [{"rename": "pr://123"}]}),
            ("edit", {"input": '*** Begin Patch\n*** Move to: pr://123\n*** End Patch\n'}),
            ("edit", {"input": '*** Begin Patch\n*** Move to: "pr://123"\n*** End Patch\n'}),
            ("edit", {"input": '[inside.txt#ABCD]\nMV "pr://123"\n'}),
        ]
        for name, data in cases:
            event = {"cwd": str(self.root), "tool_name": name, "tool_input": data}
            with self.subTest(name=name, data=data):
                result = self.runner("gate", event=event)
                self.assertEqual(result.returncode, 0, result.stderr)
                self.assertEqual(json.loads(result.stdout)["state"], "blocked")

    def test_publish_uses_its_cwd_not_an_earlier_git_target(self):
        path = self.root / ".workflow-checks.json"
        data = json.loads(path.read_text(encoding="utf-8"))
        data["checks"][0]["actions"].append("publish")
        path.write_text(json.dumps(data), encoding="utf-8")
        with tempfile.TemporaryDirectory() as other:
            subprocess.run(["git", "init", "-q", other], check=True)
            result = self.gate(f'git -C "{other}" push && gh pr create --fill')
            self.assertEqual(result["state"], "blocked")

    def test_undeclared_repository_does_not_enforce_a_gate(self):
        with tempfile.TemporaryDirectory() as directory:
            subprocess.run(["git", "init", "-q", directory], check=True)
            for command in ("git commit -m change", "git commit -m fix # don't amend"):
                event = {"cwd": directory, "tool_name": "Bash", "tool_input": {"command": command}}
                with self.subTest(command=command):
                    result = self.runner("gate", event=event)
                    self.assertEqual(result.returncode, 0, result.stderr)
                    self.assertEqual(json.loads(result.stdout)["state"], "unverified")

    def test_client_hook_denies_stale_then_requests_approval_for_current_tree(self):
        command = f'git -C "{self.root}" commit -m change'
        event = {"cwd": str(self.root), "tool_name": "Bash", "tool_input": {"command": command}}
        hook = RUNNER.parent / "pre_tool_use.py"
        def decision():
            result = subprocess.run(["python3", str(hook), "--client", "claude"], cwd=self.root,
                                    input=json.dumps(event), text=True, capture_output=True, check=True)
            return json.loads(result.stdout)["hookSpecificOutput"]
        self.assertEqual(decision()["permissionDecision"], "deny")
        self.assertEqual(self.runner("run", "check").returncode, 0)
        confirmed = decision()
        self.assertEqual(confirmed["permissionDecision"], "ask")
        self.assertIn("Verified tree", confirmed["permissionDecisionReason"])
        (self.root / "data.txt").write_text("changed\n", encoding="utf-8")
        self.git("add", ".")
        self.assertEqual(decision()["permissionDecision"], "deny")

    def test_push_with_nondefault_ref_behavior_cannot_use_head_receipt(self):
        self.assertEqual(self.runner("run", "check").returncode, 0)
        self.assertEqual(self.gate("git push")["state"], "pass")
        self.git("config", "push.default", "matching")
        self.assertEqual(self.gate("git push")["state"], "blocked")


if __name__ == "__main__":
    unittest.main()
