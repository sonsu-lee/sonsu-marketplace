---
name: writing-pull-requests
description: Use for PR content, publishing/readiness, stacks, and merge messages; not code review/status lookup. Includes titles, descriptions, UI evidence, and dependent PR setup. Not for code fixes.
compatibility: >-
  Requires Git and the bundled writing-commits skill. Publishing requires
  authenticated GitHub tooling; native media uploads require gh with --attach
  support and repository push access.
---

# Writing pull requests

A PR description lets reviewers understand what changed and where to focus
without reconstructing it from the diff; the linked ticket carries why the work
was needed. Repository contribution rules and required template fields come
first. For prose drafting or editing, also read the matching language skill.

## Workflow

Do only the requested part: a title, a draft description, or publishing,
updating, or marking ready.

1. **Establish the change.** Identify the repository, head, and base: the
   user's destination or established project target, otherwise the default
   branch. Read the full diff against the base and the related ticket or design
   context.
2. **Check the scope.** One purpose per PR, with its implementation, callers,
   tests, and required documentation. Split independent changes, not related
   files merely to reduce size. Each PR must leave the target branch working.
   For work that depends on an unmerged PR, read
   [Stacked pull requests](references/stacked-prs.md) before choosing the base;
   independent PRs target the trunk separately.
3. **Write the title** as the resulting commit subject, describing the final
   change rather than the work sequence. Validate it with
   [writing-commits](../writing-commits/SKILL.md), again after any edit.
4. **Write the body** as described below.
5. **Publish only when asked.** For publishing, updating, marking ready, or
   preparing a merge message, read
   [Publishing a pull request](references/publishing.md). Create new PRs as
   Draft; mark one ready only when the user asks and the repository's
   readiness requirements are met. Keep the title, body, links, and media
   aligned with later changes.

## Write the body

Without a repository template, use this shape:

```markdown
## Summary

What changed, in a few sentences. Link the ticket for why.

## <Content-specific heading, only when needed>
```

A small change can use Summary alone. Name any extra section for its content,
and choose prose, lists, tables, or checkboxes to suit it.

Include what helps review this change:

- **Changed behavior:** what the feature, interface, or implementation now
  does, including preserved behavior when it matters.
- **Code to examine:** a few points central to review, such as a condition,
  processing order, data conversion, or responsibility boundary, with a short
  excerpt or code link when useful.
- **Structure or flow:** a Mermaid diagram for component relationships or
  processing flow.
- **Constraints:** compatibility changes, rollout order, or known limitations
  that affect understanding or merging the change.
- **UI changes:** marked screenshots or focused recordings, prepared and
  checked with [UI evidence](references/ui-evidence.md), so reviewers see the
  changed location and result without running the app.
- **Evidence, only when required or needed for a claim** such as a
  performance improvement: keep the method, environment, and trade-offs, and
  separate observations from unverified claims.
- **Context missing from the ticket:** state the problem briefly when no
  ticket is accessible, and add decision context only when reviewers need it.

Leave out:

- The ticket's motivation, which the link already carries.
- A file-by-file narration of the diff, or prose repeating a diagram.
- Routine verification results, commands, and work logs.

## Link issues

Link issues and dependencies without copying them. Decide each issue's
relationship from its stated outcome and the final diff, counting work that
lands before or with it: this PR completes it, advances part of it, or only
relates to it. Link an issue this PR completes so that merging closes it; link
any other issue so that merging leaves it open.

## Gotchas

- A repository PR template lives on the default branch, or is inherited from
  the owner's public `.github` repository. Keep its required fields and
  markers, including in CLI or API submissions, and put the summary in its
  matching section instead of adding a duplicate.
- GitHub renders single newlines in PR bodies as line breaks. Keep each prose
  paragraph, including list items, on one source line; repository Markdown
  column limits do not apply.
- GitHub closing keywords work only in PRs that target the default branch. For
  another base, read [closing issues](references/publishing.md#edge-cases).
- Mark work in progress with GitHub's Draft state, not a title prefix.
