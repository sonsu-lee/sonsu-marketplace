# Research memos: state the judgment you need first

## Reader's question

What is known, what remains unresolved, and what should the reader decide?
Unlike minutes recording events or reports presenting established findings, a
memo starts discussion before a conclusion has settled. Include both a
provisional view and unresolved questions without presenting either as a final
decision.

## Required elements

- A central claim in the title or first sentence, not just 「〜について」.
  A proposal may say 「〜すべきである」; a tentative view must remain tentative.
- A title and opening understandable before reading the body. Do not use an
  unexplained 「A案」 or 「第2案」; say 「紙の申請書をやめて Web フォームにしたい」
  instead of 「A案を採用したい」.
- Scope and exclusions, but only those established by the material or user.
- Background, problem framing, proposals or issues, unresolved questions,
  and a conclusion.
- The decision requested by this memo, stated near the opening.

## Structure

State the main claim and requested judgment before background and problem
framing. If provisional, label it as the current view rather than hiding it
until the end. Readers who stop early should still know the memo's purpose.

Define concepts within prose rather than automatically creating a glossary.
Avoid three consecutive paragraph openings of 「Xとは〜である」. Mix supported
parenthetical definitions, such as 「起動率(アプリを開いてから災害情報を確認する
まで進んだ利用者の割合)」, with naming a concept after explaining it:
「この動線を、本メモでは平時導線と呼ぶ」.

Compare options on consistent axes, not unrelated pros and cons. Cost, adoption
speed, or another source-supported axis lets readers apply their own priorities.
Use 「—」 when an axis does not apply to an option; do not clutter the table
with administrative labels such as 「該当しない」 or 「記載なし」. Missing evidence
is not the same as inapplicability; disclose it rather than inventing a value.

Explain scope and deliberate exclusions briefly when provided: an issue may
have been settled elsewhere or lack information. Do not invent plausible
exclusions such as excluding customer inquiries.

## The author's provisional view

A memo gains value from the author's current view on unresolved questions,
such as 「現時点では A 案に傾いている」. Questions alone do not establish a
starting point for discussion. But the view belongs to the author, not the
editor. Use supplied views; if absent and necessary, ask which way the author
leans. Never add a new view while revising an existing memo.

The same restraint applies to conditional judgments, evaluation metrics,
schedules, stop/continue criteria, new contact routes, or procedures. A
plausible plan can become an unauthorized commitment if written as the author's.
Report gaps outside the document rather than filling them silently.

A view is not a priority ranking. When the argument applies equally to several
targets, keep them parallel rather than assigning 「最優先・次点・後回し」.
Try grouping unresolved issues by type before imposing stages or priority.

## Quality criteria

- The title or opening communicates a claim, not only 「〜についての検討」.
- Unresolved issues have the author's sourced provisional view, not only
  「今後の検討課題」.
- Comparison axes support an actual reader decision.
- Verified cases and numbers support the main claim. If removing every name
  and figure changes nothing, the material may be too generic.
- The reader knows what judgment is needed next.
- No unsupported metric, timetable, condition, comparison, or plan was added.

## Common failures

Conceptual discussion without primary information produces paragraphs anyone
could write: 「一般に〜と考えられる」 or 「〜というアプローチが有効である」.
Give depth to the two or three issues with actual material and keep the rest
short, without inventing a hierarchy. Do not end with unresolved questions and
no author view; equally, do not fabricate the missing view or figures.

The most relevant principles are claim-first openings, prose for causality,
explicit uncertainty, and separation of primary findings from the author's
interpretation. Use 「〜と考える」 and 「〜と推定する」 accurately.

## Disaster-app concept example

Supplied material: a prefectural report finds municipal disaster apps are
opened infrequently during disasters relative to downloads. The author thinks
this is because there is no reason to open them routinely. Options are push
notifications, siren integration, or both. Comparison axes are delivery speed,
battery use, and ease of retracting a false alarm. Push-only is fast but risks
distrust after false alarms; the author currently favors the combination.
Testing an older-user interface is unresolved because the team lacks usability
testing experience. The requested decision is funding external usability work.

A weak opening merely names the topic and lists questions:

> 地域防災アプリの検討について
>
> 本メモでは地域防災アプリの可能性について検討する。
> これらについては今後さらなる検討が必要である。

A supported alternative puts the claim and its certainty first:

```markdown
# 防災アプリが災害時に開かれない原因は、平時に開く理由がないことだと考える

県の報告書によると、県内の自治体アプリは、ダウンロード数に比べて災害時の起動率が低い。
筆者は、原因は平時に開く理由がないことにあると考えている。このメモでは、
通知方式と高齢者向けの画面について、判断してほしい論点を示す。

通知方式の候補は、プッシュ通知だけ、サイレン連動、その組み合わせの3案で、
届く速さ・電池の消費・誤報のときの取り消しやすさで比べられる。
プッシュ通知だけの案は速いが、誤報のときに不信感を招きやすい。
筆者は現時点では組み合わせる案に傾いている。

未解決なのは高齢者向けの画面の検証方法で、社内にユーザーテストの経験がない。
外部の使い勝手調査に予算をつけるかどうかを、このメモで判断してほしい。
```

The source report is attributed; 「考えている」 and 「傾いている」 preserve
opinion as opinion, including in the title. There are no invented numbers,
comparison results, or new proposals.

## Distinguish the document's role

A memo precedes the decisions captured in [minutes](minutes.md) and the settled
findings emphasized in [reports](report.md). End with the judgment requested,
not an invented decision. Write for a response: specifying what judgment each
issue needs makes agreement or disagreement easier than merely delivering
information. Preserve the distinction between unresolved and decided throughout.
