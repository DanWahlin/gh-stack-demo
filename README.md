# Learn GitHub Stacked PRs

<p align="center">
  <img src="images/gh-stacked-prs.png" alt="Three dependent pull requests shown as a stack" width="350" height="344">
</p>

Learn GitHub Stacked PRs through a live three-PR stack, a GitHub CLI walkthrough, and an agentic workshop.

## Choose a path

- **5 minutes:** Learn [how stacked PRs work](#how-stacked-prs-work)
- **15 minutes:** [Review the live stack](docs/review-walkthrough.md)
- **45–60 minutes:** [Build the canonical stack using the GitHub CLI (gh)](docs/build-the-stack.md)
- **55 minutes:** Create a learner repository then run the [agentic workshop](docs/workshop/README.md)
- **Training:** Use the [PowerPoint deck](https://github.com/DanWahlin/learn-github-stacked-prs/raw/refs/heads/main/github-stacked-prs.pptx) and [facilitator guide](docs/facilitator-guide.md)

Keep the [`gh stack` cheat sheet](docs/cheat-sheet.md), [troubleshooting guide](docs/troubleshooting.md), and [glossary](docs/glossary.md) nearby after training.

## How stacked PRs work

A stacked pull request is one reviewable layer in a linear dependency chain. Each branch starts from the branch below it, and each pull request targets that lower branch. Reviewers see the change introduced by one layer instead of every change accumulated above `main`.

```mermaid
flowchart BT
    Main["main"] --> Model["tasks/model"]
    Model --> Validation["tasks/validation"]
    Validation --> API["tasks/api"]
```

| Ordinary pull request | Stacked pull requests |
| --- | --- |
| One branch targets `main` | Each branch targets the layer below it |
| One potentially large review | Several focused reviews |
| Dependencies can be hidden inside one diff | Dependencies are explicit in the branch graph |
| Best for an isolated change | Best for linear dependent changes |

Review normally starts at the bottom because higher layers depend on decisions made below.

### Decide whether to use a stack

```mermaid
flowchart TD
    Multiple{"Multiple reviewable changes?"}
    Multiple -- No --> Normal["Use a normal branch and pull request"]
    Multiple -- Yes --> Linear{"One linear dependency chain?"}
    Linear -- Yes --> Stack["Use one stack"]
    Linear -- No --> Separate["Use separate branches or stacks"]
```

Examples:

- Model → validation → API: one stack
- Authentication and billing: separate stacks
- One isolated bug fix: one normal pull request
- Shared foundation followed by independent features: one foundational pull request, then separate stacks

## Canonical live stack

The open pull requests in this repository provide a stable example for workshops and reviews:

| Layer | Pull request | Base | Head | Changed files | Tests on branch |
| --- | --- | --- | --- | --- | --- |
| Model | [PR #21](https://github.com/DanWahlin/learn-github-stacked-prs/pull/21) | `main` | `tasks/model` | `src/tasks.js`, `test/tasks.model.test.js` | 1 |
| Validation | [PR #22](https://github.com/DanWahlin/learn-github-stacked-prs/pull/22) | `tasks/model` | `tasks/validation` | `src/tasks.js`, `test/tasks.validation.test.js` | 4 |
| API | [PR #23](https://github.com/DanWahlin/learn-github-stacked-prs/pull/23) | `tasks/validation` | `tasks/api` | `package.json`, `src/server.js`, `test/tasks.api.test.js` | 6 |

Each pull request contains implementation and tests for its own behavior. The [training-resource workflow](https://github.com/DanWahlin/learn-github-stacked-prs/actions/workflows/verify-training-resource.yml) checks the documented pull request boundaries and runs the tests on every canonical branch.

## Hands-on requirements

- Bash or Zsh on macOS or Linux. On Windows, use WSL or Git Bash.
- Git 2.20 or newer, with `user.name` and `user.email` configured
- Node.js 20 or newer
- GitHub CLI 2.90 or newer, authenticated to GitHub
- Permission to create or push to a GitHub repository
- The [`github/gh-stack`](https://github.com/github/gh-stack) extension

Verify the setup:

```sh
git --version
git config user.name
git config user.email
node --version
gh --version
gh auth status
gh stack --version
```

If `gh stack --version` reports that `gh stack` is unavailable, install the extension once:

```sh
gh extension install github/gh-stack
```

## Learn with an AI coding agent

The root [`AGENTS.md`](AGENTS.md) gives coding agents the stack-selection rules, command contract, test boundaries, approval gates, and verification requirements.

The workshop focuses on:

- [GitHub Copilot](https://github.com/features/copilot)
- [GitHub Copilot CLI](https://github.com/features/copilot/cli)
- [GitHub Copilot desktop app](https://github.com/features/ai/github-app)

Other agentic coding tools can be used when they load the repository guidance and can run Git, GitHub CLI, tests, and `gh stack`.

For the GitHub Copilot CLI path, install GitHub's official `gh-stack` agent skill before starting the workshop:

```sh
gh skill install github/gh-stack
copilot skill list
```

When prompted, choose the `gh-stack` skill, GitHub Copilot, and user scope. User scope keeps the learner repository clean.

The skill gives Copilot reusable `gh stack` command and recovery guidance. The repository's [`AGENTS.md`](AGENTS.md) defines the project-specific boundaries, approvals, and verification rules. See GitHub's [Stack AI-generated code in pull requests](https://docs.github.com/copilot/tutorials/stack-ai-generated-code-in-pull-requests) tutorial for the official skill-based workflow.

Start with a planning-only prompt:

```text
Read AGENTS.md and inspect the repository. Do not modify files.

Propose the trunk, branch order, responsibility and tests for each pull request,
exact gh stack commands, and final verification commands. Wait for approval
before implementation.
```

The [agentic workshop](docs/workshop/README.md) provides the complete prompt sequence from planning through feedback.

## Create a learner repository

Do not fork this repository. Forks do not copy pull requests, reviews, checks, or the GitHub stack relationship.

Use the repository-copy script instead:

```sh
git clone https://github.com/DanWahlin/learn-github-stacked-prs.git
node learn-github-stacked-prs/scripts/create-workshop-copy.mjs YOUR-OWNER/my-stacked-prs-workshop --build --private
```

Build mode lets learners create the stack. Ready mode recreates the complete canonical stack for facilitator rehearsal, shortened sessions, or recovery. See [Create a workshop repository](docs/workshop-copies.md).

## Contributing

See [CONTRIBUTING.md](CONTRIBUTING.md). The repository is licensed under the [MIT License](LICENSE).
