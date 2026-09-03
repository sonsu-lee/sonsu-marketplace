# Figma product-design quality contract

## Canvas structure

- Inspect the current page, selection, nearby screens, components, variables and styles before changing nodes.
- Use sections to organize features or review states and top-level frames for product screens.
- Prefer semantic layer names that describe role or content. Use groups only for temporary grouping that does
  not need frame layout, constraints, clipping or prototype behavior.
- Build a parent wrapper and screen skeleton before adding detailed content. Avoid orphan top-level fragments.
- Separate canonical handoff or prototype states from exploration and archive material so an experiment is not
  mistaken for the source of truth. Use the project's existing page and naming convention instead of imposing a
  universal numbering scheme.
- Split a file when permission, ownership, library publication, load/performance or lifecycle boundaries differ;
  do not split merely to satisfy an arbitrary frame count.

## Auto Layout and responsive behavior

Use Auto Layout when sibling order, content size, spacing or alignment should determine the layout. Select
vertical, horizontal or supported grid flow, wrapping, alignment, distribution, baseline alignment, gap and
padding from the intended relationship. Use min/max width and height when a real product boundary exists rather
than as a substitute for testing.

| Sizing | Use when |
| --- | --- |
| `HUG` | Content determines the axis size |
| `FILL` | A child should consume available space from an Auto Layout parent |
| `FIXED` | Geometry is intentionally stable, such as an icon slot or touch target |

Append a child to its Auto Layout parent before assigning `FILL`. Use constraints for anchoring children inside
non-Auto Layout or fixed-position frames. Use absolute positioning for overlays and decorative overlap, not to
avoid defining ordinary structure.

Auto Layout is not a goal by itself. Reject wrappers that add no semantic, resizing or alignment behavior. Treat
clipping and overflow as explicit behavior; do not hide layout defects by enabling clipping. Layout grids and
guides align content to a page system but do not replace the child sizing relationship provided by Auto Layout.

Validate a component through an instance before declaring it complete. Put that instance inside a realistic
screen parent and test:

- narrow and wide containers, including real min/max boundaries
- short labels, long labels, multiline text, long numbers and error copy
- empty values, optional leading/trailing elements and hidden items
- localized content with materially different lengths
- 0/1/many repeated items and item insertion/removal
- icon-present and icon-absent states

Inspect both screenshot and node sizing after each material section.

## Components and variables

Search in this order: Code Connected component, enabled library, local component, existing screen pattern, then
new component. Do not detach an instance merely to force a visual match.

- Use variants for distinct state, type or size axes.
- Use Boolean, Text and Instance swap properties for controlled content changes.
- Use Slot only when free-form nested content is truly required and the target library accepts the current Slot
  capability.
- Use preferred instances to constrain or recommend valid nested replacements. Expose a nested instance when a
  consumer needs a supported control without deep-selecting internal layers.
- Use interactive components for repeated local state changes when they reduce duplicated prototype frames and
  remain understandable to consumers.
- Reuse the project's naming and token layers. Do not impose a universal primitive/semantic/component hierarchy.
- Bind semantic variables when they exist. Give new variables explicit scope, aliases and a product reason.

Do not put unrelated objects in one component set or pre-build every theoretical combination. Avoid a
mega-component whose consumers must understand unrelated property axes. Base components or hidden implementation
layers remain acceptable when they preserve a shared internal structure that public properties cannot express,
but do not expose them as the consumer API by default.

Treat library changes as an API change. Document component intent and property meaning, test representative
instances or a playground, and distinguish a compatible addition from a breaking rename, removal, property-type
change or layout behavior change before publication.

## Variables, styles and tokens

Use the current provider's supported color, number, string and Boolean variables with collections, groups, modes
and aliases that reflect the product's actual contexts. Primitive variables describe available values; semantic
variables describe usage. Add a component-specific token when that component must evolve independently, not for
every raw value.

- Do not tokenize every one-off value. Prioritize repeated or meaning-bearing values.
- Do not mix unrelated theme, density, breakpoint, locale or brand dimensions into one mode axis.
- Apply variable scopes and publishing visibility so consumers see valid choices.
- Add variable descriptions and platform code syntax when the design-to-code contract uses them.
- Use styles for reusable composite appearance or typography where they remain the project convention; do not
  replace all styles with variables mechanically.

## Text and handoff

Confirm the actual product font before editing text. Load it when the current provider exposes `font_load`; when a
required font is unsupported or unavailable, do not substitute a different font silently and mark the affected
measurement or visual scope `blocked` or `inconclusive`. Select Auto width, Auto height or fixed-size text from the
intended wrapping behavior. Use text styles or typography variables according to the project contract and preserve
line height, paragraph spacing and vertical trim when they are meaningful. Use realistic content and the intended
max-line or truncation behavior; distinguish deliberate truncation from accidental clipping.

For handoff, preserve component descriptions, external documentation links, useful development, interaction,
accessibility and content annotations, exact assets and Code Connect mappings when they exist. Mark Ready for dev,
Changed or Completed only when the team's current workflow defines those states and the relevant frame, section
or component is actually ready.

The handoff should expose happy path, empty/loading/error/permission states, responsive behavior, content limits,
focus and keyboard expectations, scroll/sticky behavior, interaction results, icon assets and component/token
mapping. After a change, re-review the affected component, consuming screen and connected prototype path rather
than treating a final screenshot as complete evidence.
