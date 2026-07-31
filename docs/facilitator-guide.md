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

## Sixty-minute agentic workshop

| Time | Activity |
| --- | --- |
| 0–8 minutes | Verify the learner repository, tools, and agent instructions |
| 8–15 minutes | Ask the agent to propose the stack and review its plan |
| 15–25 minutes | Build and test `tasks/model` |
| 25–33 minutes | Build and test `tasks/validation` |
| 33–43 minutes | Build and test `tasks/api` |
| 43–60 minutes | Verify, publish drafts, inspect GitHub, and mark ready |

Use the optional 15-minute extension for lower-layer feedback and team adoption. Do not compress approval and live-verification checkpoints merely to fit them into one hour.

Run the exercises from [`workshop/README.md`](workshop/README.md).

## Prepare learner repositories

Treat repository creation as prework for the 60-minute agenda. Add 5–10 minutes if learners must create repositories during the session.

Use build mode for the full workshop. Each learner and coding agent create the stack:

```sh
scripts/create-workshop-copy.sh \
  YOUR-OWNER/my-stacked-prs-workshop \
  --build \
  --private
```

Use ready mode for a shortened session, facilitator rehearsal, or learner recovery. It recreates the three pull requests and verifies them:

```sh
scripts/create-workshop-copy.sh \
  YOUR-OWNER/my-ready-stacked-prs-workshop \
  --ready \
  --private
```

Do not use forks. Forks do not copy pull requests or the GitHub stack relationship. See [Create a workshop repository](workshop-copies.md) for the complete setup contract.

## Coding-agent roles

### GitHub Copilot CLI

Use Copilot CLI for the hands-on workflow. It operates in the learner's local repository and can use the local Git branches and `gh stack` metadata.

Before the workshop:

```sh
copilot --version
```

During Lab 0, ask learners to run `/instructions` and confirm that `AGENTS.md` is loaded.

### GitHub Copilot cloud agent

Use Copilot cloud agent for planning, research, review, or one isolated branch contribution. Do not demonstrate it as the owner of the complete stack. A cloud-agent task can work on only one branch and open one pull request. Its session limit is 59 minutes. The local stack owner must integrate and verify any cloud-agent contribution.

### Other coding agents

Other agentic coding tools can be used. Require the learner to prove that the tool loaded equivalent repository instructions, has terminal access, and respects every approval gate.

## Facilitator preflight

Complete these checks before the session:

```sh
gh auth status
gh stack --version
copilot --version
gh pr list --repo DanWahlin/gh-stacked-prs --state open --head tasks/model --json number,baseRefName,headRefName,files
gh pr list --repo DanWahlin/gh-stacked-prs --state open --head tasks/validation --json number,baseRefName,headRefName,files
gh pr list --repo DanWahlin/gh-stacked-prs --state open --head tasks/api --json number,baseRefName,headRefName,files
```

Verify that the three canonical pull requests are open, ready for review, and focused. Keep screenshots available if network access fails.

Prepare one build-mode learner repository and rehearse the prompts. Agent output can vary. Judge the output against the rubric instead of expecting identical wording.

## Agent-plan rubric

Approve a proposed stack only when it includes:

- Explicit trunk `main`
- `tasks/model`, `tasks/validation`, and `tasks/api` in that order
- One responsibility and explicit exclusions per layer
- Implementation and tests together in every layer
- `gh stack init --base main tasks/model`
- Local verification before remote publication
- Draft publication before readiness
- Explicit approval before rebase, submission, push, synchronization, readiness, and merge
- Live GitHub verification after every approved remote change

Reject the plan if the agent:

- Puts all tests in the top layer
- Opens all pull requests against `main`
- Uses `gh pr create` instead of `gh stack submit`
- Treats cloud agent as capable of creating the complete stack in one task
- Requests broad automatic permissions without a workshop need
- Plans to force-push or merge without approval

## Teaching sequence

1. Show the monolithic-change problem.
2. Draw the branch graph and corresponding pull request base graph.
3. Explain that `AGENTS.md` provides standing rules while the learner prompt provides the current task.
4. Verify that the coding agent loaded the instructions.
5. Ask the agent to propose the stack before coding.
6. Make learners inspect and approve the proposal.
7. Implement one tested layer at a time.
8. Review local evidence before approving draft publication.
9. Inspect live drafts before approving readiness.
10. Finish with human ownership and team policy, not another command tour.

## Approval calls

Use explicit language at each boundary:

1. **Plan approval:** “The branch boundaries are approved. Implement locally one layer at a time.”
2. **Draft-publication approval:** “You may run `gh stack submit --auto` for this stack.”
3. **Readiness approval:** “The live drafts are correct. You may run `gh stack submit --auto --open`.”
4. **Rebase approval:** “The local lower-layer correction is correct. You may run `gh stack rebase`.”
5. **Remote-update approval:** “The rebased stack and tests are correct. You may push or synchronize.”
6. **Merge approval:** Give only after required reviews and checks pass. Always name the intended merge method.

Do not use one broad approval such as “finish the stack” to cover every later operation.

## Common workshop failures

### The agent did not load `AGENTS.md`

Stop before implementation. Restart the agent from the learner repository root or configure its project instruction file. Ask it to summarize the approval boundaries again.

### The agent modifies more than one layer

Do not move the extra work to the next branch automatically. Revert or separate the unrelated change, rerun the current layer tests, and inspect the parent-to-child diff.

### The agent skips the failing-test observation

Require the learner to explain why the test would fail before implementation. Record a real failing run when practical, but do not introduce artificial failure only for ceremony.

### Submission creates drafts

That is the intended first remote stage. Inspect the draft pull requests before granting readiness approval.

### Synchronization reports divergence

Stop. Agree whether local or GitHub state is authoritative before running another synchronization command. Non-interactive synchronization must not guess.

## Expected questions

### Why not open every pull request against `main`?

Dependent pull requests would include lower-layer changes in every higher-layer diff. Targeting the branch below isolates each review boundary.

### Why publish drafts first?

Drafts create observable GitHub state without telling reviewers that the stack is ready. The team can verify bases, heads, files, and linkage before a separate readiness decision.

### Can Copilot cloud agent build the complete stack?

Not in one task. A cloud-agent task works on one branch and opens one pull request. Use Copilot CLI or another local agent for the complete stack, or integrate cloud-agent contributions one branch at a time.

### Does every layer need tests?

Each layer needs enough verification to be independently reviewable. Full end-to-end tests belong at the highest layer that contains all required components.

### Can several people or agents work on one stack?

They can, but one stack owner must integrate branches and own synchronization. Use separate worktrees for independent work and never let multiple write-capable agents share one checkout.

## Knowledge check

1. Which branch does the middle pull request target?
2. Why must the agent propose the stack before coding?
3. What is the first approved remote submission command?
4. What must be verified before the drafts are marked ready?
5. Why can a single cloud-agent task not create the full stack?
6. Which local operation needs approval because it rewrites commit IDs?

Answers:

1. `tasks/model`.
2. Humans must approve review and test boundaries before implementation creates coupling.
3. `gh stack submit --auto`.
4. Live draft state, bases, heads, focused changed files, tests, and stack linkage.
5. It can work on one branch and open one pull request per task.
6. `gh stack rebase`.

## Reset and fallback

- Use a disposable learner repository for mutations.
- Keep the public canonical stack open for inspection.
- Do not merge or rewrite the canonical demonstration branches during class.
- If Copilot CLI is unavailable, use another local coding agent or run the prompts as facilitator-led planning exercises.
- If live GitHub access fails, use the deck and captured screenshots, then demonstrate local `gh stack view --json` output.
