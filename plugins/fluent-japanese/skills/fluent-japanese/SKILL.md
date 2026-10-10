---
name: fluent-japanese
description: 日本語の仕事文書・日常の連絡・技術説明・記事を作成・推敲するとき、AI臭さを診断するとき、自分の文体をプロファイル化するときに使う。技術文書の章構成やMarkdownの整形は別のスキルで扱う。
license: MIT
---

# Fluent Japanese

読者と目的に合わせて、自然で読みやすい日本語を書く。機械が見つけた疑いを文脈で判断し、事実・確実性・書き手の声を保って必要な箇所を直す。

## 手順

1. **対象とモードを決める。** `<skill-dir>` はこの `SKILL.md` があるディレクトリの絶対パスに置き換え、対象文書のパスも明示する。
   - `/fluent-japanese [quick|full] <対象>` は作成・推敲、`write [quick|full] <お題や素材>` は新規執筆。自然言語の依頼も同じように扱う。
   - `score [quick|full|exp] <既存ファイル>` は診断。[診断手順](references/diagnose.md)を最初に読み、その手順で評価して「結果」へ進む。結果を返したら手順7で中間ファイルを片付ける。
   - quick が既定。読者・主メッセージ・見出しを頭の中で確認し、該当する doctype の型を読む。ほかの参考資料は finding の判断に必要なものを開く。lint とスケルトン通読を行い、新規 finding がなければ1周で終える。
   - full は「しっかり」「時間をかけていい」という指定、対外・経営向けなど失敗コストの高い文書、目安1万字超の文書で選ぶ。開始前に所要時間の目安（短い文書で7分前後、1万字級で15〜20分）を伝える。短い文書でも outline・terms と三観点のレビューを行い、収束条件まで進める。軽くしたい場合は quick への変更を提案する。
   - Codex / Claude の quick はこの場で完結し、full の構造・読みやすさ・doctype照合は並列サブエージェントで行う。親が判断台帳と修正判断を統合し、執筆は文書全体を一人で扱う。effort を選べる場合は full に high、quick に low を推奨する。
   - OMP はセッションの model・effort・並列実行ポリシーに従う。full の三観点もこの呼び出し内で確認する。
   - 迷ったら quick で仕上げ、full でも磨けると添える。
2. **書く前に設計する。** 読者・目的・文書タイプを確認し、不明な点を聞く。主メッセージを一文にし、結論を含む見出しだけで論旨が通るか確かめる。
   - 型は[議事録](references/doctypes/minutes.md)、[調査・分析レポート](references/doctypes/report.md)、[社内ガイド](references/doctypes/guide.md)、[メモ・企画書](references/doctypes/memo.md)、[スライド](references/doctypes/slide.md)から選ぶ。記事・エッセイなどは内容に合わせて組み立てる。
   - 重要な節を厚く、補助的な節を軽くする。[濃淡設計と素材集め](references/revision-guide.md)に従い、主張を支える固有名・数値・一次情報が乏しければ集める。検索できない場合は素材を求め、得られなければ汎用的な内容になると伝える。
   - プロジェクトルートかユーザー指定の場所に `style-profile.md` があれば読む。プロファイル作成の依頼があれば過去文章3〜5本から傾向を抽出し、[テンプレート](assets/style-profile-template.md)で同じ場所に保存する。ユーザーが避けたいと指定した語の組み合わせは、その最小単位・出典・適用範囲を記録する。
3. **文体憲法に沿って書く。** モードによらず、コード・コマンド・識別子・ログ・URL・リンク先・引用・固定 UI 文言、数値と確実性を保持する。[文体憲法](references/writing-constitution.md)を基準にし、quick では次の要約を使う。細部の表現は次の検査で確認する。
   - 結論から入り、見出しにメッセージを置く。説明は地の文、真に並列な項目は箇条書きで圧縮する。
   - 専門用語は機能を説明してから名前を示し、固有名・数値で接地する。太字は文中の核1箇所だけに使う。
   - 濃淡をつけ、同じ鋳型を3回続けない。「〜ではなく」は実際の誤解を訂正するときに使う。
   - 限界・推定を明示し、事実と意見を分ける。結びでは主張を再統合し、レポートは So What まで示す。
4. **検査して判断台帳に記録する。** 文書ファイルは短くても lint を実行する。ファイルを作らない短い会話応答は同じ観点を目視で確認する。

   ```sh
   uv run <skill-dir>/scripts/lint.py --json <file>
   ```

   `findings` は疑いの位置と理由、`stats` は文書の統計。ジャンルが明確なら `--genre essay|tech|business` を付ける。終了コードは検出件数によらず0、入力エラーは1。実行できない環境では[手動チェックリスト](references/manual-checklist.md)を使い、未実行と区別して報告する。
   - finding ごとに[対応方針](references/revision-guide.md#lint-出力カテゴリごとの対応方針)を読み、[判断台帳](references/revision-guide.md#判断台帳)に「直した」か「残す（理由）」を記録する。文脈上自然な表現は残す。
   - **構造**: 見出しと各段落の先頭文で、論旨・メッセージ・鋳型の反復・濃淡・結びの So What を確かめる。business・tech の説明では主要回答を後半まで待たせていないか、事実とは別の予告・異変・種明かし・回収を繰り返していないかも見る。full は `uv run <skill-dir>/scripts/outline.py <file>` の行番号付き抽出を使う。
   - **読みやすさ**: [原則](references/readability-principles.md)と[悪文パターン](references/readability-antipatterns.md)をAから順に当て、語順・読点・一文一義・主述の距離・指示語・冗長表現を確認する。事実と係り受けを保った同等候補間で短さを選ぶ。分割や列挙の展開で長くなることもある。
   - 読解負荷の位置は `uv run <skill-dir>/scripts/lint.py --reading-load <file>` で拾える。`reading_load` は推敲の手がかりで、自然度の採点・baseline 比較とは別に扱う。
   - **doctype**: 選んだ型の必須要素と失敗例を照合する。full は `uv run <skill-dir>/scripts/terms.py <file>` で用語候補・初出行・回数・説明マーカーを読み、説明が十分か文脈で判断する。
   - 各レビューの所見も同じ台帳に入れる。素材不足なら収集へ戻る。full で環境が許すときだけ、opt-in の `uv run <skill-dir>/scripts/semantic.py --json <file>` で意味的な平板さも測る（torch・sentence-transformers、初回約1GBのモデル取得）。初回の取得前に伝え、findings は同じ台帳で扱う。
5. **収束を確認する。** 修正後に lint を実行し、直前の JSON を `--baseline <prev.json>` に渡す。`resolved`・`new`・`persisting` を読み、全 finding に判断が付き、修正が新規 finding を生まなくなるまで手順4を繰り返す。同じ finding が2周続く場合は[発散ガード](references/revision-guide.md#発散ガード)を使う。リライトは価値が増す箇所を選び、既存の濃淡を保つ。
6. **最終パスを読む。** full と重要な文書は[6軸ルーブリック](references/eval-rubric.md)で評価し、同資料の合格基準に届くまで弱い軸を改稿する。quick はその6観点で通読し、違和感を直す。
7. **作業ファイルを片付ける。** [作業ファイルの扱い](references/revision-guide.md#作業ファイルの扱い)に沿って、自分が作った台帳・lint JSON・下書きバックアップを削除し、完成文書と依頼された文体プロファイルを残す。

## 結果

- 作成・推敲: 完成文と、必要なら主な変更・残した表現の理由を返す。実行した検査と未実行の検査を分ける。
- 診断: [診断手順](references/diagnose.md)の `score.py` 出力を使い、スコア・バンド・機械ベース・判断調整、理由3〜5件、改善の優先順位2〜3件を返す。`status: too-short` は「診断対象として短すぎる」とし、数値を付けず所見だけ返す。採点は既存ファイルの score モードだけで行う。
- プロファイル: 傾向と根拠を記録した `style-profile.md` の場所を返す。

## 例

入力（チャット内の連絡文）:

> 「図書室の蔵書点検は木曜日に実施されることになります。そのため、当日は入室することができません。」を読みやすくして。

結果:

> 木曜日は蔵書点検のため、図書室に入れません。

日付・理由・利用できない範囲は保ち、重複する説明をまとめた。ファイルを作らない会話応答なので目視で確認し、自然度の数値は付けない。

対照例: 同じ文章を既存ファイルとして `score quick` で診断し、`score.py` が `too-short` を返した場合は、短すぎる旨と所見だけを返して原文を保持する。

## 境界

- score モードでは対象文書を書き換えない。リライトは依頼を受けてから行う。
- 技術文書の章構成・Markdown 整形は担当スキルに渡し、ここでは説明文の自然さと読みやすさを扱う。
- 後片付けで削除するのは、この作業で自分が作った中間ファイルだけとする。

## 参考資料

- [診断と採点ツール](references/diagnose.md)
- [語句のカタログ](references/forbidden-patterns.md)・[翻訳調](references/translationese.md)・[ジャンル別判断](references/genre-notes.md)
- [対応方針・判断台帳・収束](references/revision-guide.md)・[推敲の具体例](references/examples.md)
