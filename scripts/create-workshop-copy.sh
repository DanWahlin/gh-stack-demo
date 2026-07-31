#!/usr/bin/env bash
set -euo pipefail

SOURCE_REPO="${SOURCE_REPO:-DanWahlin/gh-stacked-prs}"
MODE=""
VISIBILITY=""
TARGET_REPO=""
TARGET_DIR=""

usage() {
  cat <<'EOF'
Create an isolated stacked-PR workshop repository.

Usage:
  scripts/create-workshop-copy.sh OWNER/REPO --build (--public|--private) [--directory PATH]
  scripts/create-workshop-copy.sh OWNER/REPO --ready (--public|--private) [--directory PATH]

Modes:
  --build   Copy main only. The learner creates the stack during the workshop.
  --ready   Copy main, create all three layers, run tests, and submit the PR stack.

The target repository and local directory must not already exist. The script
never deletes an existing repository or directory.
EOF
}

fail() {
  printf 'ERROR: %s\n' "$*" >&2
  exit 1
}

while (($#)); do
  case "$1" in
    --build|--ready)
      [[ -z "$MODE" ]] || fail "Choose only one mode."
      MODE="${1#--}"
      ;;
    --public|--private)
      [[ -z "$VISIBILITY" ]] || fail "Choose only one visibility."
      VISIBILITY="$1"
      ;;
    --directory)
      shift
      (($#)) || fail "--directory requires a path."
      TARGET_DIR="$1"
      ;;
    -h|--help)
      usage
      exit 0
      ;;
    -* )
      fail "Unknown option: $1"
      ;;
    *)
      [[ -z "$TARGET_REPO" ]] || fail "Only one OWNER/REPO target is allowed."
      TARGET_REPO="$1"
      ;;
  esac
  shift
done

[[ -n "$TARGET_REPO" ]] || fail "Provide the target as OWNER/REPO."
[[ "$TARGET_REPO" == */* ]] || fail "Use the OWNER/REPO form."
[[ -n "$MODE" ]] || fail "Choose --build or --ready."
[[ -n "$VISIBILITY" ]] || fail "Choose --public or --private."

for command in git node gh; do
  command -v "$command" >/dev/null 2>&1 || fail "$command is required."
done

gh auth status >/dev/null
gh stack --version >/dev/null

git config user.name >/dev/null || fail "git user.name is not configured."
git config user.email >/dev/null || fail "git user.email is not configured."

if gh repo view "$TARGET_REPO" >/dev/null 2>&1; then
  fail "Repository $TARGET_REPO already exists. Choose a new name."
fi

if [[ -z "$TARGET_DIR" ]]; then
  TARGET_DIR="${TARGET_REPO#*/}"
fi
[[ ! -e "$TARGET_DIR" ]] || fail "Local path $TARGET_DIR already exists."

printf 'Creating %s from template %s...\n' "$TARGET_REPO" "$SOURCE_REPO"
gh repo create "$TARGET_REPO" "$VISIBILITY" --template "$SOURCE_REPO"
gh repo clone "$TARGET_REPO" "$TARGET_DIR"

cd "$TARGET_DIR"

if [[ "$MODE" == "build" ]]; then
  cat <<EOF

Build-mode repository created:
  https://github.com/$TARGET_REPO

Next:
  cd $TARGET_DIR
  open docs/workshop/README.md
  start with: gh stack init workshop/task-model
EOF
  exit 0
fi

gh stack init --base main workshop/task-model

mkdir -p src
cat > src/tasks.js <<'EOF'
export function createTask(title) {
  return {
    id: crypto.randomUUID(),
    title,
    completed: false,
  };
}
EOF

git add src/tasks.js
git commit -m "feat: add task model"

gh stack add workshop/task-validation
cat >> src/tasks.js <<'EOF'

export function isValidTask(task) {
  return Boolean(task?.title?.trim());
}
EOF

git add src/tasks.js
git commit -m "feat: validate task titles"

gh stack add workshop/task-tests
mkdir -p test
cat > test/tasks.test.js <<'EOF'
import test from 'node:test';
import assert from 'node:assert/strict';
import { createTask, isValidTask } from '../src/tasks.js';

test('creates a valid task', () => {
  const task = createTask('Ship the demo');

  assert.equal(task.title, 'Ship the demo');
  assert.equal(task.completed, false);
  assert.equal(isValidTask(task), true);
});

test('rejects a task with an empty title', () => {
  assert.equal(isValidTask(createTask('   ')), false);
});
EOF

git add test/tasks.test.js
git commit -m "test: cover task creation and validation"

npm test
gh stack view --json
gh stack submit --auto --open
python scripts/verify-demo.py --repo "$TARGET_REPO"

cat <<EOF

Ready-mode repository created and verified:
  https://github.com/$TARGET_REPO

The three pull requests are open and ready for review.
EOF
