// Internal adapter for the pinned @google/design.md linter; no YAML/schema fork.
import { readFileSync } from 'node:fs';
import { join, resolve } from 'node:path';
import { pathToFileURL } from 'node:url';
import { createRequire } from 'node:module';

const expectedVersion = process.argv[2];
const formatRules = new Set(['section-order', 'unknown-key', 'token-like-ignored']);
const reference = /^\{([a-zA-Z0-9._-]+)\}$/;

function resolveToken(symbols, path, visited = new Set()) {
  if (!symbols.has(path) || visited.has(path)) return undefined;
  return resolveValue(symbols, symbols.get(path), new Set([...visited, path]));
}

function resolveValue(symbols, value, visited) {
  const target = typeof value === 'string' && reference.exec(value);
  if (target) return resolveToken(symbols, target[1], visited);
  if (value === null || typeof value !== 'object') return value;
  if (visited.has(value)) return undefined;
  const descendants = new Set([...visited, value]);
  const resolved = Array.isArray(value) ? [] : {};
  for (const [key, item] of Object.entries(value)) {
    resolved[key] = resolveValue(symbols, item, descendants);
    if (resolved[key] === undefined) return undefined;
  }
  return resolved;
}

function hasValue(value, visited = new Set()) {
  if (typeof value === 'string') return Boolean(value.trim());
  if (typeof value === 'number') return Number.isFinite(value);
  if (value === null || typeof value !== 'object' || visited.has(value)) return false;
  const descendants = new Set([...visited, value]);
  // Resolved typography may contain only its type tag for an empty YAML map.
  return Object.entries(value).some(([key, item]) => key !== 'type' && hasValue(item, descendants));
}

async function loadLinter() {
  // Python supplies only the package freshly installed in its isolated project.
  const root = process.argv[3];
  const pkg = JSON.parse(readFileSync(join(root, 'package.json'), 'utf8'));
  if (pkg.name !== '@google/design.md' || pkg.version !== expectedVersion) {
    throw new Error(`Expected @google/design.md@${expectedVersion}, got ${pkg.name}@${pkg.version}`);
  }
  const entry = pkg.exports['./linter'].import;
  const require = createRequire(join(root, 'package.json'));
  const dependency = name => import(pathToFileURL(require.resolve(name)).href);
  const [{ lint }, { parse: parseYaml }, { unified }, { default: remarkParse },
    { default: remarkFrontmatter }] = await Promise.all([
    import(pathToFileURL(resolve(root, entry)).href), dependency('yaml'),
    dependency('unified'), dependency('remark-parse'), dependency('remark-frontmatter'),
  ]);
  // Use the same parser dependencies and YAML nodes as upstream. Its public
  // model drops typography dimension references, so retain raw token leaves
  // solely for reference validation; schema and lint rules stay upstream.
  const parseMarkdown = unified().use(remarkParse).use(remarkFrontmatter, ['yaml']);
  return { lint, readRawTokens: content => readRawTokens(content, parseMarkdown, parseYaml) };
}

function readRawTokens(content, parseMarkdown, parseYaml) {
  const tokens = new Map();
  const cyclicPaths = [];
  const groups = new Set(['colors', 'typography', 'rounded', 'spacing', 'components']);
  function add(value, path, visited = new Set()) {
    tokens.set(path, value);
    if (value === null || typeof value !== 'object') return;
    if (visited.has(value)) {
      cyclicPaths.push(path);
      return;
    }
    const descendants = new Set([...visited, value]);
    for (const [key, item] of Object.entries(value)) add(item, `${path}.${key}`, descendants);
  }
  function visit(node) {
    if (node.type === 'yaml' || (node.type === 'code' && ['yaml', 'yml'].includes(node.lang))) {
      const block = parseYaml(node.value);
      if (block && typeof block === 'object') {
        for (const [group, values] of Object.entries(block)) {
          if (groups.has(group)) add(values, group);
        }
      }
    }
    for (const child of node.children ?? []) visit(child);
  }
  visit(parseMarkdown.parse(content));
  return { tokens, cyclicPaths };
}

function validate(content, { lint, readRawTokens }) {
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
  let rawTokens;
  let cyclicPaths;
  try {
    // Check mandatory values in frontmatter itself; fenced examples in the body
    // must not supply a missing name or a missing design system.
    frontmatter = lint(lines.slice(0, end + 1).join('\n') + '\n');
    report = lint(content);
    ({ tokens: rawTokens, cyclicPaths } = readRawTokens(content));
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
      [...component.properties.values()].some(value => hasValue(value))).length;
  if (tokenCount === 0) {
    fail('tokens', 'Frontmatter must define at least one recognized design token.');
  }
  // Keep upstream's symbol names while restoring composite reference leaves
  // that 0.4.0 drops from its model. Metadata and unknown groups are excluded.
  const symbols = new Map([...report.designSystem.symbolTable].map(([path, value]) =>
    [path, rawTokens.has(path) ? rawTokens.get(path) : value]));
  for (const path of cyclicPaths) {
    fail('broken-ref', `Circular YAML alias at ${path}.`);
  }
  for (const [path, value] of rawTokens) {
    if (typeof value === 'string' && reference.test(value)
        && resolveToken(symbols, reference.exec(value)[1]) === undefined) {
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
