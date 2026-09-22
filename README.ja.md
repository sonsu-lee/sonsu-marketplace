# Sonsu Marketplace

[한국어](README.md) · [English](README.en.md) · [日本語](README.ja.md)

Codex と Oh My Pi（OMP）の標準的な計画・実装・デバッグ・検証の上に、ドメイン判断と外部
artifact 契約だけを追加する薄い capability pack 集です。必要な pack だけをインストールします。

## インストール

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

目的に応じて `code-review`、`workflow`、`code-intelligence`、`product`、UI pack を選びます。
一般的な機能実装、デバッグ、テスト、branch/commit、Web 調査、文章校正、session 再開には
marketplace plugin は不要です。

`code-intelligence` は installer を実行しません。Codex では plugin とは別に PATH 上の exact
`mcpls 0.6.0` と対象 language server が必要です。OMP は native `lsp` と language server を使い、
mcpls MCP は起動しません。language server は project code/config を実行し得るため、信頼した
workspace でだけ有効化してください。前提がなければ text search で推測せず `blocked` になります。

## Plugin

全 plugin の version は `1.0.0` です。

| Plugin | 用途 | Skills |
| --- | --- | --- |
| [Code Review](plugins/code-review/README.md) | focused read-only review と明示的 PR review | `review-pr`, `review-failure-modes`, `review-maintainability`, `review-operability`, `review-overengineering`, `audit-overengineering` |
| [Code Intelligence](plugins/code-intelligence/README.md) | semantic definition/reference/type/rename | `semantic-code-intelligence` |
| [Workflow](plugins/workflow/README.md) | ticket/PR artifact と provider readback | `inspect-prs`, `repair-pr`, `to-ticket`, `ticket-lifecycle`, `to-pr` |
| [Developer Writing](plugins/developer-writing/README.md) | 根拠に基づく開発者向け記事 | `write-developer-blog` |
| [Prompting](plugins/prompting/README.md) | コピー可能な prompt artifact | `prompt-builder` |
| [Product](plugins/product/README.md) | 探索・根拠・domain・検証・PRD | `product-discovery`, `synthesize-product-evidence`, `product-domain-discovery`, `design-product-test`, `assess-product-test`, `to-prd` |
| [Figma Workflow](plugins/figma-workflow/README.md) | Figma 画面・prototype・audit | `figma-product-design`, `figma-prototype-flow`, `figma-design-audit` |
| [Interface Design](plugins/interface-design/README.md) | 一般 UI の設計・再設計 | `design-interface`, `redesign-interface` |
| [Operations UI](plugins/operations-ui/README.md) | 運用 UI の設計・再設計・audit・Figma flow | `design-operations-ui`, `redesign-operations-ui`, `audit-operations-ui`, `figma-operations-flow` |
| [Design Patterns](plugins/design-patterns/README.md) | pattern 選択と明示的 usage review | `select-design-patterns`, `review-pattern-usage` |

両 host は同じ 31 skills を読み込みます。Figma `apps` と Code Intelligence `codex-mcp.json` を
宣言するのは Codex だけで、OMP catalog には connector metadata を含めません。

## 使用例

- 「この変更の到達可能な failure mode をレビューして」→ `review-failure-modes`
- 「`$review-pr` で3人の独立 reviewer が確認し COMMENT を1件投稿して」→ explicit `review-pr`
- 「この symbol の定義と全 reference を LSP で探して」→ `semantic-code-intelligence`
- 「この PR の CI failure を修復して」→ `workflow:repair-pr`
- 「承認済み決定を PRD draft にして」→ `product:to-prd`

一般的な「コードレビューして」は host-native review が処理し、`review-pr` は自動選択しません。

## Major migration

削除された名前の alias/wrapper はありません。旧 plugin を削除し、必要な新 pack だけを
インストールしてください。

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

既存 cache、`.sonsu/continuity`、`.engineering` artifact は自動移動・削除しません。

## 更新

```sh
codex plugin marketplace upgrade sonsu-marketplace
omp plugin marketplace update sonsu-marketplace
omp plugin upgrade --scope project code-review@sonsu-marketplace
```

更新後は Codex の新規 task、または OMP の `/reload-plugins` で再読込します。

[ドキュメント](docs/README.md)、[plugin 開発ガイド](docs/guides/adding-a-plugin.md)、
[license と出典](docs/reference/licenses-and-sources.md)を参照してください。repository 全体の共通
root license はないため、各 package の条件を確認してください。
