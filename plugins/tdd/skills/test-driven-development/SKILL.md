---
name: test-driven-development
description: >-
  Use when implementing a feature or bug fix, changing behavior, or refactoring
  under test. Not for a plan-only request or a read-only investigation.
license: MIT
metadata:
  source: https://github.com/obra/superpowers
  source-commit: 22f0b463e7a5e579904dd6211a520321035526f7
---

# Test-Driven Development (TDD)

## Overview

Write the test first. Watch it fail. Write minimal code to pass.

**Core principle:** If you didn't watch the test fail, you don't know if it
tests the right thing.

## When to Use

- New features
- Bug fixes
- Refactoring
- Behavior changes

**Exceptions (ask your human partner):** Throwaway prototypes, generated code,
configuration files. A plan-only request stops at the proposed test contract.
This workflow grants no permission to edit, run a command, or commit.

## Agree on the test contract before writing tests

Inspect the requirement, callers, and existing tests. For each changed behavior,
show the decision-maker:

- The observable interface: who calls it and where the result can be seen.
- A concrete example: given this initial state, when this action occurs, then
  this result or side effect follows. Cite the source of the expectation: a
  requirement, an existing contract, or an independently worked example.
- The realistic failure this check must catch, and the smallest test type that
  can expose it: unit, integration, or a real consumer scenario.
- The existing coverage: name the check to reuse or extend. Propose a new test
  only if no existing check exposes that failure.

For example: “Given a blank email, submitting the form returns `Email required`
under the agreed validation rule. This catches accepting an empty address.
Extend the existing form-submission cases with this input; no browser test is
needed for the returned error.”

Get explicit user approval **before writing or changing a test**. An approved
plan that includes this contract is sufficient; don't ask again for each test.
If the plan omitted the contract, present it and wait. If the interface or
expected behavior changes, confirm only the affected contract before proceeding.
An approved test contract alone is not approval to implement.

## The Iron Law

```text
NO PRODUCTION CODE WITHOUT A FAILING TEST FIRST
```

Write code before the test? Start over with the untested code you just wrote,
if authorized to discard it. Don't keep it as a reference or adapt it while
writing tests. Never discard existing work or revert someone else's changes
to manufacture a red run.

When writing or changing any test, read [Writing Good Tests][good-tests]. Name
the production change that would make it fail. Assert on real behavior, never
on mock behavior. Keep test-only code in test utilities. Understand a
dependency's side effects before mocking it.

## Red-Green-Refactor

Read the [worked cycles][cycles] when choosing a first failing example or
implementing a bug fix; they show each verification point in order.

### RED - Write Failing Test

Write one minimal test showing what should happen. Give it a clear name and
exercise real code (no mocks unless unavoidable). If an existing test already
checks this behavior and exposes the failure, use it as RED. Don't duplicate it.

### Verify RED - Watch It Fail

Run the selected check using the project's test command within the authorized
scope. Confirm:

- Test fails (not errors).
- Failure message is expected.
- Fails because the feature is missing, not because of typos or setup.

**Test passes?** Check the approved contract and coverage. If the behavior is
already implemented and covered, retain that test; don't invent a failure.
If the assertion missed the agreed break, fix it before implementing.

**Test errors?** Fix the setup, then run the check again if allowed. If the
host or user prohibits reproducing a reported failure, don't rerun it. Use
available pre-change failure evidence for that check, identifying its source.
If no valid RED evidence exists, stop before GREEN. If checks belong to another
verifier, hand off the command and expected failure and wait for the result.
Report blocked or unverified, not a successful TDD cycle.

### GREEN - Minimal Code

Write the simplest code to pass the test. Don't add features, refactor other
code, or “improve” beyond the test.

### Verify GREEN - Watch It Pass

Run the same check. Confirm:

- Test passes.
- Other affected tests still pass.
- Output pristine (no errors, warnings).

**Test fails?** Fix code, not the approved expectation. **Other tests fail?**
Report them by name. Address in-scope regressions. Run the project's required
suite when authorized; a green run of one test is not a green suite. Respect
host limits on command scope, access, and which role verifies. Report the
command, observed result and any unrun or blocked checks as such.

### REFACTOR - Clean Up

After green only:

- Remove duplication.
- Improve names.
- Extract helpers.

Keep tests green. Don't add behavior. Re-run the affected checks after cleanup.
For a behavior-preserving refactor with adequate regression tests, establish
the existing green baseline and retain it; there is no new behavior to drive
with a contrived failing test.

### Repeat

Next failing test for the next approved behavior. If tempted to skip RED, read
[Common Rationalizations and Red Flags][red-flags] before proceeding.

## Verification Checklist

Before marking work complete:

- [ ] Each changed behavior has approved coverage; existing tests were reused
      where they already catch the break.
- [ ] Observed each new behavior's test fail before implementing.
- [ ] Each test failed for the expected reason (feature missing, not typo).
- [ ] Wrote minimal code to pass each test.
- [ ] The authorized verifier observed GREEN on the final revision.
- [ ] Tests use real code (mocks only if unavoidable).
- [ ] Reachable edge cases and errors that change the outcome are covered.

Can't check a required box? Say which one and why. A blocked check is not a
pass; neither plan approval nor an implementation report proves RED or GREEN.

## When Stuck

- **Don't know how to test:** Write the wished-for API. Propose the assertion
  first. Ask your human partner.
- **Test too complicated:** Design too complicated. Simplify the interface
  with the contract owner's approval.
- **Must mock everything:** Code too coupled. Consider dependency injection.
- **Test setup huge:** Extract helpers. Still complex? Simplify design.

## Debugging Integration

Bug found and fix authorized? Use the approved reproducing test and follow the
TDD cycle. Test proves fix and prevents regression. A request for diagnosis
does not authorize a fix.

## Final Rule

```text
Production code for new behavior → test exists and failed first
Otherwise → not TDD
```

[good-tests]: writing-good-tests.md
[cycles]: references/worked-cycles.md
[red-flags]: references/rationalizations.md
