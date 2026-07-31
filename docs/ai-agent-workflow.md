# Agentic coding workflow for stacked PRs

Repository instructions make stack planning and approval boundaries durable. Prompts define the current task. Optional skills can add command knowledge, but the workflow must remain usable when no specialized skill is installed.

## Instruction model

The root [`AGENTS.md`](../AGENTS.md) is the shared baseline for this repository. Treat it as repository-level agent instructions, not as the agent platform's true system prompt.

Before implementation, verify that the selected agent can:

1. Read `AGENTS.md` or an equivalent project instruction file.
2. Run Git, GitHub CLI, tests, and `gh stack` from the repository root.
3. Stop before local history rewrites and remote operations.
4. Return real command output instead of inferred success.

A `gh-stack` skill is optional. If one is available, the agent may load it. The agent must still follow `AGENTS.md` when a skill is missing or conflicts with repository policy.

## GitHub Copilot CLI

GitHub Copilot CLI is the primary hands-on agent for the workshop because it works in the local repository where `gh stack` stores and uses the branch stack.

Run:

```sh
copilot --version
copilot
```

In the interactive session, run `/instructions`. Verify that the root `AGENTS.md` appears. Use plan mode and restricted tool permissions for planning-only work. Do not grant broad automatic permissions merely to avoid approval prompts.

## GitHub Copilot cloud agent

GitHub Copilot cloud agent can research, plan, review, and make changes on one branch. A cloud-agent task can open one pull request and cannot own the complete multi-branch stack. A session also has a 59-minute execution limit.

Good uses in this workflow include:

- Researching the repository and proposing stack boundaries
- Reviewing one planned layer
- Implementing one isolated contribution that a local stack owner will integrate
- Reviewing live pull request diffs after submission

The local stack owner must integrate the contribution, create or adopt the stack branch, run the tests, inspect the diff, and verify local and live stack state. Cloud-agent branches do not carry the local stack owner's `.git/gh-stack` metadata.

## Other coding agents

Codex, Claude Code, Gemini CLI, Cursor, and other agentic coding tools can be used when they pass the same instruction-loading and terminal-access preflight. Some tools use different default instruction filenames. Configure the tool to load `AGENTS.md`, or provide an equivalent project instruction file without weakening the approval rules.

## Prompt 1: Propose the stack

```text
Read AGENTS.md and inspect the repository. Do not modify files.

Decide whether this work belongs in one stack, separate stacks, or a normal
pull request. Return:

1. Trunk branch.
2. Branches ordered from bottom to top.
3. Responsibility, exclusions, and acceptance criteria for each pull request.
4. Tests required in each layer.
5. Exact gh stack and verification commands.
6. Every operation that requires separate approval.

Wait for approval before implementation.
```

## Prompt 2: Implement one approved layer

```text
Implement only <branch-name> above <parent-branch>.

1. Create the layer with the approved gh stack command.
2. Add or update the layer tests first.
3. Run the tests and observe the expected failure when practical.
4. Implement only this layer's approved behavior.
5. Run the layer tests and applicable accumulated tests.
6. Inspect the diff against the parent branch.
7. Commit the implementation and tests together.

Stop after the local commit. Do not rebase or perform remote operations.
```

Repeat this prompt from bottom to top. Do not ask one agent to interleave independent workstreams in one checkout.

## Prompt 3: Verify before publication

```text
Do not change files or perform remote operations.

Return:

1. gh stack view --json.
2. Branch ancestry.
3. Parent-to-child diff and changed-file summary for every layer.
4. Layer-specific test results.
5. Full-stack test results from the top layer.
6. Any conflict, deviation, unexpected prompt, or unverified assumption.

Stop after reporting the evidence.
```

## Prompt 4: Publish drafts

Use this prompt only after a human explicitly approves remote draft publication:

```text
You are approved to run gh stack submit --auto for this stack only.
Do not mark pull requests ready and do not merge.

After submission, inspect the live pull requests and report each PR's URL,
draft state, base, head, changed files, and stack linkage. Stop if the live
state differs from the approved proposal.
```

`gh stack submit --auto` creates new pull requests as drafts. Command success alone is not proof that the live stack is correct.

## Prompt 5: Mark the stack ready

Use this prompt only after a separate human approval:

```text
You are approved to run gh stack submit --auto --open for this verified stack.
Do not merge.

After the command, inspect every live pull request and verify that its ready
state, base, head, changed files, and stack linkage remain correct.
```

## Prompt 6: Respond to lower-layer feedback

```text
Move to <lower-branch>. Implement only the approved review correction, update
its tests, run the layer tests, and commit locally.

Then report gh stack view --json and stop. Do not run gh stack rebase, push,
sync, or merge until each operation receives explicit approval.
```

After approval to rebase, the agent must rerun the full tests from the top layer and verify every diff. After separate approval to push or synchronize, it must inspect every live pull request again.

## Verification contract

Before requesting approval to publish drafts, the agent returns:

- `gh stack view --json`
- Branch ancestry verification
- Base and head for every planned pull request
- Layer-specific test results
- Full-stack test results from the top layer
- A file and commit summary for every layer
- Any conflicts, deviations, or unverified assumptions

After every remote or structural change, verify the live pull requests. Do not claim remote success until GitHub state has been inspected.

## Worktree pattern

Use separate worktrees for independent stacks:

```text
worktrees/authentication  → authentication stack
worktrees/billing         → billing stack
worktrees/notifications   → notifications stack
```

Use one write-capable agent per worktree. A planning or review agent may inspect another worktree in read-only mode.
