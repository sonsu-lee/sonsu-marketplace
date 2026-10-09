// worklog-v1 recorder for omp. Writes local JSONL only; never alters results or injects context.
import type { ExtensionAPI } from "@oh-my-pi/pi-coding-agent";
import { execFileSync } from "node:child_process";
import { createHash, randomUUID } from "node:crypto";
import { appendFileSync, existsSync, lstatSync, mkdirSync, readdirSync, readFileSync, realpathSync, renameSync, rmSync, writeFileSync } from "node:fs";
import { homedir } from "node:os";
import { dirname, isAbsolute, join, resolve } from "node:path";

const SCHEMA = "worklog-v1";
const HOST = "omp";
const DAY_MS = 24 * 60 * 60 * 1000;
const RETENTION_DAYS = 90;
const ERROR_EXCERPT = 300;
const INPUT_EXCERPT = 200;
const OFF_VALUES: Record<string, true> = { off: true, "0": true, false: true };
const SESSION_RE = /^[A-Za-z0-9._-]{1,128}$/;
const DATE_RE = /^\d{4}-\d{2}-\d{2}$/;
// SECRET_RE from memory-manager memory_store.py; plugins stay independent (ADR 0003).
const SECRET_RE = new RegExp(
	[
		String.raw`-----BEGIN [A-Z0-9 ]*PRIVATE KEY(?: BLOCK)?-----`,
		String.raw`\b(?:[a-z0-9]+[_-])*(?:api[_-]?key|access[_-]?token|password|secret|token|client[_-]?secret|aws[_-]?secret[_-]?access[_-]?key|private[_-]?key)(?:\\*["'])?\s*[:=]\s*\S+`,
		String.raw`\b(?:password|passphrase|api[ _-]?key|access[ _-]?token|secret|token)\s+(?:is|was|are)\s+\S+`,
		String.raw`(?:비밀번호|암호|비밀[ _-]?키|API[ _-]?키|토큰)\s*(?:은|는|이|가|:|=)\s*\S+`,
		String.raw`\bauthorization\s*:\s*(?:bearer|basic)\s+\S+`,
		String.raw`\b(?:sk-|ghp_|github_pat_)[A-Za-z0-9_-]{20,}`,
		String.raw`\bAKIA[0-9A-Z]{16}\b`,
	].join("|"),
	"gi",
);
// Same exclusions as memory-manager project_key(): ambient repository overrides must not change identity.
const GIT_ENV_EXCLUDED: Record<string, true> = {
	GIT_ALTERNATE_OBJECT_DIRECTORIES: true,
	GIT_CEILING_DIRECTORIES: true,
	GIT_COMMON_DIR: true,
	GIT_CONFIG: true,
	GIT_DIR: true,
	GIT_DISCOVERY_ACROSS_FILESYSTEM: true,
	GIT_IMPLICIT_WORK_TREE: true,
	GIT_INDEX_FILE: true,
	GIT_NAMESPACE: true,
	GIT_OBJECT_DIRECTORY: true,
	GIT_PREFIX: true,
	GIT_WORK_TREE: true,
};
const GIT_CONFIG_FILES: Record<string, true> = { GIT_CONFIG_GLOBAL: true, GIT_CONFIG_SYSTEM: true, GIT_CONFIG_NOSYSTEM: true };

interface Session {
	sessionId: string;
	generated: boolean;
	cwd: string;
	key: string;
	identity: string;
	projectDir: string;
	date: string;
	stateSaved: boolean;
}

// Fields read from omp handler arguments, all optional: the extension must keep working on omp
// builds where one is missing (fallbacks: generated session ID, closure state without ctx).
interface HostContext {
	cwd?: unknown;
	sessionManager?: { getSessionId?: unknown; getSessionFile?: unknown } | null;
	agent?: { kind?: unknown } | null;
}

interface ToolResultPayload {
	isError?: unknown;
	toolName?: unknown;
	toolCallId?: unknown;
	content?: Array<{ type?: unknown; text?: unknown } | null> | null;
	input?: { command?: unknown; path?: unknown } | null;
}

function errorCode(error: unknown): unknown {
	return error instanceof Error && "code" in error ? error.code : undefined;
}

function clip(value: unknown, limit: number): string | null {
	return typeof value === "string" ? value.replace(SECRET_RE, "[redacted]").slice(0, limit) : null;
}

function firstLine(value: unknown): string | null {
	if (typeof value !== "string") return null;
	for (const line of value.split(/\r?\n/)) {
		if (line.trim()) return line.trim();
	}
	return null;
}

function rootPath(): string {
	const override = process.env.SONSU_WORKLOG_HOME;
	let root = override ? override : join(homedir(), ".sonsu", "worklog");
	if (root === "~" || root.startsWith("~/")) root = join(homedir(), root.slice(1));
	if (!isAbsolute(root)) throw new Error("unsafe_path");
	for (let current = root; ; current = dirname(current)) {
		try {
			if (lstatSync(current).isSymbolicLink()) throw new Error("unsafe_path");
		} catch (error) {
			if (errorCode(error) !== "ENOENT") throw error;
		}
		if (dirname(current) === current) break;
	}
	return root;
}

function projectIdentity(cwd: string): string {
	const location = realpathSync(cwd);
	const env: Record<string, string> = {};
	for (const [name, value] of Object.entries(process.env)) {
		if (value === undefined || GIT_ENV_EXCLUDED[name]) continue;
		if (name.startsWith("GIT_CONFIG_") && !GIT_CONFIG_FILES[name]) continue;
		env[name] = value;
	}
	try {
		const out = execFileSync("git", ["-C", location, "rev-parse", "--git-common-dir"], {
			encoding: "utf8",
			env,
			stdio: ["ignore", "pipe", "ignore"],
		});
		if (out.trim()) return realpathSync(resolve(location, out.trim()));
	} catch {
		// Not a Git checkout: the directory itself is the identity.
	}
	return location;
}

function requireSafePath(path: string): void {
	for (let current = path; ; current = dirname(current)) {
		try {
			if (lstatSync(current).isSymbolicLink()) throw new Error("unsafe_path");
		} catch (error) {
			if (errorCode(error) !== "ENOENT") throw error;
		}
		if (dirname(current) === current) break;
	}
}

function ensureDir(path: string): void {
	requireSafePath(path);
	mkdirSync(path, { recursive: true, mode: 0o700 });
	if (lstatSync(path).isSymbolicLink()) throw new Error("unsafe_path");
}

function disabled(projectDir: string): boolean {
	return OFF_VALUES[(process.env.SONSU_WORKLOG ?? "").trim().toLowerCase()] === true || existsSync(join(projectDir, "disabled"));
}

// Remove date directories older than the retention period at most once per 24 hours.
function prune(hostDir: string, now: Date): void {
	requireSafePath(hostDir);
	const stateDir = join(hostDir, ".state");
	const marker = join(stateDir, "last-prune");
	try {
		const last = Date.parse(readFileSync(marker, "utf8").trim());
		if (!Number.isNaN(last) && now.getTime() - last < DAY_MS) return;
	} catch {
		// No marker yet.
	}
	const cutoff = new Date(now.getTime() - RETENTION_DAYS * DAY_MS).toISOString().slice(0, 10);
	try {
		for (const name of readdirSync(hostDir)) {
			const path = join(hostDir, name);
			if (DATE_RE.test(name) && name < cutoff && lstatSync(path).isDirectory()) {
				rmSync(path, { recursive: true, force: true });
			}
		}
	} catch {
		// Host directory does not exist yet.
	}
	ensureDir(stateDir);
	const temporary = join(stateDir, `.last-prune.${process.pid}`);
	writeFileSync(temporary, `${now.toISOString()}\n`, { mode: 0o600 });
	renameSync(temporary, marker);
}

export default function worklog(pi: ExtensionAPI) {
	const generatedId = randomUUID();
	let session: Session | null = null;

	// Handlers may run without a prior session_start (or without ctx); keep per-factory closure state.
	function open(ctx: unknown): Session {
		if (session) return session;
		// Unchecked cast: omp passes its ExtensionContext (or nothing); every field is re-checked below.
		const host = ctx as HostContext | undefined;
		const manager = host?.sessionManager;
		const nativeId: unknown = typeof manager?.getSessionId === "function" ? manager.getSessionId.call(manager) : undefined;
		const cwd = typeof host?.cwd === "string" && host.cwd ? host.cwd : process.cwd();
		const identity = projectIdentity(cwd);
		const key = createHash("sha256").update(identity).digest("hex").slice(0, 20);
		const rawId = typeof nativeId === "string" && nativeId ? nativeId : generatedId;
		session = {
			sessionId: SESSION_RE.test(rawId) ? rawId : createHash("sha256").update(rawId).digest("hex").slice(0, 32),
			generated: rawId === generatedId,
			cwd: resolve(cwd),
			key,
			identity,
			projectDir: join(rootPath(), key),
			date: new Date().toISOString().slice(0, 10),
			stateSaved: false,
		};
		return session;
	}

	function write(current: Session, event: string, source: string, data: Record<string, unknown>): void {
		if (disabled(current.projectDir)) return;
		ensureDir(current.projectDir);
		try {
			writeFileSync(
				join(current.projectDir, "project.json"),
				`${JSON.stringify({ identity: current.identity, created: new Date().toISOString() })}\n`,
				{ flag: "wx", mode: 0o600 },
			);
		} catch (error) {
			if (errorCode(error) !== "EEXIST") throw error;
		}
		if (!current.stateSaved) {
			const stateDir = join(current.projectDir, HOST, ".state");
			ensureDir(stateDir);
			const statePath = join(stateDir, `${current.sessionId}.json`);
			try {
				writeFileSync(statePath, `${JSON.stringify({ date: current.date })}\n`, { flag: "wx", mode: 0o600 });
			} catch (error) {
				if (errorCode(error) !== "EEXIST") throw error;
				const state = JSON.parse(readFileSync(statePath, "utf8"));
				if (typeof state.date !== "string" || !DATE_RE.test(state.date)) throw new Error("invalid_session_date");
				const cutoff = new Date(Date.now() - RETENTION_DAYS * DAY_MS).toISOString().slice(0, 10);
				if (state.date >= cutoff) {
					current.date = state.date;
				} else {
					const temporary = `${statePath}.${process.pid}.tmp`;
					writeFileSync(temporary, `${JSON.stringify({ date: current.date })}\n`, { mode: 0o600 });
					renameSync(temporary, statePath);
				}
			}
			current.stateSaved = true;
		}
		const day = join(current.projectDir, HOST, current.date);
		ensureDir(day);
		const record = {
			schema: SCHEMA,
			ts: new Date().toISOString(),
			host: HOST,
			host_version: null,
			session_id: current.sessionId,
			project_key: current.key,
			cwd: current.cwd,
			turn_id: null,
			event,
			signal_source: `omp:${source}`,
			data,
		};
		appendFileSync(join(day, `${current.sessionId}.jsonl`), `${JSON.stringify(record)}\n`, { mode: 0o600 });
	}

	function startSession(ctx: unknown, source: string): void {
		try {
			session = null;
			const current = open(ctx);
			if (disabled(current.projectDir)) return;
			const host = ctx as unknown as HostContext | undefined;
			const manager = host?.sessionManager;
			const transcript: unknown = typeof manager?.getSessionFile === "function" ? manager.getSessionFile.call(manager) : undefined;
			const agent = host?.agent;
			const data: Record<string, unknown> = {
				source: null,
				transcript_path: typeof transcript === "string" ? transcript : null,
				model: null,
				agent_kind: typeof agent?.kind === "string" ? agent.kind : null,
			};
			if (current.generated) data.session_id_source = "generated";
			write(current, "session_start", source, data);
			prune(join(current.projectDir, HOST), new Date());
		} catch {
			// Fail open: logging must never affect the session.
		}
	}

	pi.on("session_start", (_event, ctx) => startSession(ctx, "session_start"));
	pi.on("session_switch", (_event, ctx) => startSession(ctx, "session_switch"));
	pi.on("session_branch", (_event, ctx) => startSession(ctx, "session_branch"));

	pi.on("tool_result", (event, ctx) => {
		try {
			const current = open(ctx);
			// Unchecked cast: omp's tool_result event; each field is re-checked before use.
			const payload = event as unknown as ToolResultPayload | undefined;
			if (!payload) return;
			const failed = payload.isError === true;
			const data: Record<string, unknown> = {
				outcome: failed ? "failed" : "ok",
				tool_name: typeof payload.toolName === "string" ? payload.toolName : null,
				tool_use_id: typeof payload.toolCallId === "string" ? payload.toolCallId : null,
				exit_code: null,
				error: null,
				is_interrupt: null,
				duration_ms: null,
				input_excerpt: null,
			};
			if (failed) {
				const blocks = Array.isArray(payload.content) ? payload.content : [];
				const text = blocks.find(block => block?.type === "text" && typeof block.text === "string");
				const input = payload.input ?? {};
				data.error = clip(firstLine(text?.text), ERROR_EXCERPT);
				data.input_excerpt = clip(input.command ?? input.path, INPUT_EXCERPT);
			}
			write(current, "tool_result", "tool_result", data);
		} catch {
			// Fail open.
		}
	});

	pi.on("agent_end", (_event, ctx) => {
		try {
			write(open(ctx), "stop", "agent_end", { last_message_chars: null });
		} catch {
			// Fail open.
		}
	});

	pi.on("session_shutdown", (_event, ctx) => {
		try {
			// Synchronous append only: shutdown handlers have a 2 second budget.
			write(open(ctx), "session_end", "session_shutdown", { reason: "shutdown" });
		} catch {
			// Fail open.
		}
	});
}
