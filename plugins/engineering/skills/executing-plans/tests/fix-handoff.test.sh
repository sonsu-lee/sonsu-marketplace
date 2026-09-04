#!/usr/bin/env bash
set -euo pipefail

ROOT=$(cd "$(dirname "$0")/../../../../.." && pwd)
HELPER="$ROOT/plugins/engineering/skills/executing-plans/scripts/fix-handoff"
WORK=$(mktemp -d)
trap 'rm -rf "$WORK"' EXIT

fail() { printf 'FAIL: %s\n' "$1" >&2; exit 1; }
if [[ ! -x "$HELPER" ]]; then
  "$HELPER" verify "$WORK/missing.bundle" deadbeef || exit 127
fi

assert_rejected() {
  if "$@" >/dev/null 2>&1; then
    fail "accepted invalid input: $*"
  fi
}

create_bundle() {
  "$HELPER" create \
    --brief "$1" \
    --artifact "$2" \
    --revision 76a0526195709caf2fe1102160d8a9ae72c39130 \
    --findings "$3" \
    --verification "$4" \
    --round "$5" \
    --output-dir "$WORK"
}

parse_bundle_path() { printf '%s\n' "$1" | sed -n 's/^Bundle: //p'; }
parse_bundle_digest() { printf '%s\n' "$1" | sed -n 's/^Revision: sha256://p'; }

printf 'brief\n' > "$WORK/brief"
printf 'artifact\n' > "$WORK/artifact"

CASES="$WORK/cases"
mkdir -p "$CASES"
python3 - "$CASES" <<'PY'
import copy
import json
import os
import sys

out = sys.argv[1]
forbidden = [
    "severity", "verdict", "reviewer", "agent", "cause", "rationale",
    "suggested_fix", "recommendation", "status", "conclusion", "authority",
]
finding = {
    "schema": "finding-evidence.v1",
    "findings": [{
        "id": "F1", "observed_mismatch": "x", "expected_contract": "y",
        "artifact_locations": ["a"], "reproduction": "r", "raw_evidence": "e",
        "unknowns": [],
    }],
}
verification = {
    "schema": "verification-evidence.v1",
    "checks": [{
        "command": "true", "exit_code": 0, "output_reference": "o",
        "observed_result": "pass",
    }],
    "unknowns": [],
}

def write(kind, name, value):
    directory = os.path.join(out, kind)
    os.makedirs(directory, exist_ok=True)
    with open(os.path.join(directory, name), "w") as handle:
        json.dump(value, handle)
        handle.write("\n")

def make_cases(kind, base, array_key, item_keys):
    write(kind, "valid.json", base)
    for key in base:
        value = copy.deepcopy(base)
        del value[key]
        write(kind, f"missing-envelope-{key}.json", value)
    for key in item_keys:
        value = copy.deepcopy(base)
        del value[array_key][0][key]
        write(kind, f"missing-item-{key}.json", value)
    value = copy.deepcopy(base)
    value["schema"] = []
    write(kind, "wrong-envelope-scalar.json", value)
    value = copy.deepcopy(base)
    value[array_key] = {}
    write(kind, "wrong-envelope-array.json", value)
    value = copy.deepcopy(base)
    value[array_key] = [False]
    write(kind, "wrong-item-object.json", value)
    value = copy.deepcopy(base)
    value[array_key][0][item_keys[0]] = []
    write(kind, "wrong-item-scalar.json", value)
    for scope in ("envelope", "item"):
        value = copy.deepcopy(base)
        target = value if scope == "envelope" else value[array_key][0]
        target["unexpected"] = "blocked"
        write(kind, f"unknown-{scope}.json", value)
        for key in forbidden:
            value = copy.deepcopy(base)
            target = value if scope == "envelope" else value[array_key][0]
            target[key] = "blocked"
            write(kind, f"forbidden-{scope}-{key}.json", value)

make_cases("findings", finding, "findings", list(finding["findings"][0]))
value = copy.deepcopy(finding)
value["findings"][0]["artifact_locations"] = "a"
write("findings", "wrong-item-array.json", value)
value = copy.deepcopy(finding)
value["findings"][0]["unknowns"] = {}
write("findings", "wrong-item-unknowns-array.json", value)

make_cases("verification", verification, "checks", list(verification["checks"][0]))
value = copy.deepcopy(verification)
value["unknowns"] = {}
write("verification", "wrong-envelope-unknowns-array.json", value)
value = copy.deepcopy(verification)
value["checks"][0]["exit_code"] = "zero"
write("verification", "wrong-item-exit-code.json", value)

for kind in ("findings", "verification"):
    with open(os.path.join(out, kind, "malformed.json"), "w") as handle:
        handle.write('{"schema":')
    open(os.path.join(out, kind, "empty.json"), "w").close()
PY

for schema in findings verification; do
  validator="validate-$schema"
  "$HELPER" "$validator" "$CASES/$schema/valid.json" \
    || fail "valid $schema evidence was rejected"
  for invalid in "$CASES/$schema"/*.json; do
    [[ "$(basename "$invalid")" == valid.json ]] && continue
    assert_rejected "$HELPER" "$validator" "$invalid"
  done
done

FINDINGS="$CASES/findings/valid.json"
VERIFICATION="$CASES/verification/valid.json"
for input in brief artifact findings verification; do
  missing="$WORK/missing-$input"
  empty="$WORK/empty-$input"
  : > "$empty"
  case "$input" in
    brief)
      assert_rejected create_bundle "$missing" "$WORK/artifact" "$FINDINGS" "$VERIFICATION" 2
      assert_rejected create_bundle "$empty" "$WORK/artifact" "$FINDINGS" "$VERIFICATION" 2 ;;
    artifact)
      assert_rejected create_bundle "$WORK/brief" "$missing" "$FINDINGS" "$VERIFICATION" 2
      assert_rejected create_bundle "$WORK/brief" "$empty" "$FINDINGS" "$VERIFICATION" 2 ;;
    findings)
      assert_rejected create_bundle "$WORK/brief" "$WORK/artifact" "$missing" "$VERIFICATION" 2
      assert_rejected create_bundle "$WORK/brief" "$WORK/artifact" "$empty" "$VERIFICATION" 2 ;;
    verification)
      assert_rejected create_bundle "$WORK/brief" "$WORK/artifact" "$FINDINGS" "$missing" 2
      assert_rejected create_bundle "$WORK/brief" "$WORK/artifact" "$FINDINGS" "$empty" 2 ;;
  esac
done

# The helper contract is exact-key, immutable, digest-bound, and accepts only
# round 2/3 evidence. Each create output exposes an exact path/digest pair.
create1=$(create_bundle "$WORK/brief" "$WORK/artifact" "$FINDINGS" "$VERIFICATION" 2)
bundle1=$(parse_bundle_path "$create1")
digest1=$(parse_bundle_digest "$create1")
[[ -n "$bundle1" && -n "$digest1" ]] || fail 'create did not emit Bundle and Revision fields'
[[ -d "$bundle1" ]] || fail "bundle path is not a directory: $bundle1"
"$HELPER" verify "$bundle1" "$digest1" || fail 'first exact bundle/digest pair failed verification'

create2=$(create_bundle "$WORK/brief" "$WORK/artifact" "$FINDINGS" "$VERIFICATION" 3)
bundle2=$(parse_bundle_path "$create2")
digest2=$(parse_bundle_digest "$create2")
[[ -n "$bundle2" && -n "$digest2" ]] || fail 'second create did not emit Bundle and Revision fields'
[[ "$bundle1" != "$bundle2" ]] || fail 'separate creates reused a bundle path'
"$HELPER" verify "$bundle2" "$digest2" || fail 'second exact bundle/digest pair failed verification'

cp -R "$bundle1" "$WORK/tampered.bundle"
tampered_file=$(find "$WORK/tampered.bundle" -type f -print -quit)
[[ -n "$tampered_file" ]] || fail 'copied bundle has no file to tamper'
printf 'tampered\n' >> "$tampered_file"
assert_rejected "$HELPER" verify "$WORK/tampered.bundle" "$digest1"
"$HELPER" verify "$bundle1" "$digest1" || fail 'original bundle changed after copy tampering'

for round in 2 3; do
  create_bundle "$WORK/brief" "$WORK/artifact" "$FINDINGS" "$VERIFICATION" "$round" >/dev/null \
    || fail "round $round was rejected"
done
for round in 0 1 4 -1 two ''; do
  assert_rejected create_bundle "$WORK/brief" "$WORK/artifact" "$FINDINGS" "$VERIFICATION" "$round"
done

printf 'PASS: fix-handoff evidence regression checks\n'
