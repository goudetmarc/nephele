import { test } from 'node:test';
import assert from 'node:assert/strict';
import { proxyWithRetry } from './index.js';

// Backoff exponentiel : sleepFn injecté, on n'attend rien pour de vrai.
const noSleep = async () => {};

test('réessaie sur 502 puis réussit ; backoff exponentiel', async () => {
  let n = 0;
  const slept = [];
  const fake = async () => new Response('x', { status: ++n < 3 ? 502 : 200 });
  const resp = await proxyWithRetry(fake, 'u', {}, {
    attempts: 3, base: 10, sleepFn: async (ms) => slept.push(ms),
  });
  assert.equal(resp.status, 200);
  assert.equal(n, 3);
  assert.deepEqual(slept, [10, 20]); // 10·2^0, 10·2^1
});

test('ne réessaie pas un 400', async () => {
  let n = 0;
  const fake = async () => (n++, new Response('bad', { status: 400 }));
  const resp = await proxyWithRetry(fake, 'u', {}, { attempts: 3, base: 1, sleepFn: noSleep });
  assert.equal(resp.status, 400);
  assert.equal(n, 1);
});

test('épuise les tentatives sur 503 persistant', async () => {
  let n = 0;
  const fake = async () => (n++, new Response('down', { status: 503 }));
  const resp = await proxyWithRetry(fake, 'u', {}, { attempts: 3, base: 1, sleepFn: noSleep });
  assert.equal(resp.status, 503);
  assert.equal(n, 3);
});

test('erreur réseau : réessaie puis propage', async () => {
  let n = 0;
  const fake = async () => { n++; throw new Error('net'); };
  await assert.rejects(() => proxyWithRetry(fake, 'u', {}, { attempts: 2, base: 1, sleepFn: noSleep }));
  assert.equal(n, 2);
});
