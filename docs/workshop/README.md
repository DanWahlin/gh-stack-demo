# Agentic stacked PRs workshop

Use this workshop to build, test, publish, and review a three-layer stack with an AI coding agent. The 60-minute core workshop ends with three verified pull requests. The optional 15-minute extension covers lower-layer review feedback and team adoption.

GitHub Copilot CLI is the primary hands-on agent. GitHub Copilot cloud agent can help with planning, reviewing, or one isolated branch, but it cannot create the complete multi-branch stack in one task. Other agentic coding tools can be used when they load the repository instructions and can run the required terminal commands.

## Learning objectives

By the end of the workshop, learners can:

1. Decide whether work belongs in one stack, separate stacks, or a normal pull request.
2. Give a coding agent durable stack rules through `AGENTS.md`.
3. Evaluate and approve an agent-proposed stack before implementation.
4. Keep implementation and tests together in every layer.
5. Publish drafts, inspect live GitHub state, and separately approve readiness.
6. Explain how to update a lower layer without losing review boundaries.

## Required tools

Run the workshop from Bash or Zsh on macOS or Linux. On Windows, use Windows Subsystem for Linux (WSL) or Git Bash for the shell commands and workshop-copy script.

| Tool | Required | Validation |
| --- | --- | --- |
| Git | Yes | `git --version` |
| Node.js 20 or newer | Yes | `node --version` |
| GitHub CLI | Yes | `gh --version` and `gh auth status` |
| `github/gh-stack` | Yes | `gh stack --version` |
| GitHub Copilot CLI | Recommended | `copilot --version` |
| Another coding agent | Optional | Confirm that it can read repository instructions and run terminal commands |

## Create the learner repository

Do not fork the training repository. Create an isolated private repository in build mode:

```sh
git clone https://github.com/DanWahlin/gh-stacked-prs.git

gh-stacked-prs/scripts/create-workshop-copy.sh \
  YOUR-OWNER/my-stacked-prs-workshop \
  --build \
  --private
```

The script copies `main`, including `AGENTS.md`, but does not copy or create the training pull requests. Run the remaining labs from the new repository directory. See [Create a workshop repository](../workshop-copies.md) for ready mode and permission details.

Treat repository creation as prework. If learners create repositories during the session, add 5–10 minutes before the 60-minute core workshop.

## Core workshop map

| Lab | Topic | Time |
| --- | --- | --- |
| 0 | Agent and CLI preflight | 8 minutes |
| 1 | Plan and approve the stack | 7 minutes |
| 2 | Build the tested model layer | 10 minutes |
| 3 | Build the tested validation layer | 8 minutes |
| 4 | Build the tested API layer | 10 minutes |
| 5 | Verify, publish drafts, and mark ready | 17 minutes |

Optional extension:

| Lab | Topic | Time |
| --- | --- | --- |
| 6 | Respond to lower-layer feedback | 8 minutes |
| 7 | Team adoption discussion | 7 minutes |

Use a disposable learner repository. Do not run these labs in the public training repository.

## Lab 0: Agent and CLI preflight

### Objective

Verify the tools and confirm that the coding agent understands the repository rules before it changes code.

### Actions

Run these commands from the learner repository root:

```sh
git --version
node --version
gh --version
gh auth status
gh stack --version
git status --short --branch
```

Open [`AGENTS.md`](../../AGENTS.md) and read the approval boundaries.

### GitHub Copilot CLI

Start Copilot CLI from the learner repository root:

```sh
copilot
```

Run `/instructions` in the interactive session. Verify that `AGENTS.md` appears in the loaded instruction files.

Then enter this prompt:

```text
Read AGENTS.md. Do not modify files or run history-changing or remote commands.
Summarize:

1. When this repository requires one stack.
2. When work needs separate stacks or a normal pull request.
3. Which operations require explicit approval.
4. What evidence you must return before publishing anything.
```

Compare the response with `AGENTS.md`. Stop if the agent omits the approval boundaries or verification contract.

### GitHub Copilot cloud agent

The cloud agent loads repository custom instructions, but one cloud-agent task can work on only one branch and open one pull request. Use it to research the repository, propose the stack, review one layer, or prepare a single contribution for the local stack owner. Do not ask one cloud-agent task to create the complete three-branch stack. A cloud-agent session also has a 59-minute execution limit.

### Other coding agents

Other tools can participate. Before implementation, verify that the tool:

1. Loads `AGENTS.md` or an equivalent project instruction file.
2. Can run Git, `gh`, and `gh stack` from the learner repository.
3. Can stop before local history rewrites and remote operations.
4. Can report real command and test output.

### Checkpoint

The learner can identify the active instruction file and state every approval gate without relying on the agent's memory.

## Lab 1: Plan and approve the stack

### Objective

Require the agent to propose review boundaries before it writes code.

### Scenario

Build a small task API in three dependent layers:

```text
main
└── tasks/model
    └── tasks/validation
        └── tasks/api
```

### Planning prompt

Use a planning or read-only mode when the coding agent provides one. Restrict file writes and shell execution when the tool supports permission controls.

```text
Read AGENTS.md and inspect the repository. Do not modify files.

Plan this change as a stacked pull request workflow:

- tasks/model creates task objects with an ID, title, and completed=false.
- tasks/validation trims valid titles and rejects missing or blank titles.
- tasks/api adds a runnable POST /tasks endpoint with success and error responses.

Return:

1. The explicit trunk branch.
2. Branches ordered from bottom to top.
3. Responsibility and exclusions for each pull request.
4. Acceptance criteria and tests for each pull request.
5. Exact gh stack commands.
6. Layer-specific and full-stack verification commands.
7. Every operation that requires separate approval.

Wait for approval before implementation.
```

### Human review

Approve the plan only if:

- The branch order is `main → tasks/model → tasks/validation → tasks/api`.
- Every layer contains its own tests.
- No API code appears in the model or validation layer.
- The plan uses `gh stack init --base main tasks/model`.
- The plan stops before `rebase`, submission, push, synchronization, readiness changes, and merge.

### Checkpoint

The approved proposal has one responsibility and one green verification boundary per branch.

## Lab 2: Build the tested model layer

### Objective

Create the smallest independently reviewable foundation.

### Prompt

```text
The stack proposal is approved. Implement only tasks/model.

1. Run gh stack init --base main tasks/model.
2. Add a test that defines the task ID, title, and completed=false behavior.
3. Run the test before implementation and record the expected failure when practical.
4. Implement the minimum createTask behavior.
5. Run npm test.
6. Inspect the diff from main to tasks/model.
7. Commit the model and its test together with a focused message.

Stop after the local commit. Do not rebase, push, submit, synchronize, mark a
pull request ready, or merge.
```

### Checkpoint

Run:

```sh
npm test
gh stack view --json
git diff --stat main..tasks/model
```

Verify that `tasks/model` is green, based on `main`, and contains only the model and model test.

## Lab 3: Build the tested validation layer

### Objective

Add validation without mixing in the API boundary.

### Prompt

```text
Implement only tasks/validation above the committed tasks/model layer.

1. Run gh stack add tasks/validation.
2. Add tests for trimming a valid title and rejecting missing or blank titles.
3. Run the new tests and record the expected failure when practical.
4. Implement the minimum validation behavior in the task model.
5. Run npm test.
6. Inspect the diff from tasks/model to tasks/validation.
7. Commit the validation behavior and tests together.

Stop after the local commit. Do not rebase or perform any remote operation.
```

### Checkpoint

Run:

```sh
npm test
git diff --stat tasks/model..tasks/validation
```

Verify that the middle layer contains only validation behavior and its tests.

## Lab 4: Build the tested API layer

### Objective

Add the HTTP boundary above the validated model.

### Prompt

```text
Implement only tasks/api above the committed tasks/validation layer.

1. Run gh stack add tasks/api.
2. Add integration tests for a successful POST /tasks request and an invalid-title response.
3. Run the new tests and record the expected failure when practical.
4. Implement the minimum Node.js HTTP server and npm start command.
5. Run npm test.
6. Inspect the diff from tasks/validation to tasks/api.
7. Commit the API implementation and tests together.

Stop after the local commit. Do not rebase or perform any remote operation.
```

### Checkpoint

Run:

```sh
npm test
git diff --stat tasks/validation..tasks/api
gh stack view --json
```

Verify that the top layer contains only the API boundary, API tests, and required package-script change.

## Lab 5: Verify, publish drafts, and mark ready

### Objective

Separate local verification, remote publication, and readiness into observable approval gates.

### Step 1: Verify locally

Prompt the agent:

```text
Do not change files or perform remote operations.

Verify the complete stack and return:

1. gh stack view --json.
2. Branch ancestry from main through tasks/api.
3. Base, head, commit, and changed-file summary for every planned pull request.
4. Test result for every layer.
5. Full npm test result from tasks/api.
6. Any conflict, deviation, unexpected prompt, or unverified assumption.

Stop after reporting the evidence.
```

Review the real command output. Do not approve publication if any layer is uncommitted, stale, or failing.

### Step 2: Publish drafts

After the facilitator explicitly approves remote draft publication, run or authorize:

```sh
gh stack submit --auto
```

`--auto` skips the editor and creates new pull requests as drafts. Inspect the live pull requests and verify:

- `tasks/model` targets `main`.
- `tasks/validation` targets `tasks/model`.
- `tasks/api` targets `tasks/validation`.
- Every pull request is open and draft.
- Each changed-file list matches one layer.
- GitHub shows one linked stack.

Stop if the live state differs from the local proposal.

### Step 3: Mark the stack ready

After a separate facilitator approval, run or authorize:

```sh
gh stack submit --auto --open
```

Inspect GitHub again. Verify that all three pull requests are open, ready for review, correctly based, and still focused.

### Checkpoint

The learner can show the local stack, live stack, three correct base relationships, three focused diffs, and intentional readiness state.

## Optional Lab 6: Respond to lower-layer feedback

### Objective

Practice a lower-layer correction without hiding the resulting history change.

### Actions

1. Run `gh stack bottom`.
2. Make one requested model change and add or update its test.
3. Run the model tests and commit the correction.
4. Inspect `gh stack view --json`.
5. Request approval before running `gh stack rebase`.
6. After approval, run the rebase and resolve conflicts only when the intended result is clear.
7. Run `gh stack rebase --abort` if the resolution is uncertain.
8. Run the full tests from `tasks/api`.
9. Verify every layer diff again.
10. Request separate approval before `gh stack push` or `gh stack sync`.
11. Inspect every live pull request after the approved remote update.

A non-interactive `gh stack sync` stops rather than choosing a source of truth when local and remote stack definitions diverge. Do not bypass that stop condition.

### Checkpoint

Each pull request still has the correct base, head, readiness state, and focused diff after synchronization.

## Optional Lab 7: Team adoption discussion

Use [`../team-playbook.md`](../team-playbook.md) to agree on:

1. What qualifies for a stack.
2. Maximum stack size.
3. Required tests per layer.
4. Review order and ownership.
5. Which local and remote operations need approval.
6. How the team uses local agents versus Copilot cloud agent.
7. How the team handles independent workstreams.

## Completion criteria

The workshop is complete when each learner can:

- Explain why the three branches form one dependency chain.
- Show that the coding agent loaded the repository instructions.
- Evaluate an agent-generated stack proposal instead of accepting it blindly.
- Show one implementation-and-test boundary per pull request.
- Distinguish local implementation, draft publication, readiness, synchronization, and merge approvals.
- Verify live base branches, head branches, changed files, readiness, and stack linkage.
- Explain why a single Copilot cloud-agent task cannot own the complete multi-branch stack.
