# Model, agent and local automation architecture

This reference separates design policy from execution configuration. It is a dated operational recommendation,
not a Figma-specific benchmark result. Re-check the current Codex model catalog and provider tool schemas before
applying it.

## Responsibility boundaries

| Layer | Responsibility | Does not own |
| --- | --- | --- |
| Design skill | Routing, quality contract, evidence and stop conditions | Session model changes or provider installation |
| Codex profile | User-selected session model and reasoning effort | Artifact-specific permissions |
| Custom agent | A bounded reader, writer, auditor or plugin-builder role | Concurrent ownership of the same conflict domain |
| Figma MCP | Current Figma context and native canvas operations | Product policy or unsupported capability claims |
| Local Figma plugin | Approved deterministic transformations and QA | Open-ended design judgment |

A skill cannot silently switch the current session model. Apply a model or reasoning choice through the user's
session/profile or an explicitly created agent. Do not add custom agents merely to encode a recommendation that a
reference can express.

## Provisional model routing

The current runtime catalog on 2026-09-03 describes `gpt-5.6-sol` as the reliable agentic workhorse,
`gpt-5.6-terra` as the balanced everyday coding model and `gpt-5.6-luna` as the fast, affordable model. No public
Figma-specific head-to-head benchmark was found for these models, so the following policy is provisional.

| Task | Baseline | Escalate when |
| --- | --- | --- |
| New screen or UX flow | `gpt-5.6-sol` + `medium` | Use `high` for intertwined layout, states or ambiguous constraints |
| Complex Auto Layout, component system or interaction audit | `gpt-5.6-sol` + `high` | Consider `xhigh` only for large migrations or final cross-system review |
| Routine existing-screen edit or structure inventory | `gpt-5.6-terra` + `medium` | Move to Sol when representative review finds missed dependencies |
| Narrow deterministic repetition | `gpt-5.6-luna` + `medium` | Keep only after measured quality and retry cost beat the baseline |
| Local Figma plugin implementation | `gpt-5.6-terra` + `high` | Use Sol + high for complex Plugin API state, idempotency or debugging |

Do not make `high`, `xhigh`, `max` or `ultra` a universal default. `max` or `ultra` requires measured benefit on
representative cases. Higher reasoning does not repair a stale selection, missing design-system context, incorrect
tool routing or unsupported provider API. Treat `ultra` as a session reasoning-effort choice; it does not itself
create custom agents, grant orchestration authority or relax the conflict-domain single-writer rule. Evaluate Paper
separately instead of inheriting Figma results.

Before model escalation:

1. Confirm the exact file URL, page, frame or selection.
2. State the final artifact and unchanged area.
3. Supply the component, variable, token and icon source.
4. Select the provider and required prerequisite skill explicitly.
5. Split a broad selection into component or logical regions.
6. Repeat inspect, small write and validate on the failed scope.
7. Raise reasoning one step, then change model only if the earlier checks do not resolve the gap.

## Custom-agent and concurrency policy

Keep v0.1 single-agent by default. A future reader or auditor may run in parallel because it is read-only. A writer
must own one conflict domain at a time and re-read the target immediately before mutation. Multiple writers are
allowed only for provider-confirmed independent pages or files with no shared component, variable, prototype or
editor-state dependency. The auditor judges the artifact evidence, not the writer's self-report.

Add `figma_reader`, `figma_writer`, `figma_auditor` or `figma_plugin_builder` agents only after a representative
evaluation shows a repeatable quality, latency or cost benefit. Their model choice remains configuration, not a
skill side effect.

## When to build a local Figma plugin

Use a local plugin candidate when all of these are true:

- the same transformation or QA check recurs often enough to justify maintenance
- inputs, allowed targets, unchanged areas and outputs can be validated deterministically
- the operation can preview its target set and is idempotent or has a bounded rollback strategy
- Plugin API coverage exists for the required nodes, assets and reactions
- explicit user authorization covers creating, running and maintaining the plugin

Suitable candidates include token-binding audits, semantic rename previews, approved icon replacement, repeated
component migration and prototype-link integrity checks. Open-ended layout, UX judgment and visual direction stay
with the design workflow. Once a deterministic plugin exists, running it should not require a model call unless a
new judgment, diagnosis or unsupported input appears.

Do not create the plugin as an incidental fallback during a live canvas task. Design its manifest, permissions,
selection scope, preview, dry-run or change report, error recovery, versioning and fixture tests as a separately
approved engineering change.

## Evaluation gate

Compare representative Figma and Paper cases separately. Measure requirement completion, native structure,
resize behavior, reuse, missing interactions, manual corrections, tool failures/retries, unsupported claims,
latency, usage and repeated-run variance. Run one sample per combination to remove clearly weak candidates, then
repeat only the finalists. Model/effort cost, repetitions, live mutation scope, target files and cleanup require
separate approval; until then the comparative result is `not_run`.
