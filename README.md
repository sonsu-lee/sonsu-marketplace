# sonsu-marketplace

English | [한국어](README.ko.md)

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
codex plugin add git-workflow@sonsu-marketplace
```

For Claude Code:

```sh
claude plugin marketplace add sonsu-lee/sonsu-marketplace
claude plugin install git-workflow@sonsu-marketplace
```

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
claude plugin details git-workflow
```

Listing proves catalog or installation state, not skill execution. In a Codex
session, explicitly select the installed plugin skill as `$<plugin>:<skill>`,
for example `$git-workflow:writing-commits`. A bare `$writing-commits` does not
select that plugin skill on the checked CLI baseline. In Claude Code, invoke it
as `/<plugin>:<skill>`, for example `/git-workflow:writing-commits`. Retain the
qualified name returned by discovery when invoking skills or matching results.
Natural-language selection is model behavior, not an installation hook or
guaranteed trigger.

In an omp session, `/marketplace` opens the catalog in the plugin browser.
Installed skills provide guidance for relevant requests; for example, ask omp to
name a branch or write a commit message when using `git-workflow`. Each plugin
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
claude plugin update git-workflow@sonsu-marketplace
```

Claude Code loads plugins from a local-path marketplace in place, so their
source edits take effect at the next session without a version change.

## Available plugins

- [git-workflow][git-workflow]: Name branches, write commits, and prepare draft
  pull requests by repository conventions.
- [skill-workflow][skill-workflow]: Create, refine, evaluate, and independently
  review focused agent skills, delegating mechanical work to existing tools.
- [ticket-workflow][ticket-workflow]: Write small, outcome-centered GitHub and
  Linear tickets while leaving implementation to the assignee.
- [decision-workflow][decision-workflow]: Select consequential design decisions
  and write lightweight ADRs using repository conventions first.
- [writing-workflow][writing-workflow]: Write and refine natural Korean,
  English, and Japanese prose while preserving meaning and author voice.
- [review-workflow][review-workflow]: Evidence-driven code review with
  independent general and focused reviewers and local-first reporting.
- [planning-workflow][planning-workflow]: Plan non-trivial work and coordinate
  authorized execution through independent review and final validation.
- [design-workflow][design-workflow]: Design and review interfaces and graphics
  with scoped evidence and an optional omp verification harness.

## Contributing

Pull requests are welcome. Ask questions or report problems in
[GitHub Issues](https://github.com/sonsu-lee/sonsu-marketplace/issues). Read the
[contributor guide](CONTRIBUTING.md) before changing a plugin, skill, document,
or workflow.

## License

[MIT](LICENSE) © sonsu-lee, except
`plugins/skill-workflow/skills/evaluating-skills/`, which is under the
[Apache License 2.0](plugins/skill-workflow/skills/evaluating-skills/LICENSE.txt)
and includes material from Anthropic's
[skill-creator](https://github.com/anthropics/skills/tree/main/skills/skill-creator).

[git-workflow]: plugins/git-workflow/README.md
[skill-workflow]: plugins/skill-workflow/README.md
[ticket-workflow]: plugins/ticket-workflow/README.md
[decision-workflow]: plugins/decision-workflow/README.md
[writing-workflow]: plugins/writing-workflow/README.md
[review-workflow]: plugins/review-workflow/README.md
[planning-workflow]: plugins/planning-workflow/README.md
[design-workflow]: plugins/design-workflow/README.md
