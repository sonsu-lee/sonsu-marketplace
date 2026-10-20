# Review lenses

Read this when choosing a focused question or analyzing changed behavior.
These are complementary lenses, not four mandatory jobs or a checklist to
repeat in every worker. Start from the change's purpose and follow relevant
callers beyond the diff from input or producer through transformations and
state changes to consumers and side effects. Tests show intended behavior,
not proof of execution.

- **Flow:** does the affected end-to-end path fulfill the requirement? Trace
  producer/consumer contracts, compatibility, persistence, authorization, and
  external data where the changed path reaches them. Name the entry point and
  observable outcome the focused worker must connect.
- **Failure and state:** can a reachable error, boundary input, ordering, race,
  cancellation, or retry violate an invariant? Inspect error propagation,
  resource ownership, cleanup, and partial state. Distinguish real execution
  paths from hypothetical combinations with no caller.
- **Architecture and current cost:** do responsibilities belong at this layer
  and reuse current abstractions? Establish concrete coupling, duplicated
  policy, or present change cost. Challenge unnecessary wrappers and fallback
  paths, but do not demand a migration for taste or imagined scale.
- **Implementation:** inspect data structures, allocation/copy/computation cost,
  APIs, types, guards, comments, and test assertions. Verify supported API
  versions, returns, lifecycle, and errors before proposing replacements. Types
  do not validate external data. Validate once at a real boundary only if the
  invariant survives every entry path and mutation; retain guards for mutable
  state or bypassing callers. Comments explain intent or constraints, not
  syntax. Compare changed public behavior with docs and request tests for
  important uncovered behavior, not a quota.

The common skill owns finding thresholds, worker boundaries, verification,
and reporting. These lenses do not authorize runtime execution by reviewers.

## Sources

- [Google review criteria][criteria]: design, functionality, complexity, tests,
  comments, and surrounding context.
- [Google review standard][standard]: improve code health without demanding
  perfection or substituting personal preference for evidence.

[criteria]: https://google.github.io/eng-practices/review/reviewer/looking-for.html
[standard]: https://google.github.io/eng-practices/review/reviewer/standard.html
