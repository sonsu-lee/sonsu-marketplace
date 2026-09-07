# Sonsu Marketplace

[한국어](README.md) · [English](README.en.md) · [日本語](README.ja.md)

開発、リサーチ、プロダクト企画、文章作成に使えるCodexプラグイン集です。
必要なプラグインを選んでインストールし、いつもどおりCodexに作業を依頼してください。

[インストール](#インストール) · [プラグイン](#プラグイン) · [使用例](#使用例) · [ドキュメント](docs/README.md)

## インストール

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
| [Engineering](plugins/engineering/README.md) | ソフトウェア変更の設計、実装、デバッグ、検証 | `engineering` |
| [Quality Engineering](plugins/quality-engineering/README.md) | コードの簡素化と、保守性・障害経路・運用上の問題のレビュー | `quality-engineering` |
| [Workflow](plugins/workflow/) | Gitのブランチ・コミット・プッシュ、チケット、GitHub PRの作成・管理 | `workflow` |
| [Fluent Languages](plugins/fluent-languages/) | 技術的な内容を保った自然な韓国語・日本語・英語の文章作成 | `fluent-languages` |
| [Research](plugins/research/README.md) | 複数の情報源の調査、事実確認、根拠に基づく回答の作成 | `research` |
| [Prompting](plugins/prompting/README.md) | Codex・ChatGPT・OpenAI API向けプロンプトの作成・改善 | `prompting` |
| [Product](plugins/product/README.md) | プロダクトのアイデア探索、ユーザーに関する根拠の整理、仮説検証、PRD作成 | `product` |
| [Figma Workflow](plugins/figma-workflow/README.md) | Figmaでのプロダクト画面・クリック可能なプロトタイプの作成とデザイン品質のレビュー | `figma-workflow` |
| [Memory Manager](plugins/memory-manager/README.md) | 明示的に呼び出してコーディングエージェントのメモリを点検・整理 | `memory-manager` |

各プラグインは独立して利用できます。含まれるスキルや詳しい使い方は、上のリンクから確認してください。

## 使用例

対応するプラグインをインストールしたら、Codexに次のように依頼できます。

| プラグイン | 依頼の例 |
| --- | --- |
| Engineering | 「このバグの原因を特定して修正し、再現手順で修正結果を検証して。」 |
| Quality Engineering | 「現在のdiffに不要な抽象化や到達可能な障害経路がないかレビューして。」 |
| Workflow | 「現在の変更をコミットして、Draft PRを作成して。」 |
| Fluent Languages | 「この日本語の技術説明を、意味とコードの識別子を保ちながら自然な文章に整えて。」 |
| Research | 「この2つのサービスの料金と制限を、公式資料に基づいて比較して。」 |
| Prompting | 「このプロンプトを、Codexですぐに使えるように改善して。」 |
| Product | 「このインタビューメモから、ユーザーの課題とその根拠を整理して。」 |
| Figma Workflow | 「このFigma画面のAuto Layoutとプロトタイプの接続をレビューして。」 |
| Memory Manager | 「$memory-manager このプロジェクトのCodexメモリを点検して。」 |

Codexは依頼内容とインストール済みスキルの説明をもとに、必要なスキルを選びます。
Memory Managerは、`$memory-manager`で明示的に呼び出したときだけ動作します。
複数のプラグインを併用する際の役割分担は、[スキルルーティングのドキュメント](docs/architecture/skill-routing.md)にまとめています。

ResearchのExa・Perplexity連携は任意です。利用可能なWebツール、ブラウザー、コネクター、ローカル資料でも調査できます。
Figma Workflowでキャンバスを操作するには、公式Figma MCP接続と、そのツールで必須とされるスキルが必要です。
設定方法と必要なツールは、各プラグインのドキュメントを参照してください。

## アップデート

登録済みのGitマーケットプレイスから最新のスナップショットを取得します。

```sh
codex plugin marketplace upgrade sonsu-marketplace
```

プラグインのインストールやアップデート後は、新しいCodexタスクを開始して最新のスキル一覧を読み込んでください。

<details>
<summary>同じスキルをすでにインストールしている場合</summary>

別のマーケットプレイスから `fluent-languages` をインストールしている場合や、
`prompt-builder`、`product-discovery`、`to-prd` を単体でインストールしている場合は、同名スキルの重複を避けるため、既存のコピーを先に削除してください。

</details>

## 開発・貢献

プラグインを変更・追加する場合は、リポジトリをクローンし、ローカルマーケットプレイスとして登録します。

```sh
git clone https://github.com/sonsu-lee/sonsu-marketplace.git
cd sonsu-marketplace
codex plugin marketplace add .
codex plugin list --marketplace sonsu-marketplace
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
├── plugins/
│   └── <plugin>/
│       ├── .codex-plugin/plugin.json # プラグイン情報
│       └── skills/                  # スキルと参考資料
├── docs/                            # 保守用ドキュメント
└── evals/                           # 評価用fixtureと検証ツール
```

### 検証

リポジトリのルートで、次の静的検査を実行します。

```sh
find .agents plugins evals -name '*.json' -print0 \
  | xargs -0 -n1 python3 -m json.tool >/dev/null
python3 plugins/fluent-languages/scripts/render-skills.py --check
python3 evals/language-style/eval.py validate
python3 -m unittest -v evals/language-style/test_eval.py
git diff --check
```

これらのコマンドは、JSON構文、生成されたスキルと正本の一致、評価用fixtureとrunnerの構造を確認します。
実際のモデルによるスキル選択や出力品質は、別途検証が必要です。プラグインの構造を変更した場合は、
分離したCodex環境でマーケットプレイスの登録、プラグインのインストール、スキルが利用可能になることも確認してください。

マーケットプレイスの形式は、[OpenAI公式のプラグインパッケージングドキュメント](https://developers.openai.com/plugins/build/plugins)に従います。

</details>

## ライセンスと出典

リポジトリ全体に適用するルートレベルのライセンスは、現在宣言していません。各プラグインのライセンスと出典は次のとおりです。

- Engineeringには[MITライセンス](plugins/engineering/LICENSE)が適用されます。
- Quality Engineeringは複数のバージョンを固定したアップストリームソースに基づき、[Apache-2.0ライセンス](plugins/quality-engineering/LICENSE)、[NOTICE](plugins/quality-engineering/NOTICE)、[出典の対応表](plugins/quality-engineering/UPSTREAM.md)、[MITライセンスの原文通知](plugins/quality-engineering/THIRD_PARTY_NOTICES.md)を保持しています。
- Workflowには、現在個別のライセンスを宣言していません。
- Promptingには、現在個別のライセンスを宣言していません。
- Productには、現在個別のライセンスを宣言していません。
- Memory Managerは独自に作成したプラグインで、現在個別のライセンスを宣言していません。設計で参照した出典は[UPSTREAM.md](plugins/memory-manager/UPSTREAM.md)に記録しています。
- Figma Workflowは外部ファイルをコピーせずに独自に作成したプラグインで、現在個別のライセンスを宣言していません。参照した出典と外部ファイルをコピーしない方針は、[UPSTREAM.md](plugins/figma-workflow/UPSTREAM.md)に記録しています。
- Fluent Languagesのライセンスと各ソースの出典は、[LICENSE](plugins/fluent-languages/LICENSE)、[UPSTREAM.md](plugins/fluent-languages/UPSTREAM.md)、[THIRD_PARTY_NOTICES.md](plugins/fluent-languages/THIRD_PARTY_NOTICES.md)に記録しています。
- Researchは基準とした元のソースでライセンスファイルを確認できておらず、利用が許可されているとは推定していません。基準コミットと収録範囲は、[UPSTREAM.md](plugins/research/UPSTREAM.md)に記録しています。
