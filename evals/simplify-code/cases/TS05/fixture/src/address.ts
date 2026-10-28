import { parseConfig } from "./config.js";
export function address(json: string): string {
  const config = parseConfig(json);
  return `${config.host}:${config.port}`;
}
