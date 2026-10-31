"""Model-free checks for the evaluating-skills runner and every skill's evals."""

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

from scripts import aggregate_benchmark  # noqa: E402
from scripts.clients import codex, omp  # noqa: E402
from scripts.clients.base import (  # noqa: E402
    ERROR, NOT_TRIGGERED, TRIGGERED, Settings, check_home, copy_skill,
    name_matches, replace_description,
)
from scripts.evalsets import EvalSetError, copy_inputs, load_evals, load_queries  # noqa: E402
from scripts.grade import parse_grading  # noqa: E402
from scripts.run_evals import (  # noqa: E402
    collect_outputs, file_digests, prepare_iteration, run_one, tree_digest,
)
from scripts.run_loop import merge_results, select_best  # noqa: E402
from scripts.improve_description import improve_description  # noqa: E402
from scripts.clients import base  # noqa: E402

sys.path.insert(0, str(SKILL / "eval-viewer"))
import generate_review  # noqa: E402

SKILL_MD = """---
name: demo
description: >-
  Use this skill for demos,
  across two lines.
license: MIT
---

# Demo

Body text.
"""


def make_skill(root: Path, name: str = "demo") -> Path:
    skill = root / name
    skill.mkdir(parents=True)
    (skill / "SKILL.md").write_text(SKILL_MD.replace("name: demo", f"name: {name}"))
    return skill


def write_evals(skill: Path, evals, name: str = "demo") -> None:
    (skill / "evals").mkdir(exist_ok=True)
    (skill / "evals/evals.json").write_text(json.dumps({"skill_name": name, "evals": evals}))


def omp_start(tool, **args):
    return {"type": "tool_execution_start", "toolName": tool, "args": args}


def codex_command(item_id, command, kind="item.started"):
    return {"type": kind, "item": {"id": item_id, "type": "command_execution", "command": command}}


def feed_all(detector, events):
    for event in events:
        decision = detector.feed(event)
        if decision is not None:
            return decision
    return None


class TempDirTest(unittest.TestCase):
    def setUp(self):
        self.tmp = Path(tempfile.mkdtemp())
        self.addCleanup(shutil.rmtree, self.tmp, True)


class OmpTriggerTests(TempDirTest):
    def detector(self):
        skill_md = self.tmp / ".omp/skills/writing-adrs/SKILL.md"
        skill_md.parent.mkdir(parents=True)
        skill_md.write_text("x")
        return omp.TriggerDetector("writing-adrs", skill_md, self.tmp, 3)

    def test_skill_uri_read_after_todo_triggers(self):
        events = [omp_start("todo", op="init"), omp_start("read", path="skill://writing-adrs")]
        self.assertEqual(feed_all(self.detector(), events), TRIGGERED)

    def test_skill_uri_with_line_selector_triggers(self):
        events = [omp_start("read", path="skill://writing-adrs:1-80")]
        self.assertEqual(feed_all(self.detector(), events), TRIGGERED)

    def test_reference_read_neither_triggers_nor_counts(self):
        events = [omp_start("read", path="skill://writing-adrs/references/x.md"),
                  omp_start("read", path="a.md"), omp_start("read", path="b.md"),
                  omp_start("read", path=".omp/skills/writing-adrs/SKILL.md")]
        self.assertEqual(feed_all(self.detector(), events), TRIGGERED)

    def test_three_other_reads_do_not_trigger_and_todo_is_not_counted(self):
        detector = self.detector()
        events = [omp_start("read", path="a.md"), omp_start("todo", op="init"),
                  omp_start("read", path="b.md")]
        self.assertIsNone(feed_all(detector, events))
        self.assertEqual(detector.feed(omp_start("read", path="c.md")), NOT_TRIGGERED)

    def test_assistant_error_is_an_error(self):
        event = {"type": "message_end",
                 "message": {"role": "assistant", "stopReason": "error", "errorMessage": "quota"}}
        detector = self.detector()
        self.assertEqual(detector.feed(event), ERROR)
        self.assertEqual(detector.error, "quota")

    def test_timeout_without_tool_calls_is_an_error(self):
        self.assertEqual(self.detector().finish(None, True), ERROR)


class CodexTriggerTests(unittest.TestCase):
    def detector(self):
        return codex.TriggerDetector("writing-adrs", 3)

    def test_reading_skill_file_triggers(self):
        event = codex_command("1", "sed -n '1,200p' .agents/skills/writing-adrs/SKILL.md")
        self.assertEqual(self.detector().feed(event), TRIGGERED)

    def test_listing_then_reading_triggers(self):
        events = [codex_command("1", "ls .agents/skills/writing-adrs"),
                  codex_command("2", "cat .agents/skills/writing-adrs/SKILL.md")]
        self.assertEqual(feed_all(self.detector(), events), TRIGGERED)

    def test_three_other_commands_do_not_trigger(self):
        events = [codex_command(str(i), "ls") for i in range(3)]
        self.assertEqual(feed_all(self.detector(), events), NOT_TRIGGERED)

    def test_completed_turn_before_reading_does_not_trigger(self):
        events = [codex_command("1", "ls"), {"type": "turn.completed", "usage": {}}]
        self.assertEqual(feed_all(self.detector(), events), NOT_TRIGGERED)

    def test_failed_turn_is_an_error(self):
        event = {"type": "turn.failed", "error": {"message": "auth"}}
        self.assertEqual(self.detector().feed(event), ERROR)


class ParseRunTests(TempDirTest):
    def test_omp_events(self):
        assistant = {"role": "assistant", "model": "m1", "usage": {"totalTokens": 100},
                     "requestControls": {"effort": {"topLevel": "low"}},
                     "content": [{"type": "text", "text": "first"}], "stopReason": "toolUse"}
        last = {"role": "assistant", "model": "m2", "usage": {"input": 5, "output": 7},
                "requestControls": {"effort": {"topLevel": "high"}},
                "content": [{"type": "text", "text": "done"}], "stopReason": "stop"}
        lines = [json.dumps(e) for e in [
            {"type": "message_end", "message": assistant},
            {"type": "tool_execution_start", "toolCallId": "a", "toolName": "bash",
             "args": {"command": "false"}},
            {"type": "tool_execution_end", "toolCallId": "a", "isError": True,
             "result": {"content": [{"type": "text", "text": "boom"}]}},
            {"type": "message_end", "message": last},
        ]]
        result = omp.parse_run(lines)
        self.assertEqual((result.total_tokens, result.model, result.effort), (112, "m2", "high"))
        self.assertEqual((result.final_text, result.tool_errors, result.error), ("done", 1, None))
        self.assertIn("### Tool result: bash (error)", result.transcript)

    def test_omp_assistant_error(self):
        message = {"role": "assistant", "stopReason": "error", "errorMessage": "overloaded",
                   "content": []}
        result = omp.parse_run([json.dumps({"type": "message_end", "message": message})])
        self.assertEqual(result.error, "overloaded")

    def test_codex_events(self):
        lines = [json.dumps(e) for e in [
            {"type": "thread.started", "thread_id": "t1"},
            {"type": "item.completed", "item": {"id": "1", "type": "agent_message", "text": "hi"}},
            {"type": "turn.completed", "usage": {"input_tokens": 10, "output_tokens": 4}},
            {"type": "turn.completed", "usage": {"input_tokens": 1, "output_tokens": 1}},
        ]]
        result = codex.parse_run(lines, self.tmp)
        self.assertEqual((result.total_tokens, result.final_text, result.error), (16, "hi", None))

    def test_codex_failed_turn(self):
        lines = [json.dumps({"type": "turn.failed", "error": {"message": "auth expired"}})]
        self.assertEqual(codex.parse_run(lines, self.tmp).error, "auth expired")


class SkillCopyTests(TempDirTest):
    def test_replace_description_keeps_other_bytes(self):
        replaced = replace_description(SKILL_MD, "New: text")
        expected = SKILL_MD.replace(
            "description: >-\n  Use this skill for demos,\n  across two lines.\n",
            'description: "New: text"\n')
        self.assertEqual(replaced, expected)

    def test_copy_skill_excludes_evals_and_workspaces(self):
        skill = make_skill(self.tmp / "src")
        (skill / "evals").mkdir()
        (skill / "evals/evals.json").write_text("{}")
        (skill / "demo-workspace").mkdir()
        (skill / "references").mkdir()
        (skill / "references/a.md").write_text("a")
        copy = copy_skill(skill, self.tmp / "dst")
        self.assertEqual(sorted(p.name for p in copy.iterdir()), ["SKILL.md", "references"])


class EvalSetTests(TempDirTest):
    def setUp(self):
        super().setUp()
        self.skill = make_skill(self.tmp)
        (self.skill / "evals/files/case").mkdir(parents=True)
        (self.skill / "evals/files/case/a.txt").write_text("a")

    def case(self, **extra):
        return {"id": 1, "prompt": "p", "expected_output": "e", **extra}

    def rejects(self, evals, name="demo"):
        write_evals(self.skill, evals, name)
        with self.assertRaises(EvalSetError) as caught:
            load_evals(self.skill)
        return str(caught.exception)

    def test_accepts_valid_file(self):
        write_evals(self.skill, [self.case(files=["evals/files/case/"], assertions=["a"])])
        self.assertEqual(load_evals(self.skill)["evals"][0]["id"], 1)

    def test_rejects_expectations_key(self):
        self.assertIn("assertions", self.rejects([self.case(expectations=["a"])]))

    def test_rejects_skill_file_under_evals(self):
        (self.skill / "evals/files/case/SKILL.md").write_text("x")
        self.assertIn("SKILL.md", self.rejects([self.case()]))

    def test_rejects_path_outside_files(self):
        (self.skill / "notes.txt").write_text("n")
        self.rejects([self.case(files=["notes.txt"])])
        self.rejects([self.case(files=["evals/files/../../notes.txt"])])

    def test_rejects_duplicate_ids(self):
        self.assertIn("duplicate id", self.rejects([self.case(), self.case()]))

    def test_rejects_other_skill_name(self):
        self.assertIn("does not match", self.rejects([self.case()], name="other"))

    def test_rejects_duplicate_queries(self):
        path = self.tmp / "queries.json"
        path.write_text(json.dumps([{"query": "q", "should_trigger": True}] * 2))
        with self.assertRaises(EvalSetError):
            load_queries(path)

    def test_copy_inputs_places_files_and_directory_contents(self):
        (self.skill / "evals/files/b.txt").write_text("b")
        work = self.tmp / "work"
        work.mkdir()
        copied = copy_inputs(self.skill, ["evals/files/b.txt", "evals/files/case/"], work)
        self.assertEqual(copied, ["a.txt", "b.txt"])
        self.assertEqual((work / "a.txt").read_text(), "a")

    def test_copy_inputs_rejects_collisions(self):
        (self.skill / "evals/files/a.txt").write_text("other")
        work = self.tmp / "work"
        work.mkdir()
        with self.assertRaises(EvalSetError):
            copy_inputs(self.skill, ["evals/files/a.txt", "evals/files/case/"], work)


class ArmTests(TempDirTest):
    def plugin(self):
        plugin = self.tmp / "plugin"
        (plugin / "skills").mkdir(parents=True)
        (plugin / "plugin.json").write_text("{}")
        skill = make_skill(plugin / "skills")
        (skill / "evals").mkdir()
        (skill / "evals/evals.json").write_text("{}")
        make_skill(plugin / "skills", "sibling")
        return plugin, skill

    def test_omp_arms_share_the_plugin_and_differ_only_in_the_skill(self):
        plugin, skill = self.plugin()
        client = omp.OmpClient()
        with_arm = client.prepare_arm("with_skill", skill, self.tmp / "arms", plugin)
        without = client.prepare_arm("without_skill", skill, self.tmp / "arms", plugin)
        self.assertEqual(sorted(p.name for p in (with_arm.plugin_dir / "skills").iterdir()),
                         ["demo", "sibling"])
        self.assertFalse((with_arm.skill_dir / "evals").exists())
        self.assertIsNone(without.skill_dir)
        self.assertEqual([p.name for p in (without.plugin_dir / "skills").iterdir()], ["sibling"])


class RunCollectionTests(TempDirTest):
    def test_keeps_saved_and_changed_files_but_not_untouched_inputs(self):
        work, scratch, outputs = self.tmp / "work", self.tmp / "scratch", self.tmp / "outputs"
        for path in (work / ".git", scratch, outputs):
            path.mkdir(parents=True)
        (work / "input.txt").write_text("same")
        (work / "edited.txt").write_text("before")
        inputs = file_digests(work)
        (work / "edited.txt").write_text("after")
        (work / "new/report.md").parent.mkdir()
        (work / "new/report.md").write_text("new")
        (work / ".git/index").write_text("git")
        (scratch / "answer.md").write_text("saved")
        collect_outputs(scratch, work, inputs, outputs)
        found = sorted(p.relative_to(outputs).as_posix() for p in outputs.rglob("*") if p.is_file())
        self.assertEqual(found, ["answer.md", "working-directory/edited.txt",
                                 "working-directory/new/report.md"])

    def test_rerun_into_iteration_with_changed_skill_is_refused(self):
        skill = make_skill(self.tmp / "src")
        record = {"client": "omp", "skill_digest": tree_digest(skill, skip_evals=True)}
        prepare_iteration(self.tmp / "it", record)
        (skill / "SKILL.md").write_text(SKILL_MD + "More guidance.\n")
        changed = dict(record, skill_digest=tree_digest(skill, skip_evals=True))
        with self.assertRaises(SystemExit) as caught:
            prepare_iteration(self.tmp / "it", changed)
        self.assertIn("skill_digest", str(caught.exception.code))


class InterruptTests(TempDirTest):
    def tearDown(self):
        base.INTERRUPTED.clear()

    def test_stop_all_ends_running_client_and_marks_it_failed(self):
        errors = []

        def run():
            try:
                base.stream(["sleep", "30"], {"PATH": "/bin:/usr/bin"}, self.tmp, 60)
            except RuntimeError as error:
                errors.append(str(error))

        worker = threading.Thread(target=run)
        worker.start()
        for _ in range(50):
            if base._ACTIVE:
                break
            threading.Event().wait(0.05)
        base.stop_all()
        worker.join(timeout=5)
        self.assertFalse(worker.is_alive())
        self.assertEqual(errors, ["interrupted"])


class ReviewViewerTests(TempDirTest):
    def test_shows_nested_outputs_and_marks_unmeasured_runs(self):
        run = self.tmp / "eval-1" / "with_skill" / "run-1"
        (run / "outputs/working-directory/docs").mkdir(parents=True)
        (run / "outputs/working-directory/docs/adr.md").write_text("adr")
        (run / "outputs/metrics.json").write_text("{}")
        (run / "timing.json").write_text(json.dumps({"error": "timed out after 900s"}))
        (self.tmp / "eval-1/eval_metadata.json").write_text(json.dumps({"eval_id": 1, "prompt": "p"}))
        built = generate_review.build_run(self.tmp, run)
        self.assertEqual([o["name"] for o in built["outputs"]], ["working-directory/docs/adr.md"])
        self.assertTrue(built["prompt"].startswith("[UNMEASURED RUN: timed out after 900s]"))


class ImproverTests(unittest.TestCase):
    def test_unmeasured_queries_are_not_reported_as_failures(self):
        prompts = []
        results = {"results": [
            {"query": "never measured", "should_trigger": False, "pass": False, "triggers": 0,
             "runs": 3, "unmeasured": True},
            {"query": "real false trigger", "should_trigger": False, "pass": False,
             "triggers": 3, "runs": 3},
        ], "summary": {"passed": 0, "total": 2}}
        history = [{"description": "old", "train_passed": 0, "train_total": 2,
                    "results": results["results"]}]
        improve_description("demo", "body", "old", results, history,
                            lambda prompt: prompts.append(prompt) or "<new_description>x</new_description>")
        summary = prompts[0].split("</scores_summary>")[0]
        failures = summary.split("PREVIOUS ATTEMPTS")[0]
        self.assertIn("real false trigger", failures)
        self.assertNotIn("never measured", failures)
        self.assertIn('[UNMEASURED] "never measured"', summary)
        self.assertNotIn('[FAIL] "never measured"', summary)

    def test_measured_failure_survives_another_clients_missing_runs(self):
        def row(runs, triggers, passed):
            return {"query": "q", "should_trigger": False, "triggers": triggers, "runs": runs,
                    "errors": 3 - runs, "trigger_rate": None, "pass": passed}
        missing = merge_results({"omp": {"results": [row(0, 0, False)]},
                                 "codex": {"results": [row(3, 3, False)]}})[0]
        only_missing = merge_results({"omp": {"results": [row(0, 0, False)]},
                                      "codex": {"results": [row(3, 0, True)]}})[0]
        self.assertFalse(missing["unmeasured"])
        self.assertTrue(only_missing["unmeasured"])


class InterruptedRunTests(TempDirTest):
    def tearDown(self):
        base.INTERRUPTED.clear()

    def test_queued_run_after_interrupt_keeps_earlier_result(self):
        run_dir = self.tmp / "run-1"
        run_dir.mkdir()
        (run_dir / "timing.json").write_text(json.dumps({"error": None}))
        base.INTERRUPTED.set()
        self.assertFalse(run_one(None, None, self.tmp, {"id": 1}, None, run_dir, 1))
        self.assertEqual(json.loads((run_dir / "timing.json").read_text()), {"error": None})


class AggregateTests(TempDirTest):
    def test_delta_is_with_skill_minus_old_skill(self):
        for config, passed, seconds in (("old_skill", 1, 10), ("with_skill", 3, 30)):
            run = self.tmp / "eval-1" / config / "run-1"
            run.mkdir(parents=True)
            (run / "grading.json").write_text(json.dumps({
                "expectations": [], "summary": {"passed": passed, "failed": 3 - passed,
                                                "total": 3, "pass_rate": passed / 3}}))
            (run / "timing.json").write_text(json.dumps({"total_duration_seconds": seconds,
                                                         "total_tokens": 100}))
        delta = aggregate_benchmark.generate_benchmark(self.tmp)["run_summary"]["delta"]
        self.assertEqual((delta["pass_rate"], delta["time_seconds"]), ("+0.67", "+20.0"))

    def test_unmeasured_runs_mark_coverage_incomplete(self):
        (self.tmp / "iteration.json").write_text(json.dumps({"runs": 2}))
        for config in ("with_skill", "without_skill"):
            for number in (1, 2):
                run = self.tmp / "eval-1" / config / f"run-{number}"
                run.mkdir(parents=True)
                timed_out = config == "with_skill" and number == 2
                (run / "timing.json").write_text(json.dumps(
                    {"error": "timed out" if timed_out else None, "total_duration_seconds": 1}))
                if not timed_out:
                    (run / "grading.json").write_text(json.dumps({
                        "expectations": [], "summary": {"passed": 1, "failed": 0, "total": 1,
                                                        "pass_rate": 1.0}}))
        benchmark = aggregate_benchmark.generate_benchmark(self.tmp)
        self.assertFalse(benchmark["metadata"]["coverage_complete"])
        self.assertIn("eval-1 with_skill: 1 graded, 1 measured of 2 runs",
                      aggregate_benchmark.generate_markdown(benchmark))


class GradingTests(unittest.TestCase):
    def test_finds_json_in_prose_and_computes_summary(self):
        text = ('Here you go: {"note": 1} then {"expectations": ['
                '{"text": "x", "passed": true, "evidence": "seen"},'
                '{"text": "y", "passed": false, "evidence": "missing"}],'
                ' "summary": {"passed": 2}} trailing')
        grading = parse_grading(text, ["A", "B"])
        self.assertEqual([e["text"] for e in grading["expectations"]], ["A", "B"])
        self.assertEqual(grading["summary"],
                         {"passed": 1, "failed": 1, "total": 2, "pass_rate": 0.5})

    def test_rejects_wrong_count(self):
        text = '{"expectations": [{"text": "x", "passed": true, "evidence": "e"}]}'
        with self.assertRaises(ValueError):
            parse_grading(text, ["A", "B"])


class SelectBestTests(unittest.TestCase):
    def test_prefers_best_weakest_client(self):
        def entry(iteration, omp_score, codex_score):
            return {"iteration": iteration, "client_scores": {
                "omp": {"train_passed": 0, "test_passed": omp_score},
                "codex": {"train_passed": 0, "test_passed": codex_score}}}
        history = [entry(1, 6, 2), entry(2, 5, 5)]
        self.assertEqual(select_best(history, True)["iteration"], 2)


class FakeClient:
    def __init__(self, listed=None, error=None):
        self.listed, self.error = listed or [], error

    def list_skills(self, cwd, settings):
        if self.error:
            raise RuntimeError(self.error)
        return [(name, None) for name in self.listed]


class HomeCheckTests(unittest.TestCase):
    settings = Settings("m", "high", Path("/homes/test"), 10)

    def test_rejects_installed_skill_in_any_namespace(self):
        for listed in ("writing-adrs", "decision-workflow/writing-adrs",
                       "decision-workflow:writing-adrs"):
            problem = check_home(FakeClient([listed]), self.settings, "writing-adrs")
            self.assertIn("already has a skill named writing-adrs", problem)

    def test_accepts_home_without_the_skill(self):
        client = FakeClient(["writing-adrs-extra", "skill-creator"])
        self.assertIsNone(check_home(client, self.settings, "writing-adrs"))
        self.assertFalse(name_matches("writing-adrs-extra", "writing-adrs"))

    def test_reports_listing_failure(self):
        problem = check_home(FakeClient(error="no login"), self.settings, "writing-adrs")
        self.assertTrue(problem.startswith("could not list skills in"))


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
