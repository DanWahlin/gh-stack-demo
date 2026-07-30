# Video Script: GitHub Stacked PRs in Under 3 Minutes

**Target runtime:** 2:35 to 2:50  
**Format:** talking head for the hook and close, terminal plus GitHub for the demo

## Script and shot list

### 0:00–0:18 | Hook

**On camera**

> Ever open one giant pull request that mixes a data model, validation, and tests? Reviewers have to understand everything at once. GitHub's new Stacked PRs feature lets you split that work into small pull requests without waiting for each one to merge before starting the next.

### 0:18–0:35 | The mental model

**Show the three-branch diagram in this README or run `git log --oneline --graph --all`.**

> Think of it as a stack of dependent branches. The bottom PR targets `main`, the next PR targets that first branch, and the third targets the second. That means every review shows only one focused layer, while GitHub still displays the entire stack.

### 0:35–0:50 | Install

**Terminal**

```sh
gh extension install github/gh-stack
gh stack --version
```

> It's delivered as an official GitHub CLI extension. You need an authenticated GitHub CLI and a repository you can push to.

### 0:50–1:28 | Build the stack

**Use the prepared repository. Show the commands, but don't type or explain every code edit.**

```sh
gh stack init feature/task-model
# add and commit the task model

gh stack add feature/task-validation
# add and commit validation

gh stack add test/task-model
# add and commit tests

gh stack view
```

> `gh stack init` creates the first layer. After I commit the task model, `gh stack add` creates the next branch directly on top. I repeat that for validation and tests. `gh stack view` shows the order from `main` to the top of the stack, and navigation commands such as `up`, `down`, `top`, and `bottom` move between layers.

### 1:28–1:50 | Submit

**Terminal**

```sh
gh stack submit
```

> One submit command pushes the branches, creates the pull requests with the correct base branches, and links them as a Stack on GitHub. The interactive editor lets you set each title, description, and draft status before submitting.

### 1:50–2:18 | The payoff in GitHub

**Browser: open PR #3, point to the stack map, then the Files changed tab. Jump to PR #1 using the map.**

> Here's the payoff. GitHub adds a stack map to every pull request, so reviewers can jump between layers. This test PR shows only the tests, not the model and validation changes below it. Each PR is reviewed independently, but the full sequence stays visible.

### 2:18–2:40 | Keeping it current and merging

**Terminal, then briefly show the merge box without merging.**

```sh
gh stack rebase
gh stack push
# When everything is approved:
gh stack merge
```

> If a lower layer changes, `gh stack rebase` cascades that change through the branches and `gh stack push` updates them safely. When the stack is ready, merge the top PR to land the entire stack from bottom to top, or merge a lower PR to land only that portion.

### 2:40–2:52 | Close

**On camera**

> The big win is smaller reviews without serial development. I’ve linked this demo repository and GitHub's Stacked PRs docs so you can try it yourself.

## Recording runbook

1. Open a terminal at a readable 120–140 columns with the repo checked out on `test/task-model`.
2. Keep these commands in shell history:
   ```sh
   gh stack view
   gh stack bottom
   gh stack top
   npm test
   ```
3. Open browser tabs before recording:
   - PR #3 on **Files changed**
   - PR #1 on **Files changed**
   - GitHub Stacked PRs documentation
4. Record the interactive `gh stack submit` editor separately if you want clean B-roll. The prepared PRs already exist, so don't submit again during the final take.
5. Do not run `gh stack merge` in the published demo unless you're ready to destroy the open-stack visual. Show the command or merge UI, then cut away.
6. Use jump cuts over code edits. The story is branch layering, focused diffs, navigation, and merge behavior, not typing JavaScript.

## Reset/rehearsal commands

The checked-in `scripts/rehearse.sh` clones the repository into a temporary directory and verifies the stack, branch ancestry, PR bases, and tests without changing the public repository.

```sh
./scripts/rehearse.sh
```

## Accuracy notes worth keeping out of the main script

- All branches in a stack must be in the same repository. Cross-fork stacks aren't supported.
- A stack can contain up to 100 PRs and requires linear history.
- Every PR below the one being merged must meet reviews, checks, and branch rules.
- Direct stack merges are atomic. Merge queues evaluate queued PRs individually from bottom to top.
- Rule bypass and auto-merge are not currently supported for stacked PRs.
- GitHub Actions configured for the stack's base branch run for every PR in the stack. Stack metadata is available at `github.event.pull_request.stack`.
