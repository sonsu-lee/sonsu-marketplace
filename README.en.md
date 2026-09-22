# Sonsu Marketplace

[한국어](README.md) · [English](README.en.md) · [日本語](README.ja.md)

A collection of Codex and Oh My Pi plugins for development, research, product planning, and writing.
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

### Oh My Pi

In Oh My Pi (OMP), register the OMP catalog and install each plugin at project or user scope:

```sh
omp plugin marketplace add sonsu-lee/sonsu-marketplace
omp plugin install --scope project engineering@sonsu-marketplace
```

List the available plugins with:

```sh
omp plugin discover sonsu-marketplace
```

OMP loads the shared `skills/` tree from each plugin and exposes unprefixed skill names such as
`review-quality`. Codex-specific hooks and app connections declared under `.codex-plugin` do not run
in OMP; those automation surfaces still require Codex.

## Plugins

| Plugin | Purpose | Installation name |
| --- | --- | --- |
| [Engineering](plugins/engineering/README.md) | Design, implement, verify, simplify, and review software changes | `engineering` |
| [Workflow](plugins/workflow/) | Work with Git branches, commits, pushes, tickets, and GitHub PRs | `workflow` |
| [Fluent Languages](plugins/fluent-languages/) | Write natural Korean, Japanese, and English while preserving technical content | `fluent-languages` |
| [Writing](plugins/writing/) | Select information, choose where it belongs, and organize writing for the reader and purpose | `writing` |
| [Research](plugins/research/README.md) | Research multiple sources, verify facts, and write answers supported by evidence | `research` |
| [Prompting](plugins/prompting/README.md) | Create and improve prompts for Codex, ChatGPT, and the OpenAI API | `prompting` |
| [Product](plugins/product/README.md) | Explore product ideas, organize user evidence, test hypotheses, and write PRDs | `product` |
| [Figma Workflow](plugins/figma-workflow/README.md) | Create Figma product screens and clickable prototypes, and review design quality | `figma-workflow` |
| [Memory Manager](plugins/memory-manager/README.md) | Review and curate coding-agent memories on explicit invocation | `memory-manager` |
| [Interface Design](plugins/interface-design/README.md) | Web and mobile interface design, redesign, and information asset verification | `interface-design` |
| [Operations UI](plugins/operations-ui/README.md) | Design, redesign, and audit state- and data-intensive B2B operational interfaces | `operations-ui` |
| [Design Patterns](plugins/design-patterns/README.md) | Select patterns from observed design forces and review existing usage | `design-patterns` |

Each plugin can be used independently. Follow the links above for included skills and detailed usage instructions.

Writing selects and places information and organizes the text, Fluent Languages handles language-specific
expression, Workflow handles templates and publication for new tickets and PRs, and Engineering publishes
review results on existing PRs. See the
[skill routing documentation](docs/architecture/skill-routing.md) for how to use them together.

## Usage examples

After installing the relevant plugin, try requests like these in Codex or OMP:

| Plugin | Example request |
| --- | --- |
| Engineering | “Fix and verify this bug, or review the current diff for unnecessary abstractions and reachable failure paths.” |
| Workflow | “Commit the current changes and create a Draft PR.” |
| Fluent Languages | “Make this Japanese technical explanation read naturally while preserving its meaning and code identifiers.” |
| Writing | “Select and summarize what the README needs from this material, and update the existing documents with the details.” |
| Research | “Compare the pricing and limits of these two services using official sources.” |
| Prompting | “Improve this prompt so I can use it directly in Codex.” |
| Product | “Extract the user problems and supporting evidence from these interview notes.” |
| Figma Workflow | “Review the Auto Layout and prototype connections in this Figma screen.” |
| Memory Manager | Codex: “`$memory-manager` Review the Codex memories for this project.” / OMP: “`/skill:memory-manager` Review the Codex memories for this project.” |
| Interface Design | “Design a mobile signup flow and improve the chart presentation.” |
| Operations UI | “Implement this order-operations screen from a Design Decision Contract and verify it with DQ gates and browser evidence.” |
| Design Patterns | “Decide whether this design needs a pattern and choose the smallest implementation shape.” |

Codex and OMP select skills based on your request and the descriptions of installed skills.
Memory Manager runs only when explicitly invoked with `$memory-manager` in Codex or `/skill:memory-manager` in OMP.

Research's Exa and Perplexity integrations are optional. It can also use available web tools, browsers, connectors, and local materials.
Figma Workflow requires the official Figma MCP connection and the tool's prerequisite skills for canvas operations.
See each plugin's documentation for setup and tool requirements.

## Updates

In Codex, fetch the latest snapshot of the registered Git marketplace:

```sh
codex plugin marketplace upgrade sonsu-marketplace
```

In OMP, refresh the catalog and then upgrade an installed plugin:

```sh
omp plugin marketplace update sonsu-marketplace
omp plugin upgrade --scope project engineering@sonsu-marketplace
```

Start a new Codex task after an update. In OMP, run `/reload-plugins` or restart the session to load the latest skills.

If you installed `fluent-languages` from another marketplace or standalone copies of `prompt-builder`,
`product-discovery`, or `to-prd`, remove those copies first to avoid duplicate skill names.

## Development and contributing

The [plugin development guide](docs/guides/adding-a-plugin.md) covers local setup, modifying and adding
plugins, and validation. The detailed guides below are maintained in Korean.

- [Architecture overview](docs/architecture/overview.md) — Repository structure and loading boundaries
- [Upstream update runbook](docs/runbooks/updating-upstream-plugin.md) — Update upstream content while keeping local changes separate
- [Evaluation tools](evals/) — Validate language output, skill routing, and plugin quality
- [GitHub Issues](https://github.com/sonsu-lee/sonsu-marketplace/issues) — Bug reports and improvement suggestions

## Licenses and sources

No license is currently declared for the repository as a whole. Check the terms and original notices for
each plugin in [Licenses and sources by plugin](docs/reference/licenses-and-sources.md) (Korean).
