# TypeScript simplification pilot

## Decision

Keep the candidate as an unpublished evaluation artifact. Do not install it,
register a new marketplace plugin, or claim cross-client support from this pilot.
One observed structural improvement is useful evidence, but the small examples
mostly already work with omp alone. It does not yet justify a general-purpose
simplification package or the larger framework fixture investment.

The next useful evidence would be real TS failures with longer producer/consumer
chains, not more copies of these same exercises. Any extension remains a separate
scope decision. The language and framework expansion is not part of this change.

## Scope and method

- Client: omp 18.13.3, dedicated authenticated test HOME, no live settings copied.
- Profile: `default`, `anthropic/claude-opus-5-5`, high effort. All answer runs
  reported `claude-opus-5-5`, high.
- Six cases, three repetitions, baseline and candidate: 36 fresh contexts.
  Arm order alternated by repetition. The only intended arm difference was
  explicit reading of the [candidate](simplify-code/SKILL.md).
- Models returned complete source files, rather than editing a real repository.
  Immutable TypeScript 5.9.3 and runtime contracts checked each submission.
  This does not establish end-to-end implementation or large-repository behavior.
- Candidate exposure required a successful tool result containing its full body.
  All 18 candidate observations met this requirement.
- Structural comparisons used the existing `compare_skill.judge`, randomized
  A/B labels with seed 20261029, the original code, returned code, contract
  outcomes, and case criteria. Judges had no tools and used the same default
  model profile. Model judgment supplements, not replaces, contract execution
  and source inspection.
- Final mechanical rechecks used evaluator commit `5a180ed`. Saved model outputs
  were rechecked after correcting a syntax-only rejection; no model answer was
  changed or selectively regenerated.

## Results

| Observation | omp baseline | With candidate |
| --- | ---: | ---: |
| Type/runtime contract passes | 18 / 18 | 18 / 18 |
| All structural criteria met | 17 / 18 | 18 / 18 |
| Strict wins in blinded pairs | 0 | 1 |
| Reported total tokens across answer turns | 889985 | 1170502 |

The remaining 17 pairs were ties. The difference was TS04 repetition 2: the
baseline removed the helper but retained an unreachable `typeof name` check;
the candidate removed both unreachable guards. The submitted sources independently
confirm this difference. It is not a naming, formatting, or class/function
preference. The baseline preserves behavior but does not finish that requested
simplification.

Token totals sum the client's reported `usage.totalTokens` over assistant turns,
including cache-accounted context. They are not unique-context size, elapsed
time, or a reliable pricing comparison. This sample does not establish a stable
success rate or a statistically reliable advantage.

Automatic activation was measured separately with a native project skill in
fresh temporary projects, not through a published plugin. Two positive queries
loaded the skill in all six runs; three nearby negative queries did not load it
in all nine runs. All 15 completed on the pinned model/effort without forbidden
writes. Successful positive reads returned the full body. These small samples
are not general activation-rate estimates.

## Evaluator corrections and review

The first transport smoke exposed fenced JSON answers. The parser now accepts
one unambiguous JSON block without allowing extra paths or duplicate keys.
An interrupted intermediate comparison is excluded from this report.

Independent general and focused reviews, followed by source verification and a
targeted correction review, covered candidate-copy overlap, incomplete check
classification, exported Result narrowing, unrestricted generic inputs, both
const-inference syntaxes, and actual candidate exposure. The candidate also
received a separate skill-authoring review with no necessary changes identified.

Actual final outputs exposed an additional evaluator error: all three TS05
baseline answers used `as Record<string, unknown>` to read unknown fields, then
validated those fields at runtime. Rejecting the syntax alone would have awarded
an unjustified advantage to the candidate. The final evaluator records assertion
syntax for semantic review while still rejecting new compiler suppressions.
Source inspection and blinded judging found these three boundary uses preserve
the stated contract. Their type/runtime checks passed before and after the
classification correction. That correction has a dedicated regression test.

Final local checks: six references passed; all fourteen deliberate regressions
were rejected; all twenty-four runner regressions passed after integrating the
current trunk (twenty-two at the recorded evaluator revision). Valid alternative
TypeScript declarations were also exercised, and signal termination was observed
as incomplete rather than a contract rejection. Skill format validation and
Markdown lint passed. No published plugin changed, so catalog/version changes
and cross-client plugin checks are not applicable to this experiment.

## Evidence and reproduction

- [Behavior results](behavior-results.json): all submitted source files, observed
  model/effort, contract results, review flags, usage, and local trace digests.
- [Blind judgments](judgments.json): criteria, A/B mapping, and judge trace digests.
- [Activation queries](activation.json) and [results](activation-results.json).
  The `candidate` namespace is an experiment identifier, not an installed plugin.

Raw traces remain in the dedicated local evaluation directories; they are not
published. Digests identify those traces but do not substitute for public logs.
The public evidence includes the actual returned sources and check results.

From the marketplace root, after installing the pinned toolchain and preparing
the dedicated omp login as described in the root README:

```sh
CANDIDATE=evals/simplify-code/experiments/2026-10-29/simplify-code
python3 scripts/evaluate_simplification.py selfcheck
python3 scripts/evaluate_simplification.py run --reps 3 \
  --candidate "$CANDIDATE/SKILL.md" \
  --output /tmp/simplification-comparison
```

Use a fresh output directory and do not change the candidate or cases during a
run. Generated code executes locally, not in a security sandbox.

For activation, the recorded queries used `check_activation.load_spec`,
`execute`, and `judge`: copy the candidate to
`<temporary-project>/.omp/skills/simplify-code/SKILL.md`, run each query three
times in fresh projects with the same dedicated HOME, and inspect the actual
read results and writes. Do not force the skill read in these activation runs.
No candidate is installed into the live client or registered in a catalog.
