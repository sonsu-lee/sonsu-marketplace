# Parent tickets

Read this when a request spans parts that can be prioritized, deferred, or
completed independently, or when creating, updating, or splitting a parent,
epic, or tracker project. The platform reference decides the native container.

## Workflow

1. **Decide whether to split.** Use a parent only when the shared goal must stay
   visible while separate children progress. Keep a small change in one ticket;
   never create a parent with one child or children for steps one person
   completes together. Code, necessary tests, and required documentation stay
   together. If the problem is known but the approach remains open, use an
   investigation child or unresolved question instead of guessed implementation
   children; do not invent a split the context cannot support.
2. **Write the shared agreement in the parent.**
   - **Problem:** State the current situation and why it matters, ideally with
     a concrete case showing why the status quo fails.
   - **Desired outcome:** Describe the observable result when the parts work
     together. Distinguish delivery from later evaluation when both matter.
   - **Exclusions:** Include only work a reasonable assignee might otherwise
     include, such as an adjacent capability. Record a time or effort limit only
     when established; do not invent one.
   - **Ordering:** State dependencies between children that the tracker does not
     show; omit this when there are none. Put the proposed split outside the
     parent body in a draft, and do not repeat child lists the tracker shows
     natively, such as sub-issues.
   - **Context:** Link decisions, designs, and evidence instead of copying them.
3. **Write the children.** Give each its own problem and judgeable outcome.
   Link the parent for shared policy, retaining the local constraint needed to
   act safely rather than the whole specification. Each requirement has one
   owning ticket. If a child is cancelled, record in the parent whether its
   requirement was removed, replaced, or moved.
4. **Account for completion.** Explicitly include integration, rollout, or
   end-to-end verification when part of the outcome; make it a separate child
   if the tracker closes parents automatically.

## Gotchas

- Shared parent membership does not imply ordering between children.
- A parent is not complete merely because its children are closed.

## Sources

- [Shape Up: Write the Pitch][pitch]: problem, appetite, solution, rabbit holes,
  and no-gos as ingredients of shaped work.
- [Linear Method: Principles & Practices][linear-method]: short project specs and
  a single owner.
- [GitLab epics][gitlab-epics]: smaller deliverables that add incremental value.

[pitch]: https://basecamp.com/shapeup/1.5-chapter-06
[linear-method]: https://linear.app/method/introduction
[gitlab-epics]: https://docs.gitlab.com/user/group/epics/
