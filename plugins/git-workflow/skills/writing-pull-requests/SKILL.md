---
name: writing-pull-requests
description: Use this skill when drafting, creating, or updating a pull request, writing its title or description, preparing UI evidence for a pull request, or marking it ready for review.
compatibility: >-
  Requires Git and the bundled writing-commits skill. Publishing requires
  authenticated GitHub tooling; native media uploads require gh with --attach
  support and repository push access.
---

# Writing pull requests

Write for reviewers and maintainers, not as a narration of the diff. Follow
the repository's contribution rules, AI policy, templates, and merge
requirements first. These defaults fill gaps; they never authorize changing
repository settings or bypassing required checks.

## Choose the requested work

- **Title only:** establish the change and validate the title; skip body
  templates, labels, and media unless requested.
- **Draft content:** apply the body rules; identify evidence and labels without
  pushing, publishing, or mutating labels.
- **Publish, update, or mark ready:** only when authorized; see below.

## Establish the change and scope

Identify the repository, head, and base: the user's base or an established
project target, otherwise the discovered default branch, never an assumed
`main`. Read the full proposed diff against that base and relevant issue or design
context; do not infer scope from the last commit or the agent's summary.

A PR is one coherent, explainable change that can become a sound commit:

- Address one purpose. Split independent topics, not just files or line counts.
- Include related tests, callers, and required documentation; never split
  implementation from needed usage or tests just to shrink the diff.
- Keep the target branch working after each PR lands. Dependent PRs name
  dependencies and merge order; a later PR must not repair a broken base.
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

Preserve required fields and automation markers; satisfy the principles below
within that format instead of appending a second template. If none applies,
start from the [bundled body template](assets/pr-body.md), a structure that does
not require inventing content or filling optional sections. An explicit CLI or
API body must already incorporate the selected template.

## Explain the reason and approach

- **Why:** the concrete problem, limitation, or need motivating the change.
- **What changes:** the observable or architectural change and approach, with
  reasons, constraints, and tradeoffs not evident from the code.

Orient reviewers without listing every file or step; do not invent motivation
or demand alternatives essays for obvious changes. Include related issues,
design context, and compatibility or migration details when relevant,
summarizing essential external context in case links break. Use closing
keywords only when this PR actually completes the issue; otherwise reference
it. Follow the tracker integration's syntax; GitHub keywords may not work
identically elsewhere.

## Record author checks, not CI status

Describe change-specific situations actually checked and observed results, not
CI's build, lint, type-check, or test checklist. A targeted check can
inform, such as a reproduction that fails before the fix and passes after.

Use prose or ordinary bullets, not task checkboxes; add no arbitrary checks.
Link evidence; include commands or output only when they help reproduce or
judge it. Distinguish a proposed test plan from completed checks. Omit the
section or say why no extra checks were needed, but state material unverified
behavior or blockers: an unnecessary check differs from a needed one that
could not run. Never claim agent execution proves a person reviewed the change.

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

Before publication and again before marking ready, ensure the title, rationale,
checks, links, and media describe the current diff. Preserve others' content
when updating; keep lasting design explanations in the description, code, or
docs, not only in a review reply.

Sources: [publishing reference](references/publishing.md#design-sources).
