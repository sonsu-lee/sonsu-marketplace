# sonsu-marketplace

Personal plugin marketplace for omp, Codex, and Claude Code.

[omp](https://github.com/can1357/oh-my-pi) reads `.omp-plugin/marketplace.json`;
[Codex](https://developers.openai.com/codex/cli) reads
`.agents/plugins/marketplace.json`; [Claude Code](https://code.claude.com/docs/en/overview)
reads `.claude-plugin/marketplace.json`. All three install the same `plugins/`
packages.

## Table of Contents

- [Install](#install)
  - [Dependencies](#dependencies)
  - [omp](#omp)
  - [Codex](#codex)
  - [Claude Code](#claude-code)
  - [Migrating existing installations](#migrating-existing-installations)
- [Usage](#usage)
  - [CLI](#cli)
- [Available plugins](#available-plugins)
- [Contributing](#contributing)
- [License](#license)

## Install

### Dependencies

Install [omp](https://github.com/can1357/oh-my-pi#install),
[Codex CLI](https://developers.openai.com/codex/cli), or
[Claude Code](https://code.claude.com/docs/en/overview) before using this
marketplace. Codex and Claude Code must provide the plugin marketplace and the
subagent interfaces that some plugins use; older clients without them do not
meet the prerequisites. Local catalog installation and installed-skill discovery
were checked with Codex CLI `0.163.0`, omp `18.12.6`, and Claude Code
`2.1.304`, the versions the `checks` workflow installs. These are checked
baselines, not promises for every older release or evidence of authenticated
model execution.

Some plugins need additional tools or authenticated services; see the
`Dependencies` section of each plugin's guide in
[Available plugins](#available-plugins).

### omp

Register the marketplace once:

```sh
omp plugin marketplace add sonsu-lee/sonsu-marketplace
```

Install the package you need. The default scope is `user`; add `--scope project`
to install only in the current project.

```sh
omp plugin install git@sonsu-marketplace
```

To migrate registered packages under their previous names, run the
[migration script](scripts/migrate-omp-plugins.sh) from a checkout of this
repository. It defaults to user scope and skips packages that are not installed.
Before installing the first missing replacement, it refreshes the catalog once.

```sh
./scripts/migrate-omp-plugins.sh
```

For project scope, run the script by its absolute path from the target
project and pass `project` as the argument.

The `design` skills need no browser. To use the optional omp capture tools,
follow the [design dependencies](plugins/design/README.md#dependencies).
Install missing JavaScript dependencies in `design`'s `installPath`, not
globally or in your project.

### Codex

```sh
codex plugin marketplace add sonsu-lee/sonsu-marketplace
codex plugin list --marketplace sonsu-marketplace --available --json
```

Check the installed entries (without `--available`):

```sh
codex plugin list --marketplace sonsu-marketplace --json
```

Install the package you need:

```sh
codex plugin add git@sonsu-marketplace
```

### Claude Code

```sh
claude plugin marketplace add sonsu-lee/sonsu-marketplace
claude plugin list
```

Install the package you need:

```sh
claude plugin install git@sonsu-marketplace
```

Use `codex plugin add <name>@sonsu-marketplace` or
`claude plugin install <name>@sonsu-marketplace` for another package; Claude
Code also accepts `--scope project`. This is a repository marketplace, not a
submission to a public plugin directory. The common local marketplace format
also applies to supporting app and IDE surfaces; their availability varies,
and CLI checks do not verify those UIs.

### Migrating existing installations

Refresh your Git-backed catalog before installing replacements; see the
[update commands](#cli). The package IDs below all use `@sonsu-marketplace`.

| Previous package | Replacement |
| --- | --- |
| `product` | `prd`, `decisions`, and `tickets` |
| `skill-workflow`, `planning-workflow` | `development` |
| `decision-workflow` | `decisions` |
| `ticket-workflow` | `tickets` |
| `git-workflow` | `git` |
| `design-workflow` | `design` |
| `review-workflow` | `review` |
| `writing-workflow` | `writing` |

In omp, the [migration script](scripts/migrate-omp-plugins.sh) installs all
replacements in the selected scope before removing the old ID. In Codex and
Claude Code, install the replacements you use, then remove only an installed
old ID. For example, after replacing `product`:

```sh
codex plugin remove product@sonsu-marketplace
claude plugin uninstall product@sonsu-marketplace --scope user --keep-data
```

For Claude Code, use the old package's listed scope (`user`, `project`, or
`local`) for installation and removal. `development` keeps its ID; update it
and install `grill` to keep its former interview skills. For an integrated
code workflow, see the package list below. Update saved invocations too:
`$product:writing-prd` becomes `$prd:writing-prd`, for example, and
`/development:grill-me` becomes `/grill:grill-me`.

## Usage

### CLI

In omp, check the registered packages, scopes, and install paths, then check
plugin health and skill discovery:

```sh
omp plugin list --json
omp plugin doctor
omp skill list
```

If `doctor` still reports `Missing package.json` or `orphan` for an old name
absent from `omp plugin list --json`, uninstall cannot remove it by ID.
For a user installation, inspect `~/.omp/plugins/node_modules/<old-name>`
and `~/.omp/plugins/omp-plugins.lock.json`. Move only a confirmed stale
symlink outside `node_modules`; back up the lock file before removing only
the matching orphan entry under `plugins`. Run `omp plugin doctor` again.
Do not delete the cache or plugin data. For skill name collisions, check
the source paths printed by `omp skill list`. If the only warning is
`package_manifest: Not created yet`, it refers to `~/.omp/plugins/package.json`,
not to `design`'s dependencies. In a marketplace-only setup you can leave
that file absent; there is no need to reinstall the plugin.

In Codex, check catalog and installed state:

```sh
codex plugin list --marketplace sonsu-marketplace --json
```

In Claude Code, check installed state and a package's components:

```sh
claude plugin list
claude plugin details git
```

Listing proves catalog or installation state, not skill execution. In a Codex
session, explicitly select the installed plugin skill as `$<plugin>:<skill>`,
for example `$git:writing-commits`. A bare `$writing-commits` does not
select that plugin skill on the checked CLI baseline. In Claude Code, invoke it
as `/<plugin>:<skill>`, for example `/git:writing-commits`. Retain the
qualified name returned by discovery when invoking skills or matching results.
Natural-language selection is model behavior, not an installation hook or
guaranteed trigger.

The `development` router and optional hooks differ by client and configuration;
see its [activation and limitations](plugins/development/README.md#usage)
before relying on automatic context or approval checks.

In an omp session, `/marketplace` opens the catalog in the plugin browser.
Installed skills provide guidance for relevant requests; for example, ask omp to
name a branch or write a commit message when using `git`. Each plugin
guide in [Available plugins](#available-plugins) shows example requests for its
skills.

For omp, fetch catalog changes, then upgrade installed plugins:

```sh
omp plugin marketplace update sonsu-marketplace
omp plugin upgrade
```

For Codex, refresh a Git-backed marketplace:

```sh
codex plugin marketplace upgrade sonsu-marketplace
```

An absolute local marketplace path is used directly and cannot be refreshed
with `marketplace upgrade`; that command requires a configured Git source.

For Claude Code, refresh the catalog, then update an installed plugin:

```sh
claude plugin marketplace update sonsu-marketplace
claude plugin update git@sonsu-marketplace
```

Claude Code loads plugins from a local-path marketplace in place, so their
source edits take effect at the next session without a version change.

## Available plugins

- [development][development]: Route tasks, plan and execute work, investigate
  bugs, and author skills.
- [grill][grill]: `grill-me` interviews you about a plan or draft; `grilling`
  works through dependent decisions one question at a time; `grill-with-docs`
  checks terminology and decisions against project documents.
- [review][review]: Review code independently and report evidence locally.
- [prd][prd]: Turn agreed requirements into a PRD without another interview.
- [decisions][decisions]: Assess and record consequential architecture decisions.
- [tickets][tickets]: Draft GitHub Issues or Linear tickets; publish only when
  requested.
- [design][design]: Design and review interfaces and graphics with scoped
  evidence and an optional omp verification harness.
- [writing][writing]: Write and refine Korean, English, and Japanese prose.
- [git][git]: Manage worktrees, branches, commits, and pull requests.

For integrated code work, install `development` and `review`. Add the other
packages for product, design, prose, or Git work; each is independently usable.

Skills install in all three clients. Client-specific parts differ:

- `review` dispatches its review workers through each client's subagents; see
  [Defaults and limits](plugins/review/README.md#defaults-and-limits).
- `design` strict runs and capture tools are omp only; see
  [Start an omp strict run](plugins/design/README.md#start-an-omp-strict-run).
- For recognized sensitive actions, `development` applies the evidence gate
  without a second omp prompt. Claude Code denies a blocked action or requests
  confirmation; the separately registered Codex user hook denies it.
  See [Usage](plugins/development/README.md#usage).

## Contributing

Pull requests are welcome. Ask questions or report problems in
[GitHub Issues](https://github.com/sonsu-lee/sonsu-marketplace/issues). Read the
[contributor guide](CONTRIBUTING.md) before changing a plugin, skill, document,
or workflow.

## License

[MIT](LICENSE) © sonsu-lee.

[development]: plugins/development/README.md
[review]: plugins/review/README.md
[grill]: plugins/grill/README.md
[prd]: plugins/prd/README.md
[decisions]: plugins/decisions/README.md
[tickets]: plugins/tickets/README.md
[design]: plugins/design/README.md
[writing]: plugins/writing/README.md
[git]: plugins/git/README.md
