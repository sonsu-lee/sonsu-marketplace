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

## Research-grounded refinement

The 2026-10-29 refinement keeps prompts, criteria, model, and effort fixed.
A candidate must pass six fresh `reporting-pressure` runs in succession without
changing the skill. Keep all failed trials in the record, not just the final
streak. Run the other PR cases and separate transfer cases to check that
concision does not remove required reproduction details or material risks.
These small samples are an acceptance check, not a reliable success rate.

The change teaches evidence selection before drafting, rather than repeatedly
adding prohibitions. Three examples distinguish routine success, a failure
requiring reproduction details, and success with an unrun environment. They use
parser/upload data, not the invoice/customer fixtures or their expected answers.
The template distinguishes a review summary from the work log and preserves
explicit requirements and coverage limits.

Basis and limits:

- [Agent Skills best practices][skill-practices] recommend actionable
  procedures, clear defaults, examples that resolve ambiguity, and refinement
  from actual execution traces.
- [Anthropic prompting guidance][prompt-practices] recommends specifying the
  output structure, explaining the purpose, and using relevant, varied
  examples. These are authoring recommendations, not proof for this PR skill.
- [Opus prompting guidance][opus-guidance] recommends positive communication
  examples and explicit written-deliverable scope. Opus 5.5's guide treats
  this as a starting point; effectiveness still needs local measurement.
- [Self-Refine][self-refine] studies iterative feedback and refinement across
  seven tasks on older models. It supports investigating iteration, not a
  claim that this wording or an additional self-check will reliably fix PRs.
  The skill does not add a generic self-verification loop.

### Observed iterations

All rows use the unchanged reporting criteria and the `default` profile.
Counts include every completed reporting trial in this refinement.

| Skill revision | Change | Passed / attempted |
| --- | --- | --- |
| `58758a5` | Select evidence and group outcomes | 0 / 3 |
| `701d2a3` | Add contrasting success/failure examples | 6 / 6 |
| `7299df1` | Add execution-gap retention to the success example | 0 / 3 |
| `433a987` | Narrow the retained evidence categories | 2 / 3 |
| `31f01cf` | Put outcome placeholders in the copyable body | 0 / 3 |
| `21ea9d4` | Three distinct outcome examples | 8 / 9 |

The final revision's first batch passed 2/3, followed by six consecutive passes.
Earlier `701d2a3` passed the reporting case but omitted the unrun production
status in a transfer case; it was not accepted as the final revision.

`aggregate-success-transfer` and `required-failure-details-transfer` are
synthetic boundary cases defined before the first refinement result. They
are not additional historical user corrections. Their prompts and criteria
were held fixed; after observing the production-status omission they became
regression cases, not an untouched holdout. Final `21ea9d4` passed each 3/3.
One concurrent transfer attempt failed during test-home preflight before any
case ran; it was excluded and rerun sequentially. Use one runner at a time
per client home.

Other final-revision PR cases passed 31/33: one `stack-closing` answer missed
the default-branch condition for checking issue closure, and one `data-flow`
answer omitted the reason for removing asset links. The former also failed
once in three baseline trials; the latter passed the three baseline trials.
Neither criterion was changed or its failure suppressed. The whole quality
suite therefore remains nonzero; the six-run acceptance applies specifically
to `reporting-pressure`, not every PR behavior.

Installed-client activation/safety checks are separate evidence. Manual
inspection still found fixture or cleanup narration in Claude Code drafts,
despite successful skill and template reads. The path-based omp result is
not a claim of reliable concision in every client or session context.

[skill-practices]: https://agentskills.io/skill-creation/best-practices
[prompt-practices]: https://platform.claude.com/docs/en/build-with-claude/prompt-engineering/claude-prompting-best-practices
[opus-guidance]: https://platform.claude.com/docs/en/build-with-claude/prompt-engineering/prompting-claude-opus-5
[self-refine]: https://arxiv.org/abs/2303.17651
