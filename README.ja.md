# Sonsu Marketplace

[한국어](README.md) · [English](README.en.md) · [日本語](README.ja.md)

開発、リサーチ、プロダクト企画、文章作成に使えるCodex・Claude Code・ompプラグイン集です。

## インストール

### Codex

`codex plugin` に対応したCLIで一度登録し、必要なプラグイン一つ、または全件をインストールします。一覧にインストール状態が表示されたら、新しいCodexタスクを開始してください。

```sh
codex plugin marketplace add sonsu-lee/sonsu-marketplace --ref main
# 一つだけインストール
codex plugin add engineering@sonsu-marketplace
# 全件をインストールする場合は上の単独インストールの代わりに実行
for plugin in engineering workflow fluent-korean fluent-english fluent-japanese writing research prompting product memory-manager design-patterns design worklog; do codex plugin add "$plugin@sonsu-marketplace"; done
codex plugin marketplace list
codex plugin list --marketplace sonsu-marketplace
```

### Claude Code

マーケットプレイスを一度登録し、必要なプラグイン一つ、または全件をインストールします。一覧でインストール状態を確認して、新しいセッションを開始してください。

```sh
claude plugin marketplace add sonsu-lee/sonsu-marketplace
# 一つだけインストール
claude plugin install engineering@sonsu-marketplace
# 全件をインストールする場合は上の単独インストールの代わりに実行
for plugin in engineering workflow fluent-korean fluent-english fluent-japanese writing research prompting product memory-manager design-patterns design worklog; do claude plugin install "$plugin@sonsu-marketplace"; done
claude plugin marketplace list
claude plugin list
```

### omp

基本5件をインストールし、Worklog・Design Patternsは必要な場合だけ追加します。自動更新を新たに有効にする場合だけ、下のYAMLを `~/.omp/agent/config.yml` の既存の `marketplace:` 項目に統合してください。

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

```sh
# 任意でインストール
omp plugin install worklog@sonsu-marketplace
omp plugin install design-patterns@sonsu-marketplace
omp plugin list
```

## プラグイン

各プラグインは独立して使え、詳しい使い方はリンク先で確認できます（Codex・Claude Codeは全13件、ompは基本5件とopt-inのWorklog・Design Patterns）。

| プラグイン | 用途 | インストール名 |
| --- | --- | --- |
| [Engineering](plugins/engineering/README.md) | ソフトウェア変更の設計・実装・検証、簡素化、品質レビュー | `engineering` |
| [Workflow](plugins/workflow) | Gitのブランチ・コミット・プッシュ、チケット、GitHub PRの作成・管理 | `workflow` |
| [Fluent Korean](plugins/fluent-korean) | `im-not-ai` をもとに韓国語の新規文章に生成ルールを適用し、既存文のAI的表現・翻訳調を推敲 | `fluent-korean` |
| [Fluent English](plugins/fluent-english) | `better-writing` をもとに日常・技術文の作成・推敲・レビュー | `fluent-english` |
| [Fluent Japanese](plugins/fluent-japanese) | `natural-japanese` をもとに日常・技術文の作成・推敲と文書診断 | `fluent-japanese` |
| [Writing](plugins/writing) | 読み手と目的に合わせた情報の選別、記載先の判断、文章の構成 | `writing` |
| [Research](plugins/research/README.md) | 複数の情報源の調査、事実確認、根拠に基づく回答の作成 | `research` |
| [Prompting](plugins/prompting/README.md) | Codex・ChatGPT・OpenAI API・Claude Code・Anthropic API向けプロンプトの作成・改善 | `prompting` |
| [Product](plugins/product/README.md) | プロダクトのアイデア探索、ユーザーに関する根拠の整理、仮説検証、PRD作成 | `product` |
| [Memory Manager](plugins/memory-manager/README.md) | CodexとClaude Codeで共有するローカルメモリの想起・保存・整理 | `memory-manager` |
| [Design](plugins/design/README.md) | 一般・運用UIの新規設計・再設計・監査をFigmaまたはコードで実施し、デザインリファレンスも検索 | `design` |
| [Design Patterns](plugins/design-patterns/README.md) | 実際の設計上のforcesに基づくパターン選択と既存適用のレビュー | `design-patterns` |
| [Worklog](plugins/worklog/README.md) | Claude Code・Codex・ompの作業で起きた失敗・中断・訂正のログと診断 | `worklog` |

## 使用例

対応するプラグインをインストールしたら、CodexまたはClaude Codeに依頼してください（直接呼び出す例：Claude Code `/engineering:review`、omp `/skill:commit`）。

| プラグイン | 依頼の例 |
| --- | --- |
| Engineering | 「このバグを修正して検証するか、現在のdiffに不要な抽象化や到達可能な障害経路がないかレビューして。」 |
| Workflow | 「現在の変更をコミットして、Draft PRを作成して。」 |
| Fluent Japanese | 「この日本語の技術説明を、意味とコードの識別子を保ちながら自然な文章に整えて。」 |
| Writing | 「この資料からREADMEに必要な内容を選んで要約し、詳細は既存のドキュメントに反映して。」 |
| Research | 「この2つのサービスの料金と制限を、公式資料に基づいて比較して。」 |
| Prompting | 「このプロンプトを、Codexですぐに使えるように改善して。」 |
| Product | 「このインタビューメモから、ユーザーの課題とその根拠を整理して。」 |
| Memory Manager | 「`$memory-capture` この決定をプロジェクトのメモリに保存して。」 |
| Design | 「登録フローをFigmaで設計して。運用画面はコードで直接再設計して。」または「ログイン画面のリファレンスを出典付きで探して。」 |
| Design Patterns | 「この設計にパターンが必要か判断し、最小の実装形を選んで。」 |

ホストは依頼内容とインストール済みスキルの説明をもとに、必要なスキルを選びます。

## アップデート

```sh
codex plugin marketplace upgrade sonsu-marketplace
claude plugin marketplace update sonsu-marketplace
claude plugin update engineering@sonsu-marketplace
omp plugin marketplace update sonsu-marketplace
omp plugin upgrade
```

[旧omp構成・fluent-languagesからの移行](docs/guides/migrating-from-earlier-versions.md)（韓国語）

## ドキュメント

- [ドキュメント案内](docs/README.md)
- [スキルの組み合わせとルーティング](docs/architecture/skill-routing.md)
- [プラグイン配布のライフサイクル](docs/architecture/plugin-lifecycle.md)
- [プラグイン別のライセンスと出典](docs/reference/licenses-and-sources.md)

## 貢献

ローカル環境・変更・検証手順は[プラグイン開発ガイド](docs/guides/adding-a-plugin.md)、不具合報告や改善提案は[GitHub Issues](https://github.com/sonsu-lee/sonsu-marketplace/issues)を参照してください。詳細ガイドは韓国語で管理しています。

## ライセンス

リポジトリ全体に適用するライセンスは現在宣言していません。各プラグインの条件と原文の通知は[ライセンスと出典](docs/reference/licenses-and-sources.md)（韓国語）を確認してください。
