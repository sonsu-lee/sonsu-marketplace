---
name: writing-adrs
description: >-
  Use for ADR assessment and decision-record writing or maintenance, not
  general design discussion. Decide whether a consequential choice needs a
  record, or draft, review, update, or supersede one. Not for routine
  implementation, work logs, or general documentation edits.
---

# Writing ADRs

Record why a consequential design direction was chosen, not everything done
while implementing it. Explain one coherent decision to a future reader.

## Workflow

1. **Establish the request and conventions.** Distinguish an assessment, a
   draft, and an authorized repository edit. Discussing whether an ADR is
   needed does not authorize creating one; acceptance of the choice is separate
   from permission to write its record. Read the project's ADR instructions,
   template, related records, and supporting discussion or evidence. Follow its
   scope, location, naming, metadata, format, and approval process rather than
   imposing a second template or migrating records. Use the defaults below only
   when no convention applies; if guidance is unavailable, disclose the gap
   instead of claiming the fallback is project policy.
2. **Decide whether to record it.** Apply the threshold below and check for an
   existing proposal or accepted decision on the same issue. Revise the same
   proposal during discussion, not a new record for each round. If reconsideration
   leaves an accepted choice unchanged, no new ADR is needed. If the change does
   not warrant an ADR, say so briefly; use an operational document only when the
   requested work calls for it.
3. **Write the decision** in the project template. Otherwise read and use the
   [lightweight template](assets/adr.md): a decision-stating title, date and
   status, then Context, Decision, Rejected alternatives, and Consequences.
   Store it as `docs/decisions/NNNN-title-with-dashes.md`, with the next unused
   sequential number padded to four digits. These are defaults, not Fowler
   requirements. Follow the writing and lifecycle guidance below.
4. **Check the record with a fresh reader** before delivering a draft or revision.
   If subagents are available, give a fresh one only the record and linked files;
   ask what was decided, why, and what was rejected. Otherwise self-review and
   disclose that no independent reader was available. Fix gaps. Neither review
   replaces the decision-maker's acceptance.
5. **Deliver** the requested assessment, draft, or file changes, identifying
   unresolved assumptions and the actual decision status. For file changes,
   check relevant links and repository-required Markdown validation. Do not
   claim approval or verification that did not occur.

## Decide whether to record it

Without a project-specific threshold, write an ADR for a choice that sets the
repository's or a component's direction or consequential design constraints:
purpose and supported scope, fundamental structure, public contracts, security
boundaries, or key quality attributes. Identify the meaningful tradeoff and the
continuing constraint or substantial reversal cost, not implementation size.

- Choosing portable packages versus a client-specific format is a candidate;
  updating a manifest to comply with that choice is not.
- Routine features, fixes, document formats, lint commands, version bumps, and
  review procedures are not ADR topics merely because they affect many files or
  future tasks. A tool or process choice qualifies only when it changes the
  design constraints above.
- Keep local implementation explanations in code or module documentation and
  current procedures in the README, skills, or configuration. An ADR is not a
  work log, implementation plan, or command reference.

## Write the decision

Make the essential decision understandable on its own, normally in about one
page. Link supporting investigations, issues, and measurements rather than
copying them. In the selected format:

- Explain the problem and constraints that force the choice. Separate observed
  facts from assumptions; do not invent evidence or decision-maker agreement.
- State what was chosen, its scope, and why in a few sentences. Put important
  information first, not the investigation narrative. Leave unspecified
  implementation mechanics open rather than invent paths, APIs, tooling, or
  verification requirements. Distinguish likely consequences from facts.
- Describe the serious alternatives actually considered and why they lost. Do
  not invent a comparison to fill a heading; if constraints leave only one
  viable choice, explain those constraints.
- State benefits and accepted costs, risks, or foreclosed options. Mention
  uncertainty and concrete revisit conditions when they matter, without adding
  a mandatory checklist or a separate section for every concern.

Do not copy a prior ADR just to replace its vocabulary. Review the tradeoff and
future implications, not just whether headings match the template.

## Preserve the decision lifecycle

Unless the project specifies another lifecycle:

- Start at `proposed` and keep the proposal editable until the decision-maker
  accepts or rejects it. Mark it `accepted` only with evidence of acceptance,
  which can include an explicit decision in the current conversation. A
  rejected proposal may remain `rejected` with its reason.
- When an accepted decision changes, create a new record with the new context
  and reason, linking to the record it would supersede. Leave the old record
  accepted while the replacement is proposed. Once the replacement is accepted,
  mark the old one `superseded` and link to the new one. Returning to an
  abandoned choice is a new decision with a new rationale.

Preserve accepted records in their historical format. Correct errors, links, or
status without rewriting the original decision and rationale; do not reformat
or discard old records because today's template or scope differs. When accepted
policy changes, update current operational instructions and applicable decision
indexes; do not leave an active requirement only in an ADR.

## Gotchas

- Finishing implementation, passing tests, or requesting an ADR draft is not
  acceptance. Do not call self-review an independent reader test.
- The selection threshold and fallback file conventions are this skill's
  defaults, not rules prescribed by Fowler or copied from Evolu's full workflow.

## Sources

[Martin Fowler's Architecture Decision Record][fowler] supplies writing and
lifecycle principles, not a fixed Markdown template. The bundled template is
adapted from [Evolu's ADR template][evolu-template]; its
[ADR guidance][evolu-guidance] applies Fowler in a small project-specific format.
The fresh-reader check adapts Anthropic's [doc-coauthoring skill][doc-coauthoring].

[fowler]: https://martinfowler.com/bliki/ArchitectureDecisionRecord.html
[evolu-template]: https://github.com/evoluhq/evolu/blob/bb2644275dd99ff6dce4744db578967699045ea3/docs/adr/template.md
[evolu-guidance]: https://github.com/evoluhq/evolu/blob/bb2644275dd99ff6dce4744db578967699045ea3/docs/adr/README.md
[doc-coauthoring]: https://github.com/anthropics/skills/blob/main/skills/doc-coauthoring/SKILL.md
