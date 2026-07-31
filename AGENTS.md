# Repository agent instructions

## Stacked PR workflow

Before implementing any substantial multi-part change:

1. Load and follow the `gh-stack` skill if it is available.
2. Determine whether the work forms a linear dependency chain.
3. If it does, propose the stack before coding:
   - trunk branch
   - branch names, ordered from bottom to top
   - responsibility and acceptance criteria for each branch
4. Put foundational changes in lower branches and dependent changes above them.
5. Keep each branch independently testable and reviewable.
6. Use a normal branch or separate stacks for independent workstreams.
7. Run all `gh stack` commands non-interactively.
8. Do not push branches, submit pull requests, or merge until explicitly approved.
9. After each layer, run its tests and commit before moving to the next branch.
10. Verify the final stack state with `gh stack view --json`.

Use one stack for dependent layers of one feature. Use separate stacks, preferably in separate worktrees, for independent features. Use a normal branch and pull request for a small isolated change.
