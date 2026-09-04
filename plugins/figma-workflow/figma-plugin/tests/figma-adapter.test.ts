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

test('final adapter lookups return lookup_failed while assignment failures reject', async () => {
  await withFigma({
    currentPage: { selection: [] },
    async getNodeByIdAsync() { throw new Error('lookup failed'); },
  }, async () => {
    const port = new FigmaNodePort();
    assert.equal(await port.renameIfCurrent('node', 'A', 'B'), 'lookup_failed');
    assert.equal(await port.replaceIconInstanceIfCurrent('node', 'old', { type: 'COMPONENT', key: 'new' }), 'lookup_failed');
  });

  const icon = {
    id: 'icon', type: 'INSTANCE', name: 'Icon',
    async getMainComponentAsync() { throw new Error('component lookup failed'); },
    swapComponent() { throw new Error('must not swap'); },
  };
  await withFigma({
    currentPage: { selection: [] },
    async getNodeByIdAsync() { return icon; },
  }, async () => {
    const port = new FigmaNodePort();
    assert.equal(await port.replaceIconInstanceIfCurrent('icon', 'old', { type: 'COMPONENT', key: 'new' }), 'lookup_failed');
  });

  const node = { id: 'node', type: 'RECTANGLE' };
  Object.defineProperty(node, 'name', { get: () => 'A', set: () => { throw new Error('assignment failed'); } });
  await withFigma({
    currentPage: { selection: [] },
    async getNodeByIdAsync() { return node; },
  }, async () => {
    await assert.rejects(new FigmaNodePort().renameIfCurrent('node', 'A', 'B'), /assignment failed/);
  });

  const swapFailure = {
    id: 'swap-failure', type: 'INSTANCE', name: 'Icon',
    async getMainComponentAsync() { return { type: 'COMPONENT', key: 'old' }; },
    swapComponent() { throw new Error('swap failed'); },
  };
  await withFigma({
    currentPage: { selection: [] },
    async getNodeByIdAsync() { return swapFailure; },
  }, async () => {
    await assert.rejects(
      new FigmaNodePort().replaceIconInstanceIfCurrent('swap-failure', 'old', { type: 'COMPONENT', key: 'new' }),
      /swap failed/,
    );
  });
});

test('selection snapshots normalize aliases, alias arrays and component property bindings', async () => {
  const alias = (id: string) => ({ type: 'VARIABLE_ALIAS', id });
  const node = {
    id: 'bound', type: 'COMPONENT', name: 'Bound', opacity: 0.5, parent: null,
    boundVariables: {
      width: alias('VariableID:width'),
      fills: [alias('VariableID:fill')],
      text: [alias('VariableID:text-1'), alias('VariableID:text-2')],
      componentProperties: { 'Icon#123': alias('VariableID:icon') },
      malformed: [{ id: 'missing-type' }],
    },
  };
  const result = await withFigma({
    currentPage: { selection: [node] },
    async getNodeByIdAsync() { return null; },
  }, () => previewPlan(JSON.stringify({
    version: 1, mode: 'preview', operation: 'inspect-selection', scope: { kind: 'selection' },
  }), new FigmaNodePort()));

  assert.deepEqual(result, {
    status: 'inspected',
    nodes: [{
      id: 'bound', type: 'COMPONENT', name: 'Bound',
      variableBindings: {
        opacity: { kind: 'literal', value: 0.5 },
        width: { kind: 'binding', variableId: 'VariableID:width' },
        fills: { kind: 'binding-list', variableIds: ['VariableID:fill'] },
        text: { kind: 'binding-list', variableIds: ['VariableID:text-1', 'VariableID:text-2'] },
        componentProperties: {
          kind: 'component-properties',
          properties: { 'Icon#123': { kind: 'binding', variableId: 'VariableID:icon' } },
        },
      },
    }],
  });
});

test('prototype snapshots support legacy action and conditional nested destinations', async () => {
  const legacy = await withFigma({
    currentPage: { selection: [{ id: 'legacy', type: 'FRAME', name: 'Legacy', reactions: [{ action: { destinationId: 'known' } }] }] },
    async getNodeByIdAsync(nodeId: string) { return nodeId === 'known' ? { id: 'known', type: 'FRAME', name: 'Known' } : null; },
  }, () => previewPlan(JSON.stringify({
    version: 1, mode: 'preview', operation: 'audit-prototype-links', scope: { kind: 'selection' },
  }), new FigmaNodePort()));
  assert.deepEqual(legacy, { status: 'clean', findings: [] });

  const conditional = await withFigma({
    currentPage: { selection: [{
      id: 'conditional', type: 'FRAME', name: 'Conditional',
      reactions: [{ actions: [{ type: 'CONDITIONAL', conditionalBlocks: [{ actions: [{ destinationId: 'missing' }] }] }] }],
    }] },
    async getNodeByIdAsync() { return null; },
  }, () => previewPlan(JSON.stringify({
    version: 1, mode: 'preview', operation: 'audit-prototype-links', scope: { kind: 'selection' },
  }), new FigmaNodePort()));
  assert.deepEqual(conditional, {
    status: 'findings',
    findings: [{ code: 'PROTOTYPE_DESTINATION_MISSING', nodeId: 'conditional', observed: { destinationId: 'missing' } }],
  });
});
