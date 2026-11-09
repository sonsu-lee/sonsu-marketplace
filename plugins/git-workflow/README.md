# git-workflow

Name branches, write commits, and prepare draft pull requests by repository
conventions.

## Install

Register the marketplace as described in the
[root installation guide](../../README.md#install), then run the command for
your client:

```sh
omp plugin install git-workflow@sonsu-marketplace
codex plugin add git-workflow@sonsu-marketplace
claude plugin install git-workflow@sonsu-marketplace
```

### Dependencies

The `git-workflow` skills reuse the target repository's validation setup first.
When none exists, the commit fallback needs Node.js 22.12.0 or newer and npm
(`npx`), while the branch fallback needs uv (`uvx`) and Python 3.10 or newer.
The first uncached fallback run needs access to its package registry.

Publishing pull requests needs an authenticated GitHub tool. Native media
uploads use GitHub CLI's `--attach` support and require push access to the target
repository. Capturing UI evidence needs suitable capture and annotation tools.

## Usage

### CLI

```sh
omp skill list
codex plugin list --marketplace sonsu-marketplace --json
claude plugin details git-workflow
```

In any supported client, ask for the task naturally:

```text
Suggest a branch name for GitHub issue #45, which fixes a header overflow.

Write a commit message for the staged changes.

Draft a pull request title and body for this branch without publishing it.
```

Natural-language requests usually select the matching skill, but selection is
a model decision, not a guaranteed hook. To select a skill explicitly, use
`$git-workflow:writing-commits` in Codex or `/git-workflow:writing-commits` in
Claude Code. Listing a plugin does not prove that its skills run.

### Skills

- **`writing-commits`** writes Conventional Commit messages and validates them
  before use. It reuses repository commands, tools, versions, and configuration.
  Only without an existing execution setup does it run pinned commitlint through
  `npx`; only without configuration does it use bundled ESM defaults. See the
  [skill's validation procedure](skills/writing-commits/SKILL.md#required-validation).
- **`naming-branches`** names and validates branches with Conventional Branch
  1.1.0, reusing repository validation first. Without an execution setup it runs
  pinned `commit-check` through `uvx`; repository configuration still takes
  precedence over bundled defaults. This is a Python CLI, not an npm package.
  The skill's default prefixes are `feat/` (not `feature/`), `bugfix/` (not
  `fix/`), `hotfix/`, `release/`, and `chore/`. See the
  [skill's validation procedure](skills/naming-branches/SKILL.md#required-validation).
- **`writing-pull-requests`** starts PR descriptions with a concise Summary of
  the change, adding content-specific sections, focused code explanations,
  diagrams, and UI evidence when needed. It links ticket context instead of
  repeating it. Dependent PRs use GitHub stacks where available; new PRs are
  Draft by default. See the
  [PR writing procedure](skills/writing-pull-requests/SKILL.md).

Ask to draft, create, or update a pull request to use `writing-pull-requests`.
New PRs are Draft by default.

Branch prefixes do not change commit types: a `bugfix/` branch can contain
`fix`, `test`, and other commits. A missing dependency or failed configured
validator is not an absent setup and must not trigger a fallback. These skills
provide agent workflow instructions, not Git hooks or CI enforcement.

## Contributing

Pull requests are welcome. Ask questions or report problems in
[GitHub Issues](https://github.com/sonsu-lee/sonsu-marketplace/issues). Follow
the repository's [contributor guide](../../CONTRIBUTING.md), including its
[plugin](../../CONTRIBUTING.md#adding-a-plugin) and
[testing](../../CONTRIBUTING.md#testing-a-plugin) procedures.

## License

[MIT](../../LICENSE) © sonsu-lee
