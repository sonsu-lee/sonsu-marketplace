---
name: executing-work
description: >-
  Coordinate authorized implementation from a proportional plan through
  review and final validation. Use for executing a change, not a request only
  to plan, review, draft a pull request, or perform a native-only review.
---

# Executing work

Use the plan's goal, scope, authority, sequence, and verification to coordinate
the work through a finished result. Apply host, security, repository, and user
instructions first: this skill's defaults do not override binding constraints.
Planning and execution are distinct: an explicit plan-only request ends with the
plan, not implementation or other side effects.

## Establish the contract

For non-trivial work, use `planning-work` for a plan and any required approval.
A small, clear change needs only its goal, scope, and verification stated, not
a planning document. Reuse a supplied or existing
plan when it still matches the goal, current evidence, scope, authority and
verification; do not demand a new plan or repeat an approval already given.
Inspect relevant code and instructions before deciding that it remains valid.

Separate what is authorized from what is merely possible. Clear authorization
to implement permits the in-scope local work, not every downstream action.
Commit, push, PR publication, merge, and deployment are distinct permissions;
do not infer one from another or from an approved plan. Respect more restrictive
repository and host rules. Bulk changes, material design or scope expansion,
and external actions need the applicable approval before proceeding. If new
evidence invalidates a consequential decision, explain the change and obtain
the required decision rather than silently changing scope. Continue other
independent authorized work where safe.

## Coordinate the work

One integration owner maintains the contract and sequences planning,
implementation, independent review, fixes, final verification, and handoff.
Proceed between stages without redundant permission requests where the work is
already authorized. Preserve relevant user changes and use existing conventions.
For independent implementation slices, delegate only when useful and permitted;
give each worker its scope, interfaces, constraints, and ownership. Avoid
conflicting edits and integrate their results before final checks. A worker's
report is not proof that its output is correct.

Code and behavioral skill changes require independent review. Only a binding
instruction prohibiting review or an unavailable facility can prevent it.
A small diff is not an exception. Do not mark the workflow complete when
required review coverage is missing; state the concrete limitation.
For code review, load `reviewing-code` before dispatching reviewers and follow
its client-specific controller procedure, including its required general and
focused assignments. One reviewer alone does not satisfy that procedure.
The integration owner acts as that controller or delegates it explicitly;
do not launch an extra controller after its review is already complete.
For skill changes, include required skill-criteria review once under the same
owner instead of starting a duplicate reviewer.
For a skill-only change without a code-review controller, follow
`authoring-skills` for its independent review. Verify review findings against
the source and requirements, fix applicable findings, and keep unavailable or
incomplete review explicit rather than describing it as a pass.

A separate tester or cleanup worker is optional, not a fixed team. Delegate
only substantial, independently useful testing or cleanup when permitted; keep
small checks and cleanup with the owner. A tester needs the exact target,
scenario, expected evidence, and safe environment. Cleanup must preserve user
work. Neither role replaces review or the integration owner's responsibility.
Read [client execution](references/clients.md) when delegating or arranging an
independent review, and follow the currently exposed tools and permissions.

## Finish against the final revision

Integrate fixes and remove only owned temporary artifacts. Reassess affected
callers, tests, and documentation against the plan. Final validation and any
required review must apply to the final revision, not an earlier snapshot;
repeat affected checks or review when later edits invalidate their evidence.
Run only authorized checks, using the plan and project requirements, and report
actual commands, results, and target. Distinguish unrun, failed, and blocked
checks from passes. Do not treat a worker launch, static inspection, or a
previous revision's result as final proof.

If a binding instruction requires stopping, name the exact instruction and its
source, the affected stage, and remaining work. Likewise identify missing
permissions, unsafe execution, or unavailable tools rather than inventing a
successful result. Defaults do not require stopping merely because a stage has
finished. Deliver the completed authorized work with evidence and any genuine
blockers; do not perform unauthorized external actions.
