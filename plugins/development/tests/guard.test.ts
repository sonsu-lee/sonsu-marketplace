import { afterAll, describe, expect, test } from 'bun:test';
import type { ExtensionAPI } from '@oh-my-pi/pi-coding-agent';
import { mkdtempSync, mkdirSync, rmSync, symlinkSync, writeFileSync } from 'node:fs';
import { execFileSync } from 'node:child_process';
import { tmpdir } from 'node:os';
import { join } from 'node:path';
import { needsEvidenceGate } from '../src/guard.ts';
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

describe('recognized actions requiring evidence inspection', () => {
  test('detects Git options before a commit without blocking an ordinary test', () => {
    expect(needsEvidenceGate('bash', { command: 'git -c user.name=Example commit -m example' }, workspace)).toBe(true);
    expect(needsEvidenceGate('bash', { command: 'python3 -m unittest' }, workspace)).toBe(false);
  });

  test('permits the read-only merge-base used in reviews but recognizes a merge', () => {
    expect(needsEvidenceGate('bash', { command: 'git merge-base HEAD main' }, workspace)).toBe(false);
    expect(needsEvidenceGate('bash', { command: 'git merge main' }, workspace)).toBe(true);
  });

  test('detects remote publication and permits read-only MCP calls', () => {
    expect(needsEvidenceGate('mcp__github_create_issue', {}, workspace)).toBe(true);
    expect(needsEvidenceGate('mcp__github_get_issue', {}, workspace)).toBe(false);
  });

  test('recognizes writes outside the workspace including through symlinks', () => {
    expect(needsEvidenceGate('write', { path: join(external, 'file') }, workspace)).toBe(true);
    expect(needsEvidenceGate('write', { path: `[${join(external, 'file')}#ABCD]` }, workspace)).toBe(true);
    expect(needsEvidenceGate('write', { path: `[${join(external, 'file')}#ab12] ` }, workspace)).toBe(true);
    expect(needsEvidenceGate('write', { path: `[${join(external, 'file')}]` }, workspace)).toBe(true);
    expect(needsEvidenceGate('write', { path: 'external-link/file' }, workspace)).toBe(true);
    expect(needsEvidenceGate('write', { path: 'inside.txt' }, workspace)).toBe(false);
    expect(needsEvidenceGate('write', { path: '[inside.txt#ABCD]' }, workspace)).toBe(false);
  });

  test('recognizes multi-file and alternate edit mode targets outside the workspace', () => {
    expect(needsEvidenceGate('edit', { paths: ['inside.txt', join(external, 'file')] }, workspace)).toBe(true);
    expect(needsEvidenceGate('edit', { path: 'inside.txt', edits: [{ rename: join(external, 'file') }] }, workspace)).toBe(true);
    expect(needsEvidenceGate('edit', { input: `*** Begin Patch\n*** Add File: ${join(external, 'file')}\n+text\n*** End Patch\n` }, workspace)).toBe(true);
    expect(needsEvidenceGate('edit', { input: `[${join(external, 'file')}#ab12] \nPUT 1.=1:\n+text\n` }, workspace)).toBe(true);
    expect(needsEvidenceGate('edit', { input: `*** Edit File: ${join(external, 'file')} all\n` }, workspace)).toBe(true);
    expect(needsEvidenceGate('edit', { input: '*** Edit File: file-link all\n' }, workspace)).toBe(true);
    expect(needsEvidenceGate('edit', { input: '*** Add File: "../outside.txt"\n' }, workspace)).toBe(true);
    expect(needsEvidenceGate('edit', { input: '*** Update File: inside.txt\n MV ../outside.txt\n' }, workspace)).toBe(false);
  });

  test('recognizes a patch move to an outside destination', () => {
    const patch = `*** Begin Patch\n[inside.txt#ABCD]\nMV ${join(external, 'file')}\n*** End Patch\n`;
    expect(needsEvidenceGate('edit', { input: patch }, workspace)).toBe(true);
    expect(needsEvidenceGate('edit', { input: `[inside.txt#ABCD]\n  MV\t'${join(external, 'file')}'\n` }, workspace)).toBe(true);
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
      { cwd: workspace },
    );
    expect(result.block).toBe(true);
    expect(result.reason).toContain('Missing or stale evidence');
  });
});
