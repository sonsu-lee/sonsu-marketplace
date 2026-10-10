# Sonsu Marketplace

[한국어](README.md) · [English](README.en.md) · [日本語](README.ja.md)

A collection of Codex, Claude Code, and omp plugins for development, research, product planning, and writing.

## Installation

### Codex

Register once with a CLI that supports `codex plugin`, then install one plugin or all plugins. When the list shows the installation status, start a new Codex task.

```sh
codex plugin marketplace add sonsu-lee/sonsu-marketplace --ref main
# Install one plugin
codex plugin add engineering@sonsu-marketplace
# To install all, use this instead of the single install above
for plugin in engineering workflow fluent-korean fluent-english fluent-japanese writing research prompting product memory-manager design-patterns design career worklog; do codex plugin add "$plugin@sonsu-marketplace"; done
codex plugin marketplace list
codex plugin list --marketplace sonsu-marketplace
```

### Claude Code

Register the marketplace once, then install one plugin or all plugins. Check the installation status in the list and start a new session.

```sh
claude plugin marketplace add sonsu-lee/sonsu-marketplace
# Install one plugin
claude plugin install engineering@sonsu-marketplace
# To install all, use this instead of the single install above
for plugin in engineering workflow fluent-korean fluent-english fluent-japanese writing research prompting product memory-manager design-patterns design career worklog; do claude plugin install "$plugin@sonsu-marketplace"; done
claude plugin marketplace list
claude plugin list
```

### omp

Install the default six plugins; Worklog and Design Patterns are optional. Only if you choose to enable automatic updates, merge the YAML below into the existing `marketplace:` section of `~/.omp/agent/config.yml`.

<!-- omp-preset:start -->
```sh
omp plugin marketplace add sonsu-lee/sonsu-marketplace
for plugin in workflow fluent-korean fluent-english fluent-japanese design career; do omp plugin install "$plugin@sonsu-marketplace"; done
```

```yaml
marketplace:
  autoUpdate: auto
```
<!-- omp-preset:end -->

```sh
# Optional install
omp plugin install worklog@sonsu-marketplace
omp plugin install design-patterns@sonsu-marketplace
omp plugin list
```

## Plugins

Each plugin works independently; follow its link for details (Codex and Claude Code: all 14; omp: the default six and opt-in Worklog and Design Patterns).

| Plugin | Purpose | Installation name |
| --- | --- | --- |
| [Engineering](plugins/engineering/README.md) | Design, implement, verify, simplify, and review software changes | `engineering` |
| [Workflow](plugins/workflow) | Work with Git branches, commits, pushes, tickets, and GitHub PRs | `workflow` |
| [Fluent Korean](plugins/fluent-korean) | Apply drafting rules to new Korean text and edit AI-sounding or translationese passages in existing Korean text with `im-not-ai` as a source | `fluent-korean` |
| [Fluent English](plugins/fluent-english) | Draft, edit, and review everyday and technical English with `better-writing` as a source | `fluent-english` |
| [Fluent Japanese](plugins/fluent-japanese) | Draft and edit everyday and technical Japanese; score documents with `natural-japanese` as a source | `fluent-japanese` |
| [Writing](plugins/writing) | Select information, choose where it belongs, and organize writing for the reader and purpose | `writing` |
| [Research](plugins/research/README.md) | Research multiple sources, verify facts, and write answers supported by evidence | `research` |
| [Prompting](plugins/prompting/README.md) | Create and improve prompts for Codex, ChatGPT, OpenAI API, Claude Code, and Anthropic API | `prompting` |
| [Product](plugins/product/README.md) | Explore product ideas, organize user evidence, test hypotheses, and write PRDs | `product` |
| [Memory Manager](plugins/memory-manager/README.md) | Shared local memory for recall, capture, and maintenance in Codex and Claude Code | `memory-manager` |
| [Design](plugins/design/README.md) | Design, redesign, and audit general and operations interfaces through Figma or code, and find design references | `design` |
| [Design Patterns](plugins/design-patterns/README.md) | Select patterns from observed design forces and review existing usage | `design-patterns` |
| [Career](plugins/career/README.md) | Developer career record, US-style resume, rirekisho and shokumu keirekisho drafting, interview prep, mock interviews, and retros | `career` |
| [Worklog](plugins/worklog/README.md) | Log and diagnose failures, interruptions, and user corrections across Claude Code, Codex, and omp | `worklog` |

## Usage examples

After installing the relevant plugin, make a request in Codex or Claude Code (direct invocation examples: Claude Code `/engineering:review`, omp `/skill:commit`).

| Plugin | Example request |
| --- | --- |
| Engineering | “Fix and verify this bug, or review the current diff for unnecessary abstractions and reachable failure paths.” |
| Workflow | “Commit the current changes and create a Draft PR.” |
| Fluent Japanese | “Make this Japanese technical explanation read naturally while preserving its meaning and code identifiers.” |
| Writing | “Select and summarize what the README needs from this material, and update the existing documents with the details.” |
| Research | “Compare the pricing and limits of these two services using official sources.” |
| Prompting | “Improve this prompt so I can use it directly in Codex.” |
| Product | “Extract the user problems and supporting evidence from these interview notes.” |
| Memory Manager | “`$memory-capture` Save this decision as a memory for this project.” |
| Design | “Design a mobile signup flow in Figma, or redesign this operations screen directly in code.” or “Find sign-in screen references with their sources.” |
| Design Patterns | “Decide whether this design needs a pattern and choose the smallest implementation shape.” |
| Career | “Build a one-page English resume tailored to this JD, then run a mock interview for next week's first-round interview.” |

The host selects skills based on your request and the descriptions of installed skills.

## Updates

```sh
codex plugin marketplace upgrade sonsu-marketplace
claude plugin marketplace update sonsu-marketplace
claude plugin update engineering@sonsu-marketplace
omp plugin marketplace update sonsu-marketplace
omp plugin upgrade
```

[Migrate from earlier omp configurations or fluent-languages](docs/guides/migrating-from-earlier-versions.md) (Korean)

## Documentation

- [Documentation index](docs/README.md)
- [Skill composition and routing](docs/architecture/skill-routing.md)
- [Plugin distribution lifecycle](docs/architecture/plugin-lifecycle.md)
- [Licenses and sources by plugin](docs/reference/licenses-and-sources.md)

## Contributing

See the [plugin development guide](docs/guides/adding-a-plugin.md) for local setup, changes, and validation; report bugs or suggest improvements in [GitHub Issues](https://github.com/sonsu-lee/sonsu-marketplace/issues). Detailed guides are maintained in Korean.

## License

No license is currently declared for the repository as a whole. Check each plugin’s terms and original notices in [Licenses and sources](docs/reference/licenses-and-sources.md) (Korean).
