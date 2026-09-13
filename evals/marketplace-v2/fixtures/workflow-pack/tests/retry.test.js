import assert from "node:assert/strict";
import test from "node:test";
import { normalizeRetries } from "../src/retry.js";

test("uses the default when retries are omitted", () => {
  assert.equal(normalizeRetries(undefined), 3);
});

test("keeps an allowed positive retry count", () => {
  assert.equal(normalizeRetries(5), 5);
});
