# Publishing a pull request

Drafting a title or body does not authorize a push, PR creation, or merge. When
the user requests publication, use their intended repository, head, and base.
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

## References

- [GitHub CLI attachments][attachments]: permissions, placement, and video.
- [gh pr create][create] and [gh pr edit][edit]: flags and partial success.
- [Repository templates][templates] and [inherited defaults][defaults].
- [Squash message configuration][squash]: title and body are not always used.
- [Linking issues][issues]: closing keywords and default-branch behavior.

[attachments]: https://docs.github.com/en/github-cli/github-cli/attaching-files-with-github-cli
[create]: https://cli.github.com/manual/gh_pr_create
[edit]: https://cli.github.com/manual/gh_pr_edit
[templates]: https://docs.github.com/en/communities/using-templates-to-encourage-useful-issues-and-pull-requests/creating-a-pull-request-template-for-your-repository
[defaults]: https://docs.github.com/en/communities/setting-up-your-project-for-healthy-contributions/creating-a-default-community-health-file
[squash]: https://docs.github.com/en/repositories/configuring-branches-and-merges-in-your-repository/configuring-pull-request-merges/configuring-commit-squashing-for-pull-requests
[issues]: https://docs.github.com/en/issues/tracking-your-work-with-issues/using-issues/linking-a-pull-request-to-an-issue
