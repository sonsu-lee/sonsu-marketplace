---
name: writing-pull-requests
description: Use this skill when drafting, creating, or updating a pull request, writing its title or description, preparing UI evidence for a pull request, or marking it ready for review.
compatibility: >-
  Requires Git and the bundled writing-commits skill. Publishing requires
  authenticated GitHub tooling; native media uploads require gh with --attach
  support and repository push access.
---

# Writing pull requests

Write for reviewers in plain language: say what changes and why, using
established technical terms rather than formal filler. Follow repository rules,
templates, and AI policy first. These defaults do not authorize settings
changes or bypassing required checks.

## Choose the requested work

- **Title only:** establish the change and validate the title; skip body
  templates, labels, and media unless requested.
- **Draft content:** apply the body rules; identify evidence and labels without
  pushing, publishing, or mutating labels.
- **Publish, update, or mark ready:** only when authorized; see below.

## Establish the change and scope

Identify the repository and head. Choose the trunk: the user's destination or
established project target, otherwise the discovered default branch, never an
assumed `main`. Use that trunk as base, except when a PR depends on an unmerged
PR and the repository supports
[stacked PRs](references/publishing.md#stack-dependent-pull-requests): use the
lower PR's head branch as base. Read the full diff against that base and
relevant issue or design context, not just the last commit or agent summary.

A PR is one coherent, explainable change that can become a sound commit:

- Address one purpose. Split independent topics, not just files or line counts.
- Include related tests, callers, and required documentation; never split
  implementation from needed usage or tests just to shrink the diff.
- Keep the target branch working after each PR lands. A dependent PR names its
  dependency and merge order; a later PR must not repair a broken base. Stack
  only work that depends on an unmerged PR; independent PRs target the trunk
  separately, because stacking them imposes a false merge order.
- Prefer separating substantial refactoring from behavior changes; small
  local cleanups may stay.

A PR may be one safe step toward a larger feature and contain several commits.
If too broad to review, propose a split before publishing instead of hiding
scope behind a narrower description.

## Write and validate the title

Prefer squash merging where permitted. Write the title as the resulting commit
subject, following the
[writing-commits skill](../writing-commits/SKILL.md); reuse its
repository-first validation and defaults, not separate PR-title rules. Validate
the exact proposed title as a one-line message before presenting it as ready or
publishing it, and revalidate after edits. Describe the final change, not the
work sequence. Keep draft state in GitHub's Draft field, not a `WIP` prefix.

Squash does not guarantee GitHub uses the PR title or body; to prepare a merge,
read [Merge message](references/publishing.md#merge-message). Never merge merely
to write or open a PR.

## Choose the body format

Read contribution instructions and find the applicable PR template, including
template directories. On GitHub, inspect `.github/`, the repository
root, and `docs/`, in that precedence order. If none applies, check the owner's
public `.github` repository for an inherited default (not in the target clone).
Offered templates live on the default branch. Use an explicitly requested
template when applicable.

Preserve required fields and automation markers, without adding a second
template or filling optional sections merely because they exist. If no template
applies, use the [bundled body](assets/pr-body.md). An explicit CLI or API body
must already incorporate the selected template.

Keep paragraphs on one source line, including within list items: GitHub renders
single newlines in PR bodies as line breaks, unlike `.md` files. Preserve blank
lines and list, table, and code structure. Do not apply file-lint or column limits
unless required for PR bodies, even in a temporary `.md` file for `--body-file`.

## Explain the reason and approach

Keep what reviewers need to understand and safely use the change:

- **Why:** the concrete problem.
- **What changes:** observable results and non-obvious decisions. For nontrivial
  changes, explain relevant flow, responsibility, or ordering and what is preserved.

Do not retell every file, command, retry, or investigation step. Summarize
essential context and link existing evidence; retain material risks, rollout
constraints, and uncertainty. Do not invent rationale or alternatives for
obvious changes. Link related issues and dependencies without copying them.
Use closing keywords only when this PR completes the issue; GitHub ignores
them unless it targets the default branch
([stacks](references/publishing.md#closing-issues-from-a-stack)). Follow other
trackers' own completion-link rules.

## Record author checks, not CI status

Report scenarios and outcomes, not an execution diary. Required profile/results
reporting means names and outcomes, not an environment inventory. Keep execution
details only to explain failures, limits, or reproduction. Link evidence
reviewers can access, not local trace paths.

Use prose or ordinary bullets, not task checkboxes. Omit optional checks when
unnecessary; do not enumerate everything not tested. Keep material blockers
and unverified behavior explicit, and distinguish plans from completed checks.
Agent execution is not evidence of human review.

## Provide UI evidence

When preparing or verifying UI evidence, read
[UI evidence](references/ui-evidence.md). Select marked screenshots, focused
recordings, both, or a justified omission, so reviewers understand the
location, difference, and behavior without running the app. Inability to
capture, mark, or upload needed evidence is a blocker, not proof it is
unnecessary. Keep it synchronized with the diff.

## Disclose AI assistance

Follow the repository's AI policy before generating or publishing content; some
projects restrict AI-authored contributions, not just undisclosed use. Preserve
required body disclosure. Otherwise record known AI assistance with the designated
label, or `ai-assisted` if none is designated. For authorized publication or label
updates, read the [label procedure](references/publishing.md#label-ai-assistance).
For a draft, identify the intended label without creating or applying it.

Do not add an AI section or checkbox to the default body, or repeat a label in
a disclosure paragraph. Explain AI use in the body only when it affects review,
such as substantial generated code needing focused inspection, or when policy
requires it; tool names, models, and prompts are not required. An absent label
does not establish non-use. Do not infer unknown prior usage, remove an existing
AI label without evidence, or claim it proves human review. AI assistance never
transfers author responsibility. Do not add AI co-authorship or change commit
trailers merely to record tool use.

## Publish and maintain the PR

When publication, an update, or a ready-for-review transition is requested, read
the relevant sections of [Publishing a pull request](references/publishing.md).
Drafting is not permission to publish. Create new PRs as **Draft by
default**, even when checks pass. Mark ready only when the user explicitly asks
and readiness requirements are met. Updating a description does not change an
existing PR's stage.

Before publication or readiness, align title, body, links, and media with the
diff and remove repeated explanations. Preserve others' content. Keep current
rationale in the body, code, or docs; link substantial history rather than
appending superseded accounts.

Sources: [publishing reference](references/publishing.md#design-sources).
