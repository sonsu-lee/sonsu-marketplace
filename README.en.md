# Sonsu Marketplace

[한국어](README.md) · [English](README.en.md) · [日本語](README.ja.md)

A collection of Codex, Claude Code, and omp plugins for development, research, product planning, and writing.

Each host gets a different set of plugins. Codex and Claude Code get all 15; omp gets seven default and six optional plugins. omp handles development execution and memory with its own features, so Dev Workflow and Memory Manager are not distributed to omp.

## Installation

Register the marketplace once and install the plugins you need. Check the installation status in the list, then start a new session. The [Plugins](#plugins) table shows which plugins each host can install.

### Codex

Requires a CLI that supports `codex plugin`.

```sh
codex plugin marketplace add sonsu-lee/sonsu-marketplace --ref main
# Install one plugin
codex plugin add dev-workflow@sonsu-marketplace
# To install all, use this instead of the single install above
for plugin in git tickets review dev-workflow fluent-korean fluent-english fluent-japanese writing research prompting product memory-manager design-patterns design worklog; do codex plugin add "$plugin@sonsu-marketplace"; done
codex plugin marketplace list
codex plugin list --marketplace sonsu-marketplace
```

### Claude Code

```sh
claude plugin marketplace add sonsu-lee/sonsu-marketplace
# Install one plugin
claude plugin install dev-workflow@sonsu-marketplace
# To install all, use this instead of the single install above
for plugin in git tickets review dev-workflow fluent-korean fluent-english fluent-japanese writing research prompting product memory-manager design-patterns design worklog; do claude plugin install "$plugin@sonsu-marketplace"; done
claude plugin marketplace list
claude plugin list
```

### omp

Install the seven default plugins, and install the six optional plugins separately when you need them. Only if you are turning on automatic updates, merge the YAML below into the existing `marketplace:` section of `~/.omp/agent/config.yml`.

<!-- omp-preset:start -->
```sh
omp plugin marketplace add sonsu-lee/sonsu-marketplace
for plugin in git tickets review fluent-korean fluent-english fluent-japanese design; do omp plugin install "$plugin@sonsu-marketplace"; done
```

```yaml
marketplace:
  autoUpdate: auto
```
<!-- omp-preset:end -->

```sh
# Optional install
omp plugin install writing@sonsu-marketplace
omp plugin install research@sonsu-marketplace
omp plugin install prompting@sonsu-marketplace
omp plugin install product@sonsu-marketplace
omp plugin install worklog@sonsu-marketplace
omp plugin install design-patterns@sonsu-marketplace
omp plugin list
```

## Usage

After installation, make a request in natural language. The host picks a skill based on your request and the skill descriptions.

Request: “Prepare only a PR draft for the current branch. Don't publish it.”

The Git plugin's `write-pr` reports a PR title, body draft, and unverified items without writing to the remote.

To call a skill by name, use the host's format.

| Host | Format | Example |
| --- | --- | --- |
| Codex | `$<skill>` | `$write-pr` |
| Claude Code | `/<plugin>:<skill>` | `/git:write-pr` |
| omp | `/skill:<skill>` | `/skill:write-pr` |

Each plugin's README has example requests for that plugin (Korean).

## Plugins

The link text is the installation name. In the omp column, `default` plugins are included in the default install command and `optional` plugins are installed separately.

| Plugin | Purpose | Codex | Claude Code | omp |
| --- | --- | :---: | :---: | :---: |
| [`git`](plugins/git/README.md) | Work with Git branches, commits, and pushes, and write, inspect, and repair GitHub PRs | ✓ | ✓ | default |
| [`tickets`](plugins/tickets/README.md) | Write GitHub Issues and Linear tickets and change their status, assignee, and relations | ✓ | ✓ | default |
| [`review`](plugins/review/README.md) | Review code, diffs, commits, and PRs for code health, run focused reviews, and address review comments | ✓ | ✓ | default |
| [`dev-workflow`](plugins/dev-workflow/README.md) | Design, plan, implement, debug, verify, and simplify software changes | ✓ | ✓ | — |
| [`fluent-korean`](plugins/fluent-korean/README.md) | Apply drafting rules to new Korean text and edit AI-sounding or translationese passages in existing Korean text (based on `im-not-ai`) | ✓ | ✓ | default |
| [`fluent-english`](plugins/fluent-english/README.md) | Draft, edit, and review everyday and technical English (based on `better-writing`) | ✓ | ✓ | default |
| [`fluent-japanese`](plugins/fluent-japanese/README.md) | Draft and edit everyday and technical Japanese and score documents (based on `natural-japanese`) | ✓ | ✓ | default |
| [`writing`](plugins/writing/README.md) | Select information, choose where it belongs, and organize writing for the reader and purpose | ✓ | ✓ | optional |
| [`research`](plugins/research/README.md) | Research multiple sources, verify facts, and write answers supported by evidence | ✓ | ✓ | optional |
| [`prompting`](plugins/prompting/README.md) | Create and improve prompts for Codex, ChatGPT, OpenAI API, Claude Code, and Anthropic API | ✓ | ✓ | optional |
| [`product`](plugins/product/README.md) | Explore product ideas, organize user evidence, test hypotheses, and write PRDs | ✓ | ✓ | optional |
| [`memory-manager`](plugins/memory-manager/README.md) | Recall, capture, and maintain local memory shared by Codex and Claude Code | ✓ | ✓ | — |
| [`design`](plugins/design/README.md) | Design, redesign, and audit general and operations interfaces through Figma or code, and find design references | ✓ | ✓ | default |
| [`design-patterns`](plugins/design-patterns/README.md) | Select patterns from observed design forces and review existing usage | ✓ | ✓ | optional |
| [`worklog`](plugins/worklog/README.md) | Log and diagnose failures, interruptions, and user corrections across Claude Code, Codex, and omp | ✓ | ✓ | optional |

These plugins behave differently by host:

- **Fluent Korean**: Claude Code edits through light, standard, and heavy multi-step paths; Codex and omp edit in a single call.
- **Review**: In omp, this plugin's review standard also applies to the built-in `/review`.
- **Memory Manager**: Codex and Claude Code share memory on the same machine. omp uses its own memory feature.
- **Worklog**: Claude Code and Codex record through hooks; omp records through a runtime extension. In Codex, logging starts only after you trust the worklog hook in `/hooks` after installing or updating.

## Updates

```sh
codex plugin marketplace upgrade sonsu-marketplace
claude plugin marketplace update sonsu-marketplace
claude plugin update dev-workflow@sonsu-marketplace
omp plugin marketplace update sonsu-marketplace
omp plugin upgrade
```

[Migrate from earlier omp configurations, fluent-languages, workflow, or engineering](docs/guides/migrating-from-earlier-versions.md) (Korean)

## Documentation

- [Documentation index](docs/README.md)
- [Skill composition and routing](docs/architecture/skill-routing.md)
- [Plugin distribution lifecycle](docs/architecture/plugin-lifecycle.md)
- [Licenses and sources by plugin](docs/reference/licenses-and-sources.md)

## Contributing

See the [plugin development guide](docs/guides/adding-a-plugin.md) for local setup, changes, and validation; report bugs or suggest improvements in [GitHub Issues](https://github.com/sonsu-lee/sonsu-marketplace/issues). Detailed guides are maintained in Korean.

## License

No license is currently declared for the repository as a whole. Check each plugin’s terms and original notices in [Licenses and sources](docs/reference/licenses-and-sources.md) (Korean).
