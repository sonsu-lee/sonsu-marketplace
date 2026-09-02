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
5. If concerns: Raise them with your human partner before starting
6. If no concerns: Create todos for the plan items and proceed

### Step 2: Execute Tasks

For each task:
1. Mark as in_progress
2. Follow each step exactly (plan has bite-sized steps)
3. Run verifications as specified
4. Mark as completed

Do not execute `git add`, `git commit`, push, PR, merge, deployment, or any other external action unless that action is explicitly authorized in the current conversation. If an older plan contains an unapproved commit step, skip that step and record it for the final report.

### Step 3: Complete Development

After all tasks complete and verified:

1. Review the complete working-tree diff against the approved plan and related documentation.
2. Report what changed, verification evidence, and any remaining risk.
3. If commit authorization was not granted, stop and ask for the commit decision. Leave the verified changes uncommitted.
4. If commit authorization was granted, commit only the approved scope using the repository's Git rules, verify the resulting commit, then continue.
5. Announce: "I'm using the finishing-a-development-branch skill to complete this work."
6. **REQUIRED SUB-SKILL:** Use engineering:finishing-a-development-branch and follow it to present integration options.

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
