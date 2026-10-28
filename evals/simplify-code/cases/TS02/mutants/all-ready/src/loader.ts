export type Result = { state: "ready"; data: string; message?: never };
export function load(key: string): Result {
  return { state: "ready", data: key.toUpperCase() };
}
