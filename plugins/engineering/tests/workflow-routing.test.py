#!/usr/bin/env python3
"""Check executable edges in the workflow diagrams, without model calls.

--root accepts a frozen pre-fix source tree for regression verification.
This tests diagram routing, not runtime skill compliance or Graphviz rendering.
"""
import argparse
from pathlib import Path
import re
import unittest


parser = argparse.ArgumentParser(description=__doc__)
parser.add_argument("--root", type=Path, default=Path(__file__).resolve().parents[3])
args, test_args = parser.parse_known_args()
SKILLS = args.root / "plugins/engineering/skills"
QUOTED = r'"((?:\\.|[^"\\])*)"'


def graph(skill, name):
    text = (SKILLS / skill / "SKILL.md").read_text()
    body = next(block for block in re.findall(r"```dot\s*\n(.*?)```", text, re.S)
                if "digraph " + name + " {" in block)
    edges = {}
    for source, target, attributes in re.findall(
            QUOTED + r"\s*->\s*" + QUOTED + r"\s*(\[[^\n]*\])?\s*;", body):
        label = re.search(r"label\s*=\s*" + QUOTED, attributes)
        edges.setdefault(source, []).append((target, label.group(1) if label else None))
    return edges


def reachable(edges, start, excluded=()):
    seen, pending = set(), [start]
    while pending:
        node = pending.pop()
        if node not in seen and node not in excluded:
            seen.add(node)
            pending.extend(target for target, _ in edges.get(node, []))
    return seen


class WorkflowRoutingTests(unittest.TestCase):
    def setUp(self):
        self.brainstorming = graph("brainstorming", "brainstorming")
        self.sdd = graph("subagent-driven-development", "process")

    def branch(self, edges, source, label):
        targets = [target for target, value in edges.get(source, []) if value == label]
        self.assertEqual(len(targets), 1, (source, label, targets))
        return targets[0]

    def test_fast_path_routes_owner_specific_causes(self):
        expected = {
            "unknown failure": "Handoff to systematic-debugging",
            "multiple flows or interfaces within existing authority": "Handoff to writing-plans after contract check",
            "requirement or design change": "Reassess changed requirement or design in brainstorming",
        }
        for cause, owner in expected.items():
            with self.subTest(cause=cause):
                self.assertEqual(self.branch(self.brainstorming, "Route nearest normal workflow", cause), owner)

    def test_normal_bounded_route_preserves_same_task_disqualification(self):
        start = self.branch(self.brainstorming, "Route nearest normal workflow",
                            "budget exhausted, resumed or other bounded exploration; no owner-specific cause")
        reached = reachable(self.brainstorming, start,
                            {"Select unaffected task; preserve held task and budgets"})
        self.assertIn("Implement via normal workflow (no plan doc)", reached)
        self.assertIn("Invoke writing-plans skill", reached)
        self.assertNotIn("Run bounded Fast Path", reached)

    def test_brainstorming_hold_can_select_independent_work(self):
        start = "Hold dependent work; ask; continue independent authorized work"
        self.assertIn("Independent authorized work available?", reachable(self.brainstorming, start))
        selected = self.branch(self.brainstorming, "Independent authorized work available?", "yes")
        self.assertEqual(selected, "Select unaffected task; preserve held task and budgets")
        self.assertIn("Check request and existing authority", reachable(self.brainstorming, selected))
        waiting = self.branch(self.brainstorming, "Independent authorized work available?", "no")
        self.assertEqual(self.brainstorming.get(waiting, []), [])

    def test_sdd_blocker_keeps_other_work_runnable_and_held_tasks_pending(self):
        for start in (
            "Return defect to owner; hold dependent task; continue independent authorized work",
            "Record blocker; hold dependent task; continue independent authorized work",
        ):
            with self.subTest(start=start):
                self.assertEqual(self.sdd.get(start), [("Runnable authorized task available?", None)])
        selected = self.branch(self.sdd, "Runnable authorized task available?", "yes")
        self.assertEqual(selected, "Select unaffected task; keep blocked tasks pending")
        self.assertIn("Dispatch implementer subagent (./implementer-prompt.md)", reachable(self.sdd, selected))
        waiting = self.branch(self.sdd, "Runnable authorized task available?", "no")
        self.assertEqual(self.sdd.get(waiting, []), [])
        self.assertEqual(self.branch(self.sdd, "More tasks remain?", "yes, including pending tasks"),
                         "Runnable authorized task available?")

    def test_design_only_does_not_reach_implementation(self):
        target = self.branch(self.brainstorming, "Design/review only?", "yes")
        self.assertEqual(target, "Prepare requested artifact; honor implementation boundary")
        self.assertEqual(self.brainstorming.get(target, []), [])

    def test_pending_check_can_continue_only_independent_work(self):
        pending_check = self.branch(self.brainstorming, "Design/review only?", "no")
        self.assertEqual(pending_check, "Pre-implementation check still pending?")
        start = self.branch(self.brainstorming, pending_check, "yes")
        reached = reachable(self.brainstorming, start,
                            {"Select unaffected task; preserve held task and budgets"})
        self.assertIn("Hold dependent work; ask; continue independent authorized work", reached)
        self.assertIn("Independent authorized work available?", reached)
        self.assertIn("Wait for decision or capability change; held work remains pending", reached)
        self.assertNotIn("Run bounded Fast Path", reached)
        self.assertNotIn("Implement via normal workflow (no plan doc)", reached)
        self.assertNotIn("Invoke writing-plans skill", reached)
        selected = self.branch(self.brainstorming, "Independent authorized work available?", "yes")
        self.assertIn("Check request and existing authority", reachable(self.brainstorming, selected))


if __name__ == "__main__":
    unittest.main(argv=[__file__] + test_args)
