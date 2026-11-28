# Root Cause Tracing

## Overview

Bugs often manifest deep in the call stack (git init in the wrong directory,
file created in the wrong location, database opened with the wrong path).
Your instinct is to fix where the error appears, but that's treating a symptom.

**Core principle:** Trace backward through the call chain until you find the
original trigger, then fix at the source.

## The Tracing Process

### 1. Observe the Symptom

```text
Error: git init failed in ~/project/packages/core
```

### 2. Find Immediate Cause

What code directly causes this?

```typescript
await execFileAsync('git', ['init'], { cwd: projectDir });
```

### 3. Ask: What Called This?

```text
WorktreeManager.createSessionWorktree(projectDir, sessionId)
  → called by Session.initializeWorkspace()
  → called by Session.create()
  → called by test at Project.create()
```

### 4. Keep Tracing Up

What value was passed?

- `projectDir = ''` (empty string!)
- The empty string as `cwd` resolves to `process.cwd()` in this example.
- That's the source code directory!

### 5. Find Original Trigger

Where did the empty string come from?

```typescript
const context = setupCoreTest(); // Returns { tempDir: '' }
Project.create('name', context.tempDir); // Accessed before beforeEach!
```

## Adding Stack Traces

When you can't trace manually, use existing traces first. If instrumentation
is authorized, capture the stack before the problematic operation, along with
the relevant, non-sensitive inputs. Look for a repeated caller, parameter or
test setup. Avoid dumping environment variables, secrets or private data.

## Finding Which Test Causes Pollution

If something appears during tests but you don't know which test, use the
project runner's test selection in a permitted disposable environment. Stop
at the first triggering test. Do not run a test that writes into the real
checkout just to confirm the user's report.

## Real Example: Empty projectDir

**Root cause:** Top-level variable initialization accessing an empty value.
**Fix:** Made tempDir a getter that throws if accessed before beforeEach.
Checking only the git operation would have missed the broken setup contract.

Adapted from [Root Cause Tracing][upstream] (MIT). Use authorized observations
and the existing runner rather than installing a test bisection script.

[upstream]: https://github.com/obra/superpowers/blob/22f0b463e7a5e579904dd6211a520321035526f7/skills/systematic-debugging/root-cause-tracing.md
