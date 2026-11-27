# Condition-Based Waiting

## Overview

Flaky tests often guess at timing with arbitrary delays. This creates race
conditions where tests pass on fast machines but fail under load or in CI.

**Core principle:** Wait for the actual condition you care about, not a guess
about how long it takes.

## When to Use

- Tests have arbitrary delays (`setTimeout`, `sleep`, `time.sleep()`).
- Tests are flaky (pass sometimes, fail under load).
- Waiting for async operations to complete.

Do not replace a timing assertion when timing is the contract (debounce,
throttle intervals). Document why the interval matters.

## Core Pattern

```typescript
// BEFORE: Guessing at timing
await new Promise(r => setTimeout(r, 50));
const result = getResult();
expect(result).toBeDefined();

// AFTER: Waiting for condition
await waitFor(() => getResult() !== undefined);
const result = getResult();
expect(result).toBeDefined();
```

This example concerns readiness. Assert the approved observable outcome as
well; checking only that some result exists is not a behavior specification.

## Quick Patterns

| Scenario | Condition |
| --- | --- |
| Wait for event | A matching completion event has arrived. |
| Wait for state | The machine reached the expected public state. |
| Wait for count | Enough results to evaluate the behavior have arrived. |
| Wait for file | The expected artifact exists and is ready for use. |

## Implementation

Prefer the framework's existing event or bounded wait primitive. Get fresh
state inside the wait. A deadline should name the unmet condition when it
expires. Avoid allocating a second polling helper for a one-off check.

## When Arbitrary Timeout IS Correct

1. First wait for the triggering condition.
2. Base the interval on known timing (not guessing).
3. Comment explaining WHY: e.g. two ticks of 100 ms are required to show
   partial output. A controllable clock is preferable when it exercises the
   same interface.

Adapted from [Condition-Based Waiting][upstream] (MIT). Prefer the existing
framework primitive to the upstream example's custom polling helper.

[upstream]: https://github.com/obra/superpowers/blob/22f0b463e7a5e579904dd6211a520321035526f7/skills/systematic-debugging/condition-based-waiting.md
