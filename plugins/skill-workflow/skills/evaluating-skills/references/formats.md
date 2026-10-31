# Evaluation file formats

The scripts read the skill's `evals/` directory and write a workspace in the
layout of Anthropic's skill-creator, so its viewer and aggregation work for
every client.

## `evals/evals.json`

```json
{
  "skill_name": "csv-cleanup",
  "evals": [
    {
      "id": 1,
      "prompt": "Clean data.csv: trim spaces and drop duplicate rows.",
      "expected_output": "A cleaned CSV without duplicates or padding.",
      "files": ["evals/files/data.csv"],
      "assertions": [
        "Writes a CSV with no duplicate rows",
        "Keeps every column of the input"
      ]
    }
  ]
}
```

- The top-level keys are exactly `skill_name` and `evals`. `skill_name` equals
  the `name` in the skill's `SKILL.md`.
- `evals` is a non-empty list. Each item has an integer `id` that no other
  item uses, a non-empty `prompt`, and an `expected_output` string. `files`
  and `assertions` are optional; no other key is accepted.
- `assertions` is a list of non-empty strings. Draft them while the first runs
  execute and finalize them after reviewing the outputs; until then,
  `grade.py` skips the eval. The key `expectations` is rejected: use
  `assertions`, the Agent Skills name.

### Input files

- Each `files` entry is a relative path without `..` that exists under
  `evals/files/`. A directory entry ends with `/`.
- A file entry is copied to the run's working directory under its base name.
  A directory entry copies its contents to the top of the working directory.
  Two entries that land on the same path are an error.
- Never name a file `SKILL.md` anywhere under `evals/`, because some clients
  register nested skill files. When an eval needs a skill's text as input,
  put the text inline in the prompt.

## `evals/eval_queries.json`

```json
[
  {"query": "clean up the duplicates in exports/q3.csv", "should_trigger": true},
  {"query": "convert this CSV to a Parquet file", "should_trigger": false}
]
```

- A non-empty array of objects with exactly `query` (non-empty string) and
  `should_trigger` (boolean).
- Keep about 20 queries, 8 to 10 of each kind. A query must not appear twice;
  results are matched to the train and test split by query text.

## Workspace

```text
<workspace>/
  skill-snapshot/
  <client>/iteration-N/
    iteration.json
    eval-<id>/
      eval_metadata.json
      <config>/run-<r>/
        events.jsonl
        transcript.md
        outputs/
        timing.json
        grading.json
    benchmark.json
    benchmark.md
    feedback.json
```

`<config>` is `with_skill` and either `without_skill` or `old_skill`.

- `iteration.json`: `client`, `model`, `effort`, `home`, `skill_path`,
  `skill_name`, `baseline` (`without` or `old`), `runs`, `snapshot`,
  `skill_digest`, `snapshot_digest`, `cases_digest`, and `created`. A rerun
  into the same iteration must match all of them except `skill_name` and
  `created`. The digests cover the skill and the snapshot without `evals/`,
  and the eval prompts and input files without assertions.
- `eval_metadata.json`: `eval_id`, `eval_name`, `prompt`, `expected_output`,
  `files`, and `assertions`. `grade.py` refreshes `assertions` from
  `evals.json`.
- `events.jsonl`: the client's raw JSON events.
- `transcript.md`: sections `## Eval Prompt`, `## Brief`, `## Transcript`,
  `## Final Message`, and `## Run`.
- `outputs/`: files the agent saved to the outputs directory in its brief,
  which is a temporary directory outside the workspace during the run; files
  it created or changed in its working directory, under `working-directory/`;
  and `final_message.md` and `metrics.json` written by the runner.
  `metrics.json` holds `tool_calls`, `total_tool_calls`, `errors_encountered`,
  `files_created`, `output_chars`, and `transcript_chars`.
- `timing.json`: `total_tokens`, `duration_ms`, `total_duration_seconds`,
  `client`, `model_requested`, `model_observed`, `effort_requested`,
  `effort_observed`, and `error`. A run is measured when `error` is null. A
  run on another model or effort records an `off-profile` error.
- `grading.json`: `expectations` (each `text`, `passed`, `evidence`),
  `summary` (`passed`, `failed`, `total`, `pass_rate`), `execution_metrics`,
  optional `claims` and `eval_feedback`, and `grader` (`client`, `model`,
  `effort`). The viewer requires the `expectations` field names exactly.
- `benchmark.json` and `benchmark.md`: written by `aggregate_benchmark.py`.
  `run_summary` has one entry per configuration and a `delta` of with_skill
  minus the baseline.
- `feedback.json`: written by the viewer's server, as
  `{"reviews": [{"run_id", "feedback", "timestamp"}], "status"}`. A page
  written with `--static` downloads it instead, normally to `~/Downloads`;
  copy it into the iteration directory before reading it or passing that
  directory to `--previous-workspace`.

## Trigger results

`run_trigger_eval.py` prints one object:

- `skill_name`, `description`, `client`, and `errors` (messages of runs that
  were not measured).
- `results`: one item per query with `query`, `should_trigger`, `triggers`,
  `runs` (measured runs), `errors`, `trigger_rate` (null without measured
  runs), `pass`, and `error` (true when no run was measured). A should-trigger
  query passes when its rate reaches the threshold, 0.5 by default; a
  near-miss passes below it.
- `summary`: `total`, `passed`, and `failed`.

`run_loop.py` writes `results.json` to a timestamped directory under
`--results-dir` with `exit_reason`, `original_description`,
`best_description`, `best_score`, `best_train_score`, `best_test_score`,
`final_description`, `iterations_run`, `holdout`, `train_size`, `test_size`,
`history`, `clients`, `best_client_scores`, and `unmeasured_runs`. A query's
merged result passes only when it passes in every client; its per-client
counts are under `clients`. Each `history` item adds `client_scores` with each
client's train and test pass counts.

## Reviewing queries in a browser

To let the user edit `eval_queries.json` in `assets/eval_review.html`, copy
the file to a temporary HTML file and replace:

- `__EVAL_DATA_PLACEHOLDER__` with the JSON array itself, without quotes;
- `__SKILL_NAME_PLACEHOLDER__` with the skill name;
- `__SKILL_DESCRIPTION_PLACEHOLDER__` with the current description.

Open it for the user. "Export Eval Set" saves `~/Downloads/eval_set.json`,
or `eval_set (1).json` and so on when the name exists; save the newest one as
`evals/eval_queries.json`.

## Exit status

Every script exits with 0 on success and 1 for invalid input or a failed
preflight check. `run_evals.py`, `run_trigger_eval.py`, and `run_loop.py` exit
with 2 when some runs were not measured; `grade.py` exits with 2 when some
runs could not be graded.
