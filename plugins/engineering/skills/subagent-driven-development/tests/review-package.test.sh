#!/usr/bin/env bash
set -euo pipefail

test_dir=$(cd "$(dirname "$0")" && pwd -P)
review_package="$test_dir/../scripts/review-package"
fixture_dir=$(mktemp -d "${TMPDIR:-/tmp}/sdd-review-package-test.XXXXXX")

cleanup() {
  rm -rf "$fixture_dir"
}
trap cleanup EXIT

git -C "$fixture_dir" init -q
git -C "$fixture_dir" config user.name "SDD Review Package Test"
git -C "$fixture_dir" config user.email "sdd-review-package-test@example.com"
printf '# Plan\n' > "$fixture_dir/plan.md"
printf '\000before\n' > "$fixture_dir/artifact.bin"
git -C "$fixture_dir" add plan.md artifact.bin
git -C "$fixture_dir" commit -qm 'test: add fixture'
base=$(git -C "$fixture_dir" rev-parse HEAD)
printf '\000after\n' > "$fixture_dir/artifact.bin"
git -C "$fixture_dir" add artifact.bin
git -C "$fixture_dir" commit -qm 'test: change binary artifact'
head=$(git -C "$fixture_dir" rev-parse HEAD)

first=$(cd "$fixture_dir" && "$review_package" plan.md "$base" "$head")
second=$(cd "$fixture_dir" && "$review_package" plan.md "$base" "$head")
first_path=$(awk '/^Package: / {sub(/^Package: /, ""); print; exit}' <<<"$first")
second_path=$(awk '/^Package: / {sub(/^Package: /, ""); print; exit}' <<<"$second")

[ -n "$first_path" ] && [ -f "$first_path" ]
[ -n "$second_path" ] && [ -f "$second_path" ]
[ "$first_path" != "$second_path" ]
grep -Fq 'GIT binary patch' "$first_path"
grep -Fq 'GIT binary patch' "$second_path"

echo 'SDD binary and immutable review package test: PASS'
