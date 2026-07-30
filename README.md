# GitHub Stacked PRs Demo

<p align="center">
  <img src="images/gh-stack-demo.png" alt="Three dependent pull requests shown as a stack" width="350" height="344">
</p>

A tiny Node.js task API built as three focused pull requests to demonstrate [GitHub's Stacked PRs feature](https://docs.github.com/pull-requests/how-tos/stacked-pull-requests) and the `gh stack` CLI extension.

## Presentation

Need to bring your team up to speed on GitHub Stacked PRs? [Download the latest PowerPoint deck](https://github.com/DanWahlin/gh-stack-demo/raw/refs/heads/main/github-stacked-prs.pptx) to use for a quick presentation. It includes the challenge stacked PRs address, high-level concept, CLI workflow, and a start-to-finish terminal example.

## Planned stack

1. `feature/task-model` adds the task model.
2. `feature/task-validation` adds title validation.
3. `test/task-model` adds tests for both layers.

Each PR targets the branch below it, so reviewers see only that layer's changes.

## Requirements

- Node.js 20 or newer
- GitHub CLI 2.0 or newer
- [`github/gh-stack`](https://github.com/github/gh-stack)

Verify the extension is available:

```sh
gh stack --version
```

If that command is unavailable, install the extension once:

```sh
gh extension install github/gh-stack
```

## Commands used to create this demo

The sequence below is a complete, tested reproduction of this repository's three-PR stack. It creates every required file, publishes `main`, builds each layer, runs the tests, and submits the stack. It was validated with Node.js 24.18.0, Git 2.43.0, GitHub CLI 2.96.0, and `gh stack` 0.1.0.

The commands use Bash or Zsh syntax. Before starting:

- Run `gh auth status` and confirm that GitHub CLI is authenticated.
- Confirm that `git config user.name` and `git config user.email` return your Git identity.
- Choose a repository name that does not already exist in your GitHub account.
- Run the sequence from the directory where you want the new repository folder created.

### 1. Set the repository name and verify `gh stack`

```sh
OWNER="$(gh api user --jq .login)"
REPO="gh-stack-demo-copy" # Change this if the name already exists.

# Install the extension only when it is not already available.
if ! gh stack --version >/dev/null 2>&1; then
  gh extension install github/gh-stack
fi
```

Avoid adding `--force` to the installation command. A forced upgrade depends on GitHub being able to resolve the latest extension release and is unnecessary when `gh stack` is already installed.

### 2. Create and publish `main`

```sh
mkdir "$REPO"
cd "$REPO"

git init -b main

cat > README.md <<'EOF'
# GitHub Stacked PRs Demo

A tiny Node.js project built as three focused stacked pull requests.
EOF

cat > package.json <<'EOF'
{
  "name": "gh-stack-demo",
  "version": "1.0.0",
  "private": true,
  "description": "A tiny Node.js API for demonstrating GitHub Stacked PRs",
  "type": "module",
  "scripts": {
    "test": "node --test"
  },
  "engines": {
    "node": ">=20"
  }
}
EOF

git add README.md package.json
git commit -m "chore: scaffold stacked PR demo"

gh repo create "$OWNER/$REPO" \
  --public \
  --source=. \
  --remote=origin \
  --push
```

Publishing `main` before initializing the stack gives `gh stack` a remote and a default trunk branch to detect.

### 3. Create the bottom layer: task model

`gh stack init` creates `feature/task-model` from `main`, records it as the first layer, and checks it out.

```sh
gh stack init feature/task-model

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
```

### 4. Add the middle layer: validation

`gh stack add` creates the next branch from the current top layer and checks it out.

```sh
gh stack add feature/task-validation

cat >> src/tasks.js <<'EOF'

export function isValidTask(task) {
  return Boolean(task?.title?.trim());
}
EOF

git add src/tasks.js
git commit -m "feat: validate task titles"
```

### 5. Add the top layer: tests

```sh
gh stack add test/task-model

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
```

The local branch chain is now:

```text
main
└── feature/task-model
    └── feature/task-validation
        └── test/task-model
```

### 6. Test, inspect, and submit

```sh
npm test
gh stack view
gh stack submit --auto --open
```

`gh stack submit --auto --open` performs the GitHub-side work in one operation:

1. Pushes all three branches.
2. Creates PR #1 from `feature/task-model` into `main`.
3. Creates PR #2 from `feature/task-validation` into `feature/task-model`.
4. Creates PR #3 from `test/task-model` into `feature/task-validation`.
5. Links the three PRs as one GitHub stack.
6. Marks all three PRs ready for review rather than draft.

`--auto` skips the interactive editor and derives PR titles from the commits. `--open` is important with `--auto` because automatically submitted PRs otherwise default to drafts. To edit each title, description, and draft state interactively, use `gh stack submit` without those flags.

This exact flow was independently executed and verified in [`DanWahlin/gh-stack-demo-validated`](https://github.com/DanWahlin/gh-stack-demo-validated).

## Useful commands after submission

```sh
# Inspect the current stack and PR states.
gh stack view

# Move between adjacent layers.
gh stack up
gh stack down

# Push committed changes on every stack branch.
gh stack push

# Fetch, rebase, push, and synchronize PR/stack state.
gh stack sync

# Rebase locally without performing the rest of a sync.
gh stack rebase

# Interactively land all or part of the stack.
gh stack merge
```
