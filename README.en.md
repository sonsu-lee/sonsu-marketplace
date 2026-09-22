# Sonsu Marketplace

[한국어](README.md) · [English](README.en.md) · [日本語](README.ja.md)

Thin capability packs for Codex and Oh My Pi (OMP). The host owns general planning, implementation,
debugging, testing, Git, web research, editing, continuity, and memory. Install only the domain judgment or
external-artifact capability you need.

## Install

### Codex

```sh
codex plugin marketplace add sonsu-lee/sonsu-marketplace --ref main
codex plugin add code-review@sonsu-marketplace
codex plugin list --marketplace sonsu-marketplace
```

### Oh My Pi

```sh
omp plugin marketplace add sonsu-lee/sonsu-marketplace
omp plugin install --scope project code-review@sonsu-marketplace
omp plugin discover sonsu-marketplace
```

Choose `code-review`, `workflow`, `code-intelligence`, `product`, or a UI pack for the requested outcome.
General feature work, debugging, tests, branches/commits, web research, language editing, and session resume
do not require a marketplace plugin.

`code-intelligence` never runs an installer. Codex requires an exact `mcpls 0.6.0` and the relevant language
server on PATH, installed separately. OMP uses its native `lsp` capability and a language server; it does not
start the mcpls MCP. Language servers can execute project code or configuration, so enable the pack only in a
trusted workspace. Missing prerequisites produce `blocked`, never a text-search approximation.

## Plugins

Every plugin is version `1.0.0`.

| Plugin | Purpose | Skills |
| --- | --- | --- |
| [Code Review](plugins/code-review/README.md) | Focused read-only review and explicit PR review | `review-pr`, `review-failure-modes`, `review-maintainability`, `review-operability`, `review-overengineering`, `audit-overengineering` |
| [Code Intelligence](plugins/code-intelligence/README.md) | Semantic definitions, references, types, and renames | `semantic-code-intelligence` |
| [Workflow](plugins/workflow/README.md) | Ticket/PR artifacts and provider readback | `inspect-prs`, `repair-pr`, `to-ticket`, `ticket-lifecycle`, `to-pr` |
| [Developer Writing](plugins/developer-writing/README.md) | Evidence-based developer articles | `write-developer-blog` |
| [Prompting](plugins/prompting/README.md) | Copy-ready prompt artifacts | `prompt-builder` |
| [Product](plugins/product/README.md) | Discovery, evidence, domain rules, tests, and PRDs | `product-discovery`, `synthesize-product-evidence`, `product-domain-discovery`, `design-product-test`, `assess-product-test`, `to-prd` |
| [Figma Workflow](plugins/figma-workflow/README.md) | Figma screens, prototypes, and audits | `figma-product-design`, `figma-prototype-flow`, `figma-design-audit` |
| [Interface Design](plugins/interface-design/README.md) | General UI design and redesign | `design-interface`, `redesign-interface` |
| [Operations UI](plugins/operations-ui/README.md) | Operations UI design, redesign, audit, and Figma flow | `design-operations-ui`, `redesign-operations-ui`, `audit-operations-ui`, `figma-operations-flow` |
| [Design Patterns](plugins/design-patterns/README.md) | Pattern selection and explicit usage review | `select-design-patterns`, `review-pattern-usage` |

Both hosts load the same 31 skills. Only Codex declares the Figma `apps` metadata and Code Intelligence
`codex-mcp.json`; the OMP catalog contains neither connector declaration.

## Examples

- “Review reachable failure modes in this change.” → `code-review:review-failure-modes`
- “`$review-pr` review this PR with three independent reviewers and post one COMMENT.” → explicit `review-pr`
- “Find this symbol's definition and every reference through LSP.” → `semantic-code-intelligence`
- “Repair this PR's CI failure.” → `workflow:repair-pr`
- “Turn the approved decisions into a PRD draft.” → `product:to-prd`

A general “review this code” request uses host-native review and does not auto-select `review-pr`.

## Major migration

The removed names have no aliases or wrappers. Remove old installations, then install only the new packs you
need.

```sh
codex plugin remove engineering@sonsu-marketplace
codex plugin remove research@sonsu-marketplace
codex plugin remove fluent-languages@sonsu-marketplace
codex plugin remove memory-manager@sonsu-marketplace
codex plugin remove writing@sonsu-marketplace

omp plugin uninstall --scope <scope> engineering@sonsu-marketplace
omp plugin uninstall --scope <scope> research@sonsu-marketplace
omp plugin uninstall --scope <scope> fluent-languages@sonsu-marketplace
omp plugin uninstall --scope <scope> memory-manager@sonsu-marketplace
omp plugin uninstall --scope <scope> writing@sonsu-marketplace
```

Existing caches, `.sonsu/continuity`, and `.engineering` artifacts are not moved or deleted automatically.

## Update

```sh
codex plugin marketplace upgrade sonsu-marketplace
omp plugin marketplace update sonsu-marketplace
omp plugin upgrade --scope project code-review@sonsu-marketplace
```

Start a new Codex task or run OMP `/reload-plugins` after updating.

See [documentation](docs/README.md), the [plugin guide](docs/guides/adding-a-plugin.md), and
[licenses and sources](docs/reference/licenses-and-sources.md). The repository has no single root license;
check each package's terms and provenance.
