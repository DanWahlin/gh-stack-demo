# Facilitator guide

Use the repository's [PowerPoint deck](../github-stacked-prs.pptx) with this guide. The deck remains the source of truth for presentation visuals and animations.

## Fifteen-minute briefing

| Time | Activity |
| --- | --- |
| 0–3 minutes | Explain the problem with one large dependent change |
| 3–6 minutes | Draw the branch and PR graph |
| 6–10 minutes | Inspect the three live pull requests |
| 10–13 minutes | Demonstrate `gh stack view` and focused diffs |
| 13–15 minutes | Explain when not to use a stack and take questions |

## Sixty-minute workshop

| Time | Activity |
| --- | --- |
| 0–10 minutes | Slides and mental model |
| 10–15 minutes | Preflight and stack decision |
| 15–35 minutes | Create three layers |
| 35–45 minutes | Submit and inspect PRs |
| 45–52 minutes | Lower-layer feedback and rebase discussion |
| 52–60 minutes | Team policy and knowledge check |

Run the exercises from [`workshop/README.md`](workshop/README.md).

## Prepare learner repositories

Use build mode for the full workshop. Each learner creates the stack:

```sh
scripts/create-workshop-copy.sh \
  YOUR-OWNER/my-stacked-prs-workshop \
  --build \
  --private
```

Use ready mode for a shortened session, facilitator rehearsal, or learner recovery. It recreates the three PRs and verifies them:

```sh
scripts/create-workshop-copy.sh \
  YOUR-OWNER/my-ready-stacked-prs-workshop \
  --ready \
  --private
```

Do not use forks. Forks do not copy the pull requests or GitHub stack relationship. See [Create a workshop repository](workshop-copies.md) for the complete setup contract.

## Demo preflight

Complete these checks before the session:

```sh
gh auth status
gh stack --version
gh pr list --repo DanWahlin/gh-stacked-prs-demo --state open --head workshop/task-model --json number,baseRefName,headRefName,files
gh pr list --repo DanWahlin/gh-stacked-prs-demo --state open --head workshop/task-validation --json number,baseRefName,headRefName,files
gh pr list --repo DanWahlin/gh-stacked-prs-demo --state open --head workshop/task-tests --json number,baseRefName,headRefName,files
```

Verify that the three PRs are open, ready for review, and focused. Keep screenshots available in case network access fails.

## Teaching sequence

1. Show the monolithic-change problem.
2. Draw the branch graph.
3. Draw the corresponding PR base graph.
4. Open PR #1 and identify its base, head, and one-file diff.
5. Repeat for PRs #2 and #3.
6. Run `gh stack view --json` and connect the output to the GitHub UI.
7. Ask learners to classify dependent and independent scenarios.
8. Run the hands-on workshop.
9. Finish with the team playbook, not another command tour.

## Expected questions

### Why not open every PR against `main`?

Dependent PRs would include lower-layer changes in every higher-layer diff. Targeting the branch below isolates each review boundary.

### Can several people work on one stack?

They can, but rebasing and force-with-lease updates require coordination. A single stack owner is the safer default.

### Does every layer need tests?

Each layer needs enough verification to be independently reviewable. Full end-to-end tests belong at the highest layer that contains all required components.

### What happens when `main` changes?

Rebase or synchronize the stack, rerun tests, and verify every PR diff before asking reviewers to continue.

### Should every large feature use a stack?

No. Stack only linear dependencies. Independent work belongs in separate branches or stacks.

## Knowledge check

1. Which branch does the middle PR target?
2. Why should review normally start at the bottom?
3. When should two features use separate stacks?
4. What must be verified after a lower-layer rebase?
5. Which operations require explicit approval from an AI agent?

Answers:

1. The branch immediately below it.
2. Higher layers depend on decisions made below.
3. When the features do not form one dependency chain.
4. Tests, ancestry, PR bases, focused diffs, and PR state.
5. Push, PR submission, merge, and other remote mutations.

## Reset and fallback

- Use a disposable learner repository for mutations.
- Keep the public validated stack open for inspection.
- Do not merge or rewrite the public demonstration branches during a class.
- If live GitHub access fails, use the deck and captured screenshots, then demonstrate local `gh stack view --json` output.
