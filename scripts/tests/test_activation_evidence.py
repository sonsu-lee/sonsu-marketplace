"""Guard campaign authentication and conversation-scoped loading evidence."""

import json
from pathlib import Path
import random
import subprocess
import sys
import tempfile
import unittest
from unittest.mock import patch

SCRIPTS = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(SCRIPTS))
import check_activation as ca  # noqa: E402
import compare_skill as comparison  # noqa: E402


def stream(*events):
    return "\n".join(json.dumps(event) for event in events)


def command_event(command, output, code=0, ident="read"):
    return {"type": "item.completed", "item": {
        "id": ident, "type": "command_execution", "command": command,
        "aggregated_output": output, "exit_code": code,
        "status": "completed" if code == 0 else "failed",
    }}


class EvidenceTests(unittest.TestCase):
    def setUp(self):
        temporary = tempfile.TemporaryDirectory()
        self.addCleanup(temporary.cleanup)
        self.root = Path(temporary.name)
        self.skill = self.root / "plugins/demo/skills/case"
        (self.skill / "references").mkdir(parents=True)
        self.main = "---\nname: case\n---\n# Main\nRead all instructions.\nKeep the boundary.\n"
        self.reference = "# Reference\nFirst rule.\nSecond rule.\nThird rule.\n"
        (self.skill / "SKILL.md").write_text(self.main)
        (self.skill / "references/rules.md").write_text(self.reference)
        self.inventory = {"demo:case": self.skill}

    def test_relative_main_and_reference_reads_are_both_observed(self):
        command = f"cd {self.skill} && cat SKILL.md references/rules.md"
        trace = ca.parse_codex(stream(command_event(command, self.main + self.reference)),
                               "demo:case", self.inventory)
        self.assertEqual(trace.successful, {"demo:case"})
        self.assertEqual(ca.judge(ca.Step("load", "load", reads=["references/rules.md"]),
                                  trace, "demo:case", trace.successful), [])
        self.assertTrue(ca.judge(ca.Step("exclude", "no-load"), trace,
                                 "demo:case", trace.successful))

    def test_complete_content_survives_an_unrelated_shell_failure(self):
        command = f"cat {self.skill}/SKILL.md; rg --files missing-directory"
        trace = ca.parse_codex(stream(command_event(command, self.main, 1)),
                               "demo:case", self.inventory)
        self.assertEqual(trace.successful, {"demo:case"})

    def test_partial_successes_accumulate_but_failed_partial_content_does_not(self):
        command = f"cat {self.skill}/SKILL.md"
        first, second = self.main.split("# Main", 1)
        second = "# Main" + second
        partial = [command_event(command, first, ident="first"),
                   command_event(command, second, 1, ident="failed")]
        trace = ca.parse_codex(stream(*partial), "demo:case", self.inventory)
        self.assertEqual(trace.successful, set())
        complete = ca.parse_codex(stream(*partial, command_event(command, second, ident="last")),
                                  "demo:case", self.inventory)
        self.assertEqual(complete.successful, {"demo:case"})

    def test_reference_coverage_and_available_context_survive_a_followup(self):
        command = f"cat {self.skill}/references/rules.md"
        first, second = self.reference.split("Second rule.", 1)
        second = "Second rule." + second
        coverage = {}
        partial = ca.parse_codex(stream(command_event(command, first)),
                                 "demo:case", self.inventory, coverage)
        self.assertEqual(partial.reads, set())
        completed = ca.parse_codex(stream(command_event(command, second)),
                                   "demo:case", self.inventory, coverage)
        self.assertEqual(ca.judge(ca.Step("reuse", "load", reads=["references/rules.md"]),
                                  ca.Trace(), "demo:case", {"demo:case"}, completed.reads), [])
        failed_reread = ca.parse_codex(stream(command_event(command, "permission denied", 1)),
                                       "demo:case", self.inventory, coverage)
        self.assertEqual(failed_reread.reads, set())

    def test_reference_sections_require_the_whole_requested_section(self):
        content = "# Guide\nIntro.\n## Merge\nKeep attribution.\nValidate the message.\n## Publish\nAsk first.\n"
        (self.skill / "references/rules.md").write_text(content)
        command = f"rg -n -A 3 '^## Merge' {self.skill}/references/rules.md"
        complete = "3:## Merge\n4-Keep attribution.\n5-Validate the message.\n6-## Publish\n"
        step = ca.Step("merge advice", "load", reads=["references/rules.md#merge"])
        partial = ca.parse_codex(stream(command_event(command, "3:## Merge\n4-Keep attribution.\n")),
                                 "demo:case", self.inventory)
        self.assertEqual(ca.judge(step, partial, "demo:case", {"demo:case"}),
                         ["not read: references/rules.md#merge"])
        trace = ca.parse_codex(stream(command_event(command, complete)), "demo:case", self.inventory)
        self.assertEqual(ca.judge(step, trace, "demo:case", {"demo:case"}), [])
        self.assertEqual(ca.judge(ca.Step("full guide", "load", reads=["references/rules.md"]),
                                  trace, "demo:case", {"demo:case"}),
                         ["not read: references/rules.md"])

    def test_nested_line_numbers_preserve_numeric_source_content(self):
        content = "# Reference\n## Codes\n123: preserve this literal prefix.\nKeep attribution.\n"
        (self.skill / "references/rules.md").write_text(content)
        numbered = "\n".join(f"{index}-{index}:{line}" for index, line in enumerate(content.splitlines(), 1))
        command = f"grep -n '' {self.skill}/references/rules.md | grep -n -A5 Codes"
        trace = ca.parse_codex(stream(command_event(command, numbered)), "demo:case", self.inventory)
        step = ca.Step("code guidance", "load", reads=["references/rules.md#codes"])
        self.assertEqual(ca.judge(step, trace, "demo:case", {"demo:case"}), [])

    def test_fenced_headings_do_not_cut_off_required_guidance(self):
        content = "## Example\n```markdown\n## Example\nquoted text\n```\nRequired rule.\n## Next\nOther.\n"
        (self.skill / "references/rules.md").write_text(content)
        command = f"cat {self.skill}/references/rules.md"
        trace = ca.parse_codex(stream(command_event(command, content.split('Required rule.')[0])),
                               "demo:case", self.inventory)
        step = ca.Step("example", "load", reads=["references/rules.md#example"])
        self.assertTrue(ca.judge(step, trace, "demo:case", {"demo:case"}))
        complete = ca.parse_codex(stream(command_event(command, content)), "demo:case", self.inventory)
        self.assertEqual(ca.judge(step, complete, "demo:case", {"demo:case"}), [])

    def test_relative_read_from_the_skills_directory_is_available(self):
        command = f"cd {self.skill.parent} && cat case/SKILL.md"
        trace = ca.parse_codex(stream(command_event(command, self.main)), "demo:case", self.inventory)
        self.assertEqual(ca.judge(ca.Step("apply guidance", "load"), trace,
                                  "demo:case", trace.successful), [])

    def test_metadata_inspection_is_not_workflow_selection(self):
        for command, output in (
                (f"head -3 {self.skill}/SKILL.md", "---\nname: case\n---\n"),
                (f'grep -n -E "rule|instruction" {self.skill}/SKILL.md', "5:Read all instructions.\n"),
                (f"grep -n rule {self.skill}/SKILL.md", "5:Read all instructions.\n")):
            with self.subTest(command=command):
                trace = ca.parse_codex(stream(command_event(command, output)), "demo:case", self.inventory)
                self.assertEqual(trace.inspected, {"demo:case"})
                self.assertEqual(ca.judge(ca.Step("inspect metadata", "no-load"),
                                          trace, "demo:case", trace.successful), [])
        complete = ca.parse_codex(stream(command_event(f"grep '.*' {self.skill}/SKILL.md", self.main)),
                                  "demo:case", self.inventory)
        self.assertTrue(ca.judge(ca.Step("no guidance", "no-load"), complete,
                                 "demo:case", complete.successful))

    def test_qualified_catalog_search_is_not_workflow_selection(self):
        for step in (ca.Step("search the catalog", "no-load"),
                     ca.Step("search the catalog", "load", skills={"forbidden": ["demo:case"]})):
            with self.subTest(expect=step.expect):
                trace = ca.parse_codex(stream(command_event(
                    "rg 'demo:case' catalog.json", '{"name": "demo:case"}\n')),
                    "other:skill", self.inventory)
                self.assertEqual(trace.attempted, set())
                problems = ca.judge(step, trace, "demo:case", trace.successful)
                self.assertNotIn("skill selection attempted", problems)
                self.assertFalse(any("forbidden" in p for p in problems))
        # 同じ修飾名でも本文を読めば起動として残る。
        read = ca.parse_codex(stream(command_event(
            f"rg -n demo:case catalog.json && cat {self.skill}/SKILL.md", self.main)),
            "demo:case", self.inventory)
        self.assertIn("demo:case", read.attempted)

    def test_metadata_inspection_does_not_erase_a_denied_main_load(self):
        trace = ca.parse_codex(stream(
            command_event(f"cat {self.skill}/SKILL.md", "permission denied", 1),
            command_event(f"head -3 {self.skill}/SKILL.md", "---\nname: case\n---\n")),
            "demo:case", self.inventory)
        self.assertEqual(ca.judge(ca.Step("no guidance", "no-load"), trace,
                                  "demo:case", trace.successful), ["skill selection attempted"])

    def test_same_command_inspection_preserves_a_denied_relative_main_load(self):
        command = f"cd {self.skill} && cat SKILL.md; head -1 {self.skill}/SKILL.md"
        trace = ca.parse_codex(stream(command_event(command, "Permission denied", 1)),
                               "demo:case", self.inventory)
        step = ca.Step("no workflow", "no-load", skills={"forbidden": ["demo:case"]})
        self.assertEqual(ca.judge(step, trace, "demo:case", set()),
                         ["skill selection attempted", "forbidden skills attempted: demo:case"])
        metadata = f"cat package.json; head -3 {self.skill}/SKILL.md"
        control = ca.parse_codex(stream(command_event(metadata, "---\nname: case\n---\n")),
                                 "demo:case", self.inventory)
        self.assertEqual(ca.judge(step, control, "demo:case", set()), [])

    def test_omp_parent_session_is_not_confused_with_child_sidecars(self):
        target = self.root / "target"
        target.mkdir()
        sessions = self.root / "session-files"
        def run(*args, **kwargs):
            (sessions / "root.jsonl").write_text("{}\n")
            (sessions / "root").mkdir()
            (sessions / "root/child.jsonl").write_text("{}\n")
            output = stream({"type": "message_end", "message": {
                "role": "assistant", "model": "model", "stopReason": "stop",
                "requestControls": {"effort": {"topLevel": "high"}},
                "content": [{"type": "text", "text": "Done."}],
            }})
            return subprocess.CompletedProcess([], 0, output, "")
        with patch.object(ca.cp, "run", side_effect=run):
            _, trace = ca.execute("omp", self.root, self.root, ca.Pin("provider/model", "high"),
                                  "inspect", target, "demo:case", self.inventory, "new", sessions)
        self.assertEqual(trace.session, str(sessions / "root.jsonl"))
        self.assertFalse(trace.failed)

    def test_child_content_never_becomes_parent_availability(self):
        child = "agent-call"
        events = [
            {"type": "system", "subtype": "init", "model": "parent", "session_id": "root"},
            {"type": "system", "subtype": "init", "model": "child", "session_id": "child",
             "parent_tool_use_id": child},
            {"type": "assistant", "parent_tool_use_id": child, "message": {"content": [
                {"type": "tool_use", "id": "read", "name": "Bash",
                 "input": {"command": f"cat {self.skill}/SKILL.md {self.skill}/references/rules.md"}}]}},
            {"type": "user", "parent_tool_use_id": child, "message": {"content": [
                {"type": "tool_result", "tool_use_id": "read", "content": self.main + self.reference}]}},
            {"type": "assistant", "parent_tool_use_id": None,
             "message": {"content": [{"type": "text", "text": "The helper returned a summary."}]}},
            {"type": "result", "subtype": "success", "parent_tool_use_id": None},
        ]
        trace = ca.parse_claude(stream(*events), "demo:case", self.inventory)
        self.assertEqual((trace.model, trace.session), ("parent", "root"))
        self.assertEqual(trace.child_attempted, {"demo:case"})
        self.assertEqual(trace.successful, set())
        self.assertEqual(trace.reads, set())
        self.assertTrue(ca.judge(ca.Step("require parent", "load"), trace, "demo:case", set()))
        root_read = [
            {"type": "assistant", "message": {"content": [
                {"type": "tool_use", "id": "read", "name": "Read",
                 "input": {"file_path": str(self.skill / "SKILL.md")}}]}},
            {"type": "user", "message": {"content": [
                {"type": "tool_result", "tool_use_id": "read", "content": self.main}]}},
        ]
        observed = ca.parse_claude(stream(*events, *root_read), "demo:case", self.inventory)
        self.assertEqual(observed.successful, {"demo:case"})

    def test_observed_prohibitions_fail_incomplete_pinned_turns_only(self):
        query = ca.Query("negative", [ca.Step("do not select", "no-load")])
        spec = ca.Spec(self.root / "spec.json", "demo", "case", [query])
        for mismatch, expected in (("", "fail"), ("another model", "unmeasured")):
            with self.subTest(mismatch=mismatch):
                trace = ca.Trace(reached=True, failed=True, attempted={"demo:case"},
                                 mismatch=mismatch, error="provider failure", session="id")
                with patch.object(ca, "execute", return_value=(
                        subprocess.CompletedProcess([], 1, "", ""), trace)):
                    result = ca.run_once("codex", self.root, self.root, ca.Pin("model", "high"),
                                         spec, query, "off-profile" if mismatch else "pinned")
                self.assertEqual(result[0]["status"], expected)

    def test_nonadjacent_fixture_ancestor_is_rejected(self):
        path = self.root / "spec.json"
        path.write_text(json.dumps({"skill": "demo:case", "queries": [{
            "id": "overlap", "prompt": "inspect", "expect": "no-load",
            "fixtures": {"a": "file", "a-b": "other", "a/c": "child"},
        }]}))
        with self.assertRaisesRegex(ValueError, "fixture paths overlap"):
            ca.load_spec(path)

    def test_later_comparison_load_cannot_repair_an_unguided_first_answer(self):
        query = ca.Query("conversation", [ca.Step("first", "load"), ca.Step("second", "load")],
                         criteria=["Uses the assigned guidance"])
        calls = iter([set(), {"demo:case"}])
        def execute(*args, **kwargs):
            trace = ca.Trace(reached=True, complete=True, session="id", successful=next(calls))
            output = stream({"type": "message_end", "message": {
                "role": "assistant", "stopReason": "stop",
                "content": [{"type": "text", "text": "Answer without initial guidance."}],
            }})
            return subprocess.CompletedProcess([], 0, output, ""), trace
        with patch.object(ca, "execute", side_effect=execute):
            answer = comparison.answer(self.root, self.root, ca.Pin("m", "high"), self.skill,
                                       "demo", "case", query, "base", "comparison")
        verdict = comparison.compare(self.root, self.root, ca.Pin("m", "high"), query,
                                     {"base": answer, "head": answer}, random.Random(0), "judge")
        self.assertEqual(verdict.winner, "")
        self.assertTrue(answer.trace.failed)


class AuthenticationTests(unittest.TestCase):
    def setUp(self):
        temporary = tempfile.TemporaryDirectory()
        self.addCleanup(temporary.cleanup)
        self.root = Path(temporary.name)
        self.source = self.root / "dedicated"
        self.home, target = ca.homes_for(self.source, "codex")
        (self.home / ".codex").mkdir(parents=True)
        target.mkdir()
        self.auth = self.home / ".codex/auth.json"
        self.auth.write_bytes(b'{"refresh_token":"test-only-initial"}')

    def test_refresh_is_preserved_before_the_next_campaign_can_copy_it(self):
        first, second = self.root / "first", self.root / "second"
        refreshed = b'{"refresh_token":"test-only-refreshed"}'
        # 1. 使用中の認証を他のキャンペーンへ複製させない。
        with ca.AuthLease("codex", self.source, first) as lease:
            (first / "codex-home/.codex/auth.json").write_bytes(refreshed)
            with ca.AuthLease("codex", self.source, second) as blocked:
                self.assertEqual(blocked.sync_status, "not-started")
                self.assertFalse((second / "codex-home/.codex/auth.json").exists())
        # 2. 更新を保存してからロックを解放し、次の呼び出しへ引き継ぐ。
        self.assertEqual(lease.sync_status, "saved")
        self.assertEqual(self.auth.read_bytes(), refreshed)
        self.assertEqual(self.auth.stat().st_mode & 0o777, 0o600)
        with ca.AuthLease("codex", self.source, second):
            self.assertEqual((second / "codex-home/.codex/auth.json").read_bytes(), refreshed)

    def test_manual_relogin_is_not_overwritten_by_an_older_campaign(self):
        destination = self.root / "campaign"
        new_login = b'{"refresh_token":"test-only-new-login"}'
        with ca.AuthLease("codex", self.source, destination) as lease:
            (destination / "codex-home/.codex/auth.json").write_bytes(
                b'{"refresh_token":"test-only-older-refresh"}')
            self.auth.write_bytes(new_login)
        self.assertEqual(lease.sync_status, "preserved-newer-login")
        self.assertEqual(self.auth.read_bytes(), new_login)

    def test_exception_still_saves_refresh_and_releases_the_lease(self):
        refreshed = b'{"refresh_token":"test-only-exception-refresh"}'
        with self.assertRaises(RuntimeError):
            with ca.AuthLease("codex", self.source, self.root / "failed"):
                (self.root / "failed/codex-home/.codex/auth.json").write_bytes(refreshed)
                raise RuntimeError("worker failed")
        self.assertEqual(self.auth.read_bytes(), refreshed)
        with ca.AuthLease("codex", self.source, self.root / "next") as lease:
            self.assertEqual(lease.sync_status, "active")


if __name__ == "__main__":
    unittest.main()
