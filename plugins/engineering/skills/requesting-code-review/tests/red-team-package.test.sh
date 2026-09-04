#!/usr/bin/env bash
set -euo pipefail

test_dir=$(cd "$(dirname "$0")" && pwd -P)
red_team_package="$test_dir/../scripts/red-team-package"
fixture_dir=$(mktemp -d "${TMPDIR:-/tmp}/red-team-package-test.XXXXXX")

cleanup() {
  rm -rf "$fixture_dir"
}
trap cleanup EXIT

printf 'binary-safe full diff\n' > "$fixture_dir/diff.package"
printf '사용자 목표\n' > "$fixture_dir/original-goal.md"
printf '승인 요구사항과 설계\n' > "$fixture_dir/requirements.md"
printf '의사코드와 flow mapping\n' > "$fixture_dir/plan.md"
printf '결정론적 검증 결과\n' > "$fixture_dir/verification.md"
printf '관찰 결과와 알려진 제약\n' > "$fixture_dir/outcomes.md"
printf 'none\n' > "$fixture_dir/provenance.md"

package_path="$(cd "$fixture_dir" && pwd -P)/red-team.bundle"
result=$("$red_team_package" \
  "$fixture_dir/diff.package" \
  "$fixture_dir/original-goal.md" \
  "$fixture_dir/requirements.md" \
  "$fixture_dir/plan.md" \
  "$fixture_dir/verification.md" \
  "$fixture_dir/outcomes.md" \
  "$fixture_dir/provenance.md" \
  "$package_path")

grep -Fq "Package: $package_path" <<<"$result"
grep -Fq "Revision: sha256:" <<<"$result"
declared_digest=$(awk -F: '/^Revision: sha256:/ {print $3}' <<<"$result")
if command -v shasum >/dev/null 2>&1; then
  actual_digest=$(shasum -a 256 "$package_path" | awk '{print $1}')
else
  actual_digest=$(sha256sum "$package_path" | awk '{print $1}')
fi
[ "$declared_digest" = "$actual_digest" ]
if mode=$(stat -f '%Lp' "$package_path" 2>/dev/null); then
  :
else
  mode=$(stat -c '%a' "$package_path")
fi
[ "$mode" = 600 ] || {
  echo "explicit bundle mode was $mode, expected 600" >&2
  exit 1
}
grep -Fq '## Component: original-goal' "$package_path"
grep -Fq '사용자 목표' "$package_path"
grep -Fq '## Component: review-finding-provenance' "$package_path"
[ "$(grep -c '^## Component:' "$package_path")" -eq 7 ] || {
  echo 'bundle did not contain exactly seven components' >&2
  exit 1
}

default_result=$(TMPDIR="$fixture_dir" "$red_team_package" \
  "$fixture_dir/diff.package" \
  "$fixture_dir/original-goal.md" \
  "$fixture_dir/requirements.md" \
  "$fixture_dir/plan.md" \
  "$fixture_dir/verification.md" \
  "$fixture_dir/outcomes.md" \
  "$fixture_dir/provenance.md")
default_package_path=$(awk -F': ' '/^Package: / {print $2}' <<<"$default_result")
case "$default_package_path" in
  "$fixture_dir"/engineering-red-team.*) ;;
  *)
    echo "default output path was unexpected: $default_package_path" >&2
    exit 1
    ;;
esac
[ -f "$default_package_path" ] || {
  echo 'default output package was not created' >&2
  exit 1
}
default_declared_digest=$(awk -F: '/^Revision: sha256:/ {print $3}' <<<"$default_result")
if command -v shasum >/dev/null 2>&1; then
  default_actual_digest=$(shasum -a 256 "$default_package_path" | awk '{print $1}')
else
  default_actual_digest=$(sha256sum "$default_package_path" | awk '{print $1}')
fi
[ "$default_declared_digest" = "$default_actual_digest" ] || {
  echo 'default output digest did not match the package' >&2
  exit 1
}

printf 'mutated after freeze\n' > "$fixture_dir/original-goal.md"
grep -Fq '사용자 목표' "$package_path"
if grep -Fq 'mutated after freeze' "$package_path"; then
  echo 'bundle followed a mutable source after freezing' >&2
  exit 1
fi

if "$red_team_package" \
  "$fixture_dir/diff.package" \
  "$fixture_dir/original-goal.md" \
  "$fixture_dir/requirements.md" \
  "$fixture_dir/plan.md" \
  "$fixture_dir/verification.md" \
  "$fixture_dir/outcomes.md" \
  "$fixture_dir/provenance.md" \
  "$package_path" >/dev/null 2>&1; then
  echo 'existing bundle was overwritten' >&2
  exit 1
fi

real_cat=$(command -v cat)
mkdir "$fixture_dir/bin"
cat > "$fixture_dir/bin/cat" <<'EOF'
#!/usr/bin/env bash
set -euo pipefail

if [ "${RED_TEAM_TEST_FAIL_INPUT:-}" = "${1:-}" ]; then
  exit 73
fi
if [ "${RED_TEAM_TEST_RACE_INPUT:-}" = "${1:-}" ]; then
  printf 'racer-owned\n' > "$RED_TEAM_TEST_RACE_OUTPUT"
fi

exec "$RED_TEAM_TEST_REAL_CAT" "$@"
EOF
chmod +x "$fixture_dir/bin/cat"

race_package_path="$fixture_dir/race.bundle"
if PATH="$fixture_dir/bin:$PATH" \
  RED_TEAM_TEST_REAL_CAT="$real_cat" \
  RED_TEAM_TEST_RACE_INPUT="$fixture_dir/plan.md" \
  RED_TEAM_TEST_RACE_OUTPUT="$race_package_path" \
  "$red_team_package" \
    "$fixture_dir/diff.package" \
    "$fixture_dir/original-goal.md" \
    "$fixture_dir/requirements.md" \
    "$fixture_dir/plan.md" \
    "$fixture_dir/verification.md" \
    "$fixture_dir/outcomes.md" \
    "$fixture_dir/provenance.md" \
    "$race_package_path" >/dev/null 2>&1; then
  echo 'concurrent output creation was accepted' >&2
  exit 1
fi
[ "$(cat "$race_package_path")" = 'racer-owned' ] || {
  echo 'concurrent output path was overwritten' >&2
  exit 1
}

dangling_package_path="$fixture_dir/dangling.bundle"
dangling_target="$fixture_dir/must-not-be-created.bundle"
ln -s "$dangling_target" "$dangling_package_path"
if "$red_team_package" \
  "$fixture_dir/diff.package" \
  "$fixture_dir/original-goal.md" \
  "$fixture_dir/requirements.md" \
  "$fixture_dir/plan.md" \
  "$fixture_dir/verification.md" \
  "$fixture_dir/outcomes.md" \
  "$fixture_dir/provenance.md" \
  "$dangling_package_path" >/dev/null 2>&1; then
  echo 'dangling symlink output was accepted' >&2
  exit 1
fi
[ -L "$dangling_package_path" ] || {
  echo 'dangling symlink output was replaced' >&2
  exit 1
}
if [ -e "$dangling_target" ] || [ -L "$dangling_target" ]; then
  echo 'dangling symlink target was created' >&2
  exit 1
fi

failed_package_path="$fixture_dir/failed.bundle"
if PATH="$fixture_dir/bin:$PATH" \
  RED_TEAM_TEST_REAL_CAT="$real_cat" \
  RED_TEAM_TEST_FAIL_INPUT="$fixture_dir/plan.md" \
  "$red_team_package" \
    "$fixture_dir/diff.package" \
    "$fixture_dir/original-goal.md" \
    "$fixture_dir/requirements.md" \
    "$fixture_dir/plan.md" \
    "$fixture_dir/verification.md" \
    "$fixture_dir/outcomes.md" \
    "$fixture_dir/provenance.md" \
    "$failed_package_path" >/dev/null 2>&1; then
  echo 'component copy failure was accepted' >&2
  exit 1
fi
if [ -e "$failed_package_path" ] || [ -L "$failed_package_path" ]; then
  echo 'component copy failure left a final package path' >&2
  exit 1
fi
if find "$fixture_dir" -maxdepth 1 -name 'failed.bundle.staging.*' -print -quit | grep -q .; then
  echo 'component copy failure left a staging file' >&2
  exit 1
fi

if "$red_team_package" \
  "$fixture_dir/missing-diff.package" \
  "$fixture_dir/original-goal.md" \
  "$fixture_dir/requirements.md" \
  "$fixture_dir/plan.md" \
  "$fixture_dir/verification.md" \
  "$fixture_dir/outcomes.md" \
  "$fixture_dir/provenance.md" >/dev/null 2>&1; then
  echo 'missing required component was accepted' >&2
  exit 1
fi

echo 'red-team immutable bundle test: PASS'
