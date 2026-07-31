# Repository agent instructions

## Purpose

Use these instructions when planning, implementing, reviewing, or maintaining stacked pull requests with the `gh stack` CLI extension. These repository instructions are the required baseline. A specialized `gh-stack` skill is optional; do not stop only because no skill is available.

## Decide whether to use a stack

Before implementing a substantial multi-part change:

1. Inspect the repository and identify the trunk branch.
2. Decide whether the work contains independently reviewable layers.
3. Use one stack only when those layers form one linear dependency chain.
4. Use a normal branch and pull request for a small isolated change.
5. Use separate stacks, preferably in separate worktrees, for independent features.
6. Do not interleave unrelated changes merely because they belong to one project.

## Preflight

Run these checks from the repository root before creating stack branches:

```sh
git status --short --branch
gh auth status
gh stack --version
```

Stop if:

- The working tree contains changes that are outside the requested work.
- GitHub CLI is not authenticated for an operation that needs GitHub.
- `gh stack` is unavailable.
- The intended trunk or branch ownership is uncertain.

Read [`docs/cheat-sheet.md`](docs/cheat-sheet.md) before using a command whose behavior or flags are not covered below.

## Propose the stack before coding

Return this information and wait for approval:

- Trunk branch
- Branch names ordered from bottom to top
- Responsibility and explicit exclusions for each branch
- Acceptance criteria and tests for each branch
- Layer-specific and full-stack verification commands
- Work that belongs in a separate stack or normal pull request

Put foundational changes in lower branches and dependent changes above them. Keep each branch independently testable and reviewable.

## Implement one layer at a time

For each approved layer:

1. Create or check out the layer.
2. Add or update its tests first.
3. Run the tests and observe the expected failure when practical.
4. Implement only the behavior assigned to that layer.
5. Run the layer tests and the applicable accumulated tests.
6. Inspect the layer diff against its parent branch.
7. Commit the implementation and tests together.
8. Stop if the layer is not green before creating the next branch.

Do not defer all meaningful tests to the top pull request.

## Minimum `gh stack` command contract

Use non-interactive flags when the command supports them. Stop rather than guessing if a command asks an unexpected question.

```sh
# Create the bottom layer from an explicit trunk.
gh stack init --base <trunk> <bottom-branch>

# Add a dependent layer above the current top branch.
gh stack add <next-branch>

# Inspect local stack order and state.
gh stack view --json

# Create or update draft pull requests after approval.
gh stack submit --auto

# Mark the stack ready for review after separate approval.
gh stack submit --auto --open

# Move to stack edges.
gh stack bottom
gh stack top
```

Maintenance commands have additional risk:

- `gh stack rebase` rewrites local stack commit IDs. Get approval first. Run `gh stack rebase --abort` if conflict resolution is uncertain.
- `gh stack push` updates existing remote stack branches with force-with-lease protection. Get approval first and verify every remote branch afterward.
- `gh stack sync` fetches, reconciles, rebases, pushes, and synchronizes pull request state. Get approval first. Stop on local/remote divergence or an unexpected prompt.
- `gh stack merge --yes --squash` performs a non-interactive squash merge through the selected layer, subject to GitHub rules and merge queues. Always specify the merge method, get explicit approval, and verify the final GitHub state.

Do not use plain `git push --force`. Do not substitute manual `gh pr create` commands for `gh stack submit` on a tracked stack.

## Approval boundaries

Do not perform any of these operations without explicit human approval for that operation:

- Rewrite stack history with `gh stack rebase`
- Push branches
- Run `gh stack submit`
- Run `gh stack push` or `gh stack sync`
- Mark draft pull requests ready for review
- Merge any pull request or stack
- Delete branches, repositories, or stack data

A request to plan or implement does not automatically approve remote publication, history rewrites, readiness changes, or merge.

## Verification contract

Before requesting approval to publish drafts, return:

- `gh stack view --json` output
- Branch ancestry verification
- Parent-to-child diff summary for every layer
- Layer-specific test results
- Full-stack test results from the top layer
- Any conflicts, deviations, or unverified assumptions

After an approved submission, inspect the live GitHub pull requests. Verify:

- Every pull request is open.
- Draft or ready state matches the approved stage.
- Every base and head branch is correct.
- Every changed-file list matches the layer responsibility.
- The pull requests are linked as one stack.

Do not claim remote success from command exit status alone.

## Coding-agent compatibility

GitHub Copilot CLI is the primary hands-on agent for this workshop. GitHub Copilot cloud agent can plan, review, or contribute to one isolated branch, but it cannot create or maintain the complete multi-branch stack in one task. A local stack owner must integrate and verify any cloud-agent contribution.

Other agentic coding tools can be used when they:

- Load these repository instructions or an equivalent instruction file.
- Have terminal access to Git, GitHub CLI, and `gh stack`.
- Follow the same approval and verification boundaries.

Before relying on any agent, ask it to summarize the applicable stack rules and compare its answer with this file.
