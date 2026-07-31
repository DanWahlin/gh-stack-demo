#!/usr/bin/env bash
set -euo pipefail

SOURCE_REPO="${SOURCE_REPO:-DanWahlin/gh-stacked-prs}"
MODE=""
VISIBILITY=""
TARGET_REPO=""
TARGET_DIR=""

usage() {
  cat <<'EOF'
Create an isolated stacked-PR workshop repository.

Usage:
  scripts/create-workshop-copy.sh OWNER/REPO --build (--public|--private) [--directory PATH]
  scripts/create-workshop-copy.sh OWNER/REPO --ready (--public|--private) [--directory PATH]

Modes:
  --build   Copy main only. The learner creates the stack during the workshop.
  --ready   Copy main, create all three layers, run tests, and submit the PR stack.

The target repository and local directory must not already exist. The script
never deletes an existing repository or directory.
EOF
}

fail() {
  printf 'ERROR: %s\n' "$*" >&2
  exit 1
}

while (($#)); do
  case "$1" in
    --build|--ready)
      [[ -z "$MODE" ]] || fail "Choose only one mode."
      MODE="${1#--}"
      ;;
    --public|--private)
      [[ -z "$VISIBILITY" ]] || fail "Choose only one visibility."
      VISIBILITY="$1"
      ;;
    --directory)
      shift
      (($#)) || fail "--directory requires a path."
      TARGET_DIR="$1"
      ;;
    -h|--help)
      usage
      exit 0
      ;;
    -* )
      fail "Unknown option: $1"
      ;;
    *)
      [[ -z "$TARGET_REPO" ]] || fail "Only one OWNER/REPO target is allowed."
      TARGET_REPO="$1"
      ;;
  esac
  shift
done

[[ -n "$TARGET_REPO" ]] || fail "Provide the target as OWNER/REPO."
[[ "$TARGET_REPO" == */* ]] || fail "Use the OWNER/REPO form."
[[ -n "$MODE" ]] || fail "Choose --build or --ready."
[[ -n "$VISIBILITY" ]] || fail "Choose --public or --private."

for command in git node gh; do
  command -v "$command" >/dev/null 2>&1 || fail "$command is required."
done

gh auth status >/dev/null
gh stack --version >/dev/null

git config user.name >/dev/null || fail "git user.name is not configured."
git config user.email >/dev/null || fail "git user.email is not configured."

if gh repo view "$TARGET_REPO" >/dev/null 2>&1; then
  fail "Repository $TARGET_REPO already exists. Choose a new name."
fi

if [[ -z "$TARGET_DIR" ]]; then
  TARGET_DIR="${TARGET_REPO#*/}"
fi
[[ ! -e "$TARGET_DIR" ]] || fail "Local path $TARGET_DIR already exists."

printf 'Creating %s from template %s...\n' "$TARGET_REPO" "$SOURCE_REPO"
gh repo create "$TARGET_REPO" "$VISIBILITY" --template "$SOURCE_REPO"
gh repo clone "$TARGET_REPO" "$TARGET_DIR"

cd "$TARGET_DIR"

if [[ "$MODE" == "build" ]]; then
  cat <<EOF

Build-mode repository created:
  https://github.com/$TARGET_REPO

Next:
  cd $TARGET_DIR
  open docs/workshop/README.md
  start with: gh stack init tasks/model
EOF
  exit 0
fi

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

gh stack view --json
gh stack submit --auto --open
python scripts/verify-demo.py --repo "$TARGET_REPO"

cat <<EOF

Ready-mode repository created and verified:
  https://github.com/$TARGET_REPO

The three pull requests are open, green, and ready for review.
EOF
