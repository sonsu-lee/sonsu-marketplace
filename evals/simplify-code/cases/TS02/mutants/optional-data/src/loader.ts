export type Result = { state: "ready"; data?: string; message?: never } | { state: "error"; message: string; data?: never };
export function load(key: string): Result {
  return key ? { state: "ready", data: key.toUpperCase() } : { state: "error", message: "empty key" };
}
