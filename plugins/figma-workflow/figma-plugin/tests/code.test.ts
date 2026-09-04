import assert from 'node:assert/strict';
import test from 'node:test';

import { FigmaNodePort } from '../src/figma-adapter.js';
type ResultMessage = { type: 'result'; request: string; requestId: number | null; input: string | null; result: unknown };
type Handler = (message: unknown) => Promise<void>;

const startupFigma = {
  showUI() {},
  ui: { onmessage: undefined, postMessage() {} },
  currentPage: { selection: [] },
  async getNodeByIdAsync() { return null; },
};
Object.defineProperty(globalThis, 'figma', { configurable: true, value: startupFigma });
const codeModule = await import('../src/code.js');

function handlerFor(port: unknown, posted: ResultMessage[]): Handler {
  const create = (codeModule as unknown as {
    createUiMessageHandler?: (port: unknown, post: (message: ResultMessage) => void) => Handler;
  }).createUiMessageHandler;
  assert.equal(typeof create, 'function');
  return create!(port, (message) => posted.push(message));
}

test('malformed UI messages receive a structured invalid result', async () => {
  const posted: ResultMessage[] = [];
  await handlerFor({}, posted)(null);

  assert.deepEqual(posted, [{
    type: 'result', request: 'invalid', requestId: null, input: null,
    result: { status: 'invalid', reason: 'INVALID_FIELD' },
  }]);
});

test('throwing malformed message fields still receive a structured invalid result', async () => {
  const posted: ResultMessage[] = [];
  const malformed = Object.defineProperty({}, 'type', { get() { throw new Error('malformed getter'); } });

  await handlerFor({}, posted)(malformed);

  assert.deepEqual(posted, [{
    type: 'result', request: 'invalid', requestId: null, input: null,
    result: { status: 'invalid', reason: 'INVALID_FIELD' },
  }]);
});

test('selection getMainComponentAsync rejection is classified without exposing raw errors', async () => {
  const posted: ResultMessage[] = [];
  const plan = JSON.stringify({ version: 1, mode: 'preview', operation: 'inspect-selection', scope: { kind: 'selection' } });
  const descriptor = Object.getOwnPropertyDescriptor(globalThis, 'figma');
  Object.defineProperty(globalThis, 'figma', { configurable: true, value: {
    currentPage: { selection: [{ id: 'instance', type: 'INSTANCE', name: 'Instance', async getMainComponentAsync() { throw new Error('lookup failed'); } }] },
    async getNodeByIdAsync() { return null; },
  } });
  try {
    await handlerFor(new FigmaNodePort(), posted)({ type: 'preview', plan, input: plan, requestId: 7 });
  } finally {
    if (descriptor) Object.defineProperty(globalThis, 'figma', descriptor);
    else Reflect.deleteProperty(globalThis, 'figma');
  }

  assert.deepEqual(posted, [{
    type: 'result', request: 'preview', requestId: 7, input: plan,
    result: { status: 'invalid', reason: 'LOOKUP_FAILED' },
  }]);
});

test('prototype destination lookup exceptions are classified without exposing raw errors', async () => {
  const posted: ResultMessage[] = [];
  const plan = JSON.stringify({ version: 1, mode: 'preview', operation: 'audit-prototype-links', scope: { kind: 'selection' } });
  await handlerFor({
    async getSelection() {
      return [{ id: 'screen', type: 'FRAME', name: 'Screen', reactions: [{ actions: [{ destinationId: 'gone' }] }] }];
    },
    async readNode() { throw new Error('destination lookup failed'); },
  }, posted)({ type: 'preview', plan, input: plan, requestId: 8 });

  assert.deepEqual(posted, [{
    type: 'result', request: 'preview', requestId: 8, input: plan,
    result: { status: 'invalid', reason: 'LOOKUP_FAILED' },
  }]);
});
