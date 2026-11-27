# Subagent-Driven Development

Execute the plan by dispatching a fresh implementer subagent per task, a task
review (spec compliance + code quality) after each, and a broad review of
the integrated change at the end.

**Why subagents:** You delegate tasks to specialized agents with isolated
context. They should not need your session's context or history — construct
exactly what they need. This also preserves your own context for coordination.

## When to Use

Use for independently runnable tasks when the host supports delegation and
the user has not requested inline execution. Coupled tasks stay inline. For
two or more independent domains, read
[Dispatching Parallel Agents](dispatching-parallel-agents.md) before dispatch.
Batch small same-shape edits rather than paying for one worker per line.

## Setup

Read the plan and its governing spec. Scan for shared interfaces, conflicting
task instructions and unfinished inputs. Do not use an isolated worker unless
its baseline includes all required staged, unstaged and untracked work and
its creation, auto-application, branch and cleanup effects are authorized.
Use [client execution](clients.md) for the supported interface. No parallel
implementation against shared files or mutable state.

## Model Selection

Use only available roles and model controls permitted by the host. Match
mechanical work to a bounded implementation assignment; reserve judgment and
integration for workers able to assess the contract and its consequences.
Role labels are not evidence of isolation or independence.

## The Task Loop

### 1. Dispatch the implementer

A dispatch prompt describes one task, not the session's history. Provide:

1. The task's full brief or a precise pointer to it; where it fits and what
   it owns. Include the authorized working baseline and global constraints.
2. Interfaces and decisions from earlier tasks that the brief cannot know.
3. The required skills to load before task artifacts, including Ponytail for
   code and TDD for test work; the approved test specification and who owns
   RED, GREEN and final verification. Workers do not grant test approval.
4. Expected observable output, required evidence and limits. One controller
   dispatches reviewers. The implementer does not spawn helpers or reviewers.

### 2. Handle the report

- **DONE:** Freeze the task change, including uncommitted files. Give its
  full scope, exact brief and reported evidence to the independent reviewer.
  A spawn acknowledgment or a worker's assertion is not evidence of a pass.
- **DONE_WITH_CONCERNS:** Read the concerns before proceeding. If they are
  about correctness or scope, address them before review. Note observations
  the reviewer should assess independently.
- **NEEDS_CONTEXT:** Provide the missing context and resume the task.
- **BLOCKED:** Assess the blocker. Supply evidence, split the task or obtain a
  missing decision or permission. Never force the same retry without changes.

### 3. Review the task

Per-task reviews are task-scoped gates. Never accept a report missing either
verdict: spec compliance AND task quality are both required. Assign one
independent task reviewer, not the full
review workflow. Reserve its reviewer batch and runtime check for integration.
Supply the actual diff, brief, results and binding global
constraints. Do not pre-judge findings or ask a reviewer to rerun checks on
unchanged code. If a requirement cannot be verified from the diff, trace it
to unchanged code, another task or the assigned verifier. Unavailable evidence
remains unverified, not a pass.

### 4. The fix loop

The loop triggers when review finds a spec gap, a Critical or Important issue,
or a previously unverified item confirmed as a real gap. Verify the finding
against the source and the approved contract. Tell the implementer what
failed, not how to disguise it. After authorized corrections, freeze the new
target. The assigned verifier repeats affected checks; an independent scoped
re-review judges the correction and new breakage in the changed portion.
Keep deferred observations visible. Do not wave through a load-bearing gap,
retry unchanged or broaden the contract without approval. If three correction
and evaluation rounds do not resolve it, report the blocker and evidence.

### 5. Complete the task

Only mark a task complete when its contract and review gates are met. Continue
newly ready work without check-in prompts. Do not build dependent tasks on
unresolved required behavior.

## Final Review

After integrating all slices, follow [Final Review](../SKILL.md#final-review).
Review their interactions, not just each task again. The final reviewer gets
the full change, original requirements, review focus, evidence and unresolved
concerns. Make corrections, verify and re-review the changed portion before
finishing.

Adapted from [Subagent-Driven Development][upstream] and its task briefs,
preflight, report-handling, fix-loop and final-review references (MIT).
Native dispatch and the review controller replace upstream workspace,
report-file, commit and model-tier requirements.

[upstream]: https://github.com/obra/superpowers/tree/22f0b463e7a5e579904dd6211a520321035526f7/skills/subagent-driven-development
