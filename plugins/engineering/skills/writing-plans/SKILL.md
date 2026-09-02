---
name: writing-plans
description: Use when you have an approved design or requirements for a multi-step implementation task, before touching code
---

# Writing Plans

## Overview

Write a buildable implementation plan for an engineer who knows little about the codebase. Name exact files, interfaces, commands, expected results, documentation impact, and verification appropriate to each change. Keep the plan self-contained, focused, and free of speculative work.

**Announce at start:** "I'm using the writing-plans skill to create the implementation plan."

If execution will use an isolated worktree, create or verify it with `engineering:using-git-worktrees` at execution time.

## Plan Location

The default deliverable is an in-chat plan. Do not create `docs/engineering/plans/` or a dated plan file.

When an execution tool requires a file, save a scratch copy to:

```text
.superpowers/plans/<feature-name>.md
```

The scratch path must be excluded from Git. If the repository already uses an issue, ticket, or another plan location, or the user names one, follow that convention. Writing a plan file does not authorize staging or committing it.

## Documentation Check

Before defining tasks, read the approved design or requirements and the relevant existing documentation. Record one of these outcomes in the plan:

- no documentation change
- update an existing document
- create an approved durable document
- supersede an existing decision

Do not turn the implementation plan itself into a durable design document. If planning exposes a missing decision or a conflict with existing docs, return to the user with the finding before implementation.

## Scope and File Structure

If requirements cover independent subsystems that cannot be implemented and verified on their own, propose separate plans. Before defining tasks, map the exact files to create or modify and each file's responsibility.

- Follow established project patterns.
- Keep units focused and interfaces explicit.
- Fold setup, configuration, documentation, and migration work into the task whose deliverable needs them.
- Split tasks only where a reviewer could meaningfully approve one and reject another.
- Do not include unrelated refactoring.

## Verification Selection

Choose verification per task instead of applying one ceremony to every change.

| Change | Plan |
| --- | --- |
| New or changed code behavior | Use `engineering:test-driven-development`; include RED, GREEN, and regression commands |
| Bug fix | Reproduce with a failing test, fix, and retain the regression test |
| Refactoring that can change behavior | Protect affected behavior with tests before refactoring |
| Documentation | Check links, paths, examples, and consistency with related docs |
| Skill instructions | Validate frontmatter and paths; add realistic behavior evaluation only when risk warrants it |
| Manifest or metadata | Parse syntax, verify referenced paths, and use the native loader when available |
| Simple configuration | Run the smallest command that consumes the changed configuration |

Do not add tests that merely duplicate static text, metadata, or the implementation. TDD's test-first cycle applies when the task changes production behavior.

## Commit Authorization

A plan never grants Git permission. Determine the current state from the user's request and write one of these values in the header:

```text
Commit authorization: granted for this plan
Commit authorization: not granted
```

Do not add `git add` or `git commit` as task steps. You may list potential commit boundaries as advisory notes, but execution requires explicit authorization. Push, PR, merge, and deployment remain separate permissions.

`engineering:subagent-driven-development` relies on task commits for recovery and review ranges. Offer it only when task commits are explicitly authorized. Otherwise use inline `engineering:executing-plans`, report the completed diff, and ask for the commit decision.

## Plan Header

Every plan, including an in-chat plan, starts with the fields below so its requirements,
documentation action, and Git boundary survive handoff. A short in-chat plan may omit
`Approach` and `Global Constraints` only when the plan prose already states the approach
and there are no additional global constraints; it must retain `Requirements source`,
`Documentation impact`, and `Commit authorization`.

```markdown
# [Feature Name] Implementation Plan

**Goal:** [one sentence]

**Approach:** [two or three sentences]

**Requirements source:** [approved document, issue, ticket, or user-approved conversation design]

**Documentation impact:** [none, update path, create approved path, or supersede decision]

**Commit authorization:** [granted for this plan | not granted]

## Global Constraints

[Exact project-wide constraints that every task must preserve]
```

If no durable requirements document exists, include enough approved context in the plan for an executor that cannot read the original conversation.

## Task Structure

Use checkbox steps for file-backed plans so execution can track progress.

````markdown
### Task N: [Deliverable]

**Files:**
- Create: `exact/path/to/file.py`
- Modify: `exact/path/to/existing.py:123`
- Verify: `tests/exact/path/to/test.py` or the applicable validation target

**Interfaces:**
- Consumes: [exact earlier interface or input]
- Produces: [exact interface later tasks rely on]

**Verification:** [TDD, regression test, native loader, syntax/path check, or other proportionate method]

- [ ] **Step 1: Establish the expected behavior or invariant**

[Actual test, command, or invariant. For TDD tasks, include the failing test and expected failure.]

- [ ] **Step 2: Make the minimal change**

[Exact edit or code needed; no placeholders.]

- [ ] **Step 3: Verify the result**

Run: `[exact command]`
Expected: `[observable result]`

- [ ] **Step 4: Review task diff and documentation consistency**

[Exact paths and requirements to compare.]
````

## No Placeholders

A plan is not buildable if it contains:

- `TBD`, `TODO`, "implement later", or "fill in details"
- "add appropriate error handling" without the actual rule
- "write tests" without the behavior, test location, and command
- "similar to Task N" when the executor may see tasks independently
- an interface that no task defines
- a verification step with no observable expected result

## Self-Review

Before handoff:

1. Map every approved requirement to a task.
2. Check all paths, interface names, types, and exact values across tasks.
3. Remove placeholders and speculative work.
4. Confirm each task's verification matches its change type.
5. Confirm no task performs a commit, push, PR, merge, or deployment beyond current authorization.
6. Confirm the documentation impact matches existing project docs.

Fix issues inline before presenting the plan.

## Execution Handoff

Report where the plan lives and its commit authorization state. Offer only applicable execution choices:

- **Inline execution:** use `engineering:executing-plans`; implement and verify, then report the diff before any unapproved commit.
- **Subagent-driven execution:** use `engineering:subagent-driven-development` only when a file-backed plan exists, subagents are available, and task commits are explicitly authorized.

Do not imply that choosing an execution mode grants additional Git or external-action permission.
