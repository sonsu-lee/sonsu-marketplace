import { load, type Result } from "../src/loader.js";
const result = load("x");
if (result.state === "ready") { const data: string = result.data; void data; }
else { const message: string = result.message; void message; }
const error: Result = { state: "error", message: "bad" };
void error;
function inspect(value: Result): string {
  return value.state === "ready" ? value.data : value.message;
}
void inspect;
// @ts-expect-error error must carry its message
const missingMessage: Result = { state: "error" };
void missingMessage;
// @ts-expect-error ready must carry data
const badReady: Result = { state: "ready" };
// @ts-expect-error error cannot carry ready data
const badError: Result = { state: "error", message: "bad", data: "x" };
void [badReady, badError];
