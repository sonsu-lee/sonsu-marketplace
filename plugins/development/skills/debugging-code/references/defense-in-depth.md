# Defense-in-Depth Validation

## Overview

When you fix a bug caused by invalid data, adding validation at one place
feels sufficient. But that single check can be bypassed by different code
paths, refactoring, or mocks. Trace the paths that can actually reach the
operation before deciding where validation belongs.

## The Four Layers

### Layer 1: Entry Point Validation

**Purpose:** Reject obviously invalid input at the API boundary. In the
upstream example, the entry point rejects an empty or missing working
directory instead of treating it as the current working directory.

### Layer 2: Business Logic Validation

**Purpose:** Ensure data makes sense for this operation. Can a caller
legitimately reach it without passing through the first entry point?

### Layer 3: Environment Guards

**Purpose:** Prevent dangerous operations in specific contexts. For a test
that initializes a repository, establish that the resolved working directory
belongs to the authorized disposable location before acting. A shared string
prefix does not establish path containment.

### Layer 4: Debug Instrumentation

**Purpose:** Capture context for forensics. Where permitted, capture the
caller and relevant non-sensitive state before the operation, not afterward.

## Applying the Pattern

1. **Trace the data flow.** Where does the bad value originate? Where is it
   used?
2. **Map all checkpoints.** Which distinct callers, environments or trust
   boundaries bypass earlier checks?
3. **Validate at boundaries with distinct obligations.** Keep the smallest
   complete fix. Don't add identical checks at every call site by default.
4. **Test each relevant boundary.** Obtain approval before writing or
   changing a test. Use the failure the earlier boundary cannot catch.

## Example from Session

Empty `projectDir` caused `git init` in source code: test setup returned
an empty string, the project and workspace passed it along, and the git
process used the current working directory. Correct the setup invariant;
keep distinct environmental safeguards where a wrong directory would harm
other files.

Adapted from [Defense-in-Depth Validation][upstream] (MIT). Select distinct
reachable boundaries; four layers are an example, not an implementation quota.

[upstream]: https://github.com/obra/superpowers/blob/22f0b463e7a5e579904dd6211a520321035526f7/skills/systematic-debugging/defense-in-depth.md
