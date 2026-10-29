---
name: designing-interfaces
description: >-
  Design or improve a digital interface: propose new layouts or redesigns,
  responsive behavior, content hierarchy and interaction states, or implement
  them. Applies to design proposals even when no files should be changed.
  Use reviewing-designs to evaluate an existing design for issues, and
  designing-graphics for standalone icons, illustration or identity assets.
---

# Designing interfaces

Establish the user's goal, audience, relevant constraints, existing design
system and the intended deliverable. Inspect the existing interface and its
real content before changing it. Preserve requirements, functionality,
meaningful content and state, including error, empty and recovery paths; do
not remove features or invent policy to make a composition look cleaner.
Identify unknowns that materially change the solution.

Choose a hierarchy from the user's tasks, then compose readable groups,
controls and responsive arrangements around real content. Specify what stays
fixed, resizes or rearranges, and consider intermediate widths. Design state
and action labels to match actual behavior; avoid claiming success before the
system has confirmed it. Consider keyboard, accessible names and contrast using
the applicable project requirements and appropriate tools, not a visual guess.
No fixed font or spacing number is universally correct.

Inspect the result at relevant target sizes and states, including actual assets.
If a browser or needed state is unavailable, report the limitation instead of
claiming visual verification. Distinguish observations from proposals, list
meaningful changes and checks performed, and identify unresolved tradeoffs.

## Conditional research

Read only what fits the design decision: [visual judgments](references/visual.md)
for typography, spacing, imagery, icons or visual encoding; [flow judgments](references/flows.md)
for responsive behavior, controls, state, service policy or design rationale;
[handoff workflows](references/handoff.md) when editable deliverables, conflicting
references, destructive edits or production handoff are relevant. These are
contextual heuristics, not universal rules or evidence of user outcomes.

## Optional omp strict run

The portable skill alone is guidance, not enforcement. Codex and Claude Code do
not acquire the omp extension's controls. In omp, strict mode is dormant until
the operator explicitly invokes `/design-start <plan-json-path>` and confirms
the displayed plan. The plan specifies mode `design`, or `advisory` for a
proposal without captures, checks or edits; exact workspace-relative file
paths; goal; the original request; confirmed project facts; capture
targets/viewports/scenarios and any approved check executable and argv. Visual
work needs a capture. Do not start, approve or change the plan on the
operator's behalf.

Once active, use `design_status`, `design_read`, `design_write`,
`design_capture` and declared `design_check` operations for the approved scope.
When fresh evidence exists, stop and ask the operator to run `/design-report`,
which writes and fact-checks the final report outside the conversation, then
`/design-accept` to publish it unchanged. A receipt proves only the recorded
operation, not visual quality or compliance. If a capture/check cannot be
performed or scope must change, explain the blocker and ask the operator to use
`/design-stop`, `/design-blocked reason`, or `/design-limited reason`; these are
non-success exits. Do not fabricate evidence, self-accept, or bypass the gate.
The extension runs in-process, not as an OS sandbox; approved checks are process
execution, not sandboxed. The official result is the published report, not
assistant prose.
