---
name: reviewing-designs
description: >-
  Evaluate an existing interface or visual design for issues without modifying
  it. Use for a critique, walkthrough or evidence-bound review of a supplied
  design. Use designing-interfaces for a new layout or redesign proposal;
  not for implementation or a general code review.
---

# Reviewing designs

Review only the requested artifact and task. Establish the intended user goal,
requirements, actual content, states and viewing context from available evidence.
A screenshot or textual snapshot describes only the supplied state; it does not
prove behavior, keyboard access, responsive transitions, compliance or user
outcomes. Inspect additional states or rendered views when available and
authorized; otherwise state what is not observable. Do not edit files, create
design artifacts, execute commands that mutate the project, or publish findings
as part of a read-only review.

Scope negative findings to the evidence: no visible guidance in the supplied
state is an observation; no recovery exists or the task cannot complete requires
additional flow evidence. Do not label a blockage permanent from a single state.
Describe possible impact conditionally. A closing caveat does not correct an
earlier unqualified verdict.

Trace each consequential issue to a specific observed element and its impact on
the stated task. Distinguish a demonstrated defect from a hypothesis or taste;
explain any missing evidence. Consider hierarchy, meaningful grouping, accurate
labels, interaction and recovery states, responsive content preservation and
relevant accessibility requirements. Do not prescribe arbitrary font or spacing
numbers or assert conformance from appearance alone. Rank actionable findings by
impact, propose proportionate remedies, and report scope and limitations. If no
issue is supported, say so rather than inventing one.

Read [critique evidence](references/evidence.md) when a specific visual or flow
judgment, conflicting reference, or handoff question needs research context.
These source-derived suggestions are not independent validation of the reviewed
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
