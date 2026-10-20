# Linear

## Select the applicable template

Establish the workspace and team, then inspect applicable issue templates and
team defaults. Linear has workspace and team templates, including templates
available from parent teams. Defaults can differ for team members and
non-members; do not assume that a template with a familiar name is the default.

Use an explicitly selected applicable template or the relevant team/workspace
template before the bundled fallback. Inspect both its content and properties.
Preserve required form answers and established metadata without inventing
priority, assignment, or due dates. Workspace templates cannot preset
team-specific labels or statuses.

When the creation tool supports a template parameter, use the selected template
and verify the result. Otherwise incorporate its required content and applicable
properties explicitly. Do not assume that API creation applies the UI's default
template or that a named template was used merely because its headings match.

## Review team and project metadata

Inspect available team/workspace labels, team members and ownership guidance,
priority conventions, the team's estimate configuration, and the intended
project's milestones. Apply the [common criteria](metadata.md) to recommend
values; do not make the user supply metadata that the selected template or
project guidance already establishes.

Use the team's actual estimate scale only when estimation is enabled and the
scope supports a meaningful suggestion. Do not enable estimates or substitute
zero for an unknown value. Distinguish an explicit assignee or valid template
default from a suggested owner, and explain priority recommendations using the
reported impact rather than treating all bugs as urgent.

Select a milestone only within the intended project and when the issue's outcome
fits that milestone's goal. If the project is unresolved, keep the milestone
unresolved too. Resolve actual user, label, project, and milestone identities
before publication; matching display names alone may be ambiguous.

## Publish and connect work

Search existing issues in the relevant scope before creating one. Respect
configured GitHub Issues Sync; a synchronized counterpart is not a second
independent work item to recreate. Use actual issue identifiers returned by
Linear, and preserve existing relations when updating or splitting work.

Inspect the integration's current workflow before relying on automatic status
changes. Linear distinguishes these PR description relationships:

- Closing keywords such as `Fixes ENG-123` apply the configured merge status.
- Non-closing keywords such as `Refs ENG-123` link partial work without applying
  the merge status, but can still trigger other configured status transitions.
- Relation keywords such as `Related to ENG-123` link context without status
  changes.

A branch containing an issue ID can also link work automatically. Do not assume
that omitting a closing keyword alone disables all automation; establish the
appropriate relationship and check the resulting linkage. Keywords in PR
comments do not create the links described above.

Linear supports multiple PRs per issue and multiple issues per PR. Its documented
multi-PR behavior waits for the final linked PR to reach the configured state.
That does not account for future, not-yet-linked PRs or prove that the ticket's
outcome is met. Keep intermediate work non-closing and distinguish merged code
from a result that still needs deployment or verification. Reuse the PR skill
for actual PR work; do not change integration settings to write a ticket.

## Sources

- [Issue templates](https://linear.app/docs/issue-templates)
- [GitHub integration](https://linear.app/docs/github)
