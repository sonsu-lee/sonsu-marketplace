#!/usr/bin/env bash
set -euo pipefail

ROOT=$(cd "$(dirname "$0")/../../../../.." && pwd)
HELPER="$ROOT/plugins/engineering/skills/executing-plans/scripts/fix-handoff"
WORK=$(mktemp -d)
trap 'rm -rf "$WORK"' EXIT

fail() { printf 'FAIL: %s\n' "$1" >&2; exit 1; }
[[ -x "$HELPER" ]] || { "$HELPER" verify "$WORK/missing.bundle" deadbeef; }
printf 'brief\n' > "$WORK/brief"

printf '%s\n' '{"schema":"finding-evidence.v1","findings":[{"id":"F1","observed_mismatch":"x","expected_contract":"y","artifact_locations":["a"],"reproduction":"r","raw_evidence":"e","unknowns":[]}]}' > "$WORK/findings.json"
printf '%s\n' '{"schema":"verification-evidence.v1","checks":[{"command":"true","exit_code":0,"output_reference":"o","observed_result":"pass"}],"unknowns":[]}' > "$WORK/verification.json"
printf 'artifact\n' > "$WORK/artifact"

# The helper contract is exact-key, immutable, digest-bound, and accepts only
# round 2/3 evidence. These calls become GREEN when Task 3 supplies the helper.
bundle=$($HELPER create --brief "$WORK/brief" --artifact "$WORK/artifact" --revision 76a0526195709caf2fe1102160d8a9ae72c39130 --findings "$WORK/findings.json" --verification "$WORK/verification.json" --round 2 --output-dir "$WORK")
digest=$(printf '%s\n' "$bundle" | tail -n1)
[[ -n "$digest" ]] || fail 'bundle digest was not emitted'
$HELPER verify "$WORK" "$digest"
bundle2=$($HELPER create --brief "$WORK/brief" --artifact "$WORK/artifact" --revision 76a0526195709caf2fe1102160d8a9ae72c39130 --findings "$WORK/findings.json" --verification "$WORK/verification.json" --round 3 --output-dir "$WORK")
digest2=$(printf '%s\n' "$bundle2" | tail -n1)
[[ "$digest" != "$digest2" ]] || fail 'bundle paths/digests are not unique'
! $HELPER verify "$WORK" "$digest2" || fail 'wrong path/digest pairing accepted'
for round in 0 1 4; do ! $HELPER create --brief "$WORK/brief" --artifact "$WORK/artifact" --revision r --findings "$WORK/findings.json" --verification "$WORK/verification.json" --round "$round" --output-dir "$WORK" || fail "round $round accepted"; done

for key in suggested_fix verdict rationale authority unexpected; do
  sed "s/\"unknowns\":\[\]/\"$key\":\"blocked\",\"unknowns\":[]/" "$WORK/findings.json" > "$WORK/bad.json"
  ! $HELPER validate-findings "$WORK/bad.json" || fail "forbidden finding key accepted: $key"
done
for key in conclusion status unexpected; do
  sed "s/\"unknowns\":\[\]/\"$key\":\"blocked\",\"unknowns\":[]/" "$WORK/verification.json" > "$WORK/bad.json"
  ! $HELPER validate-verification "$WORK/bad.json" || fail "forbidden verification key accepted: $key"
done

printf 'PASS: fix-handoff evidence regression checks\n'
