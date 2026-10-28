export type Result = { state: "ready"; data: string; message?: never } | { state: "error"; message?: string; data?: never };
export function load(key: string) {
  return key ? { state: "ready" as const, data: key.toUpperCase() } : { state: "error" as const, message: "empty key" };
}
