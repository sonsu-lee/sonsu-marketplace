export type Config = { host: string; port: number };
export function parseConfig(json: string): Config {
  const value: unknown = JSON.parse(json);
  if (typeof value !== "object" || value === null || Array.isArray(value)) throw new Error("invalid config");
  if (!("host" in value) || typeof value.host !== "string" || !("port" in value) || typeof value.port !== "number" || !Number.isInteger(value.port) || value.port < 1 || value.port > 65535) throw new Error("invalid config");
  return { host: value.host, port: value.port };
}
