# Red Flags - STOP and Follow Process

If you catch yourself thinking:

- "Quick fix for now, investigate later"
- "Just try changing X and see if it works"
- "Add multiple changes, run tests"
- "It's probably X, let me fix that"
- "I don't fully understand but this might work"
- "Here are the main problems: [lists fixes without investigation]"
- "One more fix attempt" (when already tried 2+)
- Each fix reveals a new problem in a different place.

**ALL of these mean: STOP. Return to Phase 1.** If three fixes failed,
question the architecture before trying another.

## Your Human Partner's Signals You're Doing It Wrong

- "Is that not happening?" — You assumed without verifying.
- "Will it show us...?" — Identify the evidence that discriminates causes.
- "Stop guessing" — You're proposing fixes without understanding.
- "We're stuck?" — Your approach isn't working.

## Common Rationalizations

- **“Just try this first, then investigate”** — First fix sets the pattern.
- **“Multiple fixes at once saves time”** — Can't isolate what worked.
- **“I see the problem, let me fix it”** — Seeing symptoms ≠ understanding
  root cause.

## Quick Reference

1. **Root Cause:** Read errors, check changes, gather evidence.
   Success: Understand WHAT and WHY.
2. **Pattern:** Find working examples, compare.
   Success: Identify differences.
3. **Hypothesis:** Form theory, test minimally.
   Success: Confirmed or new hypothesis.
4. **Implementation:** Approved test, fix, verify.
   Success: Bug resolved, tests pass.

## When Process Reveals “No Root Cause”

If investigation points to the environment, timing or an external component,
report what you investigated and the evidence distinguishing it from a local
cause. Name the next discriminating observation when the evidence is still
inconclusive. Retries, timeouts, error handling or monitoring are changes;
propose them only if they address the demonstrated failure and obtain any
needed authority before implementing them.

Adapted from the concluding sections of [Systematic Debugging][upstream]
(MIT). An unknown cause does not itself authorize changes.

[upstream]: https://github.com/obra/superpowers/blob/22f0b463e7a5e579904dd6211a520321035526f7/skills/systematic-debugging/SKILL.md
