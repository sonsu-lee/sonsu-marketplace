---
name: writing-tickets
description: >-
  Use this skill before drafting, opening, filing, or updating any GitHub issue
  or Linear ticket, including bug reports, feature requests, and suspected
  security vulnerabilities, or when turning a problem into actionable issues,
  splitting an oversized ticket, or capturing unrelated work found during
  another task. Not for implementing the work or writing pull requests.
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
does not permit publishing children. When the current task permits reporting
unrelated work, offer a ticket draft instead of expanding its scope; publish
only when asked. Do not bypass a focused review's exclusion of unrelated debt.

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

Treat a suspected security vulnerability as a disclosure: follow the project's
security policy or private reporting channel, and never put exploit details or
reproduction in a public or publicly synced ticket. Without a private path,
return the draft in your reply, not a repository file, and say so.

## Choose the format

Read only the references that apply:

- [Bug](references/bug.md): behavior differs from what the product,
  documentation, or a contract promises, including regressions.
- [Parent](references/parent.md): independently completable parts share a
  goal, or a parent, epic, or project is created or split.
- [GitHub Issues](references/github-issue.md) or [Linear](references/linear.md):
  the selected platform's templates, metadata, relationships, and publishing.

Feature requests, maintenance, and investigations need no kind reference.

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

For maintenance, the problem is the current state's cost or risk; an agreed or
externally required change may itself be the outcome. Do not file trivial debt
that belongs in the current change, or title a ticket `Follow-up`.

## Review and propose metadata

Review metadata alongside the body: inspect fields, allowed values, template
defaults, and repository or team conventions. Use explicit user choices and
established rules first; propose grounded candidates for missing values, kept
distinct from established ones. For per-field criteria and presentation, read
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

Read existing relationships before changing them. For genuine uncertainty, name
the question and needed decision or deliverable; do not promise the eventual
feature or stop at "investigate".

## Connect tickets to work and pull requests

The normal flow is ticket, work, PR; establish the issue ID before naming the
work branch. Drafting does not authorize implementation, branches, or PRs; for
those use `naming-branches` and `writing-pull-requests` from `git-workflow`,
repository rules first. For work spanning tickets, use the primary ticket for
the branch ID and explain every relationship in the PR.

Tickets and PRs need not be one-to-one. Reference partial work without closing
the ticket; use completion links only when the outcome is fulfilled under the
tracker's actual automation, not while deployment or verification remains.

The assignee may change the approach while preserving the outcome. State
changes to the problem, scope, or outcome in the ticket with the reason; never
silently redefine success. Keep implementation details and evidence in the PR.

## Deliver the requested result

For a draft, return title, body, metadata recommendations, splits or relations,
and material unresolved questions. Do not invent an ID or imply publication.

For an authorized create or update, apply the selected template and established
metadata with the tracker tools, preserving unrelated content and properties.
Read back the issue and separately stored project fields to confirm
destination, content, metadata, and relationships.
Report the real ID, URL, and incomplete actions; never call a draft published.

Source: [Linear's Write issues not user stories](https://linear.app/method/write-issues-not-user-stories);
the fallback body and outcome guidance are this plugin's defaults.
