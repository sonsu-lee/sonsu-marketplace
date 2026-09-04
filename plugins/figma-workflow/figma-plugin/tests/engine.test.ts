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

test('invalid JSON returns INVALID_JSON', () => {
  assert.deepEqual(parsePlan('{'), { status: 'invalid', reason: 'INVALID_JSON' });
});

test('preview rejects a mutation plan in apply mode without reading a node', async () => {
  const result = await previewPlan(JSON.stringify({
    version: 1,
    mode: 'apply',
    operation: 'rename-exact',
    targets: [{ nodeId: 'node-1', expectedName: 'Before', newName: 'After' }],
  }), {
    async readNode() { throw new Error('must not read'); },
  });

  assert.deepEqual(result, { status: 'invalid', reason: 'INVALID_FIELD' });
});

test('rename preview keeps later targets when an earlier lookup fails', async () => {
  const result = await previewPlan(JSON.stringify({
    version: 1,
    mode: 'preview',
    operation: 'rename-exact',
    targets: [
      { nodeId: 'broken', expectedName: 'Before', newName: 'After' },
      { nodeId: 'ready', expectedName: 'Before', newName: 'After' },
    ],
  }), {
    async readNode(nodeId: string) {
      if (nodeId === 'broken') throw new Error('lookup broke');
      return { id: 'ready', type: 'RECTANGLE', name: 'Before' };
    },
  });

  assert.deepEqual(result, {
    status: 'partial',
    results: [
      { nodeId: 'broken', status: 'failed', reason: 'LOOKUP_FAILED' },
      { nodeId: 'ready', status: 'ready', reason: 'READY', before: { name: 'Before' }, after: { name: 'After' } },
    ],
    receipt: {
      fingerprint: '{"operation":"rename-exact","targets":[{"expectedName":"Before","newName":"After","nodeId":"broken"},{"expectedName":"Before","newName":"After","nodeId":"ready"}]}',
      targets: [
        { nodeId: 'broken', expectedName: 'Before', disposition: 'LOOKUP_FAILED' },
        { nodeId: 'ready', expectedName: 'Before', observedName: 'Before', disposition: 'READY' },
      ],
    },
  });
});

test('preview with only lookup failures reports failed', async () => {
  const result = await previewPlan(JSON.stringify({
    version: 1,
    mode: 'preview',
    operation: 'rename-exact',
    targets: [{ nodeId: 'broken', expectedName: 'Before', newName: 'After' }],
  }), {
    async readNode() { throw new Error('lookup broke'); },
  });

  assert.deepEqual(result, {
    status: 'failed',
    results: [{ nodeId: 'broken', status: 'failed', reason: 'LOOKUP_FAILED' }],
    receipt: {
      fingerprint: '{"operation":"rename-exact","targets":[{"expectedName":"Before","newName":"After","nodeId":"broken"}]}',
      targets: [{ nodeId: 'broken', expectedName: 'Before', disposition: 'LOOKUP_FAILED' }],
    },
  });
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
      targets: [{ nodeId: 'node-1', expectedName: 'Before', observedName: 'Before', disposition: 'READY' }],
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
      targets: [{ nodeId: 'node-1', expectedName: 'Before', observedName: 'After', disposition: 'ALREADY_DESIRED' }],
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
      targets: [{ nodeId: 'node-1', expectedName: 'Before', observedName: 'Changed externally', disposition: 'STALE_EXPECTED_STATE' }],
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
      targets: [{ nodeId: 'icon-1', expectedMainComponentKey: 'old-key', observedMainComponentKey: 'old-key', disposition: 'WRONG_NODE_TYPE' }],
    },
  });
  assert.deepEqual(staleKey, {
    status: 'no_changes',
    results: [{ nodeId: 'icon-1', status: 'skipped', reason: 'STALE_EXPECTED_STATE' }],
    receipt: {
      fingerprint: '{"operation":"replace-icon-instance-exact","targets":[{"expectedMainComponentKey":"old-key","nodeId":"icon-1","replacementComponentKey":"new-key"}]}',
      targets: [{ nodeId: 'icon-1', expectedMainComponentKey: 'old-key', observedMainComponentKey: 'other-key', disposition: 'STALE_EXPECTED_STATE' }],
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
    async renameIfCurrent(nodeId: string, expectedName: string, name: string) {
      if (!nodes[nodeId]) return 'missing';
      if (nodes[nodeId].name !== expectedName) return 'stale';
      nodes[nodeId].name = name;
      return 'applied';
    },
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
    async renameIfCurrent(nodeId: string, expectedName: string, name: string) {
      if (!nodes[nodeId]) return 'missing';
      if (nodes[nodeId].name !== expectedName) return 'stale';
      nodes[nodeId].name = name;
      return 'applied';
    },
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
    async renameIfCurrent(nodeId: string, expectedName: string, name: string) {
      if (nodeId === 'mutation') throw new Error('mutation broke');
      if (!nodes[nodeId]) return 'missing';
      if (nodes[nodeId].name !== expectedName) return 'stale';
      nodes[nodeId].name = name;
      return 'applied';
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

test('auto-layout audit treats a GRID parent as an Auto Layout parent for ABSOLUTE children', async () => {
  const result = await previewPlan(JSON.stringify({
    version: 1, mode: 'preview', operation: 'audit-auto-layout', scope: { kind: 'selection' },
  }), {
    async readNode() { return null; },
    async getSelection() {
      return [{
        id: 'grid', type: 'FRAME', name: 'Grid', layoutMode: 'GRID',
        children: [{ id: 'absolute', type: 'RECTANGLE', name: 'Absolute', layoutPositioning: 'ABSOLUTE' }],
      }];
    },
  });

  assert.deepEqual(result, { status: 'clean', findings: [] });
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
    async renameIfCurrent() { return 'applied'; /* Figma accepted the request but state did not change. */ },
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
    async replaceIconInstanceIfCurrent() { return 'applied'; /* Mutation request completed but readback stays old. */ },
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

test('rename preview records MISSING_NODE as its target disposition', async () => {
  const result = await previewPlan(JSON.stringify({
    version: 1, mode: 'preview', operation: 'rename-exact',
    targets: [{ nodeId: 'gone', expectedName: 'Before', newName: 'After' }],
  }), new MemoryPort({}));

  assert.deepEqual(result, {
    status: 'no_changes',
    results: [{ nodeId: 'gone', status: 'skipped', reason: 'MISSING_NODE' }],
    receipt: {
      fingerprint: '{"operation":"rename-exact","targets":[{"expectedName":"Before","newName":"After","nodeId":"gone"}]}',
      targets: [{ nodeId: 'gone', expectedName: 'Before', disposition: 'MISSING_NODE' }],
    },
  });
});

test('apply only reads and mutates targets whose preview disposition was READY', async () => {
  const previewText = JSON.stringify({
    version: 1, mode: 'preview', operation: 'rename-exact',
    targets: [
      { nodeId: 'gone', expectedName: 'Before', newName: 'After' },
      { nodeId: 'ready', expectedName: 'Before', newName: 'After' },
    ],
  });
  const applyText = previewText.replace('"preview"', '"apply"');
  const node = { id: 'ready', type: 'RECTANGLE', name: 'Before' };
  let phase: 'preview' | 'apply' = 'preview';
  const port = {
    async readNode(nodeId: string) {
      if (phase === 'apply' && nodeId === 'gone') throw new Error('skipped target was read');
      return nodeId === 'ready' ? node : null;
    },
    async renameIfCurrent(nodeId: string, expectedName: string, name: string) {
      assert.equal(nodeId, 'ready');
      assert.equal(node.name, expectedName);
      node.name = name;
      return 'applied';
    },
  };
  const preview = await previewPlan(previewText, port) as { receipt: unknown };
  phase = 'apply';

  const result = await applyPlan(applyText, preview.receipt, port);

  assert.deepEqual(result, {
    status: 'partial',
    results: [
      { nodeId: 'gone', status: 'skipped', reason: 'PREVIEW_NOT_READY' },
      { nodeId: 'ready', status: 'applied', reason: 'READY', before: { name: 'Before' }, after: { name: 'After' } },
    ],
  });
});

test('apply honors a receipt disposition changed from READY without reading the target', async () => {
  const previewText = JSON.stringify({
    version: 1, mode: 'preview', operation: 'rename-exact',
    targets: [{ nodeId: 'ready', expectedName: 'Before', newName: 'After' }],
  });
  const applyText = previewText.replace('"preview"', '"apply"');
  let phase: 'preview' | 'apply' = 'preview';
  const port = {
    async readNode() {
      if (phase === 'apply') throw new Error('receipt-skipped target was read');
      return { id: 'ready', type: 'RECTANGLE', name: 'Before' };
    },
    async renameIfCurrent() { throw new Error('receipt-skipped target was mutated'); },
  };
  const preview = await previewPlan(previewText, port) as {
    receipt: { targets: Array<Record<string, unknown>> };
  };
  preview.receipt.targets[0].disposition = 'STALE_EXPECTED_STATE';
  phase = 'apply';

  const result = await applyPlan(applyText, preview.receipt, port);

  assert.deepEqual(result, {
    status: 'no_changes',
    results: [{ nodeId: 'ready', status: 'skipped', reason: 'PREVIEW_NOT_READY' }],
  });
});

test('apply with no preview-ready targets skips without reading or mutating', async () => {
  const previewText = JSON.stringify({
    version: 1, mode: 'preview', operation: 'rename-exact',
    targets: [{ nodeId: 'gone', expectedName: 'Before', newName: 'After' }],
  });
  const applyText = previewText.replace('"preview"', '"apply"');
  let phase: 'preview' | 'apply' = 'preview';
  const port = {
    async readNode() {
      if (phase === 'apply') throw new Error('all-skipped target was read');
      return null;
    },
    async renameIfCurrent() { throw new Error('all-skipped target was mutated'); },
  };
  const preview = await previewPlan(previewText, port) as { receipt: unknown };
  phase = 'apply';

  const result = await applyPlan(applyText, preview.receipt, port);

  assert.deepEqual(result, {
    status: 'no_changes',
    results: [{ nodeId: 'gone', status: 'skipped', reason: 'PREVIEW_NOT_READY' }],
  });
});

test('icon apply reports a successful replacement after readback', async () => {
  const previewText = JSON.stringify({
    version: 1, mode: 'preview', operation: 'replace-icon-instance-exact',
    targets: [{ nodeId: 'icon', expectedMainComponentKey: 'old', replacementComponentKey: 'new' }],
  });
  const applyText = previewText.replace('"preview"', '"apply"');
  const node = { id: 'icon', type: 'INSTANCE', name: 'Icon', mainComponentKey: 'old' };
  const port = {
    async readNode() { return node; },
    async importComponent(key: string) { return { key }; },
    async replaceIconInstanceIfCurrent(_nodeId: string, expectedKey: string, component: { key: string }) {
      if (node.mainComponentKey !== expectedKey) return 'stale';
      node.mainComponentKey = component.key;
      return 'applied';
    },
  };
  const preview = await previewPlan(previewText, port) as { receipt: unknown };

  const result = await applyPlan(applyText, preview.receipt, port);

  assert.deepEqual(result, {
    status: 'applied',
    results: [{
      nodeId: 'icon', status: 'applied', reason: 'READY',
      before: { mainComponentKey: 'old' }, after: { mainComponentKey: 'new' },
    }],
  });
});

test('rename apply skips when the adapter rejects a stale final precondition', async () => {
  const previewText = JSON.stringify({
    version: 1, mode: 'preview', operation: 'rename-exact',
    targets: [{ nodeId: 'node', expectedName: 'A', newName: 'B' }],
  });
  const applyText = previewText.replace('"preview"', '"apply"');
  const node = { id: 'node', type: 'RECTANGLE', name: 'A' };
  const port = {
    async readNode() { return node; },
    async renameIfCurrent() { node.name = 'C'; return 'stale'; },
  };
  const preview = await previewPlan(previewText, port) as { receipt: unknown };
  const result = await applyPlan(applyText, preview.receipt, port);

  assert.deepEqual(result, {
    status: 'no_changes',
    results: [{ nodeId: 'node', status: 'skipped', reason: 'STALE_EXPECTED_STATE' }],
  });
  assert.equal(node.name, 'C');
});

test('icon apply skips when state changes during component import', async () => {
  const previewText = JSON.stringify({
    version: 1, mode: 'preview', operation: 'replace-icon-instance-exact',
    targets: [{ nodeId: 'icon', expectedMainComponentKey: 'A', replacementComponentKey: 'B' }],
  });
  const applyText = previewText.replace('"preview"', '"apply"');
  const node = { id: 'icon', type: 'INSTANCE', name: 'Icon', mainComponentKey: 'A' };
  const port = {
    async readNode() { return node; },
    async importComponent() { node.mainComponentKey = 'C'; return { key: 'B' }; },
    async replaceIconInstanceIfCurrent() {
      return node.mainComponentKey === 'A' ? 'applied' : 'stale';
    },
  };
  const preview = await previewPlan(previewText, port) as { receipt: unknown };
  const result = await applyPlan(applyText, preview.receipt, port);

  assert.deepEqual(result, {
    status: 'no_changes',
    results: [{ nodeId: 'icon', status: 'skipped', reason: 'STALE_EXPECTED_STATE' }],
  });
  assert.equal(node.mainComponentKey, 'C');
});

test('apply classifies a final conditional lookup failure without mutating', async () => {
  const previewText = JSON.stringify({
    version: 1, mode: 'preview', operation: 'rename-exact',
    targets: [{ nodeId: 'node', expectedName: 'A', newName: 'B' }],
  });
  const applyText = previewText.replace('"preview"', '"apply"');
  const node = { id: 'node', type: 'RECTANGLE', name: 'A' };
  const port = {
    async readNode() { return node; },
    async renameIfCurrent() { return 'lookup_failed'; },
  };
  const preview = await previewPlan(previewText, port) as { receipt: unknown };
  const result = await applyPlan(applyText, preview.receipt, port);

  assert.deepEqual(result, {
    status: 'failed',
    results: [{ nodeId: 'node', status: 'failed', reason: 'LOOKUP_FAILED' }],
  });
  assert.equal(node.name, 'A');
});

test('auto-layout audit returns clean when every checked node has an Auto Layout parent', async () => {
  const result = await previewPlan(JSON.stringify({
    version: 1, mode: 'preview', operation: 'audit-auto-layout', scope: { kind: 'selection' },
  }), {
    async getSelection() {
      return [{
        id: 'root', type: 'FRAME', name: 'Root', layoutMode: 'VERTICAL',
        children: [{ id: 'fill', type: 'RECTANGLE', name: 'Fill', layoutSizingHorizontal: 'FILL' }],
      }];
    },
    async readNode() { return null; },
  });

  assert.deepEqual(result, { status: 'clean', findings: [] });
});
