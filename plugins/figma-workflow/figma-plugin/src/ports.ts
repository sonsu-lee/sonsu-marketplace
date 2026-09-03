import type { NormalizedNodeSnapshot } from './contracts.js';

export interface NodePort {
  getSelection(): Promise<NormalizedNodeSnapshot[]>;
  readNode(nodeId: string): Promise<NormalizedNodeSnapshot | null>;
  rename(nodeId: string, name: string): Promise<void>;
  importComponent(componentKey: string): Promise<unknown>;
  replaceIconInstance(nodeId: string, component: unknown): Promise<void>;
}
