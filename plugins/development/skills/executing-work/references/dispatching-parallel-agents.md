# Dispatching Parallel Agents

## Overview

When you have multiple unrelated failures (different test files, different
subsystems, different bugs), investigating them sequentially wastes time.
Each investigation is independent and can happen in parallel.

**Core principle:** Dispatch one agent per independent problem domain. Let
them work concurrently.

## When to Use

- Each problem can be understood without context from others.
- No shared state between investigations.
- No unfinished output from one task is an input to another.

## The Pattern

### 1. Identify Independent Domains

Group failures by what's broken: tool approval flow, batch completion behavior,
abort functionality. Are the failures related? Fixing one might fix others.
Investigate together first if the answer is not clear.

### 2. Create Focused Agent Tasks

Each agent gets:

- **Specific scope:** One test file or subsystem.
- **Clear goal:** Identify the cause or deliver the authorized correction.
- **Constraints:** File ownership, approved contract, allowed side effects
  and who runs checks. An investigation-only assignment does not allow fixes.
- **Expected output:** Evidence, what changed, and remaining uncertainty.

### 3. Dispatch in Parallel

Use the native dispatch interface for all independent assignments. Work on
other ready tasks while they run; use the host's result collection mechanism
when blocked. Never treat a dispatch as a completed result.

### 4. Review and Integrate

When agents return, read each summary. Verify fixes don't conflict. Confirm
all changes are present on the frozen integration target. Review the combined
result and have the assigned verifier exercise the actual affected paths.

## When NOT to Use

**Related failures:** Fixing one might fix others — investigate together first.
**Need full context:** Understanding requires seeing entire system state.
**Exploratory debugging:** You don't know what's broken yet.
**Shared state:** Agents would interfere (editing the same files, using the
same resources).

Adapted from [Dispatching Parallel Agents][upstream] (MIT). Use host dispatch,
disjoint ownership and assigned verification rather than assuming a particular
worker tool or requiring a full suite.

[upstream]: https://github.com/obra/superpowers/blob/22f0b463e7a5e579904dd6211a520321035526f7/skills/dispatching-parallel-agents/SKILL.md
