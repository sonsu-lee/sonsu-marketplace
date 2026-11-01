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

Run the two [Agent Skills evaluation loops][evaluating] against omp and Codex:
output quality first, then [description triggering][descriptions] when
activation is in question. Claude Code results come from Anthropic's
`skill-creator` plugin instead
(`/plugin install skill-creator@claude-plugins-official`).

The scripts are in this skill's `scripts/` and `eval-viewer/` directories.
Call them by absolute path under the directory this file was loaded from (in
omp, `realpath skill://evaluating-skills`). File formats and the workspace
layout are in [references/formats.md](references/formats.md); how each client
runs is in [references/clients.md](references/clients.md).

## Before running

- **Client, model, effort:** use the ones the user or project names;
  otherwise the client, model, and effort you are running with, if that
  client is omp or Codex. Results hold only for that combination.
- **Home:** pass `--home`, a dedicated client home with a test login where the
  evaluated skill is not installed (the scripts refuse one where it is).
  Never pass the user's own home; `references/clients.md` shows how to make
  one.
- **Launch:** scripts that call a model run for many minutes and need network
  access and writes under `~/.cache` and the temporary directory. Start them
  as background jobs outside any sandbox of your own client.
- **Cost:** each eval runs once per configuration and repetition. Agree on
  the scope with the user before a large run.

## Evaluate output quality

1. **Cases.** Start with two or three realistic prompts with an
   `expected_output` in the skill's `evals/evals.json`, with input files under
   `evals/files/`, including one boundary case. Keep earlier cases and add
   cases for a revised behavior or a gap the results reveal. Show the cases to
   the user.
2. **Baseline.** A new skill is compared with no skill
   (`--baseline without`). For a revision, put the previous version in
   `<workspace>/skill-snapshot` and use `--baseline old`.
3. **Run.** `scripts/run_evals.py --skill-path <skill> --client <omp|codex>
   --model <model> --effort <effort> --home <home> --iteration <N>
   --baseline <without|old>` runs every eval with the skill and with the
   baseline, three times each. Use a new `<N>` for each evaluation; exit
   status 2 means some runs were not measured, so rerun with `--resume`.
4. **Assertions.** While the runs execute, write objectively checkable
   assertions into `evals.json` and explain them to the user. The grader sees
   only the transcript and the files the run saved, so assert on those.
5. **Grade.** `scripts/grade.py <iteration-dir>` grades each measured run with
   [agents/grader.md](agents/grader.md). Rerun it after changing assertions.
6. **Benchmark.** `scripts/aggregate_benchmark.py <iteration-dir> --skill-name
   <name>` writes `benchmark.json` and `benchmark.md`. Apply
   [agents/analyzer.md](agents/analyzer.md) to the benchmark and add your
   notes to its `notes` array.
7. **Review.** Start `eval-viewer/generate_review.py <iteration-dir>
   --skill-name <name> --benchmark <iteration-dir>/benchmark.json` in the
   background and ask the user to review each output. Their feedback is saved
   to `<iteration-dir>/feedback.json`.
8. **Improve.** Revise the skill from failed assertions, feedback, and
   transcripts, generalizing rather than patching single prompts. Repeat from
   step 3 with the next iteration until the user is satisfied.

## Tune the description

1. **Queries.** Keep about 20 realistic queries in `evals/eval_queries.json`:
   half that should trigger the skill, half near-misses that share its
   vocabulary but need something else. Review them with the user.
2. **Compare an edit.** Run `scripts/run_trigger_eval.py --skill-path <skill>
   --client <client> --model <model> --effort <effort> --home <home>` once
   as is and once with `--description "<previous description>"`. Adopt the
   edit only if it passes no fewer queries.
3. **Search.** To have the client propose descriptions, run
   `scripts/run_loop.py` with the same arguments. It holds out 40% of the
   queries, revises from the rest, and reports `best_description` by its
   held-out score.
4. **Other clients.** If other clients load the skill, repeat step 2 in each
   before adopting the change.

## Report

Report the client, model, effort, and iteration; pass rates with the skill
and the baseline and their delta; time and tokens; trigger pass counts; and
runs that were not measured or graded. A few runs show a direction, not a
reliable rate.

[evaluating]: https://agentskills.io/skill-creation/evaluating-skills
[descriptions]: https://agentskills.io/skill-creation/optimizing-descriptions
