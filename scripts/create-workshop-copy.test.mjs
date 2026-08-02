import test from 'node:test';
import assert from 'node:assert/strict';
import { mkdtempSync, mkdirSync, rmSync, writeFileSync } from 'node:fs';
import { tmpdir } from 'node:os';
import path from 'node:path';

import {
  API_PACKAGE_JSON,
  API_TEST,
  EXPECTED_PULL_REQUESTS,
  MODEL_SOURCE,
  MODEL_TEST,
  SERVER_SOURCE,
  VALIDATION_SOURCE,
  VALIDATION_TEST,
  parseArgs,
  run,
  usage,
} from './create-workshop-copy.mjs';

test('parses build mode with the repository name as the default directory', () => {
  assert.deepEqual(
    parseArgs(['octocat/workshop', '--build', '--private']),
    {
      help: false,
      mode: 'build',
      visibility: '--private',
      targetRepo: 'octocat/workshop',
      targetDir: 'workshop',
    },
  );
});

test('parses ready mode with an explicit directory', () => {
  assert.deepEqual(
    parseArgs([
      'octocat/workshop',
      '--ready',
      '--public',
      '--directory',
      'copies/team-a',
    ]),
    {
      help: false,
      mode: 'ready',
      visibility: '--public',
      targetRepo: 'octocat/workshop',
      targetDir: 'copies/team-a',
    },
  );
});

test('returns help without requiring other arguments', () => {
  assert.deepEqual(parseArgs(['--help']), { help: true });
  assert.match(usage(), /node scripts\/create-workshop-copy\.mjs/);
});

test('rejects incomplete or ambiguous arguments', () => {
  const cases = [
    [[], /Provide the target/],
    [['workshop', '--build', '--private'], /OWNER\/REPO/],
    [['octocat/workshop', '--private'], /--build or --ready/],
    [['octocat/workshop', '--build'], /--public or --private/],
    [['octocat/workshop', '--build', '--ready', '--private'], /only one mode/],
    [['octocat/workshop', '--build', '--public', '--private'], /only one visibility/],
    [['octocat/workshop', '--build', '--private', '--directory'], /requires a path/],
    [['octocat/workshop', '--build', '--private', '--unknown'], /Unknown option/],
  ];

  for (const [args, expected] of cases) {
    assert.throws(() => parseArgs(args), expected);
  }
});

test('defines the expected three-layer pull request contract', () => {
  assert.deepEqual(
    EXPECTED_PULL_REQUESTS.map(({ base, head, position }) => ({ base, head, position })),
    [
      { base: 'main', head: 'tasks/model', position: 1 },
      { base: 'tasks/model', head: 'tasks/validation', position: 2 },
      { base: 'tasks/validation', head: 'tasks/api', position: 3 },
    ],
  );
});

test('runs a cross-platform Node prerequisite check', () => {
  assert.match(run('node', ['--version'], { capture: true }), /^v\d+/);
});

test('generated files pass the tests at every workshop layer', () => {
  const directory = mkdtempSync(path.join(tmpdir(), 'gh-stack-workshop-copy-'));
  try {
    mkdirSync(path.join(directory, 'src'));
    mkdirSync(path.join(directory, 'test'));
    writeFileSync(path.join(directory, 'package.json'), `${API_PACKAGE_JSON}\n`);

    writeFileSync(path.join(directory, 'src/tasks.js'), `${MODEL_SOURCE}\n`);
    writeFileSync(path.join(directory, 'test/tasks.model.test.js'), `${MODEL_TEST}\n`);
    run('node', ['--test'], { cwd: directory, capture: true });

    writeFileSync(path.join(directory, 'src/tasks.js'), `${VALIDATION_SOURCE}\n`);
    writeFileSync(path.join(directory, 'test/tasks.validation.test.js'), `${VALIDATION_TEST}\n`);
    run('node', ['--test'], { cwd: directory, capture: true });

    writeFileSync(path.join(directory, 'src/server.js'), `${SERVER_SOURCE}\n`);
    writeFileSync(path.join(directory, 'test/tasks.api.test.js'), `${API_TEST}\n`);
    run('node', ['--test'], { cwd: directory, capture: true });
  } finally {
    rmSync(directory, { recursive: true, force: true });
  }
});
