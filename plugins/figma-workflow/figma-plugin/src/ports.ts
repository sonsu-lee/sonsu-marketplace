import type { NormalizedNodeSnapshot } from './contracts.js';

export type ConditionalMutationResult = 'applied' | 'stale' | 'missing';

export interface NodePort {
  getSelection(): Promise<NormalizedNodeSnapshot[]>;
  readNode(nodeId: string): Promise<NormalizedNodeSnapshot | null>;
  renameIfCurrent(nodeId: string, expectedName: string, name: string): Promise<ConditionalMutationResult>;
  importComponent(componentKey: string): Promise<unknown>;
  replaceIconInstanceIfCurrent(
    nodeId: string,
    expectedMainComponentKey: string,
    component: unknown,
  ): Promise<ConditionalMutationResult>;
}
