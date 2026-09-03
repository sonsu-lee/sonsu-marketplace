# Capability, permission and evidence

## Capability preflight

Before mutation, identify the current provider tools, required provider skill, target document, authenticated
identity, permission level and requested scope. A plugin being installed does not prove that a tool, desktop
application, editable file or full seat is available.

Record each capability separately before using it: `structure_read`, `screenshot`, `reaction_write`,
`reaction_readback`, `prototype_playback`, `font_load`, `asset_import`, `export` and provider cleanup. Use
`supported`, `unsupported` or `unavailable` for the current environment; one supported capability does not imply
the others.

When a provider requires a prerequisite skill before a tool call, load that installed skill and follow its current
contract. Do not reproduce or assume the contents of a provider skill that is unavailable.

Treat the connected runtime tool schema as the operational source of truth. When public documentation, a cached
skill and the live schema disagree, use only the capability confirmed for the current call and record the mismatch
as `inconclusive`; do not preserve a stale tool name or assume that a documented limitation still applies. For
example, image upload support must be decided from the current asset tools rather than a cached statement alone.

## Authorization boundary

Reading or auditing a file does not authorize mutation. Creating or editing a Figma or Paper artifact requires
the user's request to include that external change and requires an exact target or an approved new file. Creating
assets, publishing a library, changing Code Connect mappings and exporting files are separate side effects when
they exceed the requested result.

## Evidence layers

| Claim | Required evidence |
| --- | --- |
| Visual layout | Current screenshot of the affected section and whole view when relevant |
| Structural layout | Node tree, Auto Layout/resizing metadata, DOM or computed style readback |
| Reuse | Component instance, property and variable bindings or Paper token references |
| Clickable interaction | Current Figma reaction readback and prototype playback |
| Paper code handoff | Exact JSX and computed styles, then adaptation to the target codebase |
| Cleanup | Provider working-state readback or successful finalization call |

Report results as `passed`, `failed`, `blocked`, `inconclusive`, `not_run`, `not_applicable` or
`accepted_risk`. A screenshot cannot prove structure, an annotation cannot prove a reaction, and a successful
write response cannot prove the final appearance. Preserve successful partial work, read the latest state and
retry only the affected scope.

If reaction write and readback pass but prototype playback is unsupported, report the first two evidence layers
as passed, playback as `not_run` and the overall clickable-interaction claim as `inconclusive`. Distinguish an
unsupported operation from a supported call that failed. If the required font or exact asset cannot be loaded,
do not substitute it silently; mark only the affected visual scope `blocked` or `inconclusive`.

## Conflict-domain single writer

Serialize writes that can invalidate each other's target or assumptions. Conflict domains include:

- the same page subtree or connected set of screen frames
- one component set or instances being changed with its public property contract
- one variable collection, mode or alias graph
- one prototype graph, starting point or connected state set
- writes that depend on the current selection, current page or another mutable editor state

Read-only inspection and separate files can run in parallel. Independent pages in one file may run in parallel only
when the provider explicitly permits it and there are no shared node, component, variable, prototype or editor-state
dependencies. Every writer re-reads its exact target immediately before mutation. If another writer changed the
same conflict domain, serialize, refresh the plan or stop; a file boundary alone is not the lock key.
