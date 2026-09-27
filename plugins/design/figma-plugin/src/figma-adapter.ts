import type { NormalizedNodeSnapshot, NormalizedVariableBinding } from './contracts.js';
import type { ConditionalMutationResult, NodePort } from './ports.js';

type NodeWithName = BaseNode & { name: string };
type NodeWithChildren = BaseNode & { children: readonly BaseNode[] };
type NodeWithLayout = BaseNode & {
  layoutMode?: string;
  layoutSizingHorizontal?: string;
  layoutSizingVertical?: string;
  layoutPositioning?: string;
};
type NodeWithReactions = BaseNode & { reactions?: readonly unknown[] };
type NodeWithParent = BaseNode & { parent: BaseNode | null };
type NodeWithVariables = BaseNode & { opacity?: unknown; boundVariables?: unknown };

const asRecord = (value: unknown): Record<string, unknown> | undefined =>
  typeof value === 'object' && value !== null ? value as Record<string, unknown> : undefined;

type NormalizedAction = { type?: string; destinationId?: string | null };

function snapshotAction(action: unknown): NormalizedAction | undefined {
  const record = asRecord(action);
  if (!record) return undefined;
  const snapshot: NormalizedAction = {};
  if (typeof record.type === 'string') snapshot.type = record.type;
  if (record.destinationId === null || typeof record.destinationId === 'string') {
    snapshot.destinationId = record.destinationId;
  }
  return snapshot;
}

function snapshotActions(action: unknown): NormalizedAction[] {
  const record = asRecord(action);
  if (!record) return [];
  const actions: NormalizedAction[] = [snapshotAction(action) ?? {}];
  const conditionalBlocks = record.conditionalBlocks;
  if (!Array.isArray(conditionalBlocks)) return actions;
  for (const block of conditionalBlocks) {
    const nestedActions = asRecord(block)?.actions;
    if (!Array.isArray(nestedActions)) continue;
    for (const nestedAction of nestedActions) actions.push(...snapshotActions(nestedAction));
  }
  return actions;
}

function snapshotReactionActions(reaction: unknown): NormalizedAction[] | undefined {
  const record = asRecord(reaction);
  if (!record) return undefined;
  const actions = Array.isArray(record.actions)
    ? record.actions
    : record.action === undefined ? undefined : [record.action];
  return actions?.flatMap(snapshotActions);
}

function snapshotParent(parent: BaseNode): NonNullable<NormalizedNodeSnapshot['parent']> {
  const layoutMode = (parent as NodeWithLayout).layoutMode;
  return typeof layoutMode === 'string'
    ? { id: parent.id, type: parent.type, layoutMode }
    : { id: parent.id, type: parent.type };
}

function normalizeVariableAlias(value: unknown): string | undefined {
  const alias = asRecord(value);
  return alias?.type === 'VARIABLE_ALIAS' && typeof alias.id === 'string' ? alias.id : undefined;
}

function normalizeVariableBinding(value: unknown): NormalizedVariableBinding | undefined {
  const alias = normalizeVariableAlias(value);
  if (alias) return { kind: 'binding', variableId: alias };
  if (!Array.isArray(value)) return undefined;
  const variableIds = value.map(normalizeVariableAlias).filter((id): id is string => id !== undefined);
  return variableIds.length > 0 ? { kind: 'binding-list', variableIds } : undefined;
}

function snapshotVariableBindings(node: BaseNode): Record<string, NormalizedVariableBinding> | undefined {
  const variableNode = node as NodeWithVariables;
  const bindings: Record<string, NormalizedVariableBinding> = {};
  if (typeof variableNode.opacity === 'number' && Number.isFinite(variableNode.opacity)) {
    bindings.opacity = { kind: 'literal', value: variableNode.opacity };
  }
  const boundVariables = asRecord(variableNode.boundVariables);
  if (!boundVariables) return Object.keys(bindings).length > 0 ? bindings : undefined;
  for (const [field, value] of Object.entries(boundVariables)) {
    const componentProperties = asRecord(value);
    if (field === 'componentProperties' && componentProperties) {
      const properties: Record<string, NormalizedVariableBinding> = {};
      for (const [propertyName, propertyValue] of Object.entries(componentProperties)) {
        const normalized = normalizeVariableBinding(propertyValue);
        if (normalized) properties[propertyName] = normalized;
      }
      if (Object.keys(properties).length > 0) {
        bindings.componentProperties = { kind: 'component-properties', properties };
      }
      continue;
    }
    const normalized = normalizeVariableBinding(value);
    if (normalized) bindings[field] = normalized;
  }
  return Object.keys(bindings).length > 0 ? bindings : undefined;
}

async function snapshotNodeShallow(node: BaseNode): Promise<NormalizedNodeSnapshot> {
  const namedNode = node as NodeWithName;
  const layoutNode = node as NodeWithLayout;
  const snapshot: NormalizedNodeSnapshot = {
    id: node.id,
    type: node.type,
    name: typeof namedNode.name === 'string' ? namedNode.name : '',
  };

  if (node.type === 'INSTANCE') {
    const mainComponent = await node.getMainComponentAsync();
    if (mainComponent) snapshot.mainComponentKey = mainComponent.key;
  }

  if (typeof layoutNode.layoutMode === 'string') snapshot.layoutMode = layoutNode.layoutMode;
  if (typeof layoutNode.layoutSizingHorizontal === 'string') {
    snapshot.layoutSizingHorizontal = layoutNode.layoutSizingHorizontal;
  }
  if (typeof layoutNode.layoutSizingVertical === 'string') {
    snapshot.layoutSizingVertical = layoutNode.layoutSizingVertical;
  }
  if (typeof layoutNode.layoutPositioning === 'string') {
    snapshot.layoutPositioning = layoutNode.layoutPositioning;
  }
  const parent = (node as NodeWithParent).parent;
  if (parent) snapshot.parent = snapshotParent(parent);
  const variableBindings = snapshotVariableBindings(node);
  if (variableBindings) snapshot.variableBindings = variableBindings;

  const reactionNode = node as NodeWithReactions;
  if (reactionNode.reactions) {
    snapshot.reactions = reactionNode.reactions.map((reaction) => {
      const actions = snapshotReactionActions(reaction);
      return actions === undefined ? {} : { actions };
    });
  }

  return snapshot;
}

async function snapshotSelectionTree(node: BaseNode): Promise<NormalizedNodeSnapshot> {
  const snapshot = await snapshotNodeShallow(node);
  if ('children' in node) {
    const children = (node as NodeWithChildren).children;
    snapshot.children = await Promise.all(children.map(snapshotSelectionTree));
  }
  return snapshot;
}

export class FigmaNodePort implements NodePort {
  async getSelection(): Promise<NormalizedNodeSnapshot[]> {
    return Promise.all(figma.currentPage.selection.map(snapshotSelectionTree));
  }

  async readNode(nodeId: string): Promise<NormalizedNodeSnapshot | null> {
    const node = await figma.getNodeByIdAsync(nodeId);
    return node ? snapshotNodeShallow(node) : null;
  }

  async renameIfCurrent(nodeId: string, expectedName: string, name: string): Promise<ConditionalMutationResult> {
    let node;
    try {
      node = await figma.getNodeByIdAsync(nodeId);
    } catch {
      return 'lookup_failed';
    }
    if (!node) return 'missing';
    if (!('name' in node) || (node as Partial<NodeWithName>).name !== expectedName) return 'stale';
    (node as NodeWithName).name = name;
    return 'applied';
  }

  async importComponent(componentKey: string): Promise<ComponentNode> {
    return figma.importComponentByKeyAsync(componentKey);
  }

  async replaceIconInstanceIfCurrent(
    nodeId: string,
    expectedMainComponentKey: string,
    component: unknown,
  ): Promise<ConditionalMutationResult> {
    let node;
    try {
      node = await figma.getNodeByIdAsync(nodeId);
    } catch {
      return 'lookup_failed';
    }
    if (!node) return 'missing';
    if (node.type !== 'INSTANCE') return 'stale';
    if (!isComponentNode(component)) throw new Error('Imported value is not a component');
    let currentComponent;
    try {
      currentComponent = await node.getMainComponentAsync();
    } catch {
      return 'lookup_failed';
    }
    if (currentComponent?.key !== expectedMainComponentKey) return 'stale';
    node.swapComponent(component);
    return 'applied';
  }
}

function isComponentNode(value: unknown): value is ComponentNode {
  const candidate = asRecord(value);
  return candidate?.type === 'COMPONENT' && typeof candidate.key === 'string';
}
