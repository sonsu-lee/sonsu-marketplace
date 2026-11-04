# Stacked pull requests

Stack only PRs that depend on an unmerged PR in the same repository. Each
branch contains the one below it and each PR targets that branch; the bottom PR
targets the trunk. Forks cannot join a stack. If stacking is unsupported, target
the trunk and state the dependency and merge order in the body.

1. Create each PR with the [publishing procedure](publishing.md).
2. Link the chain on GitHub's website or with the optional `gh stack`
   extension, setting the trunk explicitly.
3. Check each PR's base, title, body, and Draft state, and restore what the
   tool changed.

## Gotchas

- `gh stack submit` opens new PRs as ready by default, and `--open` on `submit`
  or `link` marks PRs ready.
- Linking can push branches and change PR bases.
- Rebasing rewrites branches; rebase a stack only when the user asks. Stacks
  created on the website have no local tracking until checked out.
- Merging a PR also merges every unmerged PR below it. Confirm that scope
  before merging mid-stack.
- PRs above the bottom target another PR's branch, so GitHub ignores their
  closing keywords ([closing issues](publishing.md#edge-cases)). After the
  completing PR lands, check the issue.

## References

- [Stack constraints][stacks]; [creating][create], [managing][manage], and
  [merging][merge] stacks.
- [Stack CLI commands][cli] and [other tools][other].

[stacks]: https://docs.github.com/en/pull-requests/reference/stacked-pull-requests
[create]: https://docs.github.com/en/pull-requests/how-tos/create-pull-requests/creating-stacked-pull-requests
[manage]: https://docs.github.com/en/pull-requests/how-tos/create-pull-requests/managing-stacked-pull-requests
[merge]: https://docs.github.com/en/pull-requests/how-tos/merge-and-close-pull-requests/merging-stacked-pull-requests
[cli]: https://docs.github.com/en/pull-requests/reference/stacked-prs-cli-commands
[other]: https://docs.github.com/en/pull-requests/reference/use-other-tools-with-stacked-pull-requests
