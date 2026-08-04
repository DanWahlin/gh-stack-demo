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
