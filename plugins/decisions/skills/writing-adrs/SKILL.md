---
name: writing-adrs
description: >-
  Assess, draft, review, update, or supersede an architecture decision record.
  Use for consequential design choices, not general design discussion, routine
  work logs, or documentation.
---

# Writing ADRs

Distinguish an assessment, a chat draft, an authorized file edit, and acceptance
of the decision. One does not authorize another. Read the target project's ADR
criteria, location, format, lifecycle, related records, and supporting evidence.
Project conventions take precedence over the defaults below; report unavailable
guidance rather than claiming it does not exist.

Without project criteria, offer an ADR only when all three conditions apply:
the choice is hard to reverse, surprising without context, and the result of a
real tradeoff between alternatives. A routine manifest change is not enough.
If the user explicitly requests a draft even when the threshold is not met,
explain the assessment and provide the draft within the authorized scope.

Use the project's format and path. Otherwise use [the short template](assets/adr.md):
`docs/adr/NNNN-slug.md`, with the highest existing number plus one, a decision
title and one to three sentences explaining context, decision, and why. Add
status, considered alternatives, or consequences
only when useful. Explain real alternatives or constraints without inventing
options, preserve factual uncertainty, and make the decision understandable to
a future reader. Current commands, configuration, skill procedures, and agent
routing belong in their operational sources, not the ADR.

Follow the project's lifecycle. Unless it specifies otherwise, retain a proposal
until the decision-maker accepts it, and make its unaccepted status clear. A
completed implementation or request to draft is not acceptance. If an accepted
decision changes, write and link a new
record; supersede the old record only when the replacement is accepted. Preserve
accepted records' original reasons; correct errors, links, or status as needed.
Independent review is required only when requested or required by the project
or host. Arrange it within the authorized scope; report an unavailable required
review rather than treating self-evaluation as its replacement.

Assess context, decision and reasons, actual alternatives or constraints,
consequences, and document boundary. Score each applicable item 0, 1, or 2,
record exclusions and reasons, and normalize to 10. Require 8/10 and verified
requirements, authorization, security, data safety, confirmed contracts, and
stage evidence. Correct failures and reevaluate at most three times, never
without changes. If unsuccessful, report each score, mandatory conditions,
evidence, and blockers. Wait for user decisions, permission, or access instead
of automatic retries. Required independent review must be completed or reported
as unavailable; it does not establish decision acceptance.
