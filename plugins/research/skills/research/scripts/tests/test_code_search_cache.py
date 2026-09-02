from __future__ import annotations

import json
import stat
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path


SCRIPT = Path(__file__).resolve().parents[1] / "code_search_cache.py"


class CodeSearchCacheCliTests(unittest.TestCase):
    def run_cli(
        self,
        *arguments: str,
        payload: dict | None = None,
        expect_success: bool = True,
    ) -> subprocess.CompletedProcess[str]:
        result = subprocess.run(
            [sys.executable, str(SCRIPT), *arguments],
            input=None if payload is None else json.dumps(payload),
            text=True,
            capture_output=True,
            check=False,
        )
        if expect_success and result.returncode != 0:
            self.fail(f"command failed ({result.returncode}): {result.stderr}")
        if not expect_success and result.returncode == 0:
            self.fail(f"command unexpectedly succeeded: {result.stdout}")
        return result

    def query_contract(self) -> dict:
        return {
            "provider": "github",
            "query": "retry_with_backoff lang:rust",
            "filters": {"path": "src", "archived": False},
            "language": "Rust",
            "framework": "Tokio",
            "version": "1.x",
            "strategy_version": "code-search-v1",
        }

    def artifact(self, *, blob_sha: str | None = None) -> dict:
        artifact = {
            "canonical_repository": "Example/Retry.git",
            "full_commit_sha": "a" * 40,
            "file_path": "src/retry.rs",
            "symbol": "retry_with_backoff",
            "line_start": 20,
            "line_end": 54,
            "immutable_locator": "https://github.com/example/retry/blob/" + "a" * 40 + "/src/retry.rs#L20-L54",
            "role": "release_path",
            "license": "MIT",
            "verified_at": "2026-09-02T10:00:00Z",
        }
        if blob_sha is not None:
            artifact["blob_sha"] = blob_sha
        return artifact

    def record_payload(self, *, blob_sha: str | None = None) -> dict:
        return {
            "query_contract": self.query_contract(),
            "run": {
                "provider": "github",
                "searched_at": "2026-09-02T10:00:00Z",
                "status": "complete",
                "complete": True,
                "result_count": 1,
            },
            "artifacts": [self.artifact(blob_sha=blob_sha)],
        }

    def init_database(self, directory: Path) -> Path:
        database = directory / "code-search.sqlite3"
        result = self.run_cli("init", "--db", str(database))
        self.assertEqual(1, json.loads(result.stdout)["schema_version"])
        return database

    def test_fingerprint_normalizes_query_whitespace_and_filter_order(self) -> None:
        first = self.query_contract()
        second = {
            "strategy_version": "code-search-v1",
            "version": "1.x",
            "framework": "Tokio",
            "language": "Rust",
            "filters": {"archived": False, "path": "src"},
            "query": " retry_with_backoff   lang:rust ",
            "provider": "GitHub",
        }

        first_result = self.run_cli("fingerprint", "--input", "-", payload=first)
        second_result = self.run_cli("fingerprint", "--input", "-", payload=second)

        self.assertEqual(
            json.loads(first_result.stdout)["query_fingerprint"],
            json.loads(second_result.stdout)["query_fingerprint"],
        )

    def test_repeated_record_reuses_query_and_artifact_identity(self) -> None:
        with tempfile.TemporaryDirectory() as raw_directory:
            database = self.init_database(Path(raw_directory))
            first = self.run_cli(
                "record-run", "--db", str(database), "--input", "-", payload=self.record_payload()
            )
            second = self.run_cli(
                "record-run",
                "--db",
                str(database),
                "--input",
                "-",
                payload=self.record_payload(blob_sha="b" * 40),
            )
            lookup = self.run_cli(
                "lookup", "--db", str(database), "--input", "-", payload=self.query_contract()
            )

            self.assertEqual(1, json.loads(first.stdout)["unique_artifacts_added"])
            self.assertEqual(0, json.loads(second.stdout)["unique_artifacts_added"])
            result = json.loads(lookup.stdout)
            self.assertEqual("hit", result["cache_state"])
            self.assertEqual(1, len(result["artifacts"]))
            self.assertEqual("b" * 40, result["artifacts"][0]["blob_sha"])
            self.assertEqual("reused", result["artifacts"][0]["reuse_state"])
            self.assertTrue(result["artifacts"][0]["mutable_revalidation_required"])

    def test_only_accepted_evaluation_can_enter_catalog(self) -> None:
        with tempfile.TemporaryDirectory() as raw_directory:
            database = self.init_database(Path(raw_directory))
            recorded = self.run_cli(
                "record-run", "--db", str(database), "--input", "-", payload=self.record_payload()
            )
            artifact_id = json.loads(
                self.run_cli(
                    "lookup", "--db", str(database), "--input", "-", payload=self.query_contract()
                ).stdout
            )["artifacts"][0]["artifact_id"]
            self.assertEqual(1, json.loads(recorded.stdout)["artifacts_recorded"])

            rejected = {
                "artifact_id": artifact_id,
                "rubric_version": "production-pattern-v1",
                "verdict": "rejected",
                "scores": {"reachability": 0},
                "rationale": "Only an example path was verified.",
                "evaluated_at": "2026-09-02T11:00:00Z",
            }
            self.run_cli("evaluate", "--db", str(database), "--input", "-", payload=rejected)
            promotion = {
                "artifact_id": artifact_id,
                "rubric_version": "production-pattern-v1",
                "note": "Reference implementation for retry cancellation.",
                "promoted_at": "2026-09-02T12:00:00Z",
            }
            failed = self.run_cli(
                "promote",
                "--db",
                str(database),
                "--input",
                "-",
                payload=promotion,
                expect_success=False,
            )
            self.assertIn("only an accepted evaluation", failed.stderr)

            accepted = {**rejected, "verdict": "accepted", "scores": {"reachability": 2}}
            self.run_cli("evaluate", "--db", str(database), "--input", "-", payload=accepted)
            self.run_cli("promote", "--db", str(database), "--input", "-", payload=promotion)
            catalog = self.run_cli(
                "catalog", "--db", str(database), "--rubric-version", "production-pattern-v1"
            )
            entries = json.loads(catalog.stdout)["entries"]
            self.assertEqual(1, len(entries))
            self.assertEqual("accepted", entries[0]["verdict"])

            demoted = self.run_cli(
                "evaluate", "--db", str(database), "--input", "-", payload=rejected
            )
            self.assertTrue(json.loads(demoted.stdout)["catalog_removed"])
            catalog_after_demote = self.run_cli("catalog", "--db", str(database))
            self.assertEqual([], json.loads(catalog_after_demote.stdout)["entries"])

    def test_raw_code_field_is_rejected(self) -> None:
        with tempfile.TemporaryDirectory() as raw_directory:
            database = self.init_database(Path(raw_directory))
            payload = self.record_payload()
            payload["artifacts"][0]["snippet"] = "fn retry_with_backoff() {}"

            result = self.run_cli(
                "record-run",
                "--db",
                str(database),
                "--input",
                "-",
                payload=payload,
                expect_success=False,
            )

            self.assertIn("unsupported fields: snippet", result.stderr)

    def test_database_path_must_be_absolute_and_new_database_is_private(self) -> None:
        relative = self.run_cli(
            "init", "--db", "relative.sqlite3", expect_success=False
        )
        self.assertIn("--db must be an absolute path", relative.stderr)

        with tempfile.TemporaryDirectory() as raw_directory:
            database = self.init_database(Path(raw_directory))
            mode = stat.S_IMODE(database.stat().st_mode)
            self.assertEqual(0o600, mode)

    def test_init_refuses_to_modify_an_existing_non_cache_file(self) -> None:
        with tempfile.TemporaryDirectory() as raw_directory:
            database = Path(raw_directory) / "existing.sqlite3"
            original = b"not a database\n"
            database.write_bytes(original)

            result = self.run_cli(
                "init", "--db", str(database), expect_success=False
            )

            self.assertNotEqual(0, result.returncode)
            self.assertEqual(original, database.read_bytes())


if __name__ == "__main__":
    unittest.main()
