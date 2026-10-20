# Meeting minutes: separate decisions and actions from discussion

## Reader's question

What was decided, and who will do what by when? Minutes are not a transcript
for its own sake. Readers may not have attended or may have forgotten details;
they should find decisions and actions within seconds rather than reread a
chronological account of everything said.

## Required elements

Include the meeting name, date and time, participants, discussion by agenda,
decisions, actions with owners and deadlines, and unresolved agenda items.
For new minutes, put decisions, actions, and unresolved items together before
the discussion. “Everyone will handle it” and “as soon as possible” do not
establish an owner or deadline. Mark a genuinely undecided owner as 「未定」.

When revising, never infer absent owners or deadlines. Do not add new columns
or sections whose contents would consist only of 「未定」. Preserve the source's
certainty: a proposal with supporters is not necessarily a decision.

## Structure

This structure is for new writing. Existing minutes retain their section order
unless the user requests restructuring or a concrete comprehension problem
justifies it under the skill's section 3. Otherwise propose moving decisions
forward rather than silently doing so.

Start with one bullet per metadata item: name, date/time, participants, and
pre-reading where supplied. Plain adjacent lines collapse into a Markdown
paragraph. Then state recording limitations in one paragraph: transcript
accuracy, whether a recording exists, confidence in speaker identification,
and the supplied correction channel. Do not invent any of these facts.

Next place decisions and unresolved items as lists; actions may be a table or
list of owner, task, and deadline. Divide the body by agenda item. Headings
communicate what was decided, deferred, or discussed. Describe the discussion's
chronology and causality in prose. A two-line item need not receive the same
space as a ten-line debate. An optional next-meeting note contains actual
changes for next time, not a repeated summary.

Noun endings and である style are appropriate; do not force polite endings.
Preserve a key quotation's spoken register. Changing 「それ先に言ってよ」 to
「それを先に言ってほしい」 loses force and information about the speaker.

## Quality criteria

- Decisions alone show what changed. 「引き続き検討する」 belongs under unresolved
  items, not decisions.
- An action identifies task, owner, and deadline when supplied:
  「田中: 在庫アラートのしきい値案を7/18までに作成」 is actionable;
  「アラートのしきい値については検討していく」 is not.
- Uncertain attribution remains explicit, for example 「(佐藤さんと推定)」.
- Discussion appears in prose; decisions and actions are easy to scan.
  Independent advice or lookup items may remain lists.
- Advice in a review or 1:1 includes the recipient's response when recorded,
  such as 「了承した」 or 「持ち帰って検討する」. Without it, a dialogue can look
  like a one-way lecture. Do not invent an unrecorded response.

## Common failures

Do not summarize every contribution at equal length: a five-minute confirmation
and a thirty-minute dispute deserve different weight. Do not flatten all
speakers into equally confident statements or equally tentative 「〜と思われる」.
Do not turn a proposal, support, or deferred decision into 「合意した」.

Removing 「えーと」 and 「まあ」 is insufficient if conversational padding
remains. A long request to take something back and discuss it internally can
be reduced to 「持ち帰って検討する」 when that preserves the actual commitment.
The most relevant principles are certainty, prose for causality, informative
headings, uneven emphasis, and restrained bold.

## Fictional example

The following names, dates, and decisions are illustrative material, not facts
to reuse in another user's minutes:

```markdown
# 在庫すいすい開発定例(2026-07-10)

- 出席: 田中(PM)、佐藤(バックエンド)、鈴木(デザイン)
- 記録: 田中のメモ。録音なし

発言者の帰属はおおむね確実だが、一部推定が入る箇所は「(推定)」と注記する。
訂正はこのドキュメントへのコメントで受け付ける。

## 決定事項

- しきい値の算出方法を在庫数から在庫回転率に変更する

## 宿題

- 田中: 回転率ベースのしきい値案を7/18までに作成
- 佐藤: 現行ロジックの改修範囲を7/15までに見積もる

## 継続議題

- 通知先をSlackに一本化するかは未定。次回、鈴木がUI観点の意見を持ち寄る

## 在庫アラートのしきい値は在庫数でなく在庫回転率で決める

現行のしきい値(在庫数10個未満で通知)は季節商品で誤検知が多いと佐藤が指摘した。
鈴木は、店舗担当者からも同様の苦情が来ていると補足した
(推定: どの店舗からかは未確認)。在庫回転率を基準にする案を田中が提案し、合意した。
```

## Preserve a deferred decision

Source:

> 田中さんから在庫アラートについて説明があり、現行のしきい値だと誤検知が多いという話になった。
> 佐藤さんはそれに対して在庫回転率を使う案を出し、鈴木さんも賛成した。
> 最終的にどう決まったかは次回また相談することになった。

When converting this account into minutes is requested, foreground the actual
outcome without inventing a decision or assignment:

> 在庫アラートの件は結論が出ず、次回また相談することになった。
> 田中さんから在庫アラートの説明があり、現行のしきい値では誤検知が多いという話になった。
> 佐藤さんが在庫回転率を使う案を出し、鈴木さんも賛成した。

The supported unresolved item is 「在庫アラートの件(次回また相談)」. No owner,
deadline, final agreement, or new speaker attribution may be added.
