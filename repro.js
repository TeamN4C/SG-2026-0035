'use strict';

const express = require('express');

const app = express();

app.get('/health', (_request, response) => {
  response.set('X-Process-Id', String(process.pid));
  response.type('text/plain').send('PONG\n');
});

app.post('/upload', express.json(), (_request, response) => {
  response.type('text/plain').send('DONE\n');
});

app.use((error, _request, response, _next) => {
  response.status(400).type('text/plain').send(
    `ERR ${error.code || error.type || error.message}\n`,
  );
});

app.listen(31338, '127.0.0.1', () => {
  console.log('listening on http://127.0.0.1:31338');
});
