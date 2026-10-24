# Publishing a pull request

Drafting a title or body does not authorize a push, PR creation, or merge. When
the user requests publication, use their intended repository, head, and base;
a head that depends on an unmerged PR uses that PR's branch as base (see
[Stack dependent pull requests](#stack-dependent-pull-requests)).
Check for an existing PR for that head and base before creating another.
Preserve its content and stage when updating; do not automatically convert an
existing ready PR back to Draft.

Run shell examples from the target repository root. Set `repo` to `OWNER/REPO`,
`base` and `head` to the intended branches, `title` to the validated title, and
`body_file` to the absolute path of the completed UTF-8 body file. For updates,
set `pr` to the existing PR number or URL. For labels, set `label` to the name
selected from repository policy, or `ai-assisted` if none is designated.
Resolve media paths against this working directory, not the skill directory;
use absolute paths for captures stored elsewhere. Set only the inputs needed
for the requested operation.

## Create as Draft

New PRs are Draft by default, even when local checks and CI pass. Use the
publishing tool required by the environment. With GitHub CLI:

```sh
gh pr create --draft --repo "$repo" --base "$base" --head "$head" \
  --title "$title" --body-file "$body_file"
```

With a structured GitHub API tool, explicitly set `draft: true`. Do not assume
an omitted field creates a Draft. Select the repository explicitly if the CLI
context is ambiguous. Do not use `--fill` as a substitute for an accurate,
template-aware description. `--dry-run` is not a side-effect-free preview:
GitHub CLI documents that it may still push changes.

Push only the intended commits to the intended remote and branch, using the
repository's workflow. Do not force-push, merge, enable auto-merge, request
reviewers, or change repository settings merely to publish a Draft.

Use the returned URL to inspect the created PR. Confirm its head, base, title,
body, and Draft state; do not infer creation or stage solely from an exit code.
Keep a PR draft until the user explicitly requests ready-for-review and the
repository's readiness requirements are satisfied. Creating a Draft must not
be followed by an automatic ready transition. A request to mark ready is not
permission to merge.

## Stack dependent pull requests

Use a [stack][stacks] only for a PR that depends on another unmerged PR in the
same repository. Its base is the head branch of the PR below it; the bottom PR
targets the trunk, normally the default branch. Independent PRs stay separate
against the trunk. A stack is one linear chain of branches, each containing the
one below, and cannot include a head in a fork. If the repository or host
offers no stack option, or a constraint fails, use the trunk as base and state
the dependency and merge order in the body.

Create each PR as above with `base` set to the branch below, then link them. On
the website, choose **Create stack** when creating the next PR with that base;
GitHub also offers a banner to stack existing PRs whose bases already chain
([creating stacks][stack-create]). With the `gh stack` extension,
`gh stack link` takes branches or PR numbers from bottom to top, uses existing
PRs, and creates and pushes missing ones as drafts
([other tools][stack-other]). The extension is optional: do not install it to
publish; the website needs none.

Extension commands do not follow this procedure by default: the `submit`
editor opens new PRs ready for review unless toggled, `--auto` generates
titles, and `--open` on `submit` or `link` marks PRs ready
([commands][stack-cli]). Inspect each PR's title, body, and Draft state, and
correct them as above.

Pushing to a lower branch or a moved trunk breaks the linear history merging
requires. Restore it with **Rebase stack** in the merge box or
`gh stack rebase` then `gh stack push` ([managing][stack-manage]). Rebasing
rewrites branches, so do it only when the user asks to update the stack. The
website rebase is unsigned; use the CLI where signed commits are required.

A stack merges from the bottom: merging a PR also merges every unmerged PR
below it, and a mid-stack PR cannot merge alone. A request to merge one
stacked PR therefore covers those below it; confirm that scope. Afterward,
GitHub rebases the next PR to target the stack base ([merging][stack-merge]).

### Closing issues from a stack

GitHub interprets closing keywords only when the PR targets the default branch.
For any other base they are ignored, no link is created, and merging does not
affect the issue ([linking issues][issues]). In a stack, every PR above the
bottom targets another PR's branch, and a stack on a non-default trunk has no
PR that targets the default branch. Reference the issue there without a
keyword. The bottom PR on the default branch may carry a keyword when it alone
completes the issue.

The stack docs do not say whether keywords take effect after a PR is retargeted
to the stack base. After the PR that completes the issue lands, check the
issue; report it if still open, or close it when the user asked.

## Label AI assistance

Inspect the repository's AI policy and existing labels. Reuse its designated
label; otherwise prefer `ai-assisted` for known AI use. A label describes tool
assistance, not a claim that all content was generated or human-reviewed.

Use the environment's required GitHub tool. With GitHub CLI, apply an existing
label without replacing unrelated labels:

```sh
gh pr edit "$pr" --repo "$repo" --add-label "$label"
```

The equivalent creation flag is `gh pr create --draft --label "$label"` alongside
the other creation arguments. Confirm the label exists before using it. If it
does not exist, create it only with explicit user or repository authorization:

```sh
gh label create "$label" --repo "$repo" \
  --description "AI tools assisted in preparing this pull request." \
  --color 8250df
```

Do not use `--force` to overwrite an existing label's metadata. If creation or
application is unavailable or unauthorized, report the missing label or
permission and request maintainer help rather than silently claiming disclosure
is complete. Do not bypass repository-required body disclosure. Verify the PR's
labels after publication; preserve its other labels and Draft state.

## Attach and verify media

Prepare and inspect media using [UI evidence](ui-evidence.md) before uploading.
Check `gh --version` and the relevant command's `--help` for `--attach` support.
The native attachment feature needs push access to the target repository.
If CLI support or permissions are missing, use an authorized browser upload
where available or report the blocker; do not publish fake URLs or silently
skip required evidence. Do not change permissions to make an upload work.

The following Markdown controls placement in a complete body file. Replace the
example paths and captions with the actual inspected media:

```markdown
## UI evidence

Before: the old error overlaps the submit button; the box marks the overlap.

![Marked overlap in the old form](./before-marked.png)

After: the error is below the field, leaving the button usable.

![Marked error placement in the updated form](./after-marked.png)

Interaction: submit invalid input, correct it, and submit again.

![](./form-flow.mp4)
```

Attach the exact referenced files. For a PR already created as Draft:

```sh
gh pr edit "$pr" --body-file "$body_file" \
  --attach ./before-marked.png \
  --attach ./after-marked.png \
  --attach ./form-flow.mp4
```

Select only the media the change needs, not necessarily all three examples.
`--body-file` replaces the body: load and preserve existing content before
editing it. Without a body flag, `gh pr edit --attach` keeps the existing body
and appends media. Attachments can also accompany `gh pr create --draft` or
`gh pr comment` when those operations are appropriate and authorized.

GitHub CLI uploads local media and rewrites matching Markdown references to
asset URLs. Unreferenced files are appended. Existing Markdown image alt text
is preserved; for appended images use `--attach './image.png#Description'`.
Video has no alt text: put a descriptive caption before a video reference in
its own paragraph so it renders as a player instead of an inline link.

Observe GitHub's current supported formats and size limits. Do not assume all
local files are uploadable. Do not commit evidence to Git just to obtain URLs.

If only some attachments succeed, creation or editing can still take effect
while the command exits nonzero. Inspect the returned PR and successful assets
before retrying. Update the existing PR and attach only missing media; never
blindly repeat a create command and produce duplicate PRs.

Open the rendered PR to verify image placement, legible annotations, captions,
and video playback. If playback or visual inspection is unavailable, report
that limitation instead of declaring the evidence verified. Remove obsolete
local-path placeholders and synchronize evidence after further UI changes.

## Merge message

Squash does not guarantee that GitHub uses the PR title or body. Its default
message depends on repository settings and sometimes the number of commits.
The PR body can use Markdown and media; it need not be a verbatim commit body.
When preparing a merge, inspect and validate the final complete commit message
with [writing-commits](../../writing-commits/SKILL.md), preserving important
rationale, breaking-change details, and attribution. Do not merge as part of a
request merely to write or open a PR.

## Design sources

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

## References

- [GitHub CLI attachments][attachments]: permissions, placement, and video.
- [gh pr create][create] and [gh pr edit][edit]: flags and partial success.
- [Repository templates][templates] and [inherited defaults][defaults].
- [Squash message configuration][squash]: title and body are not always used.
- [Linking issues][issues]: closing keywords apply only to default-branch PRs.
- [Stacked pull requests][stacks]: same repository, linear history, trunk.
- [Creating][stack-create], [managing][stack-manage], and
  [merging][stack-merge] stacks: website and CLI paths, rebasing, bottom-up
  merges.
- [Stack CLI commands][stack-cli] and [other tools][stack-other]: `submit`,
  `link`, draft and ready defaults.

[attachments]: https://docs.github.com/en/github-cli/github-cli/attaching-files-with-github-cli
[create]: https://cli.github.com/manual/gh_pr_create
[edit]: https://cli.github.com/manual/gh_pr_edit
[templates]: https://docs.github.com/en/communities/using-templates-to-encourage-useful-issues-and-pull-requests/creating-a-pull-request-template-for-your-repository
[defaults]: https://docs.github.com/en/communities/setting-up-your-project-for-healthy-contributions/creating-a-default-community-health-file
[squash]: https://docs.github.com/en/repositories/configuring-branches-and-merges-in-your-repository/configuring-pull-request-merges/configuring-commit-squashing-for-pull-requests
[issues]: https://docs.github.com/en/issues/tracking-your-work-with-issues/using-issues/linking-a-pull-request-to-an-issue
[stacks]: https://docs.github.com/en/pull-requests/reference/stacked-pull-requests
[stack-create]: https://docs.github.com/en/pull-requests/how-tos/create-pull-requests/creating-stacked-pull-requests
[stack-manage]: https://docs.github.com/en/pull-requests/how-tos/create-pull-requests/managing-stacked-pull-requests
[stack-merge]: https://docs.github.com/en/pull-requests/how-tos/merge-and-close-pull-requests/merging-stacked-pull-requests
[stack-cli]: https://docs.github.com/en/pull-requests/reference/stacked-prs-cli-commands
[stack-other]: https://docs.github.com/en/pull-requests/reference/use-other-tools-with-stacked-pull-requests
[descriptions]: https://google.github.io/eng-practices/review/developer/cl-descriptions.html
[small]: https://google.github.io/eng-practices/review/developer/small-cls.html
[review]: https://google.github.io/eng-practices/review/reviewer/looking-for.html
[react]: https://github.com/facebook/react/blob/main/.github/PULL_REQUEST_TEMPLATE.md
[rust]: https://rustc-dev-guide.rust-lang.org/llm-guidance/writing.html
[llvm]: https://llvm.org/docs/AIToolPolicy.html
