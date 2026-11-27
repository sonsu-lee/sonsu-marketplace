---
name: writing-plans
description: >-
  Use when you have a spec or requirements for a multi-step task, before
  touching code, or when an implementation plan is requested. Not for
  choosing a new design or executing an already approved plan.
license: MIT
metadata:
  source: https://github.com/obra/superpowers
  source-commit: 22f0b463e7a5e579904dd6211a520321035526f7
---

# Writing Plans

## Overview

Write implementation plans for an engineer who has not seen this codebase or
this spec. Assume they write idiomatic code in the project's language once
they know the exact interface and the exact test, and that they will make a
reasonable choice wherever the plan leaves one open. What they cannot know
is what you decided: which files, which names and signatures, which values
from the spec, which tests prove each task. Document those. Give them the
whole plan as bite-sized tasks. DRY. YAGNI. TDD.

**Context:** start from the approved design, PRD, or settled requirements,
including decisions made in chat. If a material design choice remains open,
load `development:brainstorming` before further design work. Do not reopen
what they already decided. When a PRD is the input, load `prd:writing-prd`
and apply its `references/plan-readiness.md` gate first; until it passes,
plan no part of that PRD.

**Where it goes:** return the plan in chat unless they authorized a file
and destination. Use an undated name. Do not create a worktree or commit.

## Scope Check

If the spec covers multiple independent subsystems, it should have been
broken into sub-project specs during brainstorming. If it wasn't, suggest
breaking this into separate plans — one per subsystem. Each plan should
produce working, testable software on its own.

## File Structure

Before inspecting source, load `ponytail:ponytail`; if missing, stop before
reading code. Load `tdd:test-driven-development` before inspecting a target
for a feature, behavior fix, or test change.

Before defining tasks, map out which files will be created or modified and
what each one is responsible for. This is where decomposition decisions get
locked in.

- Design units with clear boundaries and well-defined interfaces. Each file
  should have one clear responsibility.
- Prefer smaller, focused files over large ones that do too much.
- Files that change together should live together. Split by responsibility,
  not by technical layer.
- In existing codebases, follow established patterns. If the codebase uses
  large files, don't unilaterally restructure — but if a file you're modifying
  has grown unwieldy, including a split in the plan is reasonable.

This structure informs the task decomposition. Each task should produce
self-contained changes that make sense independently.

## Task Right-Sizing

A task is the smallest unit that carries its own test cycle and is worth a
fresh reviewer's gate. When drawing task boundaries: fold setup,
configuration, scaffolding, and documentation steps into the task whose
deliverable needs them; split only where a reviewer could meaningfully
reject one task while approving its neighbor. Each task ends with an
independently testable deliverable.

## Step Granularity

Each step is one action with a checkable result. For one approved behavior:

- "Write the failing test" (or use the existing one that catches this failure).
- "Run it to make sure it fails" for the missing behavior.
- "Implement the minimal code to make the test pass."
- "Run the test and make sure it passes."
- "Refactor while green; rerun the affected checks."

## Plan Document Header

Before writing the plan, read the [plan and task template](references/plan-template.md).
Start with its approval section, header, global constraints, and review
focus. Include the spec or design from chat so the executor has both.

## Task Structure

Use the template's Files and Interfaces blocks. Order tasks by their real
dependencies. Include the **test specification** for each
changed behavior: observable interface, initial state and action, expected
result and its basis, failure the test must catch, test type, and whether an
existing check already covers it. Derive expectations from the contract,
not the proposed implementation. Reuse the existing check if it catches the
same failure. If no automated test applies, state why and what evidence to
collect instead.

## What a Step Contains

A step is done when the implementer can write exactly one reasonable thing
from it. That is the whole requirement: unambiguous, not complete. Each kind
of step carries what makes it unambiguous and nothing more:

- **A test step:** the test's name and its assertions, with the spec's exact
  values in them. Show them as part of the proposed plan, not a test-file edit.
- **A code step:** the exact signature (name, parameters, return type), the
  file it lives in, and the specific values the spec pins. The implementer
  writes the body. A body appears only for an algorithm the signature and
  tests do not determine, or for exact copy the spec fixes.
- **A verification step:** the command to run and the output that means it
  passed.
- **A reference to another task:** that task's Interfaces block says what
  to use; the plan does not repeat that task's code.

A plan is the set of decisions the implementer cannot make alone. A plan
longer than the code it describes has written the code instead. Lines that
decide nothing ("TBD", "handle edge cases", "add appropriate validation",
"write tests for the above", a type or function no task defines) are the
opposite failure, and the self-review catches both.

## Self-Review

After writing the complete plan, look at the spec with fresh eyes and check
the plan against it. Run this checklist yourself, then apply the
[plan gate](references/plan-gate.md): yourself for a one-task plan, a fresh
worker for a larger plan handed to execution.

1. **Spec coverage:** skim each requirement. Can you point to a task that
   implements it? List any gaps.
2. **Step scan:** a line that decides nothing is a gap, a function body the
   signature and tests already determine is a transcript. Fix both.
3. **Type consistency:** do the types, method signatures, and property names
   used in later tasks match what you defined in earlier tasks? A function
   called `clearLayers()` in Task 3 but `clearFullLayers()` in Task 7 is a bug.
4. **Review Focus:** for each reachable input class or failure mode the spec
   implies, is there a task whose tests exercise it? Put the most important
   uncovered cases in Review Focus and add each test to the owning task.
   An empty section means you checked and found none.
5. **Proportion:** if code blocks are most of the plan, replace bodies with
   signatures, test names and assertions. Check that each step is still
   unambiguous.

If you find issues, fix them inline. If you find a spec requirement with no
task, add the task.

## Execution Handoff

Present the plan with its test specification for explicit user approval
**before writing tests**. For a plan-only request, stop with the plan.
Approval of a design does not approve test cases the user has not seen.
Approval of a plan containing the concrete specification covers those cases:
do not ask again for each test. If a plan was already approved without the
specification, ask only for the missing specification. If the interface or
expected behavior changes, reconfirm only the affected cases.

For authorized implementation, preserve the execution method they supplied.
If inline and delegated execution are both permitted and the choice matters,
recommend one based on task dependencies and the cost of a mistake. Include
the choice in the plan discussion rather than adding another approval.
After approval, load `development:executing-work` to execute the plan;
use `tdd:test-driven-development` for one approved behavior at a time.
Report an unavailable required skill; don't silently skip the stage.
