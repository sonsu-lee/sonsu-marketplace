import { afterAll, describe, expect, test } from 'bun:test';
import type { ExtensionAPI } from '@oh-my-pi/pi-coding-agent';
import { mkdtempSync, mkdirSync, rmSync, symlinkSync, writeFileSync } from 'node:fs';
import { execFileSync } from 'node:child_process';
import { tmpdir } from 'node:os';
import { join } from 'node:path';
import { actionReason } from '../src/guard.ts';
import development from '../src/index.ts';

const root = mkdtempSync(join(tmpdir(), 'development-guard-'));
const workspace = join(root, 'workspace');
const external = join(root, 'external');
mkdirSync(workspace);
mkdirSync(external);
writeFileSync(join(external, 'file'), 'content');
symlinkSync(join(external, 'file'), join(workspace, 'file-link'));
symlinkSync(external, join(workspace, 'external-link'));
afterAll(() => rmSync(root, { recursive: true, force: true }));

test('blocks a recognized write when the operator declines', async () => {
  const handlers: Record<string, unknown> = {};
  development({ on: (key: string, fn: unknown) => { handlers[key] = fn; } } as unknown as ExtensionAPI);
  const toolCall = handlers.tool_call;
  if (typeof toolCall !== 'function') throw new Error('tool_call handler was not registered');
  const ctx = { cwd: workspace, hasUI: true, ui: { confirm: async () => false } };
  expect(await toolCall({ toolName: 'write', input: { path: join(external, 'new') } }, ctx)).toMatchObject({ block: true });
});

test('injects router policy without accumulating transcript messages or affecting subagents', async () => {
  const handlers: Record<string, unknown> = {};
  development({ on: (name: string, handler: unknown) => { handlers[name] = handler; } } as unknown as ExtensionAPI);
  const handler = handlers.before_agent_start;
  if (typeof handler !== 'function') throw new Error('before_agent_start handler was not registered');
  const event = { systemPrompt: ['host policy'] };
  const first = await handler(event, { agent: { kind: 'main' } });
  const next = await handler(event, { agent: { kind: 'main' } });
  expect(first.systemPrompt[0]).toBe('host policy');
  expect(first.systemPrompt[1]).toContain('# Working on tasks');
  expect(next).toEqual(first);
  expect(first.message).toBeUndefined();
  expect(await handler(event, { agent: { kind: 'subagent' } })).toBeUndefined();
});

describe('recognized actions requiring approval', () => {
  test('detects Git options before a commit without blocking an ordinary test', () => {
    expect(actionReason('bash', { command: 'git -c user.name=Example commit -m example' }, workspace)).toContain('approval');
    expect(actionReason('bash', { command: 'python3 -m unittest' }, workspace)).toBeUndefined();
  });

  test('permits the read-only merge-base used in reviews but requires approval for a merge', () => {
    expect(actionReason('bash', { command: 'git merge-base HEAD main' }, workspace)).toBeUndefined();
    expect(actionReason('bash', { command: 'git merge main' }, workspace)).toContain('approval');
  });

  test('detects remote publication and permits read-only MCP calls', () => {
    expect(actionReason('mcp__github_create_issue', {}, workspace)).toContain('approval');
    expect(actionReason('mcp__github_get_issue', {}, workspace)).toBeUndefined();
  });

  test('recognizes writes outside the workspace including through symlinks', () => {
    expect(actionReason('write', { path: join(external, 'file') }, workspace)).toContain('approval');
    expect(actionReason('write', { path: `[${join(external, 'file')}#ABCD]` }, workspace)).toContain('approval');
    expect(actionReason('write', { path: `[${join(external, 'file')}#ab12] ` }, workspace)).toContain('approval');
    expect(actionReason('write', { path: `[${join(external, 'file')}]` }, workspace)).toContain('approval');
    expect(actionReason('write', { path: 'external-link/file' }, workspace)).toContain('approval');
    expect(actionReason('write', { path: 'inside.txt' }, workspace)).toBeUndefined();
    expect(actionReason('write', { path: '[inside.txt#ABCD]' }, workspace)).toBeUndefined();
  });

  test('recognizes multi-file and alternate edit mode targets outside the workspace', () => {
    expect(actionReason('edit', { paths: ['inside.txt', join(external, 'file')] }, workspace)).toContain('approval');
    expect(actionReason('edit', { path: 'inside.txt', edits: [{ rename: join(external, 'file') }] }, workspace)).toContain('approval');
    expect(actionReason('edit', { input: `*** Begin Patch\n*** Add File: ${join(external, 'file')}\n+text\n*** End Patch\n` }, workspace)).toContain('approval');
    expect(actionReason('edit', { input: `[${join(external, 'file')}#ab12] \nPUT 1.=1:\n+text\n` }, workspace)).toContain('approval');
    expect(actionReason('edit', { input: `*** Edit File: ${join(external, 'file')} all\n` }, workspace)).toContain('approval');
    expect(actionReason('edit', { input: '*** Edit File: file-link all\n' }, workspace)).toContain('approval');
    expect(actionReason('edit', { input: '*** Add File: "../outside.txt"\n' }, workspace)).toContain('approval');
    expect(actionReason('edit', { input: '*** Update File: inside.txt\n MV ../outside.txt\n' }, workspace)).toBeUndefined();
  });

  test('recognizes a patch move to an outside destination', () => {
    const patch = `*** Begin Patch\n[inside.txt#ABCD]\nMV ${join(external, 'file')}\n*** End Patch\n`;
    expect(actionReason('edit', { input: patch }, workspace)).toContain('approval');
    expect(actionReason('edit', { input: `[inside.txt#ABCD]\n  MV\t'${join(external, 'file')}'\n` }, workspace)).toContain('approval');
  });

  test('checks the shell working directory rather than the parent workspace', async () => {
    const repo = join(workspace, 'nested-repo');
    mkdirSync(repo);
    const git = (...args: string[]) => execFileSync('git', ['-C', repo, ...args]);
    git('init', '-q');
    writeFileSync(join(repo, '.workflow-checks.json'), JSON.stringify({
      checks: [{ id: 'check', argv: ['python3', '-c', 'pass'], actions: ['commit'] }],
    }));
    git('add', '.');
    const handlers: Record<string, unknown> = {};
    development({ on: (name: string, handler: unknown) => { handlers[name] = handler; } } as unknown as ExtensionAPI);
    const handler = handlers.tool_call;
    if (typeof handler !== 'function') throw new Error('tool_call handler was not registered');
    const result = await handler(
      { toolName: 'bash', input: { command: 'git commit -m change', cwd: 'nested-repo' } },
      { cwd: workspace, hasUI: true, ui: { confirm: async () => true } },
    );
    expect(result.block).toBe(true);
    expect(result.reason).toContain('Missing or stale evidence');
  });

  test('blocks if the staged target changes during operator confirmation', async () => {
    const repo = join(root, 'repo');
    mkdirSync(repo);
    const git = (...args: string[]) => execFileSync('git', ['-C', repo, ...args]);
    // 1. 検査済みツリーを作り、確認前に有効な証拠を用意する。
    git('init', '-q');
    git('config', 'commit.gpgsign', 'false');
    git('config', 'user.name', 'Scenario');
    git('config', 'user.email', 'scenario@example.invalid');
    writeFileSync(join(repo, 'data.txt'), 'one\n');
    writeFileSync(join(repo, '.workflow-checks.json'), JSON.stringify({
      checks: [{ id: 'check', argv: ['python3', '-c', 'print("ok")'], actions: ['commit'] }],
    }));
    git('add', '.');
    git('commit', '-qm', 'baseline');
    writeFileSync(join(repo, 'data.txt'), 'two\n');
    git('add', '.');
    execFileSync('python3', [join(import.meta.dir, '../hooks/evidence.py'), 'run', 'check'], { cwd: repo });

    // 2. 確認中の変更を再検査し、古い証拠で操作を許可しない。
    const handlers: Record<string, unknown> = {};
    const host = { on: (name: string, handler: unknown) => { handlers[name] = handler; } };
    // この検証はイベント登録のみを使うため、ホストの残りの API は不要。
    development(host as unknown as ExtensionAPI);
    const handler = handlers.tool_call;
    if (typeof handler !== 'function') throw new Error('tool_call handler was not registered');
    const result = await handler(
      { toolName: 'bash', input: { command: 'git commit -m change' } },
      { cwd: repo, hasUI: true, ui: { confirm: async () => {
        writeFileSync(join(repo, 'data.txt'), 'three\n');
        git('add', '.');
        return true;
      } } },
    );
    expect(result).toEqual({ block: true, reason: 'Target or evidence changed during approval.' });
  });
});
