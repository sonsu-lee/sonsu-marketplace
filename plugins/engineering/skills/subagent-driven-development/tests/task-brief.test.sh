#!/usr/bin/env bash
set -euo pipefail

script=$(cd "$(dirname "$0")/../scripts" && pwd)/task-brief
fixture_dir=$(mktemp -d)
trap 'rm -rf "$fixture_dir"' EXIT

plan="$fixture_dir/plan.md"
brief="$fixture_dir/task-2-brief.md"

cat >"$plan" <<'PLAN'
# Example Implementation Plan

**Goal:** Preserve the behavior contract in each task brief.

## Global Constraints

- Keep exact values from the approved plan.

## Behavioral Flow Pseudocode

FLOW F1: Return a validated result
  INPUT: request
  IF request is invalid:
      RETURN validation error
  OUTPUT: validated result

```text
### Task 99: This fenced heading is not a plan task
```

## Flow Mapping

| Flow | Inputs and outcomes | Files and responsibilities | Task and dependencies | Verification and reason |
| --- | --- | --- | --- | --- |
| `F1` | request -> result | `src/service.ts`: validate | Task 2; after Task 1 | regression test; protects the contract |

### Task 1: Prepare the dependency

Task 1 details must not appear in Task 2's brief.

### Task 2: Implement validation

**Flows:** `F1`

Task 2 implementation details.

### Task 3: Update callers

Task 3 details must not appear in Task 2's brief.
PLAN

"$script" "$plan" 2 "$brief" >/dev/null

assert_contains() {
  local expected=$1
  grep -Fq -- "$expected" "$brief" || {
    echo "missing expected brief content: $expected" >&2
    exit 1
  }
}

assert_excludes() {
  local unexpected=$1
  if grep -Fq -- "$unexpected" "$brief"; then
    echo "unexpected brief content: $unexpected" >&2
    exit 1
  fi
}

assert_contains '# Example Implementation Plan'
assert_contains '## Global Constraints'
assert_contains '## Behavioral Flow Pseudocode'
assert_contains 'FLOW F1: Return a validated result'
assert_contains '## Flow Mapping'
assert_contains '### Task 2: Implement validation'
assert_contains 'Task 2 implementation details.'
assert_excludes 'Task 1 details must not appear'
assert_excludes 'Task 3 details must not appear'

if "$script" "$plan" 8 "$fixture_dir/missing.md" >"$fixture_dir/missing.stdout" 2>"$fixture_dir/missing.stderr"; then
  echo 'missing task unexpectedly succeeded' >&2
  exit 1
fi

grep -Fq "task 8 not found" "$fixture_dir/missing.stderr" || {
  echo 'missing task did not report the expected error' >&2
  exit 1
}

echo 'task-brief tests passed'
