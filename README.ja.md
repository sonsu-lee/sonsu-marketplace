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

Claude Codeでは、同じリポジトリをマーケットプレイスとして登録し、必要なプラグインをインストールします。

```sh
claude plugin marketplace add sonsu-lee/sonsu-marketplace
claude plugin install engineering@sonsu-marketplace
```

別のプラグインをインストールする場合は、下の表にあるインストール名に置き換えてください。
インストール済みの項目とマーケットプレイスで利用できる項目は、次のコマンドで確認できます。

```sh
claude plugin list --available --json
```

Claude Code向けパッケージは、同じ`skills/`、`hooks/`、`scripts/`を使用します。Codex専用の
`apps`とUI metadataはClaude manifestへコピーしないため、Figmaなどの外部ツールはClaude Code
host側で別途設定し、実際にtoolが利用できることを確認してください。

## プラグイン

| プラグイン | 用途 | インストール名 |
| --- | --- | --- |
| [Engineering](plugins/engineering/README.md) | ソフトウェア変更の設計、実装、デバッグ、検証 | `engineering` |
| [Quality Engineering](plugins/quality-engineering/README.md) | コードの簡素化と、保守性・障害経路・運用上の問題のレビュー | `quality-engineering` |
| [Workflow](plugins/workflow/) | Gitのブランチ・コミット・プッシュ、チケット、GitHub PRの作成・管理 | `workflow` |
| [Writing](plugins/writing/) | 韓国語・日本語・英語の文章を、構成から表現まで目的に合わせて作成・編集 | `writing` |
| [Research](plugins/research/README.md) | 複数の情報源の調査、事実確認、根拠に基づく回答の作成 | `research` |
| [Prompting](plugins/prompting/README.md) | Codex・ChatGPT・OpenAI API向けプロンプトの作成・改善 | `prompting` |
| [Product](plugins/product/README.md) | プロダクトのアイデア探索、ユーザーに関する根拠の整理、仮説検証、PRD作成 | `product` |
| [Figma Workflow](plugins/figma-workflow/README.md) | Figmaでのプロダクト画面・クリック可能なプロトタイプの作成とデザイン品質のレビュー | `figma-workflow` |
| [Memory Manager](plugins/memory-manager/README.md) | 明示的に呼び出してコーディングエージェントのメモリを点検・整理 | `memory-manager` |
| [Operations UI](plugins/operations-ui/README.md) | 状態とデータを扱うB2B運用画面の設計・再設計・品質監査 | `operations-ui` |
| [Design Patterns](plugins/design-patterns/README.md) | 実際の設計上のforcesに基づくパターン選択と既存適用のレビュー | `design-patterns` |

各プラグインは独立して利用できます。含まれるスキルや詳しい使い方は、上のリンクから確認してください。

## 使用例

対応するプラグインをインストールしたら、CodexまたはClaude Codeに次のように依頼できます。

| プラグイン | 依頼の例 |
| --- | --- |
| Engineering | 「このバグの原因を特定して修正し、再現手順で修正結果を検証して。」 |
| Quality Engineering | 「現在のdiffに不要な抽象化や到達可能な障害経路がないかレビューして。」 |
| Workflow | 「現在の変更をコミットして、Draft PRを作成して。」 |
| Writing | 「この日本語のPR説明を、変更理由と動作がレビュー担当者に伝わる構成に直して。意味とコードの識別子は保って。」 |
| Research | 「この2つのサービスの料金と制限を、公式資料に基づいて比較して。」 |
| Prompting | 「このプロンプトを、Codexですぐに使えるように改善して。」 |
| Product | 「このインタビューメモから、ユーザーの課題とその根拠を整理して。」 |
| Figma Workflow | 「このFigma画面のAuto Layoutとプロトタイプの接続をレビューして。」 |
| Memory Manager | Codex: 「$memory-manager このプロジェクトのCodexメモリを点検して。」<br>Claude Code: 「/memory-manager:memory-manager このプロジェクトのClaude Codeメモリを点検して。」 |
| Operations UI | 「この受注運用画面をScreen Contractから実装し、ブラウザーの証跡で検証して。」 |
| Design Patterns | 「この設計にパターンが必要か判断し、最小の実装形を選んで。」 |

CodexとClaude Codeは、依頼内容とインストール済みスキルの説明をもとに、必要なスキルを選びます。
Memory Managerは、Codexでは`$memory-manager`、Claude Codeでは
`/memory-manager:memory-manager`で明示的に呼び出したときだけ動作します。
複数のプラグインを併用する際の役割分担は、[スキルルーティングのドキュメント](docs/architecture/skill-routing.md)にまとめています。

ResearchのExa・Perplexity連携は任意です。利用可能なWebツール、ブラウザー、コネクター、ローカル資料でも調査できます。
Figma Workflowでキャンバスを操作するには、公式Figma MCP接続と、そのツールで必須とされるスキルが必要です。
設定方法と必要なツールは、各プラグインのドキュメントを参照してください。

## アップデート

登録済みのGitマーケットプレイスから最新のスナップショットを取得します。

```sh
codex plugin marketplace upgrade sonsu-marketplace
```

Claude Codeでは、マーケットプレイスの一覧を更新してから、インストール済みの各プラグインを更新します。

```sh
claude plugin marketplace update sonsu-marketplace
claude plugin update engineering@sonsu-marketplace
```

`engineering`をインストール済みの各プラグイン名に置き換え、2つ目のコマンドを繰り返します。
`project`または`local`スコープにインストールした場合は、同じスコープを`--scope project`または`--scope local`で指定します。

プラグインのインストールやアップデート後は、Codexで新しいタスクを開始するか、Claude Codeで
`/reload-plugins`を実行して最新のスキル一覧を読み込んでください。

<details>
<summary>Fluent Languagesからの移行とスキルの重複解消</summary>

Writing `0.2.0-beta.1`はFluent Languagesを置き換えるプラグインです。`writing:writing`スキルで
文章の構成と言語別の表現を扱います。利用するホストに合わせて、新しいプラグインをインストールしてください。

```sh
codex plugin add writing@sonsu-marketplace
```

```sh
claude plugin install writing@sonsu-marketplace
```

スキルが重複して検出されないよう、インストール済みの`fluent-languages`も削除してください。
マーケットプレイスを更新しても、インストール済みプラグインの名前やcontinuityの記録は自動では変わりません。
Fluentで未完了の作業があり、記録の場所が分かっている場合は、削除する前に元のプラグインで原文と下書きを復旧し、
確認した作業範囲と根拠をWritingの新しいタスクへ明示的に引き継いでください。他のプラグインの記録を自動で
読み込んだり、名前だけを変えて再利用したりしません。詳しくは[作業継続の契約](docs/reference/task-continuity.md)を参照してください。

`prompt-builder`、`product-discovery`、`to-prd`を単体でインストールしている場合も、同名スキルの
重複を避けるため、既存のコピーを先に削除してください。

</details>

## 開発・貢献

プラグインを変更・追加する場合は、リポジトリをクローンし、ローカルマーケットプレイスとして登録します。

```sh
git clone https://github.com/sonsu-lee/sonsu-marketplace.git
cd sonsu-marketplace
codex plugin marketplace add .
codex plugin list --marketplace sonsu-marketplace

claude plugin marketplace add . --scope local
claude plugin list --available --json
```

GitHubソースとローカルパスは同じ `sonsu-marketplace` 識別子を使うため、1つの環境ではどちらか一方の方法で登録してください。

- [プラグイン追加ガイド](docs/guides/adding-a-plugin.md) — ディレクトリ構成とマニフェスト登録
- [ドキュメント案内](docs/README.md) — アーキテクチャ、設計上の決定、プラグインの契約
- [アップストリーム更新ランブック](docs/runbooks/updating-upstream-plugin.md) — 元のソースとローカル変更を分けて更新する手順
- [評価ツール](evals/) — 言語出力、スキルルーティング、プラグイン品質の検証
- [GitHub Issues](https://github.com/sonsu-lee/sonsu-marketplace/issues) — バグ報告・改善提案

<details>
<summary>リポジトリ構成と検証コマンド</summary>

### リポジトリ構成

```text
sonsu-marketplace/
├── .agents/plugins/marketplace.json  # プラグイン一覧
├── .claude-plugin/marketplace.json   # Claude Codeプラグイン一覧
├── plugins/
│   └── <plugin>/
│       ├── .codex-plugin/plugin.json # プラグイン情報
│       ├── .claude-plugin/plugin.json # 生成されたClaude Codeプラグイン情報
│       └── skills/                  # スキルと参考資料
├── docs/                            # 保守用ドキュメント
└── evals/                           # 評価用fixtureと検証ツール
```

### 検証

リポジトリのルートで、次の静的検査を実行します。

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

これらのコマンドは、JSON構文、Writingの正本から生成したWorkflow資料の一致、スキルのmetadata、
評価用fixtureとrunnerの構造を確認します。
実際のモデルによるスキル選択や出力品質は、別途検証が必要です。プラグインの構造を変更した場合は、
分離したCodex・Claude Code環境でマーケットプレイスの登録、プラグインのインストール、スキルが利用可能になることも確認してください。

各プラットフォームの形式は、[OpenAI公式のプラグインパッケージングドキュメント](https://developers.openai.com/plugins/build/plugins)と
[Anthropic公式のマーケットプレイスドキュメント](https://code.claude.com/docs/en/plugin-marketplaces)に従います。

</details>

## ライセンスと出典

リポジトリ全体に適用するルートレベルのライセンスは、現在宣言していません。各プラグインのライセンスと出典は次のとおりです。

- Engineeringには[MITライセンス](plugins/engineering/LICENSE)が適用されます。
- Quality Engineeringは複数のバージョンを固定したアップストリームソースに基づき、[Apache-2.0ライセンス](plugins/quality-engineering/LICENSE)、[NOTICE](plugins/quality-engineering/NOTICE)、[出典の対応表](plugins/quality-engineering/UPSTREAM.md)、[MITライセンスの原文通知](plugins/quality-engineering/THIRD_PARTY_NOTICES.md)を保持しています。
- Workflowには、現在個別のライセンスを宣言していません。Writingから同梱した作成指針とテンプレートには、[MITの表記](plugins/workflow/WRITING_LICENSE.md)を別途保持しています。
- Promptingには、現在個別のライセンスを宣言していません。
- Productには、現在個別のライセンスを宣言していません。
- Memory Managerは独自に作成したプラグインで、現在個別のライセンスを宣言していません。設計で参照した出典は[UPSTREAM.md](plugins/memory-manager/UPSTREAM.md)に記録しています。
- Operations UIは外部のUIコードやアセットをコピーせずに独自に作成したプラグインで、現在個別のライセンスを宣言していません。設計で参照した出典は[UPSTREAM.md](plugins/operations-ui/UPSTREAM.md)に記録しています。
- Design Patternsはパターン名と出典位置のみを索引化し、選択・レビュー契約は独自に作成しています。現在個別のライセンスは宣言しておらず、収録範囲と出典条件は[UPSTREAM.md](plugins/design-patterns/UPSTREAM.md)に記録しています。
- Figma Workflowは外部ファイルをコピーせずに独自に作成したプラグインで、現在個別のライセンスを宣言していません。参照した出典と外部ファイルをコピーしない方針は、[UPSTREAM.md](plugins/figma-workflow/UPSTREAM.md)に記録しています。
- WritingがFluent Languagesから引き継いだライセンスと各ソースの出典は、[LICENSE](plugins/writing/LICENSE)、[UPSTREAM.md](plugins/writing/UPSTREAM.md)、[THIRD_PARTY_NOTICES.md](plugins/writing/THIRD_PARTY_NOTICES.md)に記録しています。
- Researchは基準とした元のソースでライセンスファイルを確認できておらず、利用が許可されているとは推定していません。基準コミットと収録範囲は、[UPSTREAM.md](plugins/research/UPSTREAM.md)に記録しています。
