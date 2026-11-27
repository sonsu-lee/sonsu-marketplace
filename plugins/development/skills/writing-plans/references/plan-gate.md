# Plan gate

Apply this gate after the self-review and before a plan is handed to
execution. A plan-only request still ends with the plan; report the verdict
with it.

## Inputs

Give the evaluator the approved requirements (spec, PRD, or design), the
agreed exclusions and delegated choices, and the whole plan version being
judged. Who evaluates, and what a missing evaluator means, is in the
`working-on-tasks` skill's `references/quality-gates.md`.

**Question:** if every task is done and every proposed check passes, can the
result still break an approved requirement? If so, name the input or
situation and the wrong result.

The person who approves the approach reads a plan. It shows what changes, why
that way, and what observation proves it. Details the implementer can settle,
and rules a linter enforces, stay out of it; their absence is never a
finding.

## Checks

1. **Requirements to tasks.** An agreed behavior no task delivers, or a task
   that builds an explicit non-goal.
2. **Contracts between tasks.** A value or state one task produces that the
   next task reads differently, or a task that starts before its input
   exists.
3. **Checks that discriminate.** A proposed check that a realistic wrong
   result also passes, or an expected value copied from the implementation
   instead of the requirement.
4. **Test specification.** Each new or changed test is stated so the user can
   approve it: in this situation, this action gives this result. When `tdd`
   is installed, the `tdd:test-driven-development` skill's
   `references/test-selection.md` decides which cases and levels are worth a
   test.
5. **Decisions on the surface.** A choice that changes product behavior,
   scope, or a material risk is visible in the approval section, not buried
   in a step. A constraint found while planning that changes what users get,
   such as a search delay after archiving, is such a choice. A decision
   listed under "Needs your decision" with what each answer changes can
   `pass`: the user's answer becomes part of the approval.

## Verdict

- `pass`: hand the plan on. This is not approval: wait for the user's
  approval of the test specification, and for implementation authority, when
  either is outstanding.
- `revise_plan`: the PRD or design has the answer. Fix tasks, order, or
  checks without asking the user.
- `reopen_spec`: fixing the plan needs a product or design decision. Return
  to that decision; hand no part of the plan to execution meanwhile.
- `unverified`: a required fresh evaluator could not run. A fork or a spawn
  that copies this history does not count. Do not substitute your own
  evaluation; hand nothing to execution until the user explicitly waives the
  gate.

Block only with the commitment broken, the reachable path, why existing
guarantees or checks miss it, and the effect a user or caller would see. Do
not report a case that is reachable only in imagination or already stopped
at an entry boundary. When the path is real but the right result is not
agreed and not already listed for decision, the verdict is `reopen_spec`,
not a guessed test. Name the result to
guarantee, never "add a guard" or "add a test".

## Paired examples

Requirement: "an archived note leaves the default list and stays searchable."

- The plan only checks that the list is empty after archiving one note. A
  version that deletes the note also passes: `revise_plan`.
- The plan checks that an archived note leaves the list, and reuses an
  existing integration test that finds the same id in search: `pass`.
- The API rejects an invalid status and every internal path receives the
  validated type. A reviewer proposes a forced `null`: `pass`, with no guard
  and no test. If a batch job is shown to bypass that validation, judge again
  at that boundary.
- Cancellation closes at 18:00 and nothing says whether a request at 18:00
  sharp is allowed: `reopen_spec`.
