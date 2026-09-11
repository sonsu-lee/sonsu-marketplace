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

In Claude Code, register the same repository as a marketplace and install the plugin you need.

```sh
claude plugin marketplace add sonsu-lee/sonsu-marketplace
claude plugin install engineering@sonsu-marketplace
```

Replace the plugin name with an installation name from the table below. To list installed and available plugins, run:

```sh
claude plugin list --available --json
```

Claude Code packages use the same `skills/`, `hooks/`, and `scripts/`. Codex-only `apps` and UI metadata
are not copied into Claude manifests, so configure external tools such as Figma separately in the Claude
Code host and verify that their tools are available.

## Plugins

| Plugin | Purpose | Installation name |
| --- | --- | --- |
| [Engineering](plugins/engineering/README.md) | Design, implement, debug, and verify software changes | `engineering` |
| [Quality Engineering](plugins/quality-engineering/README.md) | Simplify code and review maintainability, failure paths, and operational issues | `quality-engineering` |
| [Workflow](plugins/workflow/) | Work with Git branches, commits, pushes, tickets, and GitHub PRs | `workflow` |
| [Writing](plugins/writing/) | Compose and edit Korean, Japanese, and English for the document's purpose, from structure to wording | `writing` |
| [Research](plugins/research/README.md) | Research multiple sources, verify facts, and write answers supported by evidence | `research` |
| [Prompting](plugins/prompting/README.md) | Create and improve prompts for Codex, ChatGPT, and the OpenAI API | `prompting` |
| [Product](plugins/product/README.md) | Explore product ideas, organize user evidence, test hypotheses, and write PRDs | `product` |
| [Figma Workflow](plugins/figma-workflow/README.md) | Create Figma product screens and clickable prototypes, and review design quality | `figma-workflow` |
| [Memory Manager](plugins/memory-manager/README.md) | Review and curate coding-agent memories on explicit invocation | `memory-manager` |
| [Operations UI](plugins/operations-ui/README.md) | Design, redesign, and audit state- and data-intensive B2B operational interfaces | `operations-ui` |
| [Design Patterns](plugins/design-patterns/README.md) | Select patterns from observed design forces and review existing usage | `design-patterns` |

Each plugin can be used independently. Follow the links above for included skills and detailed usage instructions.

## Usage examples

After installing the relevant plugin, try requests like these in Codex or Claude Code:

| Plugin | Example request |
| --- | --- |
| Engineering | “Find and fix the cause of this bug, then verify the fix using the reproduction steps.” |
| Quality Engineering | “Review the current diff for unnecessary abstractions and reachable failure paths.” |
| Workflow | “Commit the current changes and create a Draft PR.” |
| Writing | “Restructure this Japanese PR description so reviewers can understand the reason for the change and its behavior, while preserving its meaning and code identifiers.” |
| Research | “Compare the pricing and limits of these two services using official sources.” |
| Prompting | “Improve this prompt so I can use it directly in Codex.” |
| Product | “Extract the user problems and supporting evidence from these interview notes.” |
| Figma Workflow | “Review the Auto Layout and prototype connections in this Figma screen.” |
| Memory Manager | Codex: “$memory-manager Review the Codex memories for this project.”<br>Claude Code: “/memory-manager:memory-manager Review the Claude Code memories for this project.” |
| Operations UI | “Implement this order-operations screen from a Screen Contract and verify it with browser evidence.” |
| Design Patterns | “Decide whether this design needs a pattern and choose the smallest implementation shape.” |

Codex and Claude Code select skills based on your request and the descriptions of installed skills.
Memory Manager runs only when explicitly invoked with `$memory-manager` in Codex or
`/memory-manager:memory-manager` in Claude Code.
See the [skill routing documentation](docs/architecture/skill-routing.md) for how plugins share responsibilities when used together.

Research's Exa and Perplexity integrations are optional. It can also use available web tools, browsers, connectors, and local materials.
Figma Workflow requires the official Figma MCP connection and the tool's prerequisite skills for canvas operations.
See each plugin's documentation for setup and tool requirements.

## Updates

Fetch the latest snapshot of the registered Git marketplace:

```sh
codex plugin marketplace upgrade sonsu-marketplace
```

In Claude Code, refresh the marketplace listing, then update each installed plugin:

```sh
claude plugin marketplace update sonsu-marketplace
claude plugin update engineering@sonsu-marketplace
```

Repeat the second command for each installed plugin, replacing `engineering` with its name. For plugins
installed at `project` or `local` scope, specify the matching `--scope project` or `--scope local` option.

After installing or updating plugins, start a new Codex task or run `/reload-plugins` in Claude Code to
load the latest skill list.

<details>
<summary>Migrating from Fluent Languages or removing duplicate skills</summary>

Writing `0.2.0-beta.1` replaces Fluent Languages. Its `writing:writing` skill combines document
composition with guidance for the requested language. Install the new plugin in your host:

```sh
codex plugin add writing@sonsu-marketplace
```

```sh
claude plugin install writing@sonsu-marketplace
```

Remove the installed `fluent-languages` plugin to avoid duplicate skill discovery. A marketplace refresh
does not automatically rename installed plugins or continuity records. If an unfinished Fluent task has
a known record, restore its source and draft with the original plugin before removing it, then explicitly
hand the verified scope and evidence to a new Writing task. Do not automatically load another plugin's
records or reuse them by renaming them. See the [task continuity contract](docs/reference/task-continuity.md)
for the record boundaries.

If you installed standalone copies of `prompt-builder`, `product-discovery`, or `to-prd`, remove those
copies first to avoid duplicate skill names.

</details>

## Development and contributing

To modify or add plugins, clone the repository and register it as a local marketplace:

```sh
git clone https://github.com/sonsu-lee/sonsu-marketplace.git
cd sonsu-marketplace
codex plugin marketplace add .
codex plugin list --marketplace sonsu-marketplace

claude plugin marketplace add . --scope local
claude plugin list --available --json
```

The GitHub source and local path share the `sonsu-marketplace` identifier, so use one registration method per environment.

- [Adding a plugin](docs/guides/adding-a-plugin.md) — Directory layout and manifest registration
- [Documentation guide](docs/README.md) — Architecture, design decisions, and plugin contracts
- [Upstream update runbook](docs/runbooks/updating-upstream-plugin.md) — Update upstream content while keeping local changes separate
- [Evaluation tools](evals/) — Validate language output, skill routing, and plugin quality
- [GitHub Issues](https://github.com/sonsu-lee/sonsu-marketplace/issues) — Bug reports and improvement suggestions

<details>
<summary>Repository structure and validation commands</summary>

### Repository structure

```text
sonsu-marketplace/
├── .agents/plugins/marketplace.json  # Plugin catalog
├── .claude-plugin/marketplace.json   # Claude Code plugin catalog
├── plugins/
│   └── <plugin>/
│       ├── .codex-plugin/plugin.json # Plugin metadata
│       ├── .claude-plugin/plugin.json # Generated Claude Code metadata
│       └── skills/                  # Skills and reference materials
├── docs/                            # Maintenance documentation
└── evals/                           # Evaluation fixtures and validation tools
```

### Validation

Run these static checks from the repository root:

```sh
find .agents .claude-plugin plugins evals -name '*.json' -print0 \
  | xargs -0 -n1 python3 -m json.tool >/dev/null
python3 scripts/render-claude-compat.py --check
python3 scripts/render-writing.py --check
python3 "${CODEX_HOME:-$HOME/.codex}/skills/.system/skill-creator/scripts/quick_validate.py" \
  plugins/writing/skills/writing
python3 evals/language-style/eval.py validate
python3 -m unittest -v evals/language-style/test_eval.py
claude plugin validate . --strict
git diff --check
```

These commands check JSON syntax, whether generated Workflow materials match their Writing sources,
skill metadata, and the structure of evaluation fixtures and the runner.
Actual model skill selection and output quality require separate validation. If you change a plugin's structure,
also verify marketplace registration, plugin installation, and skill availability in isolated Codex and Claude Code environments.

The platform-specific formats follow the [official OpenAI plugin packaging documentation](https://developers.openai.com/plugins/build/plugins)
and the [official Anthropic marketplace documentation](https://code.claude.com/docs/en/plugin-marketplaces).

</details>

## Licenses and sources

No root-level license is currently declared for the repository as a whole. Licensing and source information vary by plugin:

- Engineering is covered by the [MIT License](plugins/engineering/LICENSE).
- Quality Engineering is based on several pinned upstream sources and retains the [Apache-2.0 License](plugins/quality-engineering/LICENSE), [NOTICE](plugins/quality-engineering/NOTICE), [source mapping](plugins/quality-engineering/UPSTREAM.md), and [original MIT notices](plugins/quality-engineering/THIRD_PARTY_NOTICES.md).
- Workflow currently has no separately declared license. Bundled Writing guidance and templates retain their [MIT notice](plugins/workflow/WRITING_LICENSE.md).
- Prompting currently has no separately declared license.
- Product currently has no separately declared license.
- Memory Manager was independently authored and currently has no separately declared license. Design references are recorded in [UPSTREAM.md](plugins/memory-manager/UPSTREAM.md).
- Operations UI was independently authored without copying external UI code or assets and currently has no separately declared license. Design references are recorded in [UPSTREAM.md](plugins/operations-ui/UPSTREAM.md).
- Design Patterns indexes only pattern names and source locations; its selection and review contracts are independently authored and currently have no separately declared license. Inclusion and source terms are recorded in [UPSTREAM.md](plugins/design-patterns/UPSTREAM.md).
- Figma Workflow was independently authored without copying external files and currently has no separately declared license. Consulted sources and the policy against copying external files are documented in [UPSTREAM.md](plugins/figma-workflow/UPSTREAM.md).
- Writing retains the licensing and source attribution inherited from Fluent Languages in [LICENSE](plugins/writing/LICENSE), [UPSTREAM.md](plugins/writing/UPSTREAM.md), and [THIRD_PARTY_NOTICES.md](plugins/writing/THIRD_PARTY_NOTICES.md).
- Research's upstream baseline had no license file that could be verified, and permission to use it is not assumed. The baseline commit and included scope are recorded in [UPSTREAM.md](plugins/research/UPSTREAM.md).
