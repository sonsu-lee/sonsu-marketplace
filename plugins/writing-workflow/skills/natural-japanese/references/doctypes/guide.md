# Internal guides: readers open them when they need an action

## Reader's question

How do I do this now? Teaching the whole system is not the primary purpose.
Readers often arrive from search or a contents list and read one section only.
Judge a guide by whether that isolated section enables the task, not merely by
how smoothly it reads from beginning to end. This reference covers structure
and navigation; use [writing principles](../writing-principles.md) for
sentence-level guidance.

Technical guides, API guides, README instructions, and runbooks remain eligible
for natural Japanese editing. Preserve code, commands, identifiers, established
terms, exact UI labels, facts, and safety conditions.

## Required elements

For a new guide, include:

- Three or four numbered essentials: the minimum actions the reader must know.
- Intended reader, stated in the title or a short opening. Include prior
  knowledge only when it helps readers decide whether the guide fits them.
- What to read initially and what to consult later, for example chapters 1–3
  first, then chapter 4 onward as needed. A contents list alone is not enough.
- A glossary at the end, even for terms explained on first use.
- A supplied contact or route for questions not answered by the guide.

Do not invent missing procedures, contacts, or policies to fill this structure.
When editing, the source-preservation and restructuring limits still apply.

## Match structure to the section's purpose

Do not give every section the same construction. Different structures signal
how closely the reader needs to read:

- **Narrative introduction:** follow a task's flow in sequence.
- **Lookup:** map a goal or symptom to a method; each row can stand alone.
- **Hands-on:** one action per numbered step, followed by a brief reason.
- **Reference:** tables of parameters and settings rather than prose paragraphs.

Guide-specific lookup needs override the general preference for prose and
conclusion-style headings:

- A short welcome or reader-directed instruction may open a new guide. Follow
  with three or four essentials, then the reading route. Omit author-centered
  prefaces about who prepared the guide unless needed for the task.
- Use short recognizable headings such as 「VPN につながらないとき」 or
  「パスワードの再設定」 rather than full conclusion sentences. Give each
  discrete rule, operation, or exception a subheading. Use bullets and numbers
  within lookup items; place a needed reason briefly in parentheses at the end
  of the item rather than in a separate introductory paragraph.
- Number procedural steps, one action per step. Briefly identify the procedure
  before its steps. Put long explanations elsewhere rather than interrupting
  an operation to teach the underlying mechanism.
- Use bullets for deadlines, conditions, and exceptions.
- Prefer ordinary Japanese over 「該当の」「当該」「〜の際は」:
  「その節を開く」 rather than 「該当の節を開く」.
- Use two-column symptom/remedy tables. Contact routes can be issue/contact;
  glossaries can be term/meaning. Readers should find both halves on one row.
- Keep the reader as the subject of reader-directed instructions. 「全体会議で
  共有し、迷ったときに参照してください」 mixes the writer's sharing action
  with the reader's reference action; separate them when the source supports it.

Separate complex background into end-of-section notes. Do not introduce every
note or cross-reference with the same formula; say what that note explains.

## Quality criteria

- Contents headings identify actual tasks, not generic 「概要」 or 「利用方法」.
- A section works without reading the previous one. Avoid routine bridges such
  as 「ここまでで〜できました。ここからは〜です」 in lookup sections. A long
  narrative introduction may briefly explain its relation to the previous part.
- Repeated concepts are explained once; later sections link there and describe
  only their differences.
- Missing source material is disclosed, not filled with full-length boilerplate.
  Do not present an unfinished guide as complete; surface what is missing and
  use an existing inquiry route where supplied.
- Prohibited operations pair the action with its actual consequence, rather
  than ending only with 「注意してください」.

## Common failures

Equal-length sections and identical heading hierarchies obscure which topics
need more attention. Formulaic 「詳細は次章で解説します」 bridges add words
without connecting meaning. Never assert an unverified UI operation or result:
「〜と表示される想定」 distinguishes an expectation from verified behavior.
Only assert what the source or user has established.

Relevant principles are task-oriented headings, unequal emphasis, avoiding
repeated section and note patterns, and explicit certainty for unverified steps.

## Fictional guide excerpt

These policies and dates are fictional example material, not recommendations
or facts to insert in another guide:

```markdown
# 社内 VPN 接続ガイド(在宅勤務をする人向け)

在宅勤務を始める方へ。自宅から社内のシステムを使うときは、
このガイドの手順で VPN につないでください。

## まず覚えること

1. 社内のシステムを使う前に、VPN アプリで「接続」を押す
2. パスワードは90日ごとに変わる。期限の7日前に通知が届く
3. つながらないときは、下の「困ったとき」を見る

初回は「はじめての接続」だけを読めば足ります。
ほかの節は、必要になったときに開いてください。

## はじめての接続

1. 社内ポータルから VPN アプリをダウンロードする
2. アプリを開き、社員番号とパスワードを入れる
3. スマートフォンに届く確認コードを入れる

## パスワードの更新

- 90日ごとに更新が必要
- 期限の7日前に、メールで通知が届く
- 期限を過ぎると接続できなくなる(情報システム部で再発行が必要)

## 困ったとき

| 症状 | 直し方 |
| --- | --- |
| 「認証に失敗しました」と出る | パスワードの期限が切れていないか確かめる |
| つながるがすぐ切れる | 自宅のルーターを再起動してから、もう一度つなぐ |
| 確認コードが届かない | 情報システム部に連絡する |

## 問い合わせ先

| 困りごと | 連絡先 |
| --- | --- |
| 接続の操作 | 情報システム部(#it-help) |
| 在宅勤務の申請 | 総務部 |

最終更新日:2026年4月1日
```

The opening addresses the reader, not the author. Each operation or rule has
its own heading; numbers and bullets keep it searchable. Reasons remain short,
as in 「(情報システム部で再発行が必要)」. This is an excerpt rather than a
complete glossary-bearing deliverable.

## Expense-claim example

Supplied material: submit one claim per receipt because accounting reconciles
receipts individually; combined claims are returned. Transfers occur
automatically after approval, normally within three business days. Month-end
may delay them; the delay length is still being checked with accounting.

A generic 「概要」 paragraph hides the actions. Task headings make them visible:

```markdown
## 申請のしかた

- 領収書1枚につき1件で申請する。まとめて申請すると差し戻しになる
  (経理の突き合わせが領収書単位のため)

## 振込

- 承認後、自動で振り込まれる。通常は3営業日
- 月末は遅れることがある。どのくらい遅れるかは経理チームに確認中【要確認】
```

Keep the unresolved delay unresolved. Do not turn it into an invented service
level. For a lookup section, supplied facts can instead form independent
situation-to-method mappings:

- 「領収書をなくした」 → 「『紛失理由書』フォームから代わりに申請できる」.
- 「申請が差し戻された」 → 「理由は通知メールの末尾に書いてある」.
- 「海外出張の領収書が外貨」 → 「申請日のシステム内レートで自動で換算される」.

Unlike a narrative procedure, each mapping stands alone. Different sections in
the same guide can legitimately use different structures.

## Maintain through actual use

Reader questions provide evidence for the next revision. Show the last-updated
date and supplied question route. Expand sections that repeatedly cause
confusion rather than rewriting every section equally. Guides change current
behavior rather than merely recording historical events: obsolete instructions
can cause real operational errors. Do not hide the update date or silently
invent replacement behavior when its source is missing.
