# Create a workshop repository

Do not fork the training repository for the workshop. Forks do not copy pull requests, reviews, checks, or the GitHub stack object. They also make it easier to accidentally target the source repository with a learner pull request.

This repository is a GitHub template and supports two isolated workshop modes.

## Build mode: learners create the stack

Use build mode for the full hands-on workshop:

```sh
git clone https://github.com/DanWahlin/gh-stacked-prs-demo.git
gh-stacked-prs-demo/scripts/create-workshop-copy.sh \
  YOUR-OWNER/my-stacked-prs-workshop \
  --build \
  --private
```

The script creates a standalone repository from `main` and clones it locally. The learner then follows [`workshop/README.md`](workshop/README.md) to create and submit the stack.

Use a unique repository name. Change `--private` to `--public` only when the learner intends to publish the exercise.

## Ready mode: recreate the complete PR stack

Use ready mode for facilitators, shortened sessions, or recovery when a learner falls behind:

```sh
git clone https://github.com/DanWahlin/gh-stacked-prs-demo.git
gh-stacked-prs-demo/scripts/create-workshop-copy.sh \
  YOUR-OWNER/my-ready-stacked-prs-workshop \
  --ready \
  --private
```

Ready mode:

1. Creates a standalone repository from the template.
2. Creates the model, validation, and test branches.
3. Commits one focused change per branch.
4. Runs the complete tests.
5. Submits three open, ready-for-review pull requests.
6. Verifies each PR's base, head, draft state, and changed files.

The recreated PRs receive new numbers. Reviews, comments, checks, and PR history from the source repository are not copied.

## Required tools and permissions

- Git
- Node.js 20 or newer
- Authenticated GitHub CLI
- `github/gh-stack`
- Configured `git user.name` and `git user.email`
- Permission to create a repository under the selected owner

Verify the setup:

```sh
git --version
node --version
gh --version
gh auth status
gh stack --version
git config user.name
git config user.email
```

## Safety behavior

The script:

- Requires an explicit `--build` or `--ready` mode.
- Requires explicit `--public` or `--private` visibility.
- Refuses to reuse an existing GitHub repository.
- Refuses to overwrite an existing local directory.
- Never deletes a repository or local directory.
- Stops and reports the current state if setup or verification fails.
