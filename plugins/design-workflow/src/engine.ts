import { createHash, randomBytes } from 'node:crypto';
import { constants } from 'node:fs';
import { lstat, mkdir, open, realpath, rename, unlink } from 'node:fs/promises';
import path from 'node:path';

export type BrowserStep =
  | { action: 'click'; selector: string }
  | { action: 'fill'; selector: string; value: string }
  | { action: 'press'; selector: string; key: string }
  | { action: 'assert-visible'; selector: string }
  | { action: 'assert-text'; selector: string; text: string };

export interface CaptureSpec {
  id: string;
  kind: 'file' | 'web';
  target: string;
  width: number;
  height: number;
  steps?: BrowserStep[];
}

export interface CheckSpec {
  id: string;
  command: string;
  args: string[];
  timeoutMs: number;
}

export type Approval = 'approved' | 'rejected' | 'pending' | 'not-supplied';
export type Availability = 'inspectable' | 'exists-not-supplied' | 'does-not-exist' | 'unknown';

export interface Fact {
  subject: string;
  approval: Approval;
  availability: Availability;
}

export interface DesignPlan {
  mode: 'design' | 'review' | 'graphics' | 'advisory';
  paths: string[];
  goal: string;
  brief: string;
  facts: Fact[];
  captures: CaptureSpec[];
  checks: CheckSpec[];
}

export interface Evidence {
  kind: 'capture' | 'check';
  id: string;
  revision: string;
  artifacts: { path: string; sha256: string }[];
  details: unknown;
}

export interface ReportRecord {
  path: string;
  sha256: string;
  inputSha256: string;
}

export interface RunState {
  version: 2;
  workspaceRoot: string;
  artifactRoot: string;
  plan: DesignPlan;
  phase: 'active' | 'completed' | 'advised' | 'stopped' | 'blocked' | 'limited';
  revision: string;
  evidence: Evidence[];
  report?: ReportRecord;
  acceptedReport?: string;
  reason?: string;
  missing: string[];
}

const APPROVALS: Approval[] = ['approved', 'rejected', 'pending', 'not-supplied'];
const AVAILABILITY: Availability[] = ['inspectable', 'exists-not-supplied', 'does-not-exist', 'unknown'];
export const MAX_REPORT = 64 * 1024;

const MAX_FILE = 10 * 1024 * 1024;
const MAX_ARTIFACT = 50 * 1024 * 1024;
const MAX_DETAILS = 32 * 1024;
const MAX_PLAN = 512 * 1024;
const DIGEST = /^[a-f0-9]{64}$/;
const ID = /^[a-zA-Z0-9][a-zA-Z0-9_.-]{0,63}$/;
const encoder = new TextEncoder();
export const MAX_CAPTURE_DIMENSION = 4096;

function fail(message: string): never { throw new Error(message); }
function object(value: unknown, name: string): Record<string, unknown> {
  if (!value || typeof value !== 'object' || Array.isArray(value)) fail(`${name} must be an object`);
  const proto = Object.getPrototypeOf(value);
  if (proto !== Object.prototype && proto !== null) fail(`${name} must be a plain object`);
  return value as Record<string, unknown>;
}
function keys(value: Record<string, unknown>, allowed: string[], name: string): void {
  for (const key of Object.keys(value)) if (!allowed.includes(key)) fail(`Unexpected ${name} property: ${key}`);
}
function text(value: unknown, name: string, max: number, allowEmpty = false): string {
  if (typeof value !== 'string' || (!allowEmpty && !value.trim()) || value.length > max || value.includes('\0')) fail(`Invalid ${name}`);
  return value;
}
function integer(value: unknown, name: string, min: number, max: number): number {
  if (typeof value !== 'number' || !Number.isInteger(value) || value < min || value > max) fail(`Invalid ${name}`);
  return value;
}
function list(value: unknown, name: string, max: number): unknown[] {
  if (!Array.isArray(value) || value.length > max) fail(`Invalid ${name}`);
  return value;
}
function identifier(value: unknown, name: string): string {
  const id = text(value, name, 64);
  if (!ID.test(id)) fail(`Invalid ${name}`);
  return id;
}
function relativeFile(value: unknown): string {
  const file = text(value, 'path', 1024);
  if (path.isAbsolute(file) || file.includes('\\') || /[\x00-\x1f*?\[\]{}]/.test(file) || /^[a-zA-Z][a-zA-Z0-9+.-]*:/.test(file)) fail(`Invalid path: ${file}`);
  const parts = file.split('/');
  if (parts.some(part => !part || part === '.' || part === '..')) fail(`Invalid path: ${file}`);
  return file;
}
function within(root: string, target: string): boolean {
  const rel = path.relative(root, target);
  return rel === '' || (!rel.startsWith(`..${path.sep}`) && rel !== '..' && !path.isAbsolute(rel));
}
function hash(bytes: string | Uint8Array): string { return createHash('sha256').update(bytes).digest('hex'); }
function jsonCopy<T>(value: T, max = MAX_DETAILS): T {
  let encoded: string | undefined;
  try { encoded = JSON.stringify(value); } catch { fail('Value must be JSON serializable'); }
  if (encoded === undefined || Buffer.byteLength(encoded) > max) fail('Invalid or oversized JSON value');
  return JSON.parse(encoded) as T;
}
function webTarget(value: unknown): string {
  const target = text(value, 'web target', 2048);
  let url: URL;
  try { url = new URL(target); } catch { return fail('Invalid web target'); }
  const host = url.hostname.toLowerCase();
  const ipv4 = host.split('.');
  const loopback4 = ipv4.length === 4 && ipv4.every(part => /^\d+$/.test(part) && Number(part) <= 255) && Number(ipv4[0]) === 127;
  if (!['http:', 'https:'].includes(url.protocol) || url.username || url.password || !(host === 'localhost' || host === '[::1]' || loopback4)) fail('Web target must use a loopback HTTP(S) origin without credentials');
  return target;
}
function parsePlan(input: unknown): DesignPlan {
  const plan = object(input, 'plan');
  keys(plan, ['mode', 'paths', 'goal', 'brief', 'facts', 'captures', 'checks'], 'plan');
  if (plan.mode !== 'design' && plan.mode !== 'review' && plan.mode !== 'graphics' && plan.mode !== 'advisory') fail('Invalid mode');
  const mode = plan.mode;
  const paths = list(plan.paths, 'paths', 128).map(relativeFile);
  if (new Set(paths).size !== paths.length) fail('Paths must be unique');
  const goal = text(plan.goal, 'goal', 4000);
  const brief = text(plan.brief, 'brief', 16_000);
  const facts = list(plan.facts, 'facts', 32).map((item): Fact => {
    const fact = object(item, 'fact');
    keys(fact, ['subject', 'approval', 'availability'], 'fact');
    const subject = text(fact.subject, 'fact subject', 200);
    if (/[\r\n|]/.test(subject)) fail('Fact subject must be one line without "|"');
    if (!APPROVALS.includes(fact.approval as Approval)) fail('Invalid fact approval');
    if (!AVAILABILITY.includes(fact.availability as Availability)) fail('Invalid fact availability');
    return { subject, approval: fact.approval as Approval, availability: fact.availability as Availability };
  });
  if (new Set(facts.map(f => f.subject)).size !== facts.length) fail('Fact subjects must be unique');
  const captures = list(plan.captures, 'captures', 32).map((item): CaptureSpec => {
    const spec = object(item, 'capture');
    keys(spec, ['id', 'kind', 'target', 'width', 'height', 'steps'], 'capture');
    const id = identifier(spec.id, 'capture id');
    if (spec.kind !== 'file' && spec.kind !== 'web') fail('Invalid capture kind');
    const kind = spec.kind;
    const target = kind === 'file' ? relativeFile(spec.target) : webTarget(spec.target);
    if (kind === 'file' && (!paths.includes(target) || !/\.(html?|svg)$/i.test(target))) fail('File capture target must be an allowed HTML or SVG file');
    const width = integer(spec.width, 'capture width', 1, MAX_CAPTURE_DIMENSION);
    const height = integer(spec.height, 'capture height', 1, MAX_CAPTURE_DIMENSION);
    let steps: BrowserStep[] | undefined;
    if (spec.steps !== undefined) {
      steps = list(spec.steps, 'browser steps', 64).map((item): BrowserStep => {
        const step = object(item, 'browser step');
        const action = step.action;
        if (action !== 'click' && action !== 'fill' && action !== 'press' && action !== 'assert-visible' && action !== 'assert-text') fail('Invalid browser action');
        if (mode === 'review' && action !== 'assert-visible' && action !== 'assert-text') fail('Review mode permits assertion steps only');
        const extra = action === 'fill' ? 'value' : action === 'press' ? 'key' : action === 'assert-text' ? 'text' : undefined;
        keys(step, ['action', 'selector', ...(extra ? [extra] : [])], 'browser step');
        const selector = text(step.selector, 'selector', 2048);
        if (action === 'fill') return { action, selector, value: text(step.value, 'fill value', 4096, true) };
        if (action === 'press') return { action, selector, key: text(step.key, 'key', 128) };
        if (action === 'assert-text') return { action, selector, text: text(step.text, 'assertion text', 4096, true) };
        return { action, selector };
      });
    }
    return { id, kind, target, width, height, ...(steps === undefined ? {} : { steps }) };
  });
  if (new Set(captures.map(c => c.id)).size !== captures.length) fail('Capture IDs must be unique');
  if (mode === 'advisory' ? captures.length : !captures.length) fail(mode === 'advisory' ? 'Advisory mode cannot declare captures' : 'At least one capture is required');
  const checks = list(plan.checks, 'checks', 32).map((item): CheckSpec => {
    const spec = object(item, 'check');
    keys(spec, ['id', 'command', 'args', 'timeoutMs'], 'check');
    const id = identifier(spec.id, 'check id');
    const command = text(spec.command, 'command', 1024);
    const args = list(spec.args, 'check args', 128).map(arg => text(arg, 'check argument', 4096, true));
    const timeoutMs = integer(spec.timeoutMs, 'timeout', 1, 600_000);
    return { id, command, args, timeoutMs };
  });
  if (new Set(checks.map(c => c.id)).size !== checks.length) fail('Check IDs must be unique');
  if ((mode === 'review' || mode === 'advisory') && checks.length) fail('Review and advisory modes cannot run command checks');
  return jsonCopy({ mode, paths, goal, brief, facts, captures, checks }, MAX_PLAN);
}

interface Resolved { actual: string; exists: boolean }

// 各成分を実際に解決し、既存部分がルート外に出ないことを確認する。
async function resolveInside(root: string, relative: string): Promise<Resolved> {
  if (await realpath(root) !== root) fail('Root identity changed');
  let current = root;
  const parts = relative.split('/');
  for (let i = 0; i < parts.length; i++) {
    const candidate = path.join(current, parts[i]);
    let stat;
    try { stat = await lstat(candidate); } catch (error) {
      if ((error as NodeJS.ErrnoException).code === 'ENOENT') return { actual: path.join(candidate, ...parts.slice(i + 1)), exists: false };
      throw error;
    }
    if (stat.isSymbolicLink()) {
      current = await realpath(candidate);
      if (!within(root, current)) fail(`Path escapes root: ${relative}`);
      stat = await lstat(current);
    } else {
      current = candidate;
    }
    if (i < parts.length - 1 && !stat.isDirectory()) fail(`Path parent is not a directory: ${relative}`);
    if (i === parts.length - 1 && !stat.isFile()) fail(`Path is not a regular file: ${relative}`);
  }
  return { actual: current, exists: true };
}
async function stableFile(root: string, relative: string, limit: number): Promise<{ actual: string; bytes: Buffer } | null> {
  const before = await resolveInside(root, relative);
  if (!before.exists) {
    const after = await resolveInside(root, relative);
    if (after.exists || before.actual !== after.actual) fail(`Path changed while reading: ${relative}`);
    return null;
  }
  const handle = await open(before.actual, constants.O_RDONLY | (constants.O_NOFOLLOW ?? 0));
  try {
    const first = await handle.stat();
    if (!first.isFile() || first.size > limit) fail(`Invalid or oversized file: ${relative}`);
    const bytes = await handle.readFile();
    const last = await handle.stat();
    const after = await resolveInside(root, relative);
    if (!after.exists || before.actual !== after.actual || first.dev !== last.dev || first.ino !== last.ino || first.size !== last.size || first.mtimeMs !== last.mtimeMs || first.ctimeMs !== last.ctimeMs || bytes.length > limit) fail(`Path changed while reading: ${relative}`);
    const current = await lstat(after.actual);
    if (!current.isFile() || current.dev !== last.dev || current.ino !== last.ino || current.size !== last.size || current.mtimeMs !== last.mtimeMs || current.ctimeMs !== last.ctimeMs) fail(`Path changed while reading: ${relative}`);
    return { actual: before.actual, bytes };
  } finally { await handle.close(); }
}

export class DesignRunEngine {
  private state?: RunState;
  private roots?: Promise<{ workspace: string; artifact: string }>;
  constructor(private readonly workspaceRoot: string, private readonly artifactRoot: string) {}

  private async getRoots(): Promise<{ workspace: string; artifact: string }> {
    if (!this.roots) this.roots = (async () => {
      const workspace = await realpath(this.workspaceRoot);
      const artifact = await realpath(this.artifactRoot);
      if (!(await lstat(workspace)).isDirectory() || !(await lstat(artifact)).isDirectory()) fail('Roots must be directories');
      if (within(workspace, artifact) || within(artifact, workspace)) fail('Artifact and workspace roots must not overlap');
      return { workspace, artifact };
    })();
    return this.roots;
  }
  private current(): RunState { return this.state ?? fail('No design run'); }
  private active(): RunState {
    const state = this.current();
    if (state.phase !== 'active') fail('Design run is not active');
    return state;
  }
  private allowed(file: string): string {
    const relative = relativeFile(file);
    if (!this.current().plan.paths.includes(relative)) fail(`Path is not approved: ${relative}`);
    return relative;
  }
  private async digest(plan: DesignPlan): Promise<string> {
    const { workspace } = await this.getRoots();
    if (await realpath(workspace) !== workspace) fail('Root identity changed');
    const paths = [...plan.paths].sort();
    let previous: string | undefined;
    for (let pass = 0; pass < 2; pass++) {
      const entries: unknown[] = [];
      for (const file of paths) {
        const result = await stableFile(workspace, file, MAX_FILE);
        if (result) entries.push([file, result.actual, hash(result.bytes)]);
        else {
          const missing = await resolveInside(workspace, file);
          if (missing.exists) fail(`Path changed while snapshotting: ${file}`);
          entries.push([file, missing.actual, null]);
        }
      }
      const digest = hash(JSON.stringify(entries));
      if (previous !== undefined && previous !== digest) fail('Workspace changed while snapshotting');
      previous = digest;
    }
    return previous!;
  }
  async start(input: DesignPlan): Promise<RunState> {
    if (this.state?.phase === 'active') fail('A design run is already active');
    const plan = parsePlan(input);
    const { workspace, artifact } = await this.getRoots();
    const revision = await this.digest(plan);
    this.state = { version: 2, workspaceRoot: workspace, artifactRoot: artifact, plan, phase: 'active', revision, evidence: [], missing: [] };
    await this.refresh();
    return this.exportState();
  }
  async snapshot(): Promise<string> { return this.digest(this.current().plan); }
  async read(file: string): Promise<string> {
    const relative = this.allowed(file);
    const result = await stableFile((await this.getRoots()).workspace, relative, MAX_FILE);
    if (!result) fail(`File does not exist: ${relative}`);
    try { return new TextDecoder('utf-8', { fatal: true }).decode(result.bytes); }
    catch { return fail(`File is not UTF-8: ${relative}`); }
  }
  async write(file: string, content: string): Promise<RunState> {
    // 1. 一時ファイルを作る前に権限・対象パス・元の指紋を確定する。
    const state = this.active();
    if (state.plan.mode === 'review' || state.plan.mode === 'advisory') fail(`${state.plan.mode === 'review' ? 'Review' : 'Advisory'} mode cannot write`);
    const relative = this.allowed(file);
    if (typeof content !== 'string' || encoder.encode(content).length > MAX_FILE) fail('Invalid or oversized content');
    await this.refresh();
    const { workspace } = await this.getRoots();
    const parts = relative.split('/');
    for (let i = 1; i < parts.length; i++) {
      const prefix = parts.slice(0, i).join('/');
      const parent = await resolveDirectory(workspace, prefix);
      if (!parent.exists) {
        try { await mkdir(parent.actual); } catch (error) { if ((error as NodeJS.ErrnoException).code !== 'EEXIST') throw error; }
        await resolveDirectory(workspace, prefix);
      }
    }
    const destination = await resolveInside(workspace, relative);
    const parentRelative = parts.slice(0, -1).join('/');
    const parent = parentRelative ? await resolveDirectory(workspace, parentRelative) : { actual: workspace, exists: true };
    if (!parent.exists || !within(workspace, path.dirname(destination.actual))) fail('Destination parent changed');
    // 2. 元の権限を保った一時ファイルを準備し、未完成の内容を公開しない。
    const temp = path.join(path.dirname(destination.actual), `.design-workflow-${randomBytes(16).toString('hex')}.tmp`);
    const mode = destination.exists ? (await lstat(destination.actual)).mode & 0o777 : undefined;
    let created = false;
    try {
      const handle = await open(temp, 'wx', mode ?? 0o666);
      created = true;
      try {
        if (mode !== undefined) await handle.chmod(mode);
        await handle.writeFile(content, 'utf8');
      } finally { await handle.close(); }
      // 3. 保存中の差替えを再検査してから、同じ親内で原子的に置換する。
      const again = await resolveInside(workspace, relative);
      const parentAgain = parentRelative ? await resolveDirectory(workspace, parentRelative) : { actual: workspace, exists: true };
      if (!parentAgain.exists || parentAgain.actual !== parent.actual || again.actual !== destination.actual || again.exists !== destination.exists) fail('Destination changed during write');
      if (await this.snapshot() !== state.revision) fail('Workspace changed during write');
      await rename(temp, destination.actual);
      created = false;
    } finally { if (created) await unlink(temp).catch(() => {}); }
    // 4. 書込み後の指紋で古い証拠と承認を失効させる。
    await this.refresh();
    return this.exportState();
  }
  captureSpec(id: string): CaptureSpec {
    const spec = this.current().plan.captures.find(item => item.id === id);
    if (!spec) fail(`Unknown capture: ${id}`);
    return jsonCopy(spec, MAX_PLAN);
  }
  checkSpec(id: string): CheckSpec {
    const spec = this.current().plan.checks.find(item => item.id === id);
    if (!spec) fail(`Unknown check: ${id}`);
    return jsonCopy(spec, MAX_PLAN);
  }
  beginEvidence(kind: 'capture' | 'check', id: string): void {
    const state = this.active();
    if (kind === 'capture') this.captureSpec(id);
    else this.checkSpec(id);
    // 再実行の開始時点で旧証拠・報告・承認を失効させ、失敗時にも成功を持ち越さない。
    state.evidence = state.evidence.filter(item => item.kind !== kind || item.id !== id);
    this.dropReport(state);
    const required = `${kind}:${id}`;
    if (!state.missing.includes(required)) state.missing.unshift(required);
  }
  private dropReport(state: RunState): void {
    delete state.report;
    delete state.acceptedReport;
    for (const item of ['report', 'review']) if (!state.missing.includes(item)) state.missing.push(item);
  }
  // 計画・ファイル指紋・証拠を一つの入力指紋にまとめ、報告をこの入力へ束縛する。
  private inputDigest(state: RunState): string {
    const evidence = [...state.evidence]
      .sort((a, b) => `${a.kind}:${a.id}`.localeCompare(`${b.kind}:${b.id}`))
      .map(item => [item.kind, item.id, item.revision, item.artifacts]);
    return hash(JSON.stringify({ plan: state.plan, revision: state.revision, evidence }));
  }
  private async artifact(file: string): Promise<{ path: string; sha256: string }> {
    const { artifact } = await this.getRoots();
    if (typeof file !== 'string' || !file || file.includes('\0')) fail('Invalid artifact path');
    const requested = path.resolve(artifact, file);
    const suppliedRoot = path.resolve(this.artifactRoot);
    const absolute = path.isAbsolute(file) && within(suppliedRoot, requested)
      ? path.resolve(artifact, path.relative(suppliedRoot, requested))
      : requested;
    if (!within(artifact, absolute) || absolute === artifact) fail('Artifact escapes artifact root');
    const relative = path.relative(artifact, absolute).split(path.sep).join('/');
    const result = await stableFile(artifact, relative, MAX_ARTIFACT);
    if (!result) fail(`Artifact does not exist: ${file}`);
    return { path: absolute, sha256: hash(result.bytes) };
  }
  async recordEvidence(input: { kind: 'capture' | 'check'; id: string; revision: string; artifacts: string[]; details: unknown }): Promise<RunState> {
    // 1. 宣言済みの項目と現在の指紋だけを証拠として受け付ける。
    const state = this.active();
    const record = object(input, 'evidence');
    keys(record, ['kind', 'id', 'revision', 'artifacts', 'details'], 'evidence');
    if (input.kind === 'capture') this.captureSpec(input.id);
    else if (input.kind === 'check') this.checkSpec(input.id);
    else fail('Invalid evidence kind');
    await this.refresh();
    if (input.revision !== state.revision) fail('Evidence revision is stale');
    const paths = list(input.artifacts, 'artifacts', 16).map(item => text(item, 'artifact path', 4096));
    if (paths.length < (input.kind === 'capture' ? 2 : 1) || new Set(paths).size !== paths.length) fail('Evidence requires distinct artifact files');
    // 2. 実ファイルの検証後に指紋を再確認し、新しい証拠で承認をリセットする。
    const artifacts = [];
    for (const file of paths) artifacts.push(await this.artifact(file));
    if (new Set(artifacts.map(item => item.path)).size !== artifacts.length) fail('Evidence artifacts must be distinct');
    const details = jsonCopy(input.details);
    if (await this.snapshot() !== input.revision) { await this.refresh(); fail('Evidence revision changed while recording'); }
    state.evidence = state.evidence.filter(item => item.kind !== input.kind || item.id !== input.id);
    state.evidence.push({ kind: input.kind, id: input.id, revision: input.revision, artifacts, details });
    this.dropReport(state);
    await this.refresh();
    return this.exportState();
  }
  private async refresh(): Promise<void> {
    const state = this.current();
    const revision = await this.digest(state.plan);
    if (state.revision !== revision) {
      state.revision = revision;
      state.evidence = [];
      delete state.report;
      delete state.acceptedReport;
    }
    const missing: string[] = [];
    for (const [kind, specs] of [['capture', state.plan.captures], ['check', state.plan.checks]] as const) {
      for (const spec of specs) {
        const evidence = state.evidence.find(item => item.kind === kind && item.id === spec.id && item.revision === revision);
        let fresh = !!evidence;
        if (evidence) for (const stored of evidence.artifacts) {
          try {
            const actual = await this.artifact(stored.path);
            if (actual.path !== stored.path || actual.sha256 !== stored.sha256) fresh = false;
          } catch { fresh = false; }
        }
        if (!fresh) {
          missing.push(`${kind}:${spec.id}`);
          state.evidence = state.evidence.filter(item => item.kind !== kind || item.id !== spec.id);
        }
      }
    }
    if (await this.digest(state.plan) !== revision) fail('Workspace changed while validating evidence');
    // 報告は現在の入力指紋と保存済み本文が一致する場合だけ有効とする。
    if (state.report) {
      let fresh = !missing.length && state.report.inputSha256 === this.inputDigest(state);
      if (fresh) {
        try {
          const actual = await this.artifact(state.report.path);
          fresh = actual.path === state.report.path && actual.sha256 === state.report.sha256;
        } catch { fresh = false; }
      }
      if (!fresh) delete state.report;
    }
    if (!state.report) missing.push('report');
    if (!state.report || state.acceptedReport !== state.report.sha256) {
      delete state.acceptedReport;
      missing.push('review');
    }
    state.missing = missing;
    if ((state.phase === 'completed' || state.phase === 'advised') && missing.length) state.phase = 'active';
  }
  beginReport(): void {
    this.dropReport(this.active());
  }
  async reportInput(): Promise<{ inputSha256: string; state: RunState }> {
    const state = this.active();
    await this.refresh();
    const evidence = state.missing.filter(item => item !== 'report' && item !== 'review');
    if (evidence.length) fail(`Evidence is missing or stale: ${evidence.join(', ')}`);
    return { inputSha256: this.inputDigest(state), state: this.exportState() };
  }
  async recordReport(inputSha256: string, report: string): Promise<RunState> {
    // 1. 生成中に入力が変わった報告は保存しない。
    const state = this.active();
    if (typeof report !== 'string' || !report.trim() || encoder.encode(report).length > MAX_REPORT) fail('Invalid or oversized report');
    await this.refresh();
    if (state.missing.some(item => item !== 'report' && item !== 'review') || this.inputDigest(state) !== inputSha256) fail('Report input is stale');
    // 2. 成果物ルートに新規作成し、保存後の内容ハッシュを記録する。
    const { artifact } = await this.getRoots();
    const file = path.join(artifact, `report-${randomBytes(16).toString('hex')}.md`);
    const handle = await open(file, 'wx', 0o600);
    try { await handle.writeFile(report, 'utf8'); } finally { await handle.close(); }
    const stored = await this.artifact(file);
    if (stored.sha256 !== hash(report)) fail('Report changed while storing');
    state.report = { path: stored.path, sha256: stored.sha256, inputSha256 };
    delete state.acceptedReport;
    await this.refresh();
    if (!state.report || state.report.sha256 !== stored.sha256) fail('Report input changed while storing');
    return this.exportState();
  }
  async reportText(): Promise<string> {
    const state = this.current();
    await this.refresh();
    if (!state.report) fail('No checked report for the current input');
    const { artifact } = await this.getRoots();
    const result = await stableFile(artifact, path.relative(artifact, state.report.path).split(path.sep).join('/'), MAX_REPORT);
    if (!result || hash(result.bytes) !== state.report.sha256) fail('Report changed on disk');
    return result.bytes.toString('utf8');
  }
  // 承認は現在の入力に束縛された報告の正確なハッシュに対してだけ記録し、同時に完了させる。
  async acceptAndFinish(reportSha256: string): Promise<RunState> {
    const state = this.active();
    await this.refresh();
    if (state.missing.some(item => item !== 'review')) fail(`Cannot accept; missing or stale: ${state.missing.join(', ')}`);
    if (state.report?.sha256 !== reportSha256) fail('Report changed since it was shown');
    state.acceptedReport = reportSha256;
    await this.refresh();
    if (state.missing.length || state.acceptedReport !== reportSha256) fail('Input changed while accepting the report');
    state.phase = state.plan.mode === 'advisory' ? 'advised' : 'completed';
    return this.exportState();
  }
  async stop(reason: string, outcome: 'stopped' | 'blocked' | 'limited'): Promise<RunState> {
    const state = this.current();
    if (outcome !== 'stopped' && outcome !== 'blocked' && outcome !== 'limited') fail('Invalid outcome');
    state.reason = text(reason, 'reason', 4000);
    state.phase = outcome;
    delete state.acceptedReport;
    if (!state.missing.includes('review')) state.missing.push('review');
    return this.exportState();
  }
  async status(): Promise<RunState> { await this.refresh(); return this.exportState(); }
  exportState(): RunState { return jsonCopy(this.current(), 16 * 1024 * 1024); }
  isActive(): boolean { return this.state?.phase === 'active'; }
  async restore(input: RunState): Promise<void> {
    // 1. 保存データ全体を検証するまで、稼働中の状態を置き換えない。
    const value = object(input, 'state');
    keys(value, ['version', 'workspaceRoot', 'artifactRoot', 'plan', 'phase', 'revision', 'evidence', 'report', 'acceptedReport', 'reason', 'missing'], 'state');
    if (value.version !== 2) fail('Unsupported state version');
    const roots = await this.getRoots();
    if (value.workspaceRoot !== roots.workspace || value.artifactRoot !== roots.artifact) fail('State roots do not match');
    const plan = parsePlan(value.plan);
    if (!['active', 'completed', 'advised', 'stopped', 'blocked', 'limited'].includes(value.phase as string)) fail('Invalid state phase');
    const phase = value.phase as RunState['phase'];
    const revision = text(value.revision, 'revision', 64);
    if (!DIGEST.test(revision)) fail('Invalid state revision');
    const evidence = list(value.evidence, 'evidence', 64).map((item): Evidence => {
      const entry = object(item, 'evidence');
      keys(entry, ['kind', 'id', 'revision', 'artifacts', 'details'], 'evidence');
      if (entry.kind !== 'capture' && entry.kind !== 'check') fail('Invalid evidence kind');
      const kind = entry.kind;
      const id = identifier(entry.id, 'evidence id');
      if (!(kind === 'capture' ? plan.captures : plan.checks).some(spec => spec.id === id)) fail('Evidence is not declared');
      const evidenceRevision = text(entry.revision, 'evidence revision', 64);
      if (!DIGEST.test(evidenceRevision)) fail('Invalid evidence revision');
      const artifacts = list(entry.artifacts, 'artifacts', 16).map(item => {
        const entry = object(item, 'artifact');
        keys(entry, ['path', 'sha256'], 'artifact');
        const file = text(entry.path, 'artifact path', 4096);
        const sha256 = text(entry.sha256, 'artifact hash', 64);
        if (!path.isAbsolute(file) || !within(roots.artifact, file) || path.resolve(file) !== file || file === roots.artifact || !DIGEST.test(sha256)) fail('Invalid stored artifact');
        return { path: file, sha256 };
      });
      if (artifacts.length < (kind === 'capture' ? 2 : 1) || new Set(artifacts.map(a => a.path)).size !== artifacts.length) fail('Invalid stored artifacts');
      return { kind, id, revision: evidenceRevision, artifacts, details: jsonCopy(entry.details) };
    });
    if (new Set(evidence.map(item => `${item.kind}:${item.id}`)).size !== evidence.length) fail('Duplicate evidence');
    let report: ReportRecord | undefined;
    if (value.report !== undefined) {
      const entry = object(value.report, 'report');
      keys(entry, ['path', 'sha256', 'inputSha256'], 'report');
      const file = text(entry.path, 'report path', 4096);
      const sha256 = text(entry.sha256, 'report hash', 64);
      const inputSha256 = text(entry.inputSha256, 'report input hash', 64);
      if (!path.isAbsolute(file) || !within(roots.artifact, file) || path.resolve(file) !== file || file === roots.artifact || !DIGEST.test(sha256) || !DIGEST.test(inputSha256)) fail('Invalid stored report');
      report = { path: file, sha256, inputSha256 };
    }
    const acceptedReport = value.acceptedReport === undefined ? undefined : text(value.acceptedReport, 'accepted report', 64);
    if (acceptedReport !== undefined && !DIGEST.test(acceptedReport)) fail('Invalid accepted report');
    const reason = value.reason === undefined ? undefined : text(value.reason, 'reason', 4000);
    if (['stopped', 'blocked', 'limited'].includes(phase) && !reason) fail('Terminal outcome requires a reason');
    list(value.missing, 'missing', 65).forEach(item => text(item, 'missing entry', 128));
    // 2. 実ファイルとの整合性を再検証し、復元不能なら元の状態へ戻す。
    const previous = this.state;
    this.state = { version: 2, workspaceRoot: roots.workspace, artifactRoot: roots.artifact, plan, phase, revision, evidence, ...(report === undefined ? {} : { report }), ...(acceptedReport === undefined ? {} : { acceptedReport }), ...(reason === undefined ? {} : { reason }), missing: [] };
    try { await this.refresh(); } catch (error) { this.state = previous; throw error; }
  }
}

async function resolveDirectory(root: string, relative: string): Promise<Resolved> {
  if (await realpath(root) !== root) fail('Root identity changed');
  let current = root;
  const parts = relative.split('/');
  for (let i = 0; i < parts.length; i++) {
    const candidate = path.join(current, parts[i]);
    let stat;
    try { stat = await lstat(candidate); } catch (error) {
      if ((error as NodeJS.ErrnoException).code === 'ENOENT') return { actual: path.join(candidate, ...parts.slice(i + 1)), exists: false };
      throw error;
    }
    if (stat.isSymbolicLink()) {
      current = await realpath(candidate);
      if (!within(root, current)) fail(`Directory escapes root: ${relative}`);
      stat = await lstat(current);
    } else current = candidate;
    if (!stat.isDirectory()) fail(`Path parent is not a directory: ${relative}`);
  }
  return { actual: current, exists: true };
}
