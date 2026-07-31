# Troubleshooting stacked PRs

Inspect the stack before changing it:

```sh
git status --short --branch
gh stack view --json
```

Commit or stash work before rebasing or synchronizing.

| Symptom | Likely cause | Diagnostic | Recovery |
| --- | --- | --- | --- |
| A PR shows unrelated files | Incorrect base or stale parent branch | Inspect `baseRefName`, `headRefName`, and the Files changed tab | Correct the stack relationship, rebase, then verify before pushing |
| A branch shows `needsRebase` | Trunk or a lower layer advanced | Run `gh stack view --json` | Get approval before `gh stack rebase`; test and verify every diff before any push |
| A PR was created as a draft | `--auto` was used without `--open` | Inspect the PR draft state | Run `gh stack submit --auto --open` after approval to mark the stack ready |
| A command asks an unexpected question | The command is interactive, state is ambiguous, or local and remote definitions differ | Read the complete prompt without selecting an option | Stop and ask the stack owner to approve a specific choice; do not guess in automation |
| A branch is missing from the stack | The branch was created outside the stack or metadata is absent | Compare `git branch` with `gh stack view --json` | Adopt existing branches with `gh stack init` in bottom-to-top order |
| Synchronization reports divergence | Local and GitHub stack definitions differ | Read the complete `gh stack sync` message and resulting state, even when the process exits successfully | In a terminal, select the intended source of truth; in automation, stop and resolve manually |
| Rebase reports conflicts | Two layers changed overlapping lines | Inspect conflict markers and layer responsibilities | Resolve, test, and run `gh stack rebase --continue`; use `--abort` when uncertain |
| CI passes only on the top PR | Lower layers depend on higher-layer files or tests | Check out each branch and run its tests | Move required tests or code into the correct lower layer |
| Push updates some branches but rejects another | A remote branch advanced | Read the rejected branch name from `gh stack push` | Fetch, inspect the remote change, reconcile it, and rerun the command |
| Merge is rejected | A PR is draft, checks failed, or repository rules block it | Inspect PR checks and branch protection | Satisfy the GitHub requirement; stack merge does not bypass it |
| The default trunk is wrong | Repository default branch detection differs from the intended trunk | Inspect the remote default branch | Initialize with `gh stack init --base <branch> ...` |

## Recovery rules

1. Do not run a plain force push.
2. Do not rewrite another contributor's stack branches.
3. Use `gh stack rebase --abort` when conflict resolution is uncertain.
4. Re-run layer tests and full-stack tests after recovery.
5. Verify bases, heads, diffs, and PR state before resuming review.
6. Record the root cause when the same failure could affect other team members.
