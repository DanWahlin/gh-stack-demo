# Stacked PRs team workshop

Use this 45–60 minute workshop to teach the full stacked pull request lifecycle. Learners need Git, Node.js 20 or newer, an authenticated GitHub CLI, and the `github/gh-stack` extension.

## Learning objectives

By the end of the workshop, learners can:

1. Decide whether work belongs in one stack, separate stacks, or a normal pull request.
2. Create a linear stack with independently reviewable layers.
3. Submit and inspect the stack on GitHub.
4. Update a lower layer and synchronize dependent layers.
5. Explain the team's review, continuous integration, and merge order.

## Create the learner repository

Do not fork this repository. Create an isolated build-mode repository before the workshop:

```sh
git clone https://github.com/DanWahlin/gh-stacked-prs.git
gh-stacked-prs/scripts/create-workshop-copy.sh \
  YOUR-OWNER/my-stacked-prs-workshop \
  --build \
  --private
```

The script copies `main` but does not copy or create the training pull requests. Learners create those during the labs. See [Create a workshop repository](../workshop-copies.md) for ready mode and permission details.

## Workshop map

| Lab | Topic | Time |
| --- | --- | --- |
| 0 | Preflight and mental model | 5 minutes |
| 1 | Create the domain layer | 10 minutes |
| 2 | Add the API and UI layers | 10 minutes |
| 3 | Test and submit | 10 minutes |
| 4 | Respond to review feedback | 10 minutes |
| 5 | Team adoption discussion | 10 minutes |

Use a disposable repository. Do not run the labs in the public demo repository.

## Lab 0: Preflight and stack decision

### Objective

Verify the tools and decide how the work should be divided.

### Actions

Run:

```sh
git --version
node --version
gh --version
gh auth status
gh stack --version
```

Discuss this scenario:

> Add an order model, an orders API, and an administrative orders screen.

The layers form one dependency chain:

```text
main
└── orders/domain-model
    └── orders/api
        └── orders/admin-ui
```

### Checkpoint

Each learner can state what belongs in each layer and why the UI layer depends on the API layer.

### Discussion question

Would an unrelated billing change belong in this stack? No. Use a separate branch or stack.

## Lab 1: Create the domain layer

### Objective

Create the smallest independently reviewable foundation.

### Actions

Create and publish a disposable repository with a `main` branch. Then run:

```sh
gh stack init orders/domain-model
```

Add an order model, test it, and commit it. Use one focused commit.

### Checkpoint

Run:

```sh
gh stack view --json
```

Verify that `orders/domain-model` is based on `main`.

### Common failure

If `gh stack init` cannot detect the trunk, verify that `main` exists on the remote and that the repository's default branch is `main`.

## Lab 2: Add dependent layers

### Objective

Add API and UI layers without mixing their responsibilities.

### Actions

Run:

```sh
gh stack add orders/api
# Add and commit only the API layer.

gh stack add orders/admin-ui
# Add and commit only the UI layer.
```

Run the applicable tests after each commit.

### Checkpoint

Verify this order with `gh stack view --json`:

```text
main
└── orders/domain-model
    └── orders/api
        └── orders/admin-ui
```

Inspect `git diff orders/domain-model..orders/api` and `git diff orders/api..orders/admin-ui`. Each diff must contain only its intended layer.

## Lab 3: Test and submit

### Objective

Publish focused pull requests with correct base branches.

### Actions

Run the complete test suite from the top branch. Then inspect the stack:

```sh
npm test
gh stack view --json
```

After the facilitator approves the proposed stack and verification results, submit non-interactively:

```sh
gh stack submit --auto --open
```

### Expected result

- The domain PR targets `main`.
- The API PR targets `orders/domain-model`.
- The UI PR targets `orders/api`.
- All PRs are open and ready for review.

### Checkpoint

Open each PR's **Files changed** tab. Verify that each PR shows only one layer.

## Lab 4: Respond to review feedback

### Objective

Practice changing a lower layer without manually rebuilding every branch.

### Actions

1. Move to the bottom branch with `gh stack bottom`.
2. Make a small requested change to the order model.
3. Run the domain tests and commit the change.
4. Run `gh stack rebase` to cascade the change through dependent branches.
5. Resolve conflicts if prompted. Run `gh stack rebase --abort` to restore the original state if the resolution is uncertain.
6. Re-run the full tests from the top branch.
7. Inspect `gh stack view --json`.
8. Push only after the facilitator approves the result.

The `gh stack push` and `gh stack sync` commands use force-with-lease semantics because rebasing changes commit IDs. Do not run them against shared branches without team agreement.

### Checkpoint

Each pull request still has the correct base and focused diff after synchronization.

## Lab 5: Team adoption discussion

Use [`../team-playbook.md`](../team-playbook.md) to agree on:

1. What qualifies for a stack.
2. Maximum stack size.
3. Required tests per layer.
4. Review order and ownership.
5. Who may synchronize and merge stacks.
6. How the team handles independent workstreams.

## Completion criteria

The workshop is complete when each learner can:

- Draw the branch and PR graph.
- Explain why each base branch is correct.
- Identify a change that should not be added to the stack.
- Show one focused diff per PR.
- Explain what rebase, push, sync, and merge change.
