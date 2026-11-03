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

## Choose the requested work

- **Title only:** establish the change and validate the title.
- **Draft content:** read the diff and write the description.
- **Publish, update, or mark ready:** perform only the requested operation.

## Establish the change and scope

Identify the repository, head, and target branch. Use the user's destination or
established project target, otherwise discover the default branch. Read the
full diff against the base and the related ticket or design context.

Keep one purpose per PR, including its implementation, callers, tests, and
required documentation. Split independent changes, not related files merely to
reduce size. Each PR must leave the target branch working when it lands.

For work that depends on an unmerged PR, read
[Stacked pull requests](references/stacked-prs.md) before selecting the base.
Independent PRs target the trunk separately.

## Write and validate the title

Write the title as the resulting commit subject and validate it with
[writing-commits](../writing-commits/SKILL.md), again after any edit. Describe
the final change, not the work sequence. Mark work in progress with GitHub's
Draft state, not a title prefix.

## Write the body

Start with `## Summary` and briefly explain what changed. Add subsections only
when the change needs them, naming each for its content rather than filling a
fixed outline. A small change can use Summary alone.

Read the applicable repository template and preserve its required fields and
markers, including in CLI or API submissions. If its required layout differs,
use its summary equivalent rather than adding a duplicate section.
If no repository template applies on GitHub, check the owner's public `.github`
repository for an inherited default; it is not part of the target checkout.

Select the details that help review this change:

- **Changed behavior:** what the feature, interface, or implementation now does,
  including preserved behavior when it matters.
- **Code to examine:** a few implementation points central to review, such as
  a condition, processing order, data conversion, or responsibility boundary.
  Explain the relevant decision with a short excerpt or code link when useful;
  do not narrate the diff file by file.
- **Structure or flow:** a Mermaid diagram for component relationships or
  processing flow, without repeating it in prose.
- **Constraints:** compatibility changes, rollout order, or known limitations
  that affect understanding or merging the change.
- **UI changes:** marked screenshots or focused recordings prepared with
  [UI evidence](references/ui-evidence.md), so reviewers see the changed
  location and result without running the app.

Choose prose, lists, tables, or checkboxes to suit the content. Link the related
ticket instead of repeating its motivation. Add decision context only when the
ticket does not cover it and reviewers need it to understand the implementation.

Do not add routine verification results, commands, or work logs. Include evidence
only when the repository requires it or a claim needs support, such as a
performance improvement. Keep the method, environment, and trade-offs needed to
interpret such evidence; distinguish observations from unverified claims.

Keep each prose paragraph, including list items, on one source line: GitHub
renders single newlines in PR bodies as line breaks. Repository Markdown column
limits do not apply to PR bodies.

Link issues and dependencies without copying them. Decide each issue's
relationship from its stated outcome and the final diff, counting work that
lands before or with it: this PR completes it, advances part of it, or only
relates to it. Link an issue this PR completes so that merging closes it; link
any other issue so that merging leaves it open. If the base is not GitHub's
default branch, read
[closing issues](references/publishing.md#edge-cases).

## Publish and maintain the PR

When publishing, updating, marking ready, or preparing a merge message, read
[Publishing a pull request](references/publishing.md). Create new PRs as Draft,
and mark one ready only when the user asks and the repository's readiness
requirements are met. Keep the title, body, links, and media aligned with later
changes.
