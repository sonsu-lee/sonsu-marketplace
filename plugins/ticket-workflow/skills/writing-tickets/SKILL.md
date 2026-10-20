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
solution. Write directly; no user-story formula is required.

## Establish the request and context

Distinguish drafting from publishing. A request to propose, organize, or draft
does not authorize creating issues, changing metadata, or configuring
integrations. Create or update tickets only when requested; splitting a draft
does not permit publishing children.

Identify the repository or Linear team and primary tracker from the request and
project guidance. Support either platform; never copy a ticket into both.
Respect established sync; do not set it up.

Read the relevant ticket, discussion, evidence, and guidance. Before creating a
ticket, search the target tracker for the same problem; reuse or link an
existing issue instead of duplicating it or rewriting someone else's ticket.

Separate observations, suspected causes, and proposed solutions. Preserve useful
feedback verbatim and link its source when available. Never invent impact,
reproduction steps, thresholds, prior decisions, or issue IDs. Ask only when
context cannot resolve a material gap in problem, scope, destination, or completion.

## Choose the format

For the selected platform, read only its applicable procedure:

- [GitHub Issues](references/github-issue.md): templates, issue forms,
  metadata, and relationships.
- [Linear](references/linear.md): templates, metadata, PR status automation.

Within the project's mandatory rules, use an explicitly requested applicable
template first, then the applicable repository, team, or issue-type template;
otherwise the [default body](assets/ticket-body.md). If template lookup is
unavailable, distinguish that from finding none: disclose the limitation in a
draft and resolve required fields before publishing.

Preserve required fields and automation markers. Apply these principles inside
the selected format, not a second template (for example, put outcomes in an
existing Acceptance Criteria field). Do not assume a CLI or API applies a UI
template to an explicit body.

## Describe the problem and desired outcome

Use a short, specific title conveying the problem or purpose on a board.
Keep the body only as long as the work requires:

- **Problem:** what happens now, relevant conditions, and why it matters. A
  feature request describes an unmet need or limitation, not an invented bug.
  Include reproduction details when they help locate a failure.
- **Desired outcome:** the observable state that resolves the problem, making
  completion judgeable without prescribing implementation. One sentence may
  suffice; use a short list for distinct outcomes, not a default extra checklist.
- **Context:** relevant history, decisions, evidence, dependencies, and links,
  summarized to stand alone. Omit when empty unless required.

Add detail when omission would permit solving the wrong problem or declaring
completion wrongly, not to list edge cases. Preserve established security,
compatibility, and external-contract constraints; distinguish them from
unverified implementation preferences.

Describe restored capability, not a vanished symptom: prefer "Repeated save
attempts produce one record" over "Debounce the save button" or "Hide the
duplicate-record error." Leave storage, timing, and code structure to the
assignee unless a requirement constrains them; mark proposed
approaches tentative or omit them. Do not turn routine implementation steps,
test counts, or generic CI checks into outcomes; the PR records those.

## Review and propose metadata

Review metadata alongside the body: inspect fields, allowed values, template
defaults, and repository or team conventions. Use explicit user choices and
established rules first; propose grounded candidates for missing values, kept
distinct from established ones. For label, type, assignee,
priority, estimate, project, and milestone criteria and presentation, read
[Metadata](references/metadata.md).

When publication is authorized, apply established values and project-supported
choices; never silently promote proposals into assignments or commitments, or
create labels, fields, milestones, or projects merely to fill the ticket. If
tooling cannot read or write a field, disclose that instead of treating it as
absent or claiming it was applied.

## Keep a meaningful small scope

Aim for one problem and one coherent outcome; split work whose parts can be
prioritized, deferred, or completed independently. Never split code, necessary
tests, and required documentation just to reduce size; file counts and time
limits are not the criterion.

For a larger request, give each child an independently judgeable outcome and
name real dependencies. Use a parent only to retain the shared goal; never
copy the full specification into children. Read relationships before changing
them. For genuine uncertainty, name the question and needed decision or
deliverable; do not promise the eventual feature or stop at "investigate".

## Connect tickets to work and pull requests

The normal flow is ticket, work, PR. Establish the issue ID before naming the
work branch. Drafting a ticket does not authorize implementation, branch
creation, or publishing a PR; for those use `naming-branches` and
`writing-pull-requests` from `git-workflow`, repository rules first, without
duplicating their procedures. For work spanning tickets, use the primary ticket
for the branch ID and explain every relationship in the PR.

A ticket may need several PRs; a PR may address several tickets. Reference
partial work without closing the ticket; use completion links only when the
desired outcome is fulfilled, given the tracker's actual automation. A merge
does not prove completion when deployment or other verification remains.

The assignee may change the approach while preserving the outcome. If the
problem, scope, or outcome changes, state it in the ticket with the important
reason; never silently redefine success. Keep implementation details and
evidence in the PR, not a work log.

## Deliver the requested result

For a draft, return title, body, metadata recommendations, splits or relations,
and material unresolved questions. Do not invent an ID or imply publication.

For an authorized create or update, apply the selected template and established
metadata with the tracker tools, preserving unrelated content and properties.
Inspect the returned issue and separately stored project fields, or read them
back, to confirm destination, content, metadata, and relationships.
Report the real ID, URL, and incomplete actions; never call a draft published.

Source: [Linear's Write issues not user stories](https://linear.app/method/write-issues-not-user-stories);
the fallback body and outcome guidance are this plugin's defaults.
