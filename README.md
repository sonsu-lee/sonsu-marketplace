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
  - [Marketplace](#marketplace)
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

### Marketplace

For omp, add the marketplace:

```sh
omp plugin marketplace add sonsu-lee/sonsu-marketplace
```

List its plugins and install one:

```sh
omp plugin discover sonsu-marketplace
omp plugin install <plugin>@sonsu-marketplace
```

Add `--scope project` to install a plugin for the current project only.

For Codex:

```sh
codex plugin marketplace add sonsu-lee/sonsu-marketplace
codex plugin list --marketplace sonsu-marketplace --available --json
codex plugin add git@sonsu-marketplace
```

If this Codex home previously installed the old `*-workflow` packages from
this marketplace, remove them before installing their replacements. Otherwise
duplicate skill names can cause a natural-language request to load older guidance:

```sh
for plugin in git skill ticket decision writing review planning design; do
  codex plugin remove "$plugin-workflow@sonsu-marketplace"
done
```

Ignore a not-installed error for a package absent from that home, but investigate
other errors. The new packages have different names and must be installed
separately.

For Claude Code:

```sh
claude plugin marketplace add sonsu-lee/sonsu-marketplace
claude plugin install git@sonsu-marketplace
```

For omp or Claude Code, inspect installed packages and remove any of the same
old `*-workflow` names before installing their replacements. Select the scope
where each package is installed. The Claude Code example keeps its plugin data:

```sh
omp plugin uninstall <old-name>@sonsu-marketplace --dry-run
omp plugin uninstall <old-name>@sonsu-marketplace
claude plugin uninstall <old-name>@sonsu-marketplace --keep-data
```

The omp dry run previews removal; it does not remove the package. Use
`--scope project` for omp project installations. Claude Code also supports
`--scope project` and `--scope local`.

Use `codex plugin add <name>@sonsu-marketplace` or
`claude plugin install <name>@sonsu-marketplace` for another package; Claude
Code also accepts `--scope project`. This is a repository marketplace, not a
submission to a public plugin directory. The common local marketplace format
also applies to supporting app and IDE surfaces; their availability varies,
and CLI checks do not verify those UIs.

## Usage

### CLI

In omp, check available skills after installation:

```sh
omp skill list
```

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
- [review][review]: Review code independently and report evidence locally.
- [product][product]: Draft product requirements, ADRs, and tracker tickets.
- [design][design]: Design and review interfaces and graphics with scoped
  evidence and an optional omp verification harness.
- [writing][writing]: Write and refine Korean, English, and Japanese prose.
- [git][git]: Manage worktrees, branches, commits, and pull requests.

For integrated code work, install `development` and `review`. Add the other
packages for product, design, prose, or Git work; each is independently usable.
To migrate an existing installation, remove the old workflow packages and
install the new names. The old names are not aliases.

## Contributing

Pull requests are welcome. Ask questions or report problems in
[GitHub Issues](https://github.com/sonsu-lee/sonsu-marketplace/issues). Read the
[contributor guide](CONTRIBUTING.md) before changing a plugin, skill, document,
or workflow.

## License

[MIT](LICENSE) © sonsu-lee.

[development]: plugins/development/README.md
[review]: plugins/review/README.md
[product]: plugins/product/README.md
[design]: plugins/design/README.md
[writing]: plugins/writing/README.md
[git]: plugins/git/README.md
