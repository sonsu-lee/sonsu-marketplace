import assert from "node:assert/strict";
import { report, summary } from "../dist/src/report.js";
assert.equal(report("abc"), "abc:3");
assert.equal(report(""), ":0");
assert.equal(summary(), "all:0");
