# Stacked PR lifecycle

A useful stack stays understandable after its first submission.

## 1. Propose

Define the trunk, branch order, responsibility, exclusions, tests, and acceptance criteria before coding. Keep independent workstreams in separate stacks.

## 2. Implement

Build from bottom to top. Keep implementation and tests together, and make every layer green before creating the next branch.

## 3. Inspect

Run `gh stack view --json`. Verify ancestry, focused parent-to-child diffs, and test results for every layer.

## 4. Submit

After approval, run:

```sh
gh stack submit --auto --open
```

Inspect the live pull requests. Verify bases, heads, changed files, readiness, and stack linkage. Command exit status alone is not proof that the stack is correct.

## 5. Review

Review from bottom to top. Resolve lower-layer design issues before approving dependent layers.

## 6. Revise

When a lower layer changes:

1. Update and test that layer.
2. Commit the correction.
3. Get approval before `gh stack rebase`.
4. Run the full tests from the top and inspect every diff.
5. Get approval before `gh stack push` or `gh stack sync`.
6. Inspect every live pull request after the update.

Use `gh stack rebase --abort` if conflict resolution is uncertain.

## 7. Synchronize

Use `gh stack sync` only after approval when the stack must reconcile remote changes, update trunk, cascade-rebase branches, push them, and synchronize pull request state. Stop if local and remote stack definitions have diverged and no source of truth has been agreed.

## 8. Merge

Use an explicit merge method for non-interactive operation, such as `gh stack merge --yes --squash`. GitHub still enforces required checks, reviews, merge queues, and repository rules. Get explicit approval and verify the final GitHub state.

## 9. Clean up

After merge, confirm trunk CI passes. Follow the team's branch-retention policy. `gh stack sync --prune` can remove local branches for merged pull requests.

## Verify after every structural change

- Stack order is correct.
- Pull request bases and heads are correct.
- Each diff remains focused.
- Layer and full-stack tests pass.
- Readiness state is intentional.
- Reviewers know when commit IDs or diffs changed.
