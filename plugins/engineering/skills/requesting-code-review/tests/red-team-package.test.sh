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
grep -Fq '## Component: original-goal' "$package_path"
grep -Fq '사용자 목표' "$package_path"
grep -Fq '## Component: review-finding-provenance' "$package_path"

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
