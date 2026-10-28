# Default PR body

Copy the fenced body below, not this heading or introduction. Follow the
repository's template instead when one applies. Fill relevant sections, remove
unused optional sections and instructional comments, and disclose material
unknowns rather than leaving empty fields or implying that checks passed.
Record AI assistance with PR labels as described in the skill, not an additional
body section, unless the repository requires body disclosure.

## Selecting author checks

The reviewer needs the result and what it proves, not a compressed work log.
Extract check type, outcome, required profile name, and checks or environments
not exercised. Write from these facts instead of shortening each supplied note.
Removing temporary test artifacts after a run does not make it unverified.

These examples illustrate selection, not results to claim:

- Notes: "Blue profile; eight parser checks passed, covering quoted fields,
  empty rows, and Unicode; tool v7; deleted temporary samples; local log saved;
  staging not run."
  Summary: "Blue profile: eight parser checks passed; staging remains unverified."
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

<!-- Fill these outcome summaries from observed facts; omit unused placeholders.
Group successful runs by check family, not by fixture. Preserve required details
and failed or unrun checks. Do not copy the examples' facts or outcomes. -->
[Required profile name, if any]: [check family and aggregate result; other results].

[Failures, explicitly unrun checks/environments, and material limits, if any].

## UI evidence

<!-- Show the change with marked screenshots or focused video when useful.
Caption the visible result and meaningful limits, not the recording process.
Omit if not applicable; disclose missing required evidence. -->
```
