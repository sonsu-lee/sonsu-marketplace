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
   readable groups, controls and responsive layouts around real content. Settle
   the order and grouping of content before visual styling, and note the reason
   for each structural choice. Specify what stays fixed, resizes or rearranges,
   including at intermediate widths. Match state and action labels to actual
   behavior; do not claim success before confirmation. Consider keyboard
   access, accessible names and contrast using applicable requirements and
   appropriate tools, not visual guesses.
3. **Inspect and report.** Inspect relevant target sizes and states with actual
   assets. If a browser or state is unavailable, report the limitation rather
   than claiming visual verification. Distinguish observations from proposals,
   list meaningful changes and checks, and identify unresolved tradeoffs.

For requested prototypes, explore genuinely different directions on named
axes with realistic content and working interactions in an authorized isolated
surface. Present tradeoffs and wait for the user's choice before integration.
When choosing a UI library, inspect existing dependencies and components first;
reuse them where suitable and do not install or replace one without authority.
For a genuine new selection, Emil's curated starting points include Base UI
for accessible primitives, cmdk for command menus, Sonner for toasts, Vaul for
drawers, input-otp for verification codes, Motion for complex motion, Recharts
for general charts, Liveline for streaming charts, dnd kit for drag-and-drop,
Virtuoso for virtualization, Zustand for shared state, clsx for class composition,
and cva for typed variants. Check suitability and current maintenance rather
than treating this list as mandatory or replacing a working dependency.

## Evaluate the design

Assess goals and states, hierarchy and interaction, accessibility, actual screen
evidence, and constraints and limits. Score applicable items 0, 1, or 2, record
exclusions and reasons, and normalize to 10. Require 8/10 and verified
requirements, authority, security, data safety, confirmed contracts, and stage
evidence. Correct failures and reevaluate up to three times, not unchanged.
If still unsuccessful, report each score, mandatory conditions, evidence, and
blockers. Wait for required decisions, permission, or access; a score does not
replace an actual screen check or required independent review.

## Gotchas

- No fixed font or spacing number is universally correct.

## Conditional research

Read only the references that fit the design decision:

- [Visual judgments](references/visual.md): typography, spacing, imagery,
  icons or visual encoding.
- [Input and navigation](references/input-and-navigation.md): hit areas,
  icon labels, navigation, selection and input controls, which questions to
  ask, value before a costly verification, data or consent request, and
  pressable or scrollable cues.
- [States and feedback](references/states-and-feedback.md): selection and
  status, risk warnings, composing, message order across turns, overlays,
  progress and long processing, AI answers, suggestions, errors and lockout,
  screen-reader state and reading order, and empty history.
- [Actions, policy and commitments](references/commitments-and-policy.md):
  action labels and copy across a flow, operational counterparts, policy
  branches, money, exit friction, defaults and consent.
- [Direction and rationale](references/direction-and-rationale.md): studying
  references, comparing alternatives, open or structural directions, design
  rationale and redesign transitions.
- [Responsive layout](references/responsive.md): fixed, fluid and changing
  elements across widths.
- [Handoff workflows](references/handoff.md): editable deliverables,
  component specifications, conflicting references, destructive edits or
  production handoff.
- [Motion](references/motion.md): adding, changing or removing animation, or
  the rendering cost of effects such as blur.
- [Web on touch devices](references/web-touch-platform.md): a web interface
  used on phones or tablets.

These are contextual heuristics, not universal rules or evidence of user
outcomes.

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
