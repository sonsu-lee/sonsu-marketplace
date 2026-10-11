/**
 * Validate .omp-plugin/marketplace.json with the omp CLI.
 *
 * TEMPORARY WORKAROUND: omp has no catalog schema or validation command, and it
 * skips invalid plugin entries without telling the user (it only writes a warn
 * line to its log file). We plan to contribute a fix to omp
 * (https://github.com/can1357/oh-my-pi). Replace this script with the official
 * mechanism once omp provides one.
 *
 * How it works, using documented omp commands only:
 *   1. `omp plugin marketplace add ./` fails when the catalog is invalid JSON or
 *      has invalid top-level fields.
 *   2. Names that appear twice, compared case-insensitively like omp does, are
 *      rejected. omp keeps only the first entry, and an exact repeat (`a`/`a`)
 *      would otherwise pass step 3 because both dry-runs resolve to that entry.
 *   3. `omp plugin install --dry-run` on every declared plugin fails when omp
 *      skipped the entry (invalid name or source, case-only duplicate) or when
 *      its source directory does not exist.
 *
 * omp runs with a temporary HOME, so your own omp registry is never touched.
 *
 * Usage: node scripts/validate-marketplace.ts   (Node.js 22.18 or later)
 * Set OMP to use a specific omp binary.
 */
import { spawnSync } from "node:child_process";
import { mkdtempSync, readFileSync, rmSync } from "node:fs";
import { tmpdir } from "node:os";
import { dirname, join } from "node:path";
import { fileURLToPath } from "node:url";

const omp = process.env.OMP ?? "omp";
const root = join(dirname(fileURLToPath(import.meta.url)), "..");
const catalogPath = join(root, ".omp-plugin", "marketplace.json");
const home = mkdtempSync(join(tmpdir(), "validate-marketplace-"));

class OmpUnavailable extends Error {}

function runOmp(args: string[]): boolean {
	const result = spawnSync(omp, args, {
		cwd: root,
		env: { ...process.env, HOME: home },
		stdio: ["ignore", "inherit", "inherit"],
	});
	if (result.error) throw new OmpUnavailable(`✘ Could not run ${omp}: ${result.error.message}`);
	return result.status === 0;
}

/** Returns the error lines to print; an empty array means the catalog is valid. */
function validate(): string[] {
	if (!runOmp(["plugin", "marketplace", "add", "./"])) {
		return [`✘ omp rejected ${catalogPath}`];
	}

	const catalog = JSON.parse(readFileSync(catalogPath, "utf8")) as {
		name: string;
		plugins: { name?: unknown }[];
	};
	const names = catalog.plugins.map(plugin => String(plugin?.name));

	const seen = new Set<string>();
	const duplicates = new Set<string>();
	for (const name of names) {
		const key = name.toLowerCase();
		if (seen.has(key)) duplicates.add(key);
		seen.add(key);
	}
	if (duplicates.size > 0) {
		return [`✘ Duplicate plugin names (case-insensitive): ${[...duplicates].join(", ")}`];
	}

	const failed = names.filter(
		name => !runOmp(["plugin", "install", "--dry-run", "--scope", "project", `${name}@${catalog.name}`]),
	);
	if (failed.length > 0) {
		return [
			`✘ ${failed.length} of ${names.length} plugin entries failed: ${failed.join(", ")}`,
			"  Check names (ASCII letters, digits, '-', '.'; max 64), './' sources, and directories.",
		];
	}

	console.log(`✔ ${names.length} plugin entries accepted by omp`);
	return [];
}

let errors: string[];
try {
	errors = validate();
} catch (err) {
	if (!(err instanceof OmpUnavailable)) throw err;
	errors = [err.message];
} finally {
	rmSync(home, { recursive: true, force: true });
}
for (const line of errors) console.error(line);
process.exitCode = errors.length > 0 ? 1 : 0;
