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
