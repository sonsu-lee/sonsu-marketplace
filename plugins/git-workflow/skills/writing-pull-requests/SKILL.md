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
ticket carries why. Repository rules and templates come first. For prose
drafting or editing, also read the matching language skill.

## Workflow

Do only the requested part: title, description, or publishing.

1. **Read the change.** Base is the user's or project's target, otherwise the
   default branch. Read the full diff and the related ticket.
2. **Check the scope.** One purpose per PR, with its tests, callers, and docs;
   split independent changes. The target branch must still work after it
   lands. If it depends on an unmerged PR, read
   [Stacked pull requests](references/stacked-prs.md).
3. **Write the title** as the final commit subject and validate it with
   [writing-commits](../writing-commits/SKILL.md).
4. **Write the body** as below.
5. **Publish only when asked**, following
   [Publishing a pull request](references/publishing.md). New PRs start as
   Draft; mark ready only on request and once repository requirements are met.

## Write the body

Start with `## Summary`: what changed, in a few sentences. Add headings named
for their content only when needed.

Include only what helps review:

- **Changed behavior,** including preserved behavior when it matters.
- **Code to examine:** a few key points, such as a condition or processing
  order, with a short excerpt or link.
- **Structure or flow:** a Mermaid diagram, not repeated in prose.
- **Constraints:** compatibility, rollout order, or known limitations.
- **UI changes:** evidence prepared with [UI evidence](references/ui-evidence.md).
- **Evidence** only when the repository requires it or a claim needs it, with
  its method and environment.
- **The problem,** briefly, only when no ticket is accessible.

Leave out the ticket's motivation, file-by-file narration, routine
verification results, and work logs.

## Link issues

For each issue, decide whether this PR completes it, advances part of it, or
only relates to it, judging by the issue's stated outcome and the work landed
before or with this PR. Only a completing link should close the issue on merge.

## Gotchas

- A repository PR template may be inherited from the owner's public `.github`
  repository. Keep its required fields and markers, even in `--body-file` or
  API bodies, and put the summary in its matching section.
- GitHub renders single newlines in PR bodies as line breaks. Keep each
  paragraph and list item on one line.
- GitHub closing keywords work only when the PR targets the default branch;
  otherwise read [closing issues](references/publishing.md#edge-cases).
- Mark work in progress with GitHub's Draft state, not a title prefix.
