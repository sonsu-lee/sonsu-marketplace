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

printf '\000before\n' > "$fixture_dir/artifact.bin"
git -C "$fixture_dir" add -A
git -C "$fixture_dir" commit -qm "test: add binary fixture"
base=$(git -C "$fixture_dir" rev-parse HEAD)
printf '\000after\n' > "$fixture_dir/artifact.bin"
git -C "$fixture_dir" add artifact.bin
git -C "$fixture_dir" commit -qm "test: change binary artifact"
head=$(git -C "$fixture_dir" rev-parse HEAD)

first=$(cd "$fixture_dir" && "$review_package" range "$base" "$head")
second=$(cd "$fixture_dir" && "$review_package" range "$base" "$head")
first_path=$(awk '/^Package: / {sub(/^Package: /, ""); print; exit}' <<<"$first")
second_path=$(awk '/^Package: / {sub(/^Package: /, ""); print; exit}' <<<"$second")
[ -n "$first_path" ] && [ -f "$first_path" ]
[ -n "$second_path" ] && [ -f "$second_path" ]
[ "$first_path" != "$second_path" ]
grep -Fq 'GIT binary patch' "$first_path"
rm -f "$first_path" "$second_path"

if (cd "$fixture_dir" && "$review_package" range "$base" "$head" "$package_path") 2>/dev/null; then
  echo "existing OUTFILE was overwritten" >&2
  exit 1
fi

echo "review-package working-tree and binary range tests: PASS"
