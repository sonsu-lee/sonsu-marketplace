# Icon and vector asset policy

## Source priority

1. Existing design-system icon component
2. An `INSTANCE_SWAP` property on the consuming component
3. Preferred instances that identify supported or recommended replacements
4. Exact SVG from the product codebase or approved icon set
5. Ask for or locate the exact asset

Do not replace a missing icon with emoji, a guessed glyph or a reconstruction made from primitive lines and
shapes. Do not invent a brand mark. If the exact asset is unavailable, stop the affected scope and preserve the
rest of the work.

For SVG insertion, preserve the source `viewBox`, aspect ratio, stroke/fill behavior and explicit width/height.
Resize the resulting node to the intended slot such as 16, 20 or 24 pixels. Replace unresolved `currentColor`
with the literal or semantic variable required by the target system without flattening meaningful vector
structure.

In Figma, use the provider's current exact-asset path such as `figma.createNodeFromSvg` for SVG source or asset
upload for a real file. In Paper, use the current SVG or image insertion capability. Follow the provider-required
skill for exact call syntax rather than preserving a stale community tool name in this policy.

Validate icon family, outlined/filled state, stroke weight, optical alignment, semantic color and behavior across
enabled, hover, pressed, selected and disabled states that the component actually supports. Icon-only controls
need an accessible name in the product contract and a useful design annotation when that name is not otherwise
visible.

Preserve the design system's canvas, safe area, cap, join, corner and pixel-alignment rules. A 16px, 20px or 24px
asset may require its own optical drawing; do not assume that uniform scaling preserves clarity. Keep Figma and
code naming aligned with descriptive names and searchable aliases. Do not duplicate every icon state as variants
inside each consuming component when Instance swap plus the icon system can express the combination.

Keep strokes editable when governance expects continued vector editing. Outline or flatten strokes only when the
approved export or rendering contract requires it, and confirm that multiple vector paths and color bindings
survive the conversion.

For changed interactions, compare the relevant before and after states so the icon does not accidentally change
size, position or meaning.
