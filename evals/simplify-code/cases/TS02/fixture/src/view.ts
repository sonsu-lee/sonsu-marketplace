import { load } from "./loader.js";
export function view(key: string): string {
  const result = load(key);
  if (result.state === "ready") {
    if (result.data === undefined) throw new Error("missing data");
    return result.data;
  }
  if (result.message === undefined) throw new Error("missing message");
  return `Error: ${result.message}`;
}
