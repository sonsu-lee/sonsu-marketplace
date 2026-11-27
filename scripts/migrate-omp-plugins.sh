#!/bin/sh
set -eu

scope=${1-user}
case "$#:$scope" in
  0:user|1:user|1:project) ;;
  *) echo 'Usage: migrate-omp-plugins.sh [user|project]' >&2; exit 2 ;;
esac

listed() {
  printf '%s\n' "$installed" | grep -Eq "^  $1 \(.*\) \($scope\)( \[shadowed\])?$"
}

refreshed=no
migrate() {
  old=$1@sonsu-marketplace
  shift
  installed=$(omp plugin list)
  listed "$old" || return 0
  for package do
    new=$package@sonsu-marketplace
    listed "$new" && continue
    if [ "$refreshed" = no ]; then
      omp plugin marketplace update sonsu-marketplace
      refreshed=yes
    fi
    omp plugin install "$new" --scope "$scope"
  done
  # Keep the old package if any replacement fails to install.
  omp plugin uninstall "$old" --scope "$scope"
}

migrate product prd decisions tickets
migrate skill-workflow development
migrate planning-workflow development
migrate ticket-workflow tickets
migrate decision-workflow decisions
for name in git design review writing; do
  migrate "$name-workflow" "$name"
done
