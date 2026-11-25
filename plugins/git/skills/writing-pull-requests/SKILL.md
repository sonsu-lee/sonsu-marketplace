---
name: writing-pull-requests
description: Use for PR content, publishing/readiness, stacks, and merge messages; not code review/status lookup. Includes titles, descriptions, UI evidence, and dependent PR setup. Not for code fixes.
compatibility: >-
  Requires Git and the bundled writing-commits skill. Publishing requires
  authenticated GitHub tooling; native media uploads require gh with --attach
  support and repository push access.
---

# Writing pull requests

A PR description tells reviewers what changed and where to focus; the linked
ticket carries the motivation. Reviewers act on its statements and cannot tell
a guess from a fact, so write only what the diff, the ticket, or the author
supports. Repository rules and templates come first. For prose drafting or
editing, also read the matching language skill.

## Workflow

Do only the requested part: title, description, or publishing.

1. **Read the change.** Base is the user's or project's target, otherwise the
   default branch. Read the full diff and the related ticket. Commit messages
   and an existing title or body may be stale; check them against the diff
   before reusing them.
2. **Check the scope.** One purpose per PR, with its tests, callers, and docs;
   split independent changes. The target branch must still work after it
   lands. If it depends on an unmerged PR, read
   [Stacked pull requests](references/stacked-prs.md).
3. **Write the title** as the final commit subject and validate it with the
   `writing-commits` skill. Use the client's skill interface: Codex
   `$git:writing-commits`, Claude Code `/git:writing-commits`, or omp
   `skill://writing-commits`. If nested invocation is unavailable, read the
   installed skill's `SKILL.md` and distinguish reading from invocation.
   If it is inaccessible, report the blocker; do not claim validation passed.
4. **Write the body** as below.
5. **Publish only when asked**, following
   [Publishing a pull request](references/publishing.md). New PRs start as
   Draft; mark ready only on request and once repository requirements are met.

## Write the body

Start with `## Summary`: what changed, in a few sentences. Name the condition
and the resulting behavior ("status lookups retry once after a timeout"), not
a quality ("improves reliability"). Add headings named for their content only
when needed.

Include only what helps review:

- **Changed behavior,** including preserved behavior when it matters.
- **Design choices the diff does not explain:** why this approach over the
  obvious alternative.
- **Code to examine:** a few key points, such as a condition or processing
  order, with a short excerpt or link.
- **Structure or flow:** a Mermaid diagram, not repeated in prose.
- **Constraints:** compatibility, rollout order, or known limitations.
- **UI changes:** evidence prepared with [UI evidence](references/ui-evidence.md).
- **Evidence** only when the repository requires it or a claim needs it: the
  observation itself with its method and environment, such as a request and
  response, command output, or a measurement. A bare report that routine
  checks ran or passed (tests, lint, local or staging runs, model or tool
  versions) is not evidence; omit it unless the repository requires it.
- **The problem,** briefly, only when no ticket is accessible.

Leave out the ticket's motivation, file-by-file narration, work logs, and
repetition of a point already made.

Do not infer a motivation, a consequence, or a result, and do not call a
change safe or verified without a check that shows it. When a reason reviewers
need is unknown, leave it out and tell the user what is missing.

When updating a PR, correct every statement that later commits made false.
Rewrite it in place; do not append a revision history.

## Link issues

For each issue, decide whether this PR completes it, advances part of it, or
only relates to it, judging by the issue's stated outcome and the work landed
before or with this PR. Take the linking form for that relation from repository
guidance or the tracker's integration; if none is established, reference the
issue plainly and state the relation in words. Only a completing link should
close the issue on merge.

Do not assume that merging closes the issue or that only a completing link
changes its status: the target branch, tracker settings, branch names, and
commit messages can each decide. State any check the issue needs after merge,
as in [closing issues](references/publishing.md#edge-cases).

## Evaluate the result

Score audience/purpose, factual fidelity, clarity, scope/authority, and
verification: 0 failed, 1 partial, 2 evidenced. Exclude inapplicable items with
reasons and normalize to 10. Require 8/10 and verified requirements, authority,
safety, contracts, and evidence. Fix failures and reevaluate up to three times,
not unchanged. If still unsuccessful, report each score, conditions, evidence,
and blockers. Wait for required decisions, permission, or access.

## Gotchas

- A repository PR template may be inherited from the owner's public `.github`
  repository. Keep its required fields and markers, even in `--body-file` or
  API bodies, and put the summary in its matching section.
- GitHub renders single newlines in PR bodies as line breaks. Keep each
  paragraph and list item on one line.
- Mark work in progress with GitHub's Draft state, not a title prefix.
