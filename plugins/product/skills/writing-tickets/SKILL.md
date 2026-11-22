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
2. **Find context.** Confirm the repository or Linear workspace/team and primary
   tracker from the request and project guidance. Read the selected platform's
   differences: [GitHub Issues](references/github-issue.md) or
   [Linear](references/linear.md). Read relevant tickets, discussion, evidence,
   and guidance. Before creation, search that scope and inspect likely
   duplicates; reuse or link existing issues without rewriting someone else's.
   Respect existing sync; do not create independent counterparts or set up sync.
3. **Choose the format.** Read [Bug](references/bug.md) for behavior differing
   from product, documentation, or contract promises, including regressions.
   Read [Parent](references/parent.md) when independently completable parts share
   a goal, or a parent, epic, or project is created or split. Other kinds need
   no kind reference.

   Under project rules, prefer an explicitly requested applicable template,
   then the applicable repository, team, or issue-type template; use
   [body guidance](assets/ticket-body.md) only when none applies. Clarify
   materially different template choices. Inspect content and properties; keep
   required fields, metadata, and automation markers within that format, not a
   second template. Disclose failed lookup, not template absence, in drafts.
   Resolve required fields before publishing; CLI/API creation does not waive them.
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
5. **Scope and connect.** Default to one ticket for one coherent problem and
   outcome; do not split solely by size or file count. When splitting is useful,
   prefer independently verifiable vertical slices that deliver complete
   behavior across the needed layers, including tests and docs.
   Name only real blocking edges and identify the frontier whose blockers are
   resolved. If a wide mechanical change cannot land in green slices, plan its
   safe integration sequence rather than inventing independence. Preserve the
   original requirements, defaults, and prohibitions. Quote quantified
   constraints exactly when paraphrasing could change scope; check all
   restatements, including the title, problem, and outcome. Do not strengthen a
   collective prohibition into a per-item requirement. For example, prohibiting
   all sessions from merging into one does not establish exact session counts
   or membership; treat those additional constraints as open unless agreed.
   Read and preserve existing relationships. Tracker changes require approval.
   For genuine uncertainty, name the needed decision or deliverable.

   The normal flow is ticket, work, PR. Use the `git` package's
   `naming-branches` and `writing-pull-requests` as applicable. A ticket may need
   multiple PRs or a PR address multiple tickets. Reference partial work without
   closing; completion links require the actual outcome and verification.
6. **Review metadata.** Read [Metadata](references/metadata.md) for relevant
   fields, grounded proposals, and publication constraints.
7. **Deliver.** Return the draft's title, needed body, metadata proposals,
   relations, and material questions; distinguish relevant field states, omit
   empty categories, and invent no ID. Honor title-and-body-only requests.
   For authorized creation or update, apply template and established metadata;
   preserve unrelated content and properties. Read back the issue, relationships,
   and separately stored fields to confirm intended results. Report the real ID,
   URL, incomplete actions, and unapplied recommendations separately; never
   call a draft or failed action published.

Independent review is required only when requested or required by the project
or host. Arrange it within the authorized scope; report unavailable required
review rather than replacing it with self-evaluation.

## Evaluate the ticket

Assess user problem, requirements accuracy, scope, open questions and evidence,
and acceptance. Score each applicable item 0, 1, or 2, record exclusions and
reasons, and normalize to 10. Require 8/10 and verified requirements, authority,
security, data safety, confirmed contracts, and stage evidence. Fix supported
failures and reevaluate up to three times, never without changes. If still
unsuccessful, report each score, mandatory conditions, evidence, and blockers.
Wait for required user decisions, permission, or access instead of retrying.
Required independent review cannot be replaced by a self-score.

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
