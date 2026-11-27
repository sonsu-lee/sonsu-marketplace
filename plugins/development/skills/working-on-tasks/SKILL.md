---
name: working-on-tasks
description: >-
  Route a general work request to the relevant development, product, design,
  writing, review, or Git workflow. Use when starting or reclassifying work;
  explicit skill and native-only requests take precedence.
---

# Working on tasks

Identify the requested outcome, relevant context, authorized actions, and how
success can be observed. Host, security, repository, and user instructions
have precedence. Reclassify the work when new evidence changes its needs.
Skill selection is model-dependent, not an authorization or a security gate.
Each workflow may also be invoked directly.

## The Rule

**Invoke relevant or requested skills BEFORE any response or action**,
including clarifying questions, exploring the codebase, or checking files.
Process skills come first: they set the approach. Load each applicable
skill before reading the code, ticket, PRD, or draft it governs. If none
applies, answer directly. Otherwise announce "Using [skill] to [purpose]"
after loading it. Knowing the concept is not a substitute for reading the skill.

## Platform adaptation

In Claude Code invoke the Skill tool with the qualified name, such as
`development:executing-work`; in Codex use `$<plugin>:<skill>` when available;
in omp read `skill://<skill>` before acting. Use native delegation, not a
second CLI, for workers. A worker uses its assigned workflow, not this router.
If nested invocation is unavailable, read only the installed skill path
reported by this client. Report reading rather than invocation. Do not
search other client homes for a missing skill or offer to bypass approval.

## Skill priority

When multiple skills apply, process skills come first: they set the approach;
implementation skills carry it out. "Let's build X" starts with brainstorming
if it needs a design. "Fix this bug" starts with debugging.

- New development designs: use `brainstorming` first. When a PRD is needed,
  use `prd:writing-prd` to capture agreed requirements before planning. Load
  `writing-plans` for the agreed spec and design; start there if they already
  exist. A standalone design, PRD, or plan ends at the requested deliverable.
- Implementation: use `executing-work` for authorized work when no material
  design or planning decisions remain. Do not seek approval of an accepted plan.
- Bug investigation: `debugging-code`; implement a fix only if authorized.
  Do not reproduce a reported failure where the user or host forbids it.
- Architecture improvement: `improving-codebase-architecture`; distinguish it
  from a routine diff review and preserve discussion-only authority.
- Skill creation, revision, or assigned skill-criteria review: `authoring-skills`.
  For authorized skill changes, also use `executing-work` for implementation
  and independent review. A change, diff, or PR review uses `reviewing-code`
  even when it changes a skill; include skill criteria as that procedure requires.
- For refining documents or ideas, load the applicable `grill` skill before
  reading the draft: `grill-me` for an interview, `grilling` for decision
  dependencies, `grill-with-docs` for project terminology and constraints.
  Use the language skill for copy editing. Do not reopen settled PRD decisions.
- Product requirements, decisions, or tickets: `prd:writing-prd`,
  `decisions:writing-adrs`, or `tickets:writing-tickets`. Drafting a document
  does not authorize publishing it.
- Code review or explicitly requested audit: `reviewing-code`. Respect a
  native-only request and keep a review read-only unless edits are authorized.
- Interface work, design review, or graphics: `designing-interfaces`,
  `reviewing-designs`, or `designing-graphics`. A proposal or review does not
  authorize implementation.
- Prose or Git: the relevant language or Git skill. General documentation:
  the project's documentation procedure.

Compose workflows in task order for mixed requests without widening authority.
A chat draft is read-only; permission to write a named draft applies only to
that file. Loading a skill grants no permission to edit a glossary, migrate,
commit, push, publish, modify a tracker, or deploy. Obtain applicable separate
approval for those actions. Follow stricter project rules.

For code changes and investigations, load `ponytail:ponytail` and the process
skill before reading code. If Ponytail is missing, stop before code exploration,
even for read-only diagnosis. Standalone review does not require Ponytail.
For integrated change review, use `ponytail-review`
as criteria inside `review:reviewing-code`, not as a second review. Use
`ponytail-audit` only for a requested repository audit. For a feature,
behavior fix or new or changed test, load `tdd:test-driven-development`
before inspecting the target. Block dependent implementation if it is missing.
Obtain explicit approval of the observable test specification before
writing tests; approval in the plan suffices unless the contract changes.
Once the tests are approved and implementation is authorized, route the
implementation turn to `development:executing-work` before the first edit. If already
loaded, continue its workflow. TDD governs the test cycle; GREEN hands the
change to independent review, not directly to a completion report.

Each package is independently installable. If an integrated stage requires
a missing package, identify it and stop that stage; continue only independent
authorized work. Never claim that a missing skill or reviewer ran.

## Quality gates

A stage's result becomes the next stage's input only through its gate. Read
the `working-on-tasks` skill's
[quality gates](references/quality-gates.md) at a handoff or when a gate
fails. A failed gate returns the work to the stage that owns the defect;
files are never reset to roll back. `unverified` is not a pass.

## Evaluate each performed stage

The stage owner records evidence and evaluates only stages actually performed.
Each applicable item scores 0 (absent or failed), 1 (partial), or 2 (supported
by evidence). Exclude inapplicable items with reasons and normalize the rest to
10. A stage needs at least 8/10, but cannot pass if any mandatory condition is
failed or unverified: user requirements and authorization, security and data
safety, confirmed contracts, and evidence appropriate to the stage. An
unavailable execution is blocked or unverified, not a success score.

- **Plan or interview:** purpose and scope; evidence; substantive alternatives;
  decided versus open; verifiability.
- **PRD or ticket:** user problem; requirements accuracy; scope; open questions
  and evidence; acceptance.
- **ADR:** context; decision and reasons; actual alternatives or constraints;
  consequences; document boundary.
- **Implementation:** contract and happy path; reachable boundaries; test
  design and expected values; execution evidence; unnecessary code removal.
- **Review:** target and scope; reachable paths; impact; evidence and
  deduplication; unverified areas.
- **Design:** goals and states; hierarchy and interaction; accessibility;
  actual screen evidence; constraints and limits.
- **Writing or delivery:** audience and purpose; factual fidelity; clarity;
  scope and authority; verification results.

After the initial evaluation, correct failures using real evidence and
reevaluate at most three times. Do not repeat an unchanged evaluation or weaken
expected results to match an implementation. Stop and report each score,
mandatory conditions, evidence, and remaining blockers if the stage still fails.
Wait rather than automatically retry when a user decision, permission, or
external access is required. Independent review is required where applicable;
a model's score does not prove a test, browser run, or authorization.
