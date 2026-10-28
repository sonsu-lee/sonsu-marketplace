export type Config = { host: string; port: number };
export function parseConfig(json: string): Config {
  return JSON.parse(json) as Config;
}
