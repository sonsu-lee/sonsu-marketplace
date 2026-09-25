"""Behavioral contracts for the local Memory Manager store."""

import json
import importlib.util
import os
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest
from unittest import mock
import sqlite3


SCRIPT = Path(__file__).resolve().parents[2] / "plugins/memory-manager/scripts/memory_store.py"
HOOK = SCRIPT.parents[1] / "hooks/capture.py"


class StoreTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.base = Path(self.temp.name).resolve()
        self.store = self.base / "private-store"
        self.project = self.base / "project-a"
        self.project.mkdir()
        self.other = self.base / "project-b"
        self.other.mkdir()

    def run_store(self, *args, payload=None, cwd=None, expect=0):
        env = os.environ.copy()
        env["SONSU_MEMORY_HOME"] = str(self.store)
        result = subprocess.run(
            [sys.executable, str(SCRIPT), *args, "--cwd", str(cwd or self.project)],
            input=None if payload is None else json.dumps(payload, ensure_ascii=False),
            text=True,
            capture_output=True,
            env=env,
        )
        self.assertEqual(result.returncode, expect, result.stderr + result.stdout)
        return json.loads(result.stdout) if result.stdout else None

    def put(self, title="테스트 명령", body="이 프로젝트는 pnpm test를 사용한다.", **extra):
        return self.run_store("put", payload={
            "decision": "ADD", "scope": "project", "title": title,
            "body": body, "sources": ["repo:AGENTS.md"], **extra,
        })

    def test_add_update_noop_and_supersede_preserve_provenance(self):
        added = self.put()
        self.assertEqual(added["decision"], "ADD")
        self.assertEqual(self.run_store("get", added["id"])["body"], "이 프로젝트는 pnpm test를 사용한다.")

        updated = self.run_store("put", payload={
            "decision": "UPDATE", "scope": "project", "target_id": added["id"],
            "expected_sha256": added["sha256"], "title": "테스트 명령",
            "body": "이 프로젝트는 pnpm test --run을 사용한다.", "sources": ["repo:package.json"],
        })
        self.assertEqual(updated["id"], added["id"])
        self.assertEqual(self.run_store("get", added["id"])["sources"], ["repo:AGENTS.md", "repo:package.json"])
        noop = self.run_store("put", payload={"decision": "NOOP", "scope": "project"})
        self.assertEqual(noop["decision"], "NOOP")

        replacement = self.run_store("put", payload={
            "decision": "SUPERSEDE", "scope": "project", "target_id": added["id"],
            "expected_sha256": updated["sha256"], "title": "테스트 명령",
            "body": "현재는 uv run pytest를 사용한다.", "sources": ["repo:pyproject.toml"],
        })
        self.assertNotEqual(replacement["id"], added["id"])
        self.assertEqual(self.run_store("get", added["id"])["status"], "superseded")
        self.assertIn(added["id"], self.run_store("get", replacement["id"])["supersedes"])
        self.assertEqual([x["id"] for x in self.run_store("search", "테스트")["results"]], [replacement["id"]])

    def test_project_isolation_and_compare_before_write(self):
        added = self.put()
        self.assertEqual(self.run_store("search", "테스트", cwd=self.other)["results"], [])
        stale = self.run_store("put", payload={
            "decision": "UPDATE", "scope": "project", "target_id": added["id"],
            "expected_sha256": "0" * 64, "title": "테스트 명령", "body": "틀린 내용",
            "sources": ["repo:AGENTS.md"],
        }, expect=2)
        self.assertEqual(stale["error"], "conflict")
        self.assertEqual(self.run_store("get", added["id"])["body"], "이 프로젝트는 pnpm test를 사용한다.")

    def test_corrupt_index_is_rebuilt_from_markdown(self):
        added = self.put()
        (self.store / "index.sqlite3").write_bytes(b"broken index")
        result = self.run_store("search", "pnpm")
        self.assertEqual([x["id"] for x in result["results"]], [added["id"]])

    def test_external_markdown_edit_refreshes_search_index(self):
        added = self.put()
        path = Path(added["path"])
        original = path.read_text(encoding="utf-8")
        path.write_text(original.replace("pnpm test", "uv run pytest"), encoding="utf-8")
        self.assertEqual([x["id"] for x in self.run_store("search", "pytest")["results"]], [added["id"]])

    def test_tampered_index_cannot_supply_forged_title_or_match(self):
        added = self.put(title="Original fact", body="stable fact")
        connection = sqlite3.connect(self.store / "index.sqlite3")
        connection.execute("UPDATE memories SET title = 'forged' WHERE id = ?", (added["id"],))
        connection.commit()
        connection.close()
        self.assertEqual(self.run_store("search", "forged")["results"], [])
        result = self.run_store("search", "stable")["results"]
        self.assertEqual(result[0]["title"], "Original fact")

    def test_index_failure_keeps_markdown_usable(self):
        spec = importlib.util.spec_from_file_location("memory_store_test", SCRIPT)
        module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(module)
        key = module.project_key(self.project)
        with mock.patch.object(module, "rebuild_index", side_effect=sqlite3.OperationalError("no fts5")):
            saved = module.put(self.store, key, {"decision": "ADD", "scope": "project",
                                                 "title": "검색 대체", "body": "fallback lookup",
                                                 "sources": ["user:request"]})
            self.assertTrue(saved["index_degraded"])
            found = module.search(self.store, key, "project", "fallback")
            self.assertEqual([x["id"] for x in found["results"]], [saved["id"]])
            self.assertTrue(found["degraded"])

    def test_hook_is_opt_in_and_only_stages_a_candidate(self):
        event = {"session_id": "session-1", "cwd": str(self.project),
                 "hook_event_name": "UserPromptSubmit", "prompt": "기억해 줘: 프로젝트 테스트는 pnpm test"}
        disabled = self.run_store("hook", payload=event)
        self.assertEqual(disabled["status"], "disabled")
        self.assertFalse(self.store.exists())
        self.run_store("capture", "on")
        staged = self.run_store("hook", payload=event)
        self.assertEqual(staged["status"], "staged")
        self.assertEqual(self.run_store("search", "pnpm")["results"], [])
        self.assertEqual(len(self.run_store("pending")["results"]), 1)

    def test_secret_and_symlink_output_are_rejected(self):
        result = self.run_store("put", payload={
            "decision": "ADD", "scope": "project", "title": "secret",
            "body": "api_key = sk-abcdefghijklmnopqrstuvwxyz123456", "sources": ["user:request"],
        }, expect=2)
        self.assertEqual(result["error"], "sensitive_content")
        self.assertFalse(self.store.exists())
        target = self.base / "outside"
        target.mkdir()
        self.store.symlink_to(target, target_is_directory=True)
        result = self.run_store("put", payload={
            "decision": "ADD", "scope": "project", "title": "normal",
            "body": "plain", "sources": ["user:request"],
        }, expect=2)
        self.assertEqual(result["error"], "unsafe_path")
        self.assertEqual(list(target.iterdir()), [])

    def test_common_credentials_are_rejected_in_notes_and_candidates(self):
        for secret in ("AWS_SECRET_ACCESS_KEY=abcdef0123456789",
                       "Authorization: Bearer abcdef0123456789",
                       "-----BEGIN PGP PRIVATE KEY BLOCK-----"):
            with self.subTest(secret=secret[:15]):
                result = self.run_store("put", payload={"decision": "ADD", "scope": "project",
                                                        "title": "secret", "body": secret,
                                                        "sources": ["user:request"]}, expect=2)
                self.assertEqual(result["error"], "sensitive_content")
        self.run_store("capture", "on")
        event = {"hook_event_name": "UserPromptSubmit", "cwd": str(self.project),
                 "prompt": "기억해 줘: Authorization: Bearer abcdef0123456789"}
        self.assertEqual(self.run_store("hook", payload=event)["status"], "sensitive_content")
        self.assertEqual(self.run_store("pending")["results"], [])

    def test_quoted_json_secret_is_rejected_in_notes_and_candidates(self):
        phrase = '설정은 {"password": "fixture-value"}'
        result = self.run_store("put", payload={"decision": "ADD", "scope": "project",
                                                "title": "설정", "body": phrase,
                                                "sources": ["user:request"]}, expect=2)
        self.assertEqual(result["error"], "sensitive_content")
        self.run_store("capture", "on")
        event = {"hook_event_name": "UserPromptSubmit", "cwd": str(self.project),
                 "prompt": "기억해 줘: " + phrase}
        self.assertEqual(self.run_store("hook", payload=event)["status"], "sensitive_content")
        self.assertEqual(self.run_store("pending")["results"], [])

    def test_hook_ignores_explicit_korean_do_not_remember_requests(self):
        self.run_store("capture", "on")
        for phrase in ("이 내용은 기억하지 말아줘", "이 내용은 기억하지 말아 주세요"):
            with self.subTest(phrase=phrase):
                event = {"hook_event_name": "UserPromptSubmit", "cwd": str(self.project),
                         "prompt": phrase}
                self.assertEqual(self.run_store("hook", payload=event)["status"], "ignored")
        self.assertEqual(self.run_store("pending")["results"], [])

    def test_ancestor_symlink_store_is_rejected(self):
        outside = self.base / "outside"
        outside.mkdir()
        link = self.base / "link"
        link.symlink_to(outside, target_is_directory=True)
        env = os.environ.copy()
        env["SONSU_MEMORY_HOME"] = str(link / "nested" / "store")
        result = subprocess.run([sys.executable, str(SCRIPT), "put", "--cwd", str(self.project)],
                                input=json.dumps({"decision": "ADD", "scope": "project",
                                                  "title": "x", "body": "x", "sources": ["user:request"]}),
                                text=True, capture_output=True, env=env)
        self.assertEqual(json.loads(result.stdout)["error"], "unsafe_path")
        self.assertEqual(list(outside.iterdir()), [])

    def test_archive_and_explicit_forget_remove_search_results(self):
        archived = self.put(title="보관할 항목")
        self.run_store("archive", archived["id"], archived["sha256"])
        self.assertEqual(self.run_store("search", "보관")["results"], [])
        removed = self.put(title="삭제할 항목")
        self.run_store("forget", removed["id"], removed["sha256"])
        self.assertEqual(self.run_store("search", "삭제")["results"], [])
        self.assertEqual(self.run_store("get", removed["id"], expect=2)["error"], "not_found")

    def test_linked_worktrees_share_project_notes(self):
        subprocess.run(["git", "init", "-q", str(self.project)], check=True)
        subprocess.run(["git", "-C", str(self.project), "config", "user.email", "test@example.invalid"], check=True)
        subprocess.run(["git", "-C", str(self.project), "config", "user.name", "Test"], check=True)
        (self.project / "README.md").write_text("fixture", encoding="utf-8")
        subprocess.run(["git", "-C", str(self.project), "add", "README.md"], check=True)
        subprocess.run(["git", "-C", str(self.project), "commit", "-qm", "fixture"], check=True)
        linked = self.base / "linked"
        subprocess.run(["git", "-C", str(self.project), "worktree", "add", "-qb", "linked", str(linked)], check=True)
        note = self.put()
        self.assertEqual(self.run_store("get", note["id"], cwd=linked)["id"], note["id"])
        self.assertEqual(self.run_store("search", "pnpm", cwd=self.other)["results"], [])

    def test_relative_git_common_dir_identifies_the_same_project(self):
        spec = importlib.util.spec_from_file_location("memory_store_git_test", SCRIPT)
        module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(module)
        common = self.base / "shared" / ".git"

        def old_git(command, **_):
            if "--path-format=absolute" in command:
                return subprocess.CompletedProcess(command, 1, "", "unknown option")
            relative = os.path.relpath(common, command[2])
            return subprocess.CompletedProcess(command, 0, relative + "\n", "")

        with mock.patch.object(module.subprocess, "run", side_effect=old_git):
            self.assertEqual(module.project_key(self.project), module.project_key(self.other))

    def test_user_scope_is_shared_but_project_scope_is_not(self):
        note = self.run_store("put", payload={"decision": "ADD", "scope": "user", "title": "선호 언어",
                                               "body": "답변은 한국어로 쓴다.", "sources": ["user:request"]})
        self.assertEqual(self.run_store("get", note["id"], "--scope", "user", cwd=self.other)["body"], "답변은 한국어로 쓴다.")
        self.assertEqual(self.run_store("search", "한국어", cwd=self.other)["results"], [])

    def test_hook_skips_secrets_even_after_excerpt_limit_and_uses_event_cwd(self):
        self.run_store("capture", "on", cwd=self.other)
        event = {"hook_event_name": "UserPromptSubmit", "cwd": str(self.other),
                 "prompt": "기억해 줘 " + "a" * 2100 + " api_key=sk-abcdefghijklmnopqrstuvwxyz123456"}
        self.assertEqual(self.run_store("hook", payload=event)["status"], "sensitive_content")
        self.assertEqual(self.run_store("pending", cwd=self.other)["results"], [])
        event["prompt"] = "기억해 줘: 다른 프로젝트의 결정"
        self.assertEqual(self.run_store("hook", payload=event)["status"], "staged")
        self.assertEqual(self.run_store("pending", cwd=self.project)["results"], [])
        self.assertEqual(len(self.run_store("pending", cwd=self.other)["results"]), 1)

    def test_hook_keeps_only_local_window_around_signal(self):
        self.run_store("capture", "on")
        event = {"hook_event_name": "Stop", "cwd": str(self.project),
                 "last_assistant_message": "unrelated " * 500 + "결정했음: 테스트는 pytest" + " trailing" * 500}
        self.assertEqual(self.run_store("hook", payload=event)["status"], "staged")
        candidate = self.run_store("pending")["results"][0]
        self.assertIn("결정했음", candidate["excerpt"])
        self.assertLessEqual(len(candidate["excerpt"]), 730)

    def test_hook_adapter_is_silent_and_fail_open(self):
        env = os.environ.copy()
        env["SONSU_MEMORY_HOME"] = str(self.store)
        result = subprocess.run([sys.executable, str(HOOK)], input="not-json", text=True,
                                capture_output=True, env=env)
        self.assertEqual(result.returncode, 0)
        self.assertEqual(result.stdout, "")
        self.assertIn("capture hook unavailable", result.stderr)

    def test_selective_import_does_not_modify_host_source(self):
        source = self.base / "native-memory.md"
        source.write_text("사용자가 선택한 결정", encoding="utf-8")
        selected = self.run_store("put", payload={"decision": "ADD", "scope": "project",
                                                  "title": "선택한 결정", "body": source.read_text(encoding="utf-8"),
                                                  "sources": ["file:" + str(source)]})
        self.assertEqual(source.read_text(encoding="utf-8"), "사용자가 선택한 결정")
        self.assertEqual(self.run_store("get", selected["id"])["sources"], ["file:" + str(source)])

    def test_note_path_symlink_does_not_allow_external_write(self):
        initial = self.put()
        note = self.run_store("get", initial["id"])
        target = self.base / "outside.md"
        target.write_text("outside", encoding="utf-8")
        note_path = Path(initial["path"])
        note_path.unlink()
        note_path.symlink_to(target)
        result = self.run_store("put", payload={"decision": "UPDATE", "scope": "project",
                                               "target_id": initial["id"], "expected_sha256": note["sha256"],
                                               "title": "변경", "body": "변경", "sources": ["user:request"]}, expect=2)
        self.assertEqual(result["error"], "unsafe_path")
        self.assertEqual(target.read_text(encoding="utf-8"), "outside")

    def test_malformed_or_cross_project_metadata_cannot_poison_search_or_put(self):
        damaged = self.put(title="손상될 항목")
        path = Path(damaged["path"])
        path.write_text(path.read_text(encoding="utf-8").replace('"supersedes": []', '"supersedes": null'),
                        encoding="utf-8")
        saved = self.put(title="새 항목", body="valid searchable fact")
        self.assertEqual(self.run_store("get", saved["id"])["title"], "새 항목")
        self.assertIn(path.name, self.run_store("audit")["invalid_files"])
        self.assertEqual([x["id"] for x in self.run_store("search", "searchable")["results"]], [saved["id"]])
        second = Path(saved["path"])
        spec = importlib.util.spec_from_file_location("memory_store_scope_test", SCRIPT)
        module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(module)
        other_key = module.project_key(self.other)
        original = second.read_text(encoding="utf-8")
        second.write_text(original.replace('"project": "' + module.project_key(self.project) + '"',
                                           '"project": "' + other_key + '"'), encoding="utf-8")
        (self.store / "index.sqlite3").write_bytes(b"broken index")
        self.assertEqual(self.run_store("search", "searchable", cwd=self.other)["results"], [])

    def test_archived_and_superseded_targets_cannot_be_updated_again(self):
        archived = self.put(title="보관")
        self.run_store("archive", archived["id"], archived["sha256"])
        archived_sha = self.run_store("get", archived["id"])["sha256"]
        for decision in ("UPDATE", "SUPERSEDE"):
            result = self.run_store("put", payload={"decision": decision, "scope": "project",
                                                    "target_id": archived["id"], "expected_sha256": archived_sha,
                                                    "title": "재활성", "body": "should not appear",
                                                    "sources": ["user:request"]}, expect=2)
            self.assertEqual(result["error"], "inactive_target")
        source = self.put(title="대체 전")
        self.run_store("put", payload={"decision": "SUPERSEDE", "scope": "project",
                                       "target_id": source["id"], "expected_sha256": source["sha256"],
                                       "title": "대체 후", "body": "new truth", "sources": ["user:request"]})
        old_sha = self.run_store("get", source["id"])["sha256"]
        self.assertEqual(self.run_store("put", payload={"decision": "SUPERSEDE", "scope": "project",
                                                        "target_id": source["id"], "expected_sha256": old_sha,
                                                        "title": "분기", "body": "second successor",
                                                        "sources": ["user:request"]}, expect=2)["error"], "inactive_target")

    def test_audit_lists_all_items_and_broken_repo_sources(self):
        source = self.project / "AGENTS.md"
        source.write_text("evidence", encoding="utf-8")
        first = self.put(title="테스트 명령 A", body="첫 주장")
        second = self.put(title="테스트 명령 B", body="상충하는 주장")
        source.unlink()
        result = self.run_store("audit")
        self.assertEqual({x["id"] for x in result["items"]}, {first["id"], second["id"]})
        self.assertEqual({x["id"] for x in result["broken_sources"]}, {first["id"], second["id"]})

    def test_superseded_historical_source_is_not_an_active_broken_reference(self):
        old_source = self.project / "old.md"
        old_source.write_text("old", encoding="utf-8")
        original = self.run_store("put", payload={"decision": "ADD", "scope": "project",
                                                  "title": "옛 절차", "body": "old workflow",
                                                  "sources": ["repo:old.md"]})
        new_source = self.project / "new.md"
        new_source.write_text("new", encoding="utf-8")
        replacement = self.run_store("put", payload={"decision": "SUPERSEDE", "scope": "project",
                                                     "target_id": original["id"],
                                                     "expected_sha256": original["sha256"],
                                                     "title": "새 절차", "body": "new workflow",
                                                     "sources": ["repo:new.md"]})
        old_source.unlink()
        result = self.run_store("audit")
        self.assertEqual(result["broken_sources"], [])
        self.assertEqual({x["id"] for x in result["items"]}, {original["id"], replacement["id"]})

    def test_foreign_supersedes_claim_cannot_hide_project_memory(self):
        first = self.put(title="A unique fact", body="alpha memory")
        foreign = self.run_store("put", cwd=self.other, payload={"decision": "ADD", "scope": "project",
                                                                 "title": "B fact", "body": "beta memory",
                                                                 "sources": ["user:request"]})
        path = Path(foreign["path"])
        path.write_text(path.read_text(encoding="utf-8").replace('"supersedes": []',
                                                                 '"supersedes": ["' + first["id"] + '"]'),
                        encoding="utf-8")
        self.assertEqual([x["id"] for x in self.run_store("search", "alpha")["results"]], [first["id"]])

    def test_candidate_dismissal_and_nonboolean_config(self):
        self.run_store("capture", "on")
        event = {"hook_event_name": "UserPromptSubmit", "cwd": str(self.project), "prompt": "기억해 줘: 판정할 후보"}
        self.run_store("hook", payload=event)
        candidate = self.run_store("pending")["results"][0]
        self.assertEqual(self.run_store("dismiss", candidate["id"], candidate["sha256"])["status"], "dismissed")
        self.assertEqual(self.run_store("pending")["results"], [])
        config = next((self.store / "settings").glob("*.json"))
        config.write_text('{"enabled":"false"}', encoding="utf-8")
        self.assertEqual(self.run_store("hook", payload=event, expect=2)["error"], "invalid_config")
        self.assertEqual(self.run_store("pending")["results"], [])

    def test_capture_off_recheck_prevents_late_stage(self):
        spec = importlib.util.spec_from_file_location("memory_store_race_test", SCRIPT)
        module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(module)
        key = module.project_key(self.project)
        event = {"hook_event_name": "UserPromptSubmit", "prompt": "기억해 줘: 경합 후보"}
        with mock.patch.object(module, "capture_config", side_effect=[{"enabled": True}, {"enabled": False}]):
            self.assertEqual(module.stage_hook(self.store, key, event)["status"], "disabled")
        self.assertEqual(module.pending(self.store, key)["results"], [])

    def test_simultaneous_updates_allow_exactly_one_writer(self):
        original = self.put(title="경합 항목")
        env = os.environ.copy()
        env["SONSU_MEMORY_HOME"] = str(self.store)
        processes = []
        for index in range(2):
            process = subprocess.Popen([sys.executable, str(SCRIPT), "put", "--cwd", str(self.project)],
                                       stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.PIPE,
                                       text=True, env=env)
            payload = {"decision": "UPDATE", "scope": "project", "target_id": original["id"],
                       "expected_sha256": original["sha256"], "title": "경합 항목",
                       "body": "value " + str(index), "sources": ["fixture:parallel"]}
            processes.append((process, payload))
        results = []
        for process, payload in processes:
            process.stdin.write(json.dumps(payload))
            process.stdin.close()
        for process, _ in processes:
            process.wait(timeout=10)
            output = process.stdout.read()
            process.stdout.close()
            process.stderr.close()
            results.append((process.returncode, json.loads(output)))
        self.assertEqual(sorted(code for code, _ in results), [0, 2])
        self.assertEqual([value.get("error") for code, value in results if code == 2], ["conflict"])
        self.assertIn(self.run_store("get", original["id"])["body"], ("value 0", "value 1"))

    def test_supersede_keeps_successor_if_old_status_write_fails_after_replace(self):
        original = self.put(title="이전 결정", body="old decision")
        spec = importlib.util.spec_from_file_location("memory_store_fsync_test", SCRIPT)
        module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(module)
        real_fsync = module.os.fsync
        calls = 0

        def fail_after_old_replace(fd):
            nonlocal calls
            calls += 1
            if calls == 4:
                raise OSError("directory fsync failed after replacement")
            return real_fsync(fd)

        with mock.patch.object(module.os, "fsync", side_effect=fail_after_old_replace):
            with self.assertRaises(OSError):
                module.put(self.store, module.project_key(self.project), {
                    "decision": "SUPERSEDE", "scope": "project", "target_id": original["id"],
                    "expected_sha256": original["sha256"], "title": "새 결정",
                    "body": "new decision", "sources": ["user:request"],
                })
        notes = [note for note, _ in module.active_notes(self.store)]
        self.assertEqual([note["title"] for note in notes], ["새 결정"])

    def test_supersede_discards_successor_if_old_status_write_fails_before_replace(self):
        original = self.put(title="이전 결정", body="old decision")
        spec = importlib.util.spec_from_file_location("memory_store_rollback_test", SCRIPT)
        module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(module)
        real_atomic_write = module.atomic_write

        def fail_before_old_replace(root, path, data):
            if path.name == original["id"] + ".md":
                raise OSError("old status was not replaced")
            return real_atomic_write(root, path, data)

        with mock.patch.object(module, "atomic_write", side_effect=fail_before_old_replace):
            with self.assertRaises(OSError):
                module.put(self.store, module.project_key(self.project), {
                    "decision": "SUPERSEDE", "scope": "project", "target_id": original["id"],
                    "expected_sha256": original["sha256"], "title": "새 결정",
                    "body": "new decision", "sources": ["user:request"],
                })
        self.assertEqual([note["id"] for note, _ in module.active_notes(self.store)], [original["id"]])

    def test_interrupted_supersede_does_not_revive_old_note(self):
        spec = importlib.util.spec_from_file_location("memory_store_crash_test", SCRIPT)
        module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(module)
        key = module.project_key(self.project)
        real_atomic_write = module.atomic_write

        for action in ("archive", "forget", "supersede"):
            with self.subTest(action=action), tempfile.TemporaryDirectory(dir=self.base) as location:
                root = Path(location) / "store"
                original = module.put(root, key, {"decision": "ADD", "scope": "project",
                                                  "title": "이전 결정", "body": "old decision",
                                                  "sources": ["user:request"]})

                def stop_after_new_note(store_root, path, data):
                    real_atomic_write(store_root, path, data)
                    if path.name != original["id"] + ".md":
                        raise SystemExit("interrupted before old status update")

                with mock.patch.object(module, "atomic_write", side_effect=stop_after_new_note):
                    with self.assertRaises(SystemExit):
                        module.put(root, key, {"decision": "SUPERSEDE", "scope": "project",
                                               "target_id": original["id"],
                                               "expected_sha256": original["sha256"],
                                               "title": "새 결정", "body": "new decision",
                                               "sources": ["user:request"]})
                successor = next(note for note, _ in module.iter_notes(root) if note["id"] != original["id"])
                if action in ("archive", "forget"):
                    module.change_status(root, key, "project", successor["id"], successor["sha256"], action)
                    self.assertEqual(module.active_notes(root), [])
                else:
                    latest = module.put(root, key, {"decision": "SUPERSEDE", "scope": "project",
                                                    "target_id": successor["id"],
                                                    "expected_sha256": successor["sha256"],
                                                    "title": "최신 결정", "body": "latest decision",
                                                    "sources": ["user:request"]})
                    self.assertEqual([note["id"] for note, _ in module.active_notes(root)], [latest["id"]])


if __name__ == "__main__":
    unittest.main()
