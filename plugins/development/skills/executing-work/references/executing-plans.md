# Executing Plans

Execute the plan yourself, task by task, in this session: no implementer
subagent per task, no reviewer per task. One fresh-context review of the
whole change at the end.

**Why inline:** Subagent-driven development pays for a fresh implementer
and a fresh reviewer on every task, each re-reading the codebase from zero.
Inline execution pays for one context (yours) plus one final review round.
What it gives up is a fresh context per task and a second pair of eyes per
task. The brief is the specification, the approved test behavior is the
per-task gate, and the final review is the second pair of eyes.

## When to Use

- Your human partner chose inline execution at the handoff.
- Implementation workers are unavailable but required independent reviewers
  can run. If a required reviewer cannot run, stop before editing.
- Tasks are coupled, share files or depend on unfinished inputs.

## Setup

Read the plan once, note its context and Global Constraints. If the plan
names a Spec, read that too: the spec is the authority the plan argues
from, and conflicts inside the plan resolve against it. Use the authorized
workspace and native task state. After a handoff, resume from the actual
changes and observed results, not from memory alone.

## The Task Loop

### 1. Take the task

Read the task's full brief, including exact values, signatures and approved
test cases. Identify its expected output and inputs from earlier tasks.

### 2. Work the steps

Follow the approved RED-GREEN order for new behavior. Watching the right
test fail is a step, not a formality: a test that passes before the
implementation exists is a finding about the test.

Every verification step has an expected result. The assigned verifier
runs the authorized command, reads its output, and compares. Three outcomes:

- **Matches.** Next step.
- **The code is wrong.** Load `development:debugging-code` before investigating.
  Find the cause; never patch the symptom to make the step's output match.
- **The plan is wrong.** A step contradicts the spec, an interface from an
  earlier task doesn't match what this task consumes, or a command cannot
  work. Use the smallest correction supported by the approved spec. Record
  the decision and its basis in the handoff. Ask before changing a contract.

### 3. The completion contract

Before marking the task verified, all of the following are true, with
evidence on the revision in question — not inferred from the diff looking
right:

- The approved behaviors are covered without duplicating existing tests.
- Each expected result was compared against real output by the assigned
  verifier. If checks are reserved until integration, hand off as unverified.
- Each deviation from the brief has a decision and a reason.

### 4. Complete the task

Take the next ready task. If the test or comparison failed, do not mark it
as passed. Resolve the failure or report the affected work as incomplete.

## Final Review

Use the final review in [Executing Plans](../SKILL.md#final-review). Give the
reviewer the whole change, not just the last task or the last commit. A
self-review by the author is not a fresh review.

## Finish

Report what you changed, what you observed, decisions and deferred findings.
Do not commit, publish or clean up a workspace merely because a task is done.

## Common Rationalizations

- **“I remember what Task N says”** — You remember a summary. The brief has
  the exact values. Read it.
- **“Let me check in before the next task”** — Continue approved tasks. Ask
  for decisions, not progress permission.
- **“Tests should pass, the change was trivial”** — “Should” is not evidence.
  The contract requires the command and its output.

Adapted from [Executing Plans][upstream] (MIT). Native task state and review
replace upstream workspace scripts, per-task commits and the progress ledger.

[upstream]: https://github.com/obra/superpowers/blob/22f0b463e7a5e579904dd6211a520321035526f7/skills/executing-plans/SKILL.md
