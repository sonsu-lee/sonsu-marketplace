# Plan readiness

Apply this gate before a PRD becomes the input to an implementation plan. A
standalone PRD draft may carry open questions and does not need this gate.

**Question:** can a planner write the implementation plan from this whole PRD
without making a product decision the decision-maker has not made?

A PRD settles who has which problem, what the product guarantees and where
that stops, and what observable result shows a requirement is met. It does
not settle file lists, internal names, storage design, or test code. A
technical constraint belongs in it only when it changes what a user or an
external consumer can rely on.

## Inputs

Give the evaluator the source request and the agreed answers in their own
words, the whole PRD as it would be handed to planning, and each explicit
exclusion, delegation, or deferral with where it was agreed. "Agreed" written
in the PRD is not evidence of agreement. The evaluator is a fresh worker that
has not seen the drafting conversation; a fork or a spawn that copies this
history does not count. When the decision-maker hands over a PRD they
approved without the drafting discussion, that PRD is the agreement: apply
checks 3 and 4 only.

## Checks

1. **Agreement to PRD.** Find an agreed user, problem, outcome, scope limit,
   behavior, important exception, or prohibition that the PRD drops or
   changes. Different wording with the same result is a match.
2. **PRD to agreement.** Find a policy, number, deadline, permission, or
   acceptance condition the PRD states without a source.
3. **Remaining gaps.** For a gap, name one situation in this scope and the two
   results a user or external consumer would see depending on the answer. If
   the difference is only an internal name, storage choice, or task order, it
   is not a gap. Do not invent future cases.
4. **Exceptions.** Do not reopen what was explicitly excluded or delegated. A
   fact nobody can know yet passes only when the PRD states the rule or scope
   that applies without it. Difficulty confirming a fact never passes a core
   product decision.

## Verdict

Return one verdict for the whole PRD. For each finding give the PRD passage,
the source passage, the situation, and the next action. Give no score, no
rewritten PRD, and no product decision.

- `pass`: the product decisions this scope needs are settled and the PRD
  preserves the agreement. Hand this exact version to planning.
- `revise_prd`: the answer exists, but the PRD dropped it, changed it, or
  added an unsourced statement. Fix the PRD and evaluate again. Do not ask
  the decision-maker a question already answered.
- `needs_decision`: the sources do not settle it and the answer changes
  product behavior or acceptance. Ask the decision-maker only that decision,
  with `grill:grilling` when that skill is installed. No part of the PRD goes
  to planning meanwhile.

If the source agreement is unavailable or no fresh evaluator can run, report
`unverified` and the reason instead of a verdict, and plan nothing until the
user explicitly waives the gate. Never substitute your own evaluation.
Findings of both kinds can coexist: fix the `revise_prd` items yourself and
ask only about the `needs_decision` items.

Before any plan, report the verdict and each finding to the user, quoting the
PRD passage and the agreed passage, including `revise_prd` items you fixed.
Then have a fresh evaluator check the revised PRD. Never revise silently.

A PRD that only restates settled answers needs no second approval. Confirm
again when a decision, a scope change, or an explicit deferral was added
after the decision-maker's last answer, or when they asked to approve the
final document.

## Paired examples

The agreement decides the verdict, not the sentence. Agreed: "an archived
note leaves the default list and stays searchable."

- "Excluded from the default list, included in search results.": `pass`. The
  same contract in other words.
- "Archived notes are excluded from every query.": `revise_prd`. Search was
  already decided, so asking again is wrong.
- "Deleted automatically 30 days after archiving.": `revise_prd`. An
  unsourced deletion policy; remove it.
- The PRD names no storage field: `pass`. An internal choice left to the
  implementer.

Agreed only "leaves the default list", and search is in scope and undecided.
A PRD saying "excluded from the default list" is `needs_decision`: keeping
and hiding the note in search both satisfy it. If the agreement instead says
"this change covers the default list only; search behavior stays as it is",
the same PRD is `pass`.
