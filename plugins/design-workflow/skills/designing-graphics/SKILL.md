---
name: designing-graphics
description: >-
  Design or refine icons, illustrations and visual identity assets, including
  their intended rendering and delivery. Not for photo retouching, equipment
  advice, promotion or design-career guidance.
---

# Designing graphics

Establish the purpose, audience, existing identity, authoritative assets,
editable format, intended output and real reproduction constraints. Preserve
supplied proportions, meaningful content, required editability and existing
treatments unless the request authorizes a change. If a needed change is not
authorized, propose it and ask whether to adopt it; that is a scope decision,
not a sign-off requirement. Do not assume a preview is the editable master or
invent approval or production requirements.
Approval status and responsibility are project facts, not conclusions from
missing files or tests. When not supplied, keep them unknown throughout the
answer; do not turn unknown into "unapproved", "not yet approved" or "undecided",
and do not prescribe sign-off as a required step. Advise confirming whether
approval is needed and who gives it.

For icons, judge the family together: visual weight, corners and silhouettes,
then inspect the export at its actual size and renderer. Preserve recognizable
meaning while simplifying detail that collapses. For illustration and identity,
make composition and treatment serve the brief and actual uses. If an operation
would destroy a representation needed for later editing or comparison, preserve
an appropriate earlier state. Where real reproduction constraints require an
identity variant, account for the whole lockup and retain the full-color
original; do not assume every physical medium prohibits gradients.

Inspect available output in context and report what was actually rendered,
checked and delivered. A vector canvas or a still preview does not establish
manufacturing feasibility, color-management accuracy or approval. State missing
assets, rendering or production evidence rather than inventing results.

Read [graphic craft and handoff](references/craft.md) when icon construction,
rendering, graphic encoding, editable stages, reproduction variants, or
master/preview delivery need the corresponding research context.
The research is conditional guidance, not a universal recipe or measured outcome.

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
