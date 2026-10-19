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

Use real requests, successful work, user corrections, and project artifacts
such as configurations or review discussions. Establish the intended outcome,
when the skill should apply, and nearby tasks it should not handle. Ask only
about material gaps that available context cannot resolve.

For each proposed instruction, ask: would its absence cause a meaningful
mistake on this task? Keep necessary domain knowledge, project conventions,
decision criteria, and non-obvious constraints. Omit general knowledge and
information that ordinary tool discovery can supply when needed. If value is
uncertain, test the omission rather than assume more detail is safer.

Scope around a reusable unit of work, not one example or an entire profession.
Split skills when users need independently useful workflows, not merely
because source documents have separate chapters. Do not invent expertise or
requirements to fill an outline.

## Identify the target environment

Start from the common Agent Skills format and writing principles; no client
is the default. Establish the intended consumer from the user's request and
the target project's instructions, manifests, installation layout, or runtime
documentation. For example, an omp marketplace catalog together with documented
omp installation identifies an omp target. A portable `plugin.json` or shared
skills directory alone does not identify a client.

The client running this authoring session is not necessarily the consumer of
the skill being written. An explicit target takes precedence over that context.
When a target is established, read only its reference and apply the relevant
differences to the artifact being authored:

| Intended consumer | Conditional reference |
| --- | --- |
| omp | [omp authoring considerations](references/omp.md) |
| Claude Code, claude.ai, or Claude API | [Claude authoring considerations](references/claude.md) |
| Codex | [Codex authoring considerations](references/codex.md) |

If no target is established, keep the artifact portable and do not load every
client reference or add client-specific metadata. Ask only if an unresolved
client choice affects a required capability. For explicitly shared skills,
consult the named targets and keep shared content standard; do not combine
incompatible extensions or claim compatibility without target-specific checks.

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

Keep installation, marketplace registration, and contributor evaluation
procedures in their owning project documentation unless they are the task
this skill is specifically meant to teach. Create supporting files only when
needed, not a standard set of empty directories.

## Write actionable guidance

Use the [Agent Skills specification][specification] for metadata and layout.
Keep the body focused; the guidance of fewer than 500 lines and 5,000 tokens is
not a size target. State specific runtime requirements in `compatibility`
only when they apply.

Write `description` around user intent: what the skill does, when to use it,
including implicit requests it should cover, and meaningful boundaries with
adjacent work. Keep it concise and front-load the key use case rather than
internal implementation steps. Avoid keyword accumulation to match individual
failed prompts; client-specific wording preferences are not format rules.

Give a short sequence from inputs through decisions to an observable result.
Pick a default instead of offering an unranked menu. Explain why when it helps
judgment; prescribe exact steps when variation would risk correctness or
safety. Do not turn a flexible writing task into an inflexible checklist.

Use a compact example or template when it resolves ambiguity, not to repeat
the surrounding prose. Keep consequential, non-obvious gotchas visible before
the agent can make the mistake; a conditional reference is useful only if the
agent can recognize the condition.

## Delegate execution without losing the contract

Reuse the target repository's tool, version, and configuration first. If no
execution setup exists, use an appropriate existing CLI with a pinned version;
missing configuration is a separate question from a missing runner. An existing
tool's failure is not permission to bypass it with a different validator.
Do not install hooks or alter project configuration merely to use a skill.

Specify when to invoke the tool, the intended input, what result establishes
success, and what remains for judgment. For example, a commit-message validator
must inspect the proposed message; passing syntax checks does not establish
that it accurately explains the change. Keep ordinary flags and exhaustive
platform exceptions in the tool's documentation, not the skill.

For bundled scripts, read [Using scripts][scripts] when designing their
interface. Provide non-interactive inputs, helpful errors, meaningful exit
status, and bounded output; use structured results where consumers need them.
For state-changing operations, distinguish authorization from validation and
make consequential side effects explicit. Instructions to run a check are not
an enforcement mechanism such as a hook, CI check, or permission boundary.

## Verify and refine

When selecting checks for a new or changed skill, or investigating unreliable
activation or output, read [Choosing evaluation](references/evaluation.md).
Use the project's existing validation procedure and official format validator
where applicable; do not build a second parser for rules already checked.

Review outcomes and execution traces. Check for unnecessary reference loading,
repeated helpers, irrelevant checks, and expansion beyond the requested task.
Evaluate a review observation, the skill's responsibility, and the proposed
solution separately: a missing tool example is not itself a defect. Fix actual
incorrect instructions or consequential ambiguity with the smallest sufficient
change, including deletion. Generalize recurring failures instead of appending
a new rule for every incident.

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
