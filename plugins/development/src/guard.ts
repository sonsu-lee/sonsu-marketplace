import { lstatSync, readFileSync, realpathSync } from 'node:fs';
import { homedir } from 'node:os';
import { dirname, isAbsolute, relative, resolve, sep } from 'node:path';
import { fileURLToPath } from 'node:url';

const policyPath = fileURLToPath(new URL('../hooks/policy.json', import.meta.url));
const policy = JSON.parse(readFileSync(policyPath, 'utf8')) as {
  shellPatterns: string[];
  remoteMutationPattern: string;
};
const shellPatterns = policy.shellPatterns.map(pattern => new RegExp(pattern, 'i'));
const remoteMutation = new RegExp(policy.remoteMutationPattern, 'i');

function canonical(path: string): string {
  let parent = resolve(path);
  const missing: string[] = [];
  while (true) {
    try {
      lstatSync(parent);
      break;
    } catch (error) {
      if ((error as NodeJS.ErrnoException).code !== 'ENOENT') throw error;
      const next = dirname(parent);
      if (next === parent) throw error;
      missing.unshift(parent.slice(next.length + (next === sep ? 0 : 1)));
      parent = next;
    }
  }
  return resolve(realpathSync(parent), ...missing);
}

function outside(root: string, file: string): boolean {
  const expanded = file === '~' ? homedir() : file.startsWith('~/') ? resolve(homedir(), file.slice(2)) : file;
  const target = canonical(isAbsolute(expanded) ? expanded : resolve(root, expanded));
  const path = relative(canonical(root), target);
  return path === '..' || path.startsWith(`..${sep}`) || isAbsolute(path);
}

function unwrapHeader(path: string): string {
  const trimmed = path.trimEnd();
  if (!trimmed.startsWith('[') || !trimmed.endsWith(']')) return path;
  const inner = trimmed.slice(1, -1);
  const tag = /#[0-9a-f]{4}$/i.exec(inner);
  const target = tag ? inner.slice(0, tag.index) : inner;
  return target && (tag || !target.includes('#')) ? target : path;
}

function unquotePath(path: string): string {
  if (path.startsWith('"')) {
    try {
      const decoded: unknown = JSON.parse(path);
      if (typeof decoded === 'string') return decoded;
    } catch {}
  }
  return path.replace(/^['"]|['"]$/g, '');
}

export function needsEvidenceGate(name: string, input: Record<string, unknown>, cwd: string): boolean {
  if (remoteMutation.test(name)) return true;
  const lower = name.toLowerCase();
  if (lower === 'bash' && typeof input.command === 'string' && shellPatterns.some(pattern => pattern.test(input.command as string))) {
    return true;
  }
  if (lower !== 'write' && lower !== 'edit') return false;
  const paths: string[] = [];
  if (typeof input.path === 'string') paths.push(unwrapHeader(input.path));
  if (lower === 'edit') {
    if (Array.isArray(input.paths)) {
      for (const path of input.paths) if (typeof path === 'string') paths.push(unwrapHeader(path));
    }
    if (Array.isArray(input.edits)) {
      for (const edit of input.edits) {
        if (edit && typeof edit === 'object' && typeof edit.rename === 'string') paths.push(unwrapHeader(edit.rename));
      }
    }
    if (typeof input.input === 'string') {
      for (const match of input.input.matchAll(/^\[(.+)#[0-9A-Fa-f]{4}\][^\S\n]*$/gm)) paths.push(unquotePath(match[1]));
      if (!/^\*\*\* (?:Add|Update|Delete|Edit) File: /m.test(input.input)) {
        for (const match of input.input.matchAll(/^[ \t]*MV[ \t]+(.+?)[ \t]*$/gm)) paths.push(unquotePath(match[1]));
      }
      for (const match of input.input.matchAll(/^\*\*\* (?:(?:Add|Update|Delete|Edit) File|Move to): (.+?)(?: all)?[ \t]*$/gm)) paths.push(unquotePath(match[1]));
    }
  }
  for (const path of paths) {
    if (remoteMutation.test(path) || /^(ssh|cfg|issue|pr):\/\//i.test(path)) return true;
    if (!path.includes('://') && outside(cwd, path)) return true;
  }
  return false;
}
