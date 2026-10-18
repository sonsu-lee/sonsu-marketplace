import assert from "node:assert/strict";
import { mkdtempSync, rmSync } from "node:fs";
import { tmpdir } from "node:os";
import { join } from "node:path";
import { spawnSync } from "node:child_process";
import { after, test } from "node:test";
import { fileURLToPath } from "node:url";

const cwd = mkdtempSync(join(tmpdir(), "branch-rules-"));
const config = fileURLToPath(
  new URL("../skills/naming-branches/assets/commit-check.toml", import.meta.url),
);
const env = Object.fromEntries(
  Object.entries(process.env).filter(([key]) => !key.startsWith("CCHK_")),
);
after(() => rmSync(cwd, { recursive: true, force: true }));
assert.equal(spawnSync("git", ["init", "--quiet", "--initial-branch=main", cwd]).status, 0);

function lint(branch, expected, extra = []) {
  const result = spawnSync("uvx", [
    "--from", "commit-check==2.19.1", "commit-check", "--branch",
    "--format", "json", "--config", config, ...extra,
  ], { cwd, env, input: `${branch}\n`, encoding: "utf8" });
  assert.equal(result.status, expected === "pass" ? 0 : 1, result.stdout + result.stderr);
  const report = JSON.parse(result.stdout);
  const check = report.checks.find((entry) => entry.rule_id === "CC201");
  assert.equal(check.value, branch);
  assert.equal(check.status, expected);
  assert.equal(report.warnings, 0);
}

test("validates the proposed branch instead of the checked-out trunk", () => {
  lint("feature/git-workflow-validation", "pass");
  lint("unknown/git-workflow-validation", "fail");
});

test("accepts default prefixes, trunk names, and dotted descriptions", () => {
  for (const branch of [
    "feature/add-login", "fix/login", "hotfix/security-patch",
    "release/v1.2.0", "chore/upgrade-node-v20.11", "main", "master", "develop",
  ]) lint(branch, "pass");
});

test("rejects aliases, agent prefixes, and invalid description grammar", () => {
  for (const branch of [
    "feat/add-login", "bugfix/login", "codex/add-login", "Feature/add-login",
    "feature/new--login", "feature/-login", "feature/login-",
    "release/v1.-2.0", "release/v1..2", "fix/header_bug", "feature/a/b",
  ]) lint(branch, "fail");
});

test("permits an explicitly authorized prefix without relaxing grammar", () => {
  const override = ["--allow-branch-types", "feature,fix,hotfix,release,chore,codex"];
  lint("codex/add-login", "pass", override);
  lint("codex/add--login", "fail", override);
});
