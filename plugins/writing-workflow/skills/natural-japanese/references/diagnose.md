# Diagnosis: score without rewriting

Use this reference for `score` or a request such as 「この文章、AIっぽい？」.
Return a score, its reasons, and priorities if the user later wants revisions.
Do not modify the document. A rewrite request switches to sections 1–7 of
[the skill](../SKILL.md).

The score measures selected stylistic signals, not whether an AI wrote the
text. Do not frame it as an authorship probability or a detector-evasion target.

## Depth

Diagnosis depth differs from editing depth because there is no rewrite loop:

- **quick**, default: run `lint.py --json` once, with `--genre` when known,
  and glance through headings and paragraph openings. No subagents.
- **full**: also run `outline.py` and `terms.py`; include the structure,
  readability, and document-type review from section 5. Parallel reading is
  useful only for a genuinely long document. Evaluate once, without a
  convergence loop.

Resolve every script against `SKILL_DIR` as explained in the skill. This
adaptation does not ship upstream `semantic.py` or its `exp` mode, which would
require an optional model download of roughly 1 GB. Do not claim to run it.
The retained lint `--experimental` flag is not a replacement for that mode.

## Two-layer score

Report naturalness on a 0–100 scale, higher meaning fewer formulaic signals.
Always disclose both the mechanical base and editorial adjustment.

Calculate the deterministic base from the severity counts in the top-level
`findings` array, not `reading_load`:

```text
penalty = (critical * 8 + warn * 4 + info * 0.5)
          * (1000 / max(document_character_count, 1000))
mechanical_base = max(100 - penalty, 20)
```

Use the complete document's character length, including Markdown and newlines.
This is approximate length normalization: shorter documents give each finding
more weight; longer documents are penalized for density rather than raw count.
One critical finding weighs as much as two warnings or sixteen informational
findings. The floor of 20 prevents mechanical findings alone driving the score
near zero. If the document is empty or effectively too short (under 100
characters), do not score it; say it is too short for diagnosis.

For **quick**, use the mechanical base unchanged and explicitly call the result
coarse. For **full**, apply an editorial adjustment within ±15 points:

- Subtract for structural issues not detected by lint: identical section
  constructions, unrelated or unsupported lists, unclear certainty, missing
  next steps in a report that needs them, or invented ranking of parallel items.
- Restore points for findings that are false positives or natural in context.
- Apply genre and source-preservation judgment. A technical term, necessary
  safety warning, quotation, or intentional essay device is not a defect
  simply because a rule flags it.

Clamp the final result to 0–100:

```text
final = min(max(mechanical_base + editorial_adjustment, 0), 100)
```

The adjustment involves judgment and may vary by several points. This is not a
CI gate, a factual correctness grade, or a comprehensive writing-quality score.
Say so briefly in the result. If scripts did not run, report manual observations
without inventing a mechanical base or presenting an uncomputed score.

## Bands

| Score | Band | Interpretation |
| --- | --- | --- |
| 90–100 | Natural | Few formulaic signals; remaining points may be taste. |
| 70–89 | Minor | A few noticeable habits remain. |
| 50–69 | Revise | Clear surface or structural issues merit revision. |
| 0–49 | Strong | Multiple categories show pronounced issues. |

These bands describe the rubric, not the probability of human authorship.

## Output

1. Give the score and band, with mechanical base and adjustment separately.
2. Give three to five main reasons, or fewer when evidence is sparse. Explain
   actual wording in context rather than copying category names or raw details.
   Cite representative line numbers: repeated 「〜ではなく」 may create a
   mechanical rhythm, but a needed factual contrast should remain.
3. Give two or three high-impact revision priorities without making the edits.
   Offer quick or full revision only as an optional next step.

Do not dump every finding. Focus on the evidence that most affected the score,
and disclose missing execution or limits separately from editorial judgment.
