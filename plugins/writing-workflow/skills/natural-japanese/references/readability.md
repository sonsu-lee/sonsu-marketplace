# Structure and readability review

Read in full mode, and when lint or `--reading-load` readability findings need a
fix. Quick mode without such findings does not need it. `SKILL_DIR` and
`TARGET` come from [the skill](../SKILL.md); its section 3 revision limits and
preservation rules apply to every change below. Use the matching
document-type guide in `doctypes/` when the type is known.

Do not split authorship between agents: emphasis and transitions require one
view of the whole document. Parallel reading is useful only when it genuinely
helps with a long document; editorial responsibility stays with you.

## Full-mode commands

Use the appropriate genre rather than always `tech`. `--reading-load` is a
separate editorial lane: it does not enter the naturalness score or baseline
comparison.

```sh
uv run "$SKILL_DIR/scripts/outline.py" "$TARGET"
uv run "$SKILL_DIR/scripts/terms.py" "$TARGET"
uv run "$SKILL_DIR/scripts/lint.py" --reading-load --genre tech "$TARGET"
```

## Structure

Lint examines surface patterns; sparse findings in minutes or slides say
little about their structure. Read headings and paragraph openings
consecutively. Check whether the argument can be followed; headings
communicate useful content; repeated definitions, openings, or section
structures obscure emphasis; and the conclusion arrives when the reader needs
it. Do not force a suspense plot onto factual prose. Chronology can be
evidence in incident analysis or intentional in an essay. For new reports,
check supported next actions; for revisions, only assess those present in the
source. Apply the matching document-type reference.

## Readability order

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
   specialist concepts, within the revision limits in section 3 of the skill.

Brevity is not the goal. First preserve facts and grammatical relationships;
only prefer shorter wording between equally faithful candidates. A clearer
split sentence or list may be longer.
