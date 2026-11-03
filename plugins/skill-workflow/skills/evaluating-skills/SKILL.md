---
name: evaluating-skills
description: >-
  Use this skill to evaluate an agent skill in omp or Codex: run its test
  prompts with and without the skill or against its previous version, grade
  assertions with evidence, benchmark pass rate, time, and tokens, review the
  outputs with the user, and measure or tune how reliably its description
  triggers on should-trigger and near-miss queries. Use it when someone asks
  whether a skill helps, wants evals or a benchmark for a skill, or reports a
  skill activating too often or too rarely. Not for writing or reviewing a
  skill's text, or for evaluating code, models, or prompts that are not agent
  skills. For Claude Code results, use Anthropic's skill-creator plugin.
license: Apache-2.0
compatibility: Requires Python 3.11+, git, and the omp or Codex CLI.
---

# Evaluating skills

Run the two [Agent Skills evaluation loops][evaluating] in omp or Codex:
output quality first, then [description triggering][descriptions] when
activation is in question. For Claude Code, use Anthropic's `skill-creator`
plugin (`/plugin install skill-creator@claude-plugins-official`).

Call the scripts in `scripts/` and `eval-viewer/` by absolute path under this
skill's directory (in omp, `realpath skill://evaluating-skills`). File formats
and workspace layout: [references/formats.md](references/formats.md). Client
setup: [references/clients.md](references/clients.md).

## Before running

- **Client, model, effort:** the ones the user or project names, otherwise
  your own if you run in omp or Codex. Results hold only for that combination.
- **Home:** pass `--home`, a dedicated client home with a test login and
  without the evaluated skill installed. Never the user's own home.
- **Launch:** model runs take many minutes and need network access and writes
  under `~/.cache` and the temp directory. Run them as background jobs outside
  your client's sandbox.
- **Cost:** each eval runs once per configuration and repetition. Agree on
  the scope before a large run.

## Evaluate output quality

1. **Cases.** Two or three realistic prompts with an `expected_output` in
   `evals/evals.json`, input files under `evals/files/`, including one
   boundary case. Keep earlier cases; add cases for revised behavior or gaps.
   Show them to the user.
2. **Baseline.** New skill: `--baseline without`. Revision: put the previous
   version in `<workspace>/skill-snapshot` and use `--baseline old`.
3. **Run.** `scripts/run_evals.py --skill-path <skill> --client <omp|codex>
   --model <model> --effort <effort> --home <home> --iteration <N>
   --baseline <without|old>`. Add `--runs 3` before claiming a delta.
4. **Assertions.** While runs execute, write objectively checkable assertions
   in `evals.json`. The grader sees only the transcript and saved files.
5. **Grade.** `scripts/grade.py <iteration-dir>` grades with
   [agents/grader.md](agents/grader.md). Rerun after changing assertions.
6. **Benchmark.** `scripts/aggregate_benchmark.py <iteration-dir>
   --skill-name <name>` writes `benchmark.json` and `benchmark.md`. Apply
   [agents/analyzer.md](agents/analyzer.md) and add notes to `notes`.
7. **Review.** Start `eval-viewer/generate_review.py <iteration-dir>
   --skill-name <name> --benchmark <iteration-dir>/benchmark.json` in the
   background and ask the user to review each output. Feedback is saved to
   `<iteration-dir>/feedback.json`.
8. **Improve.** Revise from failed assertions, feedback, and transcripts,
   generalizing rather than patching single prompts. Repeat from step 3.

## Tune the description

1. **Queries.** About 20 realistic queries in `evals/eval_queries.json`: half
   should trigger, half near-misses sharing its vocabulary. Review them with
   the user.
2. **Compare.** Run `scripts/run_trigger_eval.py --skill-path <skill>
   --client <client> --model <model> --effort <effort> --home <home>` as is
   and with `--description "<previous>"`. Adopt the edit only if it passes no
   fewer queries.
3. **Search.** `scripts/run_loop.py` with the same arguments proposes
   descriptions, holds out 40% of queries, and reports `best_description`.
4. **Other clients.** Repeat step 2 in each client the project or user
   requires.

## Report

Client, model, effort, and iteration; pass rates with skill and baseline and
their delta; time and tokens; trigger pass counts; and runs not measured or
graded.

## Gotchas

- Each evaluation needs a new `--iteration`; existing ones are refused.
- Exit status 2 means some runs were not measured; rerun with `--resume`.
- Eval IDs are persistent keys. Never reassign an ID to a different case, and
  use a fresh workspace when IDs changed meaning.
- Rebuild `skill-snapshot` from the intended baseline revision before each
  comparison.
- A few runs show a direction, not a reliable rate. With one run, a standard
  deviation of 0 means variance was not measured.

[evaluating]: https://agentskills.io/skill-creation/evaluating-skills
[descriptions]: https://agentskills.io/skill-creation/optimizing-descriptions
