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
ANCESTOR=$(mktemp -d)
WORK=$(cd "$WORK" && pwd -P)
ANCESTOR=$(cd "$ANCESTOR" && pwd -P)
trap 'rm -rf "$WORK" "$ANCESTOR"' EXIT
REVISION_A=aaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa
REVISION_B=bbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbb
REVISION_64=ffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffff
DIGEST_A=cccccccccccccccccccccccccccccccccccccccccccccccccccccccccccccccc
DIGEST_B=dddddddddddddddddddddddddddddddddddddddddddddddddddddddddddddddd
DIGEST_C=eeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeee

# RED: Task 2 must provide this state helper. Each invocation is a new process,
# so the latch must be persisted rather than held only in memory.
[[ -x "$STATE" ]] || { "$STATE" check "$WORK" "$TASK_ID"; }
CANONICAL_STATE_ROOT="$WORK/.engineering/fast-path"
initial=$($STATE check "$CANONICAL_STATE_ROOT" "$TASK_ID") || fail 'initial state failed'
[[ "$initial" == unclassified ]] || fail "initial state: $initial"
[[ -d "$WORK/.engineering" && -d "$CANONICAL_STATE_ROOT" ]] || fail 'first check did not create missing parent and state root'

$STATE record "$CANONICAL_STATE_ROOT" "$TASK_ID" eligible "$REVISION_A" "$DIGEST_A" \
  || fail 'eligible record failed'
! $STATE check "$CANONICAL_STATE_ROOT" "$TASK_ID" >/dev/null 2>&1 \
  || fail 'eligible state did not require an expected revision'
! $STATE check "$CANONICAL_STATE_ROOT" "$TASK_ID" "$REVISION_B" >/dev/null 2>&1 \
  || fail 'eligible state accepted a stale revision'
eligible=$($STATE check "$CANONICAL_STATE_ROOT" "$TASK_ID" "$REVISION_A") || fail 'eligible state check failed'
[[ "$eligible" == eligible ]] || fail "eligible state: $eligible"
$STATE record "$CANONICAL_STATE_ROOT" "$TASK_ID" eligible "$REVISION_A" "$DIGEST_A" \
  || fail 'exact eligible record was not idempotent'
! $STATE record "$CANONICAL_STATE_ROOT" "$TASK_ID" eligible "$REVISION_A" "$DIGEST_B" >/dev/null 2>&1 \
  || fail 'eligible state accepted a changed digest'
! $STATE record "$CANONICAL_STATE_ROOT" "$TASK_ID" eligible "$REVISION_B" "$DIGEST_A" >/dev/null 2>&1 \
  || fail 'eligible state accepted a changed revision'

$STATE record "$CANONICAL_STATE_ROOT" "revision64-$TASK_ID" eligible "$REVISION_64" "$DIGEST_A" \
  || fail '64-character revision record failed'
eligible64=$($STATE check "$CANONICAL_STATE_ROOT" "revision64-$TASK_ID" "$REVISION_64") \
  || fail '64-character revision state check failed'
[[ "$eligible64" == eligible ]] || fail "64-character eligible state: $eligible64"

$STATE record "$CANONICAL_STATE_ROOT" "$TASK_ID" disqualified 'unexpected consumer' "$DIGEST_C" \
  || fail 'disqualified record failed'
disqualified=$($STATE check "$CANONICAL_STATE_ROOT" "$TASK_ID") || fail 'disqualified state check failed'
[[ "$disqualified" == disqualified ]] || fail "disqualified state: $disqualified"

! $STATE record "$CANONICAL_STATE_ROOT" "$TASK_ID" eligible "$REVISION_A" "$DIGEST_A" \
  || fail 'disqualified state accepted a later eligible record'
persisted=$($STATE check "$CANONICAL_STATE_ROOT" "$TASK_ID") || fail 'persisted state check failed'
[[ "$persisted" == disqualified ]] || fail "persisted state: $persisted"

mkdir "$ANCESTOR/real"
ln -s "$ANCESTOR/real" "$ANCESTOR/linked"
! $STATE check "$ANCESTOR/linked/state-root" "$TASK_ID" >/dev/null 2>&1 \
  || fail 'state root with an ancestor symlink was accepted'
ln -s "$ANCESTOR/real" "$ANCESTOR/root-link"
! $STATE check "$ANCESTOR/root-link" "$TASK_ID" >/dev/null 2>&1 \
  || fail 'state root symlink was accepted'

printf 'PASS: fast-path routing regression checks\n'
