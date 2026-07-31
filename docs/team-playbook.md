# Team playbook for stacked PRs

Use this playbook as a starting policy. Adjust the limits to match the team's review capacity and release process.

## When to use a stack

Use one stack when all of these conditions are true:

- The work has multiple independently reviewable layers.
- Higher layers depend on lower layers.
- Each layer can have explicit acceptance criteria.
- The team benefits from reviewing foundations before dependent behavior.

Use a normal pull request for a small isolated change. Use separate stacks, preferably in separate worktrees, for independent features.

## Recommended stack proposal

Before coding, post:

```text
Trunk: main

1. feature/domain
   Responsibility: Domain types and rules
   Acceptance: Domain tests pass

2. feature/api
   Responsibility: API that uses the domain layer
   Acceptance: API tests pass

3. feature/ui
   Responsibility: UI that calls the API
   Acceptance: UI and accessibility tests pass
```

A reviewer approves the boundaries before implementation begins.

## Team conventions

### Stack size

Start with two to five pull requests. Split larger stacks when reviewers cannot understand the complete dependency chain in one sitting.

### Branch names

Use one feature prefix across the stack:

```text
orders/domain-model
orders/api
orders/admin-ui
```

Names describe responsibility, not sequence numbers. The stack graph already communicates order.

### Pull request descriptions

Every PR states:

- Its responsibility
- Its base and head branches
- What is intentionally excluded
- Layer-specific test results
- The PR below and above it, when applicable
- Whether review should wait for a lower layer

### Test boundaries

Each layer must pass the tests relevant to that layer. The top layer must also pass the complete stack test suite. Do not defer all meaningful verification to the top PR.

### Review order

Review from bottom to top. Do not approve a higher layer while a foundational design issue remains unresolved below it. Review each PR against its stated responsibility, not against the entire final feature.

### Updating a stack

The stack author owns synchronization. Before synchronizing:

1. Commit or stash all work.
2. Fetch remote changes.
3. Confirm the current stack with `gh stack view --json`.
4. Run the applicable tests.
5. Tell active reviewers that commit IDs and diffs may change.

`gh stack rebase`, `gh stack push`, and `gh stack sync` can update commit history. Use them only on branches owned by the stack author and only under the team's agreed policy.

### Continuous integration

Run required checks on every PR. A lower layer must not depend on files that exist only in a higher layer. Keep end-to-end tests at the highest layer that contains all required components.

### Merge policy

Merge from the bottom through the approved layer. `gh stack merge` performs an atomic stack merge up to the selected PR, subject to GitHub branch protection and repository rules. Require explicit approval before invoking it.

### Independent workstreams

Do not interleave unrelated features in one stack. Use separate worktrees and stacks:

```text
Worktree A: authentication stack
Worktree B: billing stack
Worktree C: notifications stack
```

## Definition of ready

A stack is ready for review when:

- The branch order is documented.
- Every PR has the intended base and head.
- Every PR has a focused diff.
- Layer-specific tests pass.
- Full-stack tests pass at the top.
- No PR contains unrelated formatting or generated-file churn.
- The author has identified known risks and deferred work.

## Definition of done

A stack is done when:

- Required reviews and checks pass.
- The approved layers merge successfully.
- Trunk CI passes after the merge.
- Local branches are pruned according to team policy.
- Follow-up work is tracked outside the completed stack.

## AI coding agents

Repository agents must follow the root [`AGENTS.md`](../AGENTS.md). Agents propose the stack before coding and stop before pushing, submitting PRs, or merging unless a human explicitly approves the action.
