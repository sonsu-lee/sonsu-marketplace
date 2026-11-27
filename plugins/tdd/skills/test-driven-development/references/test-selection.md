# Test selection

Read this when proposing the test contract, before choosing what to test and
at which level.

Choose tests from scenarios, not from branches. A candidate is worth a test
when you can say: in this situation, when this caller does this, this result
must follow, because of this requirement or contract. The domain decides why
a case is tested; the implementation decides where.

## What the user approves

Show the scenario and its result: "A request at 18:00 sharp is rejected when
cancellation closes at 18:00." Do not ask the user to approve file names,
frameworks, mocks, or a test count. When the PRD already states the case,
cite it instead of restating it.

## Levels

- **Unit:** a module's contract: the inputs and states its callers can pass,
  and the result, error, or invariant they rely on. Cover each condition and
  boundary where the result changes, and one representative per rule
  otherwise. The module's role and contract are enough; the whole user story
  is not required.
- **Integration:** failures that appear only when parts are connected: a
  parser, store, or API that reads a value's meaning differently, and how our
  code handles an error the dependency can really return.
- **End to end:** the happy path of a core user journey. Add a failure case
  only when it needs the real app, permissions, or session and the impact is
  high.

The same story at two levels is not duplication when each level catches a
different failure. Do not repeat a unit-level rule through a database or UI.

## Cases to leave out

- A value the entry boundary and every caller exclude. Test the boundary's
  rejection once; inside, test only valid states. If a branch exists only for
  such a value, propose deleting it instead of testing it.
- A situation that holds but has no agreed result. Ask for the decision when
  it changes a product result; do not fix the current output as the answer.
- An input that follows the same rule as one already covered.

An unsupported value from an old client is a valid API case even when it is
not a valid domain state.

## Mutation testing

Use it as a probe, only where the project already has the tool, on changed
code where one operator changes the result: money, permissions, time
boundaries, state transitions. A surviving mutant is a lead:

- an approved, reachable case changes its result and the tests pass: a real
  gap, so add that one case;
- valid inputs give the same result: add nothing, and simplify the code if a
  condition is redundant;
- no agreed answer says which result is right: a missing decision, not a
  missing test.

Never use a mutation score or a coverage number as a pass threshold.
