# Paper product-design quality contract

## Context and design direction

Load the current Paper MCP guide before using Paper tools. Read basic file information, selection, target tree,
fonts and tokens before mutation. If no design system or visual direction exists, form a concise brief from the
product purpose and user request; do not impose decorative mood, asymmetry or novelty as a universal rule.

## DOM and layout

- Use flex containers, padding and gap for primary layout.
- Do not rely on `margin`, `display:inline`, CSS Grid or HTML tables where the current Paper contract does not
  support them reliably.
- Give repeated rows stable content regions and fixed-width icon, metadata or action lanes where alignment would
  otherwise drift.
- Use real content and the product's available fonts. Treat clipping with fit-content or corrected container
  behavior instead of guessed fixed heights.
- Reuse tokens when available. Do not infer token modes, themes or cross-file live synchronization that the
  current capability does not provide.

Write one visual group at a time. Prefer duplicate plus targeted text/style updates for repeated structures over
rewriting a whole subtree. Preserve unrelated siblings and successful partial writes.

Use exact SVG or image assets and verify their aspect ratio after import. Do not use emoji as interface icons.

## Validation and code roundtrip

After each meaningful group, capture a screenshot and inspect spacing, typography, contrast, alignment,
repetition, clipping and artboard fit. Read the resulting tree and computed styles because a screenshot does not
prove DOM structure or token use.

For code handoff, use exact JSX and computed styles as the Paper source, then adapt them to the target project's
components, tokens and conventions. Do not generate production code from the screenshot alone.

Track the owning artboard of each touched node, deduplicate the artboard IDs and call `finish_working_on_nodes` in
a finalization step on success, partial success and failure paths. Preserve cleanup failure as separate evidence
and lower the overall result to at least `inconclusive` while the working indicator may remain. If the tool surface
has no native prototype API, follow the Paper section of [interaction-spec.md](interaction-spec.md).
