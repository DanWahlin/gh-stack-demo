# GitHub Stacked PRs Demo

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

## Useful commands

```sh
gh stack view
gh stack up
gh stack down
gh stack rebase
gh stack push
gh stack sync
```

See [`VIDEO.md`](VIDEO.md) for the sub-three-minute script and recording runbook.
