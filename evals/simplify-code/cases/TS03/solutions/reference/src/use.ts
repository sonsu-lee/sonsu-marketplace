import { box } from "./box.js";
export function shout(value: string): string {
  return box(value).value.toUpperCase();
}
