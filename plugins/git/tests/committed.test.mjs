import assert from "node:assert/strict";
import { spawnSync } from "node:child_process";
import { fileURLToPath } from "node:url";
import { test } from "node:test";

const config = fileURLToPath(new URL("../skills/writing-commits/assets/committed.toml", import.meta.url));

function check(message) {
  return spawnSync("uvx", ["--from", "committed==1.1.12", "committed", "--config", config, "--commit-file", "-"], {
    input: message, encoding: "utf8",
  });
}

test("checks conventional messages with committed defaults", () => {
  const valid = check("feat: Add login\n");
  assert.equal(valid.status, 0, valid.stdout + valid.stderr);
  const invalid = check("feat: add login\n");
  assert.notEqual(invalid.status, 0);
  assert.match(invalid.stdout + invalid.stderr, /capitalized/);
});
