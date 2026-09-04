import assert from 'node:assert/strict';
import { readFile } from 'node:fs/promises';
import { resolve } from 'node:path';
import test from 'node:test';
import vm from 'node:vm';

type Listener = () => void;
class FakeElement {
  value = '';
  textContent = '';
  disabled = false;
  private readonly listeners = new Map<string, Listener>();

  addEventListener(type: string, listener: Listener) { this.listeners.set(type, listener); }
  trigger(type: string) { this.listeners.get(type)?.(); }
}

async function loadUi() {
  const source = await readFile(resolve(import.meta.dirname, '../src/ui.html'), 'utf8');
  const script = source.match(/<script>([\s\S]*?)<\/script>/)?.[1];
  assert.ok(script);
  const plan = new FakeElement();
  plan.value = JSON.stringify({ version: 1, mode: 'preview', operation: 'rename-exact', targets: [{ nodeId: '1:2', expectedName: 'A', newName: 'B' }] });
  const result = new FakeElement();
  const status = new FakeElement();
  const preview = new FakeElement();
  const apply = new FakeElement();
  const copy = new FakeElement();
  const elements: Record<string, FakeElement> = {
    '#plan': plan, '#result': result, '#status': status,
    '[data-action="preview"]': preview, '[data-action="apply"]': apply, '[data-action="copy"]': copy,
  };
  const posted: unknown[] = [];
  const window: { onmessage?: (event: unknown) => void } = {};
  vm.runInNewContext(script, {
    JSON, Object, Promise, document: { querySelector: (selector: string) => elements[selector] },
    parent: { postMessage: (message: unknown) => posted.push(message) },
    navigator: { clipboard: { writeText: async () => undefined } }, window,
  });
  return { plan, result, preview, apply, posted, window };
}

test('late preview responses cannot restore a receipt after the input changes', async () => {
  const ui = await loadUi();
  ui.preview.trigger('click');
  const first = ui.posted[0] as { pluginMessage: { requestId?: unknown; plan: string } };
  assert.equal(typeof first.pluginMessage.requestId, 'number');

  ui.plan.value = ui.plan.value.replace('"B"', '"C"');
  ui.plan.trigger('input');
  ui.window.onmessage?.({ data: { pluginMessage: {
    type: 'result', request: 'preview', requestId: first.pluginMessage.requestId, input: first.pluginMessage.plan,
    result: { status: 'ready', receipt: { fingerprint: 'old', targets: [] } },
  } } });

  assert.equal(ui.apply.disabled, true);
});

test('late apply responses cannot replace the latest request result', async () => {
  const ui = await loadUi();
  ui.preview.trigger('click');
  const preview = ui.posted[0] as { pluginMessage: { requestId: number; plan: string } };
  ui.window.onmessage?.({ data: { pluginMessage: {
    type: 'result', request: 'preview', requestId: preview.pluginMessage.requestId, input: preview.pluginMessage.plan,
    result: { status: 'ready', receipt: { fingerprint: 'receipt', targets: [] } },
  } } });
  ui.apply.trigger('click');
  const apply = ui.posted[1] as { pluginMessage: { requestId: number; plan: string } };
  ui.preview.trigger('click');
  const latest = ui.posted[2] as { pluginMessage: { requestId: number; plan: string } };
  ui.window.onmessage?.({ data: { pluginMessage: {
    type: 'result', request: 'apply', requestId: apply.pluginMessage.requestId, input: apply.pluginMessage.plan,
    result: { status: 'applied' },
  } } });

  assert.notEqual(apply.pluginMessage.requestId, latest.pluginMessage.requestId);
  assert.equal(ui.result.textContent, JSON.stringify({ status: 'ready', receipt: { fingerprint: 'receipt', targets: [] } }, null, 2));
});
