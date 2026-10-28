---
name: simplify-code
description: >-
  Simplify code when the user explicitly asks to remove unnecessary guards,
  branches, wrappers, or speculative machinery while preserving behavior.
  Trace TypeScript type information upstream before adding consumer checks.
  Not for ordinary feature implementation, read-only reviews, or repository-wide
  cleanup without a requested scope.
---

# Simplify code

Remove work and states the current contract does not need. Fewer lines, fewer
functions, and a preferred coding style are not evidence of improvement.
Preserve supported inputs, outputs, errors, side effects, and ownership.

## Establish what can actually happen

Read the requested code, its producers, consumers, public entry points, and
relevant checks. Distinguish a proven guarantee from an assumption based on one
caller. Include framework registration and mutation paths when they bear on the
candidate removal; do not audit unrelated code.

For each removal, identify the guarantee that makes the code unnecessary and
where that guarantee is established. An untested state is not an unreachable
state. If the required evidence is unavailable, keep the protection and report
what remains unknown rather than narrow the supported contract.

## Repair information loss at its owner

For TypeScript, locate where a known relationship became a broad type before
editing downstream guards. Inspect return annotations, intermediate containers,
and generic transformations. Preserve relationships between discriminants and
payloads, and between inputs and outputs, when the actual producers establish
them. Change the responsible type contract and affected consumers together.

Do not compensate for information lost upstream with repeated consumer guards.
Do not hide the loss with casts, non-null assertions, broad `any`, suppressed
compiler errors, or weaker checking options. A narrower declaration alone does
not prove the runtime value satisfies it.

A guard may still be necessary for external input, a missing lookup result,
a separate entry point, or mutable state. Static types do not validate network
responses, files, environment values, or values supplied by another process.
Keep validation at the boundary that owns these values. Before removing an
internal check, establish that no supported entry or mutation bypasses that
boundary.

## Make the smallest justified change

Prefer deletion, existing code, standard facilities, or direct control flow when
these preserve the contract. Remove the code made unused by the change.
A single caller is not enough reason to delete an abstraction: it may own a
resource, policy, framework boundary, or invariant. Similar-looking code is not
necessarily the same rule.

Preserve meaningful error translation and recovery, validation before mutation,
transaction boundaries, cancellation, and resource cleanup. Do not trade a
shorter expression for avoidable copying, repeated computation, or extra I/O.
Check the relevant language or library contract rather than assume an equivalent
spelling has equivalent behavior.

Do not add future options, swap dependencies, change public APIs, or clean up
unrelated code to make the requested change look simpler. When no unnecessary
work or state is established, leave the code unchanged and give the concrete
reason; do not invent a refactor to demonstrate activity.

## Verify and report

Use the project's existing type and behavior checks. Exercise the changed path,
including the reachable failures whose protection could have been removed.
Derive expected results from requirements and established contracts, not the
new implementation. A successful type check is not runtime evidence.

Report what unnecessary work or states were removed, the evidence for each
important removal, the guarantees retained, and checks actually exercised.
Separate missing evidence from observed failures. Do not claim that preserving
behavior alone proves the requested simplification was completed.

Use the host's existing task, delegation, session, and review facilities. This
skill adds no checkpoint storage, hooks, model policy, or permission to commit,
push, publish, or widen the user's request.
