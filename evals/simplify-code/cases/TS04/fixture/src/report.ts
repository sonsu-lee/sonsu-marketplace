import { format } from "./format.js";
export function report(name: string): string {
  return format({ name, count: name.length });
}
export function summary(): string {
  return format({ name: "all", count: 0 });
}
