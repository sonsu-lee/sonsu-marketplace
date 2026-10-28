import assert from "node:assert/strict";
import { load } from "../dist/src/loader.js";
import { view } from "../dist/src/view.js";
assert.deepEqual(load("ab"), { state: "ready", data: "AB" });
assert.deepEqual(load(""), { state: "error", message: "empty key" });
assert.equal(view("ab"), "AB");
assert.equal(view(""), "Error: empty key");
