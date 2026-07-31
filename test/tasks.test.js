import test from 'node:test';
import assert from 'node:assert/strict';
import { createTask, isValidTask } from '../src/tasks.js';

test('creates a valid task', () => {
  const task = createTask('Ship the demo');

  assert.equal(task.title, 'Ship the demo');
  assert.equal(task.completed, false);
  assert.equal(isValidTask(task), true);
});

test('rejects a task with an empty title', () => {
  assert.equal(isValidTask(createTask('   ')), false);
});
