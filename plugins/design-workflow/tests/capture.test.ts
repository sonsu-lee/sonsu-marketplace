import { afterEach, describe, expect, test } from 'bun:test';
import { createServer } from 'node:http';
import type { RequestListener, Server } from 'node:http';
import { mkdtemp, mkdir, readFile, readdir, rm, symlink, writeFile } from 'node:fs/promises';
import { tmpdir } from 'node:os';
import { join } from 'node:path';
import { captureEvidence } from '../src/capture.ts';
import type { CaptureSpec } from '../src/engine.ts';

const executablePath = process.env.DESIGN_WORKFLOW_CHROME;
const roots: string[] = [];
const servers: Server[] = [];

afterEach(async () => {
  await Promise.all(servers.splice(0).map(server => {
    const { promise, resolve, reject } = Promise.withResolvers<void>();
    server.close(error => error ? reject(error) : resolve());
    return promise;
  }));
  await Promise.all(roots.splice(0).map(root => rm(root, { recursive: true, force: true })));
});

async function fixture(html: string) {
  const root = await mkdtemp(join(tmpdir(), 'design-capture-test-'));
  roots.push(root);
  const workspaceRoot = join(root, 'workspace');
  const artifactRoot = join(root, 'artifacts');
  await mkdir(workspaceRoot);
  await mkdir(artifactRoot);
  await writeFile(join(workspaceRoot, 'page.html'), html);
  return { root, workspaceRoot, artifactRoot, executablePath, approvedPaths: ['page.html'] };
}

function fileSpec(steps: CaptureSpec['steps'] = []): CaptureSpec {
  return { id: 'screen', kind: 'file', target: 'page.html', width: 600, height: 400, steps };
}

async function server(handler: RequestListener) {
  const instance = createServer(handler);
  servers.push(instance);
  const { promise, resolve, reject } = Promise.withResolvers<void>();
  instance.once('error', reject);
  instance.listen(0, '127.0.0.1', resolve);
  await promise;
  const address = instance.address();
  if (!address || typeof address === 'string') throw new Error('No fixture port');
  return `http://127.0.0.1:${address.port}`;
}

describe('capture input and dependency failures', () => {
  test('rejects public targets and inaccessible executables', async () => {
    const options = await fixture('<h1>Hi</h1>');
    await expect(captureEvidence({ ...options, spec: { ...fileSpec(), kind: 'web', target: 'https://example.com' } })).rejects.toThrow('loopback');
    await expect(captureEvidence({ ...options, executablePath: join(options.root, 'absent'), spec: fileSpec() })).rejects.toThrow('Browser dependency unavailable');
    expect(await readdir(options.artifactRoot)).toEqual([]);
  });
});

describe.skipIf(!executablePath)('isolated Chromium capture (DESIGN_WORKFLOW_CHROME required)', () => {
  test('captures actual HTML, local assets and successful steps into PNG and receipt', async () => {
    const options = await fixture('<title>Fixture</title><link rel="stylesheet" href="style.css"><input id="name"><button onclick="document.querySelector(\'h1\').textContent=document.querySelector(\'input\').value">Set</button><h1>Before</h1>');
    await writeFile(join(options.workspaceRoot, 'style.css'), 'body { background: #fff; }');
    options.approvedPaths.push('style.css');
    const result = await captureEvidence({ ...options, spec: fileSpec([
      { action: 'fill', selector: '#name', value: 'After' },
      { action: 'click', selector: 'button' },
      { action: 'assert-visible', selector: 'h1' },
      { action: 'assert-text', selector: 'h1', text: 'After' },
    ]) });
    const png = await readFile(result.artifacts[0]);
    expect([...png.subarray(0, 8)]).toEqual([137, 80, 78, 71, 13, 10, 26, 10]);
    const receipt = JSON.parse(await readFile(result.artifacts[1], 'utf8'));
    expect(receipt.title).toBe('Fixture');
    expect(png.readUInt32BE(16)).toBe(600);
    expect(png.readUInt32BE(20)).toBe(400);
  });

  test('captures approved logical paths through an internal symlinked directory', async () => {
    const options = await fixture('');
    await mkdir(join(options.workspaceRoot, 'actual'));
    await writeFile(join(options.workspaceRoot, 'actual/page.html'), '<title>Alias fixture</title><link rel="stylesheet" href="style.css"><h1>Aliased page</h1>');
    await writeFile(join(options.workspaceRoot, 'actual/style.css'), 'h1 { color: red }');
    await symlink('actual', join(options.workspaceRoot, 'alias'));
    options.approvedPaths = ['alias/page.html', 'alias/style.css'];
    const result = await captureEvidence({ ...options, spec: { ...fileSpec([{ action: 'assert-text', selector: 'h1', text: 'Aliased page' }]), target: 'alias/page.html' } });
    expect(JSON.parse(await readFile(result.artifacts[1], 'utf8')).title).toBe('Alias fixture');
    expect((await readFile(result.artifacts[0])).readUInt32BE(16)).toBe(600);
  });

  test('captures SVG and rejects failed assertions without receipts', async () => {
    const options = await fixture('<h1>actual</h1>');
    await expect(captureEvidence({ ...options, spec: fileSpec([{ action: 'assert-text', selector: 'h1', text: 'missing' }]) })).rejects.toThrow('Text assertion failed');
    expect(await readdir(options.artifactRoot)).toEqual([]);
    await writeFile(join(options.workspaceRoot, 'icon.svg'), '<svg xmlns="http://www.w3.org/2000/svg" width="60" height="60"><circle cx="30" cy="30" r="20"/></svg>');
    options.approvedPaths.push('icon.svg');
    const result = await captureEvidence({ ...options, spec: { ...fileSpec(), target: 'icon.svg' } });
    expect((await readFile(result.artifacts[0])).subarray(0, 4).toString('hex')).toBe('89504e47');
  });

  test('rejects missing, broken, outside and remote assets', async () => {
    const options = await fixture('<img src="missing.png">');
    await expect(captureEvidence({ ...options, spec: fileSpec() })).rejects.toThrow();
    await writeFile(join(options.workspaceRoot, 'bad.png'), 'not an image');
    options.approvedPaths.push('bad.png');
    await writeFile(join(options.workspaceRoot, 'page.html'), '<img src="bad.png">');
    await expect(captureEvidence({ ...options, spec: fileSpec() })).rejects.toThrow();
    await writeFile(join(options.root, 'secret.css'), 'body { color: red }');
    await symlink(join(options.root, 'secret.css'), join(options.workspaceRoot, 'outside.css'));
    options.approvedPaths.push('outside.css');
    await writeFile(join(options.workspaceRoot, 'page.html'), '<link rel="stylesheet" href="outside.css">');
    await expect(captureEvidence({ ...options, spec: fileSpec() })).rejects.toThrow();
    await writeFile(join(options.workspaceRoot, 'page.html'), '<img src="https://example.com/image.png">');
    await expect(captureEvidence({ ...options, spec: fileSpec() })).rejects.toThrow();
    expect(await readdir(options.artifactRoot)).toEqual([]);
  });

  test('rejects unapproved workspace assets rather than recording untracked source evidence', async () => {
    const options = await fixture('<link rel="stylesheet" href="private.css">');
    await writeFile(join(options.workspaceRoot, 'private.css'), 'body { color: red }');
    await expect(captureEvidence({ ...options, spec: fileSpec() })).rejects.toThrow('approved source scope');
    expect(await readdir(options.artifactRoot)).toEqual([]);
  });

  test('captures only the declared loopback origin and blocks cross-origin requests and mutation methods', async () => {
    let mode = 'ok';
    let posts = 0;
    const origin = await server((request, response) => {
      if (request.method === 'POST') posts++;
      response.setHeader('content-type', 'text/html');
      response.end(mode === 'ok' ? '<title>Local</title><h1>Local</h1>' : mode === 'cross'
        ? '<img src="http://localhost:1/no.png">'
        : '<script>fetch("/write", {method:"POST"}).catch(() => {})</script>');
    });
    const options = await fixture('');
    const spec: CaptureSpec = { ...fileSpec(), kind: 'web', target: `${origin}/` };
    const result = await captureEvidence({ ...options, spec });
    expect(JSON.parse(await readFile(result.artifacts[1], 'utf8')).title).toBe('Local');
    mode = 'cross';
    await expect(captureEvidence({ ...options, spec })).rejects.toThrow();
    mode = 'post';
    await expect(captureEvidence({ ...options, spec })).rejects.toThrow();
    expect(posts).toBe(0);
  });

  test('blocks redirect destinations before an unapproved origin receives a request', async () => {
    let foreignRequests = 0;
    let redirects = 0;
    const foreign = await server((_request, response) => {
      foreignRequests++;
      response.writeHead(200, { 'content-type': 'image/svg+xml' });
      response.end('<svg xmlns="http://www.w3.org/2000/svg" width="20" height="20"><rect width="20" height="20"/></svg>');
    });
    const origin = await server((request, response) => {
      if (request.url === '/asset') {
        redirects++; response.writeHead(302, { location: `${foreign}/image.svg` }); response.end();
      } else {
        response.writeHead(200, { 'content-type': 'text/html' }); response.end('<img src="/asset">');
      }
    });
    const options = await fixture('');
    await expect(captureEvidence({ ...options, spec: { ...fileSpec(), kind: 'web', target: `${origin}/` } })).rejects.toThrow();
    expect(redirects).toBe(1);
    expect(foreignRequests).toBe(0);
    expect(await readdir(options.artifactRoot)).toEqual([]);
  });

  test('aborts in-flight capture and leaves no partial artifacts', async () => {
    const controller = new AbortController();
    const origin = await server((_request, response) => {
      controller.abort();
      response.end();
    });
    const options = await fixture('');
    const pending = captureEvidence({ ...options, spec: { ...fileSpec(), kind: 'web', target: `${origin}/` }, signal: controller.signal });
    await expect(pending).rejects.toThrow('Capture aborted');
    expect(await readdir(options.artifactRoot)).toEqual([]);
  });
});
