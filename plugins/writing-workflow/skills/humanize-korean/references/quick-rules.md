# Korean editing quick rules

The upstream quick-rule subset supports one-pass detection, editing, and
self-review. Use these IDs, not an improvised generic naturalness checklist.
For a diagnosis-selected ID absent here, read its entry in
[the complete taxonomy](diagnosis-rules.md) and apply its contextual conditions.

## Protected meaning and scope

Edit Korean prose in every genre, including technical documents and manuals.
Preserve code, identifiers, commands, URLs, numbers, units, dates, names,
attributed direct quotations, legal quotations, mathematical notation, and
technical terms. These are protected spans, not grounds to skip the document.
Authorial rhetorical quotation marks without an attributed speaker may be
edited; actual direct quotations may not.

List the core content nouns and concepts before editing. Preserve their lexical
forms at least once, while allowing particles and endings to change. Removing
empty modifiers must not remove these anchors or replace them with synonyms.
When uncertain, revert the sentence.

Preserve obligation, possibility, uncertainty, polarity, and their strength.
Moving a repeated modal sentence is different from deleting its modal marker.
Respect project terminology and required lists, headings, procedural order,
and intentional parallelism. Do not flatten technical prose into casual prose
or replace necessary passive or nominalized constructions to satisfy a quota.
All prescriptions below are subordinate to these protections.

Rates of at least 30% warn; at least 50% block acceptance. The bundled gates,
not self-estimates, determine rates. Metrics guide inspection, not authorship
claims or automatic replacements.

## A. Translationese

- **A-1 [S1]:** `~에 대해(서)` only when clustered at least three times in
  one paragraph. Preserve ordinary uses; upstream found humans using it more.
  Directly attach the object: `X에 대해 논의` → `X를 논의`.
- **A-3 [S1]:** `~에 있어(서)` → `~에서` or `~을 볼 때`.
- **A-5 [S2]:** Redundant `~와 관련하여/관련된` → `~에`, `~의` when equivalent.
- **A-6 [S2]:** Overused `~에 기반하여/바탕으로` → `~로`, `~을 보고`, retaining
  any meaningful basis or dependency relationship.
- **A-7 [S1]:** Literal have/make/take/give plus noun, including `가지고 있다`:
  restore a verb/adjective or double-subject construction.
  `강한 경쟁력을 가지고 있다` → `경쟁력이 강하다`.
- **A-8 [S1]:** Double passive `~되어진다/~지게 된다`: prefer a single passive
  or an equivalent active construction. `판단되어진다` → `판단된다`.
- **A-9 [S2]:** Unnecessary `~에 의해` passive: make the known actor the subject,
  as in `AI에 의해 생성` → `AI가 만든`. Preserve necessary passive focus and
  do not invent an actor.
- **A-10 [S2]:** The same `~할 수 있다` at least four times: vary only some
  forms, such as `~할 여지가 있다/~할 수도 있다`, if their certainty is identical.
  Never turn possibility into assertion. Preserve exact hedges in medical,
  legal, policy, and other precision-sensitive claims, even when repeated;
  work on sentence boundaries or order instead.
- **A-11 [S2]:** Preserve `~을 위해` by default; only relieve paragraph-level
  clustering with equivalent `~려고`, `~도록`, or `~위한`.
- **A-15 [S2]:** Abstract subject plus generic `보여준다/제공한다/가져온다`:
  restore the known concrete subject; use `X 때문에/덕분에/로 인해` for
  causatives and `~에 따르면 ~이다` for cognitive predicates. Do not change
  actual technical descriptions of what a system provides.
- **A-18 [S2]:** Three-or-more-word prenominal modifiers or nested relative
  clauses: split the sentence or use a following apposition, without losing
  the modified noun's constraints.
- **A-19 [S2]:** Double particles `~에서의/~에로의/~으로의/~에의/~으로부터의`
  can become clauses or simpler phrases. Plain `~의` is not a target.
- **A-20 [S2]:** `~되고 있다/~지고 있다` three or more times in one paragraph:
  vary some only if tense/aspect remains true. Keep isolated uses.
- **A-21 [S2]:** Inflated `단순한 X를 넘어 Y`: use `X만이 아니라 Y다` or remove
  only the empty escalation while retaining the proposition.
- **A-22 [S2]:** Added evaluation `~은/는 명확하다·분명하다`: state the proposition
  directly, preserving certainty with an adverb if needed. Keep a conclusion
  actually established by preceding argument. Not `분명히`, `명확히 하다`.
- **A-24 [S2]:** `더 이상 ~ 않다/아니다` twice in a document or in a concluding
  redefinition: consider `이제` or a change verb, never change a negative claim
  into an invented positive one. Preserve explicit termination of a previously
  stated condition. Never introduce `더 이상 A가 아니라 B` while editing.

## B. English terms and quotations

- **B-1 [S2]:** Repeated Korean-plus-parenthesized-English glosses: normally
  retain the first gloss and use consistent terminology thereafter. Preserve
  repeated definitions where independently readable API entries require them.
- **B-2 [S2]:** Explain empty promotional buzzwords, not established technical
  terms. Keep `API`, `SDK`, `CLI`, `prompt`, `token`, `embedding`, `agent`,
  `plugin`, `pipeline`, and `framework` when these are the audience's terms.
  Never mechanically translate `prompt` to `지시문` or `agent` to `대리인`.

## C. Structure and layout

- **C-2 [S2]:** Three or more consecutive decorative bullet blocks in a column
  or report can become prose. Keep meaningful lists, procedures, options,
  acceptance criteria, and intentionally parallel requirements.
- **C-5 [S1]:** Remove decorative emoji clutter in columns and reports; do not
  remove meaningful status notation or quoted content.
- **C-7 [S2]:** Mechanical paragraph openings `먼저–반면–결국`: remove one or
  two redundant transitions, preserving real sequence and contrast.
- **C-8 [S1]:** At least two chained `A인가, B인가`, `A가 아니라 B`,
  `~것이 아니라`, or `~것은 아니다` constructions: retain the effective one
  and vary the others asymmetrically. Do not eliminate all antithesis or
  introduce it into another sentence. Mere occurrence is not enough: human
  writers also use this rhetoric, often scattered rather than chained.
- **C-9 [S2]:** Decorative `1) 2) 3)` enumeration may become prose or
  `우선/다음으로`. Keep numbering used for procedures or cross-references.
- **C-10 [S2]:** Repeated decorative `X: Y` subtitle headings: simplify to a
  noun phrase. Preserve real section titles, labels, and navigation structure.
- **C-11 [S1]:** Unnecessary commas immediately after connective endings
  `-고/-며/-지만/-면서/-아서/-어서`: remove the comma or split at a suitable
  clause boundary. Three to five instances are S2; six or more are S1.
  The edited count must not increase. Do not touch code punctuation.

## D. Stock rhetoric

These are removal targets, never vocabulary to insert elsewhere.

- **D-1:** More than three `결론적으로/따라서/이를 통해/그러므로/요약하면/정리하자면`:
  keep one or two necessary transitions, remove redundant conclusion labels.
- **D-2:** Empty significance claims such as `시사하는 바가 크다/주목할 만하다/
  매우 중요하다`: remove, or state the concrete conclusion already present.
- **D-3:** Empty enumeration introductions such as `크게 세 가지로 나눌 수 있다`
  or `다음과 같은`: enter the content directly. Keep functional introductions
  to a table, command, or list when they orient the reader.
- **D-5 [S2]:** Personified abstract subjects such as `기술이 묻는다/시대가 부른다`:
  use the real known actor or a less personifying verb.
- **D-6 [S2]:** Formulaic `~할 때입니다/~시점입니다/~할 순간입니다` endings:
  state the same meaning with a concrete verb; normally at most one per text.
  Do not erase an obligation or invent an action.
- **D-7 [S2]:** Repeated `X에서 Y로/X을 넘어 Y로`: state the transition directly,
  retaining one effective formulation. Literal migrations remain precise.
- **D-8 [S2]:** Clefts `필요한/중요한 것은 ~이다` and `문제는/핵심은/관건은/답은`:
  connect subject and predicate. `필요한 것은 방향이다` → `방향이 필요하다`.
- **D-9 [S2]:** Concluding `(으)로 이어진다/~에 직결된다` and logical `결국`
  twice or more: state the supported causal path or use direct sentences.
  Keep at most one redundant conclusion formula; never inject `결국/이유다`.
- **D-10 [S2]:** Sentence-final `~하는 이유다`: use forward reasoning such as
  `그래서 ~다`, normally at most one per text. Never introduce this inversion.
- **D-11 [S2]:** Sentence-initial `향후/앞으로/중장기적으로` in the final 30%:
  remove vague temporal packaging, or use an actual source-provided condition
  or date. Never invent one.
- **D-12 [S2]:** Empty standalone `과제도 남아 있다/한계도 분명하다/아쉬운 점도 있다`:
  remove the signpost and lead with the real issue. Preserve substantive
  sentences such as `안전 기준 정비도 과제로 남아 있다`.
- **D-13 [S2]:** Formulaic essay-ending `어쩌면 ~일 것이다/비로소/천천히 ~이 됐다`:
  remove only empty reflective packaging, not uncertainty or genuine literary
  voice. This specific pattern is about essay endings, not technical content.
- **D-14 [S2]:** Render a metaphor's proposition literally, without strengthening
  or deleting it. Inspect sensory judgments (`진단은 서늘하다/경고는 아프다`)
  from one occurrence; likewise figurative `잠식/청사진/적신호/경고등/신호탄/
  움켜쥐다/뿌리내리다/짓누르다`. Other conceptual metaphors such as
  `청구서/과실/주춧돌` need three occurrences across the family. A metaphor
  root repeated three times qualifies even when it runs through the text;
  retain the most effective single occurrence. Preserve the original when
  its proposition cannot be determined. Literal technical terms are not
  metaphors; do not replace them. Never add a new metaphor.

## E. Rhythm

- **E-1 [S2]:** Uniform sentence lengths with no 100-character-plus sentence:
  vary rhythm with one or two short sentences and one longer combination of
  adjacent statements where useful. Do not add filler or stretch procedures.
- **E-2 [S2]:** At least four consecutive identical endings: vary endings within
  the original register, tense, and modality. Reduce `~고 있다` to simple tense
  only if the ongoing aspect is unnecessary. Required parallelism stays.
- **E-7 [S2, estimated]:** In conversational prose, inconsistent
  `해라/하게/하오/해요/합쇼` levels can be made consistent with the established
  speaker/listener relationship. Do not rewrite direct quotes, deliberately
  different speakers, or a formal document's stable register.

## F. Redundancy and modifiers

- **F-4 [S2]:** More than twelve accumulated nominalizers `-성/-적/-화` or
  literal `-tion/-ment/-ness/-ity` constructions: inspect for verbal/adjectival
  alternatives. Established nominalized technical concepts remain unchanged.
- **F-5 [S2]:** At least three abstract `~적 N` chains, such as `전략적 함의`
  or `실천적 기반`: use an equivalent noun phrase or unpack the relation,
  preserving the actual concept and any project terminology.
- **F-7 [S2]:** Dense generic `확대/강화/개선/확보/마련/구축` or abstract `설계`:
  use the concrete action already supported by the source. Preserve literal
  technical design and actual `구조/기준`. Do not amplify obligation markers.

## G. Hedging

- **G-1 [S2]:** Repeated `~로 보인다/~로 판단된다/~라고 여겨진다`: vary form only
  if certainty remains identical. Check negation and double negation first;
  when uncertain, preserve. Never turn a hedge into an assertion.
- **G-2 [S2]:** Stacked `~할 가능성이 있을 수 있다/~로 보여질 수 있다`:
  retain at least one hedge with the same polarity and certainty. Do not fold
  negative stacks or negotiation, contract, medical, legal, policy, or other
  precision-sensitive hedges where stacking carries substantive meaning.

## H. Connectives

- **H-4 [S2]:** Excessive `즉`: use an equivalent `곧/말하자면` or omit a
  redundant restatement, normally retaining no more than two. Keep necessary
  definitions and logical equivalence in technical prose.

## I. Bound nouns

- **I-2:** Empty emphasis `주목할 점은/X은 ~라는 점에 있다`: connect subject and
  predicate directly without losing the proposition.
- **I-3:** Concluding `~다는 것이다/~다는 뜻이다`: use a direct ending,
  normally retaining no more than two combined. Preserve actual interpretation
  or uncertainty rather than converting it to a stronger assertion.
- **I-4:** At least two paragraphs ending in obligation: leave the first;
  move later obligation sentences to the front or middle of their paragraph.
  Movement only: no merging, deletion, nominalization, subordination, or
  modality substitution. Keep the exact obligation-marker count. If no
  non-obligation sentence can close the paragraph, leave it unchanged.
- **I-7 [S2]:** Unattributed `~다는 분석이다/평가다`: preserve when a source
  appears nearby; otherwise remove only the unsupported attribution shell.
  Never invent a source or strengthen the underlying claim.

## J. Decoration

- **J-1 [S2]:** Bold keywords in every sentence: remove decorative body bold
  in columns/reports, preserving functional labels and meaningful notation.
- **J-2:** Five-plus decorative quotation marks: keep actual quotes and special
  uses; make ordinary emphasis plain text. Quoted technical tokens stay intact.
- **J-3:** Decorative em-dashes in every sentence: consider commas, parentheses,
  or separate sentences. Preserve original conversational asides, short
  exclamations, and rhetorical questions; do not impose a quota on those.

## Six-item self-check

Check immediately after editing. If an edit violates an item, roll that edit
back and retry once, not the entire document.

1. Facts, names, numbers, dates, quotes, content anchors, code, identifiers,
   commands, URLs, and technical terms are preserved exactly.
2. Change rate stays below the warning threshold where feasible; the gate
   provides the definitive measurement, not the editor's estimate.
3. Genre and document function are unchanged: no report-to-blog conversion,
   no technical-to-casual rewrite, no needless destruction of lists/headings.
4. Register is preserved in both directions, including living colloquial
   endings rather than artificial `했` → `하였` upgrades.
5. No confirmed applicable S1 findings remain. Recheck D-1–D-3, A-7/A-8,
   C-5/C-10/C-11, I-1, and J-2 with their conditions, not blanket deletion.
   C-11 must not increase. Resolve triggered D-14 findings; a running metaphor
   may retain one occurrence. A-16 requires contextual antecedent assessment,
   not a pronoun quota. H-1 is not a zero-occurrence target. Protected or
   intentionally structured spans are not residual findings.
6. No new claim, metaphor, stock phrase, obligation, or decorative rhetoric
   was inserted. Preserve the author's genuine voice.

If a self-check still fails, disclose its count in the summary and finalize or
hold as the workflow requires. Do not disguise a failure with a higher grade.

## Editorial grades

These are upstream self-review labels, not detector results or acceptance gates.

- **A:** No confirmed S1, at most two S2 findings, all six self-checks passed,
  and change rate in the upstream 10–25% band. Do not manufacture edits merely
  to enter that band; an already-good text may need almost no changes.
- **B:** No confirmed S1, at most four S2 findings, at least five checks passed.
- **C:** One or two S1 findings, or four or fewer checks passed; recommend heavy.
- **D:** Three or more S1 findings, or the blocking change-rate threshold;
  recommend holding the candidate rather than accepting it.
