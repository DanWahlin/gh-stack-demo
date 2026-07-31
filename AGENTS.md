# Repository agent instructions

Use these rules when planning, building, or maintaining stacked pull requests with the `gh stack` CLI extension. A specialized `gh-stack` skill is optional; this file is the required baseline.

## Decide whether to use a stack

Use one stack when the work has multiple reviewable layers and each higher layer depends on the layer below it.

Use instead:

- A normal branch and pull request for one isolated change.
- Separate stacks, preferably in separate worktrees, for independent features.

Do not combine unrelated work merely because it belongs to one project.

## Before coding

Run from the repository root:

```sh
git status --short --branch
gh auth status
gh stack --version
```

Stop if the working tree contains unrelated changes, `gh stack` is missing, or the intended trunk is uncertain. GitHub authentication is required before push, submission, synchronization, or merge; local planning and implementation can continue without it.

Inspect the repository and propose:

1. The trunk branch.
2. Branch names ordered from bottom to top.
3. The responsibility and exclusions for each branch.
4. Acceptance criteria and tests for each branch.
5. Layer-specific and full-stack verification commands.
6. Work that belongs in a separate stack or normal pull request.

Wait for approval before implementation.

## Implement bottom to top

For each approved layer:

1. Create or check out the layer.
2. Implement only the behavior assigned to the layer and add its tests.
3. Run the layer tests and applicable accumulated tests.
4. Inspect the diff against the parent branch.
5. Commit the implementation and tests together.
6. Stop if the layer is not green.

Do not defer all meaningful tests to the top pull request.

## `gh stack` command contract

Use these commands non-interactively when the command supports it:

```sh
# Create the bottom layer from an explicit trunk.
gh stack init --base <trunk> <bottom-branch>

# Add a dependent layer above the current top branch.
gh stack add <next-branch>

# Inspect local stack order and state.
gh stack view --json

# Submit approved branches and create ready-for-review pull requests.
gh stack submit --auto --open

# Navigate the stack.
gh stack bottom
gh stack top
```

Maintenance commands require extra care:

- `gh stack rebase` rewrites local commit IDs. Get approval first. Use `gh stack rebase --abort` if conflict resolution is uncertain.
- `gh stack push` updates remote stack branches with force-with-lease protection. Get approval first and verify every branch afterward.
- `gh stack sync` fetches, reconciles, rebases, pushes, and synchronizes pull request state. Get approval first. Stop on divergence or an unexpected prompt.
- `gh stack merge --yes --squash` requests a non-interactive squash merge. Get explicit approval and verify the final GitHub state.

Do not use plain `git push --force`. Do not replace `gh stack submit` with manual `gh pr create` commands for a tracked stack. See [`docs/cheat-sheet.md`](docs/cheat-sheet.md) for the full command reference.

## Approval boundaries

Do not perform these operations without explicit approval:

- Rewrite stack history.
- Push or synchronize branches.
- Submit pull requests or change their draft state.
- Merge pull requests.
- Delete branches, repositories, or stack data.

A request to plan or implement does not approve publication, history rewrites, or merge.

## Verification contract

Before requesting approval to submit, return:

- `gh stack view --json` output.
- Branch ancestry verification.
- A parent-to-child changed-file summary for every layer.
- Layer-specific test results.
- Full-stack test results from the top layer.
- Any conflicts, deviations, or unverified assumptions.

After an approved submission, inspect the live GitHub pull requests. Verify that every pull request has the intended base, head, changed files, readiness state, and stack linkage. Do not claim remote success from command exit status alone.

## Coding agents

Any coding agent can participate when it loads these instructions, has terminal access to GitHub CLI and `gh stack`, and follows the same approval and verification rules.

Before relying on an agent, ask it to summarize the applicable stack rules and compare the answer with this file.
