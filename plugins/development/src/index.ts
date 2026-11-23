import type { ExtensionAPI, ExtensionContext } from '@oh-my-pi/pi-coding-agent';
import { readFile } from 'node:fs/promises';
import { spawnSync } from 'node:child_process';
import { resolve } from 'node:path';
import { fileURLToPath } from 'node:url';
import { actionReason } from './guard.ts';

export default function development(pi: ExtensionAPI): void {
  const log = (name: string, sessionId: string) => {
    if (!process.env.SONSU_WORK_LOG_DIR) return;
    const result = spawnSync('python3', [fileURLToPath(new URL('../hooks/work_log.py', import.meta.url)), 'omp'], {
      input: JSON.stringify({ hook_event_name: name, session_id: sessionId }),
      encoding: 'utf8',
      timeout: 5000,
    });
    if (result.error || result.status !== 0 || result.stderr) {
      console.warn(`Work log unavailable: ${result.error?.message ?? result.stderr}`);
    }
  };
  pi.on('session_start', (_event, ctx) => {
    if (ctx.agent.kind === 'main') log('SessionStart', ctx.sessionManager.getSessionId());
  });
  pi.on('session_shutdown', (_event, ctx) => {
    if (ctx.agent.kind === 'main') log('SessionEnd', ctx.sessionManager.getSessionId());
  });
  pi.on('before_agent_start', async (event, ctx) => {
    if (ctx.agent.kind !== 'main') return;
    const content = await readFile(new URL('../skills/working-on-tasks/SKILL.md', import.meta.url), 'utf8');
    return { systemPrompt: [...event.systemPrompt, content] };
  });
  async function confirm(ctx: ExtensionContext, reason: string, cwd: string, tool: string, payload: Record<string, unknown>) {
    const inspect = () => {
      const result = spawnSync('python3', [fileURLToPath(new URL('../hooks/evidence.py', import.meta.url)), 'gate'], {
        cwd,
        input: JSON.stringify({ cwd, tool_name: tool, ...payload }),
        encoding: 'utf8',
        timeout: 30000,
      });
      if (result.status !== 0) throw new Error(result.stderr || 'Evidence gate could not run.');
      return JSON.parse(result.stdout) as { state: string; reason?: string; tree?: string; checks?: unknown };
    };
    const evidence = inspect();
    if (evidence.state === 'blocked') return { block: true, reason: evidence.reason };
    if (!ctx.hasUI) return { block: true, reason: `${reason} No interactive approval is available. ${evidence.reason ?? ''}` };
    const approved = await ctx.ui.confirm(reason, JSON.stringify({
      tool,
      ...payload,
      evidence,
      note: 'A receipt records execution, not test adequacy or a quality score.',
    }, null, 2));
    if (!approved) return { block: true, reason: `${reason} The operator did not approve.` };
    if (JSON.stringify(inspect()) !== JSON.stringify(evidence)) return { block: true, reason: 'Target or evidence changed during approval.' };
  }
  pi.on('tool_call', async (event, ctx) => {
    const reason = actionReason(event.toolName, event.input, ctx.cwd);
    if (!reason) return;
    const cwd = event.toolName.toLowerCase() === 'bash' && typeof event.input.cwd === 'string'
      ? resolve(ctx.cwd, event.input.cwd)
      : ctx.cwd;
    return confirm(ctx, reason, cwd, event.toolName, { tool_input: event.input });
  });
}
