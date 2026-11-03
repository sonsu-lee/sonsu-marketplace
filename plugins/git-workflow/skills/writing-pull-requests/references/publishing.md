# Publishing a pull request

Drafting a title or body does not authorize a push, PR creation, or merge.
When publication is requested:

1. Establish the intended repository, head, and base. Use the user's target or
   project target, otherwise the default branch. Check for an existing PR for
   that head and base. For a dependent PR, read [stacked PRs](stacked-prs.md).
2. Prepare the validated title and complete, repository-compliant body. Prepare
   and inspect any required [UI evidence](ui-evidence.md) before uploading.
3. Push only the intended commits to the intended remote and branch using the
   repository's workflow. Create a new PR as Draft or update the existing PR.
   Do not force-push, merge, enable auto-merge, request reviewers, or change
   repository settings merely to publish.
4. Inspect the actual PR: confirm its head, base, title, body, state, and any
   rendered media. Report incomplete publication or evidence rather than
   inferring success from a command's exit status.

Use the publishing tool required by the environment. With GitHub CLI, run from
the target repository, setting `repo` to `OWNER/REPO`, `head` and `base` to
the intended branches, `title` to the validated title, and `body_file` to the
absolute path of the completed UTF-8 body file:

```sh
gh pr create --draft --repo "$repo" --base "$base" --head "$head" \
  --title "$title" --body-file "$body_file"
```

A structured API call must explicitly set `draft: true`. Do not use `--fill`
in place of an accurate, template-aware body. CLI `--dry-run` may still push.

## Edge cases

- **Existing PR:** Read and preserve existing content and state when updating;
  a body replacement replaces the entire body. Do not turn a ready PR back into
  a Draft automatically. Mark a Draft ready only on explicit request and after
  repository readiness requirements are met. Ready is not permission to merge.
- **Media:** Resolve local paths from the working directory. Check that the
  installed CLI supports attachment and that the user has the required push
  access. Otherwise use an authorized browser upload or report the blocker;
  do not change permissions, invent URLs, or silently omit required evidence.
  Attach the inspected files, then inspect the rendered images, captions, and
  video playback. Report any inspection limitation. See [GitHub CLI
  attachments][attachments] for supported formats, placement, and limits.
- **Partial success:** An attachment failure can leave the PR created or edited
  even when the command fails. Inspect the actual PR and uploaded assets before
  retrying; update the existing PR and attach only missing files, rather than
  repeating creation.
- **Closing issues:** GitHub acts on closing keywords only in a PR that targets
  the default branch; for another base they create no link, and merging does
  not close the issue ([linking issues][issues]). After the PR that completes
  the issue lands, check the issue; report it if still open, or close it when
  the user asked. For stacks, see the [stack guidance](stacked-prs.md).
- **Merge message:** A squash message depends on repository settings and may not
  use the PR title or body. When preparing a merge, inspect and validate the
  complete final message using [writing-commits](../../writing-commits/SKILL.md),
  preserving important rationale, breaking changes, and attribution. A request
  to write or open a PR does not authorize a merge.

## References

- [GitHub CLI create][create] and [edit][edit]; [attachments][attachments].
- [PR templates][templates] and [inherited defaults][defaults].
- [Closing issues][issues] and [squash message configuration][squash].

[attachments]: https://docs.github.com/en/github-cli/github-cli/attaching-files-with-github-cli
[create]: https://cli.github.com/manual/gh_pr_create
[edit]: https://cli.github.com/manual/gh_pr_edit
[templates]: https://docs.github.com/en/communities/using-templates-to-encourage-useful-issues-and-pull-requests/creating-a-pull-request-template-for-your-repository
[defaults]: https://docs.github.com/en/communities/setting-up-your-project-for-healthy-contributions/creating-a-default-community-health-file
[squash]: https://docs.github.com/en/repositories/configuring-branches-and-merges-in-your-repository/configuring-pull-request-merges/configuring-commit-squashing-for-pull-requests
[issues]: https://docs.github.com/en/issues/tracking-your-work-with-issues/using-issues/linking-a-pull-request-to-an-issue
