// Internal adapter for the pinned @google/design.md linter; no YAML/schema fork.
import { readFileSync, realpathSync } from 'node:fs';
import { delimiter, dirname, join, resolve } from 'node:path';
import { pathToFileURL } from 'node:url';

const expectedVersion = process.argv[2];
const formatRules = new Set(['section-order', 'unknown-key', 'token-like-ignored']);
const reference = /^\{([a-zA-Z0-9._-]+)\}$/;

function resolveToken(symbols, path) {
  const visited = new Set();
  while (symbols.has(path) && !visited.has(path)) {
    visited.add(path);
    const value = symbols.get(path);
    const target = typeof value === 'string' && reference.exec(value);
    if (!target) return value;
    path = target[1];
  }
  return undefined;
}

function hasValue(value) {
  if (typeof value === 'string') return Boolean(value.trim());
  if (typeof value === 'number') return Number.isFinite(value);
  // Resolved typography may contain only its type tag for an empty YAML map.
  return value !== null && typeof value === 'object' && typeof value.type === 'string'
    && Object.entries(value).some(([key, item]) => key !== 'type' && hasValue(item));
}

async function loadLinter() {
  // npm exec exposes the selected package's bin directory through PATH, but does
  // not add its modules to this adapter's import search path.
  for (const directory of (process.env.PATH ?? '').split(delimiter).filter(Boolean)) {
    let binary;
    try {
      binary = realpathSync(join(directory, 'designmd'));
    } catch {
      continue;
    }
    const root = resolve(dirname(binary), '..');
    const pkg = JSON.parse(readFileSync(join(root, 'package.json'), 'utf8'));
    if (pkg.name !== '@google/design.md' || pkg.version !== expectedVersion) {
      throw new Error(`Expected @google/design.md@${expectedVersion}, got ${pkg.name}@${pkg.version}`);
    }
    const entry = pkg.exports['./linter'].import;
    return (await import(pathToFileURL(resolve(root, entry)).href)).lint;
  }
  throw new Error('npm exec did not expose the pinned designmd binary');
}

function validate(content, lint) {
  const findings = [];
  const fail = (rule, message) => findings.push({ severity: 'error', rule, message });
  const lines = content.replace(/^\uFEFF/, '').split(/\r?\n/);
  const end = lines.indexOf('---', 1);
  if (lines[0] !== '---' || end < 1) {
    fail('frontmatter', 'DESIGN.md must start with a closed --- YAML frontmatter block.');
    return { status: 'failed', findings };
  }

  let report;
  let frontmatter;
  try {
    // Check mandatory values in frontmatter itself; fenced examples in the body
    // must not supply a missing name or a missing design system.
    frontmatter = lint(lines.slice(0, end + 1).join('\n') + '\n');
    report = lint(content);
  } catch (error) {
    fail('parse', String(error.message ?? error));
    return { status: 'failed', findings };
  }
  const system = frontmatter.designSystem;
  if (typeof system.name !== 'string' || !system.name.trim()) {
    fail('name', 'Frontmatter must define a non-empty string name.');
  }
  // The official model keeps numeric spacing in symbolTable, outside spacing.
  const tokenCount = [...system.symbolTable.keys()]
    .filter(path => hasValue(resolveToken(system.symbolTable, path))).length
    + [...system.components.values()].filter(component =>
      [...component.properties.values()].some(hasValue)).length;
  if (tokenCount === 0) {
    fail('tokens', 'Frontmatter must define at least one recognized design token.');
  }
  // In 0.4.0 the upstream broken-ref rule only checks component references.
  // Its model also leaves unresolved primitive references in symbolTable.
  for (const [path, value] of report.designSystem.symbolTable) {
    if (typeof value === 'string' && reference.test(value)
        && resolveToken(report.designSystem.symbolTable, path) === undefined) {
      fail('broken-ref', `Unresolved or circular token reference at ${path}: ${value}`);
    }
  }
  for (const finding of report.findings) {
    findings.push({ ...finding, rule: finding.rule ?? 'parse' });
  }
  const failed = findings.some(finding => finding.severity === 'error'
    || formatRules.has(finding.rule)
    || (finding.rule === 'parse' && finding.severity === 'warning'));
  return {
    status: failed ? 'failed' : findings.some(finding => finding.severity === 'warning')
      ? 'needs_review' : 'passed',
    findings,
    upstream_summary: report.summary,
    token_count: tokenCount,
  };
}

try {
  const lint = await loadLinter();
  const result = validate(readFileSync(0, 'utf8'), lint);
  process.stdout.write(JSON.stringify(result) + '\n');
  process.exitCode = { passed: 0, failed: 1, needs_review: 3 }[result.status];
} catch (error) {
  process.stdout.write(JSON.stringify({
    status: 'blocked',
    findings: [{ severity: 'error', rule: 'runtime', message: String(error.message ?? error) }],
  }) + '\n');
  process.exitCode = 2;
}
