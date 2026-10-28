# Review-controller evaluation

`controller.json` complements, rather than replaces, the focused static cases in
`reviewing-code.json`. It uses the shared `check_activation.py` fixture support:
each trial receives a fresh copy of `evals/fixtures/review-controller/input`;
its final target tree must match `expected`. The diff is supplied explicitly
because the isolated workspace has no historical Git commit. The fixture's
happy-path test does not cover the retry failure. Run only with dedicated test
homes and authorized test logins, following the repository's plugin test
procedure. For omp controller dispatch, for example:

```sh
python3 scripts/check_activation.py --clients omp prepare
python3 scripts/check_activation.py --clients omp run \
  --spec evals/review-workflow/controller.json --reps 3
```

Use the default profile unless the evaluation explicitly records another one.
The normal case is an actual controller task. The runtime-unavailable case
creates a real execution constraint: no test or alternative runtime execution
is authorized. The missing-worker and no-duplicate cases are **simulated
checkpoints**: they exercise continuation and reporting decisions with supplied
worker outcomes, not actual worker failure injection or end-to-end dispatch.
They do not establish that the runtime can generate those events. Test real
worker failures separately when a controllable runtime is available.

For each trial retain the JSONL trace, final answer, and input/final tree
comparison. An activation or tree pass is not a controller pass. Inspect:

- **Normal completion:** worker dispatch and full completion results, target
  identity, candidate verification, actual runtime command and result in a
  disposable copy, and an unchanged target. A spawned worker or a claim in the
  final answer is not completion. Missing tool events or worker results mean
  that coverage is unmeasured, not passed.
- **Runtime unavailable:** no runtime execution occurred and the answer
  explicitly marks runtime unverified. Static evidence is not a runtime pass.
- **Failed worker checkpoint:** the answer treats the supplied failure as
  incomplete coverage while preserving its useful partial candidate. The trace
  must not show invented replacement work or execution, and the report must
  identify the events as simulated.
- **Duplicate checkpoint:** the two supplied candidates become one root-cause
  finding; the trace shows at most targeted candidate verification, not another
  general scan or worker dispatch. The report distinguishes simulated history
  from observed work.

Check the defect against the fixture and judge the answer for scope and honest
limitations. Evaluate trace and final state independently; a fluent answer or
an answer-only model grade cannot prove worker completion, runtime, or absence
of edits. Retain failed, refused, or unavailable runs as such rather than
counting them as passes. Before trusting a grader, calibrate it against a correct
report with supporting trace, an equally persuasive report with no completion
or runtime evidence, a trace showing a full rescan, and a modified target;
these must not all pass. Manually adjudicate ambiguous events and record the
model, client, profile, trials, evidence, and remaining gaps.
