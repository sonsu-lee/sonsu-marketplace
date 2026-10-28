import { Registry } from "../src/registry.js";
import { greet } from "../src/service.js";
const registry = new Registry();
const result: string = registry.get("key");
const greeting: string = greet(registry, "key");
void [result, greeting];
