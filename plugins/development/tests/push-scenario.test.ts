import { afterAll, beforeAll, expect, test } from 'bun:test';
import { execFileSync } from 'node:child_process';
import { randomUUID } from 'node:crypto';
import { mkdirSync, mkdtempSync, rmSync, writeFileSync } from 'node:fs';
import { tmpdir } from 'node:os';
import { join, resolve } from 'node:path';
import type * as Sdk from '@oh-my-pi/pi-coding-agent';
import development from '../src/index.ts';

// 実ホストは CI の固定クライアント（.github/ci-clients）から読み込む。このパッケージは依存を
// 持たないため静的 import では解決できず、所在を実行時に指定する。
// ローカルでは `bun install --frozen-lockfile --cwd .github/ci-clients` が前提。
const clients = resolve(import.meta.dir, '../../../.github/ci-clients');
const sdk: typeof Sdk = await import(Bun.resolveSync('@oh-my-pi/pi-coding-agent', clients));
const { AgentRegistry, AuthStorage, ModelRegistry, SessionManager, createAgentSession } = sdk;

const root = mkdtempSync(join(tmpdir(), 'development-push-'));
const remote = join(root, 'remote.git');
const repo = join(root, 'repo');
const runner = resolve(import.meta.dir, '../hooks/evidence.py');
const isolated = { GIT_CONFIG_GLOBAL: join(root, 'gitconfig'), GIT_CONFIG_NOSYSTEM: '1' };
const savedGitEnv = Object.entries(process.env).filter(([key]) => key.startsWith('GIT_'));
const prompts: string[] = [];
let session: Sdk.AgentSession | undefined;
let sessions: Sdk.SessionManager | undefined;
let auth: Sdk.AuthStorage | undefined;

const git = (cwd: string, ...args: string[]) => execFileSync('git', ['-C', cwd, ...args], { encoding: 'utf8' }).trim();
const remoteHead = () => git(remote, 'rev-parse', 'refs/heads/main');

async function bash(command: string) {
  const tool = session?.agent.state.tools.find(candidate => candidate.name === 'bash');
  if (!tool) throw new Error('bash is not advertised to the actual agent');
  return tool.execute(randomUUID(), { command }, new AbortController().signal);
}

beforeAll(async () => {
  // Git の呼び出しが親の作業ツリーやインデックスを操作しないようにする。
  for (const [key] of savedGitEnv) delete process.env[key];
  Object.assign(process.env, isolated);
  writeFileSync(isolated.GIT_CONFIG_GLOBAL, '');

  // 1. 使い捨ての bare リモートと、上流追跡済みのリポジトリを作る。
  execFileSync('git', ['init', '-q', '--bare', '-b', 'main', remote]);
  mkdirSync(repo);
  git(repo, 'init', '-q', '-b', 'main');
  git(repo, 'config', 'user.name', 'Scenario');
  git(repo, 'config', 'user.email', 'scenario@example.invalid');
  git(repo, 'config', 'commit.gpgsign', 'false');
  writeFileSync(join(repo, 'data.txt'), 'one\n');
  writeFileSync(join(repo, '.workflow-checks.json'), JSON.stringify({
    checks: [{ id: 'check', argv: ['python3', '-c', 'print("ok")'], actions: ['push'] }],
  }));
  git(repo, 'add', '.');
  git(repo, 'commit', '-qm', 'baseline');
  git(repo, 'remote', 'add', 'origin', remote);
  git(repo, 'push', '-q', '-u', 'origin', 'main');
  writeFileSync(join(repo, 'data.txt'), 'two\n');
  git(repo, 'commit', '-qam', 'change');

  // 2. 拡張を実際の AgentSession に登録し、bash ツール経由で tool_call を配送させる。
  const store = SessionManager.create(repo, join(root, 'sessions'));
  const credentials = await AuthStorage.create(join(root, 'auth.db'));
  sessions = store;
  auth = credentials;
  const registry = new ModelRegistry(credentials, join(root, 'models.yml'), {
    ignoreLocalModelConfig: true,
    fetch: async () => { throw new Error('Model network is forbidden in this integration host'); },
  });
  const model = registry.find('anthropic', 'claude-opus-5-5');
  if (!model) throw new Error('Pinned SDK is missing the bundled regression model');
  const { session: agent } = await createAgentSession({
    cwd: repo, agentDir: join(root, 'agent'), authStorage: credentials, modelRegistry: registry,
    model, sessionManager: store, extensions: [development], disableExtensionDiscovery: true,
    preloadedCustomToolPaths: [], skills: [], rules: [], contextFiles: [], promptTemplates: [], slashCommands: [],
    enableMCP: false, enableLsp: false, enableIrc: false, skipPythonPreflight: true, cacheWarming: false,
    bindProcessState: false, agentRegistry: new AgentRegistry(), hasUI: true,
    systemPrompt: 'Model-free extension integration host. No model requests are permitted.',
    toolNames: ['bash'],
  });
  session = agent;
  const host = agent.extensionRunner;
  if (!host) throw new Error('No extension runner in the actual AgentSession');
  const unexpected = (): never => { throw new Error('Unexpected model/session operation in integration host'); };
  // 対話 UI を用意し、プラグインまたはホストが出した確認をすべて記録して拒否する。
  const refuse = (kind: string, value: unknown) => async () => { prompts.push(kind); return value; };
  const ui = {
    ...host.getUIContext(),
    confirm: refuse('confirm', false), select: refuse('select', undefined),
    input: refuse('input', undefined), approve: refuse('approve', undefined),
  };
  host.initialize({
    sendMessage: unexpected, sendUserMessage: unexpected, appendEntry: unexpected, setLabel: unexpected,
    getActiveTools: () => agent.getEnabledToolNames(), getAllTools: () => agent.getAllToolInfos(),
    setActiveTools: unexpected, getCommands: () => [], setModel: unexpected,
    getThinkingLevel: () => agent.thinkingLevel, setThinkingLevel: unexpected,
    getSessionName: () => store.getSessionName(), setSessionName: unexpected,
  }, {
    getModel: () => agent.model, isIdle: () => !agent.isStreaming, abort: unexpected,
    hasPendingMessages: () => false, shutdown: unexpected, getContextUsage: () => agent.getContextUsage(),
    compact: unexpected, getSystemPrompt: () => agent.systemPrompt,
  }, undefined, ui, 'tui');
}, 60000);

afterAll(async () => {
  await session?.dispose();
  await sessions?.close();
  auth?.close();
  for (const key of Object.keys(isolated)) delete process.env[key];
  Object.assign(process.env, Object.fromEntries(savedGitEnv));
  rmSync(root, { recursive: true, force: true });
});

test('a declared push check blocks without evidence and lets a matching receipt push without prompting', async () => {
  const published = remoteHead();
  const local = git(repo, 'rev-parse', 'HEAD');
  expect(local).not.toBe(published);

  // 3. 証拠がなければ、実ホストの bash 実行前に拒否され、リモートは変わらない。
  await expect(bash('git push')).rejects.toThrow('Missing or stale evidence for check');
  expect(remoteHead()).toBe(published);

  // 4. 現在の HEAD ツリーに一致する証拠を記録すると、追加の確認なしに実際に push される。
  execFileSync('python3', [runner, 'run', 'check', '--root', repo], { stdio: 'ignore' });
  await bash('git push');
  expect(remoteHead()).toBe(local);
  expect(prompts).toEqual([]);
}, 60000);
