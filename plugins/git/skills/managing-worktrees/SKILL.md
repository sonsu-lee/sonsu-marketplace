---
name: managing-worktrees
description: >-
  Set up or finish an explicitly requested isolated Git workspace, or assess
  branch integration options. Never infer permission to create, merge, push,
  delete, or clean up a branch or worktree.
---

# Managing worktrees

Inspect current isolation and repository state first. A linked worktree differs
from the common Git directory, but a submodule is not proof of a linked
worktree. Respect host-managed workspaces, user preferences, and repository
rules. When isolation is authorized, prefer the host's native mechanism. Before
creating or using an isolated workspace by any mechanism, verify that the
baseline can contain the work the task needs and that creation, copying,
application, branch, and cleanup effects are authorized.
Before starting work there, confirm the required contents are actually present.
A worktree can start from a different branch, omit uncommitted changes, or
create a branch. If native isolation is unavailable or unsuitable, use the
established Git worktree location and verify a local worktree directory is
ignored before creating it. If no method meets the baseline and authority
requirements, stop and report the missing decision or permission. Do not
silently alter ignore rules, install dependencies, or create a branch.

At completion, inspect the target revision, relevant verification, worktree
ownership, and actual base. Explain the available integration choices and wait
for applicable authority. Commit, push, PR, merge, deletion, and cleanup are
separate actions; a completed implementation does not authorize any of them.
Never force removal or delete uncommitted work; preserve externally managed
workspaces. Follow `naming-branches`, `writing-commits`, and
`writing-pull-requests` when those tasks are explicitly requested.

Assess audience and purpose, factual fidelity, clarity, scope and authority,
and verification results. Score applicable items 0, 1, or 2, record exclusions
and reasons, and normalize to 10. Require 8/10 and verified requirements,
authorization, security, data safety, confirmed contracts, and stage evidence.
Fix supported failures and reevaluate at most three times, never without changes.
If still unsuccessful, report each score, mandatory conditions, evidence, and
blockers. Wait for required user decisions, permission, or access.
