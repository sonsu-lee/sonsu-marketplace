---
name: executing-plans
description: Use when you have a written implementation plan to execute in a separate session with review checkpoints
---

# Executing Plans

## Overview

Load plan, review critically, execute all tasks, report when complete.

**Announce at start:** "I'm using the executing-plans skill to implement this plan."

**Note:** Tell your human partner that Engineering works much better with access to subagents (Claude Code, Codex CLI, Codex App, Copilot CLI, and Gemini CLI all qualify; see the per-platform tool refs in `../using-engineering-skills/references/`). If subagents are available, use engineering:subagent-driven-development instead of this skill.

## The Process

### Step 1: Load and Review Plan
1. Ensure an isolated workspace: use engineering:using-git-worktrees to create one or verify the existing one
2. Read the plan from its approved source; if it is in chat, preserve its exact tasks in todos before execution
3. Review critically - identify any questions or concerns about the plan
4. Read the plan's commit authorization. A plan does not grant permission; confirm it matches the user's request in the current conversation
5. Read the shared [quality gate contract](../using-engineering-skills/references/quality-gates.md) and confirm the plan-readiness gate covers the exact plan revision. A stale, `failed`, `blocked`, `inconclusive`, or required `not_run` gate returns to planning before implementation.
6. If concerns: Raise them with your human partner before starting
7. If no concerns: Create todos for the plan items and proceed

### Step 2: Execute Tasks

For each task:
1. Mark as in_progress
2. Follow each step exactly (plan has bite-sized steps)
3. Run verifications as specified
4. Record the task gate against the exact task diff or artifact revision, including evidence and findings
5. If a check fails, return to the smallest affected implementation step; use `engineering:systematic-debugging` when the cause is not known, then re-run the focused check on the changed artifact
6. Mark as completed only when the task gate is `passed`, or when a human explicitly records `accepted_risk` for that revision

Do not repeat an unchanged failing command or an unchanged reviewer prompt. A missing tool, permission, dependency, or external service is `blocked`; it is not a reason to retry or rewrite the plan blindly. A contradiction in task details returns to `engineering:writing-plans`, and a contradiction in approved requirements returns to `engineering:brainstorming`.

Do not execute `git add`, `git commit`, push, PR, merge, deployment, or any other external action unless that action is explicitly authorized in the current conversation. If an older plan contains an unapproved commit step, skip that step and record it for the final report.

### Step 3: Complete Development

After all tasks complete and verified:

1. Review the complete working-tree diff against the approved plan and related documentation.
2. Run the final required deterministic verification for the whole change.
3. For a major or high-risk inline change, obtain an independent whole-change review when an evaluator is available. If that review is required but unavailable, record `blocked` or `not_run` and ask for a human decision instead of calling the gate passed.
4. Give a valid finding one focused fix and scoped re-review at a time, with at most three review attempts. Return plan or requirement contradictions to their owning stage. At the cap, unresolved required findings need a human decision; only explicit `accepted_risk` may advance them.
5. Record the final gate for the exact working-tree or commit revision. Report what changed, verification evidence, any remaining risk, and whether the status is `passed` or `accepted_risk`.
6. If commit authorization was not granted, stop and ask for the commit decision. Leave the verified changes uncommitted.
7. If commit authorization was granted, commit only the approved scope using the repository's Git rules, verify the resulting commit, then continue. A commit changes the artifact revision, so re-run any final checks whose evidence did not cover the committed tree.
8. Announce: "I'm using the finishing-a-development-branch skill to complete this work."
9. **REQUIRED SUB-SKILL:** Use engineering:finishing-a-development-branch and follow it to present integration options.

## When to Stop and Ask for Help

**STOP executing immediately when:**
- Hit a blocker (missing dependency, test fails, instruction unclear)
- Plan has critical gaps preventing starting
- You don't understand an instruction
- Verification fails repeatedly
- A plan requires a commit or external action that the user did not authorize

**Ask for clarification rather than guessing.**

## When to Revisit Earlier Steps

**Return to Review (Step 1) when:**
- Partner updates the plan based on your feedback
- Fundamental approach needs rethinking

**Don't force through blockers** - stop and ask.

## Remember
- Review plan critically first
- Follow plan steps exactly
- Don't skip verifications
- Reference skills when plan says to
- Stop when blocked, don't guess
- Never start implementation on main/master branch without explicit user consent
