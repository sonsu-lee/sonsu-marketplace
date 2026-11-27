---
name: debugging-code
description: >-
  Use when encountering a bug, test failure, or unexpected behavior, before
  proposing fixes. Investigation alone does not authorize edits.
license: MIT
metadata:
  source: https://github.com/obra/superpowers
  source-commit: 22f0b463e7a5e579904dd6211a520321035526f7
---

# Systematic Debugging

## Overview

**Core principle:** ALWAYS find root cause before attempting fixes. Symptom
fixes are failure.

For code investigation, including diagnosis without a fix, load
`ponytail:ponytail` **before** reading code,
tests, reports or other task material. Load `tdd:test-driven-development`
before inspecting the target if a behavior fix or test change is requested. Use
the host's installed
skill mechanism. Explicit native-only instructions take precedence: follow
the native procedure alone. If a required integrated skill is unavailable,
stop before inspecting its target; never suggest native-only as a bypass.

## The Iron Law

```text
NO FIXES WITHOUT ROOT CAUSE INVESTIGATION FIRST
```

If you haven't completed Phase 1, you cannot propose fixes. Investigation
only permits read-only observations: prevent incidental writes from tools
(caches, bytecode, logs) or use an authorized disposable copy. Preserve the
source, index and untracked state.

## When to Use

Use for test failures, bugs in production, unexpected behavior, performance
problems, build failures and integration issues. Use this especially when
"just one quick fix" seems obvious or a previous fix didn't work.

## The Four Phases

Complete each phase before proceeding to the next.

### Phase 1: Root Cause Investigation

**BEFORE attempting ANY fix:**

1. **Read Error Messages Carefully**
   - Don't skip past errors or warnings.
   - Read stack traces completely. Note line numbers, file paths, error codes.
2. **Reproduce Consistently**
   - What are the exact steps? Does it happen every time?
   - The user's reported observation is evidence. If the host or user forbids
     rerunning it, start from the report and existing traces. Reproduce only
     when safe, permitted and needed to distinguish causes.
   - If not reproducible, gather more data; don't guess.
3. **Check Recent Changes**
   - What changed that could cause this? Check relevant changes, dependencies,
     config and environmental differences.
4. **Gather Evidence in Multi-Component Systems**
   - At each relevant boundary, compare what enters the component, what
     exits, how config propagates and what state each layer observes.
   - Use existing traces first. Add instrumentation only if writes are
     authorized; never expose credentials or private payloads in logs.
   - Identify WHERE it breaks, then investigate that specific component.
5. **Trace Data Flow**
   - Where does the bad value originate? What called this with the bad value?
   - When the error is deep in the call stack, read
     [Root Cause Tracing](references/root-cause-tracing.md). Keep tracing up
     until you find the source. Fix at source, not at symptom.

### Phase 2: Pattern Analysis

**Find the pattern before fixing:**

1. **Find Working Examples.** Locate similar working code in the same
   codebase. What works that's similar to what's broken?
2. **Compare Against References.** If implementing a pattern, read its
   reference implementation completely. Understand it before applying it.
3. **Identify Differences.** What's different between working and broken?
   List every relevant difference, however small. Don't assume that it
   can't matter.
4. **Understand Dependencies.** What other components does this need? What
   settings, config, environment? What assumptions does it make?

### Phase 3: Hypothesis and Testing

**Scientific method:**

1. **Form Single Hypothesis.** State clearly: "I think X is the root cause
   because Y." Name the evidence that would distinguish X from another cause.
2. **Test Minimally.** Make the smallest permitted observation that tests the
   hypothesis. One variable at a time. Don't fix multiple things at once.
3. **Verify Before Continuing.** Did it work? Yes → Phase 4 if fixing is
   authorized. Didn't work? Form a NEW hypothesis. DON'T add more fixes on top.
4. **When You Don't Know.** Say "I don't understand X." Identify which
   observation would resolve it. Do not pretend to know.

**Investigation-only stop:** Return the evidence, cause and remaining
uncertainty without writing files. Investigation does not authorize a fix.

### Phase 4: Implementation

For an authorized fix, load `development:executing-work` before modifying
code. **Fix the root cause, not the symptom:**

1. **Create Failing Test Case.** Reuse a check that already demonstrates
   the failure. Before writing or changing a test, obtain explicit approval
   of the test specification under `tdd:test-driven-development`. An approved
   plan containing it counts. If the interface or expected behavior changes,
   reconfirm the affected specification first. Follow RED → GREEN → REFACTOR
   for one approved behavior at a time; coordinate checks with their owner.
2. **Implement Single Fix.** Address the root cause identified. ONE change
   at a time. No "while I'm here" improvements. No bundled refactoring.
3. **Verify Fix.** Does the test pass now? Issue actually resolved? Have
   the assigned verifier exercise the original consumer-visible path after
   the fix when permitted. Follow the execution skill's verification and
   independent final review. Missing evidence or review is not a pass.
4. **If Fix Doesn't Work.** STOP. Count: How many fixes have you tried?
   If fewer than three, return to Phase 1 and re-analyze with new information.
   DON'T attempt Fix #4 without architectural discussion.
5. **If 3+ Fixes Failed: Question Architecture.** Does each fix reveal new
   shared state or coupling in a different place? Do fixes require massive
   refactoring? Is the pattern fundamentally sound? Discuss with your human
   partner before attempting more fixes; obtain approval for any broader
   architectural change.

## Supporting Techniques

- When guessing, repeatedly applying fixes, or unable to establish a local
  cause, read [Red Flags and Quick Reference](references/red-flags.md).
- When invalid input reaches the same operation through distinct boundaries,
  read [Defense-in-Depth Validation](references/defense-in-depth.md).
- When a test guesses when asynchronous work finishes, read
  [Condition-Based Waiting](references/condition-based-waiting.md).
