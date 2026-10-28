import { label } from "./producer.js";
export function display(id: number): string {
  return label(id).toUpperCase();
}
