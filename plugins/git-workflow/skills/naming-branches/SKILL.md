---
name: naming-branches
description: Use this skill when choosing, creating, or renaming a git branch, or checking a branch name against naming conventions, including when starting work on a fresh branch. Not for switching to an existing branch, committing, pushing, or opening a pull request without a naming task.
compatibility: Requires Git for local branch validation or changes.
---

# Naming branches

Check the repository's explicit branch-naming rules first. Follow them where
specified; otherwise use the defaults below, based on
[Conventional Branch 1.1.0](https://conventionalbranch.org/v1.1.0/spec.json).
Existing branch names alone do not override these defaults.

## Choose a name

Use `<type>/<description>`, choosing the type by the purpose of the whole
branch, not by copying a commit-message type:

| Type | Use for |
| --- | --- |
| `feature` | New features or enhancements |
| `fix` | Bug fixes |
| `hotfix` | Urgent production fixes |
| `release` | Release preparation |
| `chore` | Other maintenance, including dependencies, docs, CI, and refactoring |

* Fix the spellings to `feature`, not `feat`, and `fix`, not `bugfix`.
  Both alternatives are valid upstream, but this skill chooses one per purpose.
  Commit messages still use their own conventions, including `feat`.
* Use purpose prefixes by default. The upstream agent prefixes `ai`, `claude`,
  `codex`, `copilot`, and `cursor` are available only when the user or repository
  explicitly requests them; being an agent is not a reason to select one.
* Keep the description concise and specific, using lowercase ASCII letters,
  digits, and single hyphens between words. Dots are allowed between
  alphanumeric segments, not just in release versions. Neither hyphens nor
  dots may lead, trail, or touch another separator: reject `--`, `..`, `-.`,
  and `.-`. Do not add spaces, underscores, or additional slashes.
* When a supplied or established issue ID applies, put it first in the
  description: `ENG-123` becomes `eng-123`, GitHub issue #45 becomes `issue-45`.
  Do not invent an ID or require one when none is available.
* Trunk branches `main`, `master`, and `develop` stay unprefixed. Do not rename
  trunk or other repository-defined long-lived branches to fit a task name.

Examples: `feature/eng-123-add-login-page`, `fix/issue-45-header-overflow`,
`hotfix/payment-outage`, `release/v1.2.0`, `chore/upgrade-node-v20.11`.

## Validate and apply

1. For a naming suggestion or compliance check, return the name and any
   necessary correction without changing Git state. Distinguish upstream
   validity from this skill's preferred spellings when reviewing an alias.
2. Check the naming rules above and, when Git is available, run
   `git check-ref-format --branch <name>`. Git checks ref syntax, not the
   naming convention; a successful exit alone does not establish compliance.
3. Only create or rename when requested as part of the task. Inspect the
   current branch, worktree state, and existing local/remote branch names
   first. Use the requested base for creation; if it is unspecified, use the
   repository's documented base or clarify when the choice affects the work.
   Do not reset, stash, delete, or force-switch to make a name fit.
4. Create with `git switch -c <name> [<base>]`, or rename the current branch
   with `git branch -m <new-name>`. Do not force-overwrite an existing branch.
   A local rename preserves the worktree, commits, and upstream configuration.
   The local name can differ from its upstream name: renaming alone neither
   loses upstream tracking nor creates divergence. The remote branch and PR
   remain unchanged. Do not recommend committing or stashing just to rename.
   Before renaming a published branch or one with an open PR, explain that
   distinction and ask only for confirmation of the local rename. If
   publication status is unknown, do not assume it is local-only. Remote
   migration is a separate task: do not offer or execute push, remote deletion,
   or PR recreation as part of a naming-only request.
5. After a requested change, confirm the resulting name with
   `git branch --show-current` and report it.
