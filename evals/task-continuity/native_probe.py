#!/usr/bin/env python3
"""Bounded native loading probe, isolated from the user's Codex config and auth.

No model calls, hook trust changes, external services or remote mutations.
Results distinguish native discovery from execution and model compliance.
"""
import argparse
import json
import os
from pathlib import Path
import selectors
import shutil
import subprocess
import time

ROOT = Path(__file__).resolve().parents[2]
PLUGINS = list(json.loads((ROOT / "shared/task-continuity/profiles.json").read_text()))


class Server:
    def __init__(self, home, cwd):
        env = os.environ.copy()
        for key in ("CODEX_THREAD_ID", "OPENAI_API_KEY", "CODEX_API_KEY", "CODEX_AUTH_JSON"):
            env.pop(key, None)
        env["CODEX_HOME"] = str(home)
        self.err = open(home / "stderr.log", "w")
        self.p = subprocess.Popen(["codex", "app-server", "--stdio"], cwd=cwd, env=env,
                                  stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=self.err,
                                  bufsize=0)
        self.selector = selectors.DefaultSelector()
        self.selector.register(self.p.stdout, selectors.EVENT_READ)
        self.buffer = b""
        self.sequence = 0
        self.events = []

    def send(self, message):
        self.p.stdin.write((json.dumps(message) + "\n").encode())
        self.p.stdin.flush()

    def call(self, method, params, timeout=20):
        self.sequence += 1
        current = self.sequence
        self.send({"id": current, "method": method, "params": params})
        deadline = time.monotonic() + timeout
        while time.monotonic() < deadline:
            if b"\n" in self.buffer:
                line, self.buffer = self.buffer.split(b"\n", 1)
                message = json.loads(line)
                self.events.append(message)
                if message.get("id") == current:
                    if "error" in message:
                        raise RuntimeError(method + ": " + json.dumps(message["error"]))
                    return message.get("result")
            elif self.selector.select(max(0, deadline - time.monotonic())):
                chunk = os.read(self.p.stdout.fileno(), 65536)
                if not chunk:
                    raise RuntimeError("app-server closed before " + method)
                self.buffer += chunk
        raise TimeoutError(method)

    def close(self):
        self.p.terminate()
        try:
            self.p.wait(timeout=5)
        except subprocess.TimeoutExpired:
            self.p.kill()
            self.p.wait()
        self.selector.close()
        self.err.close()


def probe(case_root, names):
    home = case_root / "codex-home"
    work = case_root / "workspace"
    home.mkdir(parents=True)
    work.mkdir()
    (home / "config.toml").write_text('[features]\nplugins = true\n')
    marketplace = case_root / "marketplace/.agents/plugins/marketplace.json"
    marketplace.parent.mkdir(parents=True)
    entries = []
    for name in names:
        destination = marketplace.parents[2] / "plugins" / name
        shutil.copytree(ROOT / "plugins" / name, destination, ignore=shutil.ignore_patterns("__pycache__"))
        entries.append({"name": name, "source": {"source": "local", "path": "./plugins/" + name},
                        "policy": {"installation": "AVAILABLE", "authentication": "ON_INSTALL"}})
    marketplace.write_text(json.dumps({"name": "continuity-fixture", "plugins": entries}))
    server = Server(home, work)
    result = {"plugins": names, "discovery": "not_run", "hook_execution": "not_run",
              "manual_compaction": "not_run", "automatic_compaction": "not_run",
              "model_compliance": "not_run"}
    try:
        server.call("initialize", {"clientInfo": {"name": "continuity-eval", "version": "1"},
                                   "capabilities": {"experimentalApi": True}})
        server.send({"method": "initialized"})
        reads = {}
        for name in names:
            params = {"marketplacePath": str(marketplace), "pluginName": name}
            reads[name] = server.call("plugin/read", params)
            server.call("plugin/install", params)
        hooks = server.call("hooks/list", {"cwds": [str(work)]})
        skills = server.call("skills/list", {"cwds": [str(work)], "forceReload": True})
        listed_hooks = [h for row in hooks["data"] for h in row["hooks"]]
        listed_skills = [s for row in skills["data"] for s in row["skills"] if s["name"].endswith("-task-continuity")]
        expected_skills = sorted(name + ":" + name + "-task-continuity" for name in names)
        if sorted(s["name"] for s in listed_skills) != expected_skills:
            raise RuntimeError("native skill count does not match installed plugins")
        for name in names:
            matched = [h for h in listed_hooks if h.get("pluginId") == name + "@continuity-fixture"]
            expected_events = ["sessionStart", "stop"] if name == "engineering" else ["sessionStart"]
            if sorted(h["eventName"] for h in matched) != expected_events:
                raise RuntimeError("missing or mismatched native hook for " + name)
            start = next(h for h in matched if h["eventName"] == "sessionStart")
            if start["matcher"] != "^(compact|resume)$":
                raise RuntimeError("mismatched recovery matcher for " + name)
            if any(h["trustStatus"] != "untrusted" for h in matched):
                raise RuntimeError("unexpected trust state in fresh isolated home")
        if any(row.get("errors") for row in hooks["data"] + skills["data"]):
            raise RuntimeError("native discovery reported errors")
        result.update(discovery="observed", reads=reads, hooks=hooks, skills=skills,
                      limitation="Discovery is not execution. Isolated home has no user auth or trusted hooks; no model calls or trust bypass.")
    except (RuntimeError, TimeoutError, OSError) as error:
        result.update(discovery="inconclusive", error=str(error))
    finally:
        server.close()
        (case_root / "native-events.json").write_text(json.dumps(server.events, ensure_ascii=False, indent=2) + "\n")
    return result


def main():
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("--output", type=Path, required=True)
    p.add_argument("--only", choices=PLUGINS, help="one native case for diagnosis")
    args = p.parse_args()
    args.output = args.output.resolve()
    if args.output.exists():
        p.error("output must be a new directory so prior evidence is preserved")
    args.output.mkdir(mode=0o700, parents=True)
    results = []
    groups = [[args.only]] if args.only else [[p] for p in PLUGINS] + [PLUGINS]
    for i, names in enumerate(groups):
        result = probe(args.output / ("case-" + str(i + 1)), names)
        results.append(result)
        (args.output / "results.json").write_text(json.dumps(results, ensure_ascii=False, indent=2) + "\n")
        print(json.dumps({"plugins": names, "discovery": result["discovery"], "error": result.get("error")}), flush=True)
    return int(any(r["discovery"] != "observed" for r in results))


if __name__ == "__main__":
    raise SystemExit(main())
