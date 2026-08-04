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
