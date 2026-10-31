import { mkdtemp, mkdir, rm, writeFile } from 'node:fs/promises';
import { tmpdir } from 'node:os';
import { join, resolve } from 'node:path';
import { randomUUID } from 'node:crypto';
import { AgentRegistry, AuthStorage, createAgentSession, ModelRegistry, SessionManager } from '@oh-my-pi/pi-coding-agent';
import type { AgentSession, AgentToolResult, ExtensionActions, ExtensionContextActions, ExtensionRunner, ToolDefinition } from '@oh-my-pi/pi-coding-agent';
import { loadSkillsFromDir } from '@oh-my-pi/pi-coding-agent/extensibility/skills';
import designWorkflow from '../src/index.ts';
import type { DesignWorkflowOptions } from '../src/index.ts';
import type { DesignPlan, RunState } from '../src/engine.ts';

export interface Harness {
  root: string;
  workspace: string;
  sessions: SessionManager;
  session: AgentSession;
  runner: ExtensionRunner;
  choice: { approve: boolean };
  notifications: string[];
  errors: string[];
  call(name: string, input?: Record<string, unknown>, signal?: AbortSignal): Promise<AgentToolResult>;
  command(name: string, args?: string): Promise<void>;
  /** Text of every official design result message, in order. */
  published(): string[];
  start(plan: DesignPlan): Promise<void>;
  status(): Promise<RunState>;
  close(): Promise<void>;
}

// 既定のテスト用作者・検査者はモデルを呼ばず、固定の本文と合格判定を返す。
export const passingReport: DesignWorkflowOptions = {
  author: () => async () => 'The proposal keeps the approved scope. Nothing beyond the recorded evidence was rendered or tested.',
  reviewer: () => async () => '{"decision": "pass", "findings": []}',
};

export async function createHarness(customTools: ToolDefinition[] = [], options: DesignWorkflowOptions = passingReport): Promise<Harness> {
  const root = await mkdtemp(join(tmpdir(), 'design-sdk-test-'));
  const workspace = join(root, 'workspace');
  await mkdir(workspace);
  const sessions = SessionManager.create(workspace, join(root, 'sessions'));
  const auth = await AuthStorage.create(join(root, 'auth.db'));
  const registry = new ModelRegistry(auth, join(root, 'models.yml'), {
    ignoreLocalModelConfig: true,
    fetch: async () => { throw new Error('Model network is forbidden in this integration host'); },
  });
  const model = registry.find('anthropic', 'claude-opus-5-5');
  if (!model) throw new Error('Pinned SDK is missing the bundled regression model');
  const skills = await loadSkillsFromDir({ dir: resolve(import.meta.dir, '../skills'), source: 'fixture:project' });
  if (skills.warnings.length) throw new Error(JSON.stringify(skills.warnings));
  const { session } = await createAgentSession({
    cwd: workspace, agentDir: join(root, 'agent'), authStorage: auth, modelRegistry: registry,
    model, sessionManager: sessions, extensions: [pi => designWorkflow(pi, options)], disableExtensionDiscovery: true,
    customTools,
    preloadedCustomToolPaths: [], skills: skills.skills, rules: [], contextFiles: [], promptTemplates: [], slashCommands: [],
    enableMCP: false, enableLsp: false, enableIrc: false, skipPythonPreflight: true, cacheWarming: false,
    bindProcessState: false, agentRegistry: new AgentRegistry(), hasUI: true,
    systemPrompt: 'Model-free extension integration host. No model requests are permitted.',
    toolNames: ['read', 'write', 'edit', 'bash', 'ask', 'todo'],
  });
  const runner = session.extensionRunner;
  if (!runner) throw new Error('No extension runner in the actual AgentSession');
  const errors: string[] = [];
  const notifications: string[] = [];
  runner.onError(error => errors.push(error.error));
  const choice = { approve: false };
  const unexpected = (): never => { throw new Error('Unexpected model/session operation in integration host'); };
  const actions: ExtensionActions = {
    sendMessage: (message, options) => { void session.sendCustomMessage(message, options).catch(error => errors.push(String(error))); },
    sendUserMessage: unexpected,
    appendEntry: (type, data) => { sessions.appendCustomEntry(type, data); },
    setLabel: (id, label) => { sessions.appendLabelChange(id, label); },
    getActiveTools: () => session.getEnabledToolNames(), getAllTools: () => session.getAllToolInfos(),
    setActiveTools: names => session.setActiveToolsByName(names), getCommands: () => [],
    setModel: unexpected, getThinkingLevel: () => session.thinkingLevel,
    setThinkingLevel: level => session.setThinkingLevel(level),
    getSessionName: () => sessions.getSessionName(), setSessionName: unexpected,
  };
  const context: ExtensionContextActions = {
    getModel: () => session.model, isIdle: () => !session.isStreaming,
    abort: () => { void session.abort(); }, hasPendingMessages: () => session.queuedMessageCount > 0,
    shutdown: unexpected, getContextUsage: () => session.getContextUsage(), compact: unexpected,
    getSystemPrompt: () => session.systemPrompt,
  };
  // UI の選択だけを入力として差し替え、ツール選択・中断・fork は実セッションに接続する。
  const ui = { ...runner.getUIContext(), confirm: async () => choice.approve, notify: (text: string) => { notifications.push(text); } };
  runner.initialize(actions, context, undefined, ui, 'tui');
  await runner.emit({ type: 'session_start' });
  async function call(name: string, input: Record<string, unknown> = {}, signal = new AbortController().signal) {
    const tool = session.agent.state.tools.find(candidate => candidate.name === name);
    if (!tool) throw new Error(`Tool is not advertised to the actual agent: ${name}`);
    return tool.execute(randomUUID(), input, signal);
  }
  const command = async (name: string, args = '') => {
    const entry = runner.getCommand(name);
    if (!entry) throw new Error(`Missing command ${name}`);
    await entry.handler(args, runner.createCommandContext());
  };
  async function start(plan: DesignPlan) {
    const file = join(root, `plan-${randomUUID()}.json`);
    await writeFile(file, JSON.stringify(plan));
    await command('design-start', file);
  }
  async function status(): Promise<RunState> {
    return (await call('design_status')).details as RunState;
  }
  async function close() {
    await session.dispose();
    await sessions.close(); auth.close();
    await rm(root, { recursive: true, force: true });
  }
  function published(): string[] {
    return sessions.getEntries().flatMap(entry => entry.type === 'custom_message' && entry.customType === 'sonsu.design-workflow.result.v1' && typeof entry.content === 'string' ? [entry.content] : []);
  }
  return { root, workspace, sessions, session, runner, choice, notifications, errors, call, command, published, start, status, close };
}
