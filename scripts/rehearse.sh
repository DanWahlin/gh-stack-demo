#!/usr/bin/env bash
set -euo pipefail

REPO="DanWahlin/gh-stack-demo"
WORKDIR="${TMPDIR:-/tmp}/gh-stack-demo-rehearsal"

rm -rf "$WORKDIR"
gh repo clone "$REPO" "$WORKDIR"
cd "$WORKDIR"

gh stack checkout 4

echo
echo "Stack:"
NO_COLOR=1 GIT_PAGER=cat gh stack view

echo
echo "Branch ancestry:"
git merge-base --is-ancestor main feature/task-model
git merge-base --is-ancestor feature/task-model feature/task-validation
git merge-base --is-ancestor feature/task-validation test/task-model
echo "✓ Stack ancestry is linear"

echo
echo "PR bases:"
for number in 1 2 3; do
  gh pr view "$number" --json number,baseRefName,headRefName,url \
    --jq '"PR #\(.number): \(.baseRefName) <- \(.headRefName)  \(.url)"'
done

echo
echo "Tests:"
git switch test/task-model
npm test
