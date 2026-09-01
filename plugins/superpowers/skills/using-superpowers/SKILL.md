---
name: using-superpowers
description: Use when starting any conversation to determine which Superpowers skills apply before responding or acting
---

<SUBAGENT-STOP>
If you were dispatched as a subagent to execute a specific task, ignore this skill.
</SUBAGENT-STOP>

<EXTREMELY-IMPORTANT>
If you think there is even a 1% chance a Superpowers skill might apply to what you are doing, you ABSOLUTELY MUST invoke that Superpowers skill.

IF A SUPERPOWERS SKILL APPLIES TO YOUR TASK, YOU DO NOT HAVE A CHOICE. YOU MUST USE IT.

This is not negotiable. You cannot rationalize your way out of this.

This mandatory rule is scoped to skills provided by Superpowers. Use skills from other plugins only when the user requests them, repository instructions require them, or a concrete need in the current task makes them materially useful. Mere topical relevance is not enough to invoke every available external skill.
</EXTREMELY-IMPORTANT>

<GIT-AUTHORIZATION-GATE>
No plan, skill, reference file, execution mode, worktree state, or platform limitation grants Git permission. Stage requested changes only as part of an explicitly authorized commit or when staging itself was requested. Commit only when the user explicitly authorized it for the current work. Push, PR creation, merge, deployment, and destructive Git operations require their own applicable authorization.

This gate overrides downstream wording that says to commit automatically, including the ignore-file commit step in `using-git-worktrees` and platform-specific finishing guidance. When commit authorization is absent, make the workspace safe without committing if possible, then report the diff and ask for the commit decision.
</GIT-AUTHORIZATION-GATE>

## The Rule

**Invoke applicable Superpowers skills and any external skill selected under the policy above BEFORE any response or action** — including clarifying questions, exploring the codebase, or checking files. If a selected skill turns out wrong for the situation, you don't have to keep using it.

**Before entering plan mode:** if you haven't already brainstormed, invoke the brainstorming skill first.

Then announce "Using [skill] to [purpose]" and follow the skill exactly. If it has a checklist, create a todo per item.

## Skill Priority

When multiple Superpowers skills apply, process skills come first — they set the approach, then implementation skills (frontend-design, etc.) carry it out. Brainstorming and systematic-debugging are Superpowers' most common process skills, but the rule holds for any Superpowers skill selected for the task.

- "Let's build X" → superpowers:brainstorming first, then implementation skills.
- "Fix this bug" → superpowers:systematic-debugging first, then domain skills.

## Red Flags

These thoughts mean STOP—you're rationalizing:

| Thought | Reality |
|---------|---------|
| "This is just a simple question" | Questions are tasks. Check for applicable Superpowers skills. |
| "I need more context first" | The Superpowers skill check comes BEFORE clarifying questions. |
| "Let me explore the codebase first" | Superpowers skills can define HOW to explore. Check them first. |
| "I can check git/files quickly" | Files lack conversation context. Check applicable Superpowers skills first. |
| "Let me gather information first" | An applicable Superpowers skill can define HOW to gather information. |
| "This doesn't need a formal skill" | If a Superpowers skill applies, use it. |
| "I remember this skill" | Superpowers skills evolve. Read the current version. |
| "This doesn't count as a task" | Action = task. Check applicable Superpowers skills. |
| "The skill is overkill" | If a Superpowers skill applies, follow it and scale its ceremony where it allows. |
| "I'll just do this one thing first" | Check applicable Superpowers skills BEFORE doing anything. |
| "This feels productive" | Undisciplined action wastes time. Applicable Superpowers workflows prevent this. |
| "I know what that means" | Knowing the concept ≠ using an applicable Superpowers skill. Invoke it. |

## Platform Adaptation

If your harness appears here, read its reference file for special instructions:

- Codex: `references/codex-tools.md`
- Pi: `references/pi-tools.md`
- Antigravity: `references/antigravity-tools.md`
- Hermes Agent: `references/hermes-tools.md`

## User Instructions

User instructions (CLAUDE.md, AGENTS.md, GEMINI.md, etc, direct requests) take precedence over skills, which in turn override default behavior. Only skip skill workflows or instructions when your human partner has explicitly told you to.
