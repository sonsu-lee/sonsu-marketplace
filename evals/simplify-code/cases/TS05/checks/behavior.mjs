import assert from "node:assert/strict";
import { parseConfig } from "../dist/src/config.js";
import { address } from "../dist/src/address.js";
assert.deepEqual(parseConfig('{"host":"localhost","port":80,"extra":true}'), { host: "localhost", port: 80 });
assert.equal(address('{"host":"example","port":443}'), "example:443");
for (const json of ["null", "[]", "{}", '{"host":2,"port":80}', '{"host":"x","port":"80"}', '{"host":"x","port":0}', '{"host":"x","port":65536}', '{"host":"x","port":1.5}']) {
  assert.throws(() => parseConfig(json), { message: "invalid config" });
}
assert.throws(() => parseConfig("{"), SyntaxError);
