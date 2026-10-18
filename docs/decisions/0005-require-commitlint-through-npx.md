---
status: proposed
date: 2026-10-19
decision-makers: sonsu-lee
---

# Require commitlint through npx with bundled ESM defaults

## Context and Problem Statement

The commit skill's prose conventions alone do not ensure messages are checked
before use. Target repositories may have their own commitlint configuration or
none at all. How should the skill require repeatable validation without adding
project dependencies, Git hooks, or CI configuration?

## Considered Options

- Rely on manual review
- Require a project-local or global commitlint installation
- Run commitlint through `npx` with its built-in Conventional Commits preset
- Run commitlint through `npx` with self-contained defaults bundled in the skill

## Decision Outcome

Chosen option: "Run commitlint through `npx` with self-contained defaults bundled
in the skill", because it checks the skill's own conventions without requiring
a new installation in each target repository.

Require validation before committing, amending, or presenting a message as
ready. Repository configuration takes precedence. When none exists, use the
bundled configuration; a broken or explicitly selected but missing repository
configuration is a blocker, not permission to fall back.

Bundle the defaults as an `.mjs` configuration with inline rules and parser
options. Explicit ESM avoids dependence on a nearby package manifest. Avoid
imports and external presets because packages available to the `npx` executable
are not necessarily resolvable from the installed skill's directory. Resolve the
asset relative to the loaded skill and pass its absolute path to commitlint;
a wrapper script is unnecessary.

The built-in preset was not selected because its 100-character limit and scope
rules differ from the skill's conventions. Manual review remains necessary for
message accuracy and requirements that lint cannot fully check.

### Current instructions

The [commit skill](../../plugins/git-workflow/skills/writing-commits/SKILL.md)
is the source for validation procedure, configuration precedence, pinned CLI
version, prerequisites, and manual checks. Its
[ESM configuration](../../plugins/git-workflow/skills/writing-commits/assets/commitlint.config.mjs)
defines the machine-checked defaults. The
[README](../../README.md#testing-a-plugin) documents contributor verification.
Keep those documents current rather than copying their commands and rule values
into this decision record.

### Consequences

- Good, because messages receive a mechanical check rather than prose review
  alone, without replacing repository-specific conventions.
- Good, because the default check needs no project package manifest, external
  preset, global installation, or wrapper script.
- Bad, because Node.js, npm, and initial registry access are required, and
  repository-specific presets or plugins still need their documented setup.
- Bad, because bundled rules and parser options need regression coverage.
- Bad, because skill instructions do not enforce behavior outside the agent's
  workflow and cannot replace semantic review.

### Confirmation

Follow the README's commit-validation tests and temporary-`HOME` plugin check.
Verify the installed configuration works from a separate target repository,
rejects rule violations, and is not used instead of repository-specific rules.
Tests cover module loading, breaking-change syntax, style, line-length
boundaries, and blank-line separators.
