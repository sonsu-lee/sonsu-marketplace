#!/bin/sh
set -eu

scope=${1-user}
case "$#:$scope" in
  0:user|1:user|1:project) ;;
  *) echo 'Usage: migrate-omp-plugins.sh [user|project]' >&2; exit 2 ;;
esac

for pair in skill:development planning:development ticket:product \
  decision:product git:git design:design review:review writing:writing; do
  old=${pair%%:*}-workflow@sonsu-marketplace
  new=${pair#*:}@sonsu-marketplace
  # 1. 統合先が同じ場合もあるため、直前の移行結果を含む一覧を取得する。
  installed=$(omp plugin list)
  printf '%s\n' "$installed" | grep -q "^  $old (.*) ($scope)$" || continue
  # 2. 新パッケージのインストールに失敗した場合は旧パッケージを残す。
  if ! printf '%s\n' "$installed" | grep -q "^  $new (.*) ($scope)$"; then
    omp plugin install "$new" --scope "$scope"
  fi
  omp plugin uninstall "$old" --scope "$scope"
done
