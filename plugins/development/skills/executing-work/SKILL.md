---
name: executing-work
description: >-
  Coordinate authorized implementation, test design, real-path verification,
  and independent review. Not for a plan-only request or review-only work.
---

# Executing work

Establish the requested outcome, scope, authority, and verification. Use
`planning-work` for a requested plan or consequential unresolved choices when
available. An approved plan does not require approval again, but does not decide
material choices left open by that plan. Obtain the decision-maker's approval
for a consequential unresolved design choice or scope expansion before
implementing it.
Host, user, and repository rules override these defaults.
An implementation request permits in-scope local changes, not commit, push,
publication, tracker changes, merge, deployment, or destructive work without
applicable approval. If evidence invalidates a consequential decision, obtain
the needed decision without silently changing scope.

Inspect existing code, contracts, callers, tests, and conventions. Reuse
suitable existing code or platform capabilities and make the smallest complete
change, preserving needed validation, error handling, accessibility, security,
and all requested behavior. Migrate affected callers and remove only code made
obsolete by the change. Do not add options, abstractions or features merely for
possible future use.

For an authorized repeated change, read
[mechanical changes](references/mechanical-changes.md) to establish and verify
its target set.

For a specification with tasks, identify true blocking dependencies and the
frontier of ready work. Work through the entire approved scope; after blockers
clear, continue the newly ready work. Delegate only useful independent slices
with explicit inputs, outputs, constraints, and ownership. Use isolation only
when its baseline contains the required staged, unstaged, and untracked work,
and its creation, application, branch, and cleanup effects are authorized.
Otherwise do not delegate edits that require it; work serially within the
authorized workspace. If a subagent-driven method is chosen, independently
review each task for spec compliance and quality, then review integration. Do
not automatically commit, merge, delete, change trackers, or create branches.

When coordinating delegation or independent review, read
[client execution](references/clients.md) for the current client.

## Design verification before writing tests

Identify the changed contract, caller-visible outcome, and happy path first.
Select only reachable input and state boundaries where behavior differs. Name
the plausible bug each test catches and the smallest appropriate test scope.
Set expected results from the requirement, external contract, or independently
worked example, never by copying the implementation. Avoid internal call order,
mock echoes, wiring, source text, non-emptiness, and tautological checks. For a
simple change where a test adds no value, state why and how it was checked.
Keep meaningful regression coverage when appropriate. Test-first is optional
unless explicitly requested or required by the project.

Run the real changed entry point or consumer path and observe the result;
tests, a build, or a self-assessment alone do not prove behavior. For bugs,
reproduce and retest the same path when safe and allowed; do not repeat a
reported failure where the user or host forbids it. Preserve evidence and
report unverified conditions.
If a declared verification gate blocks an action, inspect the declaration and
use the exact runner command it reports only when that check is authorized.
A receipt records execution on a tree, not test adequacy or action approval.

## Review and finish

Code and behavioral skill changes require independent review, even for a small
diff. Load the installed `reviewing-code` workflow before arranging review:
Claude Code uses the Skill tool with `review:reviewing-code`, Codex uses
`$review:reviewing-code` when available, and omp reads `skill://reviewing-code`.
If nested invocation is unavailable, read the installed `SKILL.md` and
distinguish reading from invocation. Include `authoring-skills` criteria for
skill changes, and follow the loaded review workflow's client reference for
independent workers. Respect native-only requests and client-specific worker
requirements. If a required skill, reviewer, or package is unavailable, report
incomplete coverage; do not claim review succeeded. The review's read-only,
single-round limits apply during that review. After it ends, verify findings
and make authorized corrections as the implementation owner. For any source
or test changes, freeze the final target and obtain an independent re-review
of the changed portion. Repeat affected checks when later changes invalidate
their evidence; never present a previous revision's review as final.
Update affected documentation and remove owned scaffolding. Report commands,
observed results, limitations, and remaining risks; distinguish unrun, failed,
and blocked checks from passes.

Assess contract and happy path, reachable boundaries, test design and expected
values, execution evidence, and unnecessary code removal. Score applicable
items 0, 1, or 2, record exclusions and reasons, and normalize to 10. Require
8/10 and verified requirements, authorization, security, data safety, confirmed
contracts, and stage evidence. Correct failures and reevaluate up to three times,
never without changes. If still unsuccessful, report each score, mandatory
conditions, evidence, and blockers. Wait for user decisions, permission, or
access instead of automatic retries; scores cannot replace real verification
or required independent review.
