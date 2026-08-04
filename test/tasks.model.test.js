import test from 'node:test';
import assert from 'node:assert/strict';
import { createTask } from '../src/tasks.js';

test('creates a task with the expected defaults', () => {
  const task = createTask('Ship the demo');

  assert.match(task.id, /^[0-9a-f-]{36}$/);
  assert.equal(task.title, 'Ship the demo');
  assert.equal(task.completed, false);
});
