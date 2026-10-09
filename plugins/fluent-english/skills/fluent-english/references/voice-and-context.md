# Voice and context

Use this reference when the request is not just "fix grammar". It helps choose the right kind of good.

## Brief read

Before rewriting, identify:

- Genre: email, essay, report, documentation, UI copy, marketing copy, social post, speech, proposal, reference text.
- Audience: peer, customer, executive, regulator, hiring manager, friend, broad public, specialist reader.
- Relationship: warm, distant, corrective, collaborative, persuasive, instructional, apologetic.
- Stakes: low-risk note, public-facing copy, legal or compliance-sensitive text, high-trust technical guidance.
- Outcome: inform, persuade, reassure, ask, decline, explain, sell, document, announce, apologise.
- Constraints: length, dialect, house style, forbidden claims, citations, exact wording, formatting.

Then form a one-line read:

`Reading this as: [genre] for [audience], with a [tone] voice, optimising for [outcome].`

Do not show this line unless planning helps the user.

## Dials

Set these mentally before rewriting. Adjust them from the brief rather than using one house style.

| Dial | Low | High |
| --- | --- | --- |
| Directness | gentle, indirect, relationship-preserving | concise, plain, no ceremony |
| Warmth | cool, formal, restrained | personal, generous, conversational |
| Personality | invisible editor | distinctive point of view |
| Density | spacious, accessible | compressed, expert-facing |
| Evidence | common-sense, experiential | sourced, quantified, caveated |
| Polish | rough human texture | publication-ready finish |

The dials have measurable markers. Register studies (Biber) separate involved prose (first and second person, contractions, present tense, private verbs such as "think" and "feel", emphatics) from informational prose (nouns, longer words, more distinct words, attributive adjectives). Personal letters sit on the involved side, professional letters near the middle, academic and official prose on the informational side. Use the markers to check a rewrite landed where the brief asked:

| Medium | Markers to expect |
| --- | --- |
| Chat and messages | contractions, second person, questions, fragments allowed, no headings |
| Email | contractions, first person, one ask, short paragraphs |
| Memo and report | more nouns per sentence, fewer contractions, decisions before reasons |
| Documentation | present tense, no first person unless the house style has it, identifiers exact |
| Essay and opinion | first person, hedges as voice, at most one emphasised sentence per paragraph |

Second person is a human marker the models under-use: one 2026 story corpus reported humans address the reader more often than AI, figures unverified here. Where the genre allows it, keep it.

## Genre defaults

This section sets the dials for each genre. A tell in one genre is correct in another, so before applying the general lists check the per-genre Exemptions in `genre-tells.md`, which also holds the concrete phrase banks.

### Emails

- Lead with the action or decision.
- Keep goodwill, but cut servility.
- Use concrete asks, owners, dates, and next steps.
- Preserve relationship context. Direct does not mean blunt.

### Chat and short messages

- Writing solidifies and chat dissolves, so a chat message carries one thing: a question, an answer, a decision, or a link.
- Contractions, second person, and fragments are the register. Headings, bold labels, and bullet lists are not, unless the platform is used that way.
- If the words can be read two ways, they will be read the worse way. Say the thing, not the softened version.

### Documentation and technical writing

- Prefer present-tense descriptions of how the system works. The tells, including diff-anchored wording, are under Code, pull requests, and documentation in `genre-tells.md`.
- Keep identifiers exact.
- Use active voice where it clarifies ownership, but do not force a human actor where the system is the true actor.

### Product and marketing copy

- Replace hype with proof, usage, contrast, and concrete outcomes.
- Avoid booster verbs and vague "transform your workflow" language. See the canonical bank under Marketing and SEO in `genre-tells.md`.
- Do not invent social proof, customer names, usage metrics, awards, or benchmarks.
- Use one clear promise rather than a pile of benefits.
- See Marketing and SEO in `genre-tells.md` for SEO scaffolding.

### Essays, posts, and opinion

- Let the writer have a position, uncertainty, or tension.
- Keep strange details and lived examples.
- Vary rhythm. A few short sentences are useful; a whole page of staccato lines feels manufactured.
- Avoid tidy moral conclusions unless the piece has earned them.

### Reference, legal, medical, financial, and policy text

- Keep the voice plain and neutral.
- Preserve caveats that protect accuracy.
- Do not add personality for its own sake.
- Verify unstable facts if the answer depends on current law, prices, policy, availability, or research.

## Voice calibration

Imitation from a sample has limits, and the procedure below is built around them. In a 2025 study, five sample texts beat none, but adding more changed little, and the models matched email and news while failing on blogs and forums: they copy the surface and default to their own habits underneath. The features that identify a writer are word choice and sentence construction, not tone adjectives. So the method is to measure the sample, edit as little as the brief allows, and measure again.

### Before editing

1. Ask for one or two samples of 300 words or more that the writer produced without AI help. More than that changes little. Do not accept "write like [named author]" as a sample.
2. Check the sample against the tell lists first. Human writing is drifting toward LLM style, and a sample that scores high on the catalogue may itself be AI-assisted. Ask before treating it as the source of truth.
3. Run `voice_profile.py` as described in the [skill](../SKILL.md#measurement-and-preservation-tools). Use the same text boundaries for source, sample, and rewrite. Its lexical profile supplies:
   - median sentence length, and the share of sentences under 8 words and over 30
   - mean word length in letters
   - contractions per 100 words
   - first-person and second-person pronouns per 100 words
   - hedges per 100 words ("I think", "probably", "sort of", "maybe")
   - punctuation inventory per 100 sentences: parentheses, colons, dashes, questions, exclamation marks
   - recurring words with three or more occurrences
   Complete the profile by reading sentence openers (pronoun, noun, conjunction, adverb, verb), median paragraph length in sentences, recurring phrases outside the slop lists, and choices the writer avoids (such as bold or questions).
4. Decide the unity choices once from the sample and the brief: person, tense, and stance (certain, ambivalent, sceptical). Hold them for the whole piece.

### While editing

- Hedges, first-person markers, and idiosyncratic word choices from the sample survive unless one fails a clarity test you can quote. An unusual word that appears twice in the sample is the writer's, not a tell.
- Match the sample's punctuation and openers rather than replacing them with generic "good writing". Preserve recurring quirks when they feel intentional and do not hurt clarity.
- In informal genres (blog, forum, chat, personal email) edit less. The safer strategy is subtraction, because imitation fails there.

### After editing

Recompute the profile on the rewrite. Any figure that moved by more than a third is a voice break: either justify it from the brief or put the original back. Contractions, first person, and hedges falling while word length rises is the documented direction of drift, and it happens even under a "keep my voice" instruction, so check those four first. Recompute rather than judging by ear: in a 2026 preregistered study, participants who post-edited model text said it sounded like them while it measured closer to the model than to their own writing, and a 2026 Nature Human Behaviour study found LLM revision narrowed the variation in writing style between people by 21 to 50%.

On outputs over about 600 words, or across several turns of editing, re-read the first paragraph and the last together. Drift toward formal, hedged, contraction-free prose is the failure to look for.

### Measurement rules

`english-lexical-v1` measures the complete supplied UTF-8 text, including any markup. For prose-only comparisons, prepare equally scoped prose extracts for all inputs; keep the untouched Markdown files for the preservation validator.

- Words are Unicode letter sequences with optional internal straight or curly apostrophes. Digits and underscores separate tokens; hyphenated words count separately. Apostrophes are normalised only for counting.
- Sentence spans end at a run of `.`, `!`, or `?` followed by whitespace/end (optionally after a closing quote or parenthesis), or at a blank line. Nonempty trailing fragments count. Abbreviations, initials, decimals, URLs, and unusual punctuation can distort these lexical spans; inspect them before interpreting shifts.
- Contractions use `n't` and common pronoun/question-word forms ending in `'m`, `'re`, `'s`, `'ve`, `'d`, or `'ll`, plus `let's`. Noun possessives are excluded; ambiguous pronoun forms such as `it's` count. Pronouns include inflected first, second, and third person, including the pronoun base in contractions.
- Hedges count case-insensitive `I think`, `probably`, `sort of`, and `maybe`. This bounded list is a marker, not a complete semantic hedge detector.
- Punctuation counts literal characters. Both parentheses count separately; hyphens, en dashes, and em dashes have separate fields. Word-normalised frequencies use 100 words; punctuation frequencies use 100 sentence spans. Empty denominators yield zero.
- Numeric differences are after minus before. Relative change divides by the baseline; a zero baseline yields `null`, including zero-to-zero. Counts and rates are distinct: inspect rates when text lengths differ. The tool supplies observations; the brief determines whether a shift is justified.

## Editing contract

Resolve conflicts in this order: quoted or frozen text, legal and citation exactness, keep-my-voice and sample fidelity, then strict de-AI styling.

- Preserve required facts, citations, constraints, dates, scope words, and accuracy-protecting nuance. Keep coverage unless the user requests cuts. Hold neutral reference, legal, medical, financial, and technical prose to its genre's register.
- For in-place edits, change prose while retaining code, code identifiers, YAML frontmatter, link targets, image references, and quoted text byte for byte. Table-cell prose and image alt text may change unless frozen. Retain heading levels and list style; judge information kept rather than paragraph count. Quotes include blockquotes and paired inline quoted spans.
- The preservation validator compares fenced/indented/inline code, frontmatter, blockquotes (including contiguous lazy continuation lines), paired straight/curly inline quotes, Markdown destinations, reference labels/definitions, and autolinks. It compares exact strings and multiplicity in source order within each category, retaining line endings. It is a conservative lexical check, not a full Markdown or HTML parser. Review syntax outside those forms and bare names manually.
- Prefer actors, objects, and evidence already in the source. Keep a vague claim vague or mark the gap: “powerful search” supplies no basis for “search covers everything you have written”. Replace faceless attribution with equally qualified wording, not an invented team or expert. Greetings, thanks, apologies, opinions, and questions need no fabricated evidence. Quotes, names, studies, links, statistics, and benchmarks require a source.
- Use the doer as subject where it clarifies ownership. Retain passive or system-as-subject when the actor is unknown, irrelevant, legally sensitive, or expected by the genre.
- Let sentence length follow the idea. Prefer literal wording and concrete source detail over impressive metaphors. Keep intentional asides, ambivalence, unusual details, defensible quirks, and repetition that carries distinct requirements.
- Open short pieces with the point; end with the strongest existing fact or a user-requested next action. If removing a flourish leaves no closing fact, end on the preceding sentence. Apply this per section in long documents, with specs and runbooks exempt.
- Keep additions within supplied facts and authorised register changes: contractions/second person required by chat or email, and user-requested next actions. Mark gaps or ask for missing facts. Source-free jokes, opinions, sensory detail, typos, slang, claims of progress, and invented voice are fabrications.
- Restate inflation at its actual strength in roughly the source clause's length. A hope stays a hope: “paving the way for a rollout” supplies no evidence that rollout has begun. Use “healthy”, “well within range”, or “realistic” only with a named source baseline.
- In light edits, keep contractions (or their absence), first person, hedges, lone dashes, and unusual words unless a named clarity failure or other brief-supported error warrants a change. A tell-list match alone is diagnostic input.
- Apply specificity, directness, context, voice, evidence, and reader trust together. Cut announced intentions and needless reassurance where the relationship permits; retain genuine position and rhythm already present rather than polishing the prose flat.

### Strict passes

For humanise, de-AI, remove-slop, and equivalent requests, aim for one person writing to one reader. Apply the editing contract's precedence first.

- Apply [Dash dependence](ai-writing-patterns.md#dash-dependence): sentence-hinge em/en dashes become full stops or commas, not substitute colons or parentheses; numeric/date ranges remain. Keep other punctuation when supported by the source or sample and genre. Preserve deliberate literary voice under the genre exemptions.
- Use sentence-case headings, informative bullets, and medium-appropriate emoji.
- Address the real reader. Remove pasted assistant scaffolding and disclaimers; keep genuine interpersonal coordination such as “Let me know if Thursday works”.
- Prefer literal prose in neutral and non-fiction genres; flag deliberate literary voice rather than stripping it. Close on the source's real point under the editing contract, rather than manufacturing a positive or concrete ending.

## Sentence craft

The checks that make a rewrite read as written rather than assembled. Each is a test, not a mood.

- Characters as subjects, actions as verbs. Who did what. See the specificity ladder below.
- Old before new. A sentence opens with what the reader already has from the previous sentence and ends on what is new. Test the last three words: they should carry the thing the reader did not yet know.
- Cohesion. Read the grammatical subjects of a paragraph's sentences in order. They should name a small set of recurring topics. If every sentence has a fresh subject, the paragraph is not about anything.
- Proportion. At most one emphasised sentence per paragraph: a figure of speech, an intensifier, a tricolon, or a short punchline. AI prose deploys the same level of special effects to every sentence regardless of importance. The last sentence is not automatically the emphasised one.
- Connectors only where order fails. If the paragraphs already hold their order, "however", "therefore", and "in addition" are scaffolding. AI-assisted prose converges hardest on connective structure, so removing a connector is usually safe and adding one rarely is.
- The talk test with a named reader. For any sentence the swap test flags, ask whether this writer would say it aloud to the audience in the brief. If not, write what they would say. For a draft from scratch, write the two-sentence spoken version first and build the draft from it.
- Curse of knowledge. List every term, acronym, and internal name the text does not define. For each, decide whether the brief's audience knows it. Define or cut the ones they do not.
- A stock phrase marks where the writer stopped thinking. The fix is to find the thought that was skipped, not to swap in a synonym.

## Flatness is also a tell

Removing tells is half the job. Prose sanded down to a uniform finish reads as machine-made too: every sentence the same length, no position, no reaction, nothing only this writer would say.

The fix is to surface what the source and brief already contain, never to manufacture it.

- If the writer has a position, let the prose take it instead of listing balanced pros and cons.
- If the writer is ambivalent, keep the ambivalence. "Impressive, and slightly unnerving" is more honest than "impressive".
- Keep first person where the genre allows it. It is not unprofessional in most writing.
- Vary sentence length. Let a short sentence land after a long one.
- Keep the specific observation over the general one: not "this is concerning" but the thing that is concerning.
- Leave a defendable rough edge rather than polishing the piece flat.

Never invent an opinion, an anecdote, a feeling, or a quirk the writer did not have. Where the source holds no position, state what is true plainly rather than performing conviction. See Friction-free tone under Structure check in `preflight.md`.

The failure this section causes when read too eagerly is a rewrite that adds material to sound alive: a next step the source never proposed, a line about what has or has not happened since, a joke in the writer's manner, a sensory detail. Each of these is a fabricated claim, and a joke in the writer's manner is a fabricated quote. The test for any sentence in the rewrite is whether the source states or directly implies it. If not, cut it, mark the gap, or ask.

Faking texture is the same failure from the other side. Do not add typos, slang, self-interruptions, or contractions the source lacks. Commercial humanisers do this and their output reads as damaged, not human.

## Specificity ladder

When a sentence feels vague, climb this ladder until it becomes useful:

1. Name the actor.
2. Name the object or system.
3. Name the action.
4. Add a number, date, place, example, source, or consequence.
5. Apply the swap test: if the sentence could sit unchanged in another company's or project's copy, it says nothing about this one.
6. Cut the sentence if it still only says "this is important".

## Fact safety

Concrete prose can tempt an agent to fabricate. Do not do that.

- If a fact is missing, ask for it, mark the gap with a clear placeholder such as `[figure needed from the Q1 report]`, or write around it honestly. Never fill the gap with an invented specific.
- Mark uncertain claims as uncertain without using filler.
- Do not turn "some people say" into named experts unless the source is available.
- Do not add invented anecdotes to make a piece sound human.
- When the swap test flags a sentence that could sit in any article, the fix is a question to the writer or a gap marker such as `[what did you measure or observe here?]`, never a detail supplied by the editor.
- Do not invent a baseline. "Healthy", "strong", "well within range", and "realistic" are claims about a comparison; keep them only when the source names what they are compared against.
- Editing is not fact-checking. A fact in the source that looks wrong gets a note, not a silent correction.
