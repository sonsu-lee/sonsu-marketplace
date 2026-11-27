# Verification Before Completion

## Overview

**Core principle:** Evidence before claims, always.

## The Iron Law

```text
NO COMPLETION CLAIMS WITHOUT FRESH VERIFICATION EVIDENCE
```

Fresh means evidence for this claim on the target you are reporting. A new
message, a new stage or a second reviewer is not a reason to rerun an
unchanged check. A later source or test change invalidates evidence for the
paths it affects.

## The Gate Function

Before claiming work is complete, fixed or passing:

1. IDENTIFY: What command or consumer path proves this claim? What does the
   approved contract predict?
2. RUN: The assigned verifier runs the authorized, relevant check on the
   frozen target. Reuse matching evidence; never repeat a user-reported
   failure merely to confirm it when the host or user forbids that.
3. READ: Read the output, check the exit code, count failures.
4. VERIFY: Does output confirm the claim? If no, state actual status with
   evidence. If yes, state the claim with its evidence.
5. ONLY THEN: Make the claim. If verification is unavailable, report which
   path or condition remains unverified and why.

## Common Failures

- **Tests pass.** Requires named test command: zero failures.
  Not sufficient: earlier revision, “should pass”.
- **Build succeeds.** Requires build command: exit 0.
  Not sufficient: linter passing.
- **Bug fixed.** Requires observed original consumer path after the fix.
  Not sufficient: code changed.
- **Regression test works.** Requires expected RED, then GREEN.
  Not sufficient: test passes once.
- **Requirements met.** Requires observable results for each requirement.
  Not sufficient: green suite.
- **Delegated work verified.** Requires actual changes and matching evidence.
  Not sufficient: worker says “done”.

## Key Patterns

**Requirements:** Compare each approved outcome with observed results on the
real changed entry point or consumer path. A build, a test or a self-score
alone does not prove the integration works.

**Test gate:** If a declared gate blocks an action, inspect the declaration
and use its exact runner command only when authorized. A receipt records a
run on a tree, not test adequacy or action approval.

**Handoff:** When checks belong to another role, give that verifier the path,
command, expected result and revision. Say what was not run; do not perform
or claim somebody else's check. Never broaden a narrow pass into “all tests
pass” or present evidence from before a correction as proof of the fix.

Adapted from [Verification Before Completion][upstream] (MIT). Evidence is
bound to a claim and target, not to the message in which it was collected.

[upstream]: https://github.com/obra/superpowers/blob/22f0b463e7a5e579904dd6211a520321035526f7/skills/verification-before-completion/SKILL.md
