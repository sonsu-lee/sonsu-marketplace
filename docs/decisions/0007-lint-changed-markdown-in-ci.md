# Lint changed Markdown before pushing and in CI

- Date: 2026-10-23
- Status: accepted
- Decision-makers: sonsu-lee
- Supersedes: [ADR-0004](0004-require-markdown-lint.md)

## Context

[ADR-0004](0004-require-markdown-lint.md) requires a pinned Markdown lint,
run through `npx`, on every added or modified Markdown file before pushing,
and rules out a new CI integration without recording why. The check therefore
depends on each contributor, human or agent, remembering to run it.

The repository now has a secret-free `checks` workflow
([ADR-0006](0006-keep-model-evaluations-local.md)) that already installs
Node.js, and the maintainer chose to have CI enforce the agreed rules that a
machine can check. Documentation projects commonly run Markdown lint in CI:
[GitLab](https://docs.gitlab.com/development/documentation/testing/) runs it
on merge requests that change Markdown because its documentation is "treated
like code", [.NET docs](https://github.com/dotnet/docs/blob/main/.github/workflows/markdownlint.yml)
runs it on pull requests, and
[markdownlint-cli2-action](https://github.com/DavidAnson/markdownlint-cli2-action)
documents linting only changed files for pull requests and gradual adoption.

## Decision

Keep ADR-0004's pinned `npx` command, its default rules, and the requirement
to run it on changed Markdown files before pushing. Also run the same command
in CI on the Markdown files a pull request or a push to `main` adds or
modifies, and fail the check on any error. Do not format files automatically
or lint unchanged files. The
[README's documentation guidance](../../README.md#writing-documentation) owns
the command and the workflow.

## Rejected alternatives

- **Local lint only (ADR-0004):** leaves enforcement to memory, so a missed
  run reaches review unnoticed.
- **Lint every Markdown file in CI:** would fail on untouched files and push
  repository-wide reformatting, which ADR-0004 deliberately avoided.
- **Pre-commit hooks:** need installing in every clone and can be skipped, so
  they cannot be the enforced check.

## Consequences

A Markdown error in a changed file fails the pull request even if the local
run was skipped. CI and local runs use the same pinned version and rules, so
their results should match; changing the version or rules means changing
both the README command and the workflow. The local run stays required, since
it gives feedback before pushing. Lint still does not check links, rendering,
or Standard Readme structure.
