# Parent tickets

Read this when a request spans several parts that can be prioritized,
deferred, or completed independently, or when creating, updating, or splitting
a parent, epic, or tracker project. The platform reference decides which native
container to use.

## Decide whether a parent is needed

Use a parent only when the shared goal must stay visible while separate
children progress. A small change stays one ticket. Do not create a parent with
a single child, or children for steps one person completes together; code,
necessary tests, and required documentation stay in the same ticket.

Do not invent decomposition the context cannot support. When the problem is
known but the approach is still open, keep the open question visible as an
investigation child or an unresolved question instead of listing guessed
implementation children.

## Write the parent

Hold the shared agreement in the parent so children do not repeat it:

- **Problem:** the current situation and why it matters, ideally grounded in
  one concrete case that shows why the status quo fails.
- **Desired outcome:** the observable result once the parts work together.
  Distinguish delivering the change from later evaluating its effect when both
  matter.
- **Scope and non-goals:** what is included and what is deliberately excluded,
  so children do not expand the work. Record a known time or effort limit only
  when it is established; do not invent one.
- **Children:** each child's one-line outcome and real ordering dependencies.
  Shared membership under a parent does not imply order.
- **Context:** decisions, designs, and evidence, linked rather than copied.

A parent is not complete merely because its children are closed. When
integration, rollout, or end-to-end verification is part of the outcome, make
it explicit, as its own child if the tracker closes parents automatically.

## Write the children

Give each child its own problem and an independently judgeable outcome, and
link the parent for shared context instead of copying its specification. Each
requirement belongs to one ticket. If a child is cancelled, record in the parent
whether its requirement was removed, replaced, or moved.

## Sources

- [Shape Up: Write the Pitch][pitch]: problem, appetite, solution, rabbit
  holes, and no-gos as the ingredients of shaped work.
- [Linear Method: Principles & Practices][linear-method]: short project specs
  and a single owner.
- [GitLab epics][gitlab-epics]: breaking large features into smaller
  deliverables that add incremental value.

[pitch]: https://basecamp.com/shapeup/1.5-chapter-06
[linear-method]: https://linear.app/method/introduction
[gitlab-epics]: https://docs.gitlab.com/user/group/epics/
