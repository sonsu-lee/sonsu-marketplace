# Sonsu Marketplace

[한국어](README.md) · [English](README.en.md) · [日本語](README.ja.md)

開発、リサーチ、プロダクト企画、文章作成に使えるCodex・Claude Codeプラグイン集です。
必要なプラグインを選んでインストールし、利用中のコーディングエージェントに作業を依頼してください。

[インストール](#インストール) · [プラグイン](#プラグイン) · [使用例](#使用例) · [ドキュメント](docs/README.md)

## インストール

### Codex

`codex plugin` コマンドに対応したCodex CLIで、マーケットプレイスを登録します。

```sh
codex plugin marketplace add sonsu-lee/sonsu-marketplace --ref main
```

作業に必要なプラグインをインストールします。たとえば、ソフトウェア開発にはEngineeringを利用できます。

```sh
codex plugin add engineering@sonsu-marketplace
```

別のプラグインをインストールする場合は、下の表にあるインストール名に置き換えてください。Workflowの場合は次のとおりです。

```sh
codex plugin add workflow@sonsu-marketplace
```

インストール後は、新しいCodexタスクを開始してください。マーケットプレイスのプラグイン一覧は、次のコマンドで確認できます。

```sh
codex plugin list --marketplace sonsu-marketplace
```

### Claude Code

マーケットプレイスを登録し、必要なプラグインをインストールします。

```sh
claude plugin marketplace add sonsu-lee/sonsu-marketplace
claude plugin install engineering@sonsu-marketplace
claude plugin list
```

ローカルのチェックアウトを試す場合は、最初のコマンドにリポジトリの絶対パスを渡します。
スキルは `/engineering:review` のように呼び出します。インストール・更新後は新しい
セッションで確認してください。CodexのコネクターとClaude CodeのMCP接続は別途設定します。

## プラグイン

| プラグイン | 用途 | インストール名 |
| --- | --- | --- |
| [Engineering](plugins/engineering/README.md) | ソフトウェア変更の設計・実装・検証、簡素化、品質レビュー | `engineering` |
| [Workflow](plugins/workflow) | Gitのブランチ・コミット・プッシュ、チケット、GitHub PRの作成・管理 | `workflow` |
| [Fluent Korean](plugins/fluent-korean) | `im-not-ai` をもとに既存の日常・技術文のAI的表現・翻訳調を推敲 | `fluent-korean` |
| [Fluent English](plugins/fluent-english) | `better-writing` をもとに日常・技術文の作成・推敲・レビュー | `fluent-english` |
| [Fluent Japanese](plugins/fluent-japanese) | `natural-japanese` をもとに日常・技術文の作成・推敲と文書診断 | `fluent-japanese` |
| [Writing](plugins/writing) | 読み手と目的に合わせた情報の選別、記載先の判断、文章の構成 | `writing` |
| [Research](plugins/research/README.md) | 複数の情報源の調査、事実確認、根拠に基づく回答の作成 | `research` |
| [Prompting](plugins/prompting/README.md) | Codex・ChatGPT・OpenAI API・Claude Code・Anthropic API向けプロンプトの作成・改善 | `prompting` |
| [Product](plugins/product/README.md) | プロダクトのアイデア探索、ユーザーに関する根拠の整理、仮説検証、PRD作成 | `product` |
| [Figma Workflow](plugins/figma-workflow/README.md) | Figmaでのプロダクト画面・クリック可能なプロトタイプの作成とデザイン品質のレビュー | `figma-workflow` |
| [Memory Manager](plugins/memory-manager/README.md) | 明示的に呼び出してコーディングエージェントのメモリを点検・整理 | `memory-manager` |
| [Interface Design](plugins/interface-design/README.md) | Web・アプリ画面の設計・再設計と情報表現の検証 | `interface-design` |
| [Operations UI](plugins/operations-ui/README.md) | 状態とデータを扱うB2B運用画面の設計・再設計・品質監査 | `operations-ui` |
| [Design Patterns](plugins/design-patterns/README.md) | 実際の設計上のforcesに基づくパターン選択と既存適用のレビュー | `design-patterns` |

各プラグインは独立して利用できます。含まれるスキルや詳しい使い方は、上のリンクから確認してください。

Writingは情報の選別・記載先の判断と文章の構成、各Fluentプラグインは対象言語の表現、
Workflowはチケット・PRの新規作成に使うテンプレートと公開手順、Engineeringは既存PRへのレビュー結果の投稿を担当します。併用方法は
[スキルルーティングのドキュメント](docs/architecture/skill-routing.md)を参照してください。

## 使用例

対応するプラグインをインストールしたら、Codexに次のように依頼できます。

| プラグイン | 依頼の例 |
| --- | --- |
| Engineering | 「このバグを修正して検証するか、現在のdiffに不要な抽象化や到達可能な障害経路がないかレビューして。」 |
| Workflow | 「現在の変更をコミットして、Draft PRを作成して。」 |
| Fluent Japanese | 「この日本語の技術説明を、意味とコードの識別子を保ちながら自然な文章に整えて。」 |
| Writing | 「この資料からREADMEに必要な内容を選んで要約し、詳細は既存のドキュメントに反映して。」 |
| Research | 「この2つのサービスの料金と制限を、公式資料に基づいて比較して。」 |
| Prompting | 「このプロンプトを、Codexですぐに使えるように改善して。」 |
| Product | 「このインタビューメモから、ユーザーの課題とその根拠を整理して。」 |
| Figma Workflow | 「このFigma画面のAuto Layoutとプロトタイプの接続をレビューして。」 |
| Memory Manager | 「`$memory-manager` このプロジェクトのCodexメモリを点検して。」 |
| Interface Design | 「モバイルの登録フローを設計して。このグラフの情報表現も改善して。」 |
| Operations UI | 「この受注運用画面をDesign Decision Contractから実装し、DQゲートとブラウザーの証跡で検証して。」 |
| Design Patterns | 「この設計にパターンが必要か判断し、最小の実装形を選んで。」 |

ホストは依頼内容とインストール済みスキルの説明をもとに、必要なスキルを選びます。
Memory ManagerはCodexの`$memory-manager`またはClaude Codeの`/memory-manager:memory-manager`で
明示的に呼び出したときだけ動作します。

ResearchのExa・Perplexity連携は任意です。利用可能なWebツール、ブラウザー、コネクター、ローカル資料でも調査できます。
Figma Workflowでキャンバスを操作するには、公式Figma MCP接続と、そのツールで必須とされるスキルが必要です。
設定方法と必要なツールは、各プラグインのドキュメントを参照してください。

## アップデート

Codexでは、登録済みのGitマーケットプレイスから最新のスナップショットを取得します。

```sh
codex plugin marketplace upgrade sonsu-marketplace
```

更新後は新しいCodexタスクを開始し、最新のスキル一覧を読み込んでください。

Claude Codeではマーケットプレイスとインストール済みプラグインを更新し、新しいセッションを開始します。

```sh
claude plugin marketplace update sonsu-marketplace
claude plugin update engineering@sonsu-marketplace
```

以前の `fluent-languages` がインストールされている場合は、言語指針の重複を避けるため、先に削除してから必要な言語プラグインをインストールしてください。新しいスキル ID は `fluent-korean:fluent-korean`、`fluent-english:fluent-english`、`fluent-japanese:fluent-japanese` です。英語は日常文と技術文の作成・推敲・レビューに、日本語は作成・推敲と文書診断に使えます。韓国語は既存文のAI的表現・翻訳調の推敲に使います。既存の作業継続記録は自動移行されません。[手動の復旧手順](docs/reference/task-continuity.md)を参照してください。

```sh
codex plugin remove fluent-languages@sonsu-marketplace
codex plugin add fluent-korean@sonsu-marketplace
codex plugin add fluent-english@sonsu-marketplace
codex plugin add fluent-japanese@sonsu-marketplace
```

Claude Codeでは `claude plugin uninstall fluent-languages@sonsu-marketplace` の後に、必要な言語を `claude plugin install <name>@sonsu-marketplace` でインストールします。別のマーケットプレイスや、単体でインストールした `prompt-builder`、`product-discovery`、`to-prd` に同名スキルがないかも確認してください。

## 開発・貢献

ローカル環境の準備、プラグインの変更・追加、検証手順は
[プラグイン開発ガイド](docs/guides/adding-a-plugin.md)にまとめています。詳細ガイドは韓国語で管理しています。

- [アーキテクチャ概要](docs/architecture/overview.md) — リポジトリ構成と読み込みの境界
- [アップストリーム更新ランブック](docs/runbooks/updating-upstream-plugin.md) — 元のソースとローカル変更を分けて更新する手順
- [評価ツール](evals) — 言語出力、スキルルーティング、プラグイン品質の検証
- [GitHub Issues](https://github.com/sonsu-lee/sonsu-marketplace/issues) — バグ報告・改善提案

## ライセンスと出典

リポジトリ全体に適用するライセンスは、現在宣言していません。各プラグインの条件と原文の通知は
[プラグイン別のライセンスと出典](docs/reference/licenses-and-sources.md)（韓国語）を確認してください。
