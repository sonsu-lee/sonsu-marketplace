# React judgment calls

Read this with [judgment calls](judgment.md) when a change adds or keeps a
React Effect, or passes props through components that do not use them.

## Effects

An Effect needs an answer to "which external system does this synchronize
with, and on what change?" Replacing a connection when `roomId` changes and
closing the previous one is such an answer. Without one:

- A value computable from props or state is computed during render.
- The result of a user action is handled in that event handler.
- A subscription to an external store uses the hook built for it.

Do not hide a justified Effect inside a custom hook to satisfy a rule, and do
not try `useSyncExternalStore`, `use`, and `Suspense` in turn until one
compiles. An exception that allows an Effect never suspends its dependency
check.

## Passing props

Judge by which components a change drags in, not by depth. If removing a prop
means editing several components that never read it, prefer composition
(`children` or a slot) first. If distant consumers share one feature's state,
consider a context scoped to that feature.

Keep explicit props when an intermediate component reads or transforms the
value, or when forwarding is the component's public contract, as in a design
system wrapper. Depth alone is not a reason to introduce a context.
