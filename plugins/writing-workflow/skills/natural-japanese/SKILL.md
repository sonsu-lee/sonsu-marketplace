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
  Script review requires uv and Python 3.10+ (uv resolves the Sudachi
  dependencies). Manual review is for unavailable execution, not a
  runtime-failure bypass.
metadata:
  upstream: https://github.com/coji/natural-japanese
  source-commit: 03bc944a0c4a9f0b2a66eab065b30de5c529bf08
---

# Natural Japanese

Write Japanese readers can understand. `scripts/lint.py` detects; the editor
judges. Do not stack humanizers or translate other-language passages.
All prose genres, including technical and mixed code/prose, are eligible.
Edit prose, never code, identifiers, commands, quotations, numbers, URLs, or
established terms. Genre never exempts a document.

## Most important rule: do not add content

Add no facts, numbers, people, dates, conditions, judgments, opinions, or
policies absent from the original, even true ones. Do not change certainty,
invent experience or endorsement, impose a numerical framework, change figures
or table values (report discrepancies), or add generic warnings or explanatory
paragraphs. Only directly supported clarification is allowed. Preserve claims,
examples, evidence, exceptions, conditions, attribution, and strength of
evaluation. For new writing, name missing material instead of guessing.
[Worked examples](references/revision-limits.md#preservation-examples).

## Modes and runtime

Requests select these modes: **write** drafts from authorized material, then
revises; **edit** revises existing prose (default when text is supplied);
**score** diagnoses without changing the document: read
[diagnosis](references/diagnose.md) first and do not rewrite until asked.

**Quick** is the default: work inline, read only the matching `references/doctypes/`
file, run lint even for short text, and complete the section 3 paragraph review.
Use **full** when requested, for high-impact external or executive documents, or
above roughly 10,000 Japanese characters: also run the section 5 review. One
editor owns the whole document. When uncertain, finish quick and mention full.

### Resolve installed resources before running scripts

Relative links are relative to this skill's directory, never the caller's
repository. In omp, Codex, or Claude Code, set `SKILL_DIR` to the absolute
directory containing this actually loaded `SKILL.md`; Codex reads relative links
under that root, Claude Code shows it as `Base directory for this skill`, and
omp may also use `skill://natural-japanese/<relative-path>`. Pass absolute
filesystem paths to Python/uv, never client URIs. If the loaded location or a
resource cannot be resolved, report the installation or lookup error; do not
guess a cache path, copy assets into the target repository, or bypass checks.
Quote target paths; add `--genre tech`, `business`, or `essay` when known:

```sh
uv run "$SKILL_DIR/scripts/lint.py" --json --genre tech "$TARGET"
```

Use the project's configured runtime; never change project configuration, global
installs, or hooks. If execution is unavailable, use
[manual review](references/manual-checklist.md) and disclose that no mechanical
checks ran. A configured runner, dependency, input, or script failure is not
permission to switch silently to manual review or another runner: report it,
resolve the cause, label manual observations separately, and never fabricate
scores. Inspect JSON and stderr; lint findings can still return exit 0. Read
[runtime notes](references/runtime.md) for runner/genre selection, failures,
warnings, baseline issues, or `exp` requests.

## 1. Decide before writing

Identify the reader and their goal; ask only about
missing material. For a known document type read the matching guide in
`references/doctypes/`: `minutes`, `report`, `guide`, `memo`, or `slide`.
If `style-profile.md` exists in the target project root or
user-specified location, or the user asks to learn the author's style, read
[author profile](references/author-profile.md).

## 2. Principles for writing

For drafting, full mode, or any edit touching the conclusion, headings,
causality, emphasis, certainty labels, endings, or voice, read
[writing principles](references/writing-principles.md); in revision they apply
only within source content and section 3's changes.

## 3. Revising an existing document

### Necessary review, paragraph by paragraph

When editing or reviewing a draft, read
[paragraph review](references/paragraph-review.md) (reader-effort sources and
seven vague-wording patterns). Lint JSON includes `paragraphs`; human output has
a numbered sheet of every heading, list item, table row, and prose unit. Review
every unit, including in quick mode: before editing write
`number: phrase → referent` for problems and `number: none` otherwise, through
the final unit, and record whether each issue was fixed or retained with a
reason. Standalone:

```sh
uv run "$SKILL_DIR/scripts/paragraphs.py" "$TARGET"
```

### Recover the concrete meaning behind vague wording

Check each verb and noun: name its concrete referent from source facts or code
instead of a stiffer paraphrase, keep certainty and attribution, and ask when
readings stay equally plausible.

### Limits on revision

Read [revision limits](references/revision-limits.md) before changing negation,
emphasis, connectors, certainty, lists, headings, order, or paragraph grouping,
and for `negation_repetition` or `antithesis_repetition`. Never guess a subject
or speaker, correct a number silently, delete a claim or condition as repetition,
or flatten the author's voice; change structure only when requested or a
specific misunderstanding justifies it.

## 4. Mechanical review and disposition

A lint finding is suspicion, not a mandate: decide from context and record every
outcome with a concrete reason as `[Fixed]` or `[Kept/reason]`
([format](references/finishing.md)); an unreasoned `Kept` is not a decision.

## 5. Structure and readability

Quick mode: read headings and each paragraph's first sentence in sequence. In
full mode, and for readability findings that need a fix, follow
[the readability review](references/readability.md); it holds the `outline.py`,
`terms.py`, and `--reading-load` commands.

## 6. Converge and finish

After editing or drafting, rerun lint with `--baseline "$BASELINE"` pointing to
the previous JSON. Follow [finishing](references/finishing.md) for convergence,
`newfacts.py`, and scratch files. Save and compare the exact pre-edit source;
remove unsupported additions. `newfacts.py` misses ordinary-noun details,
certainty changes, lost conditions, and swapped speakers: compare manually
even with empty output. Publish nothing.

## Sources

Adapted from [coji/natural-japanese][source] at commit
`03bc944a0c4a9f0b2a66eab065b30de5c529bf08`, under the upstream
[MIT license](LICENSE). See [provenance](references/provenance.md).

[source]: https://github.com/coji/natural-japanese/tree/03bc944a0c4a9f0b2a66eab065b30de5c529bf08/skills/natural-japanese
