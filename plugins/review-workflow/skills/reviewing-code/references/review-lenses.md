# Review lenses

Read this when choosing a focused question or analyzing changed behavior.
These are complementary lenses, not four mandatory jobs or a checklist to
repeat in every worker. Start from the change's purpose and follow relevant
callers beyond the diff from input or producer through transformations and
state changes to consumers and side effects. Tests show intended behavior,
not proof of execution.

- **Flow:** does the affected end-to-end path fulfill the requirement while
  preserving data and behavior consumers still need? Trace producer/consumer
  contracts, compatibility, persistence, authorization, and external data
  where the changed path reaches them. Check identifiers and timestamps against
  actual consumers and their semantic purpose when relevant; distinguish
  standards requirements from project choices. Name the entry point and
  observable outcome the focused worker must connect.
- **Failure and state:** can a reachable error, boundary input, ordering, race,
  cancellation, or retry violate an invariant? Inspect error propagation,
  resource ownership, cleanup, partial state, and locks, including implicit
  uniqueness waits where relevant. Trace actual callers and transaction
  lifetimes; distinguish real execution paths from hypothetical combinations
  with no caller.
- **Architecture and current cost:** do responsibilities belong at this layer
  and reuse current abstractions? Establish concrete coupling, duplicated
  policy, or present change cost. Challenge speculative code the change adds:
  unrequested options, single-use abstractions, wrappers, and fallback paths
  or guards that no caller or input reaches. Show unreachability from callers
  and inputs, not the diff alone, and propose deletion or inlining, not a
  migration for taste or imagined scale. Trust-boundary validation, data-loss
  protection, security checks, and accessibility affordances are not
  removable simplifications, and neither are tests that prove the change
  under review.
- **Implementation:** inspect data structures, allocation/copy/computation cost,
  APIs, types, guards, comments, and test assertions. Verify supported API
  versions, returns, lifecycle, and errors before proposing replacements. Types
  do not validate external data. Validate once at a real boundary only if the
  invariant survives every entry path and mutation; retain guards for mutable
  state or bypassing callers. Comments explain intent or constraints, not
  syntax; numbered phases help when the purpose or order is not obvious.
  Compare changed public behavior with docs. Request tests at the smallest
  useful level for the happy path and important reachable boundaries or races,
  naming the plausible bug each would catch. For concurrent tests, check
  deterministic coordination, resource isolation, timeout budgets, and cleanup
  on failure. Coverage percentage is not a criterion. Tests that restate
  wiring, echo mocks, or assert implementation details a behavior-preserving
  refactor would change are weak. Report them only when they give false
  confidence about changed behavior or add real maintenance cost, and ask for
  a stronger assertion rather than deleting a test that proves the change.

The common skill owns finding thresholds, worker boundaries, verification,
and reporting. These lenses do not authorize runtime execution by reviewers.

## Sources

- [Google review criteria][criteria]: design, functionality, complexity, tests,
  comments, and surrounding context.
- [Google review standard][standard]: improve code health without demanding
  perfection or substituting personal preference for evidence.
- [Compound Engineering `ce-simplify-code`][simplify] and its
  [test-value reviewer][test-value] (MIT): the safeguards for safety checks
  and proof tests, and the test-value questions, adapted rather than copied.
- [Test Behavior, Not Implementation][behavior] (Google Testing Blog, 2013):
  tests should exercise public behavior and survive implementation changes.
- [Code Coverage Best Practices][coverage] (Google Testing Blog, 2020):
  coverage is a lossy metric; judge what is untested and test quality.

[criteria]: https://google.github.io/eng-practices/review/reviewer/looking-for.html
[standard]: https://google.github.io/eng-practices/review/reviewer/standard.html
[simplify]: https://github.com/EveryInc/compound-engineering-plugin/blob/786ac0194183fadc3d0e2525b2ba6d40353926d3/skills/ce-simplify-code/SKILL.md
[test-value]: https://github.com/EveryInc/compound-engineering-plugin/blob/786ac0194183fadc3d0e2525b2ba6d40353926d3/skills/ce-simplify-code/references/personas/test-value-reviewer.md
[behavior]: https://testing.googleblog.com/2013/08/testing-on-toilet-test-behavior-not.html
[coverage]: https://testing.googleblog.com/2020/08/code-coverage-best-practices.html
