import { Registry } from "./registry.js";
export function greet(registry: Registry, key: string): string {
  return `Hello ${registry.get(key)}`;
}
