---
name: naming-branches
description: >-
  Use to choose or check Git branch names, including creation or renaming.
  Not for listing, switching, or deleting branches.
compatibility: >-
  Requires Git. Without a repository validation runner, fallback requires
  uv (uvx), Python >=3.10, and registry access.
---

# Naming branches

Choose a branch name that describes the purpose of the whole branch. Follow
repository branch-naming rules, including validator configuration; use the
defaults below where no rule is specified.

## Workflow

1. Check the repository's naming rules and the purpose of the work.
2. Choose a name using the rules below.
3. Before creating or renaming a branch, or presenting a name as ready,
   follow [Required validation](#required-validation). Recheck every changed
   proposal.

## Naming rules

Use [Conventional Branch 1.1.0](https://conventionalbranch.org/v1.1.0/spec.json):

```text
<type>/<description>
```

| Type | Use for |
| --- | --- |
| `feat` | New features or enhancements |
| `bugfix` | Bug fixes |
| `hotfix` | Urgent production fixes |
| `release` | Release preparation |
| `chore` | Maintenance: dependencies, docs, CI, and refactoring |

* **Type:** use `feat`, not `feature`, and `bugfix`, not `fix`. Choose the
  purpose of the whole branch, not an individual commit's type. Commit
  messages retain their own conventions, including `fix`.
* **Description:** keep it concise and specific. Use lowercase ASCII letters,
  digits, and hyphens between words. Dots are allowed between alphanumeric
  segments, including outside release versions. Start and end with a letter
  or digit; do not put hyphens or dots next to each other. Do not use spaces,
  underscores, or additional slashes.
* **Issue ID:** when one is supplied or established, put it first in lowercase:
  `eng-123` for `ENG-123`, or `issue-45` for GitHub issue #45. Do not invent one.
* **Trunk branches:** `main`, `master`, and `develop` stay unprefixed.
* **Agent prefixes:** use only when explicitly requested by the user or
  repository, not merely because an agent is doing the work.

## Required validation

Follow the [validation procedure](references/validation.md):

1. Check Git ref syntax and apply repository naming rules first.
2. Use the repository's existing validation command, tool, and version.
   Follow its documented setup if dependencies are missing; do not bypass
   a failing or unavailable configured validator.
3. Only if no execution setup is established, use pinned `commit-check` through
   `uvx`. This is the Python CLI linked by Conventional Branch, not an npm
   package. Preserve repository configuration when present; otherwise use
   the [bundled defaults](assets/commit-check.toml).

Inspect the result to confirm it checked the proposed name, not the current
branch or a skipped rule. Respect repository acceptance criteria. Do not
create a branch just to validate its name, or install a hook or CI job.
Report blockers rather than claim an unchecked name passed.

## Gotchas

* Review purpose, ticket IDs, and the choice of prefix separately.
* The CLI also admits special CI ref names; without an explicit repository
  exception, only `main`, `master`, and `develop` are unprefixed branch names.

## Examples

```text
feat/eng-123-add-login-page
bugfix/issue-45-header-overflow
hotfix/payment-outage
release/v1.2.0
chore/upgrade-node-v20.11
```
