#!/usr/bin/env node

import { spawnSync } from 'node:child_process';
import {
  existsSync,
  mkdirSync,
  writeFileSync,
} from 'node:fs';
import path from 'node:path';
import { fileURLToPath } from 'node:url';

const DEFAULT_SOURCE_REPO = 'DanWahlin/learn-github-stacked-prs';
const API_VERSION = '2026-03-10';

export const EXPECTED_PULL_REQUESTS = [
  {
    base: 'main',
    head: 'tasks/model',
    position: 1,
    files: ['src/tasks.js', 'test/tasks.model.test.js'],
  },
  {
    base: 'tasks/model',
    head: 'tasks/validation',
    position: 2,
    files: ['src/tasks.js', 'test/tasks.validation.test.js'],
  },
  {
    base: 'tasks/validation',
    head: 'tasks/api',
    position: 3,
    files: ['package.json', 'src/server.js', 'test/tasks.api.test.js'],
  },
];

export function usage() {
  return `Create an isolated stacked-PR workshop repository.

Usage:
  node scripts/create-workshop-copy.mjs OWNER/REPO --build (--public|--private) [--directory PATH]
  node scripts/create-workshop-copy.mjs OWNER/REPO --ready (--public|--private) [--directory PATH]

Modes:
  --build   Copy main only. The learner creates the stack during the workshop.
  --ready   Copy main, create all three layers, run tests, and submit the PR stack.

The target repository and local directory must not already exist. The script
never deletes an existing repository or directory.`;
}

export function parseArgs(args) {
  let mode = '';
  let visibility = '';
  let targetRepo = '';
  let targetDir = '';

  for (let index = 0; index < args.length; index += 1) {
    const argument = args[index];
    if (argument === '--build' || argument === '--ready') {
      if (mode) throw new Error('Choose only one mode');
      mode = argument.slice(2);
    } else if (argument === '--public' || argument === '--private') {
      if (visibility) throw new Error('Choose only one visibility');
      visibility = argument;
    } else if (argument === '--directory') {
      index += 1;
      if (index >= args.length) throw new Error('--directory requires a path');
      targetDir = args[index];
    } else if (argument === '-h' || argument === '--help') {
      return { help: true };
    } else if (argument.startsWith('-')) {
      throw new Error(`Unknown option: ${argument}`);
    } else {
      if (targetRepo) throw new Error('Only one OWNER/REPO target is allowed');
      targetRepo = argument;
    }
  }

  if (!targetRepo) throw new Error('Provide the target as OWNER/REPO');
  if (!/^[^/]+\/[^/]+$/.test(targetRepo)) throw new Error('Use the OWNER/REPO form');
  if (!mode) throw new Error('Choose --build or --ready');
  if (!visibility) throw new Error('Choose --public or --private');

  return {
    help: false,
    mode,
    visibility,
    targetRepo,
    targetDir: targetDir || targetRepo.split('/')[1],
  };
}

function commandName(command) {
  if (process.platform === 'win32' && command === 'npm') return 'npm.cmd';
  return command;
}

export function run(command, args, options = {}) {
  const capture = options.capture ?? false;
  const result = spawnSync(commandName(command), args, {
    cwd: options.cwd,
    encoding: 'utf8',
    env: process.env,
    stdio: capture ? 'pipe' : 'inherit',
  });

  if (result.error) {
    throw new Error(`${command} is required: ${result.error.message}`);
  }
  if (result.status !== 0) {
    const detail = capture
      ? (result.stderr?.trim() || result.stdout?.trim() || `exit ${result.status}`)
      : `exit ${result.status}`;
    throw new Error(`${command} ${args.join(' ')} failed: ${detail}`);
  }
  return capture ? result.stdout.trim() : '';
}

function commandSucceeds(command, args, options = {}) {
  const result = spawnSync(commandName(command), args, {
    cwd: options.cwd,
    encoding: 'utf8',
    env: process.env,
    stdio: 'ignore',
  });
  if (result.error) throw new Error(`${command} is required: ${result.error.message}`);
  return result.status === 0;
}

function writeText(relativePath, content) {
  const absolutePath = path.resolve(relativePath);
  mkdirSync(path.dirname(absolutePath), { recursive: true });
  writeFileSync(absolutePath, `${content.trim()}\n`, 'utf8');
}

function verifyPullRequests(repo) {
  const failures = [];
  const observedStackIds = new Set();

  for (const expected of EXPECTED_PULL_REQUESTS) {
    const matches = JSON.parse(run('gh', [
      'pr', 'list',
      '--repo', repo,
      '--state', 'open',
      '--head', expected.head,
      '--json', 'number,state,isDraft,baseRefName,headRefName,files,url',
    ], { capture: true }));

    if (matches.length !== 1) {
      failures.push(`${expected.head}: expected one open PR, observed ${matches.length}`);
      continue;
    }

    const pullRequest = matches[0];
    const actualFiles = pullRequest.files.map((file) => file.path).sort();
    const expectedFiles = [...expected.files].sort();
    const checks = [
      ['state', pullRequest.state, 'OPEN'],
      ['draft', pullRequest.isDraft, false],
      ['base', pullRequest.baseRefName, expected.base],
      ['head', pullRequest.headRefName, expected.head],
      ['files', actualFiles, expectedFiles],
    ];

    for (const [label, actual, wanted] of checks) {
      if (JSON.stringify(actual) !== JSON.stringify(wanted)) {
        failures.push(`PR #${pullRequest.number} ${label}: expected ${JSON.stringify(wanted)}, observed ${JSON.stringify(actual)}`);
      }
    }

    const pull = JSON.parse(run('gh', [
      'api',
      '-H', `X-GitHub-Api-Version: ${API_VERSION}`,
      `repos/${repo}/pulls/${pullRequest.number}`,
    ], { capture: true }));
    const stack = pull.stack;
    let stackDetail = '';

    if (!stack) {
      failures.push(`PR #${pullRequest.number} is not linked to a GitHub stack`);
    } else {
      observedStackIds.add(stack.id);
      stackDetail = `; stack #${stack.number} position ${stack.position}/${stack.size}`;
      const stackChecks = [
        ['stack position', stack.position, expected.position],
        ['stack size', stack.size, EXPECTED_PULL_REQUESTS.length],
        ['stack base', stack.base.ref, 'main'],
      ];
      for (const [label, actual, wanted] of stackChecks) {
        if (actual !== wanted) {
          failures.push(`PR #${pullRequest.number} ${label}: expected ${JSON.stringify(wanted)}, observed ${JSON.stringify(actual)}`);
        }
      }
    }

    console.log(`PR #${pullRequest.number}: ${pullRequest.baseRefName} <- ${pullRequest.headRefName} (${actualFiles.join(', ')})${stackDetail}`);
  }

  if (observedStackIds.size !== 1) {
    failures.push(`expected all pull requests to share one GitHub stack, observed stack IDs ${JSON.stringify([...observedStackIds].sort())}`);
  }
  if (failures.length) {
    throw new Error(`Workshop stack verification failed:\n- ${failures.join('\n- ')}`);
  }
}

export const API_PACKAGE_JSON = JSON.stringify({
  name: 'gh-stacked-prs',
  version: '1.0.0',
  private: true,
  description: 'A tiny Node.js API for demonstrating GitHub Stacked PRs',
  type: 'module',
  scripts: {
    start: 'node src/server.js',
    test: 'node --test',
  },
  engines: { node: '>=20' },
}, null, 2);

export const MODEL_SOURCE = `export function createTask(title) {
  return {
    id: crypto.randomUUID(),
    title,
    completed: false,
  };
}`;

export const MODEL_TEST = `import test from 'node:test';
import assert from 'node:assert/strict';
import { createTask } from '../src/tasks.js';

test('creates a task with the expected defaults', () => {
  const task = createTask('Ship the demo');

  assert.match(task.id, /^[0-9a-f-]{36}$/);
  assert.equal(task.title, 'Ship the demo');
  assert.equal(task.completed, false);
});`;

export const VALIDATION_SOURCE = `export function validateTaskTitle(title) {
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
}`;

export const VALIDATION_TEST = `import test from 'node:test';
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
});`;

export const SERVER_SOURCE = `import { createServer } from 'node:http';
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
    console.log(\`Task API listening on http://localhost:\${port}\`);
  });
}`;

export const API_TEST = `import test from 'node:test';
import assert from 'node:assert/strict';
import { createTaskServer } from '../src/server.js';

async function withServer(run) {
  const server = createTaskServer();
  await new Promise((resolve) => server.listen(0, '127.0.0.1', resolve));

  try {
    const { port } = server.address();
    await run(\`http://127.0.0.1:\${port}\`);
  } finally {
    await new Promise((resolve) => server.close(resolve));
  }
}

test('POST /tasks creates a task', async () => {
  await withServer(async (baseUrl) => {
    const response = await fetch(\`\${baseUrl}/tasks\`, {
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
    const response = await fetch(\`\${baseUrl}/tasks\`, {
      method: 'POST',
      headers: { 'content-type': 'application/json' },
      body: JSON.stringify({ title: '   ' }),
    });

    assert.equal(response.status, 400);
    assert.deepEqual(await response.json(), { error: 'Task title is required' });
  });
});`;

export function main(args = process.argv.slice(2)) {
  const options = parseArgs(args);
  if (options.help) {
    console.log(usage());
    return;
  }

  for (const [command, versionArgs] of [
    ['git', ['--version']],
    ['node', ['--version']],
    ['gh', ['--version']],
  ]) {
    run(command, versionArgs, { capture: true });
  }
  run('gh', ['auth', 'status'], { capture: true });
  run('gh', ['stack', '--version'], { capture: true });
  run('git', ['config', 'user.name'], { capture: true });
  run('git', ['config', 'user.email'], { capture: true });

  if (commandSucceeds('gh', ['repo', 'view', options.targetRepo])) {
    throw new Error(`Repository ${options.targetRepo} already exists. Choose a new name`);
  }

  const startDirectory = process.cwd();
  const targetDirectory = path.resolve(startDirectory, options.targetDir);
  if (existsSync(targetDirectory)) {
    throw new Error(`Local path ${options.targetDir} already exists`);
  }

  const sourceRepo = process.env.SOURCE_REPO || DEFAULT_SOURCE_REPO;
  console.log(`Creating ${options.targetRepo} from template ${sourceRepo}...`);
  run('gh', ['repo', 'create', options.targetRepo, options.visibility, '--template', sourceRepo]);
  run('gh', ['repo', 'clone', options.targetRepo, targetDirectory]);

  if (options.mode === 'build') {
    console.log(`\nBuild-mode repository created:\n  https://github.com/${options.targetRepo}\n\nNext:\n  cd ${options.targetDir}\n  inspect AGENTS.md\n  open docs/workshop/README.md\n  start the workshop with the agent and CLI preflight`);
    return;
  }

  process.chdir(targetDirectory);
  run('gh', ['stack', 'init', '--base', 'main', 'tasks/model']);
  writeText('src/tasks.js', MODEL_SOURCE);
  writeText('test/tasks.model.test.js', MODEL_TEST);
  run('npm', ['test']);
  run('git', ['add', 'src/tasks.js', 'test/tasks.model.test.js']);
  run('git', ['commit', '-m', 'feat: add tested task model']);

  run('gh', ['stack', 'add', 'tasks/validation']);
  writeText('src/tasks.js', VALIDATION_SOURCE);
  writeText('test/tasks.validation.test.js', VALIDATION_TEST);
  run('npm', ['test']);
  run('git', ['add', 'src/tasks.js', 'test/tasks.validation.test.js']);
  run('git', ['commit', '-m', 'feat: add tested task validation']);

  run('gh', ['stack', 'add', 'tasks/api']);
  writeText('src/server.js', SERVER_SOURCE);
  writeText('test/tasks.api.test.js', API_TEST);
  writeText('package.json', API_PACKAGE_JSON);
  run('npm', ['test']);
  run('git', ['add', 'package.json', 'src/server.js', 'test/tasks.api.test.js']);
  run('git', ['commit', '-m', 'feat: add tested task API']);

  run('gh', ['stack', 'view', '--json']);
  run('gh', ['stack', 'submit', '--auto', '--open']);
  verifyPullRequests(options.targetRepo);

  console.log(`\nReady-mode repository created and verified:\n  https://github.com/${options.targetRepo}\n\nThe three pull requests are open and ready for review. Their bases, heads, and changed files were verified, and the tests passed locally before submission.`);
}

const isMain = process.argv[1]
  && path.resolve(fileURLToPath(import.meta.url)) === path.resolve(process.argv[1]);

if (isMain) {
  try {
    main();
  } catch (error) {
    console.error(`ERROR: ${error.message}`);
    process.exitCode = 1;
  }
}
