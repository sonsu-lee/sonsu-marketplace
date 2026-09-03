# Figma native editing practice

This reference helps with human Figma workflow guidance and manual cleanup. It does not turn UI shortcuts into
MCP or Plugin API capabilities, and shortcut fluency is not an artifact quality gate.

| Native action | Useful intent | Classification | Automation relevance |
| --- | --- | --- | --- |
| Deep select or Select layer menu | Reach the intended nested layer without detaching or flattening structure | Safe targeting | API uses node IDs or queries instead of the UI gesture |
| Parent, child and sibling navigation | Inspect hierarchy while preserving current context | Structural understanding | Equivalent to tree traversal, not keyboard emulation |
| Select matching layers | Find equivalent roles before a controlled batch change | Safe repetition | Automate only after matching a semantic property, component or stable query |
| Multi-edit | Apply the same verified property to equivalent nodes | Safe repetition | Batch updates need the same target proof and post-write readback |
| Multi-edit variants | Compare or change corresponding layers across component variants | Component consistency | Useful concept; API implementation depends on current component structure |
| Smart selection and Tidy up | Normalize spacing and ordering in repeated manual selections | Human cleanup | Do not use as a substitute for Auto Layout in final structure |
| Batch rename | Apply an agreed semantic naming pattern | Structure improvement | Preserve unique roles and avoid broad text replacement |
| Copy/paste properties | Transfer a known compatible appearance or layout property | Safe repetition | Verify token/component bindings are not flattened to raw values |
| Paste over selection | Replace equivalent selected content while keeping placement | Human speed | Confirm instance, property and asset semantics after replacement |
| Collapse or expand layers | Reduce navigation noise and inspect one subtree | Human speed | No effect on artifact quality |
| Measurement | Inspect spacing, size and relationship | Review evidence | Prefer metadata/readback for automated exact values |
| Nudge amount | Make controlled optical adjustment | Human speed | Do not encode arbitrary nudges as a universal spacing rule |
| Quick Actions or Actions menu | Find a command without memorizing its location | Human speed | Availability and command names can change; not an API contract |

Before a batch edit, define the equivalence predicate: same component property, semantic role, token binding or
explicitly selected targets. After the edit, inspect representative first, middle and last nodes and confirm that
unrelated instances were not changed.

Use Tidy up or manual spacing adjustments during exploration, then express the final repeatable relationship with
Auto Layout when content or item count should control the structure. Preserve intentional optical corrections as
scoped exceptions rather than converting them into global spacing values.

Keyboard combinations vary by operating system and can change. When the user asks for exact shortcuts, verify the
current Figma documentation for the user's platform instead of relying on this reference.
