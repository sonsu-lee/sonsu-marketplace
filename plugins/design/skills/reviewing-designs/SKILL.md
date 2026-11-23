---
name: reviewing-designs
description: >-
  Evaluate an existing interface or visual design for issues without modifying
  it. Use for a critique, walkthrough or evidence-bound review of a supplied
  design. Use designing-interfaces for a new layout or redesign proposal;
  not for implementation or a general code review.
---

# Reviewing designs

Review existing designs without modifying them, grounding findings in the
available evidence and requested task.

## Workflow

1. **Establish scope and evidence.** Review only the requested artifact and
   task. Establish user goal, requirements, actual content, states and viewing
   context. Inspect additional states or rendered views when available and
   authorized; otherwise state what is unobservable. Do not edit files, create
   design artifacts, run project-mutating commands or publish a read-only review.
2. **Assess evidence.** Trace each consequential issue to an observed element
   and its impact on the task. Distinguish demonstrated defects from hypotheses
   or taste and explain missing evidence. Consider hierarchy, grouping, labels,
   interaction and recovery states, responsive content preservation and relevant
   accessibility requirements. Do not prescribe arbitrary font or spacing
   numbers or assert conformance from appearance alone.
3. **Report.** Rank actionable findings by impact, propose proportionate
   remedies and report scope and limitations. Removing a field, feature or
   limit and changing a default, consent or policy are owner decisions;
   recommend them as questions with evidence. If no issue is supported, say so.

For a motion review, inspect purpose, frequency, interruption, origin, reduced
motion, input capability and runtime cost. Observe actual motion when possible;
code or a still image alone cannot establish how it feels. Do not implement a
prototype or apply fixes without explicit authorization.

## Evaluate the review

Assess the review's coverage of goals and states, hierarchy and interaction,
accessibility, actual screen evidence, and constraints and limits. Score
applicable items 0, 1, or 2, record exclusions and reasons, and normalize to 10.
Require 8/10 and verified requirements, authority, security, data safety,
confirmed contracts, and stage evidence. Refine the review report, not the
artifact, and reevaluate up to three times, not unchanged. If still unsuccessful,
report each score, mandatory conditions, evidence, and
blockers. Wait for required decisions, permission, or access; a score does not
replace an actual screen check or required independent review.

## Gotchas

- A screenshot or textual snapshot describes only the supplied state; it does
  not prove behavior, keyboard access, responsive transitions, compliance or
  user outcomes.
- Scope negative findings to evidence. No visible guidance is an observation;
  no recovery or task completion requires additional flow evidence. Do not
  call a blockage permanent from one state. Describe impact conditionally: a
  closing caveat does not correct an earlier unqualified verdict.

Read [critique evidence](references/evidence.md) when the review covers
questions or fields, errors and lockout, long processing or AI answers,
screen-reader claims, defaults and consent, copy across screens, risk
warnings, redesign transitions, user-research or simulated feedback, a
claimed improvement, conflicting references or handoff, or another visual or
flow judgment that needs research context. Read
[worst-case data](references/worst-case-data.md) when the design renders user-
or system-supplied values such as names, counts, dates or lists, or when the
on-screen keyboard, OS banners or graphics that change by stage can affect what
is visible. These
source-derived suggestions are not independent validation of the reviewed
product or a substitute for applicable standards and tests.

## Optional omp strict run

This skill is guidance only in Codex and Claude Code; it does not provide omp's
runtime controls there. In omp strict mode is dormant until the operator starts
`/design-start <plan-json-path>` and confirms the displayed review plan. The
plan uses mode `review`, or `advisory` for a critique without captures; exact
files; the original request; confirmed project facts; and capture
targets/viewports/scenarios. Review capture steps may only assert, not
interact, and command checks are not allowed. Do not start or approve the run
yourself.

During the run use `design_status`, `design_read` and `design_capture` within
scope. When the evidence is ready, stop and ask the operator to run
`/design-report`, which writes and fact-checks the final review outside the
conversation, then `/design-accept` to publish it unchanged. A capture is
evidence of a specific view, not an automatic quality or compliance verdict.
If evidence is unavailable or the review cannot proceed, explain the limitation
and ask the operator to use `/design-stop`, `/design-blocked reason` or
`/design-limited reason` for a non-success exit. Never manufacture evidence or
accept it on the operator's behalf. The extension is in-process, not an OS
sandbox; the official result is the published report, not assistant prose.
