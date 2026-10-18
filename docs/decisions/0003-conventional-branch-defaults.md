---
status: accepted
date: 2026-10-18
decision-makers: sonsu-lee
---

# Use Conventional Branch with fixed feature and fix spellings

## Context and Problem Statement

The git-workflow plugin provides commit-message guidance but not branch naming.
The earlier `chore/wip-snapshot` in the reference checkout contains a
`naming-branches` draft alongside unrelated plugins and enforcement code. We
need a focused skill that complements writing-commits without importing that
whole snapshot or confusing branch purposes with commit types.

## Considered Options

* Accept every upstream alias interchangeably.
* Use Conventional Branch with fixed `feature` and `fix` spellings.
* Reuse Conventional Commits types for branch prefixes.

## Decision Outcome

Chosen option: "Use Conventional Branch with fixed `feature` and `fix`
spellings", because it honors the requested naming preference while keeping
names within the upstream grammar. Explicit repository rules take precedence,
as they do in writing-commits; existing branch names alone are not policy.

The default purpose prefixes are `feature`, `fix`, `hotfix`, `release`, and
`chore`. Upstream `feat` and `bugfix` aliases are valid Conventional Branch
names, but not the skill's default spellings. Agent-source prefixes require an
explicit user or repository request. Dots are allowed between alphanumeric
segments in any description, matching the versioned 1.1.0 grammar rather than
the draft's version-only restriction.

The skill covers naming suggestions, compliance checks, creation, and local
renames. It does not implement Git Flow, change commit-message types, migrate
remote branches or PRs, or enforce policy through hooks or CI. A local rename
preserves the worktree and upstream configuration; it does not migrate the
remote branch or PR. Published branch renames require confirmation.

### Consequences

* Good, because one spelling per purpose makes generated names predictable.
* Good, because branch purposes stay distinct from individual commit types.
* Good, because the skill adds no runtime dependency beyond Git. The existing
  `git check-ref-format --branch` command validates ref syntax; the skill must
  separately check naming-policy compliance.
* Bad, because an upstream-valid alias may still need correction under these
  defaults, and repository-specific rules can produce different spellings.
* Bad, because skill instructions are guidance, not deterministic enforcement.

### Confirmation

Install git-workflow in a temporary `HOME` using the README's testing procedure.
Both naming-branches and writing-commits must appear in `omp skill list` without
warnings. Exercise branch creation and local rename in a disposable repository,
including preservation of an uncommitted file and upstream tracking.

Behavioral cases live in
[`evals.json`](../../plugins/git-workflow/skills/naming-branches/evals/evals.json):
feature/commit spelling separation, alias and separator checks, and a published
rename with uncommitted changes. Compare independent responses with and without
the skill, inspect the responses, and refine instructions when they introduce
unrequested operations. Text-only responses cannot prove actual tool behavior.

[`trigger-queries.json`](../../plugins/git-workflow/skills/naming-branches/evals/trigger-queries.json)
contains ten positive requests and ten near-miss negatives. To measure activation,
run these through fresh agent sessions with the plugin installed and inspect
whether the agent reads naming-branches/SKILL.md. Repeat each query three times
before reporting trigger rates. Description-only routing checks and plugin
listing are not evidence of actual activation.

## More Information

* [Conventional Branch 1.1.0 grammar](https://conventionalbranch.org/v1.1.0/spec.json)
* [Agent Skills best practices](https://agentskills.io/skill-creation/best-practices):
  keep the skill focused and refine it from observed execution.
* [Optimizing descriptions](https://agentskills.io/skill-creation/optimizing-descriptions):
  name the user intents and distinguish nearby Git tasks that do not need naming.
* [Evaluating skills](https://agentskills.io/skill-creation/evaluating-skills):
  start with a few realistic cases, compare a baseline, and inspect outputs.
* [Using scripts](https://agentskills.io/skill-creation/using-scripts):
  use an existing command for simple operations; no bundled script is needed here.
