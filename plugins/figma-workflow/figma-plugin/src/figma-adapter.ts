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

function readDestinationId(action: unknown): string | undefined {
  const destinationId = asRecord(action)?.destinationId;
  return typeof destinationId === 'string' ? destinationId : undefined;
}

function snapshotParent(parent: BaseNode): NonNullable<NormalizedNodeSnapshot['parent']> {
  const layoutMode = (parent as NodeWithLayout).layoutMode;
  return typeof layoutMode === 'string'
    ? { id: parent.id, type: parent.type, layoutMode }
    : { id: parent.id, type: parent.type };
}

function snapshotVariableBindings(node: BaseNode): Record<string, NormalizedVariableBinding> | undefined {
  const variableNode = node as NodeWithVariables;
  const bindings: Record<string, NormalizedVariableBinding> = {};
  if (typeof variableNode.opacity === 'number' && Number.isFinite(variableNode.opacity)) {
    bindings.opacity = { kind: 'literal', value: variableNode.opacity };
  }
  const opacityBinding = asRecord(asRecord(variableNode.boundVariables)?.opacity);
  if (opacityBinding?.type === 'VARIABLE_ALIAS' && typeof opacityBinding.id === 'string') {
    bindings.opacity = { kind: 'binding', variableId: opacityBinding.id };
  }
  return Object.keys(bindings).length > 0 ? bindings : undefined;
}

async function snapshotNode(node: BaseNode): Promise<NormalizedNodeSnapshot> {
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
      const actions = asRecord(reaction)?.actions;
      if (!Array.isArray(actions)) return {};
      return { actions: actions.map((action) => ({ destinationId: readDestinationId(action) })) };
    });
  }

  if ('children' in node) {
    const children = (node as NodeWithChildren).children;
    snapshot.children = await Promise.all(children.map(snapshotNode));
  }

  return snapshot;
}

export class FigmaNodePort implements NodePort {
  async getSelection(): Promise<NormalizedNodeSnapshot[]> {
    return Promise.all(figma.currentPage.selection.map(snapshotNode));
  }

  async readNode(nodeId: string): Promise<NormalizedNodeSnapshot | null> {
    const node = await figma.getNodeByIdAsync(nodeId);
    return node ? snapshotNode(node) : null;
  }

  async renameIfCurrent(nodeId: string, expectedName: string, name: string): Promise<ConditionalMutationResult> {
    const node = await figma.getNodeByIdAsync(nodeId);
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
    const node = await figma.getNodeByIdAsync(nodeId);
    if (!node) return 'missing';
    if (node.type !== 'INSTANCE') return 'stale';
    if (!isComponentNode(component)) throw new Error('Imported value is not a component');
    const currentComponent = await node.getMainComponentAsync();
    if (currentComponent?.key !== expectedMainComponentKey) return 'stale';
    node.swapComponent(component);
    return 'applied';
  }
}

function isComponentNode(value: unknown): value is ComponentNode {
  const candidate = asRecord(value);
  return candidate?.type === 'COMPONENT' && typeof candidate.key === 'string';
}
