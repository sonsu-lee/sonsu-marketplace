#!/usr/bin/env bash
set -euo pipefail

repo_root=$(git rev-parse --show-toplevel)
sdd_workspace="$repo_root/plugins/engineering/skills/subagent-driven-development/scripts/sdd-workspace"
start_server="$repo_root/plugins/engineering/skills/brainstorming/scripts/start-server.sh"
stop_server="$repo_root/plugins/engineering/skills/brainstorming/scripts/stop-server.sh"
fixture_dir=$(mktemp -d)

cleanup() {
  while IFS= read -r state_dir; do
    "$stop_server" "${state_dir%/state}" >/dev/null || true
  done < <(find "$fixture_dir/.engineering/brainstorm" -type d -name state -print 2>/dev/null || true)
  rm -rf "$fixture_dir"
}
trap cleanup EXIT

git -C "$fixture_dir" init -q
plan="$fixture_dir/feature-plan.md"
printf '# Feature plan\n' > "$plan"
fixture_root=$(cd "$fixture_dir" && pwd -P)

workspace=$(cd "$fixture_dir" && "$sdd_workspace" "$plan")
expected_workspace="$fixture_root/.engineering/sdd/feature-plan"
if [[ "$workspace" != "$expected_workspace" ]]; then
  echo "expected Engineering workspace $expected_workspace, got $workspace" >&2
  exit 1
fi

server_info=$("$start_server" --project-dir "$fixture_dir" --idle-timeout-minutes 1 --background)
url=$(printf '%s\n' "$server_info" | python3 -c 'import json,sys; print(json.load(sys.stdin)["url"])')
screen_dir=$(printf '%s\n' "$server_info" | python3 -c 'import json,sys; print(json.load(sys.stdin)["screen_dir"])')

case "$screen_dir" in
  */.engineering/brainstorm/*/content) ;;
  *)
    echo "expected Engineering brainstorm path, got $screen_dir" >&2
    exit 1
    ;;
esac

curl -fsS -c "$fixture_dir/cookies.txt" "$url" >/dev/null
page=$(curl -fsS -b "$fixture_dir/cookies.txt" "${url%%\?*}")
version=$(python3 -c 'import json,sys; print(json.load(open(sys.argv[1]))["version"])' \
  "$repo_root/plugins/engineering/.codex-plugin/plugin.json")
expected_brand="<div class=\"brand\"><span class=\"brand-copy\">Engineering v$version</span></div>"
grep -Fq "$expected_brand" <<<"$page" || {
  echo "missing exact Engineering branding: $expected_brand" >&2
  exit 1
}

if grep -Eq '<(img|a)([ >])|https?://' <<<"$page"; then
  echo 'Engineering waiting page includes an image, link, or remote URL' >&2
  exit 1
fi

legacy_name='super''powers'
upstream_operator='prime''radiant'
telemetry_term='tele''metry'
if git -C "$repo_root" grep -Ini \
  -e "$legacy_name" \
  -e "$upstream_operator" \
  -- ':!plugins/engineering/tests/engineering-identity.test.sh'; then
  echo 'legacy identity remains in tracked content' >&2
  exit 1
fi

if git -C "$repo_root" grep -Ini \
  -e "$telemetry_term" \
  -- 'plugins/engineering' ':!plugins/engineering/tests/engineering-identity.test.sh'; then
  echo 'Engineering still contains a telemetry branch' >&2
  exit 1
fi

if find "$repo_root" -path "$repo_root/.git" -prune -o -iname "*$legacy_name*" -print | grep -q .; then
  echo 'legacy identity remains in a file or directory name' >&2
  exit 1
fi

echo 'engineering identity tests passed'
