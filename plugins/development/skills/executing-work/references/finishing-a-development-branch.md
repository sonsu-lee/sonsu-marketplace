# Finishing a Development Branch

## Overview

**Core principle:** Verify tests → Detect environment → Present options →
Execute choice → Clean up. This branch applies when the user asks what to do
with the work. Otherwise keep it as-is and report the implementation result.

## Step 1: Verify Tests

Use the assigned verifier's evidence for the final target. If required checks
failed or were not run, report that; do not present the result as ready to
integrate. A green run only proves the tree it ran on.

## Step 2: Detect Environment

For a requested integration assessment or workspace operation, load
`git:managing-worktrees` before inspecting Git state. Use it to distinguish a
normal checkout, named-branch worktree, and detached, host-managed workspace.
If the user requested only a commit or PR, use `git:writing-commits` or
`git:writing-pull-requests`, respectively. A PR draft is not a publication.

## Step 3: Determine Base Branch

The base branch is whatever this work forked from. Confirm it from the plan,
conversation or repository before proposing a merge. Do not assume `main`.

## Step 4: Present Options

When a choice is needed, offer only options appropriate to the environment:
keep the work as-is, merge locally into the confirmed base, or publish a
branch and open a PR. A detached workspace is not a named branch to merge.
Do not offer to discard work. The integration decision is the user's.

## Step 5: Execute Choice

Follow the owning Git skill for the requested operation. Confirm its target
and side effects; permission to assess or draft does not permit committing,
merging, pushing or posting. A failed check on the merged result invalidates
the readiness claim: stop and investigate, leaving the work recoverable.

## Step 6: Cleanup Workspace

Leave host-managed or user-owned workspaces in place. Cleanup, branch
deletion and discarding changes need specific authorization and confirmed
ownership. If removal would lose uncommitted or untracked files, report what
is at risk and wait for the user's choice; never force cleanup by default.

Adapted from [Finishing a Development Branch][upstream] (MIT). Git skills
own integration and cleanup; finishing never grants authority to act.

[upstream]: https://github.com/obra/superpowers/blob/22f0b463e7a5e579904dd6211a520321035526f7/skills/finishing-a-development-branch/SKILL.md
