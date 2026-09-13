# Sonsu Marketplace

[한국어](README.md) · [English](README.en.md) · [日本語](README.ja.md)

開発、リサーチ、プロダクト企画、文章作成に使えるCodexプラグイン集です。
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

## プラグイン

| プラグイン | 用途 | インストール名 |
| --- | --- | --- |
| [Engineering](plugins/engineering/README.md) | ソフトウェア変更の設計・実装・検証、簡素化、品質レビュー | `engineering` |
| [Workflow](plugins/workflow/) | Gitのブランチ・コミット・プッシュ、チケット、GitHub PRの作成・管理 | `workflow` |
| [Fluent Languages](plugins/fluent-languages/) | 技術的な内容を保った自然な韓国語・日本語・英語の文章作成 | `fluent-languages` |
| [Writing](plugins/writing/) | 読み手と目的に合わせた情報の選別、記載先の判断、文章の構成 | `writing` |
| [Research](plugins/research/README.md) | 複数の情報源の調査、事実確認、根拠に基づく回答の作成 | `research` |
| [Prompting](plugins/prompting/README.md) | Codex・ChatGPT・OpenAI API向けプロンプトの作成・改善 | `prompting` |
| [Product](plugins/product/README.md) | プロダクトのアイデア探索、ユーザーに関する根拠の整理、仮説検証、PRD作成 | `product` |
| [Figma Workflow](plugins/figma-workflow/README.md) | Figmaでのプロダクト画面・クリック可能なプロトタイプの作成とデザイン品質のレビュー | `figma-workflow` |
| [Memory Manager](plugins/memory-manager/README.md) | 明示的に呼び出してコーディングエージェントのメモリを点検・整理 | `memory-manager` |
| [Operations UI](plugins/operations-ui/README.md) | 状態とデータを扱うB2B運用画面の設計・再設計・品質監査 | `operations-ui` |
| [Design Patterns](plugins/design-patterns/README.md) | 実際の設計上のforcesに基づくパターン選択と既存適用のレビュー | `design-patterns` |

各プラグインは独立して利用できます。含まれるスキルや詳しい使い方は、上のリンクから確認してください。

Writingは情報の選別・記載先の判断と文章の構成、Fluent Languagesは各言語の表現、
Workflowはチケット・PRのテンプレートと公開手順を担当します。併用方法は
[スキルルーティングのドキュメント](docs/architecture/skill-routing.md)を参照してください。

## 使用例

対応するプラグインをインストールしたら、Codexに次のように依頼できます。

| プラグイン | 依頼の例 |
| --- | --- |
| Engineering | 「このバグを修正して検証するか、現在のdiffに不要な抽象化や到達可能な障害経路がないかレビューして。」 |
| Workflow | 「現在の変更をコミットして、Draft PRを作成して。」 |
| Fluent Languages | 「この日本語の技術説明を、意味とコードの識別子を保ちながら自然な文章に整えて。」 |
| Writing | 「この資料からREADMEに必要な内容を選んで要約し、詳細は既存のドキュメントに反映して。」 |
| Research | 「この2つのサービスの料金と制限を、公式資料に基づいて比較して。」 |
| Prompting | 「このプロンプトを、Codexですぐに使えるように改善して。」 |
| Product | 「このインタビューメモから、ユーザーの課題とその根拠を整理して。」 |
| Figma Workflow | 「このFigma画面のAuto Layoutとプロトタイプの接続をレビューして。」 |
| Memory Manager | 「$memory-manager このプロジェクトのCodexメモリを点検して。」 |
| Operations UI | 「この受注運用画面をScreen Contractから実装し、ブラウザーの証跡で検証して。」 |
| Design Patterns | 「この設計にパターンが必要か判断し、最小の実装形を選んで。」 |

Codexは、依頼内容とインストール済みスキルの説明をもとに、必要なスキルを選びます。
Memory Managerは、`$memory-manager`で明示的に呼び出したときだけ動作します。

ResearchのExa・Perplexity連携は任意です。利用可能なWebツール、ブラウザー、コネクター、ローカル資料でも調査できます。
Figma Workflowでキャンバスを操作するには、公式Figma MCP接続と、そのツールで必須とされるスキルが必要です。
設定方法と必要なツールは、各プラグインのドキュメントを参照してください。

## アップデート

登録済みのGitマーケットプレイスから最新のスナップショットを取得します。

```sh
codex plugin marketplace upgrade sonsu-marketplace
```

プラグインのインストールやアップデート後は、Codexで新しいタスクを開始して最新のスキル一覧を読み込んでください。

別のマーケットプレイスから `fluent-languages` をインストールしている場合や、
`prompt-builder`、`product-discovery`、`to-prd` を単体でインストールしている場合は、同名スキルの重複を避けるため、既存のコピーを先に削除してください。

## 開発・貢献

ローカル環境の準備、プラグインの変更・追加、検証手順は
[プラグイン開発ガイド](docs/guides/adding-a-plugin.md)にまとめています。詳細ガイドは韓国語で管理しています。

- [アーキテクチャ概要](docs/architecture/overview.md) — リポジトリ構成と読み込みの境界
- [アップストリーム更新ランブック](docs/runbooks/updating-upstream-plugin.md) — 元のソースとローカル変更を分けて更新する手順
- [評価ツール](evals/) — 言語出力、スキルルーティング、プラグイン品質の検証
- [GitHub Issues](https://github.com/sonsu-lee/sonsu-marketplace/issues) — バグ報告・改善提案

## ライセンスと出典

リポジトリ全体に適用するライセンスは、現在宣言していません。各プラグインの条件と原文の通知は
[プラグイン別のライセンスと出典](docs/reference/licenses-and-sources.md)（韓国語）を確認してください。
