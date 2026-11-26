# Agentic benchmark: Ponytail 5 vs Ponytail vs no skill

*2026-10-07. Opus 5.5, default effort, Claude Code CLI 2.1.288. Headless Claude
Code sessions, 39 tasks, 5 runs each.*

Ponytail 5 replaces the current Ponytail (v4.13.0). Before it shipped, every
change to the rules had to beat the current version in a paired run, one change
at a time. This file is the final check: Ponytail 5, Ponytail (v4.13.0) and the
same agent without any skill, measured in one run so that time of day and model
drift hit all three the same way.

## Setup

- **Agent:** a headless Claude Code session per task (`claude -p`), Opus 5.5,
  default effort. The skill is loaded with `--plugin-dir`, the same way a user
  gets it. The no-skill arm loads nothing. For every arm I checked the session
  transcript of a finished cell to prove what was injected. This run covers
  Claude Code; Ponytail also ships for Codex, Cursor, Copilot and more.
- **Tasks (39):**
  - 12 feature tickets in a real FastAPI + React repo
    ([full-stack-fastapi-template][template]), scored on the `git diff`.
  - 18 surgical tasks with **hidden checks**: bug fixes, refunds, SQL with
    untrusted input, path traversal, forged tokens, rate limiting, a privacy
    case (one email to many subscribers without exposing their addresses),
    renames and format changes that must reach every caller.
  - 6 "build me a small app" requests and 3 "show me an example" requests, where
    the agent picks the scope.
- **Runs:** 5 per task and arm, 585 sessions. The three arms alternate task by task.
- **Isolation:** every session runs in a fresh temp folder outside any git repo,
  with `CLAUDE.md` loading and auto memory switched off, and only the plugin
  under test. (An earlier version of the harness ran some tasks inside the
  Ponytail repo. Claude Code then showed the model the repo's recent commit
  messages. That is fixed, and none of the numbers here come from that setup.)
- **No shell, by design:** Bash is disabled for every arm. Agents write code and
  tests; the benchmark runs them afterwards (hidden checks, injected bugs). This
  measures what the agent writes, not what it can debug.

**Statistics.** For each task I take the median of the 5 runs, divide arm by
baseline, and report the geometric mean of those ratios over the tasks, with a
95% bootstrap interval. "Better on X of Y tasks" is a sign test over the tasks.

## Results

| vs no skill | Ponytail (v4.13) | **Ponytail 5** |
| --- | ---: | ---: |
| Lines of code | -48% | **-53%** [-63..-41] |
| Code information (gzip of the delivered code) | -34% | **-41%** [-51..-30] |
| Output tokens | -43% | **-45%** [-54..-35] |
| Cost | -16% [-27..-5] | **-26%** [-36..-16] |
| Time | -38% | **-41%** [-49..-32] |
| Turns | -21% | **-22%** |
| Cheaper on | 25 of 38 tasks | **30 of 38 tasks** |

| Ponytail 5 vs Ponytail (v4.13) | change | tasks better / worse |
| --- | ---: | ---: |
| Cost | **-10.8%** [-14..-8] | 35 / 4 |
| Code information (gzip) | **-10.6%** [-15..-6] | 26 / 7 |
| Lines of code | **-8.6%** [-15..-3] | 20 / 7 |
| Time | -4.0% [-9..+1] | 23 / 16 |
| Output tokens | -2.7% [-8..+3] | 21 / 18 |
| Reply length | +0.1% | 20 / 19 |

Mean cost per session: no skill $0.200, Ponytail $0.156, Ponytail 5 $0.142 (list
price).

### Correctness and safety

Only the 18 surgical tasks have hidden checks that run the code (right result
and no security or privacy hole). On those:

| Metric | no skill | Ponytail (v4.13) | Ponytail 5 |
| --- | ---: | ---: | ---: |
| Hidden checks passed | 86/90 (95.6%) | 86/90 (95.6%) | 87/90 (96.7%) |

On the six security tasks of the earlier safety tier (`safe-path`, `sql-user`,
`auth-token`, `rate-limit`, `csv-sum`, `cache`) all three arms passed 30 of 30
runs.

Less code did not cost correctness or safety. It did not add any either: the
three arms are level.
The privacy task is hard for all of them (2 of 5 runs passed in every arm).

The other 21 tasks are there to measure code size. Their "pass" only means the
code was delivered or compiles, so I do not count them as a quality result.
(Over all 39 tasks no skill passes 186/195, mostly lost to 5 timeouts on one
task. That gap says nothing about code quality.)

Whether the shorter code on these 21 tasks still does the whole job is checked
by the completeness judge (`benchmarks/agentic/complete.py`, Opus 5.5 as judge,
blind, self-test passed). It reads what each run delivered and scores it from 0
(stub) to 3 (fully implements the task).

| Metric | no skill | Ponytail 5 |
| --- | ---: | ---: |
| Fully implements the task (3 of 3) | 100/100 | 105/105 |

The 5 no-skill runs killed at the timeout delivered nothing and are not judged.
The judge scored one Ponytail 5 run 1 for a missing `col` import; the import is
on line 5 of that file (the judge only saw the diff), so it is counted as
complete.

### Tests

Ponytail's rule: logic with a branch, a loop, a parser, money or security, or a
whole new script, leaves one small test or an `assert` self-check behind.
Trivial changes need none. I sorted the tasks by that rule before measuring (22
need a test, 11 do not, 6 borderline ones count for neither), then checked what
each agent left behind. To see whether a test is worth anything, I injected
small bugs (a flipped comparison, a dropped `if`, an off-by-one) into the code
the agent wrote and ran the agent's own test against each one. The test and
mutation tools ship with the user-runnable benchmark.

| Metric | no skill | Ponytail (v4.13) | Ponytail 5 |
| --- | ---: | ---: | ---: |
| A test where the logic needs one | 68% | 95% | **98%** |
| Tests that run (90 cells) | 53 | 84 | **86** |
| Injected bugs caught, over all cells | 46% | 64% | **66%** |
| Injected bugs caught, where a test exists | 77% | 69% | 69% |
| A test where none was needed | 36% | 45% | 45% |

No skill writes the most thorough single tests, but often writes none. 20 of the
25 Ponytail 5 cells in the last row are two to four `assert` lines inside the
learning examples, where they show the result; the other 5 add an endpoint test
to the repo's existing test suite.

### Replies

A blind judge (Sonnet 5.5, order shuffled per pair, gated by a self-test) picked
the reply that serves a busy developer better: true to the diff, tells a
reviewer everything they must know, easy to read once.

- Ponytail 5 vs Ponytail (v4.13):
  - in the real run (each reply describes its own code): **110 : 67** (18 ties,
    p=0.002)
  - same code (both replies describe one diff): **131 : 89** (12 ties, p=0.006)
- Ponytail 5 vs no skill:
  - in the real run (each reply describes its own code): 82 : 106 (7 ties,
    p=0.09)
  - same code (both replies describe one diff): 99 : 118 (15 ties, p=0.22)

Ponytail 5 replies are 30% shorter than no skill. Against no skill the judge
found no significant difference, with a slight lean towards the longer no-skill
replies. Against Ponytail (v4.13) it clearly prefers Ponytail 5. The main reason
in the judge's notes: Ponytail 5 ends with what it skipped or did not check and
the risks a reviewer should know.

## Per task

Medians of 5 runs. Within each metric the order is none (no skill), PT
(Ponytail v4.13), PT5 (Ponytail 5). Lines are the delivered source lines
(comments included, tests excluded).

Task types: H = hidden check, L = learning example, R = repo feature,
S = small app.

| task | type | lines | cost $ | hidden check passed |
| --- | --- | ---: | ---: | ---: |
| `auth-token` | H | 18, 17, 16 | 0.081, 0.117, 0.105 | 5/5, 5/5, 5/5 |
| `cache` | H | 11, 11, 11 | 0.096, 0.097, 0.083 | 5/5, 5/5, 5/5 |
| `conv-seam` | H | 12, 14, 14 | 0.122, 0.149, 0.139 | 5/5, 5/5, 5/5 |
| `conv-service` | H | 7, 4, 4 | 0.099, 0.110, 0.089 | 5/5, 5/5, 5/5 |
| `conv-ui` | H | 17, 17, 17 | 0.095, 0.119, 0.099 | 5/5, 4/5, 5/5 |
| `critic-email` | H | 33, 14, 12 | 0.127, 0.125, 0.115 | 5/5, 5/5, 5/5 |
| `csv-sum` | H | 58, 24, 17 | 0.133, 0.126, 0.111 | 5/5, 5/5, 5/5 |
| `rate-limit` | H | 44, 27, 26 | 0.147, 0.145, 0.144 | 5/5, 5/5, 5/5 |
| `reuse-money` | H | 9, 9, 9 | 0.083, 0.113, 0.096 | 5/5, 5/5, 5/5 |
| `reuse-slug` | H | 20, 19, 21 | 0.091, 0.118, 0.103 | 5/5, 5/5, 5/5 |
| `safe-path` | H | 16, 13, 13 | 0.117, 0.113, 0.106 | 5/5, 5/5, 5/5 |
| `scope-format` | H | 21, 15, 15 | 0.137, 0.153, 0.147 | 5/5, 5/5, 5/5 |
| `scope-recipients` | H | 13, 6, 4 | 0.154, 0.173, 0.159 | 2/5, 2/5, 2/5 |
| `scope-rename` | H | 3, 3, 3 | 0.133, 0.163, 0.128 | 4/5, 5/5, 5/5 |
| `sql-user` | H | 9, 7, 7 | 0.093, 0.099, 0.089 | 5/5, 5/5, 5/5 |
| `todo-null` | H | 203, 84, 77 | 0.166, 0.163, 0.125 | 5/5, 5/5, 5/5 |
| `trace-amount` | H | 9, 9, 9 | 0.096, 0.120, 0.106 | 5/5, 5/5, 5/5 |
| `trace-transfer` | H | 27, 21, 20 | 0.135, 0.133, 0.126 | 5/5, 5/5, 5/5 |
| `open-dataclass` | L | 84, 62, 51 | 0.110, 0.118, 0.106 | n/a |
| `open-decorators` | L | 79, 45, 20 | 0.107, 0.104, 0.087 | n/a |
| `open-mandelbrot` | L | 129, 43, 32 | 0.237, 0.114, 0.113 | n/a |
| `tmpl-be-archive` | R | 99, 75, 59 | 0.353, 0.319, 0.269 | n/a |
| `tmpl-be-bulkdelete` | R | 35, 22, 21 | 0.338, 0.208, 0.230 | n/a |
| `tmpl-be-count` | R | 25, 11, 12 | 0.280, 0.172, 0.145 | n/a |
| `tmpl-be-csv` | R | 48, 33, 38 | 0.270, 0.226, 0.218 | n/a |
| `tmpl-be-duplicate` | R | 20, 21, 21 | 0.208, 0.207, 0.181 | n/a |
| `tmpl-be-search` | R | 31, 29, 29 | 0.244, 0.221, 0.221 | n/a |
| `tmpl-fe-colorpicker` | R | 135, 55, 26 | 0.199, 0.143, 0.111 | n/a |
| `tmpl-fe-command` | R | 319, 169, 131 | 0.431, 0.327, 0.269 | n/a |
| `tmpl-fe-datepicker` | R | 335, 11, 10 | 0.427, 0.140, 0.099 | n/a |
| `tmpl-fe-dropzone` | R | 247, 65, 62 | 0.265, 0.173, 0.134 | n/a |
| `tmpl-fe-rating` | R | 136, 70, 60 | 0.183, 0.152, 0.124 | n/a |
| `tmpl-fe-wizard` | R | 311, 95, 90 | 0.678, 0.236, 0.214 | n/a |
| `vibe-csvstats` | S | 124, 45, 47 | 0.150, 0.115, 0.102 | n/a |
| `vibe-langgraph` | S | 148, 28, 29 | 0.557, 0.103, 0.095 | n/a |
| `vibe-md2html` | S | 0, 106, 139 | timeout, 0.287, 0.316 | n/a |
| `vibe-password` | S | 224, 41, 38 | 0.175, 0.117, 0.097 | n/a |
| `vibe-shortener` | S | 285, 83, 79 | 0.240, 0.128, 0.136 | n/a |
| `vibe-todo` | S | 197, 44, 45 | 0.157, 0.101, 0.106 | n/a |

## Reproduce

See the [upstream harness instructions][harness]. Short version: clone the
template at
`cd83fc1`, run `python run.py --selftest` (no API), then

```bash
python run.py --task <the 39 task ids from the table above, comma separated> \
  --arms baseline,ponytail,ponytail2 --models opus --runs 5
```

with `PONYTAIL_PLUGIN_DIR` pointing at Ponytail (v4.13) and
`PONYTAIL2_PLUGIN_DIR` at Ponytail 5. Every workspace is kept under
`runs/<stamp>/`, so any metric can be recomputed offline with `--rescore`.

[template]: https://github.com/fastapi/full-stack-fastapi-template
[harness]: https://github.com/DietrichGebert/ponytail/blob/96608e078b2d5ea607c5c3b8b5a54d1c1fba6846/benchmarks/agentic/README.md
