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

## 4. Submit

After approval, submit interactively or run:

```sh
gh stack submit --auto --open
```

Inspect the live GitHub state. Do not treat successful command exit as proof that every PR is correct.

## 5. Review

Review from bottom to top. Resolve lower-layer design issues before approving dependent layers.

## 6. Revise

When a lower layer changes:

1. Check out that layer.
2. Make the smallest focused correction.
3. Run its tests and commit.
4. Cascade-rebase the stack with `gh stack rebase`.
5. Run the full tests from the top.
6. Verify every diff again.
7. Push only after approval.

## 7. Synchronize

Use `gh stack sync` when the stack must reconcile remote changes, update trunk, cascade-rebase branches, push them atomically, and synchronize PR state. Stop if local and remote stack definitions have diverged and no source of truth has been agreed.

## 8. Merge

`gh stack merge` merges all approved layers through the selected PR as one atomic operation. GitHub still enforces required checks, reviews, merge queues, and repository rules.

## 9. Clean up

After merge, confirm trunk CI passes. Use the team's branch-retention policy. `gh stack sync --prune` can remove local branches for merged PRs while preserving stack metadata needed by the extension.

## Verification after every structural change

- Stack order is correct.
- PR bases and heads are correct.
- Each diff remains focused.
- Layer-specific tests pass.
- Full-stack tests pass.
- Draft and review states are intentional.
- Reviewers know that commit IDs or diffs changed.
