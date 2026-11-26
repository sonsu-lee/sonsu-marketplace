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

## Route the request

Before starting a routed workflow, load its installed skill rather than relying
on this routing summary. Use the host's skill interface: in Claude Code invoke
the Skill tool with the qualified name, such as `development:executing-work`;
in Codex use `$<plugin>:<skill>` when available; in omp read `skill://<skill>`.
If nested invocation is unavailable, read the installed `SKILL.md` and report
reading, not invocation. Report an unavailable required skill.

- Implementation: `executing-work`; use `planning-work` first for a requested
  plan or material unresolved design choices. A plan-only request ends with
  the plan; an approved implementation does not need repeated approval.
- Bug investigation: `debugging-code`; implement a fix only if authorized.
  Do not reproduce a reported failure where the user or host forbids it.
- Architecture improvement: `improving-codebase-architecture`; distinguish it
  from a routine diff review and preserve discussion-only authority.
- Skill creation, revision, or assigned skill-criteria review: `authoring-skills`.
  For authorized skill changes, also use `executing-work` for implementation
  and independent review. A change, diff, or PR review uses `reviewing-code`
  even when it changes a skill; include skill criteria as that procedure requires.
- Interview: `grill-me`, or `grill-with-docs` when repository domain documents
  are needed. Domain terminology: `domain-modeling`.
- Product requirements, decisions, or tickets: `writing-prd`, `writing-adrs`,
  or `writing-tickets` respectively. Do not create or publish them merely
  because a related workflow ran.
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

Use `development` and `review` together for integrated code work, adding
`prd`, `decisions`, `tickets`, `grill`, `design`, `writing`, or `git` as
needed. Each package is independently installable. If a package is absent, do
not claim to invoke it; continue only independent authorized work. If required
independent review is unavailable, report the work incomplete.

## Implement the smallest complete change

Inspect existing code, callers, contracts, and consequences first. Reuse the
project's implementation and conventions, then suitable platform or installed
facilities. Avoid unrequested options, abstractions, dependencies, and future
features. Complete all affected callers and preserve security, validation,
error handling, accessibility, and requested behavior. Exercise the actual
changed path and arrange the required independent review; do not substitute a
skill invocation or an evaluation score for execution.

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
