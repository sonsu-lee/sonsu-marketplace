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
5. **Scope and connect.** Aim for one problem and coherent outcome; split parts
   independently prioritized, deferred, or completed. Never split code, needed
   tests, and required docs just for size; file counts and time are not criteria.
   Read and preserve existing relationships; use supported operations for
   parent/child and dependency links, not just prose. For genuine uncertainty,
   name the question and needed decision or deliverable; do not promise the
   eventual feature or stop at "investigate".

   The normal flow is ticket, work, PR; establish the issue ID before naming a
   branch. For those tasks use `git-workflow`'s `naming-branches` and
   `writing-pull-requests`, repository rules first. For work spanning tickets,
   use the primary ticket's branch ID and explain each PR relationship. Tickets
   and PRs need not be one-to-one. Reference partial work without closing; use
   completion links only when the outcome is fulfilled under actual tracker
   automation, not while deployment or verification remains.
6. **Review metadata.** Inspect actual fields, allowed values, template defaults,
   and repository/team conventions. Apply explicit choices and established rules
   before proposing grounded candidates for missing values:
   - **Labels/type:** use existing classifications fitting the problem and area,
     not every possible match or near-duplicates.
   - **Assignee:** use explicit assignment or established ownership, not an
     assumption that the reporter/current user owns it; other owners are proposals.
   - **Priority:** use known impact, severity, and time constraints on the team's
     scale; a bug is not automatically urgent.
   - **Estimate:** use the actual scale and defensible scope; leave unset when
     investigation or assignee judgment is needed. Unknown is not zero; points
     are not hours unless the team defines them so.
   - **Project/milestone:** use existing destinations whose goals and scope fit
     the outcome, not just similar names; an unresolved project leaves its
     milestone unresolved.

   Keep metadata separate from the body unless the template requires it. Give
   brief reasons for proposals; leave optional unknowns unset and batch only
   required or consequential questions that context cannot resolve. Resolve
   ambiguous identities before publication. Do not turn proposals into
   assignments or commitments, or create labels, fields, milestones, or projects
   merely to fill a ticket. Disclose fields tools cannot read or write.
7. **Deliver.** Return a draft's title, needed body, metadata proposals,
   relations, and material questions; omit empty categories and invent no ID.
   For authorized creation or update, apply the template and established
   metadata; preserve unrelated content and properties. Read back the issue,
   relationships, and separately stored fields to confirm each intended result.
   Report the real ID, URL, incomplete actions, and unapplied recommendations
   separately; never call a draft or failed action published.

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
