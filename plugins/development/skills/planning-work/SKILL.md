---
name: planning-work
description: >-
  Plan work when requested or consequential choices remain unresolved. Not
  standalone ticket, ADR, PR, or interface design requests without a planning
  need. A plan-only request does not authorize implementation.
---

# Planning work

Read the request, existing code, relevant documentation, decisions, and project
rules before asking. Establish the desired outcome, scope, authority, known
facts, assumptions, and verification. Ask only consequential questions that
cannot be answered by tools or context. A small clear change needs no formal
plan document. A plan-only request ends with the plan; an implementation request
with a plan remains an implementation request. Return the plan in the response;
write it to a file only when the user authorizes that destination. Do not create
temporary planning files without authorization. Do not repeat approval of an
already approved and still valid plan. More restrictive host and project rules
always take precedence.

For plan-only work, observations can still create caches, bytecode, or logs.
Prevent those writes or use an authorized disposable copy; preserve and check
source, index, and untracked state before claiming the workspace was unchanged.

Prefer the smallest plan that meets every requirement. Reuse an existing
capability before proposing a new one.

When material choices remain, compare two or three real alternatives against
the goal and constraints; recommend one and explain its tradeoffs. Where one
sensible approach remains, explain why. Use `grilling` or `grill-with-docs`
when an interview is actually needed and those skills are available. Separate
settled decisions, assumptions, and open questions. Offer ADR, PRD, or ticket
work only when requested or authorized; do not create or publish one by default.
Preserve explicit requirements and constraints; propose any material change to
them as an alternative for the decision-maker's approval.

For a plan sized to the task, describe the goal and exclusions, design and
interfaces, constraints and original requirements, affected responsibilities,
dependencies, each deliverable and verification, and remaining decisions.
For independently assigned tasks, identify their inputs and outputs, including
names, signatures, and types that other tasks depend on. Derive checks from
observable requirements and reachable failures, not a fixed test-first sequence.
Do not mandate commits. Trace the spec to tasks and verify coverage, omissions,
interface and type consistency, constraints, and expected results. Avoid writing
an implementation transcript in place of decisions.

When user approval is required, present the plan before file changes or
implementation. For an already approved plan, proceed within its scope. If new
evidence invalidates a consequential decision, explain it and seek the needed
decision. A fresh reader can identify ambiguity when available but cannot prove
the plan works.
If implementation is authorized and consequential decisions are settled, use
`executing-work` when available and proceed without requesting approval again.

## Evaluate the plan

Assess purpose and scope, evidence, real alternatives, decided versus open
questions, and verifiability. Give each applicable item 0, 1, or 2; record
excluded items and reasons, and normalize to 10. Require 8/10 and verified
requirements, authority, security, data safety, confirmed contracts, and stage
evidence. Fix supported failures and reevaluate at most three times, never
without a change. If still unsuccessful, report each score, mandatory
conditions, evidence, and blockers. Wait for a user decision, permission, or
access instead of automatic retries. Required independent review cannot be
replaced by a self-score.
