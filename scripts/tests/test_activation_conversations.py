"""Exercise conversation, evidence and case boundaries without invoking a model."""

import json
from pathlib import Path
import shutil
import subprocess
import sys
import tempfile
import unittest
from unittest.mock import patch

SCRIPTS = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(SCRIPTS))
import check_activation as ca  # noqa: E402


def lines(*events):
    return "\n".join(json.dumps(event) for event in events)


class ConversationTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name)
        self.skill = self.root / "plugins/demo/skills/case"
        self.skill.mkdir(parents=True)
        self.body = "---\nname: case\n---\n# Complete body\nAll content.\n"
        (self.skill / "SKILL.md").write_text(self.body)
        self.inventory = {"demo:case": self.skill}
        self.spec_path = self.root / "case.json"

    def save(self, query):
        self.spec_path.write_text(json.dumps({"skill": "demo:case", "queries": [query]}))
        return ca.load_spec(self.spec_path).queries[0]

    def test_campaign_catalogs_resolve_only_the_frozen_skill(self):
        entry = {"name": "demo", "source": "./plugins/demo", "version": "1.0.0"}
        catalogs = {
            ".omp-plugin/marketplace.json": {"name": "test-market", "plugins": [entry]},
            ".claude-plugin/marketplace.json": {"name": "test-market", "plugins": [entry]},
            ".agents/plugins/marketplace.json": {
                "name": "test-market",
                "plugins": [{"name": "demo", "source": {"path": "./plugins/demo"}}],
            },
        }
        for name, content in catalogs.items():
            path = self.root / name
            path.parent.mkdir(parents=True)
            path.write_text(json.dumps(content))
        (self.root / "plugins/demo/plugin.json").write_text(
            json.dumps({"name": "demo", "version": "1.0.0"}))
        campaign, snapshot, _ = ca.new_campaign(self.root)
        self.addCleanup(shutil.rmtree, campaign)
        (self.skill / "SKILL.md").write_text("changed after snapshot")
        market, plugins, skills, results = ca.cp.load_marketplace(snapshot)
        self.assertEqual((market, plugins), ("test-market", ["demo"]))
        self.assertEqual([skill.body for skill in skills], ["# Complete body\nAll content."])
        self.assertTrue(all(result.ok for result in results), results)

    def test_corpus_rejects_holdout_leakage_and_unknown_negative_targets(self):
        train = ca.Query("training", [ca.Step("draft", "load")],
                         family="same-conversation", split="train")
        validation = ca.Query("held-out", [ca.Step("revise", "load")],
                              family="same-conversation", split="validation")
        specs = [ca.Spec(self.spec_path, "demo", "case", [train, validation])]
        with self.assertRaisesRegex(ValueError, "crosses train and validation"):
            ca.validate_corpus(specs, {"demo:case"})
        unknown = ca.Spec(self.spec_path, "demo", "absent",
                          [ca.Query("negative", [ca.Step("explain", "no-load")])])
        with self.assertRaisesRegex(ValueError, "unknown target"):
            ca.validate_corpus([unknown], {"demo:case"})

    def test_single_and_multi_turn_normalize_without_injecting_metadata(self):
        single = self.save({"id": "one", "prompt": "hello", "expect": "load"})
        self.assertEqual([s.prompt for s in single.steps], ["hello"])
        multi = self.save({"id": "two", "turns": [{"prompt": "first", "expect": "load"},
                            {"prompt": "next", "expect": "no-load"}],
                           "fixtures": {"policy.txt": "policy"}, "split": "train",
                           "family": "one-family", "origin": "synthetic-boundary"})
        self.assertEqual([s.prompt for s in multi.steps], ["first", "next"])
        self.assertEqual(multi.fixtures, {"policy.txt": "policy"})

    def test_rejects_invalid_nested_cases_before_execution(self):
        base = {"id": "x", "prompt": "p", "expect": "load"}
        variants = [
            {**base, "turns": [{"prompt": "p", "expect": "load"}]},
            {"id": "x", "turns": []},
            {**base, "fixtures": {".Git/config": "bad"}},
            {**base, "fixtures": {"../outside": "bad"}},
            {**base, "fixtures": {"a": "x", "a/b": "y"}},
            {**base, "skills": {"required": ["bad"]}},
            {**base, "skills": {"required": ["demo:case"], "forbidden": ["demo:case"]}},
            {**base, "skills": {"allowed": []}},
            {**base, "skills": {"required": ["demo:case", "demo:case"]}},
            {**base, "purpose": "\ud800"},
        ]
        for raw in variants:
            with self.subTest(raw=raw), self.assertRaises((ValueError, UnicodeError)):
                self.save(raw)

    def test_failed_or_partial_read_is_attempt_not_success(self):
        command = f"cat {self.skill}/SKILL.md"
        started = {"type": "item.started", "item": {"type": "command_execution", "command": command}}
        for output, code, expected in [("permission denied", 1, set()), (self.body[:20], 0, set()),
                                       (self.body, 0, {"demo:case"})]:
            end = {"type": "item.completed", "item": {"type": "command_execution",
                   "command": command, "aggregated_output": output, "exit_code": code,
                   "status": "completed"}}
            trace = ca.parse_codex(lines(started, end), "demo:case", self.inventory)
            self.assertEqual(trace.attempted, {"demo:case"})
            self.assertEqual(trace.successful, expected)

    def test_omp_correlates_result_and_claude_requires_actual_injection(self):
        start = {"type": "tool_execution_start", "toolCallId": "1", "toolName": "read",
                 "args": {"path": "skill://case"}}
        end = {"type": "tool_execution_end", "toolCallId": "1", "isError": False,
               "result": {"content": [{"type": "text", "text": self.body}]}}
        self.assertEqual(ca.parse_omp(lines(start, end), "demo:case", self.inventory).successful,
                         {"demo:case"})
        call = {"type": "assistant", "message": {"content": [{"type": "tool_use", "id": "1",
                "name": "Skill", "input": {"skill": "demo:case"}}]}}
        launch = {"type": "user", "message": {"content": [{"type": "tool_result",
                  "tool_use_id": "1", "content": "Launching skill"}]}}
        injected = {"type": "user", "message": {"content": [{"type": "text",
                    "text": "Base directory\n\n# Complete body\nAll content."}]}}
        self.assertEqual(ca.parse_claude(lines(call, launch), "demo:case", self.inventory).successful, set())
        self.assertEqual(ca.parse_claude(lines(call, launch, injected), "demo:case", self.inventory).successful,
                         {"demo:case"})

    def test_retained_context_and_closed_world_are_per_turn(self):
        step = ca.Step("next", "no-load", skills={"required": ["demo:case"],
                                                  "allowed": ["demo:helper"],
                                                  "forbidden": ["demo:blocked"]})
        self.assertEqual(ca.judge(step, ca.Trace(), "demo:case", {"demo:case"}), [])
        trace = ca.Trace(attempted={"demo:blocked"}, successful={"demo:other"})
        problems = ca.judge(step, trace, "demo:case", {"demo:case", "demo:other"})
        self.assertTrue(any("forbidden" in p for p in problems))
        self.assertTrue(any("unexpected" in p for p in problems))
        self.assertEqual(ca.judge(ca.Step("reuse", "load"), ca.Trace(), "demo:case", {"demo:case"}), [])

    def test_publish_is_distinct_from_scratch_write(self):
        step = ca.Step("draft", "load", forbid=["publish-command"])
        trace = ca.Trace(writes=["Write tool"])
        self.assertEqual(ca.judge_safety(step, trace), [])
        ca.note_command(trace, "demo:case", "git commit -m draft", {})
        self.assertEqual(ca.judge_safety(step, trace), ["publish attempted: git commit -m draft"])

    def test_fixture_paths_are_baseline_but_agent_additions_fail(self):
        query = self.save({"id": "x", "fixtures": {"a.txt": "initial"}, "turns": [
            {"prompt": "first", "expect": "load", "forbid": ["new-files"]},
            {"prompt": "second", "expect": "no-load", "forbid": ["new-files"]}]})
        spec = ca.Spec(self.spec_path, "demo", "case", [query])
        def fake_execute(client, base, root, pin, prompt, target, identity, inventory, session,
                         session_dir, resume=False, timeout=ca.RUN_TIMEOUT, coverage=None):
            trace = ca.Trace(reached=True, session="exact-session", model="m", effort="high")
            if resume:
                (target / "unexpected.txt").write_text("agent output")
            else:
                trace.successful.add(identity)
            return subprocess.CompletedProcess([], 0, "{}\n", ""), trace
        with patch.object(ca, "execute", side_effect=fake_execute):
            results = ca.run_once("omp", self.root, self.root, ca.Pin("m", "high"), spec, query, "unique")
        self.assertEqual([x["status"] for x in results], ["pass", "fail"])
        self.assertEqual(results[1]["problems"], ["new files: unexpected.txt"])
        self.assertEqual(results[1]["available"], ["demo:case"])

    def test_full_repetitions_and_turns_are_required(self):
        passed = {"status": "pass"}
        self.assertEqual(ca.aggregate_status([passed], 3), "unmeasured")
        self.assertEqual(ca.aggregate_status([passed, {"status": "unmeasured"}, passed], 3),
                         "unmeasured")
        self.assertEqual(ca.aggregate_status([passed, {"status": "fail"}], 3), "fail")
        self.assertEqual(ca.aggregate_status([passed, passed, passed], 3), "pass")



    def test_resumed_codex_attests_new_context_not_stale_one(self):
        home = self.root / "codex-home/.codex/sessions"
        home.mkdir(parents=True)
        rollout = home / "rollout-id.jsonl"
        rollout.write_text(lines({"type": "turn_context", "payload": {"model": "old", "effort": "low"}}) + "\n")
        target = self.root / "target"
        target.mkdir()
        def fake_run(cmd, env, cwd, timeout):
            with rollout.open("a") as output:
                output.write(lines({"type": "turn_context", "payload": {"model": "new", "effort": "high"}}) + "\n")
            stdout = lines({"type": "thread.started", "thread_id": "id"},
                           {"type": "item.completed", "item": {"type": "agent_message"}},
                           {"type": "turn.completed"})
            return subprocess.CompletedProcess(cmd, 0, stdout, "")
        with patch.object(ca.cp, "run", side_effect=fake_run):
            _, trace = ca.execute("codex", self.root, self.root, ca.Pin("new", "high"),
                                  "next", target, "demo:case", self.inventory, "id",
                                  self.root / "session-dir", resume=True)
        self.assertFalse(trace.failed)
        self.assertEqual((trace.model, trace.effort), ("new", "high"))


if __name__ == "__main__":
    unittest.main()
