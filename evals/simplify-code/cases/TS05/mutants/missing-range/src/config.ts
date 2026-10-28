export type Config = { host: string; port: number };
export function parseConfig(json: string): Config {
  const value: unknown = JSON.parse(json);
  if (typeof value !== "object" || value === null || !("host" in value) || typeof value.host !== "string" || !("port" in value) || typeof value.port !== "number") throw new Error("invalid config");
  return { host: value.host, port: value.port };
}
