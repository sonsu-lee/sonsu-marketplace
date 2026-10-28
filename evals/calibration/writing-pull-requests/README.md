# PR reporting calibration

Real feedback records distinguish concise reporting from omitted evidence.
The fixtures are evaluation inputs, not instructions loaded by the PR skill.

## Sources

### PR 45: small change, extensive author checks

Source: [PR 45](https://github.com/sonsu-lee/sonsu-marketplace/pull/45)
and its authoring conversation on 2026-10-29 (local date). The original PR
added two sentences to `authoring-skills` and bumped the package version.
The user rejected the description as overly verbose, specifically questioning
Author checks, then approved the shorter replacement.

`pr-reporting.json` preserves the rejected and approved bodies from that
conversation. The public PR body now shows only the approved replacement.
The `reporting-pressure` query in `evals/git-workflow/writing-pull-requests.json`
reconstructs the available change, reporting requirements, and execution notes.
It does not tell the author which notes to discard. Personal filesystem
prefixes are excluded; the retained `~/.cache/` path is a generic local path,
not a shared evidence link.

Expected labels express the user's correction: preserve the change's purpose,
profile, and results, but do not reproduce the execution inventory. They do
not establish a universal ban on model IDs or versions when those details
matter to a different change.

The `synthetic-overcompressed` example is deliberately constructed, not a
historical answer: it drops the required profile and misrepresents tied
comparisons as a quality improvement. A short answer must not pass merely
because it is short. Approved wording is not an exact-match target.

### PR 25: preserve purpose and solution flow

Source: [PR 25](https://github.com/sonsu-lee/sonsu-marketplace/pull/25)
and its discussion with the user on 2026-10-23. An explanation focused on CLI
behavior and additional implementation issues; the user clarified that the
question concerned the PR's purpose. The subsequent explanation connected
variable client defaults to profile selection and actual-model verification,
while preserving normal users' model settings.

The `profile-purpose` query adapts those facts into a drafting task. This was
feedback on a conversation about the PR, not a rejected PR body; the later
answer was not explicitly approved. It is not stored as a labeled approved
output. Existing `data-flow` and `risk-boundary` cases remain complementary:
concise writing must still explain consequential behavior and preserve risks.

## Evaluation

Run these fixtures with the calibration mode documented in the repository's
[testing procedure](../../../README.md#testing-a-plugin). Expected labels
are withheld from the model judge and compared afterward. Calibration failure
means the grader is unsuitable for that case; it is not a skill regression.
Model checks run locally in dedicated authenticated homes, never in CI.
