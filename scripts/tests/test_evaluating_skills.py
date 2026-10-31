"""Model-free checks for the evaluating-skills scripts and every skill's evals."""

import json
from pathlib import Path
import shutil
import sys
import tempfile
import threading
import unittest

REPO = Path(__file__).resolve().parents[2]
SKILL = REPO / "plugins/skill-workflow/skills/evaluating-skills"
# The skill's scripts/ is a regular package, so it wins over the repository's
# scripts/ directory, which has no __init__.py.
sys.path.insert(0, str(SKILL))
sys.path.insert(0, str(SKILL / "eval-viewer"))

import generate_review  # noqa: E402
from scripts import aggregate_benchmark  # noqa: E402
from scripts.clients import base, codex, omp  # noqa: E402
from scripts.evalsets import EvalSetError, copy_inputs, load_evals, load_queries  # noqa: E402
from scripts.grade import parse_grading  # noqa: E402
from scripts.improve_description import improve_description  # noqa: E402
from scripts.run_evals import run_one  # noqa: E402

SKILL_MD = """---
name: demo
description: >-
  Use this skill for demos,
  across two lines.
license: MIT
---

# Demo
"""


def make_skill(root: Path, name: str = "demo") -> Path:
    skill = root / name
    skill.mkdir(parents=True)
    (skill / "SKILL.md").write_text(SKILL_MD.replace("name: demo", f"name: {name}"))
    return skill


def first_decision(detector, events):
    return next((d for d in map(detector.feed, events) if d is not None), None)


class TempDirTest(unittest.TestCase):
    def setUp(self):
        self.tmp = Path(tempfile.mkdtemp())
        self.addCleanup(shutil.rmtree, self.tmp, True)
        self.addCleanup(base.INTERRUPTED.clear)


class TriggerTests(unittest.TestCase):
    def omp_call(self, tool, **args):
        return {"type": "tool_execution_start", "toolName": tool, "args": args}

    def codex_call(self, command):
        return {"type": "item.started", "item": {"type": "command_execution", "command": command}}

    def test_omp_judges_the_first_call_after_todo(self):
        detector = omp.TriggerDetector("writing-adrs")
        self.assertEqual(first_decision(detector, [self.omp_call("todo"),
                                                   self.omp_call("read", path="skill://writing-adrs")]),
                         base.TRIGGERED)
        self.assertEqual(first_decision(omp.TriggerDetector("writing-adrs"),
                                        [self.omp_call("read", path="README.md")]),
                         base.NOT_TRIGGERED)

    def test_omp_answer_without_tools_is_not_a_trigger(self):
        self.assertEqual(omp.TriggerDetector("x").finish(0, False), base.NOT_TRIGGERED)
        self.assertEqual(omp.TriggerDetector("x").finish(None, True), base.ERROR)

    def test_codex_judges_the_first_tool_item(self):
        hit = self.codex_call("sed -n 1,200p .agents/skills/writing-adrs/SKILL.md")
        self.assertEqual(codex.TriggerDetector("writing-adrs").feed(hit), base.TRIGGERED)
        self.assertEqual(codex.TriggerDetector("writing-adrs").feed(self.codex_call("ls")),
                         base.NOT_TRIGGERED)
        failed = {"type": "turn.failed", "error": {"message": "usage limit"}}
        self.assertEqual(codex.TriggerDetector("writing-adrs").feed(failed), base.ERROR)


class ParseRunTests(TempDirTest):
    def test_omp_events(self):
        def assistant(text, model, tokens, stop="stop"):
            return {"type": "message_end", "message": {
                "role": "assistant", "model": model, "usage": {"totalTokens": tokens},
                "requestControls": {"effort": {"topLevel": "high"}}, "stopReason": stop,
                "content": [{"type": "text", "text": text}]}}
        lines = [json.dumps(e) for e in [
            assistant("first", "m1", 100, "toolUse"),
            {"type": "tool_execution_start", "toolCallId": "a", "toolName": "bash", "args": {}},
            {"type": "tool_execution_end", "toolCallId": "a", "isError": True,
             "result": {"content": [{"type": "text", "text": "boom"}]}},
            assistant("done", "m2", 12),
        ]]
        result = omp.parse_run(lines)
        self.assertEqual((result.total_tokens, result.model, result.effort, result.final_text,
                          result.tool_errors, result.error), (112, "m2", "high", "done", 1, None))

    def test_codex_events(self):
        lines = [json.dumps(e) for e in [
            {"type": "item.completed", "item": {"type": "agent_message", "text": "hi"}},
            {"type": "turn.completed", "usage": {"input_tokens": 10, "output_tokens": 4}},
        ]]
        result = codex.parse_run(lines, self.tmp)
        self.assertEqual((result.total_tokens, result.final_text, result.error), (14, "hi", None))
        failed = [json.dumps({"type": "turn.failed", "error": {"message": "auth expired"}})]
        self.assertEqual(codex.parse_run(failed, self.tmp).error, "auth expired")


class SkillCopyTests(TempDirTest):
    def test_replace_description_keeps_other_lines(self):
        expected = SKILL_MD.replace(
            "description: >-\n  Use this skill for demos,\n  across two lines.\n",
            'description: "New: text"\n')
        self.assertEqual(base.replace_description(SKILL_MD, "New: text"), expected)

    def test_copies_leave_out_evals(self):
        skill = make_skill(self.tmp / "src")
        (skill / "evals").mkdir()
        self.assertEqual([p.name for p in base.copy_skill(skill, self.tmp / "dst").iterdir()],
                         ["SKILL.md"])

    def test_omp_arms_share_the_plugin_and_differ_only_in_the_skill(self):
        plugin = self.tmp / "plugin"
        (plugin / "skills").mkdir(parents=True)
        (plugin / "plugin.json").write_text("{}")
        skill = make_skill(plugin / "skills")
        make_skill(plugin / "skills", "sibling")
        client = omp.OmpClient()
        with_arm = client.prepare_arm("with_skill", skill, self.tmp / "arms", plugin)
        without = client.prepare_arm("without_skill", skill, self.tmp / "arms", plugin)
        self.assertEqual(sorted(p.name for p in (with_arm.plugin_dir / "skills").iterdir()),
                         ["demo", "sibling"])
        self.assertIsNone(without.skill_dir)
        self.assertEqual([p.name for p in (without.plugin_dir / "skills").iterdir()], ["sibling"])


class EvalSetTests(TempDirTest):
    def setUp(self):
        super().setUp()
        self.skill = make_skill(self.tmp)
        (self.skill / "evals/files/case").mkdir(parents=True)
        (self.skill / "evals/files/case/a.txt").write_text("a")

    def write(self, *cases, name="demo"):
        (self.skill / "evals/evals.json").write_text(json.dumps({"skill_name": name,
                                                                 "evals": list(cases)}))

    def case(self, **extra):
        return {"id": 1, "prompt": "p", "expected_output": "e", **extra}

    def test_accepts_a_valid_file(self):
        self.write(self.case(files=["evals/files/case/"], assertions=["a"]))
        self.assertEqual(load_evals(self.skill)["evals"][0]["id"], 1)

    def test_rejects_format_violations(self):
        (self.skill / "notes.txt").write_text("n")
        for cases, name in [((self.case(expectations=["a"]),), "demo"),
                            ((self.case(files=["notes.txt"]),), "demo"),
                            ((self.case(), self.case()), "demo"),
                            ((self.case(),), "other")]:
            with self.subTest(cases=cases, name=name):
                self.write(*cases, name=name)
                with self.assertRaises(EvalSetError):
                    load_evals(self.skill)

    def test_rejects_nested_skill_files(self):
        (self.skill / "evals/files/case/SKILL.md").write_text("x")
        self.write(self.case())
        with self.assertRaises(EvalSetError):
            load_evals(self.skill)

    def test_rejects_duplicate_queries(self):
        path = self.tmp / "queries.json"
        path.write_text(json.dumps([{"query": "q", "should_trigger": True}] * 2))
        with self.assertRaises(EvalSetError):
            load_queries(path)

    def test_copy_inputs_places_files_and_directory_contents(self):
        (self.skill / "evals/files/b.txt").write_text("b")
        work = self.tmp / "work"
        work.mkdir()
        self.assertEqual(copy_inputs(self.skill, ["evals/files/b.txt", "evals/files/case/"], work),
                         ["a.txt", "b.txt"])


class ResultTests(TempDirTest):
    def grade_run(self, config, number, passed, seconds=1):
        run = self.tmp / "eval-1" / config / f"run-{number}"
        run.mkdir(parents=True)
        (run / "timing.json").write_text(json.dumps({"total_duration_seconds": seconds}))
        (run / "grading.json").write_text(json.dumps({
            "expectations": [], "summary": {"passed": passed, "failed": 3 - passed, "total": 3,
                                            "pass_rate": passed / 3}}))

    def test_delta_is_with_skill_minus_old_skill(self):
        self.grade_run("old_skill", 1, 1, 10)
        self.grade_run("with_skill", 1, 3, 30)
        delta = aggregate_benchmark.generate_benchmark(self.tmp)["run_summary"]["delta"]
        self.assertEqual((delta["pass_rate"], delta["time_seconds"]), ("+0.67", "+20.0"))

    def test_benchmark_lists_ungraded_runs(self):
        (self.tmp / "iteration.json").write_text(json.dumps({"runs": 2}))
        for number in (1, 2):
            self.grade_run("without_skill", number, 1)
        self.grade_run("with_skill", 1, 3)
        (self.tmp / "eval-1/with_skill/run-2").mkdir()
        markdown = aggregate_benchmark.generate_markdown(
            aggregate_benchmark.generate_benchmark(self.tmp))
        self.assertIn("eval-1 with_skill: 1 of 2 graded", markdown)
        self.assertNotIn("without_skill: ", markdown)

    def test_grading_is_found_in_prose_and_its_summary_recomputed(self):
        text = ('Result: {"expectations": [{"text": "x", "passed": true, "evidence": "seen"},'
                ' {"text": "y", "passed": false, "evidence": "missing"}],'
                ' "summary": {"passed": 2}} done')
        grading = parse_grading(text, ["A", "B"])
        self.assertEqual([e["text"] for e in grading["expectations"]], ["A", "B"])
        self.assertEqual(grading["summary"], {"passed": 1, "failed": 1, "total": 2,
                                              "pass_rate": 0.5})
        with self.assertRaises(ValueError):
            parse_grading(text, ["A"])

    def test_viewer_shows_nested_outputs_and_marks_unmeasured_runs(self):
        run = self.tmp / "eval-1" / "with_skill" / "run-1"
        (run / "outputs/docs").mkdir(parents=True)
        (run / "outputs/docs/adr.md").write_text("adr")
        (run / "outputs/metrics.json").write_text("{}")
        (run / "timing.json").write_text(json.dumps({"error": "timed out after 900s"}))
        (self.tmp / "eval-1/eval_metadata.json").write_text(json.dumps({"eval_id": 1,
                                                                        "prompt": "p"}))
        built = generate_review.build_run(self.tmp, run)
        self.assertEqual([o["name"] for o in built["outputs"]], ["docs/adr.md"])
        self.assertTrue(built["prompt"].startswith("[UNMEASURED RUN: timed out after 900s]"))

    def test_improver_leaves_out_unmeasured_queries(self):
        prompts = []
        rows = [{"query": "never measured", "should_trigger": False, "pass": False,
                 "triggers": 0, "runs": 0, "unmeasured": True},
                {"query": "real false trigger", "should_trigger": False, "pass": False,
                 "triggers": 3, "runs": 3}]
        results = {"results": rows, "summary": {"passed": 0, "total": 2}}
        history = [{"description": "old", "results": rows}]
        improve_description("demo", "body", "old", results, history,
                            lambda p: prompts.append(p) or "<new_description>x</new_description>")
        failures = prompts[0].split("PREVIOUS ATTEMPTS")[0]
        self.assertIn("real false trigger", failures)
        self.assertNotIn("never measured", failures)
        self.assertIn('[UNMEASURED] "never measured"', prompts[0])


class InterruptTests(TempDirTest):
    def test_stop_all_ends_a_running_client(self):
        errors = []

        def run():
            try:
                base.stream(["sleep", "30"], {"PATH": "/bin:/usr/bin"}, self.tmp, 60)
            except RuntimeError as error:
                errors.append(str(error))

        worker = threading.Thread(target=run)
        worker.start()
        while not base._ACTIVE:
            threading.Event().wait(0.05)
        base.stop_all()
        worker.join(timeout=5)
        self.assertEqual(errors, ["interrupted"])

    def test_queued_run_after_interrupt_keeps_its_earlier_result(self):
        run_dir = self.tmp / "run-1"
        run_dir.mkdir()
        (run_dir / "timing.json").write_text(json.dumps({"error": None}))
        base.INTERRUPTED.set()
        self.assertFalse(run_one(omp.OmpClient(), None, self.tmp, {"id": 1}, base.Arm("x", None, None),
                                 run_dir, 1))
        self.assertTrue((run_dir / "timing.json").is_file())


class HomeCheckTests(unittest.TestCase):
    settings = base.Settings("m", "high", Path("/homes/test"), 10)

    class Client:
        def __init__(self, listed):
            self.listed = listed

        def list_skills(self, cwd, settings):
            return [(name, None) for name in self.listed]

    def test_rejects_the_skill_in_any_namespace(self):
        for listed in ("writing-adrs", "decision-workflow/writing-adrs",
                       "decision-workflow:writing-adrs"):
            self.assertIn("already has a skill named writing-adrs",
                          base.check_home(self.Client([listed]), self.settings, "writing-adrs"))
        self.assertIsNone(base.check_home(self.Client(["writing-adrs-extra"]), self.settings,
                                          "writing-adrs"))


class RepositoryEvalTests(unittest.TestCase):
    def test_every_skill_has_valid_eval_files(self):
        skills = sorted(p.parent for p in REPO.glob("plugins/*/skills/*/SKILL.md"))
        self.assertTrue(skills)
        for skill in skills:
            with self.subTest(skill=skill.name):
                data = load_evals(skill)
                self.assertTrue(all(case.get("assertions") for case in data["evals"]))
                load_queries(skill / "evals/eval_queries.json")


if __name__ == "__main__":
    unittest.main()
