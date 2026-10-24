---
name: planning-work
description: >-
  Use this skill before implementing non-trivial work, such as a feature, a
  refactor, a change spanning several pull requests, or product and UI planning
  from features to screens, wireframes, and component usage. It produces a
  design plan and waits for approval. Not for small, clear changes, and not for
  writing tickets, ADRs, or pull requests.
---

# Planning work

A plan is a design to agree on before building. Its value is surfacing
tradeoffs and misunderstandings while they are cheap to fix. Planning a change
whose solution is obvious only adds overhead: a plan that says only how to
implement it, with no tradeoffs, should be code. Asking for a plan is not
permission to implement.

## Gather before asking

Read what exists first: the code, docs, designs, tickets, and prior decisions
that bear on the work. Looking facts up is your job; deciding is the user's.

Sort each fact the plan depends on as confirmed (name the source), inferred
(name the basis), or unknown. Ask only about unknowns and inferences that would
change the plan. Give each question a recommended answer and a one-line reason,
and word it so "yes" accepts the recommendation. Ask the questions that do not
depend on each other together, then ask what their answers unblock. Do not
interrogate on points the plan can state as an assumption and move on.

## Shape the plan

- **Goals and non-goals.** A non-goal is something that could plausibly be a
  goal and is deliberately excluded, not a negated goal such as "must not
  crash". Naming them is how scope disagreements surface early.
- **Big picture first.** Draw the overall structure before details: components
  and data flow for code; for product or UI work, features to screens to
  wireframes to component usage. Use the project's own terms and its design
  system's existing components; a needed new one is a proposal, not a given.
- **Each element.** For every element say what it is, why it is needed, how it
  works, and which alternatives were rejected and why. The rejected
  alternatives and their tradeoffs are the part most worth reading.
- **Traceability.** Each lower-level item names the higher-level requirement
  that needs it. An item with no parent is cut or becomes a question; a
  requirement with no children is a gap. Check both directions before
  presenting.

Size the plan to the work: a small change needs a page, not a template.

## Edge cases

Run a pre-mortem: assume the work failed and list why. Keep only causes
reachable from inputs, callers, or data states you can name from the code or
the requirements. Drop "just in case" causes. Each kept cause gets a handling
decision or an explicit "accepted".

## Verification

Derive scenarios from the goals and the kept edge cases. For each, choose the
lowest test level that proves it, and state the plausible bug the test would
catch. A scenario that names no bug does not need a test. Include how the final
result will be observed to work, for example a command, screen, or output.

## Split delivery

One purpose per pull request. Where pull requests depend on each other, state
the order and what each one leaves working; independent ones need no order.
Do not split a change from the tests and documentation it needs.

## Share early, mark the state

Mark the plan Draft or Decided at the top. Share a short draft first: goals,
non-goals, the big-picture diagram, and open questions. Polish the detailed
sections only after the direction is agreed. Early rough sharing and heavily
rewritten memos are both established practices; the point is that polish spent
on a rejected direction is wasted.

## Reader check

Before presenting the full plan for approval, have a reader without your
context test it. Where subagents are available, start a fresh one with only the
plan and ask it to restate the goal, say what it would build in the first pull
request, and list anything ambiguous, contradictory, or assumed. Otherwise
perform a self-review and disclose that no independent reader was available;
do not present rereading your own work as a fresh-reader test. Fix gaps in the
plan rather than explaining them away in the review brief.

## Approval and records

Present the plan with its state, assumptions still open, and the decision you
need. Wait for explicit approval before implementing, creating branches or
tickets, or editing files beyond the plan. Return the plan in the reply unless
the user or project names a location for it.

If implementation shows the plan is wrong, say what changed and why before
continuing, and update the plan. If a decision sets lasting direction or is
costly to reverse, suggest a decision record when the project keeps them,
following its conventions; the plan itself is not that record.

## Sources

- [Design Docs at Google][google]: goals and non-goals, overview before
  details, alternatives considered, and when a design doc is not worth writing.
- [Oxide RFD 1][rfd1] and [Amazon's 2017 shareholder letter][amazon]: timely
  rather than polished ideas versus memos rewritten over a week or more.
- [Performing a Project Premortem][premortem]: imagine the failure, then list
  plausible causes.
- [Spec Kit clarify][clarify] and [Matt Pocock's grilling skill][grilling]
  (both MIT): recommended answers to targeted questions and questioning in
  rounds. The wording here is original.
- [Doc co-authoring][coauthoring]: testing a document with a reader that lacks
  the author's context. No text is reused.

[google]: https://www.industrialempathy.com/posts/design-docs-at-google/
[rfd1]: https://rfd.shared.oxide.computer/rfd/0001
[amazon]: https://www.aboutamazon.com/news/company-news/2017-letter-to-shareholders
[premortem]: https://hbr.org/2007/09/performing-a-project-premortem
[clarify]: https://github.com/github/spec-kit/blob/main/templates/commands/clarify.md
[grilling]: https://github.com/mattpocock/skills/blob/main/skills/productivity/grilling/SKILL.md
[coauthoring]: https://github.com/anthropics/skills/blob/main/skills/doc-coauthoring/SKILL.md
