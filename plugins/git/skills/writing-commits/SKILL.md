---
name: writing-commits
description: Use this skill when writing or revising a git commit message, including when creating or amending a commit.
compatibility: >-
  Requires Git. Without a repository validation runner, fallback requires
  uv (uvx), a supported Python environment, and registry access.
---

# Writing commits

Write a message that describes the actual change. Follow the target repository's
commit rules; when none exist, use [committed's Conventional Commit rules](references/validation.md).

## Workflow

1. Inspect the changes, repository rules, and configured validator.
2. Draft a Conventional Commit when the repository has no other rule:
   `<type>(<scope>): <subject>`. The scope is optional. Describe the change
   accurately; add a body or breaking-change explanation when needed.
3. Before creating or amending a commit, or presenting a message as ready,
   validate the complete message using the [validation procedure](references/validation.md).
   Recheck after every edit.

Use the repository's validator, version, and configuration first. Only when no
runner exists use pinned `committed` through `uvx`; only when no repository
configuration exists use the bundled Conventional Commit configuration.
Never replace a failing configured validator or install hooks or CI to validate
a message. Report execution blockers. A hook that has not run does not validate
a proposed message.

Creating or amending a commit requires explicit authority; a message draft does
not authorize either action.

## Evaluate the result

Score audience/purpose, factual fidelity, clarity, scope/authority, and
verification: 0 failed, 1 partial, 2 evidenced. Exclude inapplicable items with
reasons and normalize to 10. Require 8/10 and verified requirements, authority,
safety, contracts, and evidence. Fix failures and reevaluate up to three times,
not unchanged. If still unsuccessful, report each score, conditions, evidence,
and blockers. Wait for required decisions, permission, or access.
