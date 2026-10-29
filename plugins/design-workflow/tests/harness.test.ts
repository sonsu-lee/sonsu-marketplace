import { expect, test } from 'bun:test';
import { readFile, writeFile } from 'node:fs/promises';
import { join } from 'node:path';
import { createHarness } from './sdk-host.ts';
import type { DesignPlan } from '../src/engine.ts';

const browser = process.env.DESIGN_WORKFLOW_CHROME;

test.skipIf(!browser)('real session enforces approval, source scope, evidence, operator wait and bounded refusal', async () => {
  const h = await createHarness();
  const initialTools = new Set(h.session.getEnabledToolNames());
  const plan: DesignPlan = {
    mode: 'design', paths: ['page.html'], goal: 'A visible real page', brief: 'Make a page that says Verified page.', facts: [],
    captures: [{ id: 'page', kind: 'file', target: 'page.html', width: 600, height: 400, steps: [{ action: 'assert-text', selector: 'h1', text: 'Verified page' }] }],
    checks: [{ id: 'source', command: process.execPath, args: ['-e', 'if (!require("fs").readFileSync("page.html", "utf8").includes("Verified page")) process.exit(2)'], timeoutMs: 2000 }],
  };
  async function stopPass() {
    return h.runner.emitSessionStop({ messages: [], turn_id: 0, session_id: h.sessions.getSessionId(), stop_hook_active: false, signal: new AbortController().signal });
  }
  try {
    // 1. 拒否された開始はファイル変更を許さず、承認後も広い実行経路を閉じる。
    await h.start(plan);
    await expect(h.call('design_write', { path: 'page.html', content: 'not approved' })).rejects.toThrow('No approved design run');
    h.choice.approve = true;
    await h.start(plan);
    await expect(h.call('bash', { command: 'true' })).rejects.toThrow('arbitrary writes');
    await expect(h.call('read', { path: 'skill://designing-interfaces/../../private' })).rejects.toThrow('arbitrary writes');
    await expect(h.call('design_write', { path: '../escape.html', content: 'bad' })).rejects.toThrow();
    await h.call('design_write', { path: 'page.html', content: '<!doctype html><title>Verified</title><h1>Verified page</h1>' });
    expect(await readFile(join(h.workspace, 'page.html'), 'utf8')).toContain('<h1>Verified page</h1>');
    await h.command('design-report');
    expect(h.notifications.at(-1)).toContain('missing or stale');
    // 2. 実キャプチャと検査を生成しても、操作側の承認なしには完了しない。
    const captured = await h.call('design_capture', { id: 'page' });
    const image = captured.content.find(part => part.type === 'image');
    expect(image?.type === 'image' && Buffer.from(image.data, 'base64').subarray(0, 8).toString('hex')).toBe('89504e470d0a1a0a');
    await h.call('design_check', { id: 'source' });
    await stopPass(); await stopPass();
    expect((await h.status()).phase).toBe('active');
    // 3. 報告は操作側のコマンドで検査し、表示した本文そのものを公式結果として公開する。
    await h.command('design-report');
    const reported = await h.status();
    expect(reported.missing).toEqual(['review']);
    const report = await readFile(reported.report!.path, 'utf8');
    expect(report).toContain('- capture `page`');
    await h.command('design-accept');
    const completed = await h.status();
    expect(completed.phase).toBe('completed');
    expect(completed.missing).toEqual([]);
    expect(h.published().at(-1)).toBe(report);
    expect(new Set(h.session.getEnabledToolNames())).toEqual(initialTools);
    // 4. 外部変更で古い完了を無効化し、未解決の機械的検証を無限再試行しない。
    await writeFile(join(h.workspace, 'page.html'), '<h1>Externally changed</h1>');
    await expect(h.call('bash', { command: 'true' })).rejects.toThrow('arbitrary writes');
    expect((await h.status()).evidence).toEqual([]);
    expect((await stopPass())?.decision).toBe('block');
    await stopPass();
    expect((await h.status()).phase).toBe('blocked');
    expect(new Set(h.session.getEnabledToolNames())).toEqual(initialTools);
    expect(h.errors).toEqual([]);
  } finally { await h.close(); }
});
