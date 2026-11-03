# Stacked pull requests

Use a stack only for PRs that depend on unmerged PRs in the same repository.
A supported stack is one linear chain: each branch contains the branch below
it, each PR targets that branch, and the bottom PR targets the user's
destination or project target, otherwise the default branch. A fork head cannot
be included. If the host or repository does not support stacking, or a
constraint fails, target the trunk and state the dependency and merge order in
the body.

Create each PR using the [publishing procedure](publishing.md), then link the
chain using a supported stack tool. GitHub's website can create a stack or link
existing PRs with chained bases. The optional `gh stack` extension can link
branches or PRs bottom to top; set its intended trunk explicitly. Linking can
push branches and change PR bases; when extending a stack, its existing trunk
is retained.

Stack tools can change state: the extension's `submit` editor defaults new PRs
to ready, and `--open` on `submit` or `link` marks PRs ready. Inspect each PR's
base, title, body, and Draft state afterward and restore the intended states.

Rebasing rewrites branches. Rebase a stack only when the user requests its
update. Website-created or linked stacks do not automatically establish local
tracking; check out the remote stack before using local stack rebase commands.

## Merging and closing issues

A stack merges bottom-up: merging a PR also merges all unmerged PRs below it.
Confirm that scope before merging a mid-stack PR. GitHub then retargets the
next PR to the stack base.

Every PR above the bottom of a stack targets another PR's branch, so GitHub
does not act on its closing keywords
([closing issues](publishing.md#edge-cases)). The stack docs do not say whether
keywords take effect after GitHub retargets such a PR to the stack base; check
the issue after the PR that completes it lands.

## References

- [Stack constraints][stacks]; [creating][create], [managing][manage], and
  [merging][merge] stacks.
- [Stack CLI commands][cli] and [other tools][other].
- [Linking pull requests to issues][issues].

[stacks]: https://docs.github.com/en/pull-requests/reference/stacked-pull-requests
[create]: https://docs.github.com/en/pull-requests/how-tos/create-pull-requests/creating-stacked-pull-requests
[manage]: https://docs.github.com/en/pull-requests/how-tos/create-pull-requests/managing-stacked-pull-requests
[merge]: https://docs.github.com/en/pull-requests/how-tos/merge-and-close-pull-requests/merging-stacked-pull-requests
[cli]: https://docs.github.com/en/pull-requests/reference/stacked-prs-cli-commands
[other]: https://docs.github.com/en/pull-requests/reference/use-other-tools-with-stacked-pull-requests
[issues]: https://docs.github.com/en/issues/tracking-your-work-with-issues/using-issues/linking-a-pull-request-to-an-issue
