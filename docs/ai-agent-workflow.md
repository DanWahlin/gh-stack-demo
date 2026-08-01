# Agentic coding workflow for stacked PRs

Keep repository-wide rules in `AGENTS.md` and task details in the prompt. GitHub's official `gh-stack` skill adds command guidance, while the repository instructions still define how work must be planned, tested, approved, and verified.

## Supported agent experiences

### GitHub Copilot CLI

Install the official skill once at user scope. This avoids adding skill files to the repository's working tree:

```sh
gh skill install github/gh-stack gh-stack --agent github-copilot --scope user
copilot skill list
```

Start Copilot CLI from the repository root:

```sh
copilot
```

Run `/instructions`, Copilot CLI's view for custom instruction files, and verify that `AGENTS.md` is loaded. Confirm that `copilot skill list` includes `gh-stack`. Use plan mode or restricted permissions for planning-only work. Do not grant broad automatic permissions merely to avoid approval prompts.

The two sources have different jobs: the skill covers reusable `gh stack` behavior, while `AGENTS.md` defines this repository's planning, testing, approval, and verification contract. Keep the repository rules even when the skill is installed.

### GitHub Copilot desktop app

Open the repository in the [GitHub Copilot desktop app](https://github.com/features/ai/github-app). For the guided workshop, start a session in the **local repository** and reference `@AGENTS.md` in the first prompt.

The desktop app can isolate sessions in working trees or cloud sandboxes. This workshop uses a local-repository session so its diffs, terminal output, and pull request context refer to the same checkout. No extra customization is required.

### Other coding agents

Other tools can be used when they:

1. Load `AGENTS.md` or equivalent repository instructions.
2. Have terminal access to Git, GitHub CLI, tests, and `gh stack`.
3. Stop before operations that require approval.
4. Return real command output rather than inferred success.

## Workflow

### 1. Plan

```text
Read AGENTS.md and inspect the repository. Do not modify files.

Decide whether this work belongs in one stack, separate stacks, or a normal pull
request. Return the trunk, branch order, responsibility and exclusions for each
pull request, tests for each layer, exact gh stack commands, and final
verification commands. Wait for approval before implementation.
```

### 2. Implement one layer

```text
Implement only <branch> above <parent>.

Create the approved stack layer, implement only the approved behavior and its
tests, run the tests, inspect the diff against the parent, and commit the
implementation and tests together.

Stop after the local commit. Do not push, submit, synchronize, or merge.
```

Repeat from the bottom layer to the top. Use one write-capable agent per checkout or worktree.

### 3. Verify

```text
Do not change files or perform remote operations.

Return gh stack view --json, branch ancestry, base and head for every planned
pull request, parent-to-child changed files, layer-specific test results, the
full test result from the top layer, and any deviation or unverified assumption.
```

### 4. Submit

After a human approves the evidence, run or authorize:

```sh
gh stack submit --auto --open
```

Then inspect the live pull requests. Verify every base, head, changed-file list, readiness state, and stack relationship. Do not claim remote success from command exit status alone.

### 5. Respond to feedback

When a lower layer changes:

1. Update and test that layer.
2. Commit the correction.
3. Get approval before `gh stack rebase`.
4. Run the full tests from the top layer and inspect every diff.
5. Get approval before `gh stack push` or `gh stack sync`.
6. Inspect every live pull request after the update.

## Independent workstreams

Use separate worktrees and stacks for unrelated features:

```text
worktrees/authentication  → authentication stack
worktrees/billing         → billing stack
worktrees/notifications   → notifications stack
```

Do not ask one agent to interleave independent features in one stack merely because they belong to the same project.

## Verification contract

Before submission, the agent returns:

- `gh stack view --json`.
- Branch ancestry.
- Base, head, commit, and changed files for every planned pull request.
- Layer-specific test results.
- Full-stack test results from the top layer.
- Conflicts, deviations, and unverified assumptions.

After every approved remote or structural change, verify the live GitHub state again.
