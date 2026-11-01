---
name: planning-work
description: >-
  Use to plan or design non-trivial work before implementation, including
  features, refactors, multi-PR changes, and product/UI work from features
  to screens, wireframes, and component usage. Produces a design plan and
  waits for approval. Not for small, clear changes or writing tickets,
  ADRs, or pull requests.
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

Separate the requested deliverable or proposed means from the intended outcome.
Use the outcome to assess whether the requested approach can work, not as
permission to replace the deliverable or expand scope. Preserve explicit
constraints; propose a material change as an alternative for approval.

Sort each fact the plan depends on as confirmed (name the source), inferred
(name the basis), or unknown. Ask only about unknowns and inferences that would
change the plan. Give each question a recommended answer and a one-line reason,
and word it so "yes" accepts the recommendation. Ask the questions that do not
depend on each other together, then ask what their answers unblock. Do not
interrogate on points the plan can state as an assumption and move on.

When a consequential assumption affects the direction, seek the most direct
available evidence, such as raw records rather than a summary, and identify
what observation would disprove it. If that evidence is unavailable, say so
and keep the assumption open rather than treating an inference as a fact.

Research only what could change the approach, scope, risk, or verification.
For an authorized, bounded experiment, state what it decides, its success
criterion, and its cost.

## Shape the plan

- **Goals and non-goals.** A non-goal is something that could plausibly be a
  goal and is deliberately excluded, not a negated goal such as "must not
  crash".
- **Big picture first.** Draw the overall structure before details: components
  and data flow for code; for product or UI work, features to screens to
  wireframes to component usage. Use the project's own terms and its design
  system's existing components; a needed new one is a proposal, not a given.
- **Each element.** For every element say what it is, why it is needed, how it
  works, and which alternatives were rejected and why.
- **Traceability.** Each lower-level item names the higher-level requirement
  that needs it. An item with no parent is cut or becomes a question; a
  requirement with no children is a gap. Check both directions before
  presenting.

Where uncertainty warrants it, draw on concrete methods or tools from relevant
fields to investigate the problem, not expert-role vocabulary or role-play.
Choose methods proportionate to the decision and within the agreed scope.

Size the plan to the work: a small change needs a page, not a template.
Follow a required output format instead of adding sections.

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

For consequential claims, identify an external check, such as observed data,
an executable test, or an independent measurement, and what result would
falsify the claim. An independent reader can expose ambiguity but is not proof
that the plan or its assumptions work. If no external check is available,
state the limitation.

## Split delivery

One purpose per pull request. Where pull requests depend on each other, state
the order and what each one leaves working; independent ones need no order.
Do not split a change from the tests and documentation it needs.

## Share early, mark the state

Mark the plan Draft or Decided at the top. Share a short draft first: goals,
non-goals, the big-picture diagram, and open questions. Polish the detailed
sections only after the direction is agreed.

## Reader check

Before presenting the full plan for approval, have a reader without your
context test it. Where subagents are available, start a fresh one with only the
plan and ask it to restate the goal, say what it would build in the first pull
request, and list anything ambiguous, contradictory, or assumed. Otherwise
perform a self-review and disclose that no independent reader was available;
do not present rereading your own work as a fresh-reader test. Fix gaps in the
plan rather than explaining them away in the review brief.

When the plan belongs in the reply, pass its text directly to the reader.
Do not create a scratch plan file merely to arrange that review, especially
when the request forbids writes; the reader check does not grant write permission.

## Approval and records

Present the plan with its state, assumptions still open, and the decision you
need. Return it in the reply; write a plan file only when the user or project
specifies that destination and the request permits writes. Planning and reader
review do not authorize temporary files. Wait for explicit approval before
implementing, creating branches or tickets, or making other file changes.

Build on the latest agreement; separate settled choices from open questions
and do not reopen them without a reason. Keep a substantive plan resumable:
agreed scope, remaining work, verification, and open decisions.

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
- [How to be more ambitious][ambitious]: distinguish outcomes from means,
  examine raw evidence, use concrete methods, and seek outside validation.

[google]: https://www.industrialempathy.com/posts/design-docs-at-google/
[rfd1]: https://rfd.shared.oxide.computer/rfd/0001
[amazon]: https://www.aboutamazon.com/news/company-news/2017-letter-to-shareholders
[premortem]: https://hbr.org/2007/09/performing-a-project-premortem
[clarify]: https://github.com/github/spec-kit/blob/main/templates/commands/clarify.md
[grilling]: https://github.com/mattpocock/skills/blob/main/skills/productivity/grilling/SKILL.md
[coauthoring]: https://github.com/anthropics/skills/blob/main/skills/doc-coauthoring/SKILL.md
[ambitious]: https://felixrieseberg.com/how-to-be-more-ambitious-a-tutorial-for-humans-with-models/
