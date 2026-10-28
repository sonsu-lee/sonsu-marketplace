import { box } from "./box.js";
export function shout(value: string): string {
  const result = box(value);
  if (typeof result.value !== "string") throw new Error("not a string");
  return result.value.toUpperCase();
}
