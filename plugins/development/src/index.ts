import type { ExtensionAPI } from '@oh-my-pi/pi-coding-agent';
import { readFile } from 'node:fs/promises';
import { spawnSync } from 'node:child_process';
import { resolve } from 'node:path';
import { fileURLToPath } from 'node:url';
import { needsEvidenceGate } from './guard.ts';

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
  pi.on('tool_call', (event, ctx) => {
    if (!needsEvidenceGate(event.toolName, event.input, ctx.cwd)) return;
    const cwd = event.toolName.toLowerCase() === 'bash' && typeof event.input.cwd === 'string'
      ? resolve(ctx.cwd, event.input.cwd)
      : ctx.cwd;
    const result = spawnSync('python3', [fileURLToPath(new URL('../hooks/evidence.py', import.meta.url)), 'gate'], {
      cwd,
      input: JSON.stringify({ cwd, tool_name: event.toolName, tool_input: event.input }),
      encoding: 'utf8',
      timeout: 30000,
    });
    if (result.status !== 0) return { block: true, reason: result.stderr || 'Evidence gate could not run.' };
    try {
      const evidence = JSON.parse(result.stdout);
      if (evidence.state === 'blocked') return { block: true, reason: evidence.reason };
      if (['pass', 'unverified', 'not_applicable'].includes(evidence.state)) return;
    } catch {
      // 判定を読み取れない場合も実行を止める。
    }
    return { block: true, reason: 'Evidence gate returned an invalid result.' };
  });
}
