import { expect, test } from 'bun:test';
import { runCheck } from '../src/check.ts';
import type { CheckSpec } from '../src/engine.ts';

function check(script: string, timeoutMs = 2000): CheckSpec {
  return { id: 'check', command: process.execPath, args: ['-e', script], timeoutMs };
}

test('executes literal argv without a shell and preserves failed exit status', async () => {
  const spec = check('process.stdout.write(JSON.stringify(process.argv.slice(1)))');
  spec.args.push('literal; echo should-not-run');
  const passed = await runCheck(spec, process.cwd(), new AbortController().signal);
  expect(passed).toEqual({ stdout: '["literal; echo should-not-run"]', stderr: '', code: 0, killed: false });
  const failed = await runCheck(check('process.stderr.write("failed assertion"); process.exit(3)'), process.cwd(), new AbortController().signal);
  expect(failed.code).toBe(3);
  expect(failed.stderr).toBe('failed assertion');
});

test('rejects excessive output instead of saving a successful receipt', async () => {
  await expect(runCheck(check('process.stdout.write("x".repeat(2 * 1024 * 1024))'), process.cwd(), new AbortController().signal)).rejects.toThrow('exceeded 1MiB');
});

test('timeout and operator cancellation cannot become successful evidence', async () => {
  await expect(runCheck(check('setInterval(() => {}, 1000)', 100), process.cwd(), new AbortController().signal)).rejects.toThrow('timed out');
  const controller = new AbortController();
  // 子プロセスと POSIX kill の実際の期限処理を検証するため、ここだけ実時計を使う。
  const pending = runCheck(check('setInterval(() => {}, 1000)'), process.cwd(), controller.signal);
  controller.abort();
  await expect(pending).rejects.toThrow('cancelled');
});
