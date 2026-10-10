# 診断モード（score）— 書き換えずに、AI臭さをスコアと理由で返す

診断モードは既存ファイルを評価し、スコア、その根拠、直すなら何からかを返す。「この文章、AIっぽい？」「どれくらいAI臭いか採点して」という依頼に使う。リライトを求められたら SKILL.md の作成・推敲手順へ切り替える。

## 3段階の深さ

診断の深さは次の内容に読み替える。SKILL.md 手順1の quick・full の説明と食い違う場合はこの節を使う。

- **quick（既定）**: `lint.py --json` を1回実行し、ジャンルが分かれば `--genre` を付ける。スケルトンを一瞥する。Codex / Claude ではこの場で完結する。OMP ではセッションの並列実行ポリシーに従う。30秒程度
- **full**: quick に加えて `outline.py` / `terms.py` を実行し、構造レビュー・読みやすさレビュー・doctype照合を判断に織り込む。Codex / Claude では三観点を並列サブエージェントへ委譲してよい。OMP ではセッションの model・effort・並列実行ポリシーに従い、三観点をこの呼び出し内で確認する。1周の評価で完結する。数分
- **exp**: full に加えて `semantic.py --json` を実行する。EXPERIMENTAL な深層検出で、torch 依存と初回約1GBのモデルダウンロードを伴うため、初回は開始前に伝える。表層を磨いた文書に残る話題の平板さまで見る

## スコアを計算する

スコアは0〜100の自然度で、**高いほど自然（AI臭が薄い）**。ユーザーへ返すときも向きを一言添える。lint の JSON を `mktemp -d` で作った一時ディレクトリに保存し、同じ対象文書と一緒に `score.py` へ渡す。結果を返したら、この一時ディレクトリを削除する。

```sh
uv run <skill-dir>/scripts/lint.py --json <file> > <lint.json>
python3 <skill-dir>/scripts/score.py <lint.json> --file <file> --mode quick
```

full は構造・読みやすさレビューの所見を `--adjustment <点>` に入れる。exp は semantic の JSON も保存して渡す。

```sh
python3 <skill-dir>/scripts/score.py <lint.json> --file <file> --mode full --adjustment -4
python3 <skill-dir>/scripts/score.py <lint.json> --file <file> --mode exp --semantic-json <semantic.json> --adjustment 3
```

| 出力 | 意味 |
|---|---|
| `status` | `scored` または `too-short`。本文の文字数が100未満なら `too-short` |
| `characters` | 改行・Markdown 記法を含む本文全体の文字数 |
| `counts` | 採点に使った severity 別件数。lint の `findings` と、exp の `semantic_topic_flatness` だけを数える。`reading_load` と baseline の解消済み項目は数えない |
| `mechanical_score` | `max(100 − (critical×8 + warn×4 + info×0.5) × 1000 / max(文字数, 1000), 20)` |
| `adjustment_range` | quick は `[0, 0]`、full / exp は `[-15, 15]` |
| `score` | 機械ベースに調整を加え、0〜100に切り詰めた最終値 |
| `band` | 下のバンド。`too-short` では `null` |

終了コードは、計算できた場合と `too-short` が0、入力ファイル・JSON の不正が1、引数・モード・調整範囲の不正が2。

結果ごとに次のように返す。

- `scored`: 内訳（機械ベース、判断調整、最終スコア）を示す。quick は「quick の精度は粗い」と添える。
- `too-short`: 数値を付けず「診断対象として短すぎる」と返す。
- 終了コード1・2: 原因を直して再実行し、計算できなかった値を推定で埋めない。

判断調整では、lint が拾えない構造のAI臭（全節同型、フラット列挙、確信度の平坦化、So What の空洞、順序・段階の押し付け）を減点する。文脈上自然と判断した lint の誤検知は減点を戻す。スコアは判断を含む目安で、同じ文書でも数点揺れる。結果には CI のゲートに使う数値ではないと一言添える。

## バンドと言い方

| スコア | バンド | 伝え方の例 |
|---|---|---|
| 90〜100 | 自然 | AI臭はほぼ見当たらない。指摘があっても好みの範囲 |
| 70〜90未満 | 軽微 | 数カ所に癖が残るが、読者が「AIっぽい」と感じる可能性は低い |
| 50〜70未満 | 要修正 | 表層か構造のどちらかに明確なAI臭がある。直す価値がある |
| 0〜50未満 | 濃厚 | 複数のカテゴリで強く検出。リライト推奨 |

## 出力の形式

1. **スコアとバンド**（機械ベースと判断調整の内訳つき）
2. **理由トップ3〜5**: カテゴリ名でなく中身で書く。「『〜ではなく』の対比が全文の4%で機械的なリズムになっている（L12ほか）」のように、代表箇所の行番号と、なぜそれがAI臭なのかを一言で示す
3. **直すなら何から**: 効果の大きい順に2〜3個挙げ、「リライトしますか（quick/full）」と添えて終える

理由は lint の detail を文書の文脈に即して言い直す。スコアを最も動かした所見に絞り、すべての findings を並べない。
