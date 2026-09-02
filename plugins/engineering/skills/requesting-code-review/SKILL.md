---
name: requesting-code-review
description: Use when completing tasks, implementing major features, or before merging to verify work meets requirements
---

# Requesting Code Review

Dispatch a code reviewer subagent to catch issues before they cascade. The reviewer gets precisely crafted context for evaluation — never your session's history.

**Core principle:** Review early, review often.

Read the shared [quality gate contract](../using-engineering-skills/references/quality-gates.md).
A review is evidence for one declared artifact revision; it is not a general approval of later edits.

## When to Request Review

**Mandatory:**
- After each task in subagent-driven development
- After completing major feature
- Before merge to main

**Optional but valuable:**
- When stuck (fresh perspective)
- Before refactoring (baseline check)
- After fixing complex bug

## How to Request

**1. Freeze the review artifact and revision:**
```bash
BASE_SHA=<the task base or verified merge base>
HEAD_SHA=$(git rev-parse HEAD)
./scripts/review-package range "$BASE_SHA" "$HEAD_SHA"
```

Do not default to `HEAD~1` for a multi-commit task. Use the base recorded before
the task or the verified branch merge base. The script prints a package path and
its SHA-256 revision; record both and pass both to the reviewer. Run
`./scripts/review-package` from this skill's directory.

When the authorized artifact is still uncommitted, freeze the complete working
tree instead:

```bash
./scripts/review-package working-tree
```

This mode includes tracked, staged, and untracked changes and refuses an empty
working tree. Its package is created outside the repository so it does not add
itself to the diff. A digest alone identifies an artifact but does not let a
reviewer inspect it; always pass the readable package path too.

**2. Dispatch code reviewer subagent:**

Dispatch a `general-purpose` subagent, filling the template at [code-reviewer.md](code-reviewer.md)

**Placeholders:**
- `{DESCRIPTION}` - Brief summary of what you built
- `{PLAN_OR_REQUIREMENTS}` - What it should do
- `{REVIEW_PACKAGE}` - Immutable package path printed by `scripts/review-package`
- `{REVIEW_REVISION}` - SHA-256 revision printed for that package

**3. Act on feedback:**
- Fix Critical issues immediately
- Fix Important issues before proceeding
- Note Minor issues for later
- Push back if reviewer is wrong (with reasoning)
- Re-review the focused fix against the changed revision

Record the review gate's artifact, revision, evidence, findings, status, return target, attempt, and decision owner. A reviewer report with missing required verdicts is `inconclusive`. If a required reviewer is unavailable, use `blocked` or `not_run`; never substitute the implementer's self-review or an unchanged retry. A technically disproved finding may be closed with evidence. A valid unresolved required finding needs a changed artifact or explicit human `accepted_risk` before the workflow advances.

## Example

```
[Just completed Task 2: Add verification function]

You: Let me request code review before proceeding.

BASE_SHA=<recorded Task 2 base>
HEAD_SHA=$(git rev-parse HEAD)
./scripts/review-package range "$BASE_SHA" "$HEAD_SHA"

[Script returns]:
  Package: /tmp/engineering-review.ABC123.diff
  Revision: sha256:012345...

[Dispatch code reviewer subagent]
  DESCRIPTION: Added verifyIndex() and repairIndex() with 4 issue types
  PLAN_OR_REQUIREMENTS: Task 2 from .superpowers/plans/deployment-plan.md
  REVIEW_PACKAGE: /tmp/engineering-review.ABC123.diff
  REVIEW_REVISION: sha256:012345...

[Subagent returns]:
  Strengths: Clean architecture, real tests
  Issues:
    Important: Missing progress indicators
    Minor: Magic number (100) for reporting interval
  Assessment: Ready to proceed

You: [Fix progress indicators]
[Continue to Task 3]
```

## Common Rationalizations

| Excuse | Reality |
|--------|---------|
| "I'll just review the diff myself instead of dispatching a reviewer" | You're the coordinator — reviewing the diff inline burns the context window you need to keep driving the work. Dispatch a reviewer subagent: the diff and the evaluation live in its context, and only the findings come back to you. |
| "The reviewer needs my whole session history to understand the change" | Hand it precisely crafted context, never your session's history. That keeps the reviewer on the work product, not your thought process. |

## Red Flags

**Never:**
- Skip review because "it's simple"
- Ignore Critical issues
- Proceed with unfixed Important issues
- Argue with valid technical feedback

**If reviewer wrong:**
- Push back with technical reasoning
- Show code/tests that prove it works
- Request clarification

See template at: [code-reviewer.md](code-reviewer.md)
