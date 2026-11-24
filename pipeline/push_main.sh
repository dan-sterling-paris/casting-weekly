#!/usr/bin/env bash
# Update castingweekly.com/site/ (GitHub Pages, served from main) with what this branch has just built.
#
#   bash pipeline/push_main.sh ["extra commit message line" ...]
#
# main and this branch have separate histories, so this does not merge. It copies every file tracked on this branch
# onto main. Files that only main has (the holding page index.html, proto.html, CNAME) are left exactly as they are,
# and the script stops if any of them would change. Never force-pushes.
set -euo pipefail

cd "$(git rev-parse --show-toplevel)"
SRC=$(git rev-parse HEAD)
SHORT=$(git rev-parse --short HEAD)
KEEP=(index.html proto.html CNAME)
WT=$(mktemp -d "${TMPDIR:-/tmp}/cw-main.XXXXXX")
trap 'git worktree remove --force "$WT" >/dev/null 2>&1 || true; rm -rf "$WT"' EXIT

attempt() {
  # (set -e is off inside a function called from "if", so each step checks for itself)
  git fetch -q origin main || return 1
  git worktree remove --force "$WT" >/dev/null 2>&1 || true
  rm -rf "$WT"
  git worktree add -q --detach "$WT" origin/main || return 1
  git -C "$WT" checkout "$SRC" -- . || { echo "could not copy the branch onto main" >&2; exit 1; }
  if ! git -C "$WT" diff --cached --quiet origin/main -- "${KEEP[@]}"; then
    echo "stopped: copying the branch would change ${KEEP[*]} on main" >&2
    exit 1
  fi
  if git -C "$WT" diff --cached --quiet origin/main; then
    echo "main already up to date"
    exit 0
  fi
  msg=(-m "Update castingweekly.com/site/ from $SHORT")
  for line in "$@"; do msg+=(-m "$line"); done
  git -C "$WT" commit -q "${msg[@]}" || { echo "commit on main failed" >&2; exit 1; }
  git -C "$WT" push -q origin HEAD:main
}

if ! attempt "$@"; then
  echo "push to main rejected; fetching main again and retrying once" >&2
  attempt "$@"
fi
echo "main is now $(git -C "$WT" rev-parse --short HEAD)"
