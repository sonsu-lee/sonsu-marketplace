# Sonsu Marketplace

[한국어](README.md) · [English](README.en.md) · [日本語](README.ja.md)

開発、リサーチ、プロダクト企画、文章作成に使えるCodex・Claude Code・ompプラグイン集です。
必要なプラグインを選んでインストールし、利用中のコーディングエージェントに作業を依頼してください。

[インストール](#インストール) · [プラグイン](#プラグイン) · [使用例](#使用例) · [ドキュメント](docs/README.md)

## インストール

### Codex

`codex plugin` コマンドに対応したCodex CLIで、GitHubのマーケットプレイスを一度登録します。
登録済みの場合は、この手順を省略してください。

```sh
codex plugin marketplace add sonsu-lee/sonsu-marketplace --ref main
```

必要なプラグインだけをインストールします。たとえば、ソフトウェア開発にはEngineeringを利用できます。

```sh
codex plugin add engineering@sonsu-marketplace
```

別のプラグインは、[下の表](#プラグイン)のインストール名に置き換えてください。
12個すべてをインストールする場合は、次のコマンドを実行します。

```sh
for plugin in \
  engineering workflow fluent-korean fluent-english fluent-japanese \
  writing research prompting product memory-manager design-patterns design
do
  codex plugin add "$plugin@sonsu-marketplace"
done
```

登録済みソースと各プラグインのインストール状態を確認し、新しいCodexタスクを開始してください。

```sh
codex plugin marketplace list
codex plugin list --marketplace sonsu-marketplace
```

Codexデスクトップアプリでこのリポジトリを開くと、`.agents/plugins/marketplace.json`の
ローカルカタログも表示される場合があります。同じ名前のGit登録元があるとローカルの
変更が隠れることがあるため、両方の項目が見えるだけではローカル版の読み込みを確認できません。
チェックアウトはGit登録元がない環境で[ローカル登録手順](docs/guides/adding-a-plugin.md#로컬-개발-환경)に従ってテストしてください。

### Claude Code

GitHubのマーケットプレイスを一度登録します。登録済みの場合は省略してください。

```sh
claude plugin marketplace add sonsu-lee/sonsu-marketplace
```

必要なプラグインだけをインストールします。たとえば、Engineeringをインストールする場合は次のとおりです。

```sh
claude plugin install engineering@sonsu-marketplace
```

[下の表](#プラグイン)の12個すべてをインストールする場合は、次のコマンドを実行します。

```sh
for plugin in \
  engineering workflow fluent-korean fluent-english fluent-japanese \
  writing research prompting product memory-manager design-patterns design
do
  claude plugin install "$plugin@sonsu-marketplace"
done
```

登録済みのマーケットプレイスとインストール状態を確認してください。

```sh
claude plugin marketplace list
claude plugin list
```

ローカルのチェックアウトを試す場合は、リポジトリのルートで
`claude plugin marketplace add "$(pwd -P)"`を実行します。どちらも`sonsu-marketplace`
という名前なので、使用するソースを一つ選んでください。
スキルは `/engineering:review` のように呼び出します。インストール・更新後は新しい
セッションで確認してください。CodexのコネクターとClaude CodeのMCP接続は別途設定します。

### omp

omp向けは `workflow`、`fluent-korean`、`fluent-english`、`fluent-japanese`、`design` の5件だけを
`.omp-plugin/marketplace.json` に登録します。開発実行・task・todo・session・reviewとメモリはomp標準の機能を使います。
ローカル変更を試す場合は[開発ガイド](docs/guides/adding-a-plugin.md)の分離環境を使ってください。

マーケットプレイスを登録して5件をインストールし、YAMLを `~/.omp/agent/config.yml` の
既存の `marketplace:` 項目に統合します。

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

`marketplace.autoUpdate: auto` はomp起動時に、24時間より古いカタログの更新を可能な範囲で試みます。
インストール済みプラグインの自動更新には、カタログ内の対象プラグインのバージョンを上げる必要があります。
`main` の常時監視や実行中セッションへのホットリロードではありません。新しいバージョンをすぐに
反映するには、カタログを更新してからインストール済みプラグインをアップグレードします。

```sh
omp plugin marketplace update sonsu-marketplace
omp plugin upgrade
```

スキルは `/skill:commit` のようにプラグイン接頭辞なしで呼び出します。カスタムロールのモデル設定は
追加しません。Fluent Koreanは現在のホストモデルによる単一呼び出しを使い、Claude Codeの
多段階・strictモードと固定Opusエージェントは配布しません。English・Japaneseの既存スキル、
Workflowのcommit・push・PRなどの権限境界、
Designの品質契約とプロファイルも変更しません。

`design`、`workflow`、`fluent-korean` は生成した `./plugins/<name>/omp` を配布元に使い、
English・Japaneseは元の `./plugins/<name>` を使います。omp向けパッケージには独自runtime extension、
hook、evidence gate、`task-continuity.py` を含めません。作業の継続はomp標準のtodo・sessionで扱い、
`.sonsu` へ新たな継続記録を書き込みません。詳細は[配布のライフサイクル](docs/architecture/plugin-lifecycle.md)を参照してください。

| 責任 | 担当 | 配布 |
| --- | --- | --- |
| 開発実行・task・todo・session・review | omp標準 | ホスト機能 |
| Git・チケット・PR操作の権限と成果物 | Workflow | 基本5件 |
| 言語別の文章品質・保護規則 | Fluent Korean・English・Japanese | 基本5件 |
| UI・prototype・handoff品質とnative tool前提 | Design | 基本5件 |
| 外部調査・製品探索・文章構成 | Research・Product・Writing | 選択候補。基本catalogには追加しない |

Research・Product・Writingを追加する場合は、必要なドメインと現在のnative tool契約を別途確認します。
Engineeringのompプロファイルは直接インストールした既存利用者向けに保持し、基本5件の設定には使いません。

#### 旧omp構成からの移行

旧11件構成または8件プリセットを使っていた場合は、次のうちインストール済みの旧プラグインを
ompからアンインストールします。インストールしていない項目の `not installed` エラーは無視します。
Codex・Claude Codeのインストールは変更しません。

```sh
for plugin in engineering writing research prompting product design-patterns memory-manager operations-ui interface-design figma-workflow; do omp plugin uninstall "$plugin@sonsu-marketplace"; done
```

登録済みの `sonsu-marketplace` がローカルのチェックアウトを指していたり、古いカタログを保持していたり
する場合があるため、GitHubのソースで登録し直します。マーケットプレイスの登録を外してもインストール済みの
プラグインは削除されません。インストール済みの `workflow`・`fluent-korean`・`design` は通常の
`install` では更新されないため、`--force` で再インストールします。

```sh
omp plugin marketplace remove sonsu-marketplace
omp plugin marketplace add sonsu-lee/sonsu-marketplace
for plugin in workflow fluent-korean fluent-english fluent-japanese design; do omp plugin install --force "$plugin@sonsu-marketplace"; done
```

旧プリセットのために追加した `skills.ignoredSkills`、`task.disabledAgents`、
`task.agentModelOverrides` の項目だけを設定から外します。独自に設定した別の項目は残してください。
プラグイン整理後はセッションを終了してompを再起動します。
読み込み済みの旧hook・agentは実行中セッションに残るため、同じセッションを使い続けないでください。
キャッシュ内のファイルは手で編集せず、既存の `.sonsu`・`.engineering` 記録も削除しません。

## プラグイン

以下はCodex・Claude Code向けの全プラグイン一覧です。omp向けの配布対象は上記5件に限ります。

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
| [Memory Manager](plugins/memory-manager/README.md) | CodexとClaude Codeで共有するローカルメモリの想起・保存・整理 | `memory-manager` |
| [Design](plugins/design/README.md) | 一般・運用UIの新規設計・再設計・監査をFigmaまたはコードで実施 | `design` |
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
| Memory Manager | 「`$memory-capture` この決定をプロジェクトのメモリに保存して。」 |
| Design | 「登録フローをFigmaで設計して。運用画面はコードで直接再設計して。」 |
| Design Patterns | 「この設計にパターンが必要か判断し、最小の実装形を選んで。」 |

ホストは依頼内容とインストール済みスキルの説明をもとに、必要なスキルを選びます。
Memory Managerの`$memory-recall`は関連する作業で選択され、明示的な保存依頼には
`$memory-capture`を使います。整理とスキル草案は`$memory-maintain`、`$memory-promote`で
明示的に依頼します。Claude Codeでは`/memory-manager:memory-capture`のように呼び出します。

ResearchのExa・Perplexity連携は任意です。利用可能なWebツール、ブラウザー、コネクター、ローカル資料でも調査できます。
DesignのFigmaキャンバスを操作するには、公式Figma MCP接続と、そのツールで必須とされるスキルが必要です。
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
