# GitHub Stacked PRs Demo

<p align="center">
  <img src="images/gh-stack-demo.png" alt="Three dependent pull requests shown as a stack" width="500">
</p>

A tiny Node.js task API built as three focused pull requests to demonstrate GitHub's Stacked PRs feature and the `gh stack` CLI extension.

## Planned stack

1. `feature/task-model` adds the task model.
2. `feature/task-validation` adds title validation.
3. `test/task-model` adds tests for both layers.

Each PR targets the branch below it, so reviewers see only that layer's changes.

## Requirements

- Node.js 20 or newer
- GitHub CLI 2.0 or newer
- [`github/gh-stack`](https://github.com/github/gh-stack)

```sh
gh extension install github/gh-stack
```

## Commands used to create this demo

The following is the actual command sequence used to create this repository and its three stacked pull requests. Run it from the directory where you want the repository created. Replace `DanWahlin` if you are using a different GitHub account.

### 1. Create and publish the repository

```sh
mkdir gh-stack-demo
cd gh-stack-demo

git init -b main
git add README.md package.json
git commit -m "chore: scaffold stacked PR demo"

gh repo create DanWahlin/gh-stack-demo \
  --public \
  --source=. \
  --remote=origin \
  --push
```

At this point, the repository has a published `main` branch. Install the extension once if it is not already available:

```sh
gh extension install github/gh-stack
```

### 2. Create the bottom layer: task model

`gh stack init` creates the first stack branch from `main` and checks it out.

```sh
gh stack init feature/task-model

# Create src/tasks.js with the task model, then commit it.
git add src/tasks.js
git commit -m "feat: add task model"
```

### 3. Add the middle layer: validation

`gh stack add` creates and checks out a branch on top of the current layer.

```sh
gh stack add feature/task-validation

# Add title validation to src/tasks.js, then commit it.
git add src/tasks.js
git commit -m "feat: validate task titles"
```

### 4. Add the top layer: tests

```sh
gh stack add test/task-model

# Create test/tasks.test.js, then commit it.
git add test/tasks.test.js
git commit -m "test: cover task creation and validation"
```

The resulting local branch chain is:

```text
main
└── feature/task-model
    └── feature/task-validation
        └── test/task-model
```

### 5. Verify and submit the stack

```sh
npm test
gh stack view
gh stack submit --auto --open
```

The final command performed all of the GitHub-side setup in one operation:

1. Pushed all three branches.
2. Created PR #1 with `main` as its base.
3. Created PR #2 with `feature/task-model` as its base.
4. Created PR #3 with `feature/task-validation` as its base.
5. Linked the three PRs as one GitHub stack.
6. Marked the PRs ready for review rather than drafts.

The `--auto` flag skipped the interactive editor and generated PR titles from the commits. The `--open` flag made the PRs ready for review. For an interactive run where you edit each title, description, and draft state before submission, use this instead:

```sh
gh stack submit
```

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
