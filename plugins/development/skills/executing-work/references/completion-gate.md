# Completion gate

The controller applies this gate after receiving the final independent
review and before reporting work complete. Use that review and the checks
already run; do not add another review pass.

**Question:** on the revision being delivered, is every approved behavior
observed on its real path, and is nothing left that the change does not need?

## Evidence

- Checks and review are for the revision being delivered. A later source or
  test change invalidates the evidence for the paths it touched; redo only
  those.
- Each approved behavior was observed at its consumer boundary, not inferred
  from a build or a test of an internal helper.
- A diagnostic that fails the project's lint check is a failed check. A
  warning the change caused is fixed or kept with a stated reason. Warnings
  that existed before the change are not part of this gate.
- Blocking review findings are resolved, or declined with a reason the
  reviewer's evidence does not contradict.

## Findings about unneeded code

Require a change only when the reviewer shows both that the guarantee holds
without the code on every real path, and what keeping it costs now. This
covers a test that catches no reachable contract violation, a guard that
re-proves a boundary's guarantee, one product rule owned in two places, and
an extension point no caller uses. A style preference, or shorter code with
no stated defect or cost, does not block.

## Verdict

- `pass`: report completion with the evidence.
- `revise`: a code defect or unneeded code. Return to implementation, or to
  debugging when the cause is unknown; redo the invalidated checks and
  re-review the changed part.
- `reopen_spec`: the fix needs a plan, design, or product decision. Return to
  the stage that owns it. Do not patch around it in code.
- `unverified`: a required check or reviewer could not run. Do not report
  completion. State what is unverified and why. If the user explicitly
  waives the check, hand off as "Unverified items", not as complete.

Passing this gate does not authorize a commit, push, pull request, or
deployment.

## Paired examples

- An internal function gained a `None` branch and a test that passes `None`,
  while the only caller rejects a non-list before calling. The test freezes
  an unsupported result: `revise`, remove both.
- Two similar validations protect an API request and a legacy restore job:
  `pass`. They guard different boundaries.
- A save handler logs the error and the success notice still runs: `revise`.
  A handler that shows the failure state and stops: `pass`.
- A complexity warning on `price >= min && price <= max`: `pass`, with the
  reason stated.
- A client scenario could not run because the test home has no model login:
  `unverified`, never `pass`.
