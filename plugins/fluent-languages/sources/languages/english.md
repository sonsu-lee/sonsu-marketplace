---
name: fluent-english
description: Use when writing or editing natural English answers, reports, explanations, or documents, including code-work results and technical documentation. Preserve code, commands, logs, identifiers, required structure and formatting, and factual meaning. Select by the requested output language.
---

# Natural English output

Write English explanatory prose that fits the requested genre, audience, voice, and format. Do not change facts, required formatting or ordered structures, certainty, or obligation while improving the wording. When a style preference conflicts with a preservation rule, preserve the source meaning and form.

## Scope

- Apply this guidance to the English portions of requested answers and documents, including implementation results, technical explanations, and technical documentation.
- Select it by the requested output language, not the language of the prompt.
- Do not translate or normalize foreign-language text, quotations, names, or established terms unless the user asks for that change.
- For code, code comments, commit messages, interface text, and other project-controlled strings, follow the user's request and the project's conventions before this guidance.
- This skill guides generated prose. It does not require a separate workspace, authorship detection, scoring, file output, or a multi-pass rewrite workflow.

{{ include: ../core/communication.md }}

{{ include: ../core/integrity.md }}

## Actors and reference

- Keep an important actor, action, and target close enough that responsibility, permission, safety, and data flow are clear on one reading.
- Distinguish the reader from software and other users. When roles change or a pronoun could refer to more than one actor, use the verified role or component name. Keep a natural pronoun when its antecedent is clear.
- Use an imperative when the reader performs an instruction. Do not add `you` to headings, labels, status text, or every procedural sentence merely to state the implied subject.
- If the available information does not identify an actor or resolve a reference, do not invent one or present one possible interpretation as established fact.

## Voice, verbs, and modifiers

- Use active voice and a direct verb when they expose a verified actor or make responsibility clearer. Keep passive voice when the result or state is the topic, or when the actor is unknown, irrelevant, or intentionally de-emphasized.
- Replace a nominalized or weak verb phrase only when the direct form preserves the same technical meaning and makes the action easier to identify. Keep established concepts such as `authentication`, `configuration`, and `error handling` when they name the actual subject.
- Unpack a noun or modifier string only when its internal relationships have more than one plausible reading. Keep established compounds, official names, interface labels, and technical terms intact.
- When the intended scope is established, place limiting modifiers such as `only`, `just`, and `even` next to the phrase they govern if another position would change or obscure the claim. If the source does not establish the scope, do not choose one interpretation and present it as fact.

## Variety, register, and terminology

- Follow the requested or existing variety of English, including spelling, punctuation, formality, contractions, person, headings, and list conventions. Do not normalize American, British, or another regional convention without a reason grounded in the document.
- Prefer a direct, familiar word when it is equally precise. Keep an expert term, qualifier, or longer construction when it carries a necessary distinction, condition, rationale, risk, or uncertainty.
- Use connected sentences for explanatory body prose. Allow natural fragments in headings, interface labels, tables, lists, and short status text where the format supplies the missing relationship.
- Use one established project term for one concept. Do not rotate among near-synonyms for variety when readers could infer different components or states. Preserve exact product names and interface labels.
- For an international audience or content intended for localization, avoid adding culture-specific idioms, slang, unexplained abbreviations, or ambiguous date expressions. Do not apply this as a blanket ban on natural English, contractions, or established phrasal verbs such as `log in`, `sign in`, and `set up`.

## Final check

After drafting, adjust a passage only when one or more of these patterns are conspicuous and make the result less clear or less faithful to the requested voice:

- an empty preamble delays the requested point;
- an unsupported importance claim, sales phrase, or vague attribution substitutes for evidence;
- synonym cycling makes one project concept appear to be several;
- a formulaic contrast, unraised objection, or unused alternative adds no real distinction;
- a closing paragraph repeats the result without adding a constraint, consequence, or next action;
- repeated sentence openings, shapes, or clipped fragments draw more attention than the content.

Do not treat a single word, transition, dash, colon, fragment, or passive construction as evidence of a problem. Keep real alternatives and objections, deliberate repetition, useful setup, safety language, and distinctive voice. Do not add a fact, source, example, number, opinion, or personal experience to make the prose seem more human. If an adjustment would weaken precision, attribution, polarity, certainty, obligation, terminology, or required formatting, leave the original expression in place.
