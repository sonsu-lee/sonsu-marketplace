# Design tool routing

Choose the product that should own the final artifact. Do not move work to another product merely because its
tool is available.

| Work | Canonical product | Supporting tool | Source of truth | Avoid | Why |
| --- | --- | --- | --- | --- | --- |
| Product screen and responsive layout | Figma Design | Official Figma canvas skill | Target Figma file | draw.io | Native Auto Layout, components and variables must remain editable |
| Button navigation or screen state flow | Figma Design | `figma-prototype-flow` | Figma reactions and named states | draw.io, FigJam | The canonical flow must execute from the actual control |
| Modal, drawer, popover or menu | Figma Design | `figma-prototype-flow` | Figma overlay reactions and dismissal behavior | draw.io | Static arrows cannot prove overlay behavior |
| Early user journey workshop | FigJam | Official FigJam skill | Editable FigJam board | Figma Design as the workshop canvas | Loose collaboration is the deliverable; it is not the final product prototype |
| AWS or network architecture | draw.io | Architecture icon libraries | Native `.drawio` file | Figma Design | System topology benefits from diagram semantics and native source |
| Service or technical data flow | draw.io | Sequence or data-flow notation | Native `.drawio` file | Figma product frames | Technical flow is not product-screen interaction |
| Code-based UI visual editing | Paper Design | Paper MCP | Paper DOM, styles, tokens and JSX | draw.io | The value is code-connected structure and roundtrip |
| Design-system component authoring | Figma Design | Official Figma library skill | Published/local Figma library and its contract | Paper as an assumed library replacement | Component properties, variables and publication are Figma-native responsibilities |
| Developer handoff | Figma Design or Paper, matching the canonical artifact | Dev Mode, Code Connect or exact JSX/style readback | The chosen artifact plus verified code mapping | Duplicate flow sources | Handoff must trace back to the maintained design source |

Use the request's explicit product when it is compatible with the requested result. If a user requests a
clickable product interaction in Paper, explain the current prototype capability gap rather than silently moving
the work to Figma. If a generic “user flow” request lacks enough context to choose among clickable UI,
collaborative ideation and system logic, ask one short artifact question before mutation.

For screen and composed-view creation, combine the local quality-contract skill with the available official
`figma-generate-design` and its `figma-use` prerequisite. Direct design-to-code remains with
`figma-design-to-code`; individual component and library authoring remains with `figma-generate-library`. The
local skill does not replace those official workflows or add a manifest dependency on them.
