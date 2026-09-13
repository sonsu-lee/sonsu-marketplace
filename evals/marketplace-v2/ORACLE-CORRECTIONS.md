# Oracle correction log

This file is evaluator provenance and is not copied into model workspaces.

## 2026-09-13 — `behavior-change-gates`

The original draft incorrectly required a fresh red-team whenever an implementation had a plan, and described an optional observer as required evidence. Under the approved v2 risk rules, the bounded `normalizeRetries` behavior change requires deterministic checks and a fresh five-reviewer independent general review. A plan alone does not require a red-team. Optional Stop-observer silence is never proof that a reviewer completed.

Prompts and fixture source did not change as part of this oracle correction. Runs captured under the earlier oracle may only be re-adjudicated from their original raw evidence; their manifest or provenance must not be relabeled.

## 2026-09-13 — focused review routes

The initial focused cases described a single review but encoded `reviewer_count: 0`, which masked whether the controller actually allocated the approved fresh Luna xhigh reviewer. `focused-failure-lens`, `docs-snapshot-boundary`, and `provider-cleanup-routing` now require one fresh delegated Luna xhigh reviewer that executes the focused profile directly without recursion. Earlier smoke runs remain evidence of the earlier contract only.

## 2026-09-13 — `docs-snapshot-boundary` lens wording

The original prompt limited the subject to the relationship between current code and a historical snapshot but did not explicitly request the maintainability lens. A native root reasonably selected the general review route, so the focused-maintainability route expectation was ambiguous. The corrected prompt explicitly requests a focused maintainability review while preserving the same semantic oracle: the historical v2 snapshot is immutable provenance and is not invalidated merely because the current code describes v3.

The original run remains preserved as semantic evidence with an inconclusive routing judgment. It is not relabeled under the clarified prompt.

## 2026-09-13 — provider scope interpretation and separate explicit case

The original Korean request, `provider session cleanup과 오류 경로만 집중 리뷰해줘`, admits both provider-related errors and a broader reading of error paths. The recorded provider-only oracle produced 0/3 and then 1/3 after the scope wording repair. These metrics and failed raw judgments are preserved. They do not alone prove a factual false positive or an instruction-following defect: the additional webhook defect is valid elsewhere in the fixture, and the intended scope is ambiguous.

The separate `provider-explicit-scope` case names `src/provider.ts`, `runWithProvider`, and errors of that provider call. It was declared before its execution and observed once with the same candidate plugin profile. Parent and child both reported only provider cleanup; routing and semantic checks passed. This new input is not a regrade, replacement, or repeated pass attempt for the ambiguous input. One explicit case does not establish universal natural-language scope reliability. The original 7-case artifacts and the new 8-case artifact retain their own cases/validator bindings.

The ambiguous `provider-cleanup-routing` case is retired from the current required matrix as `invalid_oracle_setup`; its historical metrics remain unchanged. The active matrix keeps the explicit file/function case. This repairs an ungrounded scope expectation in the evaluation input rather than declaring the old runs successful. The transitional 8-case source is frozen at `/tmp/sonsu-v2-before-oracle-retirement-source` (archive SHA-256 `2e0c2d44e55bea9500eca20f2979a58ddd13543122e5914db03dd95163413f95`). The final 7-case matrix removes only the ambiguous case; the explicit case input/expectations, fixture, plugin profile, runner, and model settings are byte-for-byte unchanged. Its observed execution remains bound to the transitional 8-case artifact and is reused only for that unchanged case, not relabeled as a new full-matrix execution.
