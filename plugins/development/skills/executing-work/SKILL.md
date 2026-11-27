---
name: executing-work
description: >-
  Use when executing authorized implementation work inline or with independent
  workers, through verification and final review. Not for plan-only or
  review-only requests.
license: MIT
metadata:
  source: https://github.com/obra/superpowers
  source-commit: 22f0b463e7a5e579904dd6211a520321035526f7
---

# Executing Plans

Execute the plan task by task. **Continuous execution:** Do not pause to check
in with your human partner between tasks. Continue through the approved work;
pause the affected task for a missing decision, permission or prerequisite.
A design or plan alone does not authorize implementation.

## Setup

1. **Load the skills before the material.** For code work, load
   `ponytail:ponytail` before reading code, tests, the plan or other task
   artifacts. For a feature, behavior fix, or new or changed test, load
   `tdd:test-driven-development` before reading its materials or asking for
   their specification. Use the host's installed skill mechanism. An explicit
   native-only request takes precedence: follow its native procedure and
   output without plugin orchestration. Otherwise, if a required skill is
   unavailable, block both the missing stage and any code change depending
   on it. Do not offer native-only as a workaround. Continue only independent
   authorized work.
   Before the first implementation or test edit, check that the host exposes
   the independent reviewers this change requires. If they cannot run, stop
   before editing. Installing the review skill does not enable worker tools.
2. **Read the plan and spec.** The spec is the binding authority, the plan is
   its argument. If a consequential design choice remains, load
   `development:brainstorming` before exploring that choice. For a requested
   plan based on settled requirements, load `development:writing-plans`.
   Execute an already approved plan without asking for approval again.
3. **Scan for conflicts between tasks.** For every task that consumes what an
   earlier task produces, compare their interfaces and the global constraints.
   Resolve discrepancies against the approved requirements. Stop for approval
   if the resolution changes a confirmed contract or expands scope.
4. **Work in the authorized workspace.** Use native task or session state
   where available. Do not create auxiliary workspaces, ledgers or commits
   to track progress. An implementation request does not authorize a branch,
   commit, push, PR, tracker update, merge, deployment or destructive action.

## The Process

- **Inline:** After the review preflight, execute the steps yourself if the
  tasks are coupled, the user chose inline work, or delegation is unavailable
  or inappropriate. Follow [Executing Plans](references/executing-plans.md).
- **Delegated:** For independently runnable slices, read
  [Subagent-Driven Development](references/subagent-driven-development.md)
  and [client execution](references/clients.md) before dispatch. Use one
  controller; a worker does not schedule its own review.
- **Small same-shape work:** When an authorized change repeats one rule across
  files, read [mechanical changes](references/mechanical-changes.md).

### Create the failing test case

Before writing or changing a test, get the user's explicit approval of its
**test specification**: observable interface, initial state and action,
expected result and its independent basis, failure to catch, test type, and
whether an existing check already covers it. An explicitly approved plan
containing that specification counts. Do not ask again for each test.
Reconfirm only the affected specification if the interface or expected
behavior changes. Do not infer approval from a general request to implement.

For approved new behavior, use `tdd:test-driven-development` one behavior at
a time: RED → GREEN → REFACTOR. Reuse an existing check that catches the same
failure. If the host reserves checks for another role, arrange the approved
RED and GREEN observations with that verifier; do not silently skip RED,
claim an unobserved cycle, or implement past a required RED gate.

### Verification Before Completion

**Core principle:** Evidence before claims, always. Before claiming work is
complete, fixed, or passing, read
[Verification Before Completion](references/verification-before-completion.md).
Unless the host or user assigns a different verifier, the inline executor
or delegation controller runs the existing local checks for the authorized
change. Otherwise hand the verifier the entry point and expected result.

## Final Review

Code and behavioral skill changes require independent review, even for a
small diff. For integrated review, load `review:reviewing-code` before
reading review material or dispatching. Its controller applies
`ponytail:ponytail-review` to code and `development:authoring-skills` to
skill changes in the same review. Read [client execution](references/clients.md)
for the current host. Use the requested native review alone for native-only
work. Do not replace a missing independent reviewer with self-review.

Freeze the integrated target. Give the reviewer the approved spec, plan,
actual changes (including uncommitted work), evidence, and review focus.
The review is read-only. After it ends, verify each finding against the
source and contract. Correct in-scope defects; explain declined or deferred
findings. Freeze any changed source or tests and obtain independent re-review
of the changed portion. Repeat only checks whose evidence was invalidated.
Do not present review or evidence for an older revision as final.

## Finish

Before calling the work complete, check for returned reports from every
required reviewer on the frozen change. A dispatch is not a report. Wait for
pending workers. If a required role was skipped and is available, dispatch
that role on the same target and collect its result; do not repeat completed
reviews. If cancellation or lost access prevents recovery, preserve the work,
report the missing role as blocked, and report passing tests separately.

Report changes, decisions, commands, observed outcomes and missing coverage.
Distinguish failed, blocked and unrun checks from passes. Leave the workspace
as-is. If the user requests a branch disposition, read
[Finishing a Development Branch](references/finishing-a-development-branch.md)
and load the applicable Git skill before reading Git artifacts or acting.
Integration and cleanup are the user's decisions, not side effects of
completing the plan.

For a fix or implementation, assess contract and happy path, reachable
boundaries, test design and expected values, execution evidence, and
unnecessary code removal. Score applicable items 0, 1 or 2, explain exclusions
and normalize to 10. Require 8/10 and verified requirements, authority,
security, data safety, contracts and stage evidence. Correct and reevaluate
at most three times, never unchanged; report remaining blockers and scores.
Scores cannot replace actual verification or independent review.
