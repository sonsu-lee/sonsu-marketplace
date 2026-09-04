import type { NormalizedNodeSnapshot } from './contracts.js';
import type { NodePort } from './ports.js';

type NodeWithName = BaseNode & { name: string };
type NodeWithChildren = BaseNode & { children: readonly BaseNode[] };
type NodeWithLayout = BaseNode & {
  layoutMode?: string;
  layoutSizingHorizontal?: string;
  layoutSizingVertical?: string;
  layoutPositioning?: string;
};
type NodeWithReactions = BaseNode & { reactions?: readonly unknown[] };

const asRecord = (value: unknown): Record<string, unknown> | undefined =>
  typeof value === 'object' && value !== null ? value as Record<string, unknown> : undefined;

function readDestinationId(action: unknown): string | undefined {
  const destinationId = asRecord(action)?.destinationId;
  return typeof destinationId === 'string' ? destinationId : undefined;
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

async function findNode(nodeId: string): Promise<BaseNode> {
  const node = await figma.getNodeByIdAsync(nodeId);
  if (!node) throw new Error(`Node not found: ${nodeId}`);
  return node;
}

export class FigmaNodePort implements NodePort {
  async getSelection(): Promise<NormalizedNodeSnapshot[]> {
    return Promise.all(figma.currentPage.selection.map(snapshotNode));
  }

  async readNode(nodeId: string): Promise<NormalizedNodeSnapshot | null> {
    const node = await figma.getNodeByIdAsync(nodeId);
    return node ? snapshotNode(node) : null;
  }

  async rename(nodeId: string, name: string): Promise<void> {
    const node = await findNode(nodeId);
    if (!('name' in node) || typeof (node as Partial<NodeWithName>).name !== 'string') {
      throw new Error(`Node cannot be renamed: ${nodeId}`);
    }
    (node as NodeWithName).name = name;
  }

  async importComponent(componentKey: string): Promise<ComponentNode> {
    return figma.importComponentByKeyAsync(componentKey);
  }

  async replaceIconInstance(nodeId: string, component: unknown): Promise<void> {
    const node = await findNode(nodeId);
    if (node.type !== 'INSTANCE') throw new Error(`Node is not an instance: ${nodeId}`);
    if (!isComponentNode(component)) throw new Error('Imported value is not a component');
    node.swapComponent(component);
  }
}

function isComponentNode(value: unknown): value is ComponentNode {
  const candidate = asRecord(value);
  return candidate?.type === 'COMPONENT' && typeof candidate.key === 'string';
}
