---
status: accepted
date: 2026-10-19
decision-makers: sonsu-lee
---

# Bundle the commit skill's rules as an ESM commitlint configuration

## Context and Problem Statement

[ADR-0005](0005-require-commitlint-through-npx.md) requires commitlint through
`npx`, using the built-in Conventional Commits preset when a repository has no
configuration. That preset allows 100-character lines and does not enforce our
lowercase scope rule. How can the fallback validate the skill's own conventions
without installing dependencies in the target repository?

## Considered Options

- Keep the built-in preset and manually check the differences
- Add a wrapper script that constructs and runs commitlint configuration
- Bundle a self-contained ESM configuration with the skill

## Decision Outcome

Chosen option: "Bundle a self-contained ESM configuration with the skill",
because commitlint already supports configuration files and no execution wrapper
is needed. This supersedes ADR-0005's fallback choice; its mandatory `npx`
validation, repository-first precedence, pinned CLI version, prerequisites, and
stop-on-failure policy remain in force.

Store the configuration at `skills/writing-commits/assets/commitlint.config.mjs`.
Use `export default` and the `.mjs` extension so module interpretation does not
depend on a nearby `package.json`. Keep rules and parser options inline, with no
imports or `extends`: packages available to the `npx` executable are not
necessarily resolvable from the installed skill's directory.

When the target repository has no commitlint configuration, resolve the asset
relative to the loaded `SKILL.md` and pass its absolute path to `--config`:

```sh
npx --yes --package @commitlint/cli@21.2.4 commitlint \
  --config "$skill_dir/assets/commitlint.config.mjs" \
  --strict --verbose --edit "$message_file"
```

Run from the target repository's root. Do not hard-code an omp cache path, copy
the configuration into the repository, or use the bundled rules to override an
existing repository configuration. If an explicitly selected configuration is
missing or an existing one is broken, report a blocker rather than falling back.

The configuration checks types, lowercase scopes, subject style, blank-line
separators, and 72-character header, body, and footer limits. Inline parser
options recognize `!`, `BREAKING CHANGE`, and `BREAKING-CHANGE` without requiring
both a header marker and a footer. Disable default ignores so semver-like or
merge-like messages do not bypass the skill's conventions.

Keep execution procedure, precedence, and semantic review in `SKILL.md`. Read
back the complete message file and reject an empty header before validation;
commitlint can skip empty files. Continue manually reviewing accuracy,
imperative wording, the subject's initial lowercase letter, and breaking-change
explanations. The built-in body-length rule exempts URL-containing lines, which
still need manual review against the skill's line limit.

### Consequences

- Good, because the fallback checks the skill's own mechanical rules rather than
  relying on a preset with different defaults.
- Good, because the installed asset runs without a project package manifest,
  external preset, global installation, or wrapper script.
- Bad, because the inline rules and parser options need behavioral regression
  coverage when the skill's conventions or pinned CLI version change.
- Bad, because not every prose requirement is mechanically checked, and skill
  instructions still provide no enforcement outside the agent's workflow.

### Confirmation

Run `node --test plugins/git-workflow/tests/commitlint.test.mjs`. Cover ESM loading
with no project manifest and with CommonJS and ESM projects, independent
breaking-change markers, invalid types and subject style, lowercase scopes,
72/73-character boundaries, and required blank lines.

Install the plugin using the README's temporary-`HOME` procedure. Verify both
skills load without warnings, then run commitlint from a separate temporary Git
repository using the asset beside the installed skill. Verify a valid message
passes, a 73-character header fails, and repository-specific configuration is
used instead of the bundled rules when present. Follow ADR-0004 for Markdown
lint, link checks, and rendered-document review.
