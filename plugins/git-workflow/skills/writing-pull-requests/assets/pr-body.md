# Default PR body

Copy the fenced body below, not this heading or introduction. Follow the
repository's template instead when one applies. Fill relevant sections, remove
unused optional sections and instructional comments, and disclose material
unknowns rather than leaving empty fields or implying that checks passed.
Record AI assistance with PR labels as described in the skill, not an additional
body section, unless the repository requires body disclosure.

## Selecting author checks

The reviewer needs the result and what it proves, not a compressed work log.
Extract check type, outcome, required profile name, and material coverage limits;
write from those facts instead of shortening each supplied note. Removing
temporary test artifacts after a run does not make that run unverified.

These examples illustrate selection, not results to claim:

- Notes: "Blue profile; eight parser checks passed, covering quoted fields,
  empty rows, and Unicode; tool v7; deleted temporary samples; local log saved."
  Summary: "Blue profile: eight parser checks passed."
- Notes: "Blue profile; parser failed on quoted commas; staging not run;
  repository requires tool v7 and the reproduction command `parse sample.csv`."
  Summary: "Blue profile: parser check failed on quoted commas with tool v7
  (`parse sample.csv`); staging remains unverified."

## Body

```markdown
<!-- Keep each prose paragraph on one source line; do not hard-wrap. -->

## Why

<!-- Explain the concrete problem or need, not a generic claim of improvement. -->

## What changes

<!-- Explain the observable change and decisions the diff cannot explain.
Keep only context needed for review; link issues rather than copying them.
Use closing keywords only for issues this PR actually completes. -->

## Author checks

<!-- Summarize selected evidence as [profile if required]: [check type] — [result].
Group matching outcomes. Keep failures, material coverage limits, and explicitly
required details. Successful fixture descriptions, environment inventories, and
temporary-artifact cleanup belong in work logs, not this section.
Use observed facts, not the examples' results. Omit this section only when there
is no relevant evidence or material verification gap. -->

## UI evidence

<!-- Show the change with marked screenshots or focused video when useful.
Caption the visible result and meaningful limits, not the recording process.
Omit if not applicable; disclose missing required evidence. -->
```
