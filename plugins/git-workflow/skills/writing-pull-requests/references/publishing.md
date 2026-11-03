# Publishing a pull request

1. **Confirm the target.** Use the intended repository, head, and base, and
   check for an existing PR. For a dependent PR, read
   [stacked PRs](stacked-prs.md).
2. **Prepare the content.** Use the validated title and the finished body;
   prepare any [UI evidence](ui-evidence.md) first.
3. **Push and create.** Push only the intended commits, then create a Draft or
   update the existing PR. Publishing does not include force-pushing, merging,
   auto-merge, reviewer requests, or settings changes.
4. **Inspect the result.** Check the PR's head, base, title, body, Draft state,
   and rendered media. Report anything incomplete; an exit code is not proof.

With GitHub CLI, from the target repository:

```sh
gh pr create --draft --repo "$repo" --base "$base" --head "$head" \
  --title "$title" --body-file "$body_file"
```

## Gotchas

- An API call must set `draft: true` explicitly.
- `--fill` does not replace a written body, and `--dry-run` can still push.
- `--body-file` on `gh pr edit` replaces the whole body. Keep existing content
  and the PR's Draft or ready state when updating.
- Mark ready only on request and once the repository's readiness requirements
  are met.
- Media upload with `--attach` needs CLI support and push access. Otherwise use
  an authorized browser upload or report the blocker; never invent URLs. See
  [GitHub CLI attachments][attachments] for formats and limits.
- A failed attachment can still leave the PR created or edited. Inspect the PR
  before retrying, and attach only what is missing.

## Edge cases

- **Closing issues:** GitHub acts on closing keywords only when the PR targets
  the default branch ([linking issues][issues]). After the completing PR lands,
  check the issue; report it if still open, or close it when the user asked.
- **Merge message:** Squash messages follow repository settings and may ignore
  the PR title or body. When preparing a merge, validate the final message with
  [writing-commits](../../writing-commits/SKILL.md), keeping rationale,
  breaking changes, and attribution. Merge only when the user asks.

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
