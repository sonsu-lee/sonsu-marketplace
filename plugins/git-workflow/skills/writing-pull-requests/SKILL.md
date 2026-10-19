---
name: writing-pull-requests
description: Use this skill when drafting, creating, or updating a pull request, writing its title or description, preparing UI evidence for a pull request, or marking it ready for review.
compatibility: >-
  Requires Git and the bundled writing-commits skill. Publishing requires
  authenticated GitHub tooling; native media uploads require gh with --attach
  support and repository push access.
---

# Writing pull requests

Write for reviewers and future maintainers, not as a narration of the diff.
Follow the target repository's contribution rules, AI policy, templates, and
merge requirements first. The defaults below fill gaps; they do not authorize
changing repository settings or bypassing required checks.

## Choose the requested work

- **Title only:** establish the change and validate the title. Skip body
  templates, label management, and media procedures unless also requested.
- **Draft content:** apply the body rules and identify relevant evidence and
  labels. Do not push, publish, or mutate labels just to prepare a draft.
- **Publish, update, or mark ready:** apply the relevant sections of the
  publication procedure only when that action is authorized.

## Establish the change and repository context

Identify the repository, head branch, and intended base. Use the user's base or
an established project target; otherwise discover the repository's default
branch rather than assuming `main`. Read the full proposed diff against that
base and relevant issue or design context. Do not infer the scope from the last
commit or a summary of the agent's work.

A PR is one coherent, explainable change that can become a sound commit:

- Address one purpose. Split independent topics, not just files or line counts.
- Include related tests, callers, and required documentation with the change.
- Keep the target branch working after each PR lands. Dependent PRs must name
  their dependencies and merge order; a later PR must not repair a broken base.
- Prefer separating substantial refactoring from behavior changes. Small local
  cleanups need not become separate PRs.
- Keep enough context to understand the change; do not split implementation from
  its necessary usage or tests merely to make the diff shorter.

A PR may be one safe step toward a larger feature and may contain multiple
working commits. If it is too broad to review, propose a coherent split before
publishing rather than disguising its scope with a narrower description.

## Write and validate the title

Prefer squash merging where the repository permits it. Write the title as the
subject of the resulting commit, following the
[writing-commits skill](../writing-commits/SKILL.md). Reuse its repository-first
validation procedure and defaults; do not create separate PR-title rules.
Validate the exact proposed title as a one-line message before presenting it as
ready or publishing it, and revalidate after edits.

Describe the final change, not the sequence of work or the branch's commit list.
Keep draft state in GitHub's Draft field, not a `WIP` title prefix.

Squash does not guarantee that GitHub uses the PR title or body. Its default
message depends on repository settings and sometimes the number of commits.
The PR body can use Markdown and media; it need not be a verbatim commit body.
When preparing a merge, inspect and validate the final complete commit message
with writing-commits, preserving important rationale, breaking-change details,
and attribution. Do not merge as part of a request merely to write or open a PR.

## Choose the body format

Read contribution instructions and find the applicable PR template, including
multiple-template directories. On GitHub, inspect `.github/`, the repository
root, and `docs/`, in that precedence order. If none applies, check the owner's
public `.github` repository for an inherited default; these files are not in
the target repository's clone. Templates offered by GitHub live on the default
branch. Use an explicitly requested template when applicable.

Preserve repository-required fields and automation markers. Satisfy the content
principles below within that format instead of appending a second template.
If no repository or inherited template applies, start with the
[bundled body template](assets/pr-body.md). It is a starting structure, not a
requirement to invent content or fill every optional section. Explicit bodies
sent through CLI or API must already incorporate the selected template; do not
assume the publishing tool will apply it for you.

## Explain the reason and approach

- **Why:** the concrete problem, limitation, or need motivating the change.
- **What changes:** the observable or architectural change and its approach.
  Include important reasons for choosing that approach, constraints, and
  tradeoffs that are not evident from the code.

Summarize enough for a reviewer to orient themselves without reading the whole
diff. Do not enumerate every file, function, or implementation step. Do not
invent motivation or require an alternatives essay for an obvious change.
Length should follow the complexity of the decision.

Include related issues, design context, and compatibility or migration details
when relevant. Summarize essential external context so the explanation remains
useful if a link becomes inaccessible. Use closing keywords only when this PR
actually completes the issue; use a reference for partial or related work.
Follow the tracker integration's syntax and behavior rather than assuming that
GitHub closing keywords work identically elsewhere.

## Record author checks, not CI status

Describe change-specific situations actually checked and the observed results.
Do not repeat CI's build, lint, type-check, or test-pass checklist. A targeted
automated check can still be informative: for example, explain that the original
reproduction fails before the fix and succeeds afterward, rather than listing
routine test commands already visible in CI.

Use concise prose or ordinary bullet lists, not task checkboxes: these are
observations, not a standardized completion checklist. Do not add arbitrary
checks to populate the section. Link evidence instead of duplicating it. Include
commands, environment details, or output only when they help reproduce or judge
the result. Distinguish a proposed test plan from completed checks.

Omit this section or briefly explain why no additional checks were needed when
appropriate. State material unverified behavior or blockers; an unnecessary
check and a necessary check that could not run are different cases. Never claim
that an agent's execution proves a person reviewed or understood the change.

## Provide UI evidence

When preparing or verifying UI evidence, read
[UI evidence](references/ui-evidence.md). Select marked screenshots, focused
recordings, both, or a justified omission based on what
changes. The reviewer should understand the location, difference, and behavior
without starting the application. Inability to capture, mark, or upload needed
evidence is a blocker to completing that evidence, not a reason to call it
unnecessary. Keep evidence synchronized with the latest diff.

## Disclose AI assistance

Follow the repository's AI policy before generating or publishing content;
some projects restrict AI-authored descriptions or contributions, not merely
undisclosed use. If the repository requires body disclosure, keep that format.
Otherwise record known AI assistance as PR metadata using its designated label,
or `ai-assisted` when it has no naming convention. For authorized publication or
label updates, read the
[label procedure](references/publishing.md#label-ai-assistance). For a draft
only, identify the intended label without creating or applying it.

Do not add an AI section or checkbox to the default body, or duplicate a label
with a routine disclosure paragraph. Explain the scope and purpose in the body
only when it affects review, such as substantial generated code needing focused
inspection, or when repository policy requires it. Tool names, model versions,
prompts, and transcripts are not required by the default.

An absent label does not establish non-use. Do not infer unknown prior usage,
remove an existing AI label without evidence, or claim that a label proves
human review. AI assistance never transfers the author's responsibility for
the change. Do not add AI co-authorship or modify commit trailers merely to
record tool use.

## Publish and maintain the PR

When publication, an update, or a ready-for-review transition is requested, read
the relevant sections of [Publishing a pull request](references/publishing.md).
Drafting is not permission to push or publish. Create new PRs as **Draft by
default**, even when checks pass. Mark ready only when the user explicitly asks
and repository readiness requirements are met. Do not change an existing PR's
stage merely because its description is updated.

Before publication and again before marking ready, ensure the title, rationale,
checks, links, and media describe the current diff. Preserve other contributors'
content when updating. Keep lasting design explanations in the description,
code, or documentation rather than only in a review reply.

## References

Google supplies content and change-size principles, not a required PR template:

- [Writing good CL descriptions][descriptions]: what, why, decision context,
  informative titles, and keeping the description current.
- [Small CLs][small]: coherent changes, related tests, and safe incremental work.
- [What to look for in a code review][review]: design, functionality, and useful
  evidence where reading code alone is insufficient.

The fallback headings, author-check policy, AI disclosure, and Draft default are
this plugin's choices. Useful comparisons are
[React's template][react], [Rust's author-check and disclosure guidance][rust],
and [LLVM's human-accountability policy][llvm]. Their project-specific
restrictions do not become universal requirements here.

[descriptions]: https://google.github.io/eng-practices/review/developer/cl-descriptions.html
[small]: https://google.github.io/eng-practices/review/developer/small-cls.html
[review]: https://google.github.io/eng-practices/review/reviewer/looking-for.html
[react]: https://github.com/facebook/react/blob/main/.github/PULL_REQUEST_TEMPLATE.md
[rust]: https://rustc-dev-guide.rust-lang.org/llm-guidance/writing.html
[llvm]: https://llvm.org/docs/AIToolPolicy.html
