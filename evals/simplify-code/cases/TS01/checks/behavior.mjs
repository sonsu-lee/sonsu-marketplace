import assert from "node:assert/strict";
import { label } from "../dist/src/producer.js";
import { display } from "../dist/src/consumer.js";
assert.equal(label(3), "item-3");
assert.equal(display(-2), "ITEM--2");
