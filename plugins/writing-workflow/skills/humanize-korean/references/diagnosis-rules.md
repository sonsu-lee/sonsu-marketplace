# Complete Korean diagnostic taxonomy

Read for standard/heavy diagnosis. This English adaptation consolidates the
upstream 85-entry diagnostic index with its operational taxonomy conditions and
prescriptions. It includes entries intentionally absent from the quick subset.
IDs are upstream IDs; the missing F-6 is intentional. Historical build metadata,
research logs, and promotion tooling are not needed to edit a document.

Use [quick rules](quick-rules.md) for ordinary editing and self-checks. Diagnose
only the three to six strongest applicable patterns, not every possible match.
Include exact source spans and an inline prescription, especially for an ID
absent from quick rules. Do not force three findings into already-good prose.

## Conditions before classification

Every Korean genre is eligible, including technical documentation and manuals.
A match inside code, an identifier, a command, a URL, a number, a direct quote,
or an established technical term is protected, not an editing finding.
Preserve required headings, lists, parallelism, tense, aspect, obligation,
uncertainty, polarity, causality, and project terminology. Technical passive
voice and nominalized concepts are often necessary. These protections override
stylistic frequency targets without exempting the rest of a technical file.

Upstream severity labels: **S1** is a high-priority contextual finding, **S2**
is a strong repetition/context signal, and **S3** is weak unless combined with
others. They are not proof of AI authorship. Never label an entire document from
one metric. Human author variation can exceed differences between group means.

## A. Translationese

- **A-1 [S1] — `~에 대하여/대해서`.** Preserve by default. Only paragraph-level
  clustering of at least three `~에 대해(서)` instances supports direct
  object/topic attachment: `AI 규제에 대해 논의` → `AI 규제를 논의`.
  Upstream measurements found ordinary uses more common in human prose.
- **A-2 [S2] — `~를 통하여/통해`.** Only at least three repeats in one paragraph:
  vary some with `~로/~해서/~함으로써`. Keep one or two ordinary uses and actual
  path/means relations. Diagnosis-only, not a quick-rule target.
- **A-3 [S1] — `~에 있어(서)`.** Replace empty situational packaging with
  `~에서/~을 볼 때/~에서는` when the meaning is equivalent.
- **A-4 [S2] — `~라는 점에서`.** Three-plus repeated rationale frames:
  consider `~해서/~라는 이유로/~이기 때문에`. Diagnosis-only; comparative
  evidence is sparse, so do not treat a single use as a defect.
- **A-5 [S2] — `~와 관련하여/관련된`.** Simplify redundant topic framing to
  `~에/~의/~를 두고`, but retain real relationships and exact terms.
- **A-6 [S2] — `~에 기반하여/~을 바탕으로`.** Vary repetitive framing with
  `~로/~를 근거로/~를 보고`; retain actual derivation or evidence relationships.
- **A-7 [S1] — Literal possession and light verbs.** `가지고 있다` or literal
  have/make/take/give plus noun may become a verb, adjective, or double subject:
  `강한 경쟁력을 가지고 있다` → `경쟁력이 강하다`;
  `회의를 가지다` → `회의를 하다`. Literal possession is not automatically wrong.
- **A-8 [S1] — Double passive.** `~되어진다/~지게 된다` can become a single
  passive or equivalent active: `판단되어진다` → `판단된다`. Preserve a necessary
  passive viewpoint and distinguish actual causation or change of state.
- **A-9 [S2] — By-passive `~에 의해`.** Restore the known actor as subject or
  use `~에/~에게` only where equivalent. Do not invent an actor, change agency,
  or erase a necessary passive construction in technical prose.
- **A-10 [S2] — Repeated `~할 수 있다`.** Default to preservation. At least four
  identical forms dominating rhythm permit some equivalent hedge variation,
  never an assertion or marker deletion. Medical, legal, policy, and other
  precision-sensitive hedges stay exact even at high frequency; change order
  or boundaries instead. Heavy review is preferable for such claims.
- **A-11 [S2] — Purpose clauses `~을 위해`.** Preserve ordinary use; only
  paragraph-level clustering permits `~려고/~도록/~위한` variation. Human prose
  uses this construction frequently too.
- **A-12 [S2] — Automatic `만들어지다/이루어지다`.** Where agency is known and
  unchanged, prefer the concrete verb: `합의가 이루어졌다` → `합의했다` or
  `합의에 이르렀다`. Keep literal creation, process, and necessary passives.
- **A-13 [S2] — Particle-free noun chains.** Restore `의/가/를` or unpack the
  relation: `기술 발전 속도 가속화` → `기술의 발전 속도가 빨라진다` when that is
  the claim. Preserve labels and defined terms. Do not convert every noun
  phrase into `~해야 한다`; that invents or amplifies obligation.
- **A-14 [S2] — Clause-linking `그리고`.** When it mechanically imitates English
  “and,” consider connective endings `-고/-며/-면서`, preserving sequence and
  logical scope. Keep useful explicit conjunctions.
- **A-15 [S2] — Abstract subject plus universal verb.** Inspect `보여준다/
  제공한다/가져온다/시사한다` with abstract subjects. Use a known concrete actor
  or direct description. Causatives can become `X 때문에/덕분에/로 인해`;
  cognitive predicates can become `~에 따르면 ~이다/~으로 ~이 드러났다`.
  `이 책은 300쪽을 가진다` → `이 책은 300쪽이다`. An actual API providing a
  resource is a technical description, not automatically personification.
- **A-16 [S1] — Contextually unsupported pronouns.** At each `그/그녀/그것/그들/
  이것/이는`, inspect antecedent noun phrases in the preceding two sentences.
  Zero candidates: restore the noun only if its identity is certain; otherwise
  flag without editing. One candidate: a zero pronoun may be natural. Two or
  more: repeat the appropriate noun phrase, not another ambiguous pronoun.
  Do not infer gender. No frequency threshold or deletion percentage applies;
  `pronoun_density` alone cannot trigger this rule. The two-sentence window and
  candidate estimates are preliminary. Applies to original Korean prose too,
  not only translated text. Diagnosis-only; preserve whenever uncertain.
- **A-17 [hold] — Mechanical inanimate/abstract `-들`.** Observation only;
  do not name it a dominant finding or edit solely because of its count.
  The metric and noun dictionary remain for measurement; promotion evidence
  was insufficient upstream.
- **A-18 [S2] — Long left-branching relative clauses.** Three-or-more-word
  prenominal modification or nesting depth of at least three deserves review;
  more than one such sentence strengthens the finding. Split the sentence or
  follow the noun with apposition, preserving all restrictions. This measures
  noun modification, not E-5's comma-segment length.
- **A-19 [S2] — Double particles.** `에서의/에로의/으로의/에의/으로부터의/로부터의`:
  rewrite as a clause or phrase. More than three per document strengthens S2.
  Plain `~의` is explicitly not a target; its supposed foreign origin is not
  sufficient grounds for editing.
- **A-20 [S2] — Passive progressive.** `~되고 있다/~지고 있다` at least three
  times per paragraph: vary only some, retaining the actual aspect and time.
  `심화되고 있다` might become `심해지는 중이다`; a completed tense is valid
  only if the source says the change has occurred. Keep isolated uses.
- **A-21 [S2] — Inflated scope escalation.** `단순한 X를 넘어 Y`: use
  `X만이 아니라 Y다` or remove the empty escalation, not the real proposition.
- **A-22 [S2] — Added certainty predicate.** `~은/는/이/가 명확하다/분명하다`:
  inspect each instance, without a frequency trigger. Remove only empty
  evaluation; preserve certainty with `분명히` when needed. Keep a conclusion
  supported by preceding argument. Not adverbial `분명히`, action
  `명확히 하다/밝히다`, or D-12's empty `한계도 분명하다` slot.
- **A-23 [S2, heavy only] — “Laying foundations” formula.** Figurative
  `(발판/토대/초석/주춧돌/교두보)을 마련/놓/다지` or `(지평/활로)를 열다`:
  state what the source actually says becomes possible. Without that detail,
  lower only the metaphor, never invent the mechanism. Preserve completed
  historical facts, direct quotations, a single nonconcluding use, physical
  openings, actual `기반을 마련`, and ordinary `길을 열다`. The target is a
  forecast-closing formula, not literal technical foundations.
- **A-24 [S2] — `더 이상 ~ 않다/아니다`.** Two-plus uses or a concluding
  redefinition can use `이제` or a change verb. Preserve explicit ending of a
  previously stated condition, quoted speech, and isolated ordinary uses.
  Never turn a negative proposition into an invented positive one, or add
  `더 이상 A가 아니라 B` while revising C-8. Not `더 이상의 N` or unrelated
  words such as `이상 기후`.

## B. English terms and quotation

- **B-1 [S2] — Repeated bilingual glosses.** Usually explain once, then use
  consistent terminology. Respect independently readable API entries and
  project terminology. Audience needs determine whether a gloss is useful.
- **B-2 [S2] — Promotional English.** Explain decorative `seamless/robust/leverage`
  only when these are empty promotional terms. Preserve established technical
  vocabulary and quoted tokens. Do not mechanically translate `prompt/token/
  agent/pipeline/framework`. In nontechnical prose, a natural Korean equivalent
  may be better when it does not change a term the source depends on.
- **B-3 [S2] — Excessive English quotations.** Inspect redundant framing around
  English quotations. Actual direct quotations are immutable; this adaptation
  does not silently translate or paraphrase them. Route translation requests
  separately rather than treating quotation replacement as Korean editing.
- **B-4 [S3] — `~라고 알려진/~로 일컬어지는`.** Remove redundant “known as”
  framing only when the name and attribution remain unambiguous.

## C. Structure and layout

- **C-1 [S2] — Mechanical enumeration.** Preserve by default. Four-plus items
  in one paragraph reading like a metronome may allow one or two to become
  prose or `우선/다음으로/마지막으로`. Do not dismantle real procedures,
  requirements, options, or intentional parallelism; three-item lists are not
  automatically defects.
- **C-2 [S2] — Decorative bullet blocks.** Three-plus consecutive blocks in
  essays, columns, or reports may become paragraphs where enumeration carries
  no meaning. Useful technical lists stay lists.
- **C-3 [S2] — Formulaic section headings.** `도입/본론/결론` segmentation:
  simplify decorative prose structure or make a heading concrete using source
  content. Keep required sections, headings referenced elsewhere, and navigation.
- **C-4 [S2] — Every paragraph starts with a summary.** Reorder an existing
  example, quotation, or scene into the opening where it improves flow. Never
  invent a scene; preserve useful topic sentences in instructional prose.
- **C-5 [S1] — Decorative emoji clutter.** Remove decorative list/heading/body
  clutter in essays and reports; retain functional status symbols, quoted
  text, and an intentional social/product-copy style.
- **C-6 [S2] — Heading followed by an empty preview.** Remove repeated
  `이 섹션에서는 ~를 다룬다` when it adds nothing. Keep a useful scope statement,
  prerequisite, or safety instruction.
- **C-7 [S2] — Mechanical `먼저/반면/결국` progression.** Remove one or two
  redundant signposts while keeping actual sequence, contrast, and consequence.
- **C-8 [S1] — Chained antithesis.** Two-plus `A인가 B인가/A가 아니라 B/~것이 아니라`
  formulas are candidates only when adjacent passages repeat the same frame.
  Keep the most effective one; use asymmetric sentence lengths or direct
  statements for the rest. Do not erase all contrast or create new antithesis
  elsewhere. Upstream's larger human sample contained frequent individual
  users of this rhetoric; isolated/scattered uses are not proof of a defect.
  The P2 check warns if at least five original matches become zero.
- **C-9 [S2] — Decorative `1) 2) 3)`.** Unpack only ornamental indexing into
  prose or sequencing words. Preserve numbered procedures, legal references,
  labels, and intentional same-structure lists.
- **C-10 [S2] — Repeated `X: Y` subtitle headings.** Simplify decorative subtitles
  into a single phrase or supported body sentence. Keep real report/academic
  section titles, technical labels, and headings used in navigation.
- **C-11 [S1/S2] — Connective-ending commas.** Commas after
  `-고/-며/-지만/-면서/-아서/-어서/-자/-는데`: three to five are S2; six-plus
  are S1. Remove unnecessary punctuation or split at an appropriate boundary,
  never add this pattern while editing. Protect code and quotations.
- **C-12 [S2] — Document-level comma inclusion.** More than 50% of sentences
  containing commas invites inspection. Some commas may be absorbed by
  connective endings, removed, or replaced with a sentence boundary. The
  upstream 26–33% reference range is not a universal prose target.

## D. Stock rhetoric

Never insert the phrases in this category into previously unaffected spans.
Preserve concrete meaning and modal force when removing rhetorical packaging.

- **D-1 — Conclusion labels.** Combined `결론적으로/따라서/이를 통해/그러므로/
  요약하면/정리하자면` above three: retain one or two needed transitions.
  Do not delete a necessary causal relation just because its marker repeats.
- **D-2 — Empty significance.** `매우 중요하다/반드시 기억해야 한다/
  시사하는 바가 크다/주목할 만하다`: remove unsupported inflation, or use the
  concrete reason already present. An actual requirement remains a requirement.
- **D-3 — Empty list prefaces.** `크게 세 가지로 나눌 수 있다/다음과 같은`:
  proceed directly to content if the preface is redundant. Useful table/list
  introductions remain.
- **D-4 — Hype adjectives.** Three-plus `혁신적/획기적/압도적/파격적/폭발적/
  전례 없는`: remove inflation or use supported concrete wording. Evidence
  for AI classification is weak; diagnosis-only, not a quick trigger.
- **D-5 [S2] — Personified abstractions.** `기술이 묻는다/시대가 부른다`:
  use the real actor or reduce personification. One effective symbolic title
  or summary may be intentional. Never invent who acted.
- **D-6 [S2] — Formulaic call-to-action ending.** `~할 때입니다/~시점입니다`:
  state the same supported action and modal force, normally keeping at most
  one rhetorical occurrence. A literal deadline is not a formula.
- **D-7 [S2] — Repeated transformation formula.** `X에서 Y로/X을 넘어 Y로`:
  directly state the change, retaining one effective summation when central.
  Do not create new `더 이상` antithesis. Literal migrations remain precise.
- **D-8 [S2] — Clefts and core/problem shells.** `필요한 것은 방향이다` →
  `방향이 필요하다`. Also inspect `문제는/핵심은/관건은/답은 ~다/~는 점이다/
  ~데 있다`. Combine with C-8 only when both actually apply.
- **D-9 [S2] — Causal conclusion formulas.** Repeated `(으)로 이어진다/
  ~에 직결된다` and logical `결국`: specify only the source's causal path or
  use a direct sentence; normally retain at most one redundant formula.
  Never introduce `결국/이유다/~로 이어진다` while fixing another ending.
- **D-10 [S2] — Inverted `~하는 이유다` ending.** Prefer forward reasoning
  such as `그래서 ~라는 우려가 나온다`, preserving the claim. Not adverbial
  `~라는 이유로`. Normally at most one; never introduce a new inversion.
- **D-11 [S2] — Vague future closure.** Sentence-initial
  `향후/앞으로/중장기적으로` within the final 30% is the combined condition.
  Remove only the vague time frame, or use an actual source-provided date or
  condition. A time word alone is not the pattern.
- **D-12 [S2] — Empty challenge slot.** Standalone `과제도 남아 있다/
  한계도 분명하다/아쉬운 점도 있다`: start with the actual challenge already
  present. Preserve substantive `안전 기준 정비도 과제로 남아 있다`.
- **D-13 [S2] — Formulaic essay reflection.** `어쩌면 ~일 것이다/비로소/
  천천히 ~이 됐다` at an essay ending: remove empty reflective packaging,
  not genuine literary structure or uncertainty. This is a pattern-specific
  essay condition, not a document-level exemption for any other genre.
- **D-14 [S2] — Layered conceptual metaphors.** Inspect abstract sensory
  judgments such as `진단은 서늘하다/경고는 아프다` from one occurrence, and
  figurative `잠식/청사진/적신호/경고등/신호탄/움켜쥐다/뿌리내리다/짓누르다`
  from one. Other families (accounting `청구서`, agriculture `과실`, building
  `주춧돌`, weight, mirrors/shadows) need three combined occurrences. A repeated
  metaphor root qualifies at three even when central to the prose; keep the
  most effective single occurrence. Render the proposition literally:
  `시장을 잠식한다` → `시장 점유율을 뺏는다`, not `사라진다` (stronger claim).
  Established idioms are not interchangeable with newly layered metaphors.
  Preserve when the proposition is uncertain, or when editing would dismantle
  the argument rather than change its wording. Literal technical vocabulary
  is protected. The upstream taxonomy contains both a central-metaphor guard
  and a later running-metaphor refinement; fidelity wins if they conflict.

## E. Rhythm and sentence length

- **E-1 [S2] — Uniform lengths, especially no long sentence.** A cluster around
  30–50 characters and no 100-character-plus sentence invites rhythm review.
  Use short sentences of roughly 10–15 characters and one supported longer
  joining of adjacent content only where natural. Do not add filler to meet
  length targets or distort technical steps.
- **E-2 [S2] — Repeated endings.** Four-plus identical endings: vary within
  the same register, tense, aspect, and modal force. Review mechanical
  `~고 있다` mappings, not actual ongoing events. Preserve required parallelism.
- **E-3 [S2] — Every paragraph has three or four sentences.** Vary paragraph
  boundaries where the existing logic supports one-sentence or longer
  paragraphs. Do not invent content or join unrelated procedures.
- **E-4 [S2] — Only simple sentences.** Combine adjacent supported statements
  with `-며/-고/-는데/-면서/-자`, relative clauses, quotation, or conditions.
  Upstream suggests roughly 60% simple and at least 30% compound/complex;
  these are rhythm heuristics, not quotas for technical instructions.
- **E-5 [S2] — Long comma segments.** Average above seven eojeol (space-delimited
  units) invites review. Segments of eight-plus can split at a period or become
  a shorter Korean modifier. This is a different axis from A-18 nesting.
- **E-6 [S2] — Commas at indiscriminate POS boundaries.** Limit unnecessary
  commas to meaningful clause boundaries or clear appositions/insertions.
  Upstream evidence applies to essays, news, blogs, QA, and reports, not poetic
  punctuation; inspect analogous technical exposition contextually. The
  bundled standard-library metrics do not provide a full POS analysis.
- **E-7 [S2, estimated] — Listener-level inconsistency.** In dialogue or
  conversational passages, inspect unintended mixing of two or more
  `해라/하게/하오/해요/합쇼` levels. Preserve actual speaker relationships,
  quotation boundaries, and deliberate voice. Do not impose this dialogue
  rule on a stable formal register. Its quantitative threshold is estimated,
  not a verified Korean corpus calibration.

## F. Excessive modifiers and redundancy

- **F-1 [S2] — Degree adverbs.** Remove mechanically added `매우/정말/진짜로/
  대단히/극히` where empty. Preserve genuine colloquial emphasis such as
  `정말 그랬다니까`. Use only already-supported comparisons or numbers.
- **F-2 [S2] — Synonymous double modifiers.** `중요하고 핵심적인 역할`:
  retain one only if the two do not carry distinct meaning.
- **F-3 [S2] — Role/function doubling.** `~로서의 역할과 기능`: simplify only
  if “role” and “function” are redundant in that context.
- **F-4 [S2] — Accumulated nominalization.** More than twelve `-성/-적/-화`
  instances or literal `-tion/-ment/-ness/-ity` chains invite verbal/adjectival
  alternatives. Preserve established technical nominalizations and concept
  anchors; suffix counts alone cannot justify changing them.
- **F-5 [S2] — Abstract `~적 N` chains.** Three-plus `전략적 함의/실천적 기반`
  type phrases: use noun-plus-noun, an explicit relation, or an equivalent
  verb phrase where the concept survives. Upstream density-reduction targets
  do not override defined terminology.
- **F-7 [S2] — Generic policy verbs.** Dense `확대/강화/개선/확보/마련/구축` and
  abstract `설계` can hide actual actions. Unpack only what the source supports.
  The related abstract `구조/기준` nouns also need context. Preserve literal
  technical design, structures, and criteria. Do not multiply `~해야 한다`.

## G. Hedging

- **G-1 [S2] — Repeated speculative endings.** Preserve by default; vary only
  equivalent forms of `~로 보인다/~로 판단된다/~라고 여겨진다` when monotonous.
  Never remove uncertainty, especially with negation or double negation.
- **G-2 [S2] — Double/triple hedges.** `~할 가능성이 있을 수 있다` may reduce
  to one hedge only if certainty and polarity remain identical. Preserve
  stacked hedges expressing negotiation, contract, medical, legal, policy,
  or other precision-sensitive scope. Edit surrounding prose normally.
- **G-3 [S2, hold] — Safe-balance vocabulary.** `양쪽 모두/두 가지 모두/
  장점도 있지만/신중하게/균형`: the upstream policy/report hypothesis used
  four-plus combined instances but lacked adequate Korean evidence. Do not
  edit solely because of this metric. In an independently justified edit,
  a source-supported concrete comparison or condition may replace vagueness.

## H. Connectives

- **H-1 [S2] — Paragraph-initial connectives.** Only three-plus in one paragraph
  with metronomic repetition: reduce some `또한/따라서/즉/나아가/아울러/게다가`.
  Preserve real logical links. Human usage and model variation undermine
  blanket removal; diagnosis-only, never a zero-occurrence target.
- **H-2 [S2] — Repetitive adversatives.** Repeated `하지만/그러나` every paragraph:
  remove only redundant contrast markers or vary equivalent wording.
- **H-3 [S2] — Repeated metadiscourse.** `이는/이 점에서/이 관점에서/이 말은`
  three-plus times within one paragraph: some can state the proposition
  directly. Preserve by default and do not discard a necessary antecedent.
- **H-4 [S2] — Repeated `즉`.** Consider `곧/말하자면/다시 말해/바꿔 말하면`
  or omit a redundant restatement; usually at most two decorative instances.
  Technical equivalence and actual definitions remain precise.

## I. Bound and formal nouns

- **I-1 [S2] — `것이다` endings.** Only three-plus consecutive overuses:
  simplify some to direct endings where assertion already exists. Default
  preservation; human prose uses this frequently. Diagnosis-only, not an
  authorship signal or permission to remove future/speculative modality.
- **I-2 [S2] — Empty `점/바/수/데`.** `주목할 점은/X은 ~라는 점에 있다`:
  use a direct subject/predicate or concrete noun while preserving the claim.
- **I-3 [S2] — `~라는 것` conclusion.** `~다는 것이다/~다는 뜻이다/~다는 점이다`:
  connect the ending directly, normally at most two redundant combined
  endings. Repeated `~인 셈이다` joins the family at two-plus; preserve a
  natural isolated use and any substantive interpretive qualification.
- **I-4 [S2] — Obligation-ending paragraphs.** At least two paragraphs ending
  `~해야 한다/합니다/~할 필요가 있다/요구된다`: leave the first, move later
  obligation sentences to the front/middle of their own paragraph. Movement
  only. Never merge obligations, delete a marker, nominalize, subordinate,
  or change modality. Exact marker count must stay equal. If no non-obligation
  sentence can close the paragraph, preserve it. Quotes and legal text stay.
- **I-5 [S2] — Abstract `~이/가 필요하다`.** Clarify who must do what only
  where the source establishes both. Do not end every converted sentence
  with `~해야 한다` or increase obligation. Keep noun forms that intentionally
  organize a list or define a requirement.
- **I-6 [S2] — Abstract `N 능력` chains.** Three-plus repeated noun phrases
  may become an equivalent verb: `워크플로우 수행 능력` →
  `워크플로우를 얼마나 잘 처리하는지`. Preserve technical names and actual
  capability distinctions rather than enforcing a two-use ceiling blindly.
- **I-7 [S2] — Unattributed verdict.** Journalistic `~다는 분석이다/평가다/
  관측이다` is normal when a source is nearby. Without one, remove only the
  unsupported attribution shell. Never fabricate a speaker or strengthen
  an uncertain proposition.

## J. Visual decoration

- **J-1 [S2] — Bold in every sentence.** Remove decorative body bold where
  unhelpful; retain labels, semantic notation, and project conventions.
- **J-2 [S2] — Decorative quotation marks.** Five-plus emphasis uses invite
  review; upstream taxonomy strengthens S2 above five. Preserve direct
  quotations and special/technical uses. Explain an ordinary concept once,
  then use plain prose instead of repeated scare quotes.
- **J-3 [S2] — Decorative em-dashes.** Repetition in every sentence may become
  commas, parentheses, or separate sentences. Preserve original conversational
  asides, exclamations, and rhetorical questions rather than flattening voice.
- **J-4 [S3] — Parenthetical over-explanation.** Repeated `(이는 ~을 의미한다)`:
  incorporate necessary content into prose or remove only redundant content.
  Preserve arguments, syntax, units, citations, and technical notation.

## Diagnostic observations, not invention prompts

- **DS-1:** An unanchored opening can sometimes use an existing dated fact or
  quotation moved from later in the document. Never invent a date or scene.
- **DS-2:** Anonymous sources without date, venue, or medium can warrant a
  “source needs confirmation” warning. Do not manufacture attribution details.
- **DS-3:** Absence of a continuing character/example is not a request to add one.
- **DS-4:** Genuine self-limitation (`솔직히 말하면/모르겠지만/내가 보기에`)
  may be authorial voice; preserve rather than import English-only heuristics.
- **DS-5:** Aphoristic endings overlap D-8/D-9/D-10. Avoid stacking conclusion
  slogans; do not invent a “human” ending.
- **DS-6:** Genuine localized emotion, mockery, or exclamation is not automatically
  a defect. Never add fake emotion. Likewise preserve authentic `당시/힘들다`,
  benefactive `~해 주다`, and sentence-initial `또,` where meaningful.

## Evidence limits

Individual author variation, genre, and task can reverse aggregate patterns.
Do not claim “zero false positives” from a source corpus with zero occurrences.
Perfect orthography or register is not proof of authorship either. A naturally
written text may need no changes; do not add intentional errors.

Upstream post-editese metrics cover simplification, normalization, and
interference. They are metric-only hypotheses, not extra replacement rules.
A-17 remains on hold; E-7 remains estimated. Plain `~의` stays outside A-19.
Pronoun counts do not establish A-16's contextual condition. The v2 baseline
contains estimated placeholders, so do not interpret v2 z-scores as calibrated
Korean evidence. These helpers do not establish naturalness or authorship.

The diagnostic taxonomy derives from the pinned source identified in
[SKILL.md](../SKILL.md#sources). Corpus studies, scholarship, and development
history remain available there; no external resource is needed at runtime.
