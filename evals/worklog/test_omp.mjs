import assert from 'node:assert/strict';
import { execFileSync } from 'node:child_process';
import { mkdtempSync, mkdirSync, readdirSync, readFileSync, realpathSync, rmSync, symlinkSync, writeFileSync } from 'node:fs';
import { tmpdir } from 'node:os';
import { join } from 'node:path';
import { test } from 'node:test';
import worklog from '../../plugins/worklog/omp-extension/worklog.ts';

function fixture(t) {
  const root = realpathSync(mkdtempSync(join(tmpdir(), 'worklog-omp-')));
  const cwd = join(root, 'project');
  mkdirSync(cwd);
  execFileSync('git', ['init', '-q', cwd]);
  const home = join(root, 'logs');
  const previous = process.env.SONSU_WORKLOG_HOME;
  const previousOff = process.env.SONSU_WORKLOG;
  process.env.SONSU_WORKLOG_HOME = home;
  delete process.env.SONSU_WORKLOG;
  t.after(() => {
    if (previous === undefined) delete process.env.SONSU_WORKLOG_HOME;
    else process.env.SONSU_WORKLOG_HOME = previous;
    if (previousOff === undefined) delete process.env.SONSU_WORKLOG;
    else process.env.SONSU_WORKLOG = previousOff;
    rmSync(root, { recursive: true, force: true });
  });
  const handlers = {};
  worklog({ on: (name, fn) => { handlers[name] = fn; } });
  const context = id => ({ cwd, sessionManager: {
    getSessionId: () => id, getSessionFile: () => join(root, `${id}.jsonl`),
  } });
  const emit = (event, id, payload = {}) => handlers[event]?.(payload, context(id));
  const project = () => join(home, readdirSync(home)[0]);
  const rows = () => {
    const host = join(project(), 'omp');
    return readdirSync(host).filter(x => /^\d{4}-/.test(x)).flatMap(date =>
      readdirSync(join(host, date)).flatMap(file => readFileSync(join(host, date, file), 'utf8')
        .trim().split('\n').filter(Boolean).map(JSON.parse)));
  };
  return { root, home, emit, project, rows };
}

test('new, resume, and branch events preserve session and transcript identity', t => {
  const f = fixture(t);
  f.emit('session_start', 'first');
  f.emit('session_switch', 'second', { reason: 'new' });
  f.emit('tool_result', 'second', { isError: true, toolName: 'bash', toolCallId: 'second-tool', content: [{type: 'text', text: 'missing'}] });
  f.emit('session_branch', 'branch');
  f.emit('agent_end', 'branch');
  f.emit('session_switch', 'first', { reason: 'resume' });
  f.emit('session_shutdown', 'first');
  const rows = f.rows();
  assert.equal(rows.find(r => r.data.tool_use_id === 'second-tool').session_id, 'second');
  assert.equal(rows.find(r => r.event === 'stop').session_id, 'branch');
  assert.equal(rows.find(r => r.event === 'session_end').session_id, 'first');
  for (const id of ['first', 'second', 'branch']) {
    assert.equal(rows.find(r => r.event === 'session_start' && r.session_id === id).data.transcript_path,
      join(f.root, `${id}.jsonl`));
  }
});

test('symlinked host cannot redirect recording or retention deletion', t => {
  const f = fixture(t);
  f.emit('session_start', 'first');
  rmSync(join(f.project(), 'omp'), { recursive: true });
  const outside = join(f.root, 'outside');
  mkdirSync(join(outside, '2000-01-01'), { recursive: true });
  const important = join(outside, '2000-01-01', 'important.txt');
  writeFileSync(important, 'keep');
  symlinkSync(outside, join(f.project(), 'omp'), 'dir');
  f.emit('session_start', 'second');
  assert.deepEqual(readdirSync(outside), ['2000-01-01']);
  assert.equal(readFileSync(important, 'utf8'), 'keep');
});

test('expired session restarts its log date before retention runs', t => {
  const f = fixture(t);
  f.emit('session_start', 'first');
  const host = join(f.project(), 'omp');
  writeFileSync(join(host, '.state', 'first.json'), JSON.stringify({date: '2000-01-01'}));
  rmSync(join(host, '.state', 'last-prune'));
  f.emit('session_start', 'first');
  f.emit('tool_result', 'first', {isError: true, toolCallId: 'resumed-tool'});
  assert.equal(JSON.parse(readFileSync(join(host, '.state', 'first.json'), 'utf8')).date,
    new Date().toISOString().slice(0, 10));
  const rows = f.rows();
  assert.equal(rows.find(r => r.data.tool_use_id === 'resumed-tool').session_id, 'first');
  assert(!readdirSync(host).includes('2000-01-01'));
});
