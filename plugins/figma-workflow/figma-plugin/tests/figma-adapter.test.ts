import assert from 'node:assert/strict';
import test from 'node:test';

import { previewPlan } from '../src/engine.js';
import { FigmaNodePort } from '../src/figma-adapter.js';

async function withFigma<T>(figmaApi: unknown, run: () => Promise<T>): Promise<T> {
  const descriptor = Object.getOwnPropertyDescriptor(globalThis, 'figma');
  Object.defineProperty(globalThis, 'figma', { configurable: true, value: figmaApi });
  try {
    return await run();
  } finally {
    if (descriptor) {
      Object.defineProperty(globalThis, 'figma', descriptor);
    } else {
      Reflect.deleteProperty(globalThis, 'figma');
    }
  }
}

test('selected FILL root preserves its Auto Layout parent for audit', async () => {
  const parent = { id: 'parent', type: 'FRAME', name: 'Auto parent', layoutMode: 'VERTICAL' };
  const selected = { id: 'selected', type: 'RECTANGLE', name: 'Fill', layoutSizingHorizontal: 'FILL', parent };
  const result = await withFigma({
    currentPage: { selection: [selected] },
    async getNodeByIdAsync(nodeId: string) { return nodeId === selected.id ? selected : null; },
  }, () => previewPlan(JSON.stringify({
    version: 1, mode: 'preview', operation: 'audit-auto-layout', scope: { kind: 'selection' },
  }), new FigmaNodePort()));

  assert.deepEqual(result, { status: 'clean', findings: [] });
});

test('selection snapshots distinguish literal and variable-bound opacity facts', async () => {
  const literal = { id: 'literal', type: 'RECTANGLE', name: 'Literal', opacity: 0.5, parent: null };
  const bound = {
    id: 'bound', type: 'RECTANGLE', name: 'Bound', opacity: 0.5, parent: null,
    boundVariables: { opacity: { type: 'VARIABLE_ALIAS', id: 'VariableID:1:2' } },
  };
  const result = await withFigma({
    currentPage: { selection: [literal, bound] },
    async getNodeByIdAsync() { return null; },
  }, () => previewPlan(JSON.stringify({
    version: 1, mode: 'preview', operation: 'inspect-selection', scope: { kind: 'selection' },
  }), new FigmaNodePort()));

  assert.deepEqual(result, {
    status: 'inspected',
    nodes: [
      { id: 'literal', type: 'RECTANGLE', name: 'Literal', variableBindings: { opacity: { kind: 'literal', value: 0.5 } } },
      { id: 'bound', type: 'RECTANGLE', name: 'Bound', variableBindings: { opacity: { kind: 'binding', variableId: 'VariableID:1:2' } } },
    ],
  });
});
