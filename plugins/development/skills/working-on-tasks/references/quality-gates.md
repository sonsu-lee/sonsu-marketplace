# Quality gates

Read this at a handoff between development stages, or when a gate fails. A
gate decides whether one stage's result may become the next stage's input.
It is not the stage owner's self-assessment, and it never grants authority.

## Gates

- **Request to first action.** The applicable skill is loaded before the
  first exploration, question, or change. Judged from the host's trace. A
  progress note printed earlier is recorded, not failed.
- **Design to PRD or plan.** The decision-maker approved the design they were
  shown. Judged by their reply, never by a model.
- **PRD to plan.** The plan readiness gate of `prd:writing-prd` passes for
  the whole PRD.
- **Diagnosis to fix.** The cause is confirmed by reproduction or recorded
  evidence before a fix, as `debugging-code` requires.
- **Plan to execution.** The `writing-plans` skill's
  [plan gate](../../writing-plans/references/plan-gate.md)
  (`references/plan-gate.md`) passes, the user approved the test
  specification, and implementation is authorized.
- **Implementation to completion.** The `executing-work` skill's
  [completion gate](../../executing-work/references/completion-gate.md)
  (`references/completion-gate.md`) passes on the revision being delivered.

## Verdicts

- `pass`: hand the evaluated version on.
- A revise verdict (`revise_prd`, `revise_plan`, `revise`): approved material
  already has the answer. The stage owner fixes its result and the gate runs
  again. The decision-maker is not asked.
- A decision verdict (`needs_decision`, `reopen_spec`): approved material
  does not settle it. Return to the stage that owns the decision and ask only
  that.
- `unverified`: the evaluator, the evidence, or the environment was
  unavailable. It is not a pass.

Approval is a separate state. A passing plan the user has not approved is
waiting for approval, not failed.

## Blocking needs evidence

A gate blocks only for a finding that names the broken commitment, the
reachable situation, why existing guarantees or checks do not cover it, and
what the user or caller would observe. A missing guard, test, section, or
detail is not a finding by itself. Judge each finding against the whole
request: a later stage or an existing check may already cover it, and results
that each look right may still not connect. For unneeded code or tests, use
the completion gate's rule instead: show that the guarantee holds without
them on every real path and what keeping them costs now.

## Who evaluates

- A PRD that feeds a plan, and a plan with two or more tasks:
  a fresh worker that has not seen the drafting conversation evaluates once,
  from the gate's inputs only. A fork or a spawn that copies this history is
  not independent. Use the host's native worker as the `executing-work`
  skill's `references/clients.md` describes. If none can run, the verdict is
  `unverified`.
- A one-task plan: its author applies the same criteria.
- Implementation: the existing independent review evaluates. Do not add a
  second pass.

## When a gate fails

Return to the stage that made the defect, not to the start:

- wording or an omission against settled answers: the stage that wrote it;
- a missing or changed product decision: the decision-maker, asked only
  that decision (with `grill:grilling` when installed);
- a plan defect: planning;
- a code defect: implementation, or debugging when the cause is unknown.

Results that depended on the returned decision (tests, review, verification)
are invalid until redone. Unrelated work stands. Keep the working files:
never reset, restore, or delete files to roll back, and never repeat an
unchanged evaluation to get a pass. After three failed corrections of the
same gate, stop and report the findings and evidence.

## Unverified results

`unverified` blocks the claim that the stage passed and stops every handoff
that depends on it; continue only work that does not. Say what could not run
and why. Go past the gate only when the user explicitly waives the check, and
report the item as unverified from then on, including in a completion report
or pull request.
