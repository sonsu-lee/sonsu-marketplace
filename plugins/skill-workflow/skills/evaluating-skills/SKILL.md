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

Run the [Agent Skills evaluation loops][evaluating] against omp and Codex:
output quality against a baseline, then [description triggering][descriptions]
when activation is in question. The scripts drive those clients from any shell.
Claude Code results come from Anthropic's `skill-creator` plugin running in
Claude Code (`/plugin install skill-creator@claude-plugins-official`).

Scripts live in this skill's `scripts/` and `eval-viewer/` directories. Run
them with `python3` and absolute paths under the directory this file was
loaded from (in omp, `realpath skill://evaluating-skills`). Read
[references/formats.md](references/formats.md) before writing eval files and
[references/clients.md](references/clients.md) before the first run against a
client.

## Prepare

- **Client and model:** evaluate each omp or Codex client the skill targets.
  When none is named, use the client you are running in if it is one of
  them, with your session's model and effort, unless the project names
  others. Results hold only for that client, model, and effort.
- **Client home:** every script that calls a model needs `--home`, a dedicated
  client home with a test login where the evaluated skill is not installed;
  the scripts refuse a home where it is installed. Never pass the user's live
  home; if the project names none, create one as `references/clients.md`
  describes.
- **Cost:** every eval runs once per configuration and repetition. Confirm the
  scope with the user before large runs.
- **Workspace:** results default to
  `${XDG_CACHE_HOME:-~/.cache}/skill-evals/<skill>-workspace`, outside any
  package that clients install. It persists per skill name across sessions,
  so start each new evaluation in an unused iteration number. Do not commit
  workspaces.

## Evaluate output quality

1. **Test cases.** Keep two or three realistic prompts with an
   `expected_output` in the skill's `evals/evals.json` and input files under
   `evals/files/`. Vary the phrasing and include one boundary case. Keep each
   eval self-contained: no paths outside its inputs, network services, or
   credentials. Show the cases to the user before running.
2. **Baseline.** A new skill is compared with no skill (`--baseline without`).
   For a revision, replace `<workspace>/skill-snapshot` with the previous
   version, not a copy into an existing snapshot, and use `--baseline old`.
3. **Run.** `scripts/run_evals.py --skill-path <skill> --client <omp|codex>
   --model <model> --effort <effort> --home <home> --iteration <N>
   --baseline <without|old>` runs every eval with the skill and with the
   baseline, three times each by default, in fresh sessions and temporary
   directories. Rerun the same command to retry failed runs; exit status 2
   means some runs were not measured. It refuses an existing iteration whose
   skill, plugin, snapshot, prompts, or settings differ. Model-calling scripts
   run for many minutes and need network access and writes to the workspace,
   home, and temporary directories: start them as background jobs, outside
   any host sandbox (in Codex, with approved escalation), and never move the
   workspace or home into the project to get around one.
4. **Assertions.** While runs execute, draft objectively verifiable
   assertions, explain them to the user, and add them to `evals.json`. Do not
   assert exact wording; leave subjective quality to human review. The grader
   sees only the transcript, the final message, and files the run saved or
   changed (text up to 20,000 bytes each, binaries by name and size).
5. **Grade.** `scripts/grade.py <iteration-dir>` grades measured runs using
   [agents/grader.md](agents/grader.md), regrading any graded against other
   assertions; `--force` regrades all.
6. **Benchmark.** `scripts/aggregate_benchmark.py <iteration-dir> --skill-name
   <name> --skill-path <skill>` writes `benchmark.json` and `benchmark.md`.
   Then apply [agents/analyzer.md](agents/analyzer.md) to that benchmark and
   add your notes to the `notes` array in `benchmark.json`.
7. **Review.** Start `eval-viewer/generate_review.py <iteration-dir>
   --skill-name <name> --benchmark <iteration-dir>/benchmark.json` in the
   background, adding `--previous-workspace <previous-iteration-dir>` after the
   first iteration, or write `--static <file>.html` without a browser. Ask the
   user to review the outputs and submit feedback, then read
   `<iteration-dir>/feedback.json`; empty feedback means the output was fine.
   A static page downloads `feedback.json` instead; copy it into the
   iteration directory first, and treat a missing file as no review yet.
8. **Improve.** Use failed assertions, feedback, and transcripts together.
   Generalize instead of patching single prompts, remove instructions that
   cause wasted work, explain why requirements matter, and bundle helpers that
   every run reinvents. Rerun into the next iteration with the same baseline
   until the user is satisfied or results stop improving.

## Tune the description

Do this only when activation is the question.

1. Keep about 20 realistic queries in `evals/eval_queries.json`: 8 to 10 that
   should trigger, including some that never name the skill's domain, and 8
   to 10 near-misses that share vocabulary but need something else. Review
   them with the user; `assets/eval_review.html` offers an editable view.
2. To check an edited description, run `scripts/run_trigger_eval.py` on the
   full query set in each client, once as is and once with `--description
   "<previous description>"`, and compare the passed counts.
3. To search for a better description, run `scripts/run_loop.py --skill-path
   <skill> --clients <client>[,<client>]` with each listed client's
   `--<client>-model`, `--<client>-effort`, and `--<client>-home`. It measures
   each query three times, holds out 40% of the queries, revises the
   description from training failures only, and selects the candidate with
   the best held-out result in its weakest client.
4. Show the user `best_description` with before and after scores, keep it
   under 1,024 characters, and check it on 5 to 10 fresh queries with
   `scripts/run_trigger_eval.py --description`. If other clients also load
   the skill, check them before adopting the change.

## Report

Report the client, model and effort, iteration, pass rates and delta, time and
token costs, trigger pass counts, unmeasured runs, and checks not performed. A
few runs show a direction, not a reliable rate.

[evaluating]: https://agentskills.io/skill-creation/evaluating-skills
[descriptions]: https://agentskills.io/skill-creation/optimizing-descriptions
