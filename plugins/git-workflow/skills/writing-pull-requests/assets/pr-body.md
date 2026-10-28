# Default PR body

Copy the fenced body below, not this heading or introduction. Follow the
repository's template instead when one applies. Fill relevant sections, remove
unused optional sections and instructional comments, and disclose material
unknowns rather than leaving empty fields or implying that checks passed.
Record AI assistance with PR labels as described in the skill, not an additional
body section, unless the repository requires body disclosure.

```markdown
<!-- Keep each prose paragraph on one source line; do not hard-wrap. -->

## Why

<!-- Explain the concrete problem or need, not a generic claim of improvement. -->

## What changes

<!-- Explain the observable change and decisions the diff cannot explain.
Keep only context needed for review; link issues rather than copying them.
Use closing keywords only for issues this PR actually completes. -->

## Author checks

<!-- Select evidence before writing: what does each result establish about
this change? Group successful runs with the same check type and outcome.
Write each group as: [profile name if required]: [check type] — [observed result].
This is a review summary, not a reproduction guide: keep successful test inputs
and setup in the logs, rather than retelling the supplied notes.
Report failures, important limits, and unverified behavior separately.
Preserve explicitly required details. Use only observed results; omit this
section if there is no relevant evidence or material verification gap. -->

## UI evidence

<!-- Show the change with marked screenshots or focused video when useful.
Caption the visible result and meaningful limits, not the recording process.
Omit if not applicable; disclose missing required evidence. -->
```
