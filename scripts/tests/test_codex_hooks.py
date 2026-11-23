"""Check how the Codex check reports package hooks from hooks/list."""

import json
import os
from pathlib import Path
import stat
import sys
import tempfile
import unittest

SCRIPTS = Path(__file__).resolve().parents[1]
ROOT = SCRIPTS.parent
sys.path.insert(0, str(SCRIPTS))

from check_plugins import codex_app_server, codex_hooks_result, declares_codex_hooks  # noqa: E402

MARKET = "sonsu-marketplace"
CACHE = "/private/tmp/home/.codex/plugins/cache"
ADDED = {
    "development": {"pluginId": f"development@{MARKET}",
                    "installedPath": f"{CACHE}/{MARKET}/development/0.1.3"},
    "review": {"pluginId": f"review@{MARKET}",
               "installedPath": f"{CACHE}/{MARKET}/review/0.1.0"},
}


def hook(event, source="plugin", plugin_id=f"development@{MARKET}", order=0,
         enabled=True, trust="untrusted"):
    # Field names follow HooksListResponse in Codex 0.163.0 and 0.171.0.
    return {"key": f"{plugin_id}:{event}:{order}", "eventName": event, "source": source,
            "pluginId": plugin_id, "displayOrder": order, "enabled": enabled,
            "trustStatus": trust, "sourcePath": "/x/hooks.json", "isManaged": False,
            "currentHash": "sha256:0", "timeoutSec": 600}


def listing(hooks=(), warnings=(), errors=()):
    return {"id": 3, "result": {"data": [{"cwd": "/tmp/target", "hooks": list(hooks),
                                          "warnings": list(warnings), "errors": list(errors)}]}}


class CodexHooksReportTests(unittest.TestCase):
    def test_counts_only_hooks_the_package_owns(self):
        reply = listing([
            hook("sessionStart", order=1),
            hook("sessionStart", order=2),
            hook("preToolUse", order=3, enabled=False, trust="trusted"),
            hook("stop", source="user", plugin_id=None),
            hook("sessionStart", plugin_id=f"other@{MARKET}"),
            hook("sessionEnd", plugin_id="development@another-marketplace"),
            hook("sessionEnd", source="project", plugin_id=f"development@{MARKET}"),
        ])
        result = codex_hooks_result(reply, ADDED, {"development"})
        self.assertTrue(result.ok)
        self.assertEqual(result.detail, f"development@{MARKET} 3 hooks listed: "
                         "sessionStart (enabled, untrusted) x2, preToolUse (disabled, trusted)")

    def test_reports_no_owned_hooks_without_failing(self):
        reply = listing([hook("stop", source="user", plugin_id=None),
                         hook("sessionStart", plugin_id=f"other@{MARKET}")])
        result = codex_hooks_result(reply, ADDED, {"development"})
        self.assertTrue(result.ok)
        self.assertEqual(result.detail, f"development@{MARKET} no hooks listed")

    def test_reports_listed_hooks_of_a_package_without_declared_hooks(self):
        reply = listing([hook("sessionStart", plugin_id=f"review@{MARKET}")])
        result = codex_hooks_result(reply, ADDED, {"development"})
        self.assertEqual(result.detail, f"development@{MARKET} no hooks listed; "
                         f"review@{MARKET} 1 hook listed: sessionStart (enabled, untrusted)")
        self.assertEqual(codex_hooks_result(listing(), ADDED, set()).detail,
                         "no package declares or lists hooks")

    def test_fails_only_on_problems_naming_a_package_install(self):
        development = ADDED["development"]["installedPath"]
        reply = listing(warnings=[
            "failed to parse plugin hooks config /home/.codex/hooks.json: bad",
            f"failed to parse plugin hooks config {CACHE}/{MARKET}/other/1/hooks/hooks.json: bad",
        ])
        self.assertTrue(codex_hooks_result(reply, ADDED, {"development"}).ok)
        for reply in (
            listing(warnings=[f"failed to parse plugin hooks config {development}/hooks/x.json"]),
            listing(errors=[{"path": f"{development}/hooks/x.json", "message": "bad"}]),
        ):
            with self.subTest(reply=reply):
                result = codex_hooks_result(reply, ADDED, {"development"})
                self.assertFalse(result.ok)
                self.assertIn(f"development@{MARKET}: ", result.detail)

    def test_request_error_fails(self):
        result = codex_hooks_result({"id": 3, "error": {"message": "unknown method"}},
                                    ADDED, {"development"})
        self.assertFalse(result.ok)
        self.assertIn("unknown method", result.detail)

    def test_development_manifest_declares_codex_hooks(self):
        self.assertTrue(declares_codex_hooks(ROOT / "plugins/development"))
        with tempfile.TemporaryDirectory() as tmp:
            (Path(tmp) / "plugin.json").write_text(json.dumps({"name": "plain"}))
            self.assertFalse(declares_codex_hooks(Path(tmp)))


FAKE_APP_SERVER = """\
import json, os, sys
with open(os.environ["FAKE_LOG"], "a") as log:
    log.write(" ".join(sys.argv[1:]) + "\\n")
for line in sys.stdin:
    message = json.loads(line)
    if "id" not in message:
        continue
    print(json.dumps({"method": "notice", "params": {}}), flush=True)
    print(json.dumps({"id": message["id"], "result": {"method": message["method"],
                                                      "params": message.get("params")}}),
          flush=True)
"""


class CodexAppServerTests(unittest.TestCase):
    def test_sends_every_request_in_one_session(self):
        with tempfile.TemporaryDirectory() as tmp:
            bin_dir = Path(tmp)
            fake = bin_dir / "codex"
            fake.write_text(f"#!{sys.executable}\n{FAKE_APP_SERVER}")
            fake.chmod(fake.stat().st_mode | stat.S_IXUSR)
            log = bin_dir / "launches.log"
            env = {"PATH": f"{bin_dir}{os.pathsep}{os.environ['PATH']}",
                   "FAKE_LOG": str(log)}
            replies = codex_app_server(env, bin_dir, [
                ("skills/list", {"cwds": ["/t"], "forceReload": True}),
                ("hooks/list", {"cwds": ["/t"]}),
            ])
            self.assertEqual(log.read_text(), "app-server\n")
        self.assertEqual([r["id"] for r in replies], [2, 3])
        self.assertEqual([r["result"]["method"] for r in replies], ["skills/list", "hooks/list"])
        self.assertEqual(replies[1]["result"]["params"], {"cwds": ["/t"]})


if __name__ == "__main__":
    unittest.main()
