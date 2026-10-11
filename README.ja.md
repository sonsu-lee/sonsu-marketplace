# Sonsu Marketplace

[한국어](README.md) · [English](README.en.md) · [日本語](README.ja.md)

開発、リサーチ、プロダクト企画、文章作成に使えるCodex・Claude Code・ompプラグイン集です。

ホストごとに提供するプラグインが異なります。CodexとClaude Codeには全15件、ompには基本7件と任意6件を提供します。ompは開発の実行とメモリを独自の機能で扱うため、Dev WorkflowとMemory Managerはompに配布していません。

## インストール

マーケットプレイスを一度登録し、必要なプラグインをインストールします。一覧でインストール状態を確認してから、新しいセッションを開始してください。ホストごとにインストールできるプラグインは[プラグイン](#プラグイン)の表で確認できます。

### Codex

`codex plugin` に対応したCLIが必要です。

```sh
codex plugin marketplace add sonsu-lee/sonsu-marketplace --ref main
# 一つだけインストール
codex plugin add dev-workflow@sonsu-marketplace
# 全件をインストールする場合は上の単独インストールの代わりに実行
for plugin in git tickets review dev-workflow fluent-korean fluent-english fluent-japanese writing research prompting product memory-manager design-patterns design worklog; do codex plugin add "$plugin@sonsu-marketplace"; done
codex plugin marketplace list
codex plugin list --marketplace sonsu-marketplace
```

### Claude Code

```sh
claude plugin marketplace add sonsu-lee/sonsu-marketplace
# 一つだけインストール
claude plugin install dev-workflow@sonsu-marketplace
# 全件をインストールする場合は上の単独インストールの代わりに実行
for plugin in git tickets review dev-workflow fluent-korean fluent-english fluent-japanese writing research prompting product memory-manager design-patterns design worklog; do claude plugin install "$plugin@sonsu-marketplace"; done
claude plugin marketplace list
claude plugin list
```

### omp

基本7件をインストールし、任意6件は必要なときに個別にインストールします。自動更新を新たに有効にする場合だけ、下のYAMLを `~/.omp/agent/config.yml` の既存の `marketplace:` 項目に統合してください。

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
# 任意でインストール
omp plugin install writing@sonsu-marketplace
omp plugin install research@sonsu-marketplace
omp plugin install prompting@sonsu-marketplace
omp plugin install product@sonsu-marketplace
omp plugin install worklog@sonsu-marketplace
omp plugin install design-patterns@sonsu-marketplace
omp plugin list
```

## 使い方

インストール後に自然な言葉で依頼すると、ホストが依頼内容とスキルの説明をもとに適切なスキルを選びます。

依頼：「現在のブランチのPR下書きだけ用意して。公開はしないで。」

Gitプラグインの `write-pr` が、リモートに書き込まずにPRのタイトル・本文の下書きと未確認の項目を報告します。

スキルを名前で直接呼び出す形式はホストごとに異なります。

| ホスト | 形式 | 例 |
| --- | --- | --- |
| Codex | `$<スキル>` | `$write-pr` |
| Claude Code | `/<プラグイン>:<スキル>` | `/git:write-pr` |
| omp | `/skill:<スキル>` | `/skill:write-pr` |

プラグインごとの依頼例は各プラグインのREADME（韓国語）にあります。

## プラグイン

リンク名がインストール名です。omp列の `基本` は基本のインストールコマンドに含まれるプラグイン、`任意` は個別にインストールするプラグインです。

| プラグイン | 用途 | Codex | Claude Code | omp |
| --- | --- | :---: | :---: | :---: |
| [`git`](plugins/git/README.md) | Gitのブランチ・コミット・プッシュと、GitHub PRの作成・状態確認・修復 | ✓ | ✓ | 基本 |
| [`tickets`](plugins/tickets/README.md) | GitHub Issues・Linearチケットの作成と、状態・担当者・関係の変更 | ✓ | ✓ | 基本 |
| [`review`](plugins/review/README.md) | コード・diff・コミット・PRのコード健全性レビュー、観点別レビュー、レビュー指摘への対応 | ✓ | ✓ | 基本 |
| [`dev-workflow`](plugins/dev-workflow/README.md) | ソフトウェア変更の設計・計画・実装・デバッグ・検証と簡素化 | ✓ | ✓ | — |
| [`fluent-korean`](plugins/fluent-korean/README.md) | 韓国語の新規文章に生成ルールを適用し、既存文のAI的表現・翻訳調を推敲（`im-not-ai` ベース） | ✓ | ✓ | 基本 |
| [`fluent-english`](plugins/fluent-english/README.md) | 日常・技術英語の作成・推敲・レビュー（`better-writing` ベース） | ✓ | ✓ | 基本 |
| [`fluent-japanese`](plugins/fluent-japanese/README.md) | 日常・技術日本語の作成・推敲と文書診断（`natural-japanese` ベース） | ✓ | ✓ | 基本 |
| [`writing`](plugins/writing/README.md) | 読み手と目的に合わせた情報の選別、記載先の判断、文章の構成 | ✓ | ✓ | 任意 |
| [`research`](plugins/research/README.md) | 複数の情報源の調査、事実確認、根拠に基づく回答の作成 | ✓ | ✓ | 任意 |
| [`prompting`](plugins/prompting/README.md) | Codex・ChatGPT・OpenAI API・Claude Code・Anthropic API向けプロンプトの作成・改善 | ✓ | ✓ | 任意 |
| [`product`](plugins/product/README.md) | プロダクトのアイデア探索、ユーザーに関する根拠の整理、仮説検証、PRD作成 | ✓ | ✓ | 任意 |
| [`memory-manager`](plugins/memory-manager/README.md) | CodexとClaude Codeで共有するローカルメモリの想起・保存・整理 | ✓ | ✓ | — |
| [`design`](plugins/design/README.md) | 一般・運用UIの新規設計・再設計・監査をFigmaまたはコードで実施し、デザインリファレンスも検索 | ✓ | ✓ | 基本 |
| [`design-patterns`](plugins/design-patterns/README.md) | 実際の設計上のforcesに基づくパターン選択と既存適用のレビュー | ✓ | ✓ | 任意 |
| [`worklog`](plugins/worklog/README.md) | Claude Code・Codex・ompの作業で起きた失敗・中断・訂正のログと診断 | ✓ | ✓ | 任意 |

ホストによって動作が異なるプラグインは次のとおりです。

- **Fluent Korean**：Claude Codeはlight・standard・heavyの多段階の経路で、Codexとompは単一の呼び出しで推敲します。
- **Review**：ompでは標準の `/review` にもこのプラグインのレビュー基準が適用されます。
- **Memory Manager**：CodexとClaude Codeが同じマシンのメモリを共有します。ompは独自のメモリ機能を使います。
- **Worklog**：Claude Code・Codexはhookで、ompはruntime extensionで記録します。Codexでは、インストール後と更新後に `/hooks` でworklogのhookを信頼すると記録が始まります。

## アップデート

```sh
codex plugin marketplace upgrade sonsu-marketplace
claude plugin marketplace update sonsu-marketplace
claude plugin update dev-workflow@sonsu-marketplace
omp plugin marketplace update sonsu-marketplace
omp plugin upgrade
```

[旧omp構成・fluent-languages・workflow・engineeringからの移行](docs/guides/migrating-from-earlier-versions.md)（韓国語）

## ドキュメント

- [ドキュメント案内](docs/README.md)
- [スキルの組み合わせとルーティング](docs/architecture/skill-routing.md)
- [プラグイン配布のライフサイクル](docs/architecture/plugin-lifecycle.md)
- [プラグイン別のライセンスと出典](docs/reference/licenses-and-sources.md)

## 貢献

ローカル環境・変更・検証手順は[プラグイン開発ガイド](docs/guides/adding-a-plugin.md)、不具合報告や改善提案は[GitHub Issues](https://github.com/sonsu-lee/sonsu-marketplace/issues)を参照してください。詳細ガイドは韓国語で管理しています。

## ライセンス

リポジトリ全体に適用するライセンスは現在宣言していません。各プラグインの条件と原文の通知は[ライセンスと出典](docs/reference/licenses-and-sources.md)（韓国語）を確認してください。
