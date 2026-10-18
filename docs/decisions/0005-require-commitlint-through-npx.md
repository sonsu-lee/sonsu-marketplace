---
status: superseded by ADR-0006
date: 2026-10-19
decision-makers: sonsu-lee
---

# Require commitlint validation through npx in the commit skill

## Context and Problem Statement

The `writing-commits` skill describes commit-message conventions and tells the
agent to respect repository commitlint configuration, but does not require
running a validator. A message can therefore be presented as ready or committed
without a mechanical check. How should the skill require validation without
adding project dependencies, Git hooks, or CI configuration?

## Considered Options

- Keep manual review as the only required check
- Require a locally or globally installed commitlint
- Require commitlint through `npx` as a skill workflow step

## Decision Outcome

Chosen option: "Require commitlint through `npx` as a skill workflow step",
because it makes validation mandatory for the agent without requiring every
target repository to install a new development dependency.

This complements [ADR-0004](0004-require-markdown-lint.md), which requires
Markdown lint through `npx`. That accepted decision remains unchanged: it
covers marketplace Markdown, while this decision covers commit messages written
with the plugin in target repositories.

The skill requires the following procedure:

- Validate the complete proposed message before creating or amending a commit,
  or presenting the message as ready to use. Validate again after every edit.
- Use Node.js 22.12.0 or newer and npm. Run the pinned CLI from the target
  repository's root, with the exact message saved in a temporary UTF-8 file:

  ```sh
  npx --yes --package @commitlint/cli@21.2.4 commitlint \
    --strict --verbose --edit "$message_file"
  ```

- Use the repository's commitlint configuration and required dependencies,
  including an explicit `--config` path when its workflow specifies one. Do not
  replace repository rules or ignore configuration failures.
- Only if no repository commitlint configuration exists, add `--default-config`
  to use the CLI's built-in Conventional Commits configuration. This avoids
  creating a package manifest or installing a separate preset in the repository.
- Require zero exit status with no errors or warnings. If the tool or required
  dependencies cannot run, report the blocker and do not commit. Manual review
  does not waive validation.
- Keep reviewing message accuracy and the skill's additional rules, including
  its default 72-character line limit; the built-in preset allows 100 characters.
  Remove the temporary message file after use.

The [commitlint CLI reference](https://commitlint.js.org/reference/cli.html)
documents `--edit`, `--strict`, and `--default-config`. The CLI version is pinned
so changes to the validation tool are deliberate plugin updates.

### Consequences

- Good, because syntax and configured rules are checked instead of relying only
  on the agent's interpretation of prose.
- Good, because repository-specific rules take precedence and repositories
  without configuration still have a runnable baseline.
- Good, because no global installation or repository setup is required for the
  baseline check; `npx` downloads and caches the pinned CLI when needed.
- Bad, because Node.js, npm, and initial npm registry access are required.
  Repository-specific presets and plugins still need their documented setup.
- Bad, because skill instructions are not enforcement outside the agent's
  workflow. This change adds no Git hook or CI check.
- Bad, because lint cannot establish message accuracy or enforce every prose
  rule, so manual review remains necessary as an additional check.

### Confirmation

Exercise the documented commands in a temporary Git repository: a valid complete
message passes with no configuration, an invalid type fails, and a warning fails
under `--strict`. With a custom repository configuration, verify that its allowed
type passes and a type it disallows fails, rather than using the baseline rules.

Run the README's plugin test procedure with a temporary `HOME`; both skills must
appear in `omp skill list` without warnings. Lint all changed Markdown according
to ADR-0004 and check links and rendered Markdown separately.
