---
name: debugging-code
description: >-
  Investigate an unexpected behavior or bug by tracing its cause. A request
  only to investigate does not authorize a fix or other writes.
---

# Debugging code

Establish the observed failure, expected behavior, scope, and authority. Treat
user-reported observations as evidence; do not repeat a failure in a way the
user or host forbids. Reproduce when safe and permitted, otherwise record the
limitation. Inspect errors, relevant changes, inputs and outputs across actual
boundaries, callers, and working examples. Form a specific hypothesis and test
it with the smallest safe observation. Trace the cause to the layer responsible
for the violated invariant; do not hide a symptom or guess a fix.
For read-only investigation, commands may still create caches, bytecode, logs,
or other files. Prevent those writes or use an authorized disposable copy;
preserve and check source, index, and untracked state.

If fixing is authorized, use `executing-work` before modifying when available;
do not claim invocation of a missing skill. Code and behavioral skill changes
require independent review even for a small diff; if unavailable, report the
work incomplete. Apply the smallest complete root-cause change. Before
writing tests, identify the changed contract, the behavior observable by a
caller, and the happy path. Select only reachable inputs and state boundaries
whose behavior differs; for each test name the plausible bug and smallest
appropriate scope. Derive expected results from requirements, an independent
example, or an external contract, not the implementation. Avoid tests of call
order, mock echoes, wiring, source text, non-emptiness, or tautologies. Keep a
meaningful regression test where useful and feasible; when no test is needed,
explain why and how the behavior was checked. Test-first is optional unless
required by the user or project.

Exercise the same failure path after a fix when allowed, including actual
consumer-visible behavior. Report what was observed and anything unverified.
For investigation-only work, return evidence and limitations without editing.

Assess contract and happy path, reachable boundaries, test design and expected
values, execution evidence, and unnecessary code removal for a fix. Score
applicable items 0, 1, or 2, record exclusions and reasons, and normalize to
10. Require 8/10 and verified requirements, authorization, security, data safety,
confirmed contracts, and stage evidence. Fix supported failures and reevaluate
at most three times, never without changes. If still unsuccessful, report each
score, mandatory conditions, evidence, and blockers. Wait for required decisions,
permission, or access instead of automatically retrying. Required independent
review cannot be replaced by a self-score.
