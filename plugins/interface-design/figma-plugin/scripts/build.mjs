import { build } from 'esbuild';
import { cp, mkdir } from 'node:fs/promises';
import { dirname, resolve } from 'node:path';
import { fileURLToPath } from 'node:url';

const packageDirectory = resolve(dirname(fileURLToPath(import.meta.url)), '..');
const sourceDirectory = resolve(packageDirectory, 'src');
const distributionDirectory = resolve(packageDirectory, 'dist');

await mkdir(distributionDirectory, { recursive: true });
await build({
  bundle: true,
  entryPoints: [resolve(sourceDirectory, 'code.ts')],
  format: 'iife',
  outfile: resolve(distributionDirectory, 'code.js'),
  platform: 'browser',
  target: 'es2020',
});
await cp(resolve(sourceDirectory, 'ui.html'), resolve(distributionDirectory, 'ui.html'));
