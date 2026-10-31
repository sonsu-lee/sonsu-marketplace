import { expect, spyOn, test } from 'bun:test';
import { createServer } from 'node:http';
import { readFile, writeFile } from 'node:fs/promises';
import { join } from 'node:path';
import { randomUUID } from 'node:crypto';
import { z } from '@oh-my-pi/pi-coding-agent';
import { ExtensionToolWrapper } from '@oh-my-pi/pi-coding-agent/extensibility/extensions/wrapper';
import { DesignRunEngine } from '../src/engine.ts';
import type { DesignPlan } from '../src/engine.ts';
import { createHarness } from './sdk-host.ts';
import type { Harness } from './sdk-host.ts';

const browser = process.env.DESIGN_WORKFLOW_CHROME;
const html = '<!doctype html><title>Fixture</title><h1>Ready</h1>';

function plan(): DesignPlan {
  return { mode: 'design', paths: ['page.html'], goal: 'Verify a real rendered state', brief: 'Show a ready page.', facts: [], captures: [{ id: 'page', kind: 'file', target: 'page.html', width: 390, height: 300, steps: [{ action: 'assert-text', selector: 'h1', text: 'Ready' }] }], checks: [] };
}

// 証拠と検査済み報告まで揃え、操作側の承認だけが残る状態にする。
async function prepare(h: Harness, approved: DesignPlan) {
  await writeFile(join(h.workspace, 'page.html'), html);
  h.choice.approve = true;
  await h.start(approved);
  expect((await h.status()).phase).toBe('active');
  await h.call('design_capture', { id: 'page' });
  for (const check of approved.checks) await h.call('design_check', { id: check.id });
  await h.command('design-report');
  expect((await h.status()).missing).toEqual(['review']);
}

test('unsupported capture dimensions never activate an approved run', async () => {
  const h = await createHarness();
  try {
    const approved = plan(); approved.captures[0].width = 5120;
    h.choice.approve = true;
    await h.start(approved);
    expect((await h.call('design_status')).details).toMatchObject({ phase: 'inactive' });
    await expect(h.call('design_write', { path: 'page.html', content: 'not approved' })).rejects.toThrow('No approved design run');
  } finally { await h.close(); }
});

test('stopping preserves unrelated xd tool presentation and invocation', async () => {
  let notePath = '';
  const h = await createHarness([{
    name: 'fixture_note', label: 'Read existing note', description: 'An unrelated read-only device',
    parameters: z.object({}), approval: 'read', loadMode: 'discoverable',
    async execute() {
      return { content: [{ type: 'text', text: await readFile(notePath, 'utf8') }], details: {} };
    },
  }]);
  try {
    // 1. 既存デバイスの実際の xd 経路と表示区分を保存する。
    notePath = join(h.workspace, 'note.txt');
    await writeFile(notePath, 'Existing note');
    const before = { top: new Set(h.session.getActiveToolNames()), mounted: new Set(h.session.getMountedXdevToolNames()) };
    expect(before.mounted.has('fixture_note')).toBe(true);
    expect((await h.call('write', { path: 'xd://fixture_note', content: '{}' })).content).toContainEqual({ type: 'text', text: 'Existing note' });
    // 2. 実行中は外側の書込み経路で拒否し、終了後は元のデバイス経路を維持する。
    h.choice.approve = true; await h.start(plan());
    await expect(h.call('write', { path: 'xd://fixture_note', content: '{}' })).rejects.toThrow('arbitrary writes');
    await h.command('design-stop', 'Presentation regression');
    expect({ top: new Set(h.session.getActiveToolNames()), mounted: new Set(h.session.getMountedXdevToolNames()) }).toEqual(before);
    expect((await h.call('write', { path: 'xd://fixture_note', content: '{}' })).content).toContainEqual({ type: 'text', text: 'Existing note' });
  } finally { await h.close(); }
});

test('real SDK advisor wrappers cannot write beyond an active plan', async () => {
  const h = await createHarness();
  try {
    h.choice.approve = true;
    await h.start(plan());
    const sentinel = join(h.workspace, 'unapproved.txt');
    const native = {
      name: 'write', label: 'Write sentinel', description: 'Regression fixture with a real file effect',
      parameters: z.object({ path: z.string(), content: z.string() }),
      async execute() { await writeFile(sentinel, 'escaped'); return { content: [{ type: 'text' as const, text: 'written' }], details: {} }; },
    };
    const advisor = new ExtensionToolWrapper(native, h.runner, { kind: 'sub', id: 'advisor', name: 'advisor', depth: 0, parentId: 'main' });
    await expect(advisor.execute(randomUUID(), { path: sentinel, content: 'escaped' }, new AbortController().signal)).rejects.toThrow('arbitrary writes');
    await expect(readFile(sentinel)).rejects.toThrow('ENOENT');
  } finally { await h.close(); }
});

test.skipIf(!browser)('a failed check retry revokes its earlier receipt and acceptance across restore', async () => {
  const h = await createHarness();
  try {
    const approved = plan();
    approved.checks = [{ id: 'check', command: process.execPath, args: ['-e', 'if (require("fs").existsSync("fail.flag")) process.exit(2)'], timeoutMs: 2000 }];
    await prepare(h, approved);
    await writeFile(join(h.workspace, 'fail.flag'), 'fail');
    await expect(h.call('design_check', { id: 'check' })).rejects.toThrow('failed');
    await h.runner.emit({ type: 'session_start' });
    expect((await h.status()).missing).toContain('check:check');
    expect((await h.status()).report).toBeUndefined();
    await h.command('design-accept');
    expect(h.notifications.at(-1)).toContain('missing or stale');
    expect((await h.status()).phase).toBe('active');
  } finally { await h.close(); }
});

test.skipIf(!browser)('a failed live recapture cannot reuse the previous accepted observation', async () => {
  const h = await createHarness();
  let failed = false;
  const server = createServer((_request, response) => { response.writeHead(failed ? 500 : 200, { 'content-type': 'text/html' }); response.end(html); });
  const listening = Promise.withResolvers<void>();
  server.listen(0, '127.0.0.1', listening.resolve);
  await listening.promise;
  try {
    const address = server.address();
    if (!address || typeof address === 'string') throw new Error('No local capture port');
    const approved = plan(); approved.paths = [];
    approved.captures[0] = { ...approved.captures[0], kind: 'web', target: `http://127.0.0.1:${address.port}/` };
    await prepare(h, approved);
    failed = true;
    await expect(h.call('design_capture', { id: 'page' })).rejects.toThrow();
    expect((await h.status()).missing).toContain('capture:page');
    await h.command('design-accept');
    expect(h.notifications.at(-1)).toContain('missing or stale');
    expect((await h.status()).phase).toBe('active');
  } finally {
    server.closeAllConnections();
    const closed = Promise.withResolvers<void>(); server.close(() => closed.resolve()); await closed.promise;
    await h.close();
  }
});

test.skipIf(!browser)('an operator stop during report generation records and publishes nothing', async () => {
  const started = Promise.withResolvers<void>();
  const h = await createHarness([], {
    author: () => (_prompt, signal) => new Promise((_resolve, reject) => {
      started.resolve();
      signal.addEventListener('abort', () => reject(new Error('Report author cancelled')), { once: true });
    }),
    reviewer: () => async () => '{"decision": "pass", "findings": []}',
  });
  try {
    await writeFile(join(h.workspace, 'page.html'), html);
    h.choice.approve = true;
    await h.start(plan());
    await h.call('design_capture', { id: 'page' });
    const pending = h.command('design-report');
    await started.promise;
    await h.command('design-stop', 'Operator cancelled the report');
    await pending;
    expect(h.published().some(text => text.startsWith('# Design report'))).toBe(false);
    const state = await h.status();
    expect(state.phase).toBe('stopped');
    expect(state.report).toBeUndefined();
  } finally { await h.close(); }
});

test.skipIf(!browser)('an in-flight status cannot transfer approval into a real full-session fork', async () => {
  const h = await createHarness();
  const entered = Promise.withResolvers<void>();
  const release = Promise.withResolvers<void>();
  const adopted = Promise.withResolvers<void>();
  let statusPatch: { mockRestore(): void } | undefined;
  let forkPatch: { mockRestore(): void } | undefined;
  try {
    await prepare(h, plan());
    const originalStatus = DesignRunEngine.prototype.status;
    statusPatch = spyOn(DesignRunEngine.prototype, 'status').mockImplementationOnce(async function (this: DesignRunEngine) {
      entered.resolve(); await release.promise;
      return originalStatus.call(this);
    });
    const originalFork = h.sessions.fork.bind(h.sessions);
    forkPatch = spyOn(h.sessions, 'fork').mockImplementation(async () => {
      const result = await originalFork(); adopted.resolve(); return result;
    });
    const pendingStatus = h.call('design_status').then(() => undefined, () => undefined);
    await entered.promise;
    const fork = h.session.fork();
    await adopted.promise;
    release.resolve();
    await pendingStatus; await fork;
    await expect(h.call('design_write', { path: 'page.html', content: 'inherited approval' })).rejects.toThrow('Run recovery failed');
    expect(await readFile(join(h.workspace, 'page.html'), 'utf8')).toBe(html);
  } finally { release.resolve(); statusPatch?.mockRestore(); forkPatch?.mockRestore(); await h.close(); }
});

test.skipIf(!browser)('operator status invalidation survives source reversion and restore', async () => {
  const h = await createHarness();
  try {
    await prepare(h, plan());
    await h.command('design-accept');
    expect((await h.status()).phase).toBe('completed');
    await writeFile(join(h.workspace, 'page.html'), '<h1>Changed</h1>');
    await h.command('design-status');
    await writeFile(join(h.workspace, 'page.html'), html);
    await h.runner.emit({ type: 'session_start' });
    const state = await h.status();
    expect(state.phase).toBe('active');
    expect(state.missing).toContain('capture:page');
    await h.command('design-accept');
    expect(h.notifications.at(-1)).toContain('missing or stale');
  } finally { await h.close(); }
});
