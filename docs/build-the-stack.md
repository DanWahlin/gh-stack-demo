# Build the canonical stack

This procedure recreates the live three-pull-request training stack without a coding agent. It creates the required files, publishes `main`, tests each layer, and submits the stack. It was validated with Node.js 24.18.0, Git 2.43.0, GitHub CLI 2.96.0, and `gh stack` 0.1.0.

The commands use Bash or Zsh syntax. Before starting:

- Run `gh auth status` and confirm that GitHub CLI is authenticated.
- Confirm that `git config user.name` and `git config user.email` return your Git identity.
- Choose a repository name that does not already exist in your GitHub account.
- Run the sequence from the directory where you want the new repository folder created.

## 1. Set the repository name and verify `gh stack`

```sh
OWNER="$(gh api user --jq .login)"
REPO="learn-github-stacked-prs-copy" # Change this if the name already exists.

# Install the extension only when it is not already available.
if ! gh stack --version >/dev/null 2>&1; then
  gh extension install github/gh-stack
fi
```

Avoid adding `--force` to the installation command. A forced upgrade depends on GitHub being able to resolve the latest extension release and is unnecessary when `gh stack` is already installed.

## 2. Create and publish `main`

The command below creates a private disposable repository. Change `--private` to `--public` only when you intend to publish the exercise.

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
  --private \
  --source=. \
  --remote=origin \
  --push
```

Publishing `main` before initializing the stack gives `gh stack` a remote and a default trunk branch to detect.

## 3. Create the bottom layer: tested task model

`gh stack init` creates `tasks/model` from `main`, records it as the first layer, and checks it out. This layer includes both the model and its unit test.

```sh
gh stack init --base main tasks/model

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

Checkpoint: `npm test` reports 1 passing test, and `git status --short` is clean after the commit.

## 4. Add the middle layer: tested validation

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

Checkpoint: `npm test` reports 4 passing tests, and the branch diff contains only model validation and its tests.

## 5. Add the top layer: tested task API

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

Checkpoint: `npm test` reports 6 passing tests, and the branch diff contains only the API layer and its tests.

Each layer keeps its implementation and tests together and must pass before the next layer is created.

The local branch chain is now:

```text
main
└── tasks/model
    └── tasks/validation
        └── tasks/api
```

## 6. Test, inspect, and submit

```sh
npm test
gh stack view --json
gh stack submit --auto --open
```

After submission, inspect the live pull requests:

1. The model pull request targets `main` from `tasks/model`.
2. The validation pull request targets `tasks/model` from `tasks/validation`.
3. The API pull request targets `tasks/validation` from `tasks/api`.
4. All three pull requests are open, ready for review, focused, and linked as one stack.

`--auto` skips the interactive editor and derives pull request titles from the commits. `--open` marks new and existing pull requests ready for review. To edit titles, descriptions, and draft states interactively, use `gh stack submit` without those flags.

The open training stack in this repository is continuously checked by the [training-resource verification workflow](https://github.com/DanWahlin/learn-github-stacked-prs/actions/workflows/verify-training-resource.yml).



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

# Fetch and cascade-rebase locally without pushing or syncing PR state.
gh stack rebase

# Interactively land all or part of the stack.
gh stack merge
```
