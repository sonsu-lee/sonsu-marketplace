from __future__ import annotations

import json
import sqlite3
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

    def test_fingerprint_trims_outer_whitespace_and_normalizes_filter_order(self) -> None:
        first = self.query_contract()
        second = {
            "strategy_version": "code-search-v1",
            "version": "1.x",
            "framework": "Tokio",
            "language": "Rust",
            "filters": {"archived": False, "path": "src"},
            "query": " retry_with_backoff lang:rust ",
            "provider": "GitHub",
        }

        first_result = self.run_cli("fingerprint", "--input", "-", payload=first)
        second_result = self.run_cli("fingerprint", "--input", "-", payload=second)

        self.assertEqual(
            json.loads(first_result.stdout)["query_fingerprint"],
            json.loads(second_result.stdout)["query_fingerprint"],
        )

    def test_fingerprint_preserves_semantically_meaningful_string_whitespace(self) -> None:
        first = self.query_contract()
        first["query"] = "/foo  bar/"
        first["filters"]["pattern"] = "alpha  beta"
        second = self.query_contract()
        second["query"] = "/foo bar/"
        second["filters"]["pattern"] = "alpha beta"

        first_result = self.run_cli("fingerprint", "--input", "-", payload=first)
        second_result = self.run_cli("fingerprint", "--input", "-", payload=second)

        self.assertNotEqual(
            json.loads(first_result.stdout)["query_fingerprint"],
            json.loads(second_result.stdout)["query_fingerprint"],
        )

    def test_github_repository_forms_share_one_artifact_identity(self) -> None:
        with tempfile.TemporaryDirectory() as raw_directory:
            database = self.init_database(Path(raw_directory))
            first_payload = self.record_payload()
            second_payload = self.record_payload()
            second_payload["artifacts"][0]["canonical_repository"] = (
                "http://GitHub.com/Example/Retry.git/"
            )

            first = self.run_cli(
                "record-run", "--db", str(database), "--input", "-", payload=first_payload
            )
            second = self.run_cli(
                "record-run", "--db", str(database), "--input", "-", payload=second_payload
            )
            lookup = self.run_cli(
                "lookup", "--db", str(database), "--input", "-", payload=self.query_contract()
            )

            self.assertEqual(1, json.loads(first.stdout)["unique_artifacts_added"])
            self.assertEqual(0, json.loads(second.stdout)["unique_artifacts_added"])
            artifacts = json.loads(lookup.stdout)["artifacts"]
            self.assertEqual(1, len(artifacts))
            self.assertEqual("https://github.com/example/retry", artifacts[0]["canonical_repository"])

    def test_symbol_identity_ignores_a_supplemental_line_range(self) -> None:
        with tempfile.TemporaryDirectory() as raw_directory:
            database = self.init_database(Path(raw_directory))
            self.run_cli(
                "record-run", "--db", str(database), "--input", "-", payload=self.record_payload()
            )
            moved_range = self.record_payload()
            moved_range["artifacts"][0]["line_start"] = 21
            moved_range["artifacts"][0]["line_end"] = 55
            recorded = self.run_cli(
                "record-run", "--db", str(database), "--input", "-", payload=moved_range
            )

            self.assertEqual(0, json.loads(recorded.stdout)["unique_artifacts_added"])
            artifact = json.loads(
                self.run_cli(
                    "lookup", "--db", str(database), "--input", "-", payload=self.query_contract()
                ).stdout
            )["artifacts"][0]
            self.assertEqual(21, artifact["line_start"])
            self.assertEqual(55, artifact["line_end"])

    def test_object_ids_must_be_exactly_40_or_64_hex_characters(self) -> None:
        with tempfile.TemporaryDirectory() as raw_directory:
            database = self.init_database(Path(raw_directory))
            invalid_commit = self.record_payload()
            invalid_commit["artifacts"][0]["full_commit_sha"] = "a" * 41
            failed_commit = self.run_cli(
                "record-run",
                "--db",
                str(database),
                "--input",
                "-",
                payload=invalid_commit,
                expect_success=False,
            )
            self.assertIn("full 40 or 64 character", failed_commit.stderr)

            invalid_blob = self.record_payload(blob_sha="b" * 63)
            failed_blob = self.run_cli(
                "record-run",
                "--db",
                str(database),
                "--input",
                "-",
                payload=invalid_blob,
                expect_success=False,
            )
            self.assertIn("full 40 or 64 character", failed_blob.stderr)

            valid = self.record_payload(blob_sha="b" * 64)
            valid["artifacts"][0]["full_commit_sha"] = "a" * 64
            self.run_cli(
                "record-run", "--db", str(database), "--input", "-", payload=valid
            )

    def test_symbol_must_be_a_non_empty_string_when_present(self) -> None:
        with tempfile.TemporaryDirectory() as raw_directory:
            database = self.init_database(Path(raw_directory))
            payload = self.record_payload()
            payload["artifacts"][0]["symbol"] = 123

            result = self.run_cli(
                "record-run",
                "--db",
                str(database),
                "--input",
                "-",
                payload=payload,
                expect_success=False,
            )

            self.assertIn("artifact.symbol must be a non-empty string", result.stderr)

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

    def test_database_constraint_rejects_cataloging_a_rejected_evaluation(self) -> None:
        with tempfile.TemporaryDirectory() as raw_directory:
            database = self.init_database(Path(raw_directory))
            self.run_cli(
                "record-run", "--db", str(database), "--input", "-", payload=self.record_payload()
            )
            artifact_id = json.loads(
                self.run_cli(
                    "lookup", "--db", str(database), "--input", "-", payload=self.query_contract()
                ).stdout
            )["artifacts"][0]["artifact_id"]
            rejected = {
                "artifact_id": artifact_id,
                "rubric_version": "production-pattern-v1",
                "verdict": "rejected",
                "scores": {"reachability": 0},
                "rationale": "Only an example path was verified.",
                "evaluated_at": "2026-09-02T11:00:00Z",
            }
            self.run_cli("evaluate", "--db", str(database), "--input", "-", payload=rejected)

            with sqlite3.connect(database) as connection:
                with self.assertRaises(sqlite3.IntegrityError):
                    connection.execute(
                        """
                        INSERT INTO catalog_entries(artifact_id, rubric_version, note, promoted_at)
                        VALUES (?, ?, ?, ?)
                        """,
                        (
                            artifact_id,
                            "production-pattern-v1",
                            "Must not be cataloged.",
                            "2026-09-02T12:00:00Z",
                        ),
                    )

    def test_evidence_metadata_change_invalidates_evaluation_and_catalog(self) -> None:
        with tempfile.TemporaryDirectory() as raw_directory:
            database = self.init_database(Path(raw_directory))
            self.run_cli(
                "record-run", "--db", str(database), "--input", "-", payload=self.record_payload()
            )
            artifact_id = json.loads(
                self.run_cli(
                    "lookup", "--db", str(database), "--input", "-", payload=self.query_contract()
                ).stdout
            )["artifacts"][0]["artifact_id"]
            accepted = {
                "artifact_id": artifact_id,
                "rubric_version": "production-pattern-v1",
                "verdict": "accepted",
                "scores": {"reachability": 2},
                "rationale": "Verified production path.",
                "evaluated_at": "2026-09-02T11:00:00Z",
            }
            promotion = {
                "artifact_id": artifact_id,
                "rubric_version": "production-pattern-v1",
                "note": "Reference implementation.",
                "promoted_at": "2026-09-02T12:00:00Z",
            }
            self.run_cli("evaluate", "--db", str(database), "--input", "-", payload=accepted)
            self.run_cli("promote", "--db", str(database), "--input", "-", payload=promotion)

            changed = self.record_payload()
            changed["run"]["searched_at"] = "2026-09-02T13:00:00Z"
            changed["artifacts"][0]["role"] = "example_only"
            changed["artifacts"][0]["license"] = "GPL-3.0"
            changed["artifacts"][0]["immutable_locator"] += "?plain=1"
            recorded = self.run_cli(
                "record-run", "--db", str(database), "--input", "-", payload=changed
            )

            self.assertEqual(1, json.loads(recorded.stdout)["evaluations_invalidated"])
            lookup = json.loads(
                self.run_cli(
                    "lookup", "--db", str(database), "--input", "-", payload=self.query_contract()
                ).stdout
            )
            self.assertEqual([], lookup["artifacts"][0]["evaluations"])
            self.assertEqual("example_only", lookup["artifacts"][0]["role"])
            self.assertEqual(
                [],
                json.loads(self.run_cli("catalog", "--db", str(database)).stdout)["entries"],
            )

    def test_latest_run_uses_search_time_and_serializes_complete_as_boolean(self) -> None:
        with tempfile.TemporaryDirectory() as raw_directory:
            database = self.init_database(Path(raw_directory))
            latest = self.record_payload()
            latest["run"]["searched_at"] = "2026-09-02T12:00:00Z"
            self.run_cli(
                "record-run", "--db", str(database), "--input", "-", payload=latest
            )
            older = self.record_payload()
            older["run"].update(
                {
                    "searched_at": "2026-09-02T11:00:00Z",
                    "status": "partial",
                    "complete": False,
                }
            )
            self.run_cli(
                "record-run", "--db", str(database), "--input", "-", payload=older
            )

            lookup = json.loads(
                self.run_cli(
                    "lookup", "--db", str(database), "--input", "-", payload=self.query_contract()
                ).stdout
            )
            self.assertEqual("2026-09-02T12:00:00Z", lookup["latest_run"]["searched_at"])
            self.assertIs(lookup["latest_run"]["complete"], True)

    def test_lookup_marks_missing_complete_results_stale_and_rejected_results_rejected(self) -> None:
        with tempfile.TemporaryDirectory() as raw_directory:
            database = self.init_database(Path(raw_directory))
            self.run_cli(
                "record-run", "--db", str(database), "--input", "-", payload=self.record_payload()
            )
            artifact_id = json.loads(
                self.run_cli(
                    "lookup", "--db", str(database), "--input", "-", payload=self.query_contract()
                ).stdout
            )["artifacts"][0]["artifact_id"]

            empty_latest = self.record_payload()
            empty_latest["run"]["searched_at"] = "2026-09-02T12:00:00Z"
            empty_latest["run"]["result_count"] = 0
            empty_latest["artifacts"] = []
            self.run_cli(
                "record-run", "--db", str(database), "--input", "-", payload=empty_latest
            )
            stale_lookup = json.loads(
                self.run_cli(
                    "lookup", "--db", str(database), "--input", "-", payload=self.query_contract()
                ).stdout
            )
            self.assertEqual("stale", stale_lookup["artifacts"][0]["reuse_state"])

            rejected = {
                "artifact_id": artifact_id,
                "rubric_version": "production-pattern-v1",
                "verdict": "rejected",
                "scores": {"reachability": 0},
                "rationale": "Hard gate failed.",
                "evaluated_at": "2026-09-02T13:00:00Z",
            }
            self.run_cli("evaluate", "--db", str(database), "--input", "-", payload=rejected)
            rejected_lookup = json.loads(
                self.run_cli(
                    "lookup", "--db", str(database), "--input", "-", payload=self.query_contract()
                ).stdout
            )
            self.assertEqual("rejected", rejected_lookup["artifacts"][0]["reuse_state"])

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

    def test_init_rejects_a_partial_database_with_only_schema_metadata(self) -> None:
        with tempfile.TemporaryDirectory() as raw_directory:
            database = Path(raw_directory) / "partial.sqlite3"
            with sqlite3.connect(database) as connection:
                connection.execute("CREATE TABLE cache_meta (key TEXT PRIMARY KEY, value TEXT NOT NULL)")
                connection.execute(
                    "INSERT INTO cache_meta(key, value) VALUES ('schema_version', '1')"
                )

            result = self.run_cli("init", "--db", str(database), expect_success=False)

            self.assertIn("missing required table", result.stderr)


if __name__ == "__main__":
    unittest.main()
