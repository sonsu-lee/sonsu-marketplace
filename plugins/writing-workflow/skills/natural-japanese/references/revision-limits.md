# Revision limits

Read before changing negation, emphasis, connectors, certainty, lists, headings,
order, or paragraph grouping; when lint reports `negation_repetition` or
`antithesis_repetition`; and when judging whether a rewrite adds content. The
mandatory rules in [the skill](../SKILL.md) (do not add content; the short
list of things never to do in revision) always apply, whether or not you open
this reference.

## Preservation examples

When revising, an addition includes changing certainty (turning a further
discussion into an agreement, a possibility into a decision, or a definite
statement into a guess), inventing experience or endorsement (「これには何度も
助けられた」, 「筆者としては〜をすすめる」), imposing a numerical framework absent
from the source (「理由は3つある」), changing figures or table values (even
apparent errors; report discrepancies), and adding generic warnings or
explanatory paragraphs. Only directly supported clarification is allowed: an
abbreviation's expansion, a short term explanation, or a connective expressing
an existing relationship. Never invent that relationship.

For example, the source says:

> 佐藤さんが在庫回転率を使う案を出し、鈴木さんも賛成した。
> 最終的にどう決まったかは次回また相談することになった。

Do not turn it into an agreement, assign 田中, or invent a 7/18 deadline. A
faithful revision is:

> 在庫回転率を使う案が佐藤さんから出て、鈴木さんも賛成した。
> 決定は次回に持ち越した。

Likewise, 「作業効率を大幅に向上させることができると言えるでしょう」
can become 「作業の効率は大きく上がるだろう」. Keep the tentative
「だろう」, not the stronger 「はずだ」. 「この事実は、従来の前提が
誤っていたことを示している」 can become 「この事実から、従来の前提が
誤っていたと分かる」 without changing certainty.

## Keep only meaningful negation

For `negation_repetition` and `antithesis_repetition`, distinguish:

- A gratuitous rebuttal of something nobody asserted, often 「〜するだけで
  自動的に〜わけではない」: remove the sentence if the next sentence still
  connects and the negation adds no factual or safety information.
- 「AはBではない。Cだ。」 used only for emphasis: remove the rebuttal and join
  its subject to the positive statement without adding content.
- Necessary distinctions, misconceptions, warnings, and contrasts: keep them.
  Examples include SQLite not being a separate database-server process,
  environment variables not by themselves protecting secrets, or sending only
  changes rather than an entire file.

## Remove theatrics by deletion, not replacement

Remove content-free 「徹底的に」「劇的に」, exaggerated physical reactions,
or reader appeals only when the remaining sentence says the same thing and
is grammatical. 「圧倒的に多く」 becomes 「多く」, not 「非常に多く」. Do not
replace one dramatic flourish with another. Do not mechanically delete
「他ならない」 if doing so breaks the sentence. A purely emotional sentence
may be removable; intentional essay voice is an exception. Never delete
factual quantifiers or evaluations whose removal changes the claim.

## Structural changes require a reason

Change list/prose layout, paragraph grouping, heading count, or order only when
requested or when a specific misunderstanding or lookup problem justifies it.
Before such edits, list existing headings and sections as `keep` or `change`,
defaulting to `keep`. Explain if more than 30% change. Rewrite at most the two
or three headings whose contents are hardest to locate. Convert lists to prose
only when hidden causality or chronology requires it. Keep searchable advice
or task lists. Do not turn line-separated writing into bullets unasked.

When splitting sentences, reuse source language. Do not introduce 「しかし」,
「ただ」, 「その結果」, 「そこで」, or 「そのため」 without a source relationship;
existing 「〜が」「〜ので」「〜ため」 may be retained.

## Never do these during revision

- Add new content, empty bridge sentences, or a new summary section. Suggest
  moving a conclusion forward rather than silently adding a new structure.
- Supply a missing subject or speaker by guesswork, especially in minutes.
- Correct numbers silently, including “three points” followed by four items.
- Add examples or figures to a generic paragraph. Identify needed material.
- Delete claims, examples, evidence, exceptions, or conditions as “repetition”.
  Remove only repetition adding no information; keep ambiguous cases.
- Fill absent genre elements with boilerplate. Ask if needed and unsupported.
- Flatten the author's voice: quotations, honorific level, emoji, arrows,
  abbreviations, spelling habits, intentional line breaks, or uneven sections
  remain unless they obstruct comprehension.
