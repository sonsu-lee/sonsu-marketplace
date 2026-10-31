# Evaluation files

The scripts read the skill's `evals/` directory and write the workspace layout
of Anthropic's skill-creator.

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
      "assertions": ["Writes a CSV with no duplicate rows"]
    }
  ]
}
```

- `skill_name` equals the `name` in `SKILL.md`.
- Each eval has a unique integer `id`, a `prompt`, and an `expected_output`.
  `files` and `assertions` are optional; no other key is accepted. The key is
  `assertions`, not `expectations`.
- `files` lists paths under `evals/files/`. A file is copied into the run's
  working directory by base name; a directory, written with a trailing `/`,
  has its contents copied there.
- Evals use only these inputs: no other paths, network services, or
  credentials.
- No file under `evals/` may be named `SKILL.md`; Codex would register it as a
  skill.

## `evals/eval_queries.json`

```json
[
  {"query": "clean the duplicates in exports/q3.csv", "should_trigger": true},
  {"query": "convert this CSV to Parquet", "should_trigger": false}
]
```

Each `query` appears once; the train and test split matches results by text.

## Workspace

Results go to `${XDG_CACHE_HOME:-~/.cache}/skill-evals/<skill>-workspace`
unless `--workspace` is given. Do not commit it.

```text
<workspace>/
  skill-snapshot/               previous version for --baseline old
  <client>/iteration-N/
    iteration.json              client, model, effort, home, baseline, runs
    benchmark.json, benchmark.md
    feedback.json               saved by the review viewer
    eval-<id>/
      eval_metadata.json        prompt, expected output, files, assertions
      <config>/run-<r>/         config: with_skill, without_skill, old_skill
        transcript.md           prompt, brief, tool calls, final message
        events.jsonl            raw client events
        outputs/                files the run saved, final_message.md,
                                metrics.json
        timing.json             tokens, duration, observed model; "error"
                                is null when the run was measured
        grading.json            expectations[] with text, passed, evidence;
                                summary
```

- A run is measured when `timing.json` has `"error": null`. A run on another
  model or effort than requested is recorded as an error.
- `benchmark.json` reports each configuration's mean pass rate, time, and
  tokens, and `delta` as with_skill minus the baseline. `metadata.coverage`
  gives the graded and expected runs for each eval and configuration;
  `benchmark.md` lists any that fall short.

## Trigger results

`run_trigger_eval.py` prints `results` with one item per query: `triggers`,
`runs` (measured runs), `trigger_rate`, `pass`, and `unmeasured` (no run
measured). A query that should trigger passes at a rate of at least 0.5; a
near-miss passes below it. `run_loop.py` adds `history` per iteration and
`best_description`.

## Exit status

All scripts exit with 0 on success and 1 for invalid input. `run_evals.py`,
`run_trigger_eval.py`, and `run_loop.py` exit with 2 when some runs were not
measured; `grade.py` exits with 2 when some runs were not graded.
