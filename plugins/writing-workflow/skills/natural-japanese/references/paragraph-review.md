# Paragraph review and concrete meaning

Read before writing the paragraph review sheet whenever you edit existing prose
or review a new draft. Score-only requests do not need it. It supplies the
sources of reader effort and the vague-wording patterns that the numbered sheet
in section 3 of [the skill](../SKILL.md) asks you to name. All preservation
rules in the skill override it.

Use the same process whether a person or model wrote the text; text alone does
not reliably establish authorship. Distinguish necessary edits, conditional
structural edits (see [revision limits](revision-limits.md)), and prohibited
changes.

## Necessary review, paragraph by paragraph

Review lint findings in context, empty exaggeration, unnecessary negation, and
these sources of reader effort:

- Redundancy: 「〜という形で進めていく予定です」 → 「〜で進める予定です」.
- Sentences with multiple claims: split without inventing logical connectors.
- Lists or paragraphs whose subject becomes clear only at the end: introduce
  the frame with words already in the source.
- Vague headings: clarify using the body's language, not one uniform pattern.
- Unexplained key terms: add only directly supported short explanations,
  such as 「SLA(サービスの品質を保証する取り決め)」.
- Vague verbs and nouns whose actual referent the reader must guess.

Preserve conditions when revising summaries or headings. 「年間契約で、月の
利用が100回を超えるユーザー」 cannot become merely 「よく使うユーザー」.
Split a summary if needed; use a heading like 「割引の対象」 if conditions are
complex. Do not replace unflagged, comprehensible language just because an
alternative seems more natural: 「気軽に試せます」 and 「お知らせいたします」
need not become 「簡単に試せます」 and 「お知らせします」.

## Recover the concrete meaning behind vague wording

For every paragraph, examine its verbs and nouns: can the concrete referent be
named using source facts or code? If so, do not leave a broader, ambiguous
paraphrase. Look for these seven patterns, especially in technical articles
and PR descriptions:

1. Opaque metaphors: 「チームの重心を移す」 does not say what changes.
2. Renaming something already named: 「注文が宙に浮く」 could mean remaining
   unpaid or losing references. Keep the established name for a state or field.
3. Personification: 「設定ファイルが育っていく」「データが語っている」.
4. Literal English calques: 「低くぶら下がった果実」「既存の利用者を壊す」
   「真実の源」. Prefer ordinary source wording when available.
5. Unnatural collocations: 「期限が終了する」 → 「期限が切れる」;
   「リスクを踏む」 → 「リスクを負う」.
6. Spoken engineering slang obscuring actions: 「ログを吐く」「サーバーが死ぬ」
   「キューに投げる」 can become 「出力する」「止まる」「渡す」 when accurate.
7. Nominalized actions hiding actors or behavior: 「重複登録が起きうる点の対処」
   can become 「同じ利用者が二重に登録されないように直す」 when supported.

Do not rely on a general impression of naturalness. For patterns 4, 5, and 7:

- Mentally back-translate suspicious phrases: 「一級市民」, 「優雅な劣化」,
  and 「端のケース」 can expose word-for-word calques. Established Japanese
  technical terms such as 「依存性の注入」 are exceptions.
- Try expressing nominalized actions with a subject and verb: 「権限の整理は
  未着手です」 may mean 「権限を誰に付けるかは、まだ決めていません」. Use
  that wording only if the source actually supports that meaning.
- Check whether noun–verb combinations occur in ordinary Japanese, especially
  after replacing everyday verbs with formal compounds.

Keep clear idioms such as 「目を通す」「手を打つ」「腰を据える」, exact
quotations, established domain terms, and unambiguous technical usages like
「キャッシュが効く」. Establishment means written specifications or references,
not merely popularity in engineers' conversation. Keep a metaphor whose
concrete meaning is stated in the same sentence. Review all confusing wording
in a paragraph, not only the first occurrence.

Replace vague wording with supported concrete actions, not stiffer compounds:
「設定ファイルに項目が増えていく」, not 「拡充される」. Preserve evaluation,
semantic breadth, attribution, certainty, and whether a statement is fact,
opinion, proposal, hypothesis, or hearsay. If context supports one reading,
state that reading in the change report. If equally plausible readings remain,
leave it unchanged and ask which meaning is intended.
