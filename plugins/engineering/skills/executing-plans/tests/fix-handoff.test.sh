#!/usr/bin/env bash
set -euo pipefail

ROOT=$(cd "$(dirname "$0")/../../../../.." && pwd)
HELPER="$ROOT/plugins/engineering/skills/executing-plans/scripts/fix-handoff"
WORK=$(mktemp -d)
trap 'rm -rf "$WORK"' EXIT
export TMPDIR="$WORK"

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
  create_bundle_with_revision "$(hash_bundle "$2")" "$@"
}

create_bundle_with_revision() {
  local revision=$1
  shift
  TMPDIR="$WORK" "$HELPER" create \
    --brief "$1" \
    --artifact "$2" \
    --revision "$revision" \
    --findings "$3" \
    --verification "$4" \
    --round "$5"
}

create_bundle_to() {
  create_bundle_to_with_revision "$(hash_bundle "$2")" "$@"
}

create_bundle_to_with_revision() {
  local revision=$1
  shift
  TMPDIR="$WORK" "$HELPER" create \
    --brief "$1" \
    --artifact "$2" \
    --revision "$revision" \
    --findings "$3" \
    --verification "$4" \
    --round "$5" \
    --output "$6"
}

parse_bundle_path() { printf '%s\n' "$1" | sed -n 's/^Bundle: //p'; }
parse_bundle_digest() { printf '%s\n' "$1" | sed -n 's/^Revision: sha256://p'; }
parse_extracted_path() { printf '%s\n' "$1" | sed -n 's/^Extracted: //p'; }
hash_bundle() { shasum -a 256 "$1" | awk '{print $1}'; }

assert_snapshot() {
  python3 - "$1" <<'PY'
import os
import stat
import sys

directory = sys.argv[1]
expected = {"metadata.json", "task-brief", "artifact-package", "findings.json", "verification.json"}
if stat.S_IMODE(os.lstat(directory).st_mode) != 0o700:
    raise SystemExit("extracted directory mode is not restricted")
actual = set(os.listdir(directory))
if actual != expected:
    raise SystemExit(f"wrong extracted members: {actual!r}")
for name in expected:
    info = os.lstat(os.path.join(directory, name))
    if not stat.S_ISREG(info.st_mode) or stat.S_ISLNK(info.st_mode):
        raise SystemExit(f"extracted member is not a regular non-symlink: {name}")
    if stat.S_IMODE(info.st_mode) != 0o600:
        raise SystemExit(f"extracted member mode is not restricted: {name}")
PY
}

extract_count() {
  find "$WORK" -maxdepth 1 -type d -name 'engineering-fix-handoff-extract.*' | wc -l | tr -d ' '
}

assert_no_extract_output() {
  local output=$1
  local before=$2
  [[ -z "$(parse_extracted_path "$output")" ]] || fail "failed verify emitted Extracted: $output"
  if [[ "$(extract_count)" != "$before" ]]; then
    fail 'failed verify left a partial extracted directory'
  fi
}

assemble_bundle_with_artifact_revision() {
  python3 - "$1" "$2" "$3" "$4" <<'PY'
import io
import json
import tarfile
import sys

source, destination, artifact_path, revision = sys.argv[1:]
with tarfile.open(source, "r:*") as archive:
    payloads = {member.name: archive.extractfile(member).read() for member in archive.getmembers()}
with open(artifact_path, "rb") as handle:
    payloads["artifact-package"] = handle.read()
metadata = json.loads(payloads["metadata.json"])
metadata["revision"] = revision
payloads["metadata.json"] = json.dumps(metadata, sort_keys=True, separators=(",", ":")).encode("utf-8")
with tarfile.open(destination, "w", format=tarfile.USTAR_FORMAT) as archive:
    for name in ("metadata.json", "task-brief", "artifact-package", "findings.json", "verification.json"):
        member = tarfile.TarInfo(name)
        member.size = len(payloads[name])
        member.mode = 0o600
        member.mtime = 0
        archive.addfile(member, io.BytesIO(payloads[name]))
PY
}

assert_reassembled_control() {
  local source_bundle=$1
  local rebuilt_bundle=$2
  local artifact=$3
  local revision=$4
  local label=$5
  local rebuilt_digest rebuilt_verify rebuilt_extract

  assemble_bundle_with_artifact_revision \
    "$source_bundle" "$rebuilt_bundle" "$artifact" "$revision"
  rebuilt_digest=$(hash_bundle "$rebuilt_bundle")
  rebuilt_verify=$("$HELPER" verify "$rebuilt_bundle" "$rebuilt_digest") \
    || fail "$label reassembled control failed verification"
  rebuilt_extract=$(parse_extracted_path "$rebuilt_verify")
  [[ -n "$rebuilt_extract" ]] || fail "$label reassembled control did not emit Extracted"
  assert_snapshot "$rebuilt_extract"
  cmp "$artifact" "$rebuilt_extract/artifact-package" \
    || fail "$label reassembled control artifact differs from the input"
}

assemble_bundle_with_round() {
  python3 - "$1" "$2" "$3" <<'PY'
import io
import json
import tarfile
import sys

source, destination, round_text = sys.argv[1:]
with tarfile.open(source, "r:*") as archive:
    payloads = {member.name: archive.extractfile(member).read() for member in archive.getmembers()}
metadata = json.loads(payloads["metadata.json"])
metadata["round"] = int(round_text)
payloads["metadata.json"] = json.dumps(metadata, sort_keys=True, separators=(",", ":")).encode("utf-8")
with tarfile.open(destination, "w", format=tarfile.USTAR_FORMAT) as archive:
    for name in ("metadata.json", "task-brief", "artifact-package", "findings.json", "verification.json"):
        member = tarfile.TarInfo(name)
        member.size = len(payloads[name])
        member.mode = 0o600
        member.mtime = 0
        archive.addfile(member, io.BytesIO(payloads[name]))
PY
}

printf 'brief\n' > "$WORK/brief"
printf '\x00artifact\xff\n' > "$WORK/artifact"

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

def wrong_type(value):
    if isinstance(value, str):
        return []
    if isinstance(value, list):
        return {}
    if isinstance(value, int):
        return "not-an-integer"
    raise AssertionError(f"unhandled fixture type: {type(value)}")

def make_cases(kind, base, array_key, item_keys):
    write(kind, "valid.json", base)
    for key in base:
        value = copy.deepcopy(base)
        del value[key]
        write(kind, f"missing-envelope-{key}.json", value)
        value = copy.deepcopy(base)
        value[key] = wrong_type(value[key])
        write(kind, f"wrong-envelope-{key}.json", value)
    for key in item_keys:
        value = copy.deepcopy(base)
        del value[array_key][0][key]
        write(kind, f"missing-item-{key}.json", value)
        value = copy.deepcopy(base)
        value[array_key][0][key] = wrong_type(value[array_key][0][key])
        write(kind, f"wrong-item-{key}.json", value)
    value = copy.deepcopy(base)
    value[array_key] = [False]
    write(kind, "wrong-item-object.json", value)
    value = copy.deepcopy(base)
    value["schema"] = "wrong-schema.v1"
    write(kind, "wrong-schema-value.json", value)
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
make_cases("verification", verification, "checks", list(verification["checks"][0]))

for kind in ("findings", "verification"):
    with open(os.path.join(out, kind, "malformed.json"), "w") as handle:
        handle.write('{"schema":')
    open(os.path.join(out, kind, "empty.json"), "w").close()
PY

FINDINGS="$CASES/findings/valid.json"
VERIFICATION="$CASES/verification/valid.json"
for invalid in "$CASES/findings"/*.json; do
  [[ "$(basename "$invalid")" == valid.json ]] && continue
  assert_rejected create_bundle \
    "$WORK/brief" "$WORK/artifact" "$invalid" "$VERIFICATION" 2
done
for invalid in "$CASES/verification"/*.json; do
  [[ "$(basename "$invalid")" == valid.json ]] && continue
  assert_rejected create_bundle \
    "$WORK/brief" "$WORK/artifact" "$FINDINGS" "$invalid" 2
done

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
# round 2-5 evidence. Each create output exposes an exact path/digest pair.
create1=$(create_bundle "$WORK/brief" "$WORK/artifact" "$FINDINGS" "$VERIFICATION" 2)
bundle1=$(parse_bundle_path "$create1")
digest1=$(parse_bundle_digest "$create1")
[[ -n "$bundle1" && -n "$digest1" ]] || fail 'create did not emit Bundle and Revision fields'
[[ -f "$bundle1" && ! -L "$bundle1" ]] || fail "bundle path is not one regular file: $bundle1"
[[ "$digest1" =~ ^[0-9a-f]{64}$ ]] || fail "bundle digest is not a SHA-256: $digest1"
[[ "$(hash_bundle "$bundle1")" == "$digest1" ]] || fail 'first digest does not hash the full bundle file'
verify1=$("$HELPER" verify "$bundle1" "$digest1") || fail 'first exact bundle/digest pair failed verification'
extract1=$(parse_extracted_path "$verify1")
[[ -n "$extract1" && -d "$extract1" && ! -L "$extract1" ]] || fail 'verify did not emit an extracted snapshot'
assert_snapshot "$extract1"
cmp "$WORK/brief" "$extract1/task-brief" || fail 'extracted brief differs from the input'
cmp "$WORK/artifact" "$extract1/artifact-package" || fail 'extracted binary artifact differs from the input'
cmp "$FINDINGS" "$extract1/findings.json" || fail 'extracted findings differ from the input'
cmp "$VERIFICATION" "$extract1/verification.json" || fail 'extracted verification differs from the input'

create2=$(create_bundle "$WORK/brief" "$WORK/artifact" "$FINDINGS" "$VERIFICATION" 3)
bundle2=$(parse_bundle_path "$create2")
digest2=$(parse_bundle_digest "$create2")
[[ -n "$bundle2" && -n "$digest2" ]] || fail 'second create did not emit Bundle and Revision fields'
[[ "$bundle1" != "$bundle2" ]] || fail 'separate creates reused a bundle path'
[[ -f "$bundle2" && ! -L "$bundle2" ]] || fail "bundle path is not one regular file: $bundle2"
[[ "$(hash_bundle "$bundle2")" == "$digest2" ]] || fail 'second digest does not hash the full bundle file'
verify2=$("$HELPER" verify "$bundle2" "$digest2") || fail 'second exact bundle/digest pair failed verification'
extract2=$(parse_extracted_path "$verify2")
[[ -n "$extract2" && -d "$extract2" && ! -L "$extract2" ]] || fail 'second verify did not emit an extracted snapshot'
assert_snapshot "$extract2"

# The verified snapshot remains the consumer input after the mutable bundle path
# is replaced and then tampered with.
cp "$bundle2" "$WORK/replacement.bundle"
mv "$WORK/replacement.bundle" "$bundle1"
printf 'tampered after verify\n' >> "$bundle1"
assert_snapshot "$extract1"
cmp "$WORK/artifact" "$extract1/artifact-package" || fail 'extracted snapshot changed after bundle replacement'

cp "$bundle1" "$WORK/tampered.bundle"
printf 'tampered\n' >> "$WORK/tampered.bundle"
extracts_before=$(extract_count)
tampered_verify=$("$HELPER" verify "$WORK/tampered.bundle" "$digest1" 2>&1 || true)
assert_no_extract_output "$tampered_verify" "$extracts_before"
assert_rejected "$HELPER" verify "$WORK/tampered.bundle" "$digest1"
"$HELPER" verify "$bundle2" "$digest2" || fail 'untampered second bundle changed after first-path replacement'

explicit_bundle="$WORK/explicit.bundle"
explicit_create=$(create_bundle_to \
  "$WORK/brief" "$WORK/artifact" "$FINDINGS" "$VERIFICATION" 2 "$explicit_bundle")
explicit_path=$(parse_bundle_path "$explicit_create")
explicit_digest=$(parse_bundle_digest "$explicit_create")
[[ "$explicit_path" == "$explicit_bundle" ]] || fail "create returned the wrong explicit output: $explicit_path"
[[ -f "$explicit_bundle" && ! -L "$explicit_bundle" ]] || fail 'explicit output is not one regular file'
[[ "$(hash_bundle "$explicit_bundle")" == "$explicit_digest" ]] \
  || fail 'explicit output digest does not hash the full bundle file'
explicit_verify=$("$HELPER" verify "$explicit_bundle" "$explicit_digest") \
  || fail 'explicit output failed verification'
explicit_extract=$(parse_extracted_path "$explicit_verify")
[[ -n "$explicit_extract" ]] || fail 'explicit output verify did not emit Extracted'
assert_snapshot "$explicit_extract"

printf 'different artifact\n' > "$WORK/other-artifact"
assert_rejected create_bundle_to \
  "$WORK/brief" "$WORK/other-artifact" "$FINDINGS" "$VERIFICATION" 3 "$explicit_bundle"
[[ "$(hash_bundle "$explicit_bundle")" == "$explicit_digest" ]] \
  || fail 'rejected create overwrote the existing explicit output'
"$HELPER" verify "$explicit_bundle" "$explicit_digest" \
  || fail 'original explicit output no longer verifies after rejected overwrite'

extracts_before=$(extract_count)
missing_verify=$("$HELPER" verify "$WORK/missing.bundle" "$digest1" 2>&1 || true)
assert_no_extract_output "$missing_verify" "$extracts_before"
assert_rejected "$HELPER" verify "$WORK/missing.bundle" "$digest1"
: > "$WORK/empty.bundle"
empty_digest=$(hash_bundle "$WORK/empty.bundle")
extracts_before=$(extract_count)
empty_verify=$("$HELPER" verify "$WORK/empty.bundle" "$empty_digest" 2>&1 || true)
assert_no_extract_output "$empty_verify" "$extracts_before"
assert_rejected "$HELPER" verify "$WORK/empty.bundle" "$empty_digest"
printf 'not a fix-handoff bundle\n' > "$WORK/malformed.bundle"
malformed_digest=$(hash_bundle "$WORK/malformed.bundle")
extracts_before=$(extract_count)
malformed_verify=$("$HELPER" verify "$WORK/malformed.bundle" "$malformed_digest" 2>&1 || true)
assert_no_extract_output "$malformed_verify" "$extracts_before"
assert_rejected "$HELPER" verify "$WORK/malformed.bundle" "$malformed_digest"

for round in 2 3 4 5; do
  round_create=$(create_bundle \
    "$WORK/brief" "$WORK/artifact" "$FINDINGS" "$VERIFICATION" "$round") \
    || fail "round $round was rejected during create"
  round_bundle=$(parse_bundle_path "$round_create")
  round_digest=$(parse_bundle_digest "$round_create")
  "$HELPER" verify "$round_bundle" "$round_digest" >/dev/null \
    || fail "round $round was rejected during verify"
done
for round in 0 1 6 -1 two ''; do
  assert_rejected create_bundle "$WORK/brief" "$WORK/artifact" "$FINDINGS" "$VERIFICATION" "$round"
done

round6_bundle="$WORK/round-6.bundle"
assemble_bundle_with_round "$round_bundle" "$round6_bundle" 6
round6_digest=$(hash_bundle "$round6_bundle")
extracts_before=$(extract_count)
round6_verify=$("$HELPER" verify "$round6_bundle" "$round6_digest" 2>&1 || true)
assert_no_extract_output "$round6_verify" "$extracts_before"
assert_rejected "$HELPER" verify "$round6_bundle" "$round6_digest"

# Canonical working-tree review packages remain content-addressed. Exercise the
# exact header shape so later parser changes cannot accidentally treat them as
# 40-hex git-revision artifacts.
working_tree_artifact="$WORK/working-tree.artifact"
printf '# Review package\nMode: working tree\nBase HEAD: %s\n\n## Status\n M sample\n\n## Tracked, staged, and unstaged diff\n' \
  90f0ac00a6df120ab960e29678cd8b3770af6830 > "$working_tree_artifact"
working_tree_revision=$(hash_bundle "$working_tree_artifact")
working_tree_create=$(create_bundle_with_revision "$working_tree_revision" \
  "$WORK/brief" "$working_tree_artifact" "$FINDINGS" "$VERIFICATION" 2)
working_tree_bundle=$(parse_bundle_path "$working_tree_create")
working_tree_digest=$(parse_bundle_digest "$working_tree_create")
working_tree_verify=$("$HELPER" verify "$working_tree_bundle" "$working_tree_digest") \
  || fail 'canonical working-tree package failed verification'
working_tree_extract=$(parse_extracted_path "$working_tree_verify")
[[ -n "$working_tree_extract" ]] || fail 'working-tree verify did not emit Extracted'
assert_snapshot "$working_tree_extract"
cmp "$working_tree_artifact" "$working_tree_extract/artifact-package" \
  || fail 'verified working-tree artifact differs from the input'
assert_rejected create_bundle_with_revision 90f0ac00a6df120ab960e29678cd8b3770af6830 \
  "$WORK/brief" "$working_tree_artifact" "$FINDINGS" "$VERIFICATION" 2

assert_reassembled_control \
  "$working_tree_bundle" "$WORK/reassembled-working-tree.bundle" \
  "$working_tree_artifact" "$working_tree_revision" 'working-tree'

stale_working_tree_bundle="$WORK/stale-working-tree.bundle"
stale_working_tree_revision=0000000000000000000000000000000000000000000000000000000000000000
assemble_bundle_with_artifact_revision "$working_tree_bundle" "$stale_working_tree_bundle" \
  "$working_tree_artifact" "$stale_working_tree_revision"
stale_working_tree_digest=$(hash_bundle "$stale_working_tree_bundle")
extracts_before=$(extract_count)
stale_working_tree_verify=$("$HELPER" verify \
  "$stale_working_tree_bundle" "$stale_working_tree_digest" 2>&1 || true)
assert_no_extract_output "$stale_working_tree_verify" "$extracts_before"
assert_rejected "$HELPER" verify "$stale_working_tree_bundle" "$stale_working_tree_digest"

# Canonical committed-range packages are git-revision addressed, not merely
# shape-checked. Create and verify must both reject a stale metadata revision.
committed_base=90f0ac00a6df120ab960e29678cd8b3770af6830
committed_head=f9aa79e56133f2448712a71ffd9755852c3df6e8
committed_artifact="$WORK/committed-range.artifact"
printf '# Review package\nMode: committed range\nBase: %s\nHead: %s\n\n## Diff\n' \
  "$committed_base" "$committed_head" > "$committed_artifact"

committed_create=$(create_bundle_with_revision "$committed_head" \
  "$WORK/brief" "$committed_artifact" "$FINDINGS" "$VERIFICATION" 2)
committed_bundle=$(parse_bundle_path "$committed_create")
committed_digest=$(parse_bundle_digest "$committed_create")
"$HELPER" verify "$committed_bundle" "$committed_digest" \
  || fail 'canonical committed-range package failed verification'
assert_rejected create_bundle_with_revision 0000000000000000000000000000000000000000 \
  "$WORK/brief" "$committed_artifact" "$FINDINGS" "$VERIFICATION" 2

assert_reassembled_control \
  "$committed_bundle" "$WORK/reassembled-committed-range.bundle" \
  "$committed_artifact" "$committed_head" 'committed-range'

for committed_case in missing-base missing-head duplicate-base duplicate-head malformed-base malformed-head; do
  case_artifact="$WORK/committed-$committed_case.artifact"
  case "$committed_case" in
    missing-base)
      printf '# Review package\nMode: committed range\nHead: %s\n\n## Diff\n' \
        "$committed_head" > "$case_artifact" ;;
    missing-head)
      printf '# Review package\nMode: committed range\nBase: %s\n\n## Diff\n' \
        "$committed_base" > "$case_artifact" ;;
    duplicate-base)
      printf '# Review package\nMode: committed range\nBase: %s\nBase: %s\nHead: %s\n\n## Diff\n' \
        "$committed_base" "$committed_base" "$committed_head" > "$case_artifact" ;;
    duplicate-head)
      printf '# Review package\nMode: committed range\nBase: %s\nHead: %s\nHead: %s\n\n## Diff\n' \
        "$committed_base" "$committed_head" "$committed_head" > "$case_artifact" ;;
    malformed-base)
      printf '# Review package\nMode: committed range\nBase: invalid\nHead: %s\n\n## Diff\n' \
        "$committed_head" > "$case_artifact" ;;
    malformed-head)
      printf '# Review package\nMode: committed range\nBase: %s\nHead: invalid\n\n## Diff\n' \
        "$committed_base" > "$case_artifact" ;;
  esac
  assert_rejected create_bundle_with_revision "$committed_head" \
    "$WORK/brief" "$case_artifact" "$FINDINGS" "$VERIFICATION" 2

  malformed_header_bundle="$WORK/verify-$committed_case.bundle"
  assemble_bundle_with_artifact_revision "$committed_bundle" "$malformed_header_bundle" \
    "$case_artifact" "$committed_head"
  malformed_header_digest=$(hash_bundle "$malformed_header_bundle")
  extracts_before=$(extract_count)
  malformed_header_verify=$("$HELPER" verify \
    "$malformed_header_bundle" "$malformed_header_digest" 2>&1 || true)
  assert_no_extract_output "$malformed_header_verify" "$extracts_before"
  assert_rejected "$HELPER" verify "$malformed_header_bundle" "$malformed_header_digest"
done

# A valid digest alone cannot make a manually assembled stale package valid.
mismatched_bundle="$WORK/mismatched-committed.bundle"
python3 - "$committed_bundle" "$mismatched_bundle" <<'PY'
import io
import json
import tarfile
import sys

source, destination = sys.argv[1:]
with tarfile.open(source, "r:*") as archive:
    payloads = {member.name: archive.extractfile(member).read() for member in archive.getmembers()}
metadata = json.loads(payloads["metadata.json"])
metadata["revision"] = "0000000000000000000000000000000000000000"
payloads["metadata.json"] = json.dumps(metadata, sort_keys=True, separators=(",", ":")).encode("utf-8")
with tarfile.open(destination, "w", format=tarfile.USTAR_FORMAT) as archive:
    for name in ("metadata.json", "task-brief", "artifact-package", "findings.json", "verification.json"):
        member = tarfile.TarInfo(name)
        member.size = len(payloads[name])
        member.mode = 0o600
        member.mtime = 0
        archive.addfile(member, io.BytesIO(payloads[name]))
PY
mismatched_digest=$(hash_bundle "$mismatched_bundle")
extracts_before=$(extract_count)
mismatched_verify=$("$HELPER" verify "$mismatched_bundle" "$mismatched_digest" 2>&1 || true)
assert_no_extract_output "$mismatched_verify" "$extracts_before"
assert_rejected "$HELPER" verify "$mismatched_bundle" "$mismatched_digest"

printf 'PASS: fix-handoff evidence regression checks\n'
