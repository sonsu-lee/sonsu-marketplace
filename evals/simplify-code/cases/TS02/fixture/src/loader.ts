export type Result = { state: "ready" | "error"; data?: string; message?: string };
export function load(key: string): Result {
  return key ? { state: "ready", data: key.toUpperCase() } : { state: "error", message: "empty key" };
}
