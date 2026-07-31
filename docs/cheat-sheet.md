# `gh stack` cheat sheet

This reference matches the CLI help verified with `gh stack` 0.1.0.

## Create and inspect

| Goal | Command | Effect |
| --- | --- | --- |
| Start a stack | `gh stack init feature/domain` | Creates or adopts the bottom branch |
| Create several layers | `gh stack init domain api ui` | Creates or adopts branches from bottom to top |
| Add a top layer | `gh stack add feature/ui` | Creates a branch above the current top layer |
| Inspect the stack | `gh stack view` | Shows branches and PR status |
| Get machine-readable state | `gh stack view --json` | Returns stack data as JSON |
| Move up or down | `gh stack up`, `gh stack down` | Checks out an adjacent active layer |
| Go to an edge | `gh stack top`, `gh stack bottom` | Checks out the top or bottom layer |
| Return to trunk | `gh stack trunk` | Checks out the trunk branch |

## Publish and synchronize

| Goal | Command | Important behavior |
| --- | --- | --- |
| Submit PRs interactively | `gh stack submit` | Pushes branches and opens the PR editor |
| Submit non-interactively | `gh stack submit --auto --open` | Generates titles and marks PRs ready |
| Push existing branches | `gh stack push` | Uses per-branch force-with-lease checks |
| Synchronize everything | `gh stack sync` | Fetches, cascade-rebases, atomically pushes, and syncs PR state |
| Prune merged local branches | `gh stack sync --prune` | Removes local branches for merged PRs |
| Rebase locally | `gh stack rebase` | Cascade-rebases the stack |
| Abort a conflicted rebase | `gh stack rebase --abort` | Restores branches to their original state |
| Continue after resolution | `gh stack rebase --continue` | Continues the active stack rebase |

## Merge

| Goal | Command | Important behavior |
| --- | --- | --- |
| Choose interactively | `gh stack merge` | Selects how far up the stack to merge |
| Merge through a PR | `gh stack merge 42` | Atomically merges all layers through PR #42 |
| Merge non-interactively | `gh stack merge --yes --squash` | Merges the whole stack using squash |

GitHub evaluates branch protection and repository rules during the merge. The command does not bypass requirements.

## Safety model

- `submit` creates or updates remote PR state.
- `push`, `sync`, and `rebase` may change commit IDs.
- `merge` changes the trunk branch.
- Agents must receive explicit approval before remote submission, push, or merge.
- Never use a plain force push. The extension uses force-with-lease safeguards where history updates are required.

## Status symbols

| Symbol | Meaning |
| --- | --- |
| `✓` | Pull request merged |
| `◎` | Pull request queued |
| `○` | Pull request open |
| `⚠` | Branch needs rebase |
