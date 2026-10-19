---
name: writing-tickets
description: >-
  Use this skill when drafting, creating, or updating GitHub Issues or Linear
  tickets, turning a problem or request into actionable issues, or splitting
  an oversized ticket. Not for implementing the work or writing pull requests.
compatibility: >-
  Publishing or reading private tracker context requires authenticated tooling
  for the selected GitHub repository or Linear workspace.
---

# Writing tickets

A ticket is an agreement about a problem and the desired outcome, not an
implementation prescription. Give the assignee enough context to choose a
solution. Write directly, without a mandatory user-story formula.

## Establish the request and context

Distinguish drafting from publishing. A request to propose, organize, or draft
content does not authorize creating issues, changing metadata, or configuring
integrations. Create or update tickets only when requested; splitting a draft
is not permission to publish its children.

Identify the repository or Linear team and the project's primary tracker from
the request and available project guidance. Support either platform without
creating a copy in both. Respect established sync relationships; do not set up
sync as part of ticket writing.

Read the relevant existing ticket, discussion, evidence, and project guidance.
Before creating a ticket, search the target tracker for the same problem. Reuse
or link an existing issue where appropriate rather than duplicating it. Do not
rewrite someone else's ticket just because a duplicate was found.

Separate observations, suspected causes, and proposed solutions. Preserve useful
user feedback in its original wording and link its source when available. Do
not invent impact, reproduction steps, performance thresholds, prior decisions,
or issue IDs. Ask only when missing information materially changes the problem,
scope, destination, or meaning of completion and cannot be found in context.

## Choose the format

For the selected platform, read only its applicable procedure:

- [GitHub Issues](references/github-issue.md): repository and inherited templates,
  issue forms, metadata, and GitHub issue relationships.
- [Linear](references/linear.md): team and workspace templates, metadata,
  and PR status automation.

Within the project's mandatory rules, use an explicitly requested applicable
template first, then the applicable repository, team, or issue-type template.
If none applies, use the [default body](assets/ticket-body.md). If template
lookup is unavailable, distinguish that from finding no template; disclose the
limitation in a draft and resolve required fields before publishing.

Preserve required fields and automation markers. Express the principles below
inside the selected format instead of appending a second template. For example,
put the desired outcome in an existing Acceptance Criteria field. Do not assume
that a CLI or API will apply a UI template to an explicit body automatically.

## Describe the problem and desired outcome

Use a short, specific title that communicates the problem or purpose on a board.
Keep the body only as long as needed to perform and understand the work:

- **Problem:** what happens now, the relevant conditions, and why it matters.
  A feature request describes an unmet need or current limitation; it does not
  need an invented bug. Include reproduction details when they help locate a
  reported failure.
- **Desired outcome:** the observable state that would resolve the problem.
  Make completion judgeable without prescribing implementation steps. One
  sentence is enough when it captures the result; use a short list for distinct
  important outcomes. Do not add a separate acceptance checklist by default.
- **Context:** relevant history, decisions, evidence, dependencies, and links.
  Summarize essential context so the ticket remains useful without opening every
  link. Omit this section when empty unless the selected template requires it.

Add detail when omitting it would permit solving the wrong problem or declaring
completion incorrectly, not to enumerate every possible edge case. Preserve
established security, compatibility, and external-contract constraints. A known
constraint is different from an unverified preference about implementation.

Describe restored capability, not merely disappearance of a symptom. For
example, prefer "Repeated save attempts produce one record" over "Debounce the
save button" or "Hide the duplicate-record error." Leave storage, timing, and
code structure to the assignee unless an established requirement constrains
them. Keep proposed approaches explicitly tentative and omit them if unhelpful.

Do not turn routine implementation steps, a test count, or generic CI checks
into ticket outcomes. The worker chooses the implementation and verification
approach; the PR records the actual change and observed evidence.

## Review and propose metadata

Review metadata alongside the body for both trackers. Inspect available fields,
allowed values, template defaults, and repository or team conventions before
choosing values. Use explicit user choices and established rules first; propose
grounded candidates for missing metadata rather than merely leaving everything
blank. Keep proposals distinct from established values.

- **Labels and type:** choose existing classifications matching the problem and
  affected area, without creating near-duplicate labels or adding every match.
- **Assignee:** use an explicit assignment or established ownership rule. A
  plausible owner is a proposal, not proof of assignment; do not assume the
  reporter or current user should do the work.
- **Priority:** use known impact, severity, and time constraints with the team's
  scale. A bug is not automatically high priority.
- **Estimate:** check the team's scale and available scope information. Propose
  an estimate only with a defensible basis; leave it unset when investigation or
  assignee judgment is needed. Unknown is not zero, and points are not hours
  unless the team defines them that way.
- **Project and milestone:** use existing destinations whose goals match the
  outcome, respecting their scope. A similar name alone is not enough.

Present relevant metadata separately from the draft body, with brief reasons
for proposals and material unresolved choices. Do not duplicate tracker fields
in the body unless the selected template requires it. Leave optional unknowns
unset; ask only about required or consequential choices that context cannot
resolve, batching them instead of asking about every field.

When publication is authorized, apply established values and choices supported
by project rules; do not silently promote unresolved proposals into assignments
or commitments. Do not create labels, fields, milestones, or projects merely to
fill the ticket. If tooling cannot read or write a relevant field, disclose that
limitation instead of treating the field as absent or claiming it was applied.

## Keep a meaningful small scope

Aim for one problem and one coherent outcome. Split work when parts can be
prioritized, deferred, or completed independently. Do not split code, its
necessary tests, and required documentation into separate tickets merely to
reduce size. File counts and fixed time limits are not the scope criterion.

For a larger request, give each child an independently judgeable outcome and
name real dependencies. Use a parent only when it helps retain the shared goal;
do not copy the full specification into every child. Read existing relationships
before creating or changing them.

When the solution is genuinely uncertain, a research ticket can name the
question to answer and the decision or deliverable needed afterward. Do not
promise the eventual feature as that research ticket's outcome or leave it at
"investigate" without a useful result.

## Connect tickets to work and pull requests

Use ticket, then work, then PR as the normal development flow. Establish the
issue ID before naming the work branch. Drafting a ticket does not authorize
starting implementation, creating a branch, or publishing a PR.

For branch naming and PR preparation, use `naming-branches` and
`writing-pull-requests` from `git-workflow`, following repository rules first.
Do not duplicate their naming or validation procedures here. Those skills are
needed only when performing those downstream tasks, not to draft a ticket.
For work spanning multiple tickets, use the primary work ticket for the branch
ID and explain all relevant relationships in the PR rather than packing every
ID into the branch name.

A ticket may need several PRs, and a coherent PR may address several tickets.
Reference partial work without closing the whole ticket. Use completion links
only when the ticket's desired outcome is fulfilled, accounting for the target
tracker's actual automation. A merge is not proof of completion when deployment
or other outcome verification remains necessary.

The assignee may change the approach while preserving the agreed outcome. If
the problem, scope, or desired outcome changes, make that change explicit in the
ticket and retain the important reason; do not silently redefine success.
Keep implementation details and verification evidence in the PR rather than
turning the ticket into a chronological work log.

## Deliver the requested result

For a draft, return the proposed title and body, metadata recommendations, any
proposed split or relations, and material unresolved questions. Do not claim a
ticket ID or link exists.

For an authorized create or update, apply the selected template and established
metadata using the tracker tools. Preserve unrelated existing content and
properties. Inspect the returned issue and any separately stored project fields,
or read them back when needed, to confirm the destination, content, metadata,
and intended relationships. Report its real ID and
URL and any actions that did not complete; do not describe a draft as published.

## Sources

[Linear's Write issues not user stories][linear-method] motivates concise,
direct issues and leaving solutions to assignees. The fallback body and
outcome-centered completion guidance here are this plugin's defaults, not
mandatory sections prescribed by Linear.

[linear-method]: https://linear.app/method/write-issues-not-user-stories
