---
name: writing-adrs
description: >-
  Use this skill when deciding whether a design choice warrants an architecture
  decision record (ADR), or drafting, reviewing, updating, or superseding one.
  Not for routine implementation, work logs, or general documentation edits.
---

# Writing ADRs

Record why a consequential design direction was chosen, not everything done
while implementing it. A useful ADR explains one coherent decision to a future
reader without making them reconstruct the discussion.

## Establish the request and repository conventions

Distinguish an assessment, a draft, and an authorized repository edit. A request
to discuss whether an ADR is needed does not authorize creating one. Acceptance
of the architectural choice is separate from permission to write its record.

Read the target project's ADR instructions, template, related records, and the
discussion or evidence supporting the choice. Use its scope, location, naming,
metadata, format, and approval process first. Apply the guidance below within
those conventions rather than imposing a second template or migrating records.
If the project has no applicable convention, use the defaults below. Unavailable
project guidance is not evidence that none exists; disclose the gap rather than
claiming the fallback is the project's policy.

## Decide whether to record it

Without a project-specific threshold, write an ADR for a choice that sets the
repository's or a component's direction or consequential design constraints:
purpose and supported scope, fundamental structure, public contracts, security
boundaries, or key quality attributes. Identify the meaningful tradeoff and the
continuing constraint or substantial reversal cost, not merely the size of the
implementation.

- Choosing portable packages versus a client-specific format is a candidate;
  updating a manifest to comply with that choice is not.
- Routine features, fixes, document formats, lint commands, version bumps, and
  review procedures are not ADR topics merely because they affect many files or
  future tasks. A tool or process choice qualifies only when it changes the
  design constraints above.
- Keep a local implementation explanation in code or module documentation, and
  current procedures in the README, skills, or configuration. An ADR is not a
  work log, implementation plan, or command reference.

Check for an existing proposal or accepted decision on the same issue. Revise
the same proposal during discussion; do not create a new record for each round
of feedback. Reconsideration that leaves an accepted choice unchanged needs no
new ADR. If the change does not warrant an ADR, explain that briefly and use the
appropriate operational document only if the requested work calls for it.

## Write the decision

Use the project template when one applies. Otherwise read and use the bundled
[lightweight template](assets/adr.md): a decision-stating title, date and status,
then Context, Decision, Rejected alternatives, and Consequences. Store it as
`docs/decisions/NNNN-title-with-dashes.md`, using the next unused sequential
number padded to four digits. These are defaults, not Fowler requirements.

Keep the essential decision understandable on its own, normally about one page.
Link supporting investigations, issues, and measurements rather than copying
them. In the selected format:

- Explain the problem and constraints that force the choice. Separate observed
  facts from assumptions; do not invent evidence or decision-maker agreement.
- State what was chosen, its scope, and why in a few sentences. Put the important
  information first within each section instead of narrating the investigation.
  Stay at the level of the actual choice: leave unspecified implementation
  mechanics open instead of inventing paths, APIs, tooling, or verification
  requirements. Distinguish a likely consequence from an established fact.
- Describe the serious alternatives actually considered and why they lost.
  Do not invent a comparison to fill a heading; if constraints leave only one
  viable choice, explain those constraints.
- State the benefits and accepted costs, risks, or foreclosed options. Mention
  uncertainty and concrete revisit conditions when they matter, without adding
  a mandatory checklist or a separate section for every possible concern.

Do not copy a prior ADR just to replace its vocabulary. Review whether the record
explains the tradeoff and its future implications, not just whether its headings
match the template.

Before delivering a drafted or revised record, check it with a reader who lacks
the discussion. Where subagents are available, give a fresh one only the record
and the files it links and ask what was decided, why, and what was rejected;
otherwise reread it cold, setting aside what you know. Fix the gaps this
exposes. It tests whether the record stands alone and does not replace the
decision-maker's acceptance.

## Preserve the decision lifecycle

Unless the project specifies another lifecycle, start at `proposed`. Keep the
proposal editable until the decision-maker accepts or rejects the choice.
Mark it `accepted` only with evidence of that acceptance, which can include an
explicit decision in the current conversation. Finishing implementation,
passing tests, or a request to draft an ADR is not acceptance. A rejected
proposal may remain `rejected` with the reason so it need not be rediscovered.

For an accepted decision that changes, create a new record explaining the new
context and reason, with a link to the record it would supersede. Leave the old
record accepted while the replacement is only proposed. Once the replacement
is accepted, mark the old record `superseded` and link to the new one. Returning
to a previously abandoned choice is still a new decision with a new rationale.

Preserve accepted records in their historical format. Correct errors, links, or
status without rewriting the original decision and rationale. Do not reformat
old records or discard them just because today's template or scope differs.
Update current operational instructions and applicable decision indexes when
the accepted policy changes; do not leave an active requirement only in an ADR.

Deliver the requested assessment, draft, or actual file changes, identifying
unresolved assumptions and the real decision status. Check relevant links and
repository-required Markdown validation for file changes. Do not claim approval
or verification that did not occur.

## Sources

[Martin Fowler's Architecture Decision Record][fowler] supplies the writing and
lifecycle principles, not a fixed Markdown template. The bundled template is
adapted from [Evolu's ADR template][evolu-template]; its
[ADR guidance][evolu-guidance] is an example of applying Fowler with a small
project-specific format. The selection threshold and fallback file conventions
above are this skill's defaults, not rules prescribed by Fowler or copied from
Evolu's full workflow.

The fresh-reader check adapts the reader-testing stage of Anthropic's
[doc-coauthoring skill][doc-coauthoring], described here in our own words.

[fowler]: https://martinfowler.com/bliki/ArchitectureDecisionRecord.html
[evolu-template]: https://github.com/evoluhq/evolu/blob/bb2644275dd99ff6dce4744db578967699045ea3/docs/adr/template.md
[evolu-guidance]: https://github.com/evoluhq/evolu/blob/bb2644275dd99ff6dce4744db578967699045ea3/docs/adr/README.md
[doc-coauthoring]: https://github.com/anthropics/skills/blob/main/skills/doc-coauthoring/SKILL.md
