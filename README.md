# GitHub Stacked PRs

<p align="center">
  <img src="images/gh-stacked-prs.png" alt="Three dependent pull requests shown as a stack" width="350" height="344">
</p>

A tiny Node.js task API built as three focused pull requests to demonstrate [GitHub's Stacked PRs feature](https://docs.github.com/pull-requests/how-tos/stacked-pull-requests) and the `gh stack` CLI extension.

## Choose your path

- **5 minutes:** Read [How stacked PRs work](#how-stacked-prs-work).
- **15 minutes:** Follow the [live-stack review walkthrough](docs/review-walkthrough.md).
- **30 minutes:** Follow [Commands used to create this demo](#commands-used-to-create-this-demo).
- **45–60 minutes:** [Create an isolated workshop repository](docs/workshop-copies.md), then run the [team workshop](docs/workshop/README.md).
- **Team leads:** Adapt the [team playbook](docs/team-playbook.md) and [full lifecycle](docs/lifecycle.md).
- **Facilitators:** Use the [presentation and facilitator guide](docs/facilitator-guide.md).
- **AI-assisted teams:** Configure the [AI-agent workflow](docs/ai-agent-workflow.md).

Keep the [`gh stack` cheat sheet](docs/cheat-sheet.md), [glossary](docs/glossary.md), and [troubleshooting guide](docs/troubleshooting.md) nearby after training.

## How stacked PRs work

A stacked pull request is one reviewable layer in a linear dependency chain. Each branch starts from the branch below it, and each pull request targets that lower branch. Reviewers see the change introduced by one layer instead of every change accumulated above `main`.

| Ordinary pull request | Stacked pull requests |
| --- | --- |
| One branch targets `main` | Each branch targets the layer below it |
| One potentially large review | Several focused reviews |
| Dependencies can be hidden inside one diff | Dependencies are explicit in the branch graph |
| Best for an isolated change | Best for linear dependent changes |

Review normally starts at the bottom because higher layers depend on decisions made below. Every layer must remain independently testable and reviewable.

### Decide whether to use a stack

```text
Does the work contain multiple reviewable changes?
├── No → Use a normal branch and pull request
└── Yes
    └── Do the changes form one linear dependency chain?
        ├── Yes → Use one stack
        └── No → Use separate branches or separate stacks
```

Examples:

- Database model → API → UI: one stack
- Authentication and billing: separate stacks
- Small typo and its test: one normal pull request
- Shared foundation followed by two independent features: foundational pull request, then separate stacks

## Presentation

Need to bring your team up to speed on GitHub Stacked PRs? [Download the latest PowerPoint deck](https://github.com/DanWahlin/gh-stacked-prs/raw/refs/heads/main/github-stacked-prs.pptx) to use for a quick presentation. It includes the challenge stacked PRs address, high-level concept, CLI workflow, and a start-to-finish terminal example.

## Planned stack

1. [`tasks/model`](https://github.com/DanWahlin/gh-stacked-prs/pulls?q=is%3Apr+head%3Atasks%2Fmodel) adds the task model and its unit test.
2. [`tasks/validation`](https://github.com/DanWahlin/gh-stacked-prs/pulls?q=is%3Apr+head%3Atasks%2Fvalidation) adds title validation and its unit tests.
3. [`tasks/api`](https://github.com/DanWahlin/gh-stacked-prs/pulls?q=is%3Apr+head%3Atasks%2Fapi) adds `POST /tasks` and API integration tests.

Each PR targets the branch below it, so reviewers see only that layer's changes.

The linked pull requests live in this repository. They remain open so teams can inspect each base branch, commit, and focused diff without changing the training artifact.

## Requirements

- Node.js LTS
- GitHub CLI 2.0 or newer
- [`github/gh-stack`](https://github.com/github/gh-stack)

Verify the extension is available:

```sh
gh stack --version
```

If that command is unavailable, install the extension once:

```sh
gh extension install github/gh-stack
```

## Use stacked PRs with an AI coding agent

This repository includes an [`AGENTS.md`](AGENTS.md) rule that helps coding agents decide whether a substantial multi-part change belongs in a stacked pull request workflow.

For the best results, make the `gh-stack` skill available to your coding agent. Ask the agent to load the skill before it plans or implements the change. Then start with a prompt such as:

```text
Build authentication, its API endpoints, and the account UI. Before coding,
inspect the repository and decide whether this should be a gh-stack. Show me
the proposed branch stack and verification boundary for each pull request.
Wait for my approval before implementing, pushing branches, or submitting
pull requests.
```

Use one stack when the changes form a linear dependency chain:

```text
main
└── auth/domain-model
    └── auth/api
        └── auth/account-ui
            └── auth/e2e-tests
```

Use separate stacks, preferably in separate worktrees, for independent features. Use a normal branch and pull request for a small isolated change. The repository's `AGENTS.md` contains the complete decision and safety rules for coding agents.

## Commands used to create this demo

The sequence below is a complete, tested reproduction of this repository's three-PR stack. It creates every required file, publishes `main`, builds each layer, runs the tests, and submits the stack. It was validated with Node.js 24.18.0, Git 2.43.0, GitHub CLI 2.96.0, and `gh stack` 0.1.0.

The commands use Bash or Zsh syntax. Before starting:

- Run `gh auth status` and confirm that GitHub CLI is authenticated.
- Confirm that `git config user.name` and `git config user.email` return your Git identity.
- Choose a repository name that does not already exist in your GitHub account.
- Run the sequence from the directory where you want the new repository folder created.

### 1. Set the repository name and verify `gh stack`

```sh
OWNER="$(gh api user --jq .login)"
REPO="gh-stacked-prs-copy" # Change this if the name already exists.

# Install the extension only when it is not already available.
if ! gh stack --version >/dev/null 2>&1; then
  gh extension install github/gh-stack
fi
```

Avoid adding `--force` to the installation command. A forced upgrade depends on GitHub being able to resolve the latest extension release and is unnecessary when `gh stack` is already installed.

### 2. Create and publish `main`

```sh
mkdir "$REPO"
cd "$REPO"

git init -b main

cat > README.md <<'EOF'
# GitHub Stacked PRs

A tiny Node.js project built as three focused stacked pull requests.
EOF

cat > package.json <<'EOF'
{
  "name": "gh-stacked-prs",
  "version": "1.0.0",
  "private": true,
  "description": "A tiny Node.js API for demonstrating GitHub Stacked PRs",
  "type": "module",
  "scripts": {
    "test": "node --test"
  },
  "engines": {
    "node": ">=20"
  }
}
EOF

git add README.md package.json
git commit -m "chore: scaffold stacked PR demo"

gh repo create "$OWNER/$REPO" \
  --public \
  --source=. \
  --remote=origin \
  --push
```

Publishing `main` before initializing the stack gives `gh stack` a remote and a default trunk branch to detect.

### 3. Create the bottom layer: tested task model

`gh stack init` creates `tasks/model` from `main`, records it as the first layer, and checks it out. This layer includes both the model and its unit test.

```sh
gh stack init tasks/model

mkdir -p src test
cat > src/tasks.js <<'EOF'
export function createTask(title) {
  return {
    id: crypto.randomUUID(),
    title,
    completed: false,
  };
}
EOF

cat > test/tasks.model.test.js <<'EOF'
import test from 'node:test';
import assert from 'node:assert/strict';
import { createTask } from '../src/tasks.js';

test('creates a task with the expected defaults', () => {
  const task = createTask('Ship the demo');

  assert.match(task.id, /^[0-9a-f-]{36}$/);
  assert.equal(task.title, 'Ship the demo');
  assert.equal(task.completed, false);
});
EOF

npm test
git add src/tasks.js test/tasks.model.test.js
git commit -m "feat: add tested task model"
```

### 4. Add the middle layer: tested validation

`gh stack add` creates the next branch from the current top layer. This layer introduces title validation and its unit tests.

```sh
gh stack add tasks/validation

cat > src/tasks.js <<'EOF'
export function validateTaskTitle(title) {
  if (typeof title !== 'string' || !title.trim()) {
    throw new TypeError('Task title is required');
  }

  return title.trim();
}

export function createTask(title) {
  return {
    id: crypto.randomUUID(),
    title: validateTaskTitle(title),
    completed: false,
  };
}
EOF

cat > test/tasks.validation.test.js <<'EOF'
import test from 'node:test';
import assert from 'node:assert/strict';
import { createTask } from '../src/tasks.js';

test('trims a valid task title', () => {
  assert.equal(createTask('  Ship the demo  ').title, 'Ship the demo');
});

test('rejects a whitespace-only task title', () => {
  assert.throws(() => createTask('   '), /Task title is required/);
});

test('rejects a missing task title', () => {
  assert.throws(() => createTask(), /Task title is required/);
});
EOF

npm test
git add src/tasks.js test/tasks.validation.test.js
git commit -m "feat: add tested task validation"
```

### 5. Add the top layer: tested task API

The top layer exposes the model and validation behavior through `POST /tasks`. It includes integration tests and a runnable `npm start` command.

```sh
gh stack add tasks/api

cat > src/server.js <<'EOF'
import { createServer } from 'node:http';
import { pathToFileURL } from 'node:url';
import { createTask } from './tasks.js';

function sendJson(response, statusCode, body) {
  response.writeHead(statusCode, { 'content-type': 'application/json' });
  response.end(JSON.stringify(body));
}

export function createTaskServer() {
  return createServer((request, response) => {
    if (request.method !== 'POST' || request.url !== '/tasks') {
      sendJson(response, 404, { error: 'Not found' });
      return;
    }

    let body = '';
    request.setEncoding('utf8');
    request.on('data', (chunk) => {
      body += chunk;
    });
    request.on('end', () => {
      try {
        const { title } = JSON.parse(body);
        sendJson(response, 201, createTask(title));
      } catch (error) {
        const message = error instanceof SyntaxError ? 'Invalid JSON' : error.message;
        sendJson(response, 400, { error: message });
      }
    });
  });
}

if (process.argv[1] && import.meta.url === pathToFileURL(process.argv[1]).href) {
  const port = Number(process.env.PORT ?? 3000);
  createTaskServer().listen(port, () => {
    console.log(`Task API listening on http://localhost:${port}`);
  });
}
EOF

cat > test/tasks.api.test.js <<'EOF'
import test from 'node:test';
import assert from 'node:assert/strict';
import { createTaskServer } from '../src/server.js';

async function withServer(run) {
  const server = createTaskServer();
  await new Promise((resolve) => server.listen(0, '127.0.0.1', resolve));

  try {
    const { port } = server.address();
    await run(`http://127.0.0.1:${port}`);
  } finally {
    await new Promise((resolve) => server.close(resolve));
  }
}

test('POST /tasks creates a task', async () => {
  await withServer(async (baseUrl) => {
    const response = await fetch(`${baseUrl}/tasks`, {
      method: 'POST',
      headers: { 'content-type': 'application/json' },
      body: JSON.stringify({ title: 'Ship the API' }),
    });
    const task = await response.json();

    assert.equal(response.status, 201);
    assert.equal(task.title, 'Ship the API');
    assert.equal(task.completed, false);
  });
});

test('POST /tasks rejects an invalid title', async () => {
  await withServer(async (baseUrl) => {
    const response = await fetch(`${baseUrl}/tasks`, {
      method: 'POST',
      headers: { 'content-type': 'application/json' },
      body: JSON.stringify({ title: '   ' }),
    });

    assert.equal(response.status, 400);
    assert.deepEqual(await response.json(), { error: 'Task title is required' });
  });
});
EOF

cat > package.json <<'EOF'
{
  "name": "gh-stacked-prs",
  "version": "1.0.0",
  "private": true,
  "description": "A tiny Node.js API for demonstrating GitHub Stacked PRs",
  "type": "module",
  "scripts": {
    "start": "node src/server.js",
    "test": "node --test"
  },
  "engines": {
    "node": ">=20"
  }
}
EOF

npm test
git add package.json src/server.js test/tasks.api.test.js
git commit -m "feat: add tested task API"
```

Each layer follows the same TDD-compatible boundary: write the test, implement the behavior, and submit a green branch containing both.

The local branch chain is now:

```text
main
└── tasks/model
    └── tasks/validation
        └── tasks/api
```

### 6. Test, inspect, and submit

```sh
npm test
gh stack view
gh stack submit --auto --open
```

`gh stack submit --auto --open` performs the GitHub-side work in one operation:

1. Pushes all three branches.
2. Creates PR #1 from `tasks/model` into `main`.
3. Creates PR #2 from `tasks/validation` into `tasks/model`.
4. Creates PR #3 from `tasks/api` into `tasks/validation`.
5. Links the three PRs as one GitHub stack.
6. Marks all three PRs ready for review rather than draft.

`--auto` skips the interactive editor and derives PR titles from the commits. `--open` is important with `--auto` because automatically submitted PRs otherwise default to drafts. To edit each title, description, and draft state interactively, use `gh stack submit` without those flags.

The open training stack in this repository is continuously checked by the [training-resource verification workflow](https://github.com/DanWahlin/gh-stacked-prs/actions/workflows/verify-training-resource.yml).

### Create the demo with an AI coding agent

If you want to quickly create your own sample repository, run the following prompt with your favorite AI coding tool. The agent needs terminal access, an authenticated GitHub CLI, and permission to create repositories.

```text
Create a working GitHub Stacked PRs sample based on this repository:

https://github.com/DanWahlin/gh-stacked-prs

You are authorized to create one new public repository in my currently
authenticated GitHub account and open three pull requests. Leave all pull
requests open. Do not modify the source repository.

Use the live README in the source repository as the source of truth:

1. Retrieve the README from the main branch.
2. Find the section titled "Commands used to create this demo."
3. Read the entire section before making changes.
4. Follow that process from start to finish rather than relying on your
   existing knowledge of gh stack.

Create the new repository in a separate, empty directory.

Use this repository name:

gh-stacked-prs-copy

If that name already exists in my GitHub account, append a short timestamp
to make it unique. Do not delete, overwrite, rename, or reuse an existing
repository.

Before starting, verify:

- Git is installed.
- Node.js LTS or newer is installed.
- GitHub CLI is installed and authenticated.
- git user.name and user.email are configured.
- gh stack is available. If it is not available, install it with:
  gh extension install github/gh-stack

Then execute the README workflow to:

- Create and publish the main branch.
- Create tasks/model as the bottom stack layer.
- Create tasks/validation as the middle layer.
- Create tasks/api as the top layer.
- Commit the focused change on each branch.
- Run the Node.js tests.
- Inspect the local stack.
- Submit all three pull requests with:
  gh stack submit --auto --open

Do not:

- Modify the source repository.
- Merge or close any pull request.
- Force-push or rewrite Git history.
- Delete any repository or branch.
- Substitute ordinary gh pr create commands for gh stack submit.
- Claim success without checking the live GitHub repository.

After submission, verify all of the following:

1. The tests pass.
2. The branch ancestry is:
   main
   └── tasks/model
       └── tasks/validation
           └── tasks/api
3. PR #1 targets main from tasks/model.
4. PR #2 targets tasks/model from tasks/validation.
5. PR #3 targets tasks/validation from tasks/api.
6. All three PRs are open and ready for review, not drafts.
7. gh stack view shows the three PRs as one linked stack.
8. Each PR contains only its intended focused change.

When finished, return:

- The new repository URL.
- The GitHub stack number.
- Links to all three pull requests.
- The test result.
- The verified base and head branch for each PR.
- Any deviations from the source README or blockers encountered.

If a required tool, authentication, or permission is unavailable, stop and
report the exact blocker. Do not fabricate commands, URLs, test results, or
GitHub state.
```

## Useful commands after submission

```sh
# Inspect the current stack and PR states.
gh stack view

# Move between adjacent layers.
gh stack up
gh stack down

# Push committed changes on every stack branch.
gh stack push

# Fetch, rebase, push, and synchronize PR/stack state.
gh stack sync

# Rebase locally without performing the rest of a sync.
gh stack rebase

# Interactively land all or part of the stack.
gh stack merge
```
