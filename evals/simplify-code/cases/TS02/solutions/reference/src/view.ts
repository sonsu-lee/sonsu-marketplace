import { load } from "./loader.js";
export function view(key: string): string {
  const result = load(key);
  return result.state === "ready" ? result.data : `Error: ${result.message}`;
}
