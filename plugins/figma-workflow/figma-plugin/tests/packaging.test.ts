import assert from 'node:assert/strict';
import { access, readFile } from 'node:fs/promises';
import { dirname, resolve } from 'node:path';
import test from 'node:test';
import { fileURLToPath } from 'node:url';

const packageDirectory = resolve(dirname(fileURLToPath(import.meta.url)), '..');

test('development-plugin manifest points to checked-in companion bundles', async () => {
  const manifestPath = resolve(packageDirectory, 'manifest.json');
  const manifest = JSON.parse(await readFile(manifestPath, 'utf8')) as Record<string, unknown>;

  assert.equal(manifest.name, 'Figma Workflow Companion');
  assert.equal(manifest.api, '1.0.0');
  assert.deepEqual(manifest.editorType, ['figma']);
  assert.equal(manifest.documentAccess, 'dynamic-page');
  assert.deepEqual(manifest.networkAccess, { allowedDomains: ['none'] });
  assert.equal(typeof manifest.main, 'string');
  assert.equal(typeof manifest.ui, 'string');

  await access(resolve(packageDirectory, manifest.main as string));
  await access(resolve(packageDirectory, manifest.ui as string));
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
