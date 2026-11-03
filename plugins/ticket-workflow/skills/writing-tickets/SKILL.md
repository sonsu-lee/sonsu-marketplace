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

Agree on the problem and observable outcome, leaving the solution to the
assignee. Use plain language and established technical terms; for prose
creation or editing, also read the matching language skill if listed.

## Workflow

1. **Establish the request.** Create or update tickets only when asked.
   Drafting, proposing, organizing, or splitting a draft authorizes neither
   publication (including children), metadata changes, integration setup,
   implementation, branches, nor PRs. When allowed to report unrelated work,
   offer a draft, not expanded scope; publish only on request. Respect
   focused-review exclusions.
2. **Find context.** Identify the repository or Linear team and primary tracker
   from the request and project guidance. Do not copy tickets to both platforms
   or set up sync; respect existing sync. Read relevant tickets, discussion,
   evidence, and guidance. Before creation, search for the problem; reuse or
   link an existing issue instead of duplicating or rewriting someone else's.
3. **Choose the format.** Read applicable references:
   - [Bug](references/bug.md): behavior differs from product, documentation,
     or contract promises, including regressions.
   - [Parent](references/parent.md): independently completable parts share a
     goal, or a parent, epic, or project is created or split.
   - [GitHub Issues](references/github-issue.md) or [Linear](references/linear.md):
     the selected platform's templates, metadata, relationships, and publishing.

   Feature requests, maintenance, and investigations need no kind reference.
   Under project rules, prefer an explicitly requested applicable template,
   then the applicable repository, team, or issue-type template; otherwise use
   [body guidance](assets/ticket-body.md). Keep required fields and automation
   markers; apply these principles within the format, not a second template.
   Disclose unavailable template lookup in a draft, distinguish it from finding
   none, and resolve required fields before publishing.
4. **Write.** Use a short problem or purpose title. Select relevant facts, not
   source notes. If the title communicates the request, omit the body unless
   required; otherwise add only what the title leaves unclear:
   - **Problem:** behavior or need, conditions, and why it matters. Do not
     frame a feature request as a bug.
   - **Outcome:** observable, judgeable results, not a recipe. One sentence
     may suffice; list distinct outcomes, not a default checklist.
   - **Context:** necessary decisions, constraints, evidence, and dependencies;
     summarize to stand alone, link details, and omit when unnecessary.

   These are optional, not required sections. Keep task- or completion-changing
   details, including security, compatibility, external contracts, and material
   unknowns; omit generic cautions, exhaustive exclusions, and routine tests or
   commands. Describe restored capability, not a fix. Leave storage, timing, and
   code structure to the assignee unless required; label proposed approaches
   tentative or omit them. For maintenance, describe cost or risk; an agreed or
   externally required change may itself be the outcome. Do not file trivial
   debt belonging in the current change or title a ticket `Follow-up`.
5. **Scope and connect.** Aim for one problem and coherent outcome; split parts
   independently prioritized, deferred, or completed. Never split code, needed
   tests, and required docs just for size; file counts and time are not criteria.
   Read relationships before changing them. For genuine uncertainty, name the
   question and needed decision or deliverable; do not promise the eventual
   feature or stop at "investigate".

   The normal flow is ticket, work, PR; establish the issue ID before naming a
   branch. For those tasks use `git-workflow`'s `naming-branches` and
   `writing-pull-requests`, repository rules first. For work spanning tickets,
   use the primary ticket's branch ID and explain each PR relationship. Tickets
   and PRs need not be one-to-one. Reference partial work without closing; use
   completion links only when the outcome is fulfilled under actual tracker
   automation, not while deployment or verification remains.
6. **Review metadata** with [Metadata](references/metadata.md). When publication
   is authorized, apply established values and project-supported choices;
   never silently promote proposals to assignments or commitments, or create
   labels, fields, milestones, or projects merely to fill the ticket. Disclose
   fields tools cannot read or write rather than claiming absence or success.
7. **Deliver.** Return a draft's title, needed body, metadata proposals,
   relations, and material questions; omit empty categories. Do not invent an ID
   or imply publication. For authorized creation or update, apply the template
   and established metadata; preserve unrelated content and properties. Read back
   the issue and separately stored project fields to confirm destination,
   content, metadata, and relationships. Report the real ID, URL, and
   incomplete actions; never call a draft published.

## Gotchas

- Suspected vulnerabilities are disclosures: follow the project's security
  policy or private reporting channel. Never put exploit details or reproduction
  in a public or publicly synced ticket. Without a private path, return the
  draft in your reply, not a repository file, and say so.
- Separate observations, suspected causes, and proposed solutions. Preserve
  useful feedback verbatim and link its source when available. Never invent
  impact, reproduction steps, thresholds, prior decisions, or issue IDs. Ask
  only when context cannot resolve a material gap in problem, scope,
  destination, or completion.
- A CLI or API may not apply a UI template to an explicit body.
- Keep the body on the agreed problem, scope, and outcome. Record changes and
  their reasons, not superseded plans or progress logs; link existing discussion
  or design records. Never redefine success silently. Keep detailed
  implementation and verification evidence with the PR.

Sources: [body guidance](assets/ticket-body.md#sources).
