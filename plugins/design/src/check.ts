import { spawn } from 'node:child_process';
import type { CheckSpec } from './engine.ts';

const MAX_OUTPUT_BYTES = 1024 * 1024;
type CheckResult = { stdout: string; stderr: string; code: number; killed: boolean };

export async function runCheck(check: CheckSpec, cwd: string, signal: AbortSignal): Promise<CheckResult> {
  signal.throwIfAborted();
  if (process.platform === 'win32') throw new Error('Strict process checks require POSIX process-group cancellation; Windows is not supported.');
  const { promise, resolve, reject } = Promise.withResolvers<CheckResult>();
  // 1. シェルを介さず起動し、子孫も中断できる専用プロセス群を作る。
  const child = spawn(check.command, check.args, { cwd, shell: false, detached: true, stdio: ['ignore', 'pipe', 'pipe'] });
  const stdout: Buffer[] = [];
  const stderr: Buffer[] = [];
  let bytes = 0;
  let failure: Error | undefined;
  const kill = (reason: string) => {
    failure ??= new Error(reason);
    if (child.pid) {
      try { process.kill(-child.pid, 'SIGKILL'); }
      catch (error) { if ((error as NodeJS.ErrnoException).code !== 'ESRCH') child.kill('SIGKILL'); }
    }
  };
  const cancel = () => kill('Check cancelled');
  const timeout = setTimeout(() => kill(`Check timed out after ${check.timeoutMs}ms`), check.timeoutMs);
  signal.addEventListener('abort', cancel, { once: true });
  if (signal.aborted) cancel();
  for (const [stream, chunks] of [[child.stdout, stdout], [child.stderr, stderr]] as const) {
    stream.on('data', (chunk: Buffer) => {
      bytes += chunk.length;
      if (bytes > MAX_OUTPUT_BYTES) kill('Check output exceeded 1MiB; no successful evidence recorded');
      else chunks.push(chunk);
    });
  }
  child.once('error', error => { failure = error; });
  // 2. 終了を観測してから結果を返す。超過や中断を成功に変換しない。
  child.once('close', (code, terminationSignal) => {
    clearTimeout(timeout);
    signal.removeEventListener('abort', cancel);
    if (failure) reject(failure);
    else resolve({ stdout: Buffer.concat(stdout).toString('utf8'), stderr: Buffer.concat(stderr).toString('utf8'), code: code ?? -1, killed: terminationSignal !== null });
  });
  return promise;
}
