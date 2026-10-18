---
name: naming-branches
description: Use this skill when choosing or checking a git branch name, including when creating or renaming a branch.
---

# Naming branches

Check and follow the repository's branch-naming rules, including its
branch-name validator configuration, such as
[commit-check](https://github.com/commit-check/commit-check). Use the defaults
below where the repository specifies no rule.

## Naming rules

Name the branch for the purpose of the work. Use
[Conventional Branch 1.1.0](https://conventionalbranch.org/v1.1.0/spec.json):

```text
<type>/<description>
```

| Type | Use for |
| --- | --- |
| `feature` | New features or enhancements |
| `fix` | Bug fixes |
| `hotfix` | Urgent production fixes |
| `release` | Release preparation |
| `chore` | Other maintenance, including dependencies, docs, CI, and refactoring |

* **Type:** use `feature`, not `feat`, and `fix`, not `bugfix`. Choose the
  purpose of the whole branch, not an individual commit's type. Commit
  messages retain their own conventions, including `feat`.
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

## Examples

```text
feature/eng-123-add-login-page
fix/issue-45-header-overflow
hotfix/payment-outage
release/v1.2.0
chore/upgrade-node-v20.11
```
