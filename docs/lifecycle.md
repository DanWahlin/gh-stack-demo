# Stacked PR lifecycle

A useful stack stays understandable after its first submission.

## 1. Propose

Define the trunk, branch order, responsibility, and acceptance criteria before coding. Separate independent workstreams.

## 2. Implement

Build from bottom to top. Test and commit each layer before creating the next branch.

## 3. Inspect

Run:

```sh
gh stack view --json
```

Verify ancestry, bases, heads, and focused diffs.

## 4. Publish drafts

After explicit approval for remote draft publication, run:

```sh
gh stack submit --auto
```

Inspect the live draft pull requests. Verify stack linkage, bases, heads, changed files, and draft state. Do not treat successful command exit as proof that every pull request is correct.

## 5. Mark ready

After a separate approval, run:

```sh
gh stack submit --auto --open
```

Inspect GitHub again and verify that every pull request is ready, correctly based, and still focused.

## 6. Review

Review from bottom to top. Resolve lower-layer design issues before approving dependent layers.

## 7. Revise

When a lower layer changes:

1. Check out that layer.
2. Make the smallest focused correction.
3. Run its tests and commit.
4. Request approval before rewriting local stack history.
5. After approval, cascade-rebase the stack with `gh stack rebase`.
6. Run the full tests from the top.
7. Verify every diff again.
8. Request separate approval before pushing or synchronizing.

Run `gh stack rebase --abort` if conflict resolution is uncertain.

## 8. Synchronize

Use `gh stack sync` only after approval when the stack must reconcile remote changes, update trunk, cascade-rebase branches, push them, and synchronize pull request state. Stop if local and remote stack definitions have diverged and no source of truth has been agreed. Verify every remote branch and pull request afterward.

## 9. Merge

Use an explicit merge method for non-interactive operation, such as `gh stack merge --yes --squash`. GitHub still enforces required checks, reviews, merge queues, and repository rules. Get explicit approval and verify the final GitHub state; do not assume queued layers merge simultaneously.

## 10. Clean up

After merge, confirm trunk CI passes. Use the team's branch-retention policy. `gh stack sync --prune` can remove local branches for merged PRs while preserving stack metadata needed by the extension.

## Verification after every structural change

- Stack order is correct.
- PR bases and heads are correct.
- Each diff remains focused.
- Layer-specific tests pass.
- Full-stack tests pass.
- Draft and review states are intentional.
- Reviewers know that commit IDs or diffs changed.
