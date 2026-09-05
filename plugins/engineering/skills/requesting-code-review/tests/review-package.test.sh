#!/usr/bin/env bash
set -euo pipefail

test_dir=$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd -P)
review_package="$test_dir/../scripts/review-package"
fixture_dir=$(mktemp -d "${TMPDIR:-/tmp}/review-package-test.XXXXXX")
package_path=$(mktemp "${TMPDIR:-/tmp}/review-package-output.XXXXXX")
rm "$package_path"
package_parent=$(cd "$(dirname "$package_path")" && pwd -P)
package_path="$package_parent/$(basename "$package_path")"

cleanup() {
  rm -rf "$fixture_dir"
  rm -f "$package_path"
}
trap cleanup EXIT

git -C "$fixture_dir" init -q
git -C "$fixture_dir" config user.name "Review Package Test"
git -C "$fixture_dir" config user.email "review-package-test@example.com"
mkdir "$fixture_dir/nested"
printf 'before\n' > "$fixture_dir/tracked.txt"
printf 'nested\n' > "$fixture_dir/nested/keep.txt"
git -C "$fixture_dir" add tracked.txt nested/keep.txt
git -C "$fixture_dir" commit -qm "test: add fixture"
printf 'after\n' > "$fixture_dir/tracked.txt"
printf 'untracked\n' > "$fixture_dir/untracked.txt"

result=$(cd "$fixture_dir/nested" && "$review_package" working-tree "$package_path")

grep -Fq "Package: $package_path" <<<"$result"
grep -Fq "Revision: sha256:" <<<"$result"
grep -Fq '+after' "$package_path"
grep -Fq '+untracked' "$package_path"

echo "review-package repository-wide working-tree test: PASS"
