#!/usr/bin/env bash
set -euo pipefail

ROOT=$(cd "$(dirname "$0")/../../../../.." && pwd)
STATE="$ROOT/plugins/engineering/skills/brainstorming/scripts/fast-path-state"

fail() { printf 'FAIL: %s\n' "$1" >&2; exit 1; }

TASK_ID="fast-path-$$"
EXECUTION_A="execution-a-$$"
EXECUTION_B="execution-b-$$"
WORK=$(mktemp -d)
ANCESTOR=$(mktemp -d)
WORK=$(cd "$WORK" && pwd -P)
ANCESTOR=$(cd "$ANCESTOR" && pwd -P)
trap 'rm -rf "$WORK" "$ANCESTOR"' EXIT
STATE_ROOT="$WORK/.engineering/fast-path"

[[ -x "$STATE" ]] || fail 'fast-path-state is not executable'

git -C "$WORK" init -q
printf 'committed content\n' > "$WORK/dirty-file"
git -C "$WORK" add dirty-file
git -C "$WORK" -c user.name=FastPathTest -c user.email=fast-path@example.invalid \
  commit -qm 'test fixture'
HEAD_BEFORE=$(git -C "$WORK" rev-parse HEAD)

# A positive controller assessment is never a reusable state verdict. Even with
# an unchanged HEAD and only dirty-file drift, a new execution must escalate.
active=$($STATE begin "$STATE_ROOT" "$TASK_ID" "$EXECUTION_A") || fail 'initial begin failed'
[[ "$active" == active ]] || fail "initial begin: $active"
search_one=$($STATE reserve "$STATE_ROOT" "$TASK_ID" "$EXECUTION_A" search) || fail 'first search reservation failed'
[[ "$search_one" == search=1 ]] || fail "first search reservation: $search_one"
printf 'dirty worktree content\n' > "$WORK/dirty-file"
HEAD_AFTER=$(git -C "$WORK" rev-parse HEAD)
[[ "$HEAD_AFTER" == "$HEAD_BEFORE" ]] || fail 'dirty-file edit unexpectedly changed HEAD'
[[ -n "$(git -C "$WORK" status --porcelain -- dirty-file)" ]] || fail 'dirty-file fixture is not dirty'
resumed=$($STATE begin "$STATE_ROOT" "$TASK_ID" "$EXECUTION_B") || fail 'resumed begin failed'
[[ "$resumed" == disqualified ]] || fail "resumed task: $resumed"
! rg -q '^status=eligible$|^verdict=eligible$' "$STATE_ROOT/$TASK_ID.state" \
  || fail 'state persisted reusable eligibility'

# Disqualification is permanent across executions.
persisted=$($STATE begin "$STATE_ROOT" "$TASK_ID" "$EXECUTION_A") || fail 'persisted disqualification check failed'
[[ "$persisted" == disqualified ]] || fail "persisted disqualification: $persisted"
! $STATE reserve "$STATE_ROOT" "$TASK_ID" "$EXECUTION_A" action >/dev/null 2>&1 \
  || fail 'disqualified task accepted an action reservation'

# Explicit disqualification also latches permanently.
DISQUALIFIED_TASK="disqualified-$TASK_ID"
$STATE begin "$STATE_ROOT" "$DISQUALIFIED_TASK" "$EXECUTION_A" >/dev/null || fail 'disqualification setup failed'
latched=$($STATE disqualify "$STATE_ROOT" "$DISQUALIFIED_TASK" "$EXECUTION_A" 'unknown consumer') \
  || fail 'explicit disqualification failed'
[[ "$latched" == disqualified ]] || fail "explicit disqualification: $latched"
again=$($STATE begin "$STATE_ROOT" "$DISQUALIFIED_TASK" "$EXECUTION_B") || fail 'latched begin failed'
[[ "$again" == disqualified ]] || fail "latched begin: $again"

# Search budget is task-wide: two reservations succeed, the third fails and
# permanently disqualifies the task.
SEARCH_TASK="search-budget-$TASK_ID"
$STATE begin "$STATE_ROOT" "$SEARCH_TASK" "$EXECUTION_A" >/dev/null || fail 'search budget setup failed'
[[ "$($STATE reserve "$STATE_ROOT" "$SEARCH_TASK" "$EXECUTION_A" search)" == search=1 ]] \
  || fail 'first search was not reserved'
[[ "$($STATE reserve "$STATE_ROOT" "$SEARCH_TASK" "$EXECUTION_A" search)" == search=2 ]] \
  || fail 'second search was not reserved'
! $STATE reserve "$STATE_ROOT" "$SEARCH_TASK" "$EXECUTION_A" search >/dev/null 2>&1 \
  || fail 'third search exceeded the budget without failing'
[[ "$($STATE begin "$STATE_ROOT" "$SEARCH_TASK" "$EXECUTION_A")" == disqualified ]] \
  || fail 'search budget exhaustion did not latch disqualification'

# One initial implementation and one focused correction are valid in the same
# uninterrupted execution. A third action exhausts the budget and latches.
ACTION_TASK="action-budget-$TASK_ID"
$STATE begin "$STATE_ROOT" "$ACTION_TASK" "$EXECUTION_A" >/dev/null || fail 'action budget setup failed'
[[ "$($STATE reserve "$STATE_ROOT" "$ACTION_TASK" "$EXECUTION_A" action)" == action=1 ]] \
  || fail 'initial implementation was not reserved'
printf 'known local edit\n' >> "$WORK/dirty-file"
[[ "$($STATE reserve "$STATE_ROOT" "$ACTION_TASK" "$EXECUTION_A" action)" == action=2 ]] \
  || fail 'focused correction was not reserved'
! $STATE reserve "$STATE_ROOT" "$ACTION_TASK" "$EXECUTION_A" action >/dev/null 2>&1 \
  || fail 'third action exceeded the budget without failing'
[[ "$($STATE begin "$STATE_ROOT" "$ACTION_TASK" "$EXECUTION_A")" == disqualified ]] \
  || fail 'action budget exhaustion did not latch disqualification'

# Legacy v1 eligible state fails closed and is replaced by a v2 disqualified
# latch. It can never restore approval.
LEGACY_TASK="legacy-$TASK_ID"
mkdir -p "$STATE_ROOT"
cat > "$STATE_ROOT/$LEGACY_TASK.state" <<'EOF'
version=1
verdict=eligible
detail=aaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa
evidence_digest=cccccccccccccccccccccccccccccccccccccccccccccccccccccccccccccccc
EOF
legacy=$($STATE begin "$STATE_ROOT" "$LEGACY_TASK" "$EXECUTION_A") || fail 'legacy state handling failed'
[[ "$legacy" == disqualified ]] || fail "legacy state: $legacy"
rg -q '^version=2$' "$STATE_ROOT/$LEGACY_TASK.state" || fail 'legacy state was not migrated to a v2 latch'
rg -q '^status=disqualified$' "$STATE_ROOT/$LEGACY_TASK.state" || fail 'legacy state did not fail closed'
! $STATE reserve "$STATE_ROOT" "$LEGACY_TASK" "$EXECUTION_A" action >/dev/null 2>&1 \
  || fail 'legacy eligible state restored Fast Path execution'

# A v2 file with legacy keys in place of required counters is malformed and
# must fail closed rather than becoming an active budget record.
MALFORMED_TASK="malformed-$TASK_ID"
cat > "$STATE_ROOT/$MALFORMED_TASK.state" <<EOF
version=2
status=active
execution_id=$EXECUTION_A
verdict=eligible
detail=aaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa
reason=none
EOF
! $STATE begin "$STATE_ROOT" "$MALFORMED_TASK" "$EXECUTION_A" >/dev/null 2>&1 \
  || fail 'v2 state without required counters was accepted'

# Proportional path safety: reject unsafe identifiers and symlinked roots.
! $STATE begin "$STATE_ROOT" '../unsafe' "$EXECUTION_A" >/dev/null 2>&1 \
  || fail 'unsafe task ID was accepted'
! $STATE begin "$STATE_ROOT" "$TASK_ID" '../unsafe' >/dev/null 2>&1 \
  || fail 'unsafe execution ID was accepted'
mkdir "$ANCESTOR/real"
ln -s "$ANCESTOR/real" "$ANCESTOR/linked"
! $STATE begin "$ANCESTOR/linked/state-root" "$TASK_ID" "$EXECUTION_A" >/dev/null 2>&1 \
  || fail 'state root with an ancestor symlink was accepted'
ln -s "$ANCESTOR/real" "$ANCESTOR/root-link"
! $STATE begin "$ANCESTOR/root-link" "$TASK_ID" "$EXECUTION_A" >/dev/null 2>&1 \
  || fail 'state root symlink was accepted'

printf 'PASS: fast-path state regression checks\n'
