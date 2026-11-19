# Commit validation

Use the target repository's documented validator, version, configuration, and
acceptance criteria first, including validators other than `committed`. A missing
or failing configured tool is a blocker, not permission to replace it. A
configuration alone does not establish a runner.

Write the exact complete message to a temporary UTF-8 file, set `message_file`
to its absolute path, and read it back. Validate that file using the existing
repository procedure. Never validate HEAD in place of a proposed message.

## Fallback

Without a repository runner, use the Rust-based
[`committed`](https://github.com/crate-ci/committed), packaged as a Python CLI.
The pinned fallback requires `uvx`, a supported Python environment, and registry
access on the first run. It does not install dependencies in the target project.

If the repository has `committed.toml`, preserve it:

```sh
uvx --from committed==1.1.12 committed --commit-file "$message_file"
```

Otherwise, if no repository commit configuration exists, set `skill_dir` to the
absolute directory containing this skill's loaded `SKILL.md` and run:

```sh
uvx --from committed==1.1.12 committed \
  --config "$skill_dir/assets/committed.toml" --commit-file "$message_file"
```

The bundled configuration enables Conventional Commits; other settings use
[committed's defaults](https://github.com/crate-ci/committed/blob/main/docs/reference.md).
In particular, the default subject limit is 50 characters, body lines 72, and
the subject must be capitalized, imperative, and not punctuated. Its default
Conventional Commit types are `fix`, `feat`, `chore`, `docs`, `style`,
`refactor`, `perf`, and `test`. Do not replace an established non-committed
configuration with bundled defaults; report a missing compatible runner instead.

Require a successful exit for the intended nonempty message. Review meaning,
accuracy, rationale, and breaking-change explanations separately. Revalidate
after every edit and remove the temporary file. Do not install hooks, CI, or
project dependencies merely to validate a message.
