---
name: authoring-skills
description: >-
  Use this skill when creating, revising, or reviewing an agent skill,
  including defining its scope, deciding what belongs in SKILL.md,
  delegating work to tools, or reducing unnecessary instructions.
  Not for installing skills or editing ordinary documentation.
---

# Authoring skills

A skill teaches an agent the judgment and minimum procedure for one coherent
task. It is not a tool manual: delegate mechanical execution and checks to
existing tools. The target project's authoring requirements come first.

## Workflow

1. **Ground the task.** Start from real requests, successful work,
   corrections, and project artifacts. Define the outcome, when the skill
   applies, and the nearby tasks it excludes. Ask only about consequential
   gaps the context cannot answer.
2. **Scope one unit.** One reusable unit of work per skill. Split
   independently useful workflows, not source-document chapters.
3. **Identify consumers.** Use the request and project evidence, not the
   client you are running in. Read only the matching references:

   | Consumer | Reference |
   | --- | --- |
   | omp | [omp](references/omp.md) |
   | Claude Code, claude.ai, or Claude API | [Claude](references/claude.md) |
   | Codex | [Codex](references/codex.md) |

   Without a named target, stay portable and add no client metadata.
4. **Keep only what prevents mistakes.** For each instruction, ask whether
   omitting it would cause a meaningful mistake. Keep domain knowledge,
   project conventions, decision criteria, and non-obvious constraints; drop
   general knowledge and ordinary tool usage. Test uncertain omissions.
5. **Place each responsibility** (below), then write the guidance.
6. **Verify and refine** (below).

## Place each responsibility

- **SKILL.md:** purpose, decision criteria, defaults, the minimum workflow, and
  constraints needed on every run.
- **references/:** detail needed only under a stated condition. Say when to
  read each file.
- **assets/ and configuration:** reusable output structures and executable
  rule values. Do not restate a validator's logic in prose.
- **Existing tools:** mechanical execution and deterministic checks, invoked
  directly rather than through a new wrapper.
- **scripts/:** only for logic agents repeatedly reinvent or get wrong, as
  shown by actual runs. See [Using scripts][scripts].
- **evals/:** evaluation cases. Installation, registration, and evaluation
  procedures stay in project documentation.

## Write the guidance

- Follow the [Agent Skills specification][specification] for metadata and
  layout. Set `compatibility` only for real requirements.
- **Description:** user intent, implicit uses, and boundaries with adjacent
  work, key use case first. Do not add keywords for single failed prompts.
- **Body:** clear headings and direct language. Use numbered steps for
  ordered work, lists for independent rules, and prose only where a decision
  needs its reasons.
- **Defaults:** pick one and name alternatives briefly. Be exact only where
  variation risks correctness or safety.
- **Constraints:** separate defaults from binding host, security, project,
  and user constraints, and say when a default yields. Never invent approvals
  or weaken permission boundaries.
- **Gotchas:** put non-obvious facts where the agent reads them before it can
  make the mistake. Give conditional references recognizable triggers.
- **Examples:** only to resolve ambiguity.

## Delegate to tools

- Reuse the target repository's tool, version, and configuration. With no
  setup, use an existing CLI at a pinned version.
- State each tool's trigger, exact input, success evidence, and the judgment
  left to the agent. Mechanical success is not semantic correctness.
- Bundled scripts take non-interactive input, give helpful errors and
  meaningful exit status, and disclose side effects.

## Verify and refine

1. **Format and loading:** run the project's checks and the official
   validator. They do not show that the skill helps.
2. **Behavior:** run the [Agent Skills evaluation loop][evaluation] on
   `evals/evals.json`, with and without the skill or its previous version.
   Read [Choosing evaluation](references/evaluation.md) to pick checks and
   runners.
3. **Revise** from failed assertions, feedback, and transcripts. Generalize
   recurring failures with the smallest change, including deletion.
4. **Review:** for new skills or behavior changes, get an independent
   skill-criteria review with the purpose, consumers, changed files,
   requirements, and review question, not your rationale. In omp use
   `skill-workflow-reviewer`; in Codex or Claude Code, a generic worker given
   this file's absolute path. Verify findings before revising.
5. **Report** the checks actually performed and any limitations.

## Gotchas

- Moving text into a reference that is always loaded saves no context.
- Size guidance in the specification is not a loading guarantee; check the
  client limit in its reference.
- Authoring checks grant no permission to write, install, or publish. When
  writes are prohibited, return proposals as text and create no files.
- When a skill stops or redirects work, cite the instruction that requires it.

## Sources

- [Best practices][practices]: scope, context economy, and calibrated guidance.
- [Optimizing descriptions][descriptions]: intent and activation boundaries.
- [Using scripts][scripts]: reuse existing commands and bundle repeated work.

[specification]: https://agentskills.io/specification
[practices]: https://agentskills.io/skill-creation/best-practices
[descriptions]: https://agentskills.io/skill-creation/optimizing-descriptions
[evaluation]: https://agentskills.io/skill-creation/evaluating-skills
[scripts]: https://agentskills.io/skill-creation/using-scripts
