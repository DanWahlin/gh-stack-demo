# Facilitator guide

Use the repository's [PowerPoint deck](../github-stacked-prs.pptx) with this guide. The deck remains the source of truth for presentation visuals and animations.

## Fifteen-minute briefing

| Time | Activity |
| --- | --- |
| 0–3 minutes | Explain the problem with one large dependent change |
| 3–6 minutes | Draw the branch and pull request graph |
| 6–10 minutes | Inspect the three live pull requests |
| 10–13 minutes | Demonstrate `gh stack view` and focused diffs |
| 13–15 minutes | Explain when not to use a stack and take questions |

## Fifty-five-minute workshop

Treat learner-repository creation as prework. Add 5–10 minutes if learners must create repositories during the session.

| Time | Activity |
| --- | --- |
| 0–5 minutes | Verify the tools and agent instructions |
| 5–15 minutes | Ask the agent to propose the stack and review its plan |
| 15–35 minutes | Build and test three layers |
| 35–45 minutes | Verify, submit, and inspect the live pull requests |
| 45–55 minutes | Demonstrate lower-layer feedback |

Run the exercises from the [agentic workshop](workshop/README.md).

## Prepare learner repositories

Use build mode for the full workshop:

```sh
node scripts/create-workshop-copy.mjs YOUR-OWNER/my-stacked-prs-workshop --build --private
```

Use ready mode for a shorter session, facilitator rehearsal, or learner recovery:

```sh
node scripts/create-workshop-copy.mjs YOUR-OWNER/my-ready-stacked-prs-workshop --ready --private
```

Do not use forks. Forks do not copy pull requests or the GitHub stack relationship. See [Create a workshop repository](workshop-copies.md) for the setup contract.

## Agent setup

### [GitHub Copilot](https://github.com/features/copilot)

Open the learner repository in a supported IDE and use agent mode from the repository workspace. Confirm that `AGENTS.md` is applied and that the agent can run the required terminal commands.

### [GitHub Copilot CLI](https://github.com/features/copilot/cli)

Install GitHub's official `gh-stack` skill:

```sh
gh skill install github/gh-stack gh-stack --agent github-copilot --scope user
copilot skill list
```

User scope makes the skill available to Copilot CLI and the GitHub Copilot app while keeping the learner repository clean.

Then start Copilot CLI. Ask learners to run `/instructions`, the view for custom instruction files, and confirm that `AGENTS.md` is loaded. The skill provides reusable CLI expertise; `AGENTS.md` remains the authority for workshop boundaries and approvals.

### [GitHub Copilot app](https://github.com/features/ai/github-app)

Open the learner repository in the app and start the workshop session in the **local repository**. Confirm that `gh-stack` appears under **Settings → Skills**, then reference `@AGENTS.md` and `/gh-stack` in the first prompt.

### Other tools

Other AI coding tools are acceptable when they load the repository instructions, can run the required terminal commands, and respect the same approval boundaries.

## Facilitator preflight

Run:

```sh
gh auth status
gh --version
gh stack --version
gh pr list --repo DanWahlin/learn-github-stacked-prs --state open --head tasks/model --json number,baseRefName,headRefName,files
gh pr list --repo DanWahlin/learn-github-stacked-prs --state open --head tasks/validation --json number,baseRefName,headRefName,files
gh pr list --repo DanWahlin/learn-github-stacked-prs --state open --head tasks/api --json number,baseRefName,headRefName,files
```

For a GitHub Copilot CLI session, also run `copilot skill list` and confirm that `gh-stack` appears. The official skill is invoked as `/gh-stack`. `/pr-stack` is not supplied by `github/gh-stack`; if it appears, inspect **Settings → Skills** because it may come from a separate custom or third-party skill.

Verify that the canonical pull requests are open, ready for review, and focused. Rehearse the workshop prompts in one build-mode repository. Agent wording can vary; evaluate the output against the rubric.

## Stack-plan rubric

Approve the plan only when it includes:

- Trunk `main`
- `tasks/model`, `tasks/validation`, and `tasks/api` in that order
- One responsibility and explicit exclusions per layer
- Implementation and tests together in every layer
- `gh stack init --base main tasks/model`
- Local verification before submission
- Approval before push, submission, synchronization, or merge
- Live GitHub verification after submission

Reject the plan if the agent opens every pull request against `main`, puts all tests in the top layer, uses `gh pr create`, mixes layer responsibilities, or plans remote operations without approval.

## Teaching sequence

1. Show the monolithic-change problem
2. Draw the branch graph and pull request base graph
3. Explain that `AGENTS.md` contains standing rules while the prompt defines the current task
4. Verify that the agent understood the instructions
5. Require a stack proposal before coding
6. Make learners approve the review and test boundaries
7. Implement and verify one layer at a time
8. Review local evidence before approving submission
9. Inspect every live pull request
10. Finish with team ownership and policy

## Common failures

### The agent did not use `AGENTS.md`

Stop before implementation. Restart from the learner repository or reference `@AGENTS.md`, then ask the agent to summarize the rules again.

### The agent modifies more than one layer

Separate or revert the extra work. Rerun the current layer tests and inspect its diff before continuing.

### Synchronization reports divergence

Stop. Agree whether local or GitHub state is authoritative before running another synchronization command.

## Expected questions

### Why not open every pull request against `main`?

Higher pull requests would include lower-layer changes. Targeting the branch below isolates each review boundary.

### How do I keep the stack current when a lower branch changes?

Run `gh stack view --json` to inspect branch order and `needsRebase`. For routine synchronization, `gh stack sync` performs the full fetch, reconcile, conditional rebase, push, and pull request and stack synchronization loop. The workshop instead uses a checkpointed branch-update workflow: `gh stack rebase`, tests and diff inspection, then `gh stack push`. That path keeps a review checkpoint before changing remote branches, but it does not reconcile local and remote stack definitions or update the remote stack object.

### Does every layer need tests?

Each layer needs enough verification to be independently reviewable. Full end-to-end tests belong at the highest layer that contains all required components.

### Can several people or agents work on one stack?

They can, but one stack owner must integrate changes and own synchronization. Use separate worktrees for independent work and one write-capable agent per checkout.

## Knowledge check

1. Which branch does the validation pull request target?
2. Why must the agent propose the stack before coding?
3. Which command submits the approved stack non-interactively and marks it ready?
4. What must be verified after submission?
5. Which operation rewrites local commit IDs?

Answers:

1. `tasks/model`
2. Humans must approve review and test boundaries before implementation creates coupling
3. `gh stack submit --auto --open`
4. Live bases, heads, changed files, readiness, tests, and stack linkage
5. `gh stack rebase`

## Fallback

- Keep the public canonical stack open for inspection
- Do not merge or rewrite canonical demonstration branches during class
- If an agent is unavailable, use the prompts as facilitator-led planning exercises
- If GitHub access fails, use screenshots and demonstrate local `gh stack view --json` output
