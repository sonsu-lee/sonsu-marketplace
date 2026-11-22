import { afterEach, describe, expect, test } from 'bun:test';
import { mkdtemp, mkdir, readFile, realpath, rm, symlink, writeFile } from 'node:fs/promises';
import os from 'node:os';
import path from 'node:path';
import { DesignRunEngine, type DesignPlan } from '../src/engine';

const temporary: string[] = [];
afterEach(async () => {
  await Promise.all(temporary.splice(0).map(dir => rm(dir, { recursive: true, force: true })));
});

async function fixture(mode: DesignPlan['mode'] = 'design') {
  const root = await mkdtemp(path.join(os.tmpdir(), 'design-engine-'));
  temporary.push(root);
  const workspace = path.join(root, 'workspace');
  const artifacts = path.join(root, 'artifacts');
  await mkdir(workspace);
  await mkdir(artifacts);
  await writeFile(path.join(workspace, 'index.html'), '<h1>Hello</h1>');
  const plan: DesignPlan = {
    mode,
    paths: ['index.html', 'new/deep/style.css'],
    goal: 'Improve the interface',
    brief: 'Make the home page clearer.',
    facts: [{ subject: 'Home page', approval: 'not-supplied', availability: 'inspectable' }],
    captures: mode === 'advisory' ? [] : [{ id: 'home', kind: 'file', target: 'index.html', width: 1024, height: 768 }],
    checks: mode === 'review' || mode === 'advisory' ? [] : [{ id: 'check', command: 'echo', args: ['ok'], timeoutMs: 1000 }],
  };
  const engine = new DesignRunEngine(workspace, artifacts);
  return { workspace, artifacts, plan, engine };
}

interface EvidenceFiles {
  screenshot: string;
  captureReceipt: string;
  checkReceipt: string;
}

async function evidenceFiles(dir: string): Promise<EvidenceFiles> {
  const screenshot = path.join(dir, 'screen.png');
  const captureReceipt = path.join(dir, 'capture.json');
  const checkReceipt = path.join(dir, 'check.json');
  await writeFile(screenshot, 'png bytes');
  await writeFile(captureReceipt, '{"capture":true}');
  await writeFile(checkReceipt, '{"check":true}');
  return { screenshot, captureReceipt, checkReceipt };
}

async function capture(engine: DesignRunEngine, revision: string, files: EvidenceFiles) {
  return engine.recordEvidence({ kind: 'capture', id: 'home', revision, artifacts: [files.screenshot, files.captureReceipt], details: { viewport: '1024x768' } });
}
async function check(engine: DesignRunEngine, revision: string, files: EvidenceFiles) {
  return engine.recordEvidence({ kind: 'check', id: 'check', revision, artifacts: [files.checkReceipt], details: { exitCode: 0 } });
}
async function report(engine: DesignRunEngine, body = '# Report\n\nChecked body.') {
  const { inputSha256 } = await engine.reportInput();
  return engine.recordReport(inputSha256, body);
}
async function complete(engine: DesignRunEngine) {
  const state = await report(engine);
  return engine.acceptAndFinish(state.report!.sha256);
}

describe('DesignRunEngine', () => {
  test('requires every declared receipt, a checked report and acceptance of that exact report', async () => {
    const { engine, plan, artifacts } = await fixture();
    const state = await engine.start(plan);
    const files = await evidenceFiles(artifacts);
    expect(state.missing).toEqual(['capture:home', 'check:check', 'report', 'review']);
    await expect(engine.reportInput()).rejects.toThrow('missing or stale');
    await capture(engine, state.revision, files);
    await check(engine, state.revision, files);
    expect((await engine.status()).missing).toEqual(['report', 'review']);
    const reported = await report(engine);
    expect(reported.missing).toEqual(['review']);
    await expect(engine.acceptAndFinish('0'.repeat(64))).rejects.toThrow('Report changed');
    const completed = await engine.acceptAndFinish(reported.report!.sha256);
    expect(completed.phase).toBe('completed');
    expect(completed.missing).toEqual([]);
    expect(engine.isActive()).toBe(false);
    await expect(engine.write('index.html', 'no')).rejects.toThrow();
  });

  test('a report generated for an earlier input cannot be recorded or accepted', async () => {
    const { engine, plan, artifacts, workspace } = await fixture();
    const initial = await engine.start(plan);
    const files = await evidenceFiles(artifacts);
    await capture(engine, initial.revision, files);
    await check(engine, initial.revision, files);
    const { inputSha256 } = await engine.reportInput();
    // 報告生成中に検査が別の結果で再記録された場合を再現する。
    await writeFile(files.checkReceipt, '{"check":"rerun"}');
    await check(engine, initial.revision, files);
    await expect(engine.recordReport(inputSha256, 'Stale body')).rejects.toThrow('stale');
    const reported = await report(engine);
    await writeFile(path.join(workspace, 'index.html'), '<h1>Changed after the report</h1>');
    const changed = await engine.status();
    expect(changed.report).toBeUndefined();
    expect(changed.missing).toEqual(['capture:home', 'check:check', 'report', 'review']);
    await expect(engine.acceptAndFinish(reported.report!.sha256)).rejects.toThrow();
  });

  test('protects approved definitions and returned state from mutation', async () => {
    const { engine, plan } = await fixture();
    const initial = await engine.start(plan);
    plan.paths.push('other.txt');
    plan.captures[0].width = 5;
    plan.facts[0].approval = 'approved';
    initial.plan.paths.push('other.txt');
    const spec = engine.captureSpec('home');
    spec.width = 9;
    expect(engine.captureSpec('home').width).toBe(1024);
    expect(engine.exportState().plan.paths).toEqual(['index.html', 'new/deep/style.css']);
    expect(engine.exportState().plan.facts[0].approval).toBe('not-supplied');
    await expect(engine.read('other.txt')).rejects.toThrow();
    expect(engine.checkSpec('check').args).toEqual(['ok']);
    expect(() => engine.captureSpec('unknown')).toThrow();
  });

  test('tracks missing paths, creates new nested files atomically and invalidates prior receipts and reports', async () => {
    const { engine, plan, workspace, artifacts } = await fixture();
    const initial = await engine.start(plan);
    const files = await evidenceFiles(artifacts);
    await capture(engine, initial.revision, files);
    await check(engine, initial.revision, files);
    await report(engine);
    await expect(engine.read('new/deep/style.css')).rejects.toThrow();
    const updated = await engine.write('new/deep/style.css', 'body { color: red; }');
    expect(updated.revision).not.toBe(initial.revision);
    expect(updated.evidence).toEqual([]);
    expect(updated.report).toBeUndefined();
    expect(updated.missing).toEqual(['capture:home', 'check:check', 'report', 'review']);
    expect(await readFile(path.join(workspace, 'new/deep/style.css'), 'utf8')).toBe('body { color: red; }');
    expect(await engine.read('new/deep/style.css')).toBe('body { color: red; }');
    await expect(capture(engine, initial.revision, files)).rejects.toThrow();
  });

  test('detects creation of a previously missing approved file', async () => {
    const { engine, plan, workspace, artifacts } = await fixture();
    const initial = await engine.start(plan);
    const files = await evidenceFiles(artifacts);
    await capture(engine, initial.revision, files);
    await mkdir(path.join(workspace, 'new/deep'), { recursive: true });
    await writeFile(path.join(workspace, 'new/deep/style.css'), 'externally created');
    const current = await engine.status();
    expect(current.revision).not.toBe(initial.revision);
    expect(current.evidence).toEqual([]);
    await expect(capture(engine, initial.revision, files)).rejects.toThrow();
  });

  test('external source changes invalidate evidence and reports even if content is later reverted', async () => {
    const { engine, plan, workspace, artifacts } = await fixture();
    const initial = await engine.start(plan);
    const files = await evidenceFiles(artifacts);
    await capture(engine, initial.revision, files);
    await check(engine, initial.revision, files);
    await report(engine);
    await writeFile(path.join(workspace, 'index.html'), '<h1>External edit</h1>');
    const changed = await engine.status();
    expect(changed.revision).not.toBe(initial.revision);
    expect(changed.evidence).toEqual([]);
    expect(changed.report).toBeUndefined();
    await writeFile(path.join(workspace, 'index.html'), '<h1>Hello</h1>');
    expect((await engine.status()).missing).toEqual(['capture:home', 'check:check', 'report', 'review']);
  });

  test('artifact or report tampering invalidates the report and its acceptance', async () => {
    const { engine, plan, artifacts } = await fixture();
    const initial = await engine.start(plan);
    const files = await evidenceFiles(artifacts);
    await capture(engine, initial.revision, files);
    await check(engine, initial.revision, files);
    await report(engine);
    await writeFile(files.screenshot, 'tampered');
    const changed = await engine.status();
    expect(changed.missing).toEqual(['capture:home', 'report', 'review']);
    expect(changed.report).toBeUndefined();
    await writeFile(files.screenshot, 'png bytes');
    await capture(engine, initial.revision, files);
    const again = await report(engine);
    await writeFile(again.report!.path, 'edited after review');
    expect((await engine.status()).missing).toEqual(['report', 'review']);
    await expect(engine.acceptAndFinish(again.report!.sha256)).rejects.toThrow();
  });

  test('restored completed state is revalidated against files, artifacts and the published report', async () => {
    const { engine, plan, workspace, artifacts } = await fixture();
    const initial = await engine.start(plan);
    const files = await evidenceFiles(artifacts);
    await capture(engine, initial.revision, files);
    await check(engine, initial.revision, files);
    const completed = await complete(engine);
    const restored = new DesignRunEngine(workspace, artifacts);
    await restored.restore(completed);
    expect((await restored.status()).phase).toBe('completed');
    expect(await restored.reportText()).toBe('# Report\n\nChecked body.');
    await writeFile(completed.report!.path, 'rewritten later');
    const tampered = new DesignRunEngine(workspace, artifacts);
    await tampered.restore(completed);
    expect(tampered.isActive()).toBe(true);
    expect((await tampered.status()).missing).toEqual(['report', 'review']);
    await writeFile(files.captureReceipt, 'changed');
    const stale = new DesignRunEngine(workspace, artifacts);
    await stale.restore(completed);
    expect((await stale.status()).missing).toEqual(['capture:home', 'report', 'review']);
  });

  test('advisory runs forbid captures, checks and writes and end as advised, never completed', async () => {
    const { engine, plan } = await fixture('advisory');
    await expect(engine.start({ ...plan, captures: [{ id: 'home', kind: 'file', target: 'index.html', width: 800, height: 600 }] })).rejects.toThrow('Advisory mode cannot declare captures');
    await expect(engine.start({ ...plan, checks: [{ id: 'run', command: 'echo', args: [], timeoutMs: 100 }] })).rejects.toThrow();
    const state = await engine.start(plan);
    expect(state.missing).toEqual(['report', 'review']);
    expect(await engine.read('index.html')).toBe('<h1>Hello</h1>');
    await expect(engine.write('index.html', 'changed')).rejects.toThrow('Advisory mode cannot write');
    const advised = await complete(engine);
    expect(advised.phase).toBe('advised');
    expect(engine.isActive()).toBe(false);
  });

  test('facts are validated and bound to the report input', async () => {
    const { engine, plan, workspace, artifacts } = await fixture('advisory');
    for (const facts of [
      [{ subject: 'Logo', approval: 'probably', availability: 'unknown' }],
      [{ subject: 'Logo', approval: 'approved', availability: 'somewhere' }],
      [{ subject: 'Logo | variant', approval: 'approved', availability: 'unknown' }],
      [{ subject: 'Logo', approval: 'approved', availability: 'unknown' }, { subject: 'Logo', approval: 'rejected', availability: 'unknown' }],
    ]) await expect(engine.start({ ...plan, facts } as DesignPlan)).rejects.toThrow();
    await engine.start({ ...plan, facts: [{ subject: 'Full-color identity', approval: 'approved', availability: 'exists-not-supplied' }] });
    const other = new DesignRunEngine(workspace, artifacts);
    await other.start({ ...plan, facts: [{ subject: 'Full-color identity', approval: 'not-supplied', availability: 'exists-not-supplied' }] });
    // 承認事実が異なる入力には同じ報告を流用できない。
    expect((await engine.reportInput()).inputSha256).not.toBe((await other.reportInput()).inputSha256);
  });

  test('rejects unsafe plans, directories, glob paths, and outside or symlink escapes', async () => {
    const { engine, plan, workspace, artifacts } = await fixture();
    for (const unsafe of ['../secret', '/tmp/file', 'a/*', 'https://host/x', 'a/../file']) {
      await expect(engine.start({ ...plan, paths: ['index.html', unsafe] })).rejects.toThrow();
    }
    await mkdir(path.join(workspace, 'directory'));
    await expect(engine.start({ ...plan, paths: ['index.html', 'directory'] })).rejects.toThrow();
    await symlink(artifacts, path.join(workspace, 'outside'));
    await expect(engine.start({ ...plan, paths: ['index.html', 'outside/new.txt'] })).rejects.toThrow();
    await engine.start(plan);
    await rm(path.join(workspace, 'index.html'));
    await symlink(path.join(artifacts, 'outside.html'), path.join(workspace, 'index.html'));
    await expect(engine.write('index.html', 'must not escape')).rejects.toThrow();
    await expect(engine.snapshot()).rejects.toThrow();
    expect((await engine.stop('unsafe scope', 'blocked')).phase).toBe('blocked');
  });

  test('allows a safe internal symlink but detects retargeting', async () => {
    const { engine, plan, workspace } = await fixture();
    await mkdir(path.join(workspace, 'actual'));
    await writeFile(path.join(workspace, 'actual', 'page.html'), 'inside');
    await symlink(path.join(workspace, 'actual', 'page.html'), path.join(workspace, 'link.html'));
    const scoped = { ...plan, paths: ['index.html', 'link.html'] };
    await engine.start(scoped);
    await engine.write('link.html', 'updated');
    expect(await readFile(path.join(workspace, 'actual', 'page.html'), 'utf8')).toBe('updated');
    const revision = await engine.snapshot();
    await writeFile(path.join(workspace, 'actual', 'other.html'), 'updated');
    await rm(path.join(workspace, 'link.html'));
    await symlink(path.join(workspace, 'actual', 'other.html'), path.join(workspace, 'link.html'));
    expect(await engine.snapshot()).not.toBe(revision);
  });

  test('rejects missing, escaped, forged or underspecified evidence', async () => {
    const { engine, plan, artifacts, workspace } = await fixture();
    const initial = await engine.start(plan);
    const files = await evidenceFiles(artifacts);
    await expect(engine.recordEvidence({ kind: 'capture', id: 'unknown', revision: initial.revision, artifacts: [files.screenshot, files.captureReceipt], details: {} })).rejects.toThrow();
    await expect(engine.recordEvidence({ kind: 'capture', id: 'home', revision: initial.revision, artifacts: [files.screenshot], details: {} })).rejects.toThrow();
    await expect(engine.recordEvidence({ kind: 'check', id: 'check', revision: initial.revision, artifacts: [path.join(workspace, 'index.html')], details: {} })).rejects.toThrow();
    await expect(engine.recordEvidence({ kind: 'check', id: 'check', revision: initial.revision, artifacts: [path.join(artifacts, 'missing')], details: {} })).rejects.toThrow();
    await symlink(path.join(workspace, 'index.html'), path.join(artifacts, 'linked'));
    await expect(engine.recordEvidence({ kind: 'check', id: 'check', revision: initial.revision, artifacts: [path.join(artifacts, 'linked')], details: {} })).rejects.toThrow();
  });

  test('review mode refuses writes, mutating browser actions and command checks', async () => {
    const { engine, plan } = await fixture('review');
    await expect(engine.start({ ...plan, checks: [{ id: 'run', command: 'echo', args: [], timeoutMs: 100 }] })).rejects.toThrow();
    await expect(engine.start({ ...plan, captures: [{ ...plan.captures[0], steps: [{ action: 'click', selector: 'button' }] }] })).rejects.toThrow();
    await engine.start({ ...plan, captures: [{ ...plan.captures[0], steps: [{ action: 'assert-visible', selector: 'h1' }, { action: 'assert-accessible', selector: 'main' }, { action: 'assert-no-overflow', selector: 'main' }] }] });
    await expect(engine.write('index.html', 'changed')).rejects.toThrow();
    expect((await engine.stop('Human stopped', 'stopped')).phase).toBe('stopped');
    expect(engine.isActive()).toBe(false);
    await expect(engine.reportInput()).rejects.toThrow();
  });

  test('validates web origins, plan bounds, roots and restored state', async () => {
    const { engine, plan, workspace, artifacts } = await fixture();
    const web = (target: string) => ({ ...plan, captures: [{ id: 'web', kind: 'web' as const, target, width: 800, height: 600 }] });
    for (const url of ['https://example.com/', 'http://localhost.example.com/', 'http://user:pass@localhost/', 'file:///tmp/x']) {
      await expect(engine.start(web(url))).rejects.toThrow();
    }
    await expect(engine.start({ ...plan, captures: [] })).rejects.toThrow();
    await expect(engine.start({ ...plan, extra: true } as DesignPlan)).rejects.toThrow();
    const state = await engine.start({ ...web('http://127.0.0.1:3000/path'), paths: [] });
    expect(state.workspaceRoot).toBe(await realpath(workspace));
    expect(state.artifactRoot).toBe(await realpath(artifacts));
    const other = new DesignRunEngine(workspace, workspace);
    await expect(other.start(plan)).rejects.toThrow();
    const newEngine = new DesignRunEngine(workspace, artifacts);
    await expect(newEngine.restore({ ...state, workspaceRoot: '/different' })).rejects.toThrow();
    await expect(newEngine.restore({ ...state, revision: 'forged' })).rejects.toThrow();
    await expect(newEngine.restore({ ...state, report: { path: '/tmp/elsewhere.md', sha256: '0'.repeat(64), inputSha256: '0'.repeat(64) } })).rejects.toThrow();
    expect((await engine.stop('Partial evidence', 'limited')).phase).toBe('limited');
  });
});
