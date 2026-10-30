# Disposition, convergence, and working files

Read after lint when you edit or draft: to record dispositions, decide when to
stop, compare with the source, and handle working files. Score-only requests
skip it. Commands, `SKILL_DIR`, and `TARGET` come from [the skill](../SKILL.md).

## Disposition

Lint detects phrases, calques, repeated negation, monotonous sentence lengths,
absent noun endings, lexical reuse, and English-like syntax. A finding is
suspicion, not a mandate. Consult its detail and hint, decide from context, and
reading the sentence aloud can help. Record each finding's outcome in the
response or scratch space:

```text
- [Fixed] translationese「〜という点で」: changed to「〜では」.
- [Kept/product name] forbidden_phrase「多角的」: part of「多角的レビュー機能」.
```

Use concrete reasons such as quotation, technical term, needed contrast, or
genre convention. “Kept” without a reason is not an editorial decision.

## Convergence

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

## Compare with the source

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

## Working files

Keep lint JSON, disposition notes, original copies, and draft backups in the
environment's scratch directory or a directory created with `mktemp -d`, not
beside the target. Remove only your temporary working files when finished.
Leave only the requested final document and, when explicitly requested, an
author profile in the user's project. This workflow does not publish or
transmit target text; an authorized artifact workflow owns publication.
