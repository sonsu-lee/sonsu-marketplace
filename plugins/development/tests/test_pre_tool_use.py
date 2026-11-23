import json
import os
import subprocess
import tempfile
import unittest
from pathlib import Path


HOOK = Path(__file__).resolve().parents[1] / "hooks/pre_tool_use.py"


class PreToolUseTests(unittest.TestCase):
    def setUp(self):
        self.workspace = tempfile.TemporaryDirectory()
        self.addCleanup(self.workspace.cleanup)

    def invoke(self, name, data, claude):
        env = dict(os.environ)
        env["CLAUDE_PLUGIN_ROOT"] = str(HOOK.parent.parent)
        event = {"cwd": self.workspace.name, "tool_name": name, "tool_input": data}
        if not claude:
            event["turn_id"] = "codex-turn"
        process = subprocess.run(
            ["python3", str(HOOK), "--client", "claude" if claude else "codex"],
            input=json.dumps(event),
            text=True, capture_output=True, check=True, env=env,
        )
        return json.loads(process.stdout)["hookSpecificOutput"]["permissionDecision"] if process.stdout else None

    def test_git_global_options_require_confirmation_or_block(self):
        command = {"command": "git -c user.name=Example commit -m example"}
        self.assertEqual(self.invoke("Bash", command, True), "ask")
        self.assertEqual(self.invoke("Bash", command, False), "deny")
        self.assertIsNone(self.invoke("Bash", {"command": "python3 -m unittest"}, True))

    def test_publication_commands_require_confirmation_or_block(self):
        for command in ("git --no-pager push", "gh pr ready 1",
                        "gh api repos/example/issues -f title=example",
                        "gh api --method=POST repos/example/issues"):
            with self.subTest(command=command):
                self.assertEqual(self.invoke("Bash", {"command": command}, True), "ask")
                self.assertEqual(self.invoke("Bash", {"command": command}, False), "deny")

    def test_external_mcp_and_patch_moves_require_confirmation(self):
        self.assertEqual(self.invoke("mcp__github_create_issue", {}, True), "ask")
        self.assertIsNone(self.invoke("mcp__github_get_issue", {}, True))
        patch = "*** Begin Patch\n*** Update File: inside.txt\n*** Move to: ../outside.txt\n*** End Patch"
        self.assertEqual(self.invoke("apply_patch", {"command": patch}, False), "deny")
        self.assertIsNone(self.invoke("Write", {"file_path": "inside.txt"}, True))


class SessionStartTests(unittest.TestCase):
    def test_bootstrap_only_applies_to_main_start_clear_and_compact(self):
        hook = HOOK.parent / "session_start.py"
        for source in ("startup", "clear", "compact", "resume", "fork"):
            with self.subTest(source=source):
                result = subprocess.run(
                    ["python3", str(hook)], input=json.dumps({"source": source, "agent_type": "custom-main"}),
                    text=True, capture_output=True, check=True,
                )
                self.assertEqual(bool(result.stdout), source in {"startup", "clear", "compact"})
                if result.stdout:
                    self.assertIn("# Working on tasks", json.loads(result.stdout)["hookSpecificOutput"]["additionalContext"])
        child = subprocess.run(
            ["python3", str(hook)], input=json.dumps({"source": "startup", "agent_id": "child"}),
            text=True, capture_output=True, check=True,
        )
        self.assertEqual(child.stdout, "")


if __name__ == "__main__":
    unittest.main()
