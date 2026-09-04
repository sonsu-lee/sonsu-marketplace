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

# Check directed DOT reachability (not a direct-edge/string grep).
python3 - "$SKILL" <<'PY'
import re,sys
from collections import defaultdict,deque
s=open(sys.argv[1]).read(); g=defaultdict(list)
for a,b in re.findall(r'^\s*"([^"]+)"\s*->\s*"([^"]+)"',s,re.M): g[a].append(b)
def reach(a,b):
 q=deque([a]); seen={a}
 while q:
  n=q.popleft()
  if n==b:return True
  for x in g[n]:
   if x not in seen: seen.add(x);q.append(x)
 return False
c=next((x for x in g if 'classifier' in x.lower()),None); p=next((x for x in g if 'All Fast Path predicates confirmed?' in x),None); e=next((x for x in g if 'Run bounded Fast Path' in x),None); h=next((x for x in g if 'Hidden complexity during Fast Path?' in x),None)
assert c and p and e and h,'required DOT nodes absent'
assert reach(c,p) and reach(c,e),'classifier does not precede execution'
assert not reach(h,p) and not reach(h,e),'escalation re-enters Fast Path'
PY

TASK_ID="red-routing-$$"
WORK=$(mktemp -d)
trap 'rm -rf "$WORK"' EXIT

# RED: Task 2 must provide this state helper. Each invocation is a new process,
# so the latch must be persisted rather than held only in memory.
[[ -x "$STATE" ]] || { "$STATE" check "$WORK" "$TASK_ID"; }
initial=$($STATE check "$WORK" "$TASK_ID") || fail 'initial state failed'
[[ "$initial" == unclassified ]] || fail "initial state: $initial"

$STATE record "$WORK" "$TASK_ID" eligible candidate-rev classifier-digest \
  || fail 'eligible record failed'
eligible=$($STATE check "$WORK" "$TASK_ID") || fail 'eligible state check failed'
[[ "$eligible" == eligible ]] || fail "eligible state: $eligible"

$STATE record "$WORK" "$TASK_ID" disqualified 'unexpected consumer' escalation-digest \
  || fail 'disqualified record failed'
disqualified=$($STATE check "$WORK" "$TASK_ID") || fail 'disqualified state check failed'
[[ "$disqualified" == disqualified ]] || fail "disqualified state: $disqualified"

! $STATE record "$WORK" "$TASK_ID" eligible candidate-rev classifier-digest \
  || fail 'disqualified state accepted a later eligible record'
persisted=$($STATE check "$WORK" "$TASK_ID") || fail 'persisted state check failed'
[[ "$persisted" == disqualified ]] || fail "persisted state: $persisted"

printf 'PASS: fast-path routing regression checks\n'
