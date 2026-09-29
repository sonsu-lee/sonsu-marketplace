// Generated copies come from shared/omp-runtime/extension.ts via scripts/render-omp-compat.py.
import type { ExtensionAPI, ExtensionContext } from "@oh-my-pi/pi-coding-agent";
import { existsSync, readFileSync } from "node:fs";
import { dirname, join } from "node:path";
import { fileURLToPath } from "node:url";

const ROOT = dirname(dirname(fileURLToPath(import.meta.url)));
const LABEL = String(JSON.parse(readFileSync(join(ROOT, "package.json"), "utf8")).name);
const CONTINUITY = join(ROOT, "scripts", "task-continuity.py");
const EVIDENCE = join(ROOT, "scripts", "evidence-gates.py");
const SESSION_VAR = "SONSU_OMP_SESSION_ID";
const SESSION_ID = /^[A-Za-z0-9][A-Za-z0-9_-]{0,127}$/;
const SCRIPT = /(?:task-continuity|evidence-gates)\.py\b/;
const EXPLICIT_SESSION = new RegExp(`\\b${SESSION_VAR}=`);

const record = (value: unknown): Record<string, unknown> | undefined =>
  value !== null && typeof value === "object" ? (value as Record<string, unknown>) : undefined;

export default function sonsuOmp(pi: ExtensionAPI) {
  const warn = (ctx: ExtensionContext, message: string) => {
    pi.logger?.warn?.(`${LABEL}: ${message}`);
    if (ctx.hasUI) ctx.ui.notify(`${LABEL}: ${message}`, "warning");
  };
  const session = (ctx: ExtensionContext): string | undefined => {
    const id: unknown = ctx.sessionManager.getSessionId();
    return typeof id === "string" && SESSION_ID.test(id) ? id : undefined;
  };
  const runHook = async (script: string, event: object, ms: number, ctx: ExtensionContext): Promise<unknown> => {
    const proc = Bun.spawn(["python3", script, "hook"], {
      cwd: ctx.cwd, stdin: new Blob([JSON.stringify(event)]), stdout: "pipe", stderr: "pipe",
    });
    const timer = ctx.setTimeout(() => proc.kill(), ms);
    const [out, err, code] = await Promise.all([
      new Response(proc.stdout).text(), new Response(proc.stderr).text(), proc.exited,
    ]);
    ctx.clearTimer(timer);
    if (code !== 0) { warn(ctx, (err.trim().split("\n")[0] || `exit ${code}`)); return undefined; }
    return out.trim() ? JSON.parse(out) : undefined;
  };

  pi.on("tool_call", (event, ctx) => {
    try {
      if (event.toolName !== "bash") return;
      const input = record(event.input);
      const command = input?.command;
      if (typeof command !== "string" || !SCRIPT.test(command) || EXPLICIT_SESSION.test(command)) return;
      const id = session(ctx);
      if (!id) return;
      return { input: { ...input, command: `export ${SESSION_VAR}=${id} # added by the Sonsu omp extension\n${command}` } };
    } catch (error) { warn(ctx, String(error)); return; }
  });

  if (existsSync(CONTINUITY)) {
    const recover = async (source: "resume" | "compact", ctx: ExtensionContext) => {
      try {
        if (ctx.agent?.kind === "sub") return;
        const id = session(ctx);
        if (!id) return;
        const result = await runHook(CONTINUITY, { hook_event_name: "SessionStart", source, session_id: id, cwd: ctx.cwd }, 5000, ctx);
        const text = record(record(result)?.hookSpecificOutput)?.additionalContext;
        if (typeof text !== "string" || !text) return;
        pi.sendMessage({ customType: "sonsu-task-continuity", content: text, display: false },
          { deliverAs: source === "compact" && !ctx.isIdle() ? "aside" : "nextTurn" });
      } catch (error) { warn(ctx, String(error)); }
    };
    pi.on("session_start", (_event, ctx) => recover("resume", ctx));
    pi.on("session_switch", (_event, ctx) => recover("resume", ctx));
    pi.on("session_compact", (_event, ctx) => recover("compact", ctx));
  }

  if (existsSync(EVIDENCE)) {
    pi.on("session_stop", async (_event, ctx) => {
      try {
        if (ctx.agent?.kind === "sub") return;
        const id = session(ctx);
        if (!id) return;
        const result = await runHook(EVIDENCE, { hook_event_name: "Stop", session_id: id, cwd: ctx.cwd }, 10000, ctx);
        const message = record(result)?.systemMessage;
        if (typeof message === "string") warn(ctx, message);
      } catch (error) { warn(ctx, String(error)); }
      return undefined;
    });
  }
}
