# Sonsu Marketplace

[한국어](README.md) · [English](README.en.md) · [日本語](README.ja.md)

A collection of Codex and Claude Code plugins for development, research, product planning, and writing.
Install the plugins you need, then work with your coding agent as usual.

[Installation](#installation) · [Plugins](#plugins) · [Usage examples](#usage-examples) · [Documentation](docs/README.md)

## Installation

### Codex

Register the marketplace using a Codex CLI version that supports `codex plugin`.

```sh
codex plugin marketplace add sonsu-lee/sonsu-marketplace --ref main
```

Install a plugin that fits your work. For example, use Engineering for software development:

```sh
codex plugin add engineering@sonsu-marketplace
```

To install another plugin, use its installation name from the table below. For example, to install Workflow:

```sh
codex plugin add workflow@sonsu-marketplace
```

Start a new Codex task after installation. To list the plugins in the marketplace, run:

```sh
codex plugin list --marketplace sonsu-marketplace
```

### Claude Code

Register the marketplace and install the plugins you need:

```sh
claude plugin marketplace add sonsu-lee/sonsu-marketplace
claude plugin install engineering@sonsu-marketplace
claude plugin list
```

For a local checkout, pass its absolute path to `claude plugin marketplace add`. Invoke skills
as `/engineering:review`. Start a new session after installation or update. Codex connectors and
Claude Code MCP connections require separate configuration.

## Plugins

| Plugin | Purpose | Installation name |
| --- | --- | --- |
| [Engineering](plugins/engineering/README.md) | Design, implement, verify, simplify, and review software changes | `engineering` |
| [Workflow](plugins/workflow) | Work with Git branches, commits, pushes, tickets, and GitHub PRs | `workflow` |
| [Fluent Korean](plugins/fluent-korean) | Edit AI-sounding everyday and technical Korean with `im-not-ai` as a source | `fluent-korean` |
| [Fluent English](plugins/fluent-english) | Draft, edit, and review everyday and technical English with `better-writing` as a source | `fluent-english` |
| [Fluent Japanese](plugins/fluent-japanese) | Draft and edit everyday and technical Japanese; score documents with `natural-japanese` as a source | `fluent-japanese` |
| [Writing](plugins/writing) | Select information, choose where it belongs, and organize writing for the reader and purpose | `writing` |
| [Research](plugins/research/README.md) | Research multiple sources, verify facts, and write answers supported by evidence | `research` |
| [Prompting](plugins/prompting/README.md) | Create and improve prompts for Codex, ChatGPT, OpenAI API, Claude Code, and Anthropic API | `prompting` |
| [Product](plugins/product/README.md) | Explore product ideas, organize user evidence, test hypotheses, and write PRDs | `product` |
| [Figma Workflow](plugins/figma-workflow/README.md) | Create Figma product screens and clickable prototypes, and review design quality | `figma-workflow` |
| [Memory Manager](plugins/memory-manager/README.md) | Review and curate coding-agent memories on explicit invocation | `memory-manager` |
| [Interface Design](plugins/interface-design/README.md) | Web and mobile interface design, redesign, and information asset verification | `interface-design` |
| [Operations UI](plugins/operations-ui/README.md) | Design, redesign, and audit state- and data-intensive B2B operational interfaces | `operations-ui` |
| [Design Patterns](plugins/design-patterns/README.md) | Select patterns from observed design forces and review existing usage | `design-patterns` |

Each plugin can be used independently. Follow the links above for included skills and detailed usage instructions.

Writing selects and places information and organizes the text, each Fluent plugin handles its language's
expression, Workflow handles templates and publication for new tickets and PRs, and Engineering publishes
review results on existing PRs. See the
[skill routing documentation](docs/architecture/skill-routing.md) for how to use them together.

## Usage examples

After installing the relevant plugin, try requests like these in Codex:

| Plugin | Example request |
| --- | --- |
| Engineering | “Fix and verify this bug, or review the current diff for unnecessary abstractions and reachable failure paths.” |
| Workflow | “Commit the current changes and create a Draft PR.” |
| Fluent Japanese | “Make this Japanese technical explanation read naturally while preserving its meaning and code identifiers.” |
| Writing | “Select and summarize what the README needs from this material, and update the existing documents with the details.” |
| Research | “Compare the pricing and limits of these two services using official sources.” |
| Prompting | “Improve this prompt so I can use it directly in Codex.” |
| Product | “Extract the user problems and supporting evidence from these interview notes.” |
| Figma Workflow | “Review the Auto Layout and prototype connections in this Figma screen.” |
| Memory Manager | “`$memory-manager` Review the Codex memories for this project.” |
| Interface Design | “Design a mobile signup flow and improve the chart presentation.” |
| Operations UI | “Implement this order-operations screen from a Design Decision Contract and verify it with DQ gates and browser evidence.” |
| Design Patterns | “Decide whether this design needs a pattern and choose the smallest implementation shape.” |

The host selects skills based on your request and the descriptions of installed skills.
Memory Manager runs only when explicitly invoked with `$memory-manager` in Codex or
`/memory-manager:memory-manager` in Claude Code.

Research's Exa and Perplexity integrations are optional. It can also use available web tools, browsers, connectors, and local materials.
Figma Workflow requires the official Figma MCP connection and the tool's prerequisite skills for canvas operations.
See each plugin's documentation for setup and tool requirements.

## Updates

In Codex, fetch the latest snapshot of the registered Git marketplace:

```sh
codex plugin marketplace upgrade sonsu-marketplace
```

Start a new Codex task after an update to load the latest skills.

In Claude Code, update the marketplace and each installed plugin, then start a new session:

```sh
claude plugin marketplace update sonsu-marketplace
claude plugin update engineering@sonsu-marketplace
```

If the previous `fluent-languages` plugin is installed, remove it before installing the language plugins
to avoid overlapping language guidance. The new skill IDs are `fluent-korean:fluent-korean`,
`fluent-english:fluent-english`, and `fluent-japanese:fluent-japanese`. English supports drafting, editing, and review; Japanese supports drafting, editing, and document scoring for everyday and technical prose. Korean targets AI-sounding or translationese passages in existing text. Existing continuity records are preserved; [recover ongoing work manually](docs/reference/task-continuity.md).

```sh
codex plugin remove fluent-languages@sonsu-marketplace
codex plugin add fluent-korean@sonsu-marketplace
codex plugin add fluent-english@sonsu-marketplace
codex plugin add fluent-japanese@sonsu-marketplace
```

In Claude Code, run `claude plugin uninstall fluent-languages@sonsu-marketplace`, then install the
languages you need with `claude plugin install <name>@sonsu-marketplace`. Also check for duplicate
skills from other marketplaces or standalone copies of `prompt-builder`, `product-discovery`, or `to-prd`.

## Development and contributing

The [plugin development guide](docs/guides/adding-a-plugin.md) covers local setup, modifying and adding
plugins, and validation. The detailed guides below are maintained in Korean.

- [Architecture overview](docs/architecture/overview.md) — Repository structure and loading boundaries
- [Upstream update runbook](docs/runbooks/updating-upstream-plugin.md) — Update upstream content while keeping local changes separate
- [Evaluation tools](evals) — Validate language output, skill routing, and plugin quality
- [GitHub Issues](https://github.com/sonsu-lee/sonsu-marketplace/issues) — Bug reports and improvement suggestions

## Licenses and sources

No license is currently declared for the repository as a whole. Check the terms and original notices for
each plugin in [Licenses and sources by plugin](docs/reference/licenses-and-sources.md) (Korean).
