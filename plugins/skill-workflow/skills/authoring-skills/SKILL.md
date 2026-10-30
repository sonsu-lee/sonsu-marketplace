---
name: authoring-skills
description: >-
  Use this skill when creating, revising, or reviewing an agent skill,
  including defining its scope, deciding what belongs in SKILL.md,
  delegating work to tools, or reducing unnecessary instructions.
  Not for installing skills or editing ordinary documentation.
---

# Authoring skills

Teach the judgment and minimum procedure needed for one coherent task.
Delegate mechanical execution and checks to existing tools; a skill is not
an exhaustive tool manual. Follow the target project's authoring requirements.

## Establish the task and added value

Ground the skill in real requests, successful work, corrections, and project
artifacts. Establish the outcome, when it applies, and nearby tasks it excludes.
Ask only about consequential gaps that available context cannot resolve.

Return text-only proposals as text; do not create even temporary files when
writes are prohibited. Authoring checks grant no permission to write, install,
or publish, and reviewing a proposal is not validating a saved artifact.

Would omitting an instruction cause a meaningful mistake? Keep domain knowledge,
project conventions, decision criteria, and non-obvious constraints. Omit general
knowledge and ordinary tool usage. Test uncertain omissions rather than assuming
more detail is safer.

Scope one reusable unit of work. Split skills for independently useful workflows,
not source-document chapters; do not invent expertise to fill an outline.

## Identify the target environment

Identify intended consumers from the request and project evidence, not the
authoring client or a portable manifest alone. An explicit target wins. Read
only the applicable client references:

| Intended consumer | Conditional reference |
| --- | --- |
| omp | [omp authoring considerations](references/omp.md) |
| Claude Code, claude.ai, or Claude API | [Claude authoring considerations](references/claude.md) |
| Codex | [Codex authoring considerations](references/codex.md) |

Without an established target, stay portable; do not load every client reference
or add client metadata. Ask only if the choice affects a required capability.
For shared skills, consult each named target, keep shared content standard, and
verify each client rather than combining incompatible extensions.

## Put each responsibility in the right place

- **SKILL.md:** purpose, decision criteria, defaults, the minimum workflow, and
  consequential constraints needed on ordinary runs.
- **references/:** task-specific detail needed only under stated conditions.
  Say when to read each file; moving text out of the body but always loading
  it does not reduce context cost.
- **Configuration and assets:** executable rule values and reusable output
  structures. A brief rule may guide generation, but do not duplicate a
  validator's implementation in prose.
- **Existing tools:** mechanical execution and deterministic checks. Prefer a
  direct invocation over a new wrapper.
- **scripts/:** repeated logic that existing tools and simple invocations do
  not adequately cover. Bundle it when actual runs show repeated reinvention
  or consequential command-construction errors, not just to add a directory.

Keep installation, marketplace registration, and contributor evaluation in
project documentation unless those are the skill's task. Create supporting
files only when needed, not a standard set of empty directories.

## Write actionable guidance

Use the [Agent Skills specification][specification] for metadata and layout.
Its size guidance is not a target or a loading guarantee; check client limits
in the applicable reference. Set `compatibility` only for real requirements.

Describe user intent, implicit uses, and boundaries with adjacent work. Front-load
the key use case, not implementation steps or keywords for individual failed
prompts. Client wording preferences are not common format rules.

Use clear headings and direct language to make conditions, constraints, and
decision criteria easy to distinguish. Optimize for sufficient guidance, not
minimum length; preserve information needed for correct judgment.

Give a short path from input to observable result. Choose a default; explain why
when useful and prescribe exact steps where variation risks correctness or
safety. Do not turn flexible judgment into an inflexible checklist.

Separate defaults from binding host, security, project, and user constraints,
and say when a default yields. When a skill stops or redirects authorized work,
cite the instruction; do not invent approvals or weaken permission boundaries.

Use examples only to resolve ambiguity. Keep consequential gotchas visible before
the agent can make the mistake; conditional references need recognizable triggers.

## Delegate execution without losing the contract

Reuse the target repository's tool, version, and configuration first. If no
execution setup exists, use an appropriate existing CLI with a pinned version;
missing configuration is a separate question from a missing runner. An existing
tool's failure is not permission to bypass it with a different validator.
Do not install hooks or alter project configuration merely to use a skill.

Specify the tool's trigger, exact input, success evidence, and remaining judgment.
Mechanical acceptance does not establish semantic correctness. Leave ordinary
flags and exhaustive platform exceptions in tool documentation.

For bundled scripts, read [Using scripts][scripts]. Provide non-interactive inputs,
helpful errors, meaningful exit status, and bounded or structured output.
Distinguish authorization from validation and disclose side effects; instructions
are not hooks, CI enforcement, or permission boundaries.

## Verify and refine

Read [Choosing evaluation](references/evaluation.md) when selecting checks or
investigating activation and output. Verify format, discovery, complete main
prompt loading, and task behavior separately using project procedures. Reuse
the official format validator; do not build another parser for its rules.

Inspect outcomes and traces for unnecessary references, repeated helpers,
irrelevant checks, and scope expansion. Evaluate an observation, the skill's
responsibility, and the proposed solution separately. Missing tool examples
alone are not defects. Correct actual errors or consequential ambiguity with
the smallest sufficient change, including deletion; generalize recurring failures.

For new skills or behavioral changes, obtain independent skill-criteria review
before delivery. Give a fresh reviewer the purpose, consumers, changed files,
project requirements, and review question, not the drafting rationale.
Skip formatting-only changes or when you are that reviewer. One execution or
review controller owns dispatch; do not duplicate its skill review. In omp use
`skill-workflow-reviewer`; in Codex or Claude Code use a fresh generic worker
with this `SKILL.md`'s absolute path. Follow `reviewing-code` when it controls
the review. Disclose unavailable review and verify findings before revising.
Review does not replace behavior checks.

Deliver the requested skill or revision with the checks actually performed
and any material limitations. Keep authoring evaluations separate from the
procedures that users of the resulting skill must perform on every task.

## Sources

- [Best practices][practices]: scope, context economy, and calibrated guidance.
- [Optimizing descriptions][descriptions]: intent and activation boundaries.
- [Evaluating skills][evaluation]: baseline comparisons and trace-driven revision.
- [Using scripts][scripts]: reuse existing commands and bundle repeated work.

[specification]: https://agentskills.io/specification
[practices]: https://agentskills.io/skill-creation/best-practices
[descriptions]: https://agentskills.io/skill-creation/optimizing-descriptions
[evaluation]: https://agentskills.io/skill-creation/evaluating-skills
[scripts]: https://agentskills.io/skill-creation/using-scripts
