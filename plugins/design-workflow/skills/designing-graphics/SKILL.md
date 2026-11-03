---
name: designing-graphics
description: >-
  Design or refine icons, illustrations and visual identity assets, including
  their intended rendering and delivery. Not for photo retouching, equipment
  advice, promotion or design-career guidance.
---

# Designing graphics

Design or refine graphics for their intended use and delivery, preserving
authorized scope and reporting only observed results.

## Workflow

1. **Establish the brief.** Identify purpose, audience, existing identity,
   authoritative assets, editable format, output and reproduction constraints.
   Preserve supplied proportions, meaningful content, required editability and
   existing treatments unless a change is authorized. Otherwise propose the
   change and ask whether to adopt it; this is a scope decision, not sign-off.
   Do not invent approval or production requirements.
2. **Design for the use.** Judge icons as a family by weight, corners and
   silhouettes, and inspect exports at actual size in the intended renderer.
   Simplify collapsed detail while preserving meaning. Make illustration and
   identity serve the brief and uses. Before destroying a representation needed
   for editing or comparison, preserve an appropriate earlier state. If actual
   reproduction constraints require a variant, consider the whole lockup and
   retain the full-color original.
3. **Inspect and report.** Inspect available output in context and report what
   was rendered, checked and delivered. State missing assets, rendering or
   production evidence rather than inventing results.

## Conditional research

Read [graphic craft and handoff](references/craft.md) when icon construction,
rendering, graphic encoding, editable stages, reproduction variants, or
master/preview delivery need the corresponding research context.
The research is conditional guidance, not a universal recipe or measured outcome.

## Gotchas

- Approval status and responsibility are project facts, not conclusions from
  missing files or tests. Keep them unknown if not supplied; do not call them
  unapproved, not yet approved or undecided, or require sign-off. Advise
  confirming whether approval is needed and who gives it.
- Do not assume a preview is an editable master. A vector canvas or still
  preview does not establish manufacturing feasibility, color accuracy or
  approval.
- Not every physical medium prohibits gradients.

## Optional omp strict run

Codex and Claude Code receive guidance only, not omp enforcement. In omp,
strict mode remains dormant until the operator invokes
`/design-start <plan-json-path>` and confirms the plan: mode `graphics`, or
`advisory` for advice without captures, checks or edits; exact
workspace-relative paths; goal; the original request; confirmed project facts;
visual captures and any approved check executable and argv. Do not start or
approve it yourself. The capture adapter supports approved HTML/SVG files or
loopback web targets, not arbitrary native editor documents; if the required
evidence cannot be captured, report that limit rather than substituting an
unrelated image.

While active use `design_status`, `design_read`, `design_write`,
`design_capture`, and declared `design_check` operations within scope. When the
evidence is ready, stop and ask the operator to run `/design-report`, which
writes and fact-checks the final report outside the conversation, then
`/design-accept` to publish it unchanged. Receipts record operations, not
design quality or production approval. If the task cannot proceed or evidence
is missing, ask the operator to use `/design-stop`, `/design-blocked reason` or
`/design-limited reason`; these are non-success exits. Never self-accept or
fabricate evidence. This in-process extension is not an OS sandbox; authorized
checks execute processes. The official result is the published report, not
your prose.
