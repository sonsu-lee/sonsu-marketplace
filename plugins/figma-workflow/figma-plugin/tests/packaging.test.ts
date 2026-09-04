import assert from 'node:assert/strict';
import { access, cp, mkdtemp, readFile, rm } from 'node:fs/promises';
import { execFile } from 'node:child_process';
import { dirname, resolve } from 'node:path';
import { promisify } from 'node:util';
import test from 'node:test';
import { fileURLToPath } from 'node:url';

const packageDirectory = resolve(dirname(fileURLToPath(import.meta.url)), '..');
const execFileAsync = promisify(execFile);

test('development-plugin manifest points to checked-in companion bundles', async () => {
  const manifestPath = resolve(packageDirectory, 'manifest.json');
  const manifest = JSON.parse(await readFile(manifestPath, 'utf8')) as Record<string, unknown>;

  assert.equal(manifest.name, 'Figma Workflow Companion');
  assert.equal(manifest.api, '1.0.0');
  assert.deepEqual(manifest.editorType, ['figma']);
  assert.equal(manifest.documentAccess, 'dynamic-page');
  assert.deepEqual(manifest.networkAccess, { allowedDomains: ['none'] });
  assert.equal(manifest.main, 'dist/code.js');
  assert.equal(manifest.ui, 'dist/ui.html');

  await access(resolve(packageDirectory, manifest.main as string));
  await access(resolve(packageDirectory, manifest.ui as string));
});

test('a temporary rebuild exactly matches checked-in dist artifacts', async () => {
  const temporaryDirectory = await mkdtemp(resolve(packageDirectory, '.tmp-build-'));
  try {
    await cp(resolve(packageDirectory, 'src'), resolve(temporaryDirectory, 'src'), { recursive: true });
    await cp(resolve(packageDirectory, 'scripts'), resolve(temporaryDirectory, 'scripts'), { recursive: true });
    await execFileAsync(process.execPath, ['scripts/build.mjs'], { cwd: temporaryDirectory });

    assert.deepEqual(
      await readFile(resolve(temporaryDirectory, 'dist/code.js')),
      await readFile(resolve(packageDirectory, 'dist/code.js')),
    );
    assert.deepEqual(
      await readFile(resolve(temporaryDirectory, 'dist/ui.html')),
      await readFile(resolve(temporaryDirectory, 'src/ui.html')),
    );
    assert.deepEqual(
      await readFile(resolve(packageDirectory, 'dist/ui.html')),
      await readFile(resolve(packageDirectory, 'src/ui.html')),
    );
  } finally {
    await rm(temporaryDirectory, { recursive: true, force: true });
  }
});

test('checked-in bundles expose the UI bridge without dynamic code execution', async () => {
  const code = await readFile(resolve(packageDirectory, 'dist/code.js'), 'utf8');
  const ui = await readFile(resolve(packageDirectory, 'dist/ui.html'), 'utf8');

  assert.match(code, /figma\.ui\.onmessage/);
  assert.match(code, /figma\.ui\.postMessage/);
  assert.match(ui, /data-action="preview"/);
  assert.match(ui, /data-action="apply"/);
  assert.doesNotMatch(`${code}\n${ui}`, /\b(?:eval|Function)\s*\(/);
});
