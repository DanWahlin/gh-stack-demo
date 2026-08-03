# `gh stack` cheat sheet

This reference is checked against the installed `gh stack` release by `scripts/check-cli-contract.py` and compared with GitHub's [Stacked pull requests CLI commands](https://docs.github.com/pull-requests/reference/stacked-prs-cli-commands).

## Create and inspect

| Goal | Command | Effect |
| --- | --- | --- |
| Start a stack | `gh stack init --base main tasks/model` | Creates or adopts the bottom branch from an explicit trunk |
| Create several layers | `gh stack init --base main tasks/model tasks/validation tasks/api` | Creates or adopts branches from bottom to top |
| Add a top layer | `gh stack add tasks/api` | Creates a branch above the current top layer |
| Inspect the stack | `gh stack view` | Shows branches and PR status |
| Get machine-readable state | `gh stack view --json` | Returns stack data as JSON |
| Move up or down | `gh stack up`, `gh stack down` | Checks out an adjacent active layer |
| Go to an edge | `gh stack top`, `gh stack bottom` | Checks out the top or bottom layer |
| Return to trunk | `gh stack trunk` | Checks out the trunk branch |

## Publish and synchronize

| Goal | Command | Important behavior |
| --- | --- | --- |
| Submit PRs interactively | `gh stack submit` | Pushes branches, opens the editor, then creates or updates PRs and the stack |
| Submit drafts non-interactively | `gh stack submit --auto` | Generates titles and creates new pull requests as drafts |
| Mark the submitted stack ready | `gh stack submit --auto --open` | Marks new and existing pull requests ready for review |
| Push existing branches | `gh stack push` | Uses per-branch force-with-lease checks |
| Synchronize everything | `gh stack sync` | Reconciles remote stack state, fast-forwards trunk when possible, rebases if trunk moved, atomically pushes active branches, and syncs existing PR and stack state |
| Prune merged local branches | `gh stack sync --prune` | Removes local branches for merged PRs |
| Fetch and rebase locally | `gh stack rebase` | Fetches the remote, then cascade-rebases the stack without pushing or syncing PR state |
| Abort a conflicted rebase | `gh stack rebase --abort` | Restores branches to their original state |
| Continue after resolution | `gh stack rebase --continue` | Continues the active stack rebase |

## Merge

| Goal | Command | Important behavior |
| --- | --- | --- |
| Choose interactively | `gh stack merge` | Selects how far up the current stack to merge, the merge method, and confirmation |
| Merge by stack or PR number | `gh stack merge 42` | Treats `42` as a stack number first, then as a PR number |
| Merge non-interactively | `gh stack merge --yes --squash` | Requests a whole-stack squash merge without prompting |

A pull request selection merges that pull request and every unmerged pull request below it. A mid-stack pull request cannot merge by itself. GitHub evaluates branch protection and repository rules during the merge, and the command does not bypass them. If the repository uses a merge queue, the queue chooses the merge method and controls when each queued layer completes; verify the final state instead of assuming simultaneous completion.

## Safety model

- `submit` creates or updates remote pull request and stack state. `--auto` creates new pull requests as drafts; `--open` marks new and existing pull requests ready.
- `rebase` and `sync` can change commit IDs
- `push` updates remote branch tips with force-with-lease protection
- `sync --prune` deletes local branches for merged pull requests; it does not delete the remote branches
- `merge` changes the trunk branch or enters the stack into a merge queue
- Agents need explicit approval before rebase, submission, push or sync, draft-state changes, and merge
- Never use a plain force push. The extension uses force-with-lease safeguards where history updates are required.

## Status symbols

| Symbol | Meaning |
| --- | --- |
| `✓` | Pull request merged |
| `◎` | Pull request queued |
| `○` | Pull request open |
| `⚠` | Branch needs rebase |
