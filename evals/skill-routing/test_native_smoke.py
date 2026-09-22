from __future__ import annotations

import importlib.util
import os
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
