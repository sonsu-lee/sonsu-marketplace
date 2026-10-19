# Use lightweight records for direction-setting decisions

- Date: 2026-10-20
- Status: accepted
- Decision-makers: sonsu-lee

## Context

During initial setup, the marketplace adopted MADR and asked agents to record
"significant choices." That threshold left room for ordinary documentation and
validation rules to acquire their own ADRs. We need to preserve the reasons for
consequential design choices without turning the decision log into a work log.

The maintainer authorized consolidating this initial policy in ADR-0001 rather
than retaining a separate replacement record. The date reflects this revision;
Git retains the earlier MADR choice. This is an initialization cleanup, not a
claim that the project followed this approach from the start.

## Decision

Follow [Martin Fowler's ADR writing and lifecycle guidance][fowler], using a
lightweight template adapted from [Evolu][evolu]. Limit new records to choices
that set direction or consequential design constraints, rather than every rule
that applies to multiple tasks. Keep the choice and its reason together, with
real rejected alternatives and the consequences we accept.

The [current procedure][procedure] owns the exact scope, template, and lifecycle
rules. The reusable [ADR skill][skill] applies target repository conventions
first and provides this approach as its default; the initialization exception
here is not a general plugin behavior.

## Rejected alternatives

- Keep the broad "significant choice" threshold: shortening the template alone
  would not stop routine work from becoming new ADRs.
- Retain the existing MADR structure: valid for projects that want it, but a
  smaller template is sufficient for the decisions we intend to record.
- Use only the bare Nygard sections: concise, but a separate rejected-alternatives
  section makes the reasoning we want to retain easier to find.
- Keep all rationale in the README: this mixes historical reasons with current
  instructions and obscures why a previous direction was replaced.

## Consequences

New records stay short and focus on continuing design constraints and meaningful
tradeoffs. Implementation details and operational procedures remain in their
owning documents rather than being repeated in ADRs.

This initialization cleanup also puts ADR-0002 through ADR-0004 into the same
lightweight format while preserving their choices, decision dates, and rationale.
Their presence is historical, not a reason to record similar operational choices
under the narrower scope.

After this one-time cleanup, accepted records are preserved and a changed
decision requires a linked replacement. Revising a proposal or reconsidering
an unchanged choice does not.

[fowler]: https://martinfowler.com/bliki/ArchitectureDecisionRecord.html
[evolu]: https://github.com/evoluhq/evolu/blob/bb2644275dd99ff6dce4744db578967699045ea3/docs/adr/template.md
[procedure]: ../../README.md#decision-records
[skill]: ../../plugins/decision-workflow/skills/writing-adrs/SKILL.md
