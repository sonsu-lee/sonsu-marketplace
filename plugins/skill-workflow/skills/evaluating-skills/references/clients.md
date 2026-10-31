# Running against omp and Codex

## Dedicated homes

Every model call runs with `HOME` set to a dedicated home that holds only a
test login. Create one per client and log in once:

```sh
H="$HOME/.cache/skill-evals/homes/omp"
mkdir -p "$H" && HOME="$H" omp login

H="$HOME/.cache/skill-evals/homes/codex"
mkdir -p "$H" && HOME="$H" CODEX_HOME="$H/.codex" codex login --device-auth
```

- Do not install the evaluated skill, or a plugin that contains it, in that
  home. An installed copy can load in the baseline runs too, so every script
  lists the home's skills first and refuses a home where the skill appears.
- Other installed skills are not refused, but their influence shows up in the
  results.
- The scripts pass only `PATH`, `LANG`, `LC_ALL`, `TMPDIR`, `USER`, `LOGNAME`,
  `SHELL`, `TERM`, and the home variables to the client, so provider keys and
  tokens in your shell are not used.

## omp

- Task runs use `--approval-mode yolo` without an OS sandbox, so the agent has
  your user's file and network access; the temporary working directory and
  the dedicated home only change its defaults. Do not write evals that touch
  paths outside the working directory, use network services, or need
  credentials.
- For a skill inside a plugin, every arm loads its own copy of the plugin with
  `--plugin-dir`: with_skill and old_skill swap in their version of the skill,
  and without_skill leaves it out. The plugin's agents, sibling skills, and
  `skill://` resources therefore resolve in every arm, and only the evaluated
  skill differs. A skill outside a plugin is given by path, and without_skill
  runs with `--no-skills`.
- Trigger runs place the candidate in `.omp/skills/<name>/` of a temporary
  project and run with `--skills <name>` and `--approval-mode always-ask`.
- A trigger counts when the agent reads `skill://<name>`, its `SKILL.md`
  (with or without a line selector), or the placed `SKILL.md` path, or runs a
  shell command naming the placed `SKILL.md` or `skill://<name>`. Reading
  other files under `skill://<name>/` is neither a trigger nor a counted call.
- Grading and description rewrites use `--no-tools` and `--no-skills`.

## Codex

- Every run uses `codex --no-daemon exec --json`, so it never attaches to a
  running Codex daemon.
- Task runs use `--sandbox workspace-write` with `--add-dir` for the outputs
  directory; commands have no network access.
- Trigger runs place the candidate in `.agents/skills/<name>/` of a temporary
  git repository and use `--sandbox read-only`. Before measuring, the script
  asks `codex app-server` (`skills/list`) to confirm that exactly that copy is
  discovered.
- A trigger counts when a command names `.agents/skills/<name>/SKILL.md`.
  Listing the skill directory is neither a trigger nor a counted call.
- The observed model and effort come from the `turn_context` entries of the
  session rollout in the home's `.codex/sessions`.
- Grading and description rewrites use `--ephemeral` and `--sandbox
  read-only` in an empty directory.

## Both clients

- Runs work in temporary directories outside the workspace, and skill copies
  never include `evals/`, so neither the brief nor the skill points the agent
  to expected outputs or assertions.
- Codex arms receive only the skill's path, without its plugin, so an omp
  delta and a Codex delta for a plugin skill measure different contexts.
- Trigger detection ignores `todo` calls. By default, a run that makes three
  other tool calls without reading the skill counts as not triggered, as does
  a run that finishes without reading it.
- A run that fails to measure is retried by rerunning the command
  (`run_evals.py`) or once automatically (trigger runs); one that still fails
  is reported as unmeasured, never as a pass or a miss.
- With a `python3` older than 3.11, each script prints its version and the
  equivalent `uv run --no-project --python 3.12 python <script> <args>`
  command and exits with 1. Run that command instead.
- Compare scores only within the same client and model; trigger detection is
  a heuristic over each client's events.
