from __future__ import annotations

import importlib.util
import os
import subprocess
from pathlib import Path
import tempfile
import unittest
from unittest import mock


SCRIPT = Path(__file__).with_name("native_smoke.py")
SPEC = importlib.util.spec_from_file_location("native_smoke", SCRIPT)
assert SPEC and SPEC.loader
MODULE = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(MODULE)


class NativeSmokeContractTest(unittest.TestCase):
    def test_ownership_requires_passed_response_status(self) -> None:
        assessment = MODULE.assess(
            {"mode": "ownership", "expected_skills": ["review-pr"]},
            {
                "returncode": 0,
                "contract": {
                    "selected_skills": ["review-pr"],
                    "status": "blocked",
                    "summary": "skill was selected but not loaded",
                },
            },
        )

        self.assertEqual(assessment["status"], "blocked")

    def test_invalid_response_contracts_are_structured_failures(self) -> None:
        valid = {
            "selected_skills": ["review-pr"],
            "status": "passed",
            "summary": "selected from native discovery",
        }
        invalid = [
            {**valid, "selected_skills": None},
            {**valid, "selected_skills": [{}]},
            {**valid, "summary": None},
            {**valid, "status": "unknown"},
            {**valid, "extra": True},
        ]
        for contract in invalid:
            with self.subTest(contract=contract):
                assessment = MODULE.assess(
                    {"mode": "ownership", "expected_skills": ["review-pr"]},
                    {"returncode": 0, "contract": contract},
                )
                self.assertEqual(assessment["status"], "fail")

    def test_native_cli_nonzero_exit_is_failure(self) -> None:
        assessment = MODULE.assess(
            {"mode": "ownership", "expected_skills": []},
            {"returncode": 2, "stderr": "unknown option", "contract": None},
        )
        self.assertEqual(assessment, {"status": "fail", "reason": "unknown option"})

    def test_native_cli_timeout_is_failure_record(self) -> None:
        timeout = subprocess.TimeoutExpired(["codex", "exec"], 5, stderr="hung")
        with mock.patch.object(MODULE.subprocess, "run", side_effect=timeout):
            execution = MODULE.run(["codex", "exec"], cwd=Path.cwd(), env={}, timeout=5)

        self.assertEqual(execution["returncode"], 124)
        self.assertIn("timed out after 5s", execution["stderr"])
        self.assertEqual(
            MODULE.assess(
                {"mode": "ownership", "expected_skills": []},
                {**execution, "contract": None},
            )["status"],
            "fail",
        )

    def test_semantic_success_requires_definition_and_reference_locations(self) -> None:
        case = {
            "mode": "behavior",
            "expected_skills": ["semantic-code-intelligence"],
            "expected_status": "passed",
            "must_contain": ["target_value", "lib.rs"],
            "expected_semantic_trace": {
                "definition": ["src/lib.rs:1"],
                "references": ["src/lib.rs:3", "src/lib.rs:5"],
            },
        }
        execution = {
            "returncode": 0,
            "contract": {
                "selected_skills": ["semantic-code-intelligence"],
                "status": "passed",
                "summary": "target_value locations in lib.rs",
            },
            "events": [],
        }
        self.assertEqual(MODULE.assess(case, execution)["status"], "fail")

        execution["events"] = [
            {
                "type": "tool_execution_end",
                "toolName": "lsp",
                "result": {
                    "content": [{"type": "text", "text": "[src/lib.rs#L1]"}],
                    "details": {"action": "definition", "success": True},
                    "isError": False,
                },
            },
            {
                "type": "tool_execution_end",
                "toolName": "lsp",
                "result": {
                    "content": [
                        {"type": "text", "text": "[src/lib.rs#L3]\\n[src/lib.rs#L5]"}
                    ],
                    "details": {"action": "references", "success": True},
                    "isError": False,
                },
            },
        ]
        self.assertEqual(MODULE.assess(case, execution)["status"], "passed")

    def test_structured_semantic_locations_use_zero_based_lsp_lines(self) -> None:
        location = {
            "uri": "file:///tmp/fixture/src/lib.rs",
            "range": {"start": {"line": 2, "character": 0}},
        }
        self.assertTrue(MODULE.result_contains_location(location, "src/lib.rs:3"))
        location["range"]["start"]["line"] = 3
        self.assertFalse(MODULE.result_contains_location(location, "src/lib.rs:3"))
        mixed_locations = {
            "details": {"request": {"file": "src/lib.rs", "line": 3}},
            "locations": [
                {"uri": "file:///tmp/fixture/other.rs", "range": {"start": {"line": 2}}},
                {"uri": "file:///tmp/fixture/src/lib.rs", "range": {"start": {"line": 4}}},
            ],
        }
        self.assertFalse(
            MODULE.result_contains_location(mixed_locations, "src/lib.rs:3")
        )
        echoed_request = {
            "content": [{"type": "text", "text": "[other.rs#L3]"}],
            "details": {"request": {"position": "src/lib.rs:3"}},
        }
        self.assertFalse(
            MODULE.result_contains_location(echoed_request, "src/lib.rs:3")
        )

    def test_codex_case_loads_disposable_plugin_config(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            work = Path(directory)
            with mock.patch.object(
                MODULE,
                "run",
                return_value={"returncode": 0, "stdout": "", "stderr": ""},
            ) as runner:
                MODULE.codex_case(
                    {"id": "ownership", "mode": "ownership", "prompt": "inspect this PR"},
                    work,
                    {},
                    [{"name": "code-review:review-pr", "description": "explicit PR review"}],
                )

        command = runner.call_args.args[0]
        self.assertNotIn("--ignore-user-config", command)
        self.assertIn(
            'plugins."code-intelligence@sonsu-marketplace".mcp_servers.mcpls.enabled=false',
            command,
        )
        self.assertNotIn("Bare skill names available", command[-1])
        self.assertIn("code-review:review-pr", command[-1])

    def test_cli_versions_only_query_selected_hosts(self) -> None:
        with mock.patch.object(MODULE, "command_version", return_value="codex-cli 1.0") as version:
            self.assertEqual(
                MODULE.selected_cli_versions(["codex"]),
                {"codex": "codex-cli 1.0"},
            )
        version.assert_called_once_with("codex")

    def test_missing_cli_version_is_structured_as_none(self) -> None:
        self.assertIsNone(MODULE.command_version("sonsu-cli-that-does-not-exist"))

    def test_omp_profile_is_blocked_when_not_explicitly_supplied(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            work = Path(directory) / "work"
            work.mkdir()
            with mock.patch.dict(os.environ, {"PI_CODING_AGENT_DIR": ""}, clear=False):
                _, blocker = MODULE.prepare_omp(work)

        self.assertIn("PI_CODING_AGENT_DIR", blocker)

    def test_omp_profile_is_copied_into_disposable_directory(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            source = root / "source-agent"
            source.mkdir()
            (source / "agent.db").write_bytes(b"credential fixture")
            (source / "models.db").write_bytes(b"model fixture")
            work = root / "work"
            work.mkdir()
            with mock.patch.dict(
                os.environ,
                {
                    "PI_CODING_AGENT_DIR": str(source),
                    "ANTHROPIC_API_KEY": "must-not-survive",
                },
                clear=False,
            ):
                env, blocker = MODULE.prepare_omp(work)

            destination = Path(env["PI_CODING_AGENT_DIR"])
            self.assertIsNone(blocker)
            self.assertNotEqual(destination, source)
            self.assertEqual((destination / "agent.db").read_bytes(), b"credential fixture")
            self.assertEqual((destination / "models.db").read_bytes(), b"model fixture")
            self.assertNotIn("ANTHROPIC_API_KEY", env)


if __name__ == "__main__":
    unittest.main()
