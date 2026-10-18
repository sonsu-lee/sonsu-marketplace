# Branch validation

Select the execution setup and configuration independently. Run from the target
repository's root. Set `branch_name` to the exact proposed name; do not use Git
shorthand such as `@{-1}` or a full `refs/heads/` path.

First verify Git ref syntax:

```sh
git check-ref-format --branch "$branch_name"
```

This checks Git syntax, not the repository's naming convention.

## Reuse the repository's execution setup

Inspect contributor instructions, scripts, dependency declarations, managed tool
versions, and relevant hook or CI configuration. Use the documented branch
validator and its version, including tools other than commit-check. Preserve
its configuration, environment settings, and acceptance criteria.

A declared or managed tool that is not installed needs its documented setup;
it is not permission to use the fallback. Report an unavailable or failing
configured validator rather than replacing it. A configuration file alone does
not establish a runner or a version, so the fallback can load it when no
execution setup exists.

Use the validator's supported candidate-name input. Do not create or rename a
branch just to make a current-branch-only command inspect a proposal, and do
not claim the proposal passed based on a check of the currently checked-out
branch. If the configured tool cannot check a proposal without mutation,
report that limitation rather than silently switching validators.

For commit-check versions supporting branch names on stdin:

```sh
printf '%s\n' "$branch_name" | commit-check --branch --format json
```

Keep any repository wrapper, managed environment, and configured version in
place. Confirm the installed version's input support before using this example.
Do not invoke a hook wholesale if it also runs unrelated checks.

## Use uvx only without an existing execution setup

[Conventional Branch](https://conventionalbranch.org/#tooling) links to
[commit-check](https://github.com/commit-check/commit-check), a Python CLI.
It is not an npm package. The fallback uses `uvx` from uv and Python 3.10 or
newer, not `npx commit-check`. The first uncached run needs registry access.

When a repository commit-check configuration exists, preserve it:

```sh
printf '%s\n' "$branch_name" |
  uvx --from commit-check==2.19.1 commit-check --branch --format json
```

The pinned CLI discovers `cchk.toml` and `commit-check.toml` in the repository
root or `.github/`. Honor explicitly selected configuration with `--config` and
existing `CCHK_*` settings. Do not pass flags that replace repository rules.
A missing explicitly selected configuration or a broken setup is a blocker,
not permission to switch to the bundled defaults.

## Select defaults only when configuration is absent

Only when no repository branch configuration is established, set `skill_dir`
to the absolute directory containing the loaded `SKILL.md` and use its
`assets/commit-check.toml`. Do not guess a plugin cache path or copy the file
into the target repository.

With an existing compatible commit-check installation, keep that executable
and add `--config "$skill_dir/assets/commit-check.toml"`. Do not upgrade its
version to load the asset; report incompatibility if necessary. With another
validator, preserve its documented behavior and manually review skill defaults
it does not check.

With neither an execution setup nor configuration:

```sh
printf '%s\n' "$branch_name" |
  uvx --from commit-check==2.19.1 commit-check --branch --format json \
    --config "$skill_dir/assets/commit-check.toml"
```

The bundled configuration narrows allowed prefixes to the skill's defaults
and enables description-grammar checks. It must not replace explicit
repository or user choices, such as an authorized agent prefix; use the
repository's rule settings or an explicit per-run override for that choice,
without broadening unrelated rules. The tool also admits special CI ref names;
manually enforce the skill's trunk-name restriction.

## Finish the check

Require a successful exit and a branch-check result for the exact candidate.
For commit-check JSON output, inspect the `CC201` entry's `value` and `status`;
a skipped rule or a result for another name does not prove validation. Honor
repository warning policy. With bundled defaults, require `CC201` to pass
without warnings. Never use `--dry-run` to establish a pass.

Review purpose, issue IDs, and prefix selection separately. Do not install
project configuration, hooks, or CI just to run this check. Report missing
runtimes, network access, and configuration errors as blockers. Recheck whenever
the proposed name changes.
