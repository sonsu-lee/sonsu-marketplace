import { spawn } from 'node:child_process';
import { mkdtemp, rm } from 'node:fs/promises';
import { tmpdir } from 'node:os';
import { join } from 'node:path';
import type { Fact, RunState } from './engine.ts';

export interface Finding { quote: string; subject: string; reason: string }
export interface Verdict { decision: 'pass' | 'reject'; findings: Finding[] }
export type Author = (prompt: string, signal: AbortSignal) => Promise<string>;
export type Reviewer = (prompt: string, signal: AbortSignal) => Promise<string>;

const MAX_OUTPUT_BYTES = 4 * 1024 * 1024;
const APPROVAL: Record<Fact['approval'], string> = {
  approved: 'approved', rejected: 'rejected', pending: 'pending', 'not-supplied': 'not supplied (unknown)',
};
const AVAILABILITY: Record<Fact['availability'], string> = {
  inspectable: 'supplied for inspection in this run', 'exists-not-supplied': 'exists, not supplied for inspection',
  'does-not-exist': 'does not exist', unknown: 'unknown',
};

export function factTable(facts: Fact[]): string {
  if (!facts.length) return 'No project facts were confirmed for this run. Approval, sign-off and availability of any artifact are unknown.';
  return ['| Subject | Approval | Availability |', '| --- | --- | --- |',
    ...facts.map(f => `| ${f.subject} | ${APPROVAL[f.approval]} | ${AVAILABILITY[f.availability]} |`)].join('\n');
}

function evidenceSummary(state: RunState): string {
  if (!state.evidence.length) return 'No captures or checks were run. Nothing in this report was rendered or tested.';
  return state.evidence.map(item => `- ${item.kind} \`${item.id}\`: ${item.artifacts.map(a => `${a.path.split('/').pop()} (sha256 ${a.sha256.slice(0, 12)})`).join(', ')}`).join('\n');
}

export function authorPrompt(state: RunState): string {
  return `Write the body of the final report for the operator-controlled design run below. Return only Markdown, no preamble.

Cover what was done or proposed, what the recorded evidence shows, and what remains unverified. The controller adds the confirmed fact table and the evidence list above your text; do not restate them, and do not state an approval, rejection, sign-off requirement or artifact availability that the table does not give. Where the table says "not supplied", treat it as unknown; you may advise confirming whether approval is needed and who gives it. Any other project state the request and table do not give, such as whether supplier requirements were gathered or an approver exists, is also unknown: say what to confirm instead of asserting it.

Mode: ${state.plan.mode}
Goal: ${state.plan.goal}

Original request:
${state.plan.brief}

Confirmed facts:
${factTable(state.plan.facts)}

Recorded evidence:
${evidenceSummary(state)}`;
}

export function renderReport(state: RunState, body: string): string {
  return `# Design report

Mode: ${state.plan.mode}. Source revision: ${state.revision.slice(0, 12)}.

## Confirmed project facts

${factTable(state.plan.facts)}

## Recorded evidence

${evidenceSummary(state)}

## Report

${body.trim()}

## Limits

The facts above are what the operator confirmed for this run. A fresh review checked this report's statements against them; that review is a model judgment and can miss errors. Operator acceptance records review of these exact bytes, not brand approval, accessibility conformance or production sign-off.
`;
}

export function reviewPrompt(state: RunState, body: string): string {
  return `You check one candidate report against the user's original request and a fact table maintained by the controller. You did not write the report.

Report every sentence that asserts, as a present fact, a project state that the fact table does not support. Project states are:
- approval, rejection or sign-off status of a specific artifact, including saying it is pending, outstanding, still needed, not yet approved or undecided when the table says "not supplied";
- that sign-off or approval is required, when the table does not establish it (for example "get sign-off on the variant" or "it will need sign-off");
- whether an artifact exists, is missing or was inspected;
- whether a test, proof, render or check was performed, beyond the recorded evidence.

Rules:
- "not supplied" means unknown. Stating the unknown as unknown is correct.
- A status the table gives for one artifact does not transfer to another artifact.
- Advising the user to confirm whether approval is needed and who gives it is allowed.
- Do not report design opinions, tone or wording preferences.

Return only JSON: {"decision": "pass" | "reject", "findings": [{"quote": "<exact sentence from the report>", "subject": "<artifact>", "reason": "<one sentence>"}]}. Use "reject" when there is at least one finding.

<original_request>
${state.plan.brief}
</original_request>

<fact_table>
${factTable(state.plan.facts)}
</fact_table>

<recorded_evidence>
${evidenceSummary(state)}
</recorded_evidence>

<candidate_report>
${body.trim()}
</candidate_report>`;
}

// 不明・不正な判定は合格に変換せず、呼び出し側で公開を止める。
export function parseVerdict(text: string): Verdict {
  const decoder = /\{[\s\S]*\}/.exec(text);
  if (!decoder) throw new Error('Reviewer returned no JSON verdict');
  let value: unknown;
  try { value = JSON.parse(decoder[0]); } catch { throw new Error('Reviewer verdict is not valid JSON'); }
  const verdict = value as { decision?: unknown; findings?: unknown };
  if (verdict.decision !== 'pass' && verdict.decision !== 'reject') throw new Error('Reviewer verdict has no pass/reject decision');
  if (!Array.isArray(verdict.findings)) throw new Error('Reviewer verdict has no findings list');
  const findings = verdict.findings.map((item): Finding => {
    const entry = item as Record<string, unknown>;
    return { quote: String(entry?.quote ?? ''), subject: String(entry?.subject ?? ''), reason: String(entry?.reason ?? '') };
  });
  return { decision: verdict.decision === 'pass' && !findings.length ? 'pass' : 'reject', findings };
}

// 作者の文脈を引き継がない新しい omp 子プロセスで、道具なしの判定を一度だけ得る。
export function ompReviewer(model: string, thinking: string | undefined, timeoutMs = 600_000): Reviewer {
  return async (prompt, signal) => {
    signal.throwIfAborted();
    if (process.platform === 'win32') throw new Error('The report reviewer requires POSIX process-group cancellation.');
    const cwd = await mkdtemp(join(tmpdir(), 'design-review-'));
    try {
      const args = ['-p', '--mode', 'json', '--no-session', '--no-title', '--no-context-files', '--no-rules',
        '--no-extensions', '--no-tools', '--no-skills', '--model', model, ...(thinking ? ['--thinking', thinking] : []), prompt];
      const { promise, resolve, reject } = Promise.withResolvers<string>();
      const child = spawn('omp', args, { cwd, shell: false, detached: true, stdio: ['ignore', 'pipe', 'pipe'] });
      const out: Buffer[] = [];
      let bytes = 0;
      let failure: Error | undefined;
      const kill = (reason: string) => {
        failure ??= new Error(reason);
        if (child.pid) { try { process.kill(-child.pid, 'SIGKILL'); } catch { child.kill('SIGKILL'); } }
      };
      const cancel = () => kill('Report review cancelled');
      const timer = setTimeout(() => kill(`Report review timed out after ${timeoutMs}ms`), timeoutMs);
      signal.addEventListener('abort', cancel, { once: true });
      if (signal.aborted) cancel();
      child.stdout.on('data', (chunk: Buffer) => { bytes += chunk.length; if (bytes > MAX_OUTPUT_BYTES) kill('Reviewer output exceeded 4MiB'); else out.push(chunk); });
      child.stderr.resume();
      child.once('error', error => { failure ??= error; });
      child.once('close', code => {
        clearTimeout(timer);
        signal.removeEventListener('abort', cancel);
        if (failure) return reject(failure);
        if (code !== 0) return reject(new Error(`Reviewer exited ${code}`));
        let text = '';
        for (const line of Buffer.concat(out).toString('utf8').split('\n')) {
          if (!line.startsWith('{')) continue;
          let event: { type?: string; message?: { role?: string; content?: unknown; errorMessage?: string } };
          try { event = JSON.parse(line); } catch { continue; }
          if (event.type !== 'message_end' || event.message?.role !== 'assistant') continue;
          if (event.message.errorMessage) return reject(new Error(`Reviewer failed: ${event.message.errorMessage}`));
          const parts = Array.isArray(event.message.content) ? event.message.content : [];
          text = parts.filter((p: { type?: string }) => p?.type === 'text').map((p: { text?: string }) => p.text ?? '').join('\n') || text;
        }
        if (!text.trim()) return reject(new Error('Reviewer returned no answer'));
        resolve(text);
      });
      return await promise;
    } finally { await rm(cwd, { recursive: true, force: true }); }
  };
}
