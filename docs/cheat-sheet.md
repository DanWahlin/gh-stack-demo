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
| Submit drafts non-interactively | `gh stack submit --auto` | Generates titles and creates new pull requests as drafts |
| Mark the submitted stack ready | `gh stack submit --auto --open` | Marks new and existing pull requests ready for review |
| Push existing branches | `gh stack push` | Uses per-branch force-with-lease checks |
| Synchronize everything | `gh stack sync` | Fetches, cascade-rebases, pushes, and syncs pull request state; verify every branch afterward |
| Prune merged local branches | `gh stack sync --prune` | Removes local branches for merged PRs |
| Rebase locally | `gh stack rebase` | Cascade-rebases the stack |
| Abort a conflicted rebase | `gh stack rebase --abort` | Restores branches to their original state |
| Continue after resolution | `gh stack rebase --continue` | Continues the active stack rebase |

## Merge

| Goal | Command | Important behavior |
| --- | --- | --- |
| Choose interactively | `gh stack merge` | Selects how far up the stack to merge |
| Merge through a PR | `gh stack merge 42` | Requests a stack merge through PR #42 |
| Merge non-interactively | `gh stack merge --yes --squash` | Requests a squash merge of the whole stack without prompting |

GitHub evaluates branch protection and repository rules during the merge. The command does not bypass requirements. If the repository uses a merge queue, GitHub controls when each queued layer completes; verify the final state instead of assuming simultaneous completion.

## Safety model

- `submit` creates or updates remote pull request state. `--auto` creates new drafts; `--open` marks pull requests ready.
- `rebase` changes local commit IDs.
- `push` and `sync` update remote branches and can change commit IDs.
- `merge` changes the trunk branch or enters the stack into a merge queue.
- Agents must receive separate explicit approval before rebase, submission, push or sync, readiness changes, and merge.
- Never use a plain force push. The extension uses force-with-lease safeguards where history updates are required.

## Status symbols

| Symbol | Meaning |
| --- | --- |
| `✓` | Pull request merged |
| `◎` | Pull request queued |
| `○` | Pull request open |
| `⚠` | Branch needs rebase |
