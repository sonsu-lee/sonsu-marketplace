---
name: natural-japanese
description: >-
  Write, revise, or diagnose natural, readable Japanese prose, including
  technical documents, README and API documentation, design documents,
  runbooks, release notes, technical blogs, PR descriptions, meeting minutes,
  reports, guides, research memos, proposals, email, slides, and essays.
  Use for awkward, verbose, translation-like, or formulaic Japanese and
  requests to learn the author's style. Diagnosis does not rewrite the text.
  Not for translation, other-language prose, or authorship detection.
license: MIT
compatibility: >-
  Script-assisted review requires uv and Python 3.10+; uv resolves the bundled
  scripts' SudachiPy and SudachiDict-core dependencies. Manual review is
  available when script execution is unavailable, not as a runtime-failure bypass.
metadata:
  upstream: https://github.com/coji/natural-japanese
  source-commit: 03bc944a0c4a9f0b2a66eab065b30de5c529bf08
---

# Natural Japanese

Write and revise Japanese that readers can understand without reconstructing
what the writer meant. Mechanical detection belongs to `scripts/lint.py`;
deciding whether a finding warrants a change belongs to the editor. Do not
stack another humanizer over this skill. Keep other-language passages in their
language; route them to the appropriate skill rather than translating them.

All prose genres are eligible, including technical and mixed code/prose files.
Edit prose, not executable code, identifiers, commands, quoted statements,
numbers, URLs, or established technical terms. Genre changes editorial
priorities and lint thresholds; it does not exempt a whole document.

## Most important rule: do not add content

When revising, do not add facts, numbers, people, dates, conditions, judgments,
opinions, or policies absent from the original. Even a true addition would be
presented as something the author said. These changes also count as additions:

- Changing certainty: turning a further discussion into an agreement, a
  possibility into a decision, or a definite statement into a guess.
- Inventing experience or endorsement: 「これには何度も助けられた」 or
  「筆者としては〜をすすめる」.
- Imposing a numerical framework absent from the source: 「理由は3つある」.
- Changing figures or table values, even apparent errors. Report discrepancies.
- Adding generic warnings or explanatory paragraphs absent from the source.

Only directly supported clarification is allowed: an abbreviation's expansion,
a short term explanation, or a connective expressing an existing relationship.
Never invent that relationship. Preserve claims, examples, evidence,
exceptions, conditions, attribution, and strength of evaluation.

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

For new writing, use supplied material and researched facts with attributable
sources. Identify missing material instead of guessing. Never manufacture
firsthand experience, decisions, or supporting numbers.

## Modes and runtime

Natural-language requests select the same operations as explicit mode names:

- **write:** draft from a topic and authorized material, then revise.
- **edit:** revise existing prose; this is the default when text is supplied.
- **score:** diagnose without changing the document. Read
  [diagnosis](references/diagnose.md) before scoring; it owns the formula and
  output format. Do not rewrite until asked.

Choose **quick** by default. Do the work inline, read only the matching
`references/doctypes/` file, run lint even for short text, and complete the
paragraph-by-paragraph review in section 3. A single sentence can trigger
phrase checks even when statistical detectors have too little data. For
structure, read headings and each paragraph's first sentence in sequence.

Use **full** when requested, for high-impact external or executive documents,
or for documents over roughly 10,000 Japanese characters. Also run
`outline.py`, `terms.py`, and the full structure and readability review in
section 5. Do not split authorship between agents: emphasis and transitions
require one view of the whole document. Parallel reading is useful only when
it genuinely helps with a long document; retain editorial responsibility.
When uncertain, finish quick and mention that full review is available.

### Resolve installed resources before running scripts

Relative links in this skill are relative to this skill's directory, never the
caller's repository. In omp, read resources through
`skill://natural-japanese/<relative-path>`. For execution, obtain the actual
loaded skill directory from omp's skill location and set `SKILL_DIR` to that
absolute directory. Do not guess a cache path or pass `skill://` to Python.
Keep the caller's working directory and pass quoted target paths:

```sh
uv run "$SKILL_DIR/scripts/lint.py" --json --genre tech "$TARGET"
```

All commands below use the same `SKILL_DIR` and `TARGET`. Choose `--genre tech`,
`business`, or `essay` when known; omit it when uncertain. Python imports resolve
beside the script, so no source checkout, development files, or corpus is
needed. Use the project's configured runtime when one exists. Otherwise uv
uses the scripts' inline dependency declarations. Do not change project
configuration, global installations, user settings, or hooks to use this skill.

If execution is unavailable, use [manual review](references/manual-checklist.md)
and disclose that no mechanical checks ran. A configured runner, dependency,
input, or script failure is not permission to silently switch to manual review
or a different runner. Report the failure and resolve its cause; if it remains
blocked, label any manual observations separately. Do not fabricate scores.

Findings return exit 0 even when numerous; input errors return nonzero. Read
stderr as well as JSON. A malformed baseline can produce an upstream warning
and omit comparison: do not claim convergence from such a result. Fix the
baseline rather than treating the warning as a successful comparison.

The optional upstream semantic-model experiment is not shipped here. There is
no `exp` mode or automatic model download in this adaptation. A request for it
must explain that limitation, not silently relabel full review as experimental.

## 1. Decide before writing

### Reader, purpose, and document type

Identify who will read the document and what they should understand or do.
Use available context first; ask about genuinely missing material. Read the
matching reference when the type is known:

- [Meeting minutes](references/doctypes/minutes.md).
- [Research and analysis reports](references/doctypes/report.md).
- [Internal guides and manuals](references/doctypes/guide.md).
- [Research memos, discussion papers, and proposals](references/doctypes/memo.md).
- [Slide outlines](references/doctypes/slide.md).

### Main message, headings, and emphasis

Write the main message in one sentence before drafting. If you cannot, inspect
the material gap. Prefer headings that communicate the section's conclusion,
not empty labels like 「背景」 or 「まとめ」. Read headings alone to check the
argument. Do not force every heading into 「noun: conclusion」. Short sections
may retain labels. If conditions cannot fit in a heading, use a topic heading
rather than an unconditional overstatement. A planned result in the body must
not become a certainty in the heading.

Allocate space according to substantive importance. Equal-length sections and
identical sentence patterns hide differences in importance. Unequal length is
not ranking: do not turn parallel topics into 「最優先・次点・後回し」 unless the
material establishes that order.

### Material for a new draft

Collect names, figures, and concrete events. A claim that remains unchanged
without any of these may need better material. If research is appropriate,
form a provisional claim, look for evidence that supports or challenges it,
and revise it once or twice. Otherwise ask for examples, numbers, or primary
information. If none exists, disclose that the result will be general; do not
invent specificity.

### Optional author profile

Read `style-profile.md` in the target project root or the user's specified
location if present. Otherwise use general guidance. Only when asked to learn
the author's style, extract tendencies from three to five prior pieces using
[the profile template](assets/style-profile-template.md). Describe tendencies,
not certainties. Record author-rejected expressions with their source and
scope; prohibit only the specific combination, not the whole word or its use
by everyone. Do not create a profile automatically.

## 2. Principles for writing

For revision, apply these principles only within source content and the
changes justified in section 3. A principle is never a reason to add a missing
next action, source, opinion, or decision. Resolve conflicts in favor of actual
reader comprehension and the document-type guidance.

1. Put the conclusion in the title or first sentence. Avoid empty openings
   like 「本稿では〜について解説する」. For long new documents, follow with a
   short conclusion and key figures.
2. Use informative headings, subject to conditions and genre exceptions.
3. Explain causality and chronology in prose. Lists hide 「だから」 and
   「しかし」 when events depend on each other. For example, 「在庫が減って
   通知は出たが、担当が見落として欠品した」 preserves the relationship better
   than four isolated bullets. Use lists for genuinely independent items and
   lookup tasks. Never invent a causal relationship.
4. Explain what a technical concept does before naming it, or give a short
   parenthetical explanation at first use when the source supports it.
5. Support abstractions with supplied names, numbers, or examples. Identify
   missing evidence rather than guessing.
6. Reserve bold for the few points that truly need emphasis. Do not decorate
   work documents with added emoji or symbols. Preserve intentional existing
   authorial marks unless they obstruct understanding.
7. Give important topics more space, without inventing priorities.
8. Do not repeat a definition, section pattern, or sentence opening three
   times. Reorder sentences or subjects, or combine related sentences. Do not
   insert rhetorical questions or noun endings just to vary the pattern.
9. Use negation only for a real misconception, factual distinction, or needed
   warning. Do not invent a misconception merely to refute it.
10. Distinguish established facts, estimates, and unknowns. Use 「〜と推定する」
    for an estimate and 【要確認】 for an unresolved fact. Do not scatter vague
    「〜と思われます」 everywhere. When editing, preserve the original degree
    of certainty; replacing its expression must not strengthen it.
11. Separate fact from opinion. Attribute data and mark the speaker of an
    opinion, such as 「筆者は〜と考える」. Do not present an unsupported claim as
    a fact or invent the author's view.
12. End with one or two useful sentences, not a repeated summary. A new report
    should connect supported findings to the next action. Label a genuinely
    authorized, evidence-based proposal as a proposal. Guides or minutes may
    need no concluding paragraph. Do not add next actions when revising a
    source that has none.

Keep です・ます and である style consistent unless existing intentional voice
requires otherwise. Aim for one claim per sentence and roughly 50–60 Japanese
characters, but do not shorten away a necessary actor or relationship. Put
long modifiers before short ones and keep subjects near predicates.

Technical prose prioritizes one meaning per sentence and consistent terms.
Business prose prioritizes the conclusion first. Essays may intentionally defer
a conclusion or leave resonance rather than state everything. Public-facing
or non-specialist prose needs shorter sentences, explicit subjects when known,
and fewer loanwords or double negatives. None of these priorities permits
inventing an actor, changing a technical term, or weakening a safety condition.

## 3. Revising an existing document

Use the same process regardless of whether a person or model wrote it. Text
alone does not reliably establish authorship. Distinguish necessary edits,
conditional structural edits, and prohibited changes.

### Necessary review, paragraph by paragraph

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

The lint JSON includes `paragraphs`; human output includes a numbered review
sheet covering headings, list items, table rows, and prose. Review every unit,
including in quick mode. Before editing, write `number: phrase → referent` for
problems and `number: none` otherwise, through the final unit. Record whether
each identified issue was fixed or retained with a reason. The same sheet is
available separately:

```sh
uv run "$SKILL_DIR/scripts/paragraphs.py" "$TARGET"
```

Preserve conditions when revising summaries or headings. 「年間契約で、月の
利用が100回を超えるユーザー」 cannot become merely 「よく使うユーザー」.
Split a summary if needed; use a heading like 「割引の対象」 if conditions are
complex. Do not replace unflagged, comprehensible language just because an
alternative seems more natural: 「気軽に試せます」 and 「お知らせいたします」
need not become 「簡単に試せます」 and 「お知らせします」.

### Recover the concrete meaning behind vague wording

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

### Keep only meaningful negation

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

### Remove theatrics by deletion, not replacement

Remove content-free 「徹底的に」「劇的に」, exaggerated physical reactions,
or reader appeals only when the remaining sentence says the same thing and
is grammatical. 「圧倒的に多く」 becomes 「多く」, not 「非常に多く」. Do not
replace one dramatic flourish with another. Do not mechanically delete
「他ならない」 if doing so breaks the sentence. A purely emotional sentence
may be removable; intentional essay voice is an exception. Never delete
factual quantifiers or evaluations whose removal changes the claim.

### Structural changes require a reason

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

### Never do these during revision

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

## 4. Mechanical review and disposition

Run the lint command from the runtime section. It detects phrases, calques,
repeated negation, monotonous sentence lengths, absent noun endings, lexical
reuse, and English-like syntax. A finding is suspicion, not a mandate. Consult
its detail and hint, and decide from context. Reading the sentence aloud can
help. Record each finding's outcome in the response or scratch space:

```text
- [Fixed] translationese「〜という点で」: changed to「〜では」.
- [Kept/product name] forbidden_phrase「多角的」: part of「多角的レビュー機能」.
```

Use concrete reasons such as quotation, technical term, needed contrast, or
genre convention. “Kept” without a reason is not an editorial decision.

## 5. Structure and readability

Lint examines surface patterns; sparse findings in minutes or slides say
little about their structure. In full mode run:

```sh
uv run "$SKILL_DIR/scripts/outline.py" "$TARGET"
uv run "$SKILL_DIR/scripts/terms.py" "$TARGET"
uv run "$SKILL_DIR/scripts/lint.py" --reading-load --genre tech "$TARGET"
```

Use the appropriate genre, not always `tech`. `--reading-load` is a separate
editorial lane: it does not enter the naturalness score or baseline comparison.

Read headings and paragraph openings consecutively. Check whether the argument
can be followed; headings communicate useful content; repeated definitions,
openings, or section structures obscure emphasis; and the conclusion arrives
when the reader needs it. Do not force a suspense plot onto factual prose.
Chronology can be evidence in incident analysis or intentional in an essay.
For new reports, check supported next actions; for revisions, only assess
those present in the source. Apply the matching document-type reference.

Review readability in this order:

1. Nested negation and conditions. Preserve truth conditions: 「設定が無効でない
   限り」 and 「設定が有効なら」 differ when unset. Do not simplify away that
   distinction or an intentional reservation.
2. Dependencies: split multiple claims; align subject and predicate; put long
   modifiers first; punctuate structural boundaries. Check repeated 「〜が、」
   and whether 「これ」「それ」 has exactly one antecedent.
3. Lexical burden: inspect runs of seven or more kanji and three or more 「の」.
   Restore verbs where nominalizations hide action. Clarify repeated passives
   only when the actor is known. Replace ambiguous loanwords when accurate,
   without changing established terms or identifiers.
4. Redundancy: 「〜することができる」 → 「〜できる」 and 「〜という形になる」
   → 「〜になる」 when no information is lost.
5. Paragraphs: avoid both unbroken walls and fragmentation that cuts connected
   reasoning. Respect intentional existing line breaks.
6. Embedded lists: expose three or more parallel items only when their sentence
   is too long. Do not default every item to **bold label** plus explanation.
7. Cross-paragraph repetition: remove only information-free duplication.
8. Terminology: use consistent names; `terms.py` lists first uses and possible
   explanations for editorial review.
9. Structure and assumed knowledge: check delayed conclusions and unexplained
   specialist concepts, within the revision limits in section 3.

Brevity is not the goal. First preserve facts and grammatical relationships;
only prefer shorter wording between equally faithful candidates. A clearer
split sentence or list may be longer.

## 6. Converge and finish

After editing, rerun lint. Pass the previous JSON file with `--baseline` to
classify findings as `resolved`, `new`, or `persisting`:

```sh
uv run "$SKILL_DIR/scripts/lint.py" --json --genre tech \
  --baseline "$BASELINE" "$TARGET"
```

Finish when every finding is fixed or explicitly retained with a reason and
edits introduce no unresolved new findings, not after an arbitrary iteration
count. If a finding recurs twice, reconsider the sentence or paragraph rather
than cycling synonyms, or retain it with a reason. A low finding count is not
proof of linguistic quality, factual fidelity, or human authorship.

Compare the revision with the exact pre-edit source. Preserve that source in
scratch space before overwriting when it is not otherwise available. For a
new draft, compare against authorized material and perform the paragraph-level
concrete-meaning review too. These helpers list newly appearing numbers,
proper nouns, and ASCII words:

```sh
uv run "$SKILL_DIR/scripts/newfacts.py" "$ORIGINAL" "$TARGET"
uv run "$SKILL_DIR/scripts/newfacts.py" --git "$TARGET"
```

`--git` compares against HEAD, not against pre-existing uncommitted changes.
Use it only when HEAD is the intended original; otherwise use the captured
pre-edit copy. Remove unsupported additions or restore original content.
Directly supported expansions may remain. The helper cannot detect added
ordinary-noun details, changed certainty, lost conditions, or swapped speakers;
manual comparison remains mandatory even when output is empty.

## 7. Working files

Keep lint JSON, disposition notes, original copies, and draft backups in the
environment's scratch directory or a directory created with `mktemp -d`, not
beside the target. Remove only your temporary working files when finished.
Leave only the requested final document and, when explicitly requested, an
author profile in the user's project. Do not publish or transmit target text.

## Sources

Adapted from [coji/natural-japanese][source] at commit
`03bc944a0c4a9f0b2a66eab065b30de5c529bf08`, under the exact upstream
[MIT license](LICENSE), copyright 2026 coji.

Instructions and supporting guides are translated into English while keeping
Japanese examples and linguistic distinctions. The runtime retains upstream
detectors, Japanese diagnostic text, and dependency ranges. Local fixes exclude
fenced examples from structural statistics and keep document-wide findings
stable across baseline comparisons without changing detector thresholds.
This adaptation removes client-specific metadata, resolves resources relative
to the installed skill, makes runner failures explicit, and preserves technical
prose eligibility. It omits upstream `semantic.py` and `exp` diagnosis (an
optional approximately 1 GB model download), corpus calibration, development
checks, release/install scaffolding, and benchmark fixtures. No remaining
workflow invokes those omitted components.

[source]: https://github.com/coji/natural-japanese/tree/03bc944a0c4a9f0b2a66eab065b30de5c529bf08/skills/natural-japanese
