# Sonsu Marketplace

[한국어](README.md) · [English](README.en.md) · [日本語](README.ja.md)

A collection of Codex, Claude Code, and omp plugins for development, research, product planning, and writing.
Install the plugins you need, then work with your coding agent as usual.

[Installation](#installation) · [Plugins](#plugins) · [Usage examples](#usage-examples) · [Documentation](docs/README.md)

## Installation

### Codex

Register the GitHub marketplace once using a Codex CLI version that supports `codex plugin`.
Skip this step if it is already registered.

```sh
codex plugin marketplace add sonsu-lee/sonsu-marketplace --ref main
```

Install only the plugins you need. For example, use Engineering for software development:

```sh
codex plugin add engineering@sonsu-marketplace
```

For another plugin, use its installation name from the [table below](#plugins).
To install all 12 plugins, run:

```sh
for plugin in \
  engineering workflow fluent-korean fluent-english fluent-japanese \
  writing research prompting product memory-manager design-patterns design
do
  codex plugin add "$plugin@sonsu-marketplace"
done
```

Check the registered sources and each plugin's installation status, then start a new Codex task:

```sh
codex plugin marketplace list
codex plugin list --marketplace sonsu-marketplace
```

When you open this repository in the Codex desktop app, its local catalog at
`.agents/plugins/marketplace.json` may also appear. A registered Git source with the same name
can hide local plugin changes, so seeing both entries does not confirm that the local copy is
loaded. Test the checkout without the Git source using the [local setup steps](docs/guides/adding-a-plugin.md#로컬-개발-환경).

### Claude Code

Register the GitHub marketplace once. Skip this step if it is already registered:

```sh
claude plugin marketplace add sonsu-lee/sonsu-marketplace
```

Install only the plugins you need. For example, to install Engineering:

```sh
claude plugin install engineering@sonsu-marketplace
```

To install all 12 plugins from the [table below](#plugins), run:

```sh
for plugin in \
  engineering workflow fluent-korean fluent-english fluent-japanese \
  writing research prompting product memory-manager design-patterns design
do
  claude plugin install "$plugin@sonsu-marketplace"
done
```

Check the registered marketplaces and installed plugins:

```sh
claude plugin marketplace list
claude plugin list
```

To test a local checkout, run `claude plugin marketplace add "$(pwd -P)"` from the repository
root. Both sources use the name `sonsu-marketplace`, so choose the one you intend to use.
Invoke skills as `/engineering:review`. Start a new session after installation or update. Codex connectors and
Claude Code MCP connections require separate configuration.

### omp

The omp catalog, `.omp-plugin/marketplace.json`, distributes five plugins: `workflow`, `fluent-korean`,
`fluent-english`, `fluent-japanese`, and `design`. Native omp features own development execution,
task, todo, session, review, and memory. Test local changes in the isolated environment described in the
[development guide](docs/guides/adding-a-plugin.md).

Register the marketplace, install the five plugins, and merge the YAML into the existing `marketplace:`
section of `~/.omp/agent/config.yml`.

<!-- omp-preset:start -->
```sh
omp plugin marketplace add sonsu-lee/sonsu-marketplace
for plugin in workflow fluent-korean fluent-english fluent-japanese design; do omp plugin install "$plugin@sonsu-marketplace"; done
```

```yaml
marketplace:
  autoUpdate: auto
```
<!-- omp-preset:end -->

`marketplace.autoUpdate: auto` attempts to refresh catalogs older than 24 hours at omp startup.
Automatic updates of installed plugins require a version increase for that plugin in the catalog.
This setting does not continuously watch `main` or reload changes into an active session.

Invoke skills without a plugin prefix, for example `/skill:commit`. The default configuration requires
no custom role model overrides. Fluent Korean uses a single call with the current host model; its omp
package does not provide Claude Code's multistep or strict mode, or fixed Opus agents. Existing English
and Japanese skills and agents, Workflow's commit/push/PR authority boundaries, and Design's quality
contracts, profiles, and native tool prerequisites remain in place.

Design, Workflow, and Fluent Korean use generated `./plugins/<name>/omp` packages. English and Japanese
use their existing `./plugins/<name>` packages. The omp packages contain no custom runtime extension,
hook, evidence gate, or `task-continuity.py`. Native todo and session features handle continuity without
new `.sonsu` records. See the [distribution lifecycle](docs/architecture/plugin-lifecycle.md).

| Responsibility | Owner | Distribution |
| --- | --- | --- |
| Development execution, task, todo, session, review | Native omp | Host features |
| Git, ticket, and PR authority and artifacts | Workflow | Default five plugins |
| Language quality and preservation rules | Fluent Korean, English, Japanese | Default five plugins |
| UI, prototype, and handoff quality; native tool prerequisites | Design | Default five plugins |
| External research, product exploration, writing structure | Research, Product, Writing | Optional candidates, excluded from the default catalog |

Before adding Research, Product, or Writing, verify the required domain and current native tool contract.
Engineering's omp profiles remain available for existing direct installations and do not configure the default five plugins.

#### Migrating from an earlier omp configuration

If you used the earlier eleven-plugin configuration or eight-plugin preset, uninstall any installed
plugins from the following list in omp. Keep Codex and Claude Code installations in place.

```sh
for plugin in engineering writing research prompting product design-patterns memory-manager operations-ui interface-design figma-workflow; do omp plugin uninstall "$plugin@sonsu-marketplace"; done
```

Remove only the `skills.ignoredSkills`, `task.disabledAgents`, and `task.agentModelOverrides` entries added
for the old preset. Preserve unrelated user settings. Install or update the five plugins above, then end
the session and restart omp to unload old hooks and agents. Do not edit cache files manually or delete
existing `.sonsu` or `.engineering` records.

## Plugins

The following is the full Codex and Claude Code catalog. omp distributes only the five plugins above.

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
| [Memory Manager](plugins/memory-manager/README.md) | Shared local memory for recall, capture, and maintenance in Codex and Claude Code | `memory-manager` |
| [Design](plugins/design/README.md) | Design, redesign, and audit general and operations interfaces through Figma or code | `design` |
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
| Memory Manager | “`$memory-capture` Save this decision as a memory for this project.” |
| Design | “Design a mobile signup flow in Figma, or redesign this operations screen directly in code.” |
| Design Patterns | “Decide whether this design needs a pattern and choose the smallest implementation shape.” |

The host selects skills based on your request and the descriptions of installed skills.
Memory Manager may select `$memory-recall` for relevant work and uses `$memory-capture` for explicit
save requests. Invoke `$memory-maintain` or `$memory-promote` explicitly for cleanup or a skill draft.
Claude Code uses names such as `/memory-manager:memory-capture`.

Research's Exa and Perplexity integrations are optional. It can also use available web tools, browsers, connectors, and local materials.
Design canvas work requires the official Figma MCP connection and the tool's prerequisite skills for canvas operations.
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
