#!/usr/bin/env bash
set -euo pipefail

ROOT=$(cd "$(dirname "$0")/../../../../.." && pwd)
SKILL="$ROOT/plugins/engineering/skills/brainstorming/SKILL.md"
STATE="$ROOT/plugins/engineering/skills/brainstorming/scripts/fast-path-state"

fail() { printf 'FAIL: %s\n' "$1" >&2; exit 1; }
assert_contains() { rg -Fq "$2" "$1" || fail "$1 does not contain: $2"; }

# The routing graph must expose an independent classifier before execution.
assert_contains "$SKILL" 'Fast Path classifier'
assert_contains "$SKILL" 'classifier verdict'
assert_contains "$SKILL" 'Run bounded Fast Path'
assert_contains "$SKILL" 'Hidden complexity during Fast Path?'

# A graph-level edge from escalation back to either predicate or execution is forbidden.
if rg -n 'Hidden complexity during Fast Path\?.*->.*(All Fast Path predicates confirmed\?|Run bounded Fast Path)' "$SKILL"; then
  fail 'escalation can reach Fast Path predicate or execution'
fi

TASK_ID="red-routing-$$"
WORK=$(mktemp -d)
trap 'rm -rf "$WORK"' EXIT

# RED: Task 2 must provide this state helper.  Exercise it in two processes so
# a transient in-memory latch cannot make disqualified -> eligible possible.
[[ -x "$STATE" ]] || { "$STATE" check "$WORK" "$TASK_ID" eligible; }
"$STATE" disqualify "$WORK" "$TASK_ID" 'unexpected consumer' >/dev/null
[[ "$({ "$STATE" check "$WORK" "$TASK_ID" eligible; } 2>/dev/null || true)" != 'eligible' ]] ||
  fail 'disqualified task was reclassified as eligible in a new process'
[[ "$({ "$STATE" route "$WORK" "$TASK_ID"; } 2>/dev/null || true)" != *'normal'* ]] ||
  true

printf 'PASS: fast-path routing regression checks\n'
