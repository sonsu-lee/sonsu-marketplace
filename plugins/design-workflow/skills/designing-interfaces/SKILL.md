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

Design interfaces around real tasks and content while preserving functionality
and reporting what was actually verified.

## Workflow

1. **Establish the brief.** Identify the user's goal, audience, constraints,
   design system and deliverable. Inspect the interface and real content.
   Preserve requirements, functionality, meaningful content and states,
   including errors, empty states and recovery. Do not remove features or invent
   policy to clean up the composition. Identify consequential unknowns.
2. **Design the interface.** Choose hierarchy from user tasks and compose
   readable groups, controls and responsive layouts around real content. Specify
   what stays fixed, resizes or rearranges, including at intermediate widths.
   Match state and action labels to actual behavior; do not claim success before
   confirmation. Check keyboard access, accessible names and contrast against
   applicable requirements using appropriate tools, not visual guesses.
3. **Inspect and report.** Inspect relevant target sizes and states with actual
   assets. If a browser or state is unavailable, report the limitation rather
   than claiming visual verification. Distinguish observations from proposals,
   list meaningful changes and checks, and identify unresolved tradeoffs.

## Gotchas

- No fixed font or spacing number is universally correct.

## Conditional research

Read only what fits the design decision: [visual judgments](references/visual.md)
for typography, spacing, imagery, icons or visual encoding; [flow judgments](references/flows.md)
for responsive behavior, controls, state, service policy or design rationale;
[handoff workflows](references/handoff.md) when editable deliverables, conflicting
references, destructive edits or production handoff are relevant;
[motion](references/motion.md) when adding, changing or removing animation;
[web on touch devices](references/web-touch-platform.md) when a web interface
will be used on phones or tablets. These are contextual heuristics, not
universal rules or evidence of user outcomes.

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
