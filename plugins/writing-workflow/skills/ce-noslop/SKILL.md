---
name: ce-noslop
description: >-
  Draft, edit, or check plain English prose: docs, runbooks, short copy,
  PR/ticket/review text. Covers technical and everyday prose and prose around
  code. Not for translation, non-English prose, authorship attribution, or
  code-only work.
license: MIT
metadata:
  source: https://github.com/EveryInc/compound-engineering-plugin
  source-commit: 2e41b4490a37f53db0beb6d4904618da9af2f559
---

# Write without slop

Write English prose that is understandable on the first read and free of AI
tells without changing the source's facts or certainty. Preserve every fact,
number, name, quote, and citation; add nothing the source or caller did not
supply.

## Workflow

1. **Choose the mode.** Honor a `mode:` token. Otherwise, no draft means
   **author**, an imperative on a draft means **edit**, and a question about a
   draft means **detect**.
2. **Choose the register** for the reader (below); the caller's interaction
   contract takes precedence.
3. **Apply the tests** to every English sentence. For edit and detect, and for
   an author passage the tests alone do not settle, read
   [the pattern catalog](references/patterns.md). For wording choices, read
   [the terminology guidance](references/terminology.md).
4. **Return the mode's output:**
   - **Author:** hold the tests as constraints while the caller writes; return
     nothing. When given content and asked to write, draft under the same tests.
   - **Edit:** rewrite only sentences that fail a test; passing sentences stay
     as written, so a second pass changes nothing. Return the text. Only if
     asked, say what changed in one line outside the rewritten text and any
     artifact.
   - **Detect:** name each pattern found, quote the line, and give the fix in a
     few words. Do not rewrite.

Write a named file in place only when requested; otherwise return the text.
Never say whether text was written by a model.

## Register

Pick by who reads the result:

- **Agent talking to the user.** The reader is a teammate who knows the domain
  and did not watch the work. Write each sentence as you would say it to them.
- **Repo or team artifact.** Neutral. Match the surrounding document's idiom.
  No first person, no opinion the artifact does not need. This is the default
  when no reader is named.
- **The user's own writing.** Preserve voice; make the minimum effective edit.
  Understandability edits stop at sentence splits and actor restoration that
  keep the user's word choice.

## The tests

Apply these to every English sentence, in author mode as constraints and in
edit or detect mode as checks.

1. **Mechanism.** Does the sentence say what the thing does, or how it feels?
   Replace the feeling with the fact it displaced, or cut the sentence.
2. **Portability.** Could the sentence move to another project unchanged?
   Then it carries no fact about this one.
3. **Actor.** Who does the verb? Name them when the source says who. Keep the
   passive when the actor is unknown or naming it adds nothing.
4. **One idea.** Would the reader have to reread to hold the sentence? Split
   it. A sentence the reader gets on the first pass stays, however long.
5. **Density.** One device proves nothing. Three or more distinct patterns in
   a passage, or one repeated across passages, is a finding.
6. **Decision first.** Does the first sentence carry the outcome the reader
   needs?
7. **Reader.** Can someone without the document or the code open act on this?
   Gloss the identifier or name the consequence.

Keep exact identifiers, paths, commands, and thresholds.

## Gotchas

- Never touch code blocks, quoted text, frontmatter, link targets, identifiers,
  or tokens required by the caller's contract unless the user names that
  content as the thing to fix.
- Apply this skill only to English prose, including prose around code and in
  README files, API docs, design docs, runbooks, release notes, and technical
  blogs. Protected content does not exclude the surrounding document.
- Leave other-language passages to their language's skill; do not translate
  them or apply these tests or the catalog to them. Do not stack another
  humanizer on English prose.
- Channel-specific marketing strategy is outside this skill; editing English
  marketing prose does not require another skill.

## Sources

Adapted from Every's [ce-noslop skill][upstream] and its pattern and terminology
references at commit `2e41b4490a37f53db0beb6d4904618da9af2f559`, under the
[MIT license](LICENSE).

This adaptation removes the unsupported `argument-hint` field and the
uninstalled `ce-promote` sibling redirect, bounds the skill to English,
clarifies technical-document coverage, and uses portable relative references
and wrapped Markdown. The upstream author, edit, and detect workflows,
registers, tests, and preservation rules remain the editorial authority.

[upstream]: https://github.com/EveryInc/compound-engineering-plugin/tree/2e41b4490a37f53db0beb6d4904618da9af2f559/skills/ce-noslop
