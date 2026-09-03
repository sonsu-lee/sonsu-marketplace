import assert from 'node:assert/strict';
import test from 'node:test';

import * as engine from '../src/engine.js';

const { parsePlan } = engine;
const previewPlan = (engine as unknown as {
  previewPlan: (text: string, port: unknown) => Promise<unknown>;
}).previewPlan;
const applyPlan = (engine as unknown as {
  applyPlan: (text: string, receipt: unknown, port: unknown) => Promise<unknown>;
}).applyPlan;

class MemoryPort {
  constructor(private readonly nodes: Record<string, Record<string, unknown>>) {}

  async readNode(nodeId: string): Promise<Record<string, unknown> | null> {
    return this.nodes[nodeId] ?? null;
  }
}

test('unsupported plan version returns UNSUPPORTED_VERSION', () => {
  const result = parsePlan(JSON.stringify({
    version: 2,
    mode: 'preview',
    operation: 'inspect-selection',
    scope: { kind: 'selection' },
  }));

  assert.deepEqual(result, { status: 'invalid', reason: 'UNSUPPORTED_VERSION' });
});

test('unknown operation returns UNKNOWN_OPERATION', () => {
  const result = parsePlan(JSON.stringify({
    version: 1,
    mode: 'preview',
    operation: 'delete-everything',
  }));

  assert.deepEqual(result, { status: 'invalid', reason: 'UNKNOWN_OPERATION' });
});

test('unknown fields return UNKNOWN_FIELD', () => {
  const result = parsePlan(JSON.stringify({
    version: 1,
    mode: 'preview',
    operation: 'inspect-selection',
    scope: { kind: 'selection', extra: true },
  }));

  assert.deepEqual(result, { status: 'invalid', reason: 'UNKNOWN_FIELD' });
});

test('malformed mutation targets return INVALID_FIELD', () => {
  const result = parsePlan(JSON.stringify({
    version: 1,
    mode: 'preview',
    operation: 'rename-exact',
    targets: [{ nodeId: 'node-1', expectedName: 'before', newName: 'before' }],
  }));

  assert.deepEqual(result, { status: 'invalid', reason: 'INVALID_FIELD' });
});

test('duplicate mutation targets return DUPLICATE_TARGET', () => {
  const result = parsePlan(JSON.stringify({
    version: 1,
    mode: 'preview',
    operation: 'rename-exact',
    targets: [
      { nodeId: 'node-1', expectedName: 'before', newName: 'after' },
      { nodeId: 'node-1', expectedName: 'another', newName: 'after-again' },
    ],
  }));

  assert.deepEqual(result, { status: 'invalid', reason: 'DUPLICATE_TARGET' });
});

test('read-only operations reject apply mode with INVALID_FIELD', () => {
  const result = parsePlan(JSON.stringify({
    version: 1,
    mode: 'apply',
    operation: 'inspect-selection',
    scope: { kind: 'selection' },
  }));

  assert.deepEqual(result, { status: 'invalid', reason: 'INVALID_FIELD' });
});

test('rename preview marks a matching node READY', async () => {
  const result = await previewPlan(JSON.stringify({
    version: 1,
    mode: 'preview',
    operation: 'rename-exact',
    targets: [{ nodeId: 'node-1', expectedName: 'Before', newName: 'After' }],
  }), new MemoryPort({ 'node-1': { id: 'node-1', type: 'RECTANGLE', name: 'Before' } }));

  assert.deepEqual(result, {
    status: 'ready',
    results: [{
      nodeId: 'node-1',
      status: 'ready',
      reason: 'READY',
      before: { name: 'Before' },
      after: { name: 'After' },
    }],
    receipt: {
      fingerprint: '{"operation":"rename-exact","targets":[{"expectedName":"Before","newName":"After","nodeId":"node-1"}]}',
      targets: [{ nodeId: 'node-1', expectedName: 'Before', observedName: 'Before' }],
    },
  });
});

test('rename preview marks an already renamed node ALREADY_DESIRED', async () => {
  const result = await previewPlan(JSON.stringify({
    version: 1,
    mode: 'preview',
    operation: 'rename-exact',
    targets: [{ nodeId: 'node-1', expectedName: 'Before', newName: 'After' }],
  }), new MemoryPort({ 'node-1': { id: 'node-1', type: 'RECTANGLE', name: 'After' } }));

  assert.deepEqual(result, {
    status: 'no_changes',
    results: [{ nodeId: 'node-1', status: 'skipped', reason: 'ALREADY_DESIRED' }],
    receipt: {
      fingerprint: '{"operation":"rename-exact","targets":[{"expectedName":"Before","newName":"After","nodeId":"node-1"}]}',
      targets: [{ nodeId: 'node-1', expectedName: 'Before', observedName: 'After' }],
    },
  });
});

test('rename preview marks a mismatched expected name STALE_EXPECTED_STATE', async () => {
  const result = await previewPlan(JSON.stringify({
    version: 1,
    mode: 'preview',
    operation: 'rename-exact',
    targets: [{ nodeId: 'node-1', expectedName: 'Before', newName: 'After' }],
  }), new MemoryPort({ 'node-1': { id: 'node-1', type: 'RECTANGLE', name: 'Changed externally' } }));

  assert.deepEqual(result, {
    status: 'no_changes',
    results: [{ nodeId: 'node-1', status: 'skipped', reason: 'STALE_EXPECTED_STATE' }],
    receipt: {
      fingerprint: '{"operation":"rename-exact","targets":[{"expectedName":"Before","newName":"After","nodeId":"node-1"}]}',
      targets: [{ nodeId: 'node-1', expectedName: 'Before', observedName: 'Changed externally' }],
    },
  });
});

test('icon preview requires an INSTANCE with the expected component key', async () => {
  const plan = JSON.stringify({
    version: 1,
    mode: 'preview',
    operation: 'replace-icon-instance-exact',
    targets: [{ nodeId: 'icon-1', expectedMainComponentKey: 'old-key', replacementComponentKey: 'new-key' }],
  });

  const wrongType = await previewPlan(plan, new MemoryPort({
    'icon-1': { id: 'icon-1', type: 'RECTANGLE', name: 'Icon', mainComponentKey: 'old-key' },
  }));
  const staleKey = await previewPlan(plan, new MemoryPort({
    'icon-1': { id: 'icon-1', type: 'INSTANCE', name: 'Icon', mainComponentKey: 'other-key' },
  }));

  assert.deepEqual(wrongType, {
    status: 'no_changes',
    results: [{ nodeId: 'icon-1', status: 'skipped', reason: 'WRONG_NODE_TYPE' }],
    receipt: {
      fingerprint: '{"operation":"replace-icon-instance-exact","targets":[{"expectedMainComponentKey":"old-key","nodeId":"icon-1","replacementComponentKey":"new-key"}]}',
      targets: [{ nodeId: 'icon-1', expectedMainComponentKey: 'old-key', observedMainComponentKey: 'old-key' }],
    },
  });
  assert.deepEqual(staleKey, {
    status: 'no_changes',
    results: [{ nodeId: 'icon-1', status: 'skipped', reason: 'STALE_EXPECTED_STATE' }],
    receipt: {
      fingerprint: '{"operation":"replace-icon-instance-exact","targets":[{"expectedMainComponentKey":"old-key","nodeId":"icon-1","replacementComponentKey":"new-key"}]}',
      targets: [{ nodeId: 'icon-1', expectedMainComponentKey: 'old-key', observedMainComponentKey: 'other-key' }],
    },
  });
});

test('icon preview marks a replacement component already present ALREADY_DESIRED', async () => {
  const result = await previewPlan(JSON.stringify({
    version: 1,
    mode: 'preview',
    operation: 'replace-icon-instance-exact',
    targets: [{ nodeId: 'icon-1', expectedMainComponentKey: 'old-key', replacementComponentKey: 'new-key' }],
  }), new MemoryPort({
    'icon-1': { id: 'icon-1', type: 'INSTANCE', name: 'Icon', mainComponentKey: 'new-key' },
  }));

  assert.equal((result as { status: string }).status, 'no_changes');
  assert.deepEqual((result as { results: unknown[] }).results, [
    { nodeId: 'icon-1', status: 'skipped', reason: 'ALREADY_DESIRED' },
  ]);
});

test('apply requires the matching preview receipt and verifies a rename by readback', async () => {
  const previewText = JSON.stringify({
    version: 1, mode: 'preview', operation: 'rename-exact',
    targets: [{ nodeId: 'node-1', expectedName: 'Before', newName: 'After' }],
  });
  const applyText = JSON.stringify({
    version: 1, mode: 'apply', operation: 'rename-exact',
    targets: [{ nodeId: 'node-1', expectedName: 'Before', newName: 'After' }],
  });
  const nodes: Record<string, Record<string, unknown>> = {
    'node-1': { id: 'node-1', type: 'RECTANGLE', name: 'Before' },
  };
  const port = {
    async readNode(nodeId: string) { return nodes[nodeId] ?? null; },
    async rename(nodeId: string, name: string) { nodes[nodeId].name = name; },
  };
  const preview = await previewPlan(previewText, port) as { receipt: unknown };

  const missingReceipt = await applyPlan(applyText, undefined, port);
  const changedPlan = await applyPlan(JSON.stringify({
    version: 1, mode: 'apply', operation: 'rename-exact',
    targets: [{ nodeId: 'node-1', expectedName: 'Before', newName: 'Other' }],
  }), preview.receipt, port);
  const applied = await applyPlan(applyText, preview.receipt, port);

  assert.deepEqual(missingReceipt, { status: 'invalid', reason: 'PREVIEW_REQUIRED' });
  assert.deepEqual(changedPlan, { status: 'invalid', reason: 'PLAN_CHANGED' });
  assert.deepEqual(applied, {
    status: 'applied',
    results: [{ nodeId: 'node-1', status: 'applied', reason: 'READY', before: { name: 'Before' }, after: { name: 'After' } }],
  });
});

test('apply re-reads each target and continues after stale and missing nodes', async () => {
  const previewText = JSON.stringify({
    version: 1, mode: 'preview', operation: 'rename-exact',
    targets: [
      { nodeId: 'first', expectedName: 'Before', newName: 'After' },
      { nodeId: 'stale', expectedName: 'Before', newName: 'After' },
      { nodeId: 'gone', expectedName: 'Before', newName: 'After' },
    ],
  });
  const applyText = previewText.replace('"preview"', '"apply"');
  const nodes: Record<string, Record<string, unknown>> = {
    first: { id: 'first', type: 'RECTANGLE', name: 'Before' },
    stale: { id: 'stale', type: 'RECTANGLE', name: 'Before' },
    gone: { id: 'gone', type: 'RECTANGLE', name: 'Before' },
  };
  const port = {
    async readNode(nodeId: string) { return nodes[nodeId] ?? null; },
    async rename(nodeId: string, name: string) { nodes[nodeId].name = name; },
  };
  const preview = await previewPlan(previewText, port) as { receipt: unknown };
  nodes.stale.name = 'Changed externally';
  delete nodes.gone;

  const result = await applyPlan(applyText, preview.receipt, port);

  assert.deepEqual(result, {
    status: 'partial',
    results: [
      { nodeId: 'first', status: 'applied', reason: 'READY', before: { name: 'Before' }, after: { name: 'After' } },
      { nodeId: 'stale', status: 'skipped', reason: 'STALE_EXPECTED_STATE' },
      { nodeId: 'gone', status: 'skipped', reason: 'MISSING_NODE' },
    ],
  });
});

test('apply isolates lookup, mutation and readback failures per target', async () => {
  const previewText = JSON.stringify({
    version: 1, mode: 'preview', operation: 'rename-exact',
    targets: [
      { nodeId: 'lookup', expectedName: 'Before', newName: 'After' },
      { nodeId: 'mutation', expectedName: 'Before', newName: 'After' },
      { nodeId: 'readback', expectedName: 'Before', newName: 'After' },
      { nodeId: 'success', expectedName: 'Before', newName: 'After' },
    ],
  });
  const applyText = previewText.replace('"preview"', '"apply"');
  const nodes: Record<string, Record<string, unknown>> = Object.fromEntries(
    ['lookup', 'mutation', 'readback', 'success'].map((id) => [id, { id, type: 'RECTANGLE', name: 'Before' }]),
  );
  let phase: 'preview' | 'apply' = 'preview';
  const port = {
    async readNode(nodeId: string) {
      if (phase === 'apply' && nodeId === 'lookup') throw new Error('lookup broke');
      if (phase === 'apply' && nodeId === 'readback' && nodes[nodeId].name === 'After') throw new Error('readback broke');
      return nodes[nodeId] ?? null;
    },
    async rename(nodeId: string, name: string) {
      if (nodeId === 'mutation') throw new Error('mutation broke');
      nodes[nodeId].name = name;
    },
  };
  const preview = await previewPlan(previewText, port) as { receipt: unknown };
  phase = 'apply';

  const result = await applyPlan(applyText, preview.receipt, port);

  assert.deepEqual(result, {
    status: 'partial',
    results: [
      { nodeId: 'lookup', status: 'failed', reason: 'LOOKUP_FAILED' },
      { nodeId: 'mutation', status: 'failed', reason: 'MUTATION_FAILED' },
      { nodeId: 'readback', status: 'failed', reason: 'READBACK_FAILED' },
      { nodeId: 'success', status: 'applied', reason: 'READY', before: { name: 'Before' }, after: { name: 'After' } },
    ],
  });
});

test('inspection rejects an empty selection and inventories a non-empty selection', async () => {
  const text = JSON.stringify({
    version: 1, mode: 'preview', operation: 'inspect-selection', scope: { kind: 'selection' },
  });
  const empty = await previewPlan(text, {
    async readNode() { return null; },
    async getSelection() { return []; },
  });
  const inspected = await previewPlan(text, {
    async readNode() { return null; },
    async getSelection() { return [{ id: 'frame-1', type: 'FRAME', name: 'Card', layoutMode: 'VERTICAL' }]; },
  });

  assert.deepEqual(empty, { status: 'invalid', reason: 'INVALID_FIELD' });
  assert.deepEqual(inspected, {
    status: 'inspected',
    nodes: [{ id: 'frame-1', type: 'FRAME', name: 'Card', layoutMode: 'VERTICAL' }],
  });
});

test('auto-layout audit reports FILL and ABSOLUTE nodes without an Auto Layout parent', async () => {
  const result = await previewPlan(JSON.stringify({
    version: 1, mode: 'preview', operation: 'audit-auto-layout', scope: { kind: 'selection' },
  }), {
    async readNode() { return null; },
    async getSelection() {
      return [{
        id: 'root', type: 'FRAME', name: 'Root', layoutMode: 'NONE',
        children: [
          { id: 'fill', type: 'RECTANGLE', name: 'Fill', layoutSizingHorizontal: 'FILL' },
          { id: 'absolute', type: 'RECTANGLE', name: 'Absolute', layoutPositioning: 'ABSOLUTE' },
        ],
      }];
    },
  });

  assert.deepEqual(result, {
    status: 'findings',
    findings: [
      { code: 'AUTO_LAYOUT_FILL_WITHOUT_AUTO_PARENT', nodeId: 'fill', observed: { layoutSizingHorizontal: 'FILL', parentLayoutMode: 'NONE' } },
      { code: 'AUTO_LAYOUT_ABSOLUTE_WITHOUT_AUTO_PARENT', nodeId: 'absolute', observed: { layoutPositioning: 'ABSOLUTE', parentLayoutMode: 'NONE' } },
    ],
  });
});

test('prototype audit reports empty actions and unresolved destinations', async () => {
  const result = await previewPlan(JSON.stringify({
    version: 1, mode: 'preview', operation: 'audit-prototype-links', scope: { kind: 'selection' },
  }), {
    async readNode(nodeId: string) { return nodeId === 'known' ? { id: 'known', type: 'FRAME', name: 'Known' } : null; },
    async getSelection() {
      return [{
        id: 'screen-1', type: 'FRAME', name: 'Screen',
        reactions: [{ actions: [] }, { actions: [{ destinationId: 'missing' }, { destinationId: 'known' }] }],
      }];
    },
  });

  assert.deepEqual(result, {
    status: 'findings',
    findings: [
      { code: 'PROTOTYPE_EMPTY_ACTIONS', nodeId: 'screen-1', observed: { reactionIndex: '0' } },
      { code: 'PROTOTYPE_DESTINATION_MISSING', nodeId: 'screen-1', observed: { destinationId: 'missing' } },
    ],
  });
});

test('apply reports READBACK_MISMATCH when a successful mutation cannot be observed', async () => {
  const previewText = JSON.stringify({
    version: 1, mode: 'preview', operation: 'rename-exact',
    targets: [{ nodeId: 'node-1', expectedName: 'Before', newName: 'After' }],
  });
  const applyText = previewText.replace('"preview"', '"apply"');
  const node = { id: 'node-1', type: 'RECTANGLE', name: 'Before' };
  const port = {
    async readNode() { return node; },
    async rename() { /* Figma accepted the request but state did not change. */ },
  };
  const preview = await previewPlan(previewText, port) as { receipt: unknown };

  const result = await applyPlan(applyText, preview.receipt, port);

  assert.deepEqual(result, {
    status: 'failed',
    results: [{ nodeId: 'node-1', status: 'failed', reason: 'READBACK_MISMATCH', observed: { name: 'Before' } }],
  });
});

test('icon apply classifies import and icon readback errors without rollback', async () => {
  const previewText = JSON.stringify({
    version: 1, mode: 'preview', operation: 'replace-icon-instance-exact',
    targets: [
      { nodeId: 'import', expectedMainComponentKey: 'old', replacementComponentKey: 'new' },
      { nodeId: 'mismatch', expectedMainComponentKey: 'old', replacementComponentKey: 'new' },
    ],
  });
  const applyText = previewText.replace('"preview"', '"apply"');
  const nodes: Record<string, { id: string; type: string; name: string; mainComponentKey: string }> = {
    import: { id: 'import', type: 'INSTANCE', name: 'Import', mainComponentKey: 'old' },
    mismatch: { id: 'mismatch', type: 'INSTANCE', name: 'Mismatch', mainComponentKey: 'old' },
  };
  const port = {
    async readNode(nodeId: string) { return nodes[nodeId] ?? null; },
    async importComponent(key: string) {
      if (key === 'new' && !('imported' in nodes)) {
        (nodes as Record<string, unknown>).imported = true;
        throw new Error('import failed');
      }
      return { key };
    },
    async replaceIconInstance() { /* Mutation request completed but readback stays old. */ },
  };
  const preview = await previewPlan(previewText, port) as { receipt: unknown };

  const result = await applyPlan(applyText, preview.receipt, port);

  assert.deepEqual(result, {
    status: 'failed',
    results: [
      { nodeId: 'import', status: 'failed', reason: 'IMPORT_FAILED' },
      { nodeId: 'mismatch', status: 'failed', reason: 'READBACK_MISMATCH', observed: { mainComponentKey: 'old' } },
    ],
  });
});
