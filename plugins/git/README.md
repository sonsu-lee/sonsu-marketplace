# git

Manage worktrees, name branches, write commits, and prepare draft pull requests.

## Install

Register the marketplace as described in the
[root installation guide](../../README.md#install), then run the command for
your client:

```sh
omp plugin install git@sonsu-marketplace
codex plugin add git@sonsu-marketplace
claude plugin install git@sonsu-marketplace
```

### Dependencies

The `git` skills reuse the target repository's validation setup first.
Without an execution setup, commit and branch fallbacks use uv (`uvx`) and a
supported Python environment; the branch fallback requires Python 3.10 or newer.
The first uncached fallback run needs access to its package registry.

Publishing pull requests needs an authenticated GitHub tool. Native media
uploads use GitHub CLI's `--attach` support and require push access to the target
repository. Capturing UI evidence needs suitable capture and annotation tools.

## Usage

### CLI

```sh
omp skill list
codex plugin list --marketplace sonsu-marketplace --json
claude plugin details git
```

In any supported client, ask for the task naturally:

```text
Suggest a branch name for GitHub issue #45, which fixes a header overflow.

Write a commit message for the staged changes.

Draft a pull request title and body for this branch without publishing it.
```

Natural-language requests usually select the matching skill, but selection is
a model decision, not a guaranteed hook. To select a skill explicitly, use
`$git:writing-commits` in Codex or `/git:writing-commits` in
Claude Code. Listing a plugin does not prove that its skills run.

### Skills

- **`writing-commits`** writes Conventional Commit messages and validates them
  before use. It reuses repository commands, tools, versions, and configuration.
  Only without an existing execution setup does it run pinned `committed` through
  `uvx`; only without repository configuration does it use bundled defaults.
  See the [skill's validation procedure](skills/writing-commits/references/validation.md).
- **`naming-branches`** names and validates branches with Conventional Branch
  1.1.0, reusing repository validation first. Without an execution setup it runs
  pinned `commit-check` through `uvx`; repository configuration still takes
  precedence over bundled defaults. This is a Python CLI, not an npm package.
  The skill's default prefixes are `feature/` (not `feat/`), `bugfix/` (not
  `fix/`), `hotfix/`, `release/`, and `chore/`. See the
  [skill's validation procedure](skills/naming-branches/SKILL.md#required-validation).
- **`managing-worktrees`** sets up an explicitly requested isolated workspace
  or assesses integration choices. Creation, merge, push, and cleanup require
  their own authority. See the [worktree procedure](skills/managing-worktrees/SKILL.md).
- **`writing-pull-requests`** writes PR descriptions from what the diff, the
  ticket, and the author support: a Summary of the changed behavior, then only
  what helps review, such as design choices the diff does not explain, code to
  examine, constraints, and evidence a claim needs. It links ticket motivation
  instead of repeating it. Dependent PRs use GitHub stacks where available; new
  PRs are Draft by default. See the
  [PR writing procedure](skills/writing-pull-requests/SKILL.md).

Ask to draft, create, or update a pull request to use `writing-pull-requests`.

Branch prefixes do not change commit types: a `bugfix/` branch can contain
`fix`, `test`, and other commits. A missing dependency or failed configured
validator is not an absent setup and must not trigger a fallback. These skills
provide agent workflow instructions, not Git hooks or CI enforcement.
Repositories that want local checks may use [Lefthook](https://lefthook.dev/)
to run their validators as Git hooks, alongside CI for enforcement. This
plugin does not install or configure those hooks.

## Contributing

Pull requests are welcome. Ask questions or report problems in
[GitHub Issues](https://github.com/sonsu-lee/sonsu-marketplace/issues). Follow
the repository's [contributor guide](../../CONTRIBUTING.md), including its
[plugin](../../CONTRIBUTING.md#adding-a-plugin) and
[testing](../../CONTRIBUTING.md#testing-a-plugin) procedures.

## License

[MIT](../../LICENSE) © sonsu-lee
