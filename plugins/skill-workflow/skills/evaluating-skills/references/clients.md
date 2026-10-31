# How omp and Codex run

## Dedicated home

Each client runs with `HOME` set to a dedicated home that holds only a test
login. Create one per client and log in once:

```sh
H="$HOME/.cache/skill-evals/homes/omp"
mkdir -p "$H" && HOME="$H" omp login

H="$HOME/.cache/skill-evals/homes/codex"
mkdir -p "$H" && HOME="$H" CODEX_HOME="$H/.codex" codex login --device-auth
```

Do not install the evaluated skill, or its plugin, in that home: an installed
copy can load in the baseline runs too. The scripts pass the client only
`HOME`, `PATH`, and locale and terminal variables, so tokens in your shell are
not used.

## Output runs

- **omp** runs with `--approval-mode yolo` and no OS sandbox. A skill in a
  plugin runs inside a copy of that plugin (`--plugin-dir`), so its agents
  and sibling skills are present; the arms differ only in the evaluated
  skill. A skill outside a plugin is given by path, and the baseline without
  it runs with `--no-skills`.
- **Codex** runs with `--sandbox workspace-write`, without network access,
  and receives only the skill's path, without its plugin.

Both start in an empty temporary git directory with the eval's input files,
and their skill copies leave out `evals/`. Ctrl-C ends the client sessions
and records the runs in flight as unmeasured.

## Trigger runs

The skill, with the description under test, is placed in a fresh project
(`.omp/skills/<name>/` or `.agents/skills/<name>/`), and the script first
confirms that the client discovers it. As in skill-creator, the agent's first
tool call decides, ignoring omp's `todo`: reading the skill is a trigger,
anything else or no tool call is not. Rates therefore compare only within
one client and model.

## Grading and rewrites

These use a tool-less call to the same client and model: omp with
`--no-tools --no-skills`, Codex with `--ephemeral --sandbox read-only`.

## Python

The scripts need Python 3.11 or newer. With an older `python3`, they print an
equivalent `uv run --no-project --python 3.12 python ...` command and exit;
run that instead.
