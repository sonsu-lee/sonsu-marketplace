import { label } from "./producer.js";
export function display(id: number): string {
  const value = label(id);
  if (value === undefined) throw new Error("label missing");
  return value.toUpperCase();
}
