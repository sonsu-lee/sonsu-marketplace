import assert from "node:assert/strict";
import { mkdtempSync, rmSync, writeFileSync } from "node:fs";
import { tmpdir } from "node:os";
import { join } from "node:path";
import { spawnSync } from "node:child_process";
import { after, test } from "node:test";
import { fileURLToPath } from "node:url";

const cwd = mkdtempSync(join(tmpdir(), "commitlint-rules-"));
const config = fileURLToPath(
  new URL("../skills/writing-commits/assets/commitlint.config.mjs", import.meta.url),
);
after(() => rmSync(cwd, { recursive: true, force: true }));
assert.equal(spawnSync("git", ["init", "--quiet", cwd]).status, 0);
const messageFile = join(cwd, "message.txt");

function lint(message, rule) {
  writeFileSync(messageFile, message);
  const result = spawnSync("npx", [
    "--yes", "--package", "@commitlint/cli@21.2.4", "commitlint",
    "--config", config, "--strict", "--verbose", "--edit", messageFile,
  ], { cwd, encoding: "utf8" });
  const output = `${result.stdout}${result.stderr}`;
  assert.equal(result.status, rule ? 3 : 0, output);
  if (rule) assert.ok(output.includes(`[${rule}]`), output);
}

test("loads the ESM asset without project dependencies in either module mode", () => {
  lint("feat: support HTTP requests\n");
  for (const type of ["commonjs", "module"]) {
    writeFileSync(join(cwd, "package.json"), JSON.stringify({ type }));
    lint("feat: support HTTP requests\n");
  }
});

test("accepts each supported breaking-change marker independently", () => {
  lint("feat(api)!: return UTC timestamps\n\nUse explicit offsets.\n");
  lint("feat(api): return UTC timestamps\n\nBREAKING-CHANGE: offsets are required.\n");
  lint("feat(api)!: return UTC timestamps\n\nBREAKING CHANGE: offsets are required.\n");
});

test("enforces type, scope, and subject rules without implicit ignores", () => {
  lint("revert: remove the timestamp conversion\n");
  lint("unknown: add timestamps\n", "type-enum");
  lint("fix(API): return timestamps\n", "scope-case");
  lint("fix: Return timestamps\n", "subject-case");
  lint("fix: return timestamps.\n", "subject-full-stop");
  lint("fix:\n", "subject-empty");
  lint("v1.2.3\n", "type-empty");
});

test("enforces 72-character boundaries in headers, bodies, and footers", () => {
  const header = "feat: " + "a".repeat(66);
  lint(`${header}\n`);
  lint(`${header}a\n`, "header-max-length");
  lint(`feat: add timestamps\n\n${"a".repeat(72)}\n`);
  lint(`feat: add timestamps\n\n${"a".repeat(73)}\n`, "body-max-line-length");
  const prefix = "BREAKING-CHANGE: ";
  const footer = prefix + "a".repeat(72 - prefix.length);
  lint(`feat: add timestamps\n\n${footer}\n`);
  lint(`feat: add timestamps\n\n${footer}a\n`, "footer-max-line-length");
});

test("requires blank lines before bodies and footers", () => {
  lint("fix: return timestamps\nExplain the change.\n", "body-leading-blank");
  lint("fix: return timestamps\nBREAKING-CHANGE: use UTC.\n", "footer-leading-blank");
});
