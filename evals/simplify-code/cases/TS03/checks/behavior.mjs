import assert from "node:assert/strict";
import { box } from "../dist/src/box.js";
import { shout } from "../dist/src/use.js";
const input = { count: 1 };
assert.equal(box(input).value, input);
assert.equal(box(null).value, null);
assert.equal(shout("hello"), "HELLO");
