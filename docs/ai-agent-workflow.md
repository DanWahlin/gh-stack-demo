# AI-agent workflow for stacked PRs

Repository rules make stack planning explicit. Skills add specialized command knowledge, but semantic skill triggering alone is not a reliable control.

## Setup

1. Install or synchronize a `gh-stack` skill into the coding agent's active profile.
2. Verify that the agent can list and load the skill.
3. Keep the root [`AGENTS.md`](../AGENTS.md) under version control.
4. Start work with an explicit kickoff prompt.

Hermes profiles isolate their skills. Installing a skill in one profile does not guarantee that another profile can load it. Verify availability in the profile that will execute the work.

## Kickoff prompt

```text
Build authentication, its API endpoints, and the account UI. Before coding,
inspect the repository and decide whether this should use gh-stack. Show me:

1. The trunk branch.
2. Branch names ordered from bottom to top.
3. Responsibility and acceptance criteria for each pull request.
4. The layer-specific and full-stack verification commands.
5. Any work that should use a separate stack or normal pull request.

Wait for my approval before implementing. After implementation, stop again
before pushing branches, submitting pull requests, or merging.
```

## Expected proposal

```text
Trunk: main

1. auth/domain-model
   Responsibility: Identity types and validation rules
   Acceptance: Domain unit tests pass

2. auth/api
   Responsibility: Authentication endpoints using the domain layer
   Acceptance: API integration tests pass

3. auth/account-ui
   Responsibility: Account screens using the API
   Acceptance: UI and accessibility tests pass

4. auth/e2e-tests
   Responsibility: Full authentication journey
   Acceptance: End-to-end tests pass
```

## Agent verification contract

Before requesting approval to submit, the agent returns:

- `gh stack view --json` output
- Branch ancestry verification
- Base and head for every proposed PR
- Test results for every layer
- Full-stack test results from the top layer
- A file or commit summary for every PR
- Any conflicts, deviations, or unverified assumptions

The agent must not claim remote success until it inspects the live GitHub PRs.

## Worktree pattern

Use separate worktrees for independent stacks:

```text
worktrees/authentication  → authentication stack
worktrees/billing         → billing stack
worktrees/notifications   → notifications stack
```

Do not ask one agent to interleave independent features in one stack merely because they belong to the same project.
