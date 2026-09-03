# Product interaction specification

## Figma interaction contract

Represent each meaningful transition with three synchronized evidence layers:

1. An executable reaction on the actual control: trigger, action, destination or result, transition and condition.
2. A concise native annotation: `Trigger → Result [Condition]`.
3. Named state frames organized around one user goal and one flow starting point.

Track the following fields for important interactions:

```text
Trigger
→ Action
→ Destination or next state
→ Condition
→ Visible result
→ Back or close behavior
→ Edge case
```

Use left-to-right order for the happy path and place error or alternative branches near the state that creates
them. Prefer component variants or variables for small reusable states; create separate frames when a state
changes the screen, is needed for review, or must be a prototype destination.

Cover the primary action, loading or submission when visible, success, meaningful error, cancel/back and recovery.
Do not create every hover or focus state as a separate frame when the component model already expresses it.
Use interactive components, variables and conditionals when they make toggle, checkbox, tab, accordion, selected
item, count, permission or authentication behavior clearer than duplicated screens. Use separate frames for
meaningful screen-level empty/populated, submit/loading/success/error or permission outcomes. Preserve fixed,
sticky, scroll and overflow behavior in both the visual state and prototype.

Example annotation set:

```text
Tap Save → Submitting [form valid]
Save succeeds → Success toast + Detail screen
Save fails → Inline errors; remain on form
Tap Cancel → Previous screen
```

Prototype validation requires a named starting point, resolvable destinations, no unexplained orphan state,
and playback of the primary and failure paths. A drawn arrow or annotation alone is documentation, not a passed
clickable prototype.

When the available Figma provider exposes the Plugin API through `use_figma`, use `setReactionsAsync` on the
actual control and read its `reactions` back. Keep trigger, action type and node navigation in their distinct API
fields:

| Intent | `Trigger.type` | `Action.type` | `Action.navigation` |
| --- | --- | --- | --- |
| Click, hover, press or drag | `ON_CLICK`, `ON_HOVER`, `ON_PRESS`, `ON_DRAG` | depends on the result | not applicable by itself |
| Move to a screen, overlay or component state | chosen trigger | `NODE` | `NAVIGATE`, `OVERLAY`, `SWAP`, `CHANGE_TO` |
| Scroll to content | chosen trigger | `NODE` | `SCROLL_TO` |
| Return or close | chosen trigger | `BACK`, `CLOSE` | not applicable |
| Advanced state | chosen trigger | `SET_VARIABLE`, `SET_VARIABLE_MODE`, `CONDITIONAL` | action-dependent |

Use the current provider schema if it differs from this snapshot. A minimal navigation reaction has a `trigger`
and a non-empty `actions` array:

```js
await control.setReactionsAsync([
  {
    trigger: { type: "ON_CLICK" },
    actions: [
      {
        type: "NODE",
        navigation: "NAVIGATE",
        destinationId,
        transition: null,
      },
    ],
  },
]);
```

Read back `reactions[0].trigger.type`, `reactions[0].actions[0].type`, `navigation` and `destinationId`
independently. Do not use a deprecated single `action` field or treat `{ type: "NAVIGATE" }` as a node action.

Use overlay actions for modal, drawer, popover and menu behavior; define dismissal and close behavior explicitly.
Use `CHANGE_TO` for component states such as toggle, pressed or selected when an interactive component is the
appropriate model. Use multiple actions or conditionals only when the user-visible behavior actually has those
steps or branches.

Preserve transition type, duration and easing when an existing product convention defines them. Do not invent
motion timing merely to fill every optional field. Set or preserve the page's `flowStartingPoints` for named
flows and confirm that each start node can reach its intended states.

## Paper interaction contract

When the connected Paper tool surface lacks native reaction APIs, represent the same flow as named before/after
artboards and comments that record trigger, result and condition. Mark the result `spec-only` and prototype
execution `not_run`. Do not report the state map as clickable behavior.
