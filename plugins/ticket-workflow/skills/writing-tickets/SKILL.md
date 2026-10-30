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

Agree on the problem and observable outcome, not an implementation recipe.
Use plain language and established technical terms; give the assignee context
to choose a solution, not your investigation diary.
For prose drafts/edits, also read the matching language skill if listed;
retain these ticket rules.

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
otherwise use the [body guidance](assets/ticket-body.md). Distinguish an
unavailable template lookup from finding none: disclose it in a draft and resolve
required fields before publishing.

Preserve required fields and automation markers. Apply these principles inside
the selected format, not a second template (for example, put outcomes in an
existing Acceptance Criteria field). Do not assume a CLI or API applies a UI
template to an explicit body.

## Describe the problem and desired outcome

Use a short title naming the problem or purpose. Select relevant facts before
writing or polishing; source notes are not the body to reproduce.
If the title communicates the request, omit the body unless the format requires
one. Otherwise add only information not already clear from the title.
These are optional content, not required sections:

- **Problem:** current behavior or need, relevant conditions, and why it
  matters. Do not frame a feature request as a bug.
- **Desired outcome:** the observable result that makes completion judgeable,
  not an implementation recipe. One sentence may suffice; list only distinct
  outcomes, not a default checklist.
- **Context:** necessary decisions, constraints, evidence, and dependencies.
  Summarize enough to stand alone, link the details, and omit when unnecessary.

Keep only detail that could change the task or completion judgment. Preserve
security, compatibility, external contracts, and material unknowns; omit
generic cautions, exhaustive exclusions, and routine test/command lists.
Describe restored capability: "Repeated saves produce one record", not
"Debounce the button". Leave storage, timing, and code structure to the assignee
unless required; label proposed approaches tentative or omit them.

For maintenance, describe the current cost or risk; an agreed or externally
required change may itself be the outcome. Do not file trivial debt that
belongs in the current change, or title a ticket `Follow-up`.

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

Keep the body on the current agreed problem, scope, and outcome. When these
change, record the reason without accumulating superseded plans or progress
logs; link existing discussion or design records. Never redefine success
silently. Keep detailed implementation and verification evidence with the PR.

## Deliver the requested result

For a draft, return the title and any needed body, relevant metadata proposals,
relations, and material questions. Omit empty categories; do not invent an ID
or imply publication.

For an authorized create or update, apply the selected template and established
metadata with the tracker tools, preserving unrelated content and properties.
Read back the issue and separately stored project fields to confirm
destination, content, metadata, and relationships.
Report the real ID, URL, and incomplete actions; never call a draft published.

Sources: [body guidance](assets/ticket-body.md#sources).
