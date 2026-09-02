#!/usr/bin/env python3
"""Metadata-only cache for repeatable external code-pattern research."""

from __future__ import annotations

import argparse
import hashlib
import json
import math
import os
import re
import sqlite3
import sys
from datetime import datetime, timezone
from pathlib import Path, PurePosixPath
from typing import Any
from urllib.parse import urlsplit, urlunsplit


SCHEMA_VERSION = 1
QUERY_KEYS = {
    "provider",
    "query",
    "filters",
    "language",
    "framework",
    "version",
    "strategy_version",
}
ARTIFACT_KEYS = {
    "canonical_repository",
    "full_commit_sha",
    "file_path",
    "symbol",
    "line_start",
    "line_end",
    "blob_sha",
    "immutable_locator",
    "role",
    "license",
    "verified_at",
}
RUN_KEYS = {
    "provider",
    "searched_at",
    "status",
    "complete",
    "next_cursor",
    "result_count",
}
EVALUATION_KEYS = {
    "artifact_id",
    "rubric_version",
    "verdict",
    "scores",
    "rationale",
    "evaluated_at",
}
PROMOTION_KEYS = {
    "artifact_id",
    "rubric_version",
    "note",
    "promoted_at",
}
HEX_OBJECT_ID = re.compile(r"^(?:[0-9a-f]{40}|[0-9a-f]{64})$")
REQUIRED_TABLE_COLUMNS = {
    "cache_meta": {
        "key": ("TEXT", 0, 1),
        "value": ("TEXT", 1, 0),
    },
    "queries": {
        "query_fingerprint": ("TEXT", 0, 1),
        "contract_json": ("TEXT", 1, 0),
        "first_seen_at": ("TEXT", 1, 0),
        "last_seen_at": ("TEXT", 1, 0),
    },
    "search_runs": {
        "run_id": ("INTEGER", 0, 1),
        "query_fingerprint": ("TEXT", 1, 0),
        "searched_at": ("TEXT", 1, 0),
        "provider": ("TEXT", 1, 0),
        "status": ("TEXT", 1, 0),
        "complete": ("INTEGER", 1, 0),
        "next_cursor": ("TEXT", 0, 0),
        "result_count": ("INTEGER", 1, 0),
    },
    "artifacts": {
        "artifact_id": ("TEXT", 0, 1),
        "canonical_repository": ("TEXT", 1, 0),
        "full_commit_sha": ("TEXT", 1, 0),
        "file_path": ("TEXT", 1, 0),
        "symbol": ("TEXT", 0, 0),
        "line_start": ("INTEGER", 0, 0),
        "line_end": ("INTEGER", 0, 0),
        "blob_sha": ("TEXT", 0, 0),
        "immutable_locator": ("TEXT", 0, 0),
        "role": ("TEXT", 0, 0),
        "license": ("TEXT", 0, 0),
        "verified_at": ("TEXT", 1, 0),
        "first_seen_at": ("TEXT", 1, 0),
        "last_seen_at": ("TEXT", 1, 0),
    },
    "query_artifacts": {
        "query_fingerprint": ("TEXT", 1, 1),
        "artifact_id": ("TEXT", 1, 2),
        "first_seen_at": ("TEXT", 1, 0),
        "last_seen_at": ("TEXT", 1, 0),
    },
    "evaluations": {
        "artifact_id": ("TEXT", 1, 1),
        "rubric_version": ("TEXT", 1, 2),
        "verdict": ("TEXT", 1, 0),
        "scores_json": ("TEXT", 1, 0),
        "rationale": ("TEXT", 1, 0),
        "evaluated_at": ("TEXT", 1, 0),
    },
    "catalog_entries": {
        "artifact_id": ("TEXT", 1, 1),
        "rubric_version": ("TEXT", 1, 2),
        "note": ("TEXT", 1, 0),
        "promoted_at": ("TEXT", 1, 0),
    },
}
REQUIRED_FOREIGN_KEYS = {
    "search_runs": {("query_fingerprint", "queries", "query_fingerprint")},
    "query_artifacts": {
        ("query_fingerprint", "queries", "query_fingerprint"),
        ("artifact_id", "artifacts", "artifact_id"),
    },
    "evaluations": {("artifact_id", "artifacts", "artifact_id")},
    "catalog_entries": {
        ("artifact_id", "evaluations", "artifact_id"),
        ("rubric_version", "evaluations", "rubric_version"),
    },
}
REQUIRED_UNIQUE_INDEXES = {
    "search_runs": {("query_fingerprint", "searched_at", "provider")},
    "query_artifacts": {("query_fingerprint", "artifact_id")},
    "evaluations": {("artifact_id", "rubric_version")},
    "catalog_entries": {("artifact_id", "rubric_version")},
}
REQUIRED_TRIGGERS = {
    "catalog_entries_require_accepted_insert",
    "catalog_entries_require_accepted_update",
    "remove_catalog_entry_after_evaluation_demotion",
}


class ContractError(ValueError):
    """Raised when cache input does not satisfy the metadata contract."""


def utc_now() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")


def canonical_json(value: Any) -> str:
    return json.dumps(value, ensure_ascii=False, sort_keys=True, separators=(",", ":"))


def sha256_json(value: Any) -> str:
    return hashlib.sha256(canonical_json(value).encode("utf-8")).hexdigest()


def reject_unknown_keys(value: dict[str, Any], allowed: set[str], label: str) -> None:
    unknown = sorted(set(value) - allowed)
    if unknown:
        raise ContractError(f"{label} contains unsupported fields: {', '.join(unknown)}")


def nonempty_string(value: Any, label: str) -> str:
    if not isinstance(value, str) or not value.strip():
        raise ContractError(f"{label} must be a non-empty string")
    return value.strip()


def normalize_json(value: Any) -> Any:
    if isinstance(value, dict):
        return {str(key): normalize_json(item) for key, item in sorted(value.items())}
    if isinstance(value, list):
        return [normalize_json(item) for item in value]
    if isinstance(value, str):
        return value.strip()
    if isinstance(value, float) and not math.isfinite(value):
        raise ContractError("query contract numbers must be finite")
    if value is None or isinstance(value, (bool, int, float)):
        return value
    raise ContractError(f"unsupported JSON value: {type(value).__name__}")


def normalize_query_contract(value: Any) -> dict[str, Any]:
    if not isinstance(value, dict):
        raise ContractError("query contract must be an object")
    reject_unknown_keys(value, QUERY_KEYS, "query contract")
    provider = nonempty_string(value.get("provider"), "query contract.provider").lower()
    query = nonempty_string(value.get("query"), "query contract.query")
    strategy = nonempty_string(
        value.get("strategy_version"), "query contract.strategy_version"
    )
    normalized: dict[str, Any] = {
        "provider": provider,
        "query": query,
        "strategy_version": strategy,
    }
    for key in ("filters", "language", "framework", "version"):
        if key in value and value[key] not in (None, "", {}, []):
            normalized[key] = normalize_json(value[key])
    return normalized


def query_fingerprint(value: Any) -> tuple[str, dict[str, Any]]:
    normalized = normalize_query_contract(value)
    return sha256_json(normalized), normalized


def normalize_repository(value: Any) -> str:
    repository = nonempty_string(value, "artifact.canonical_repository")
    if re.fullmatch(r"[^/\s]+/[^/\s]+", repository):
        owner, name = repository.removesuffix(".git").split("/", 1)
        return f"https://github.com/{owner.lower()}/{name.lower()}"

    parts = urlsplit(repository)
    if parts.scheme not in {"http", "https"} or not parts.hostname:
        raise ContractError("artifact.canonical_repository must be owner/repo or an HTTP(S) URL")
    host = parts.hostname.lower()
    try:
        port_number = parts.port
    except ValueError as exc:
        raise ContractError("artifact.canonical_repository contains an invalid port") from exc
    scheme = parts.scheme.lower()
    path = parts.path.rstrip("/")
    if path.endswith(".git"):
        path = path[:-4]
    if host == "github.com":
        if port_number not in (None, 80, 443):
            raise ContractError("artifact.canonical_repository contains an unsupported GitHub port")
        path_parts = path.strip("/").split("/")
        if len(path_parts) != 2 or not all(path_parts):
            raise ContractError("artifact.canonical_repository must identify one GitHub owner/repository")
        path = "/" + "/".join(part.lower() for part in path_parts)
        return urlunsplit(("https", host, path, "", ""))
    if not path:
        raise ContractError("artifact.canonical_repository URL must include a repository path")
    default_port = (scheme == "http" and port_number == 80) or (
        scheme == "https" and port_number == 443
    )
    port = "" if port_number is None or default_port else f":{port_number}"
    return urlunsplit((scheme, host + port, path, "", ""))


def normalize_timestamp(value: Any, label: str, default: str | None = None) -> str:
    if value in (None, ""):
        if default is None:
            raise ContractError(f"{label} must be an ISO-8601 timestamp")
        return default
    raw = nonempty_string(value, label)
    try:
        parsed = datetime.fromisoformat(raw.replace("Z", "+00:00"))
    except ValueError as exc:
        raise ContractError(f"{label} must be an ISO-8601 timestamp") from exc
    if parsed.tzinfo is None:
        raise ContractError(f"{label} must include a timezone")
    return parsed.astimezone(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")


def normalize_artifact(value: Any, default_time: str) -> tuple[str, dict[str, Any]]:
    if not isinstance(value, dict):
        raise ContractError("artifact must be an object")
    reject_unknown_keys(value, ARTIFACT_KEYS, "artifact")
    repository = normalize_repository(value.get("canonical_repository"))
    full_commit_sha = nonempty_string(value.get("full_commit_sha"), "artifact.full_commit_sha").lower()
    if not HEX_OBJECT_ID.fullmatch(full_commit_sha):
        raise ContractError("artifact.full_commit_sha must be a full 40 or 64 character hex object ID")

    file_path = nonempty_string(value.get("file_path"), "artifact.file_path").replace("\\", "/")
    path = PurePosixPath(file_path)
    if path.is_absolute() or ".." in path.parts or file_path in {".", ""}:
        raise ContractError("artifact.file_path must be a repository-relative POSIX path")
    file_path = str(path)

    symbol = None
    if "symbol" in value and value["symbol"] is not None:
        symbol = nonempty_string(value["symbol"], "artifact.symbol")
    line_start = value.get("line_start")
    line_end = value.get("line_end")
    if line_start is not None and (not isinstance(line_start, int) or isinstance(line_start, bool) or line_start < 1):
        raise ContractError("artifact.line_start must be a positive integer")
    if line_end is not None and (not isinstance(line_end, int) or isinstance(line_end, bool) or line_end < 1):
        raise ContractError("artifact.line_end must be a positive integer")
    if line_end is not None and line_start is None:
        raise ContractError("artifact.line_end requires artifact.line_start")
    if line_start is not None and line_end is not None and line_end < line_start:
        raise ContractError("artifact.line_end must not precede artifact.line_start")
    if symbol is None and line_start is None:
        raise ContractError("artifact requires artifact.symbol or artifact.line_start")

    blob_sha = value.get("blob_sha")
    if blob_sha is not None:
        blob_sha = nonempty_string(blob_sha, "artifact.blob_sha").lower()
        if not HEX_OBJECT_ID.fullmatch(blob_sha):
            raise ContractError("artifact.blob_sha must be a full 40 or 64 character hex object ID")

    normalized = {
        "canonical_repository": repository,
        "full_commit_sha": full_commit_sha,
        "file_path": file_path,
        "symbol": symbol,
        "line_start": line_start,
        "line_end": line_end,
    }
    identity = {
        "canonical_repository": repository,
        "full_commit_sha": full_commit_sha,
        "file_path": file_path,
    }
    if symbol is not None:
        identity["symbol"] = symbol
    else:
        identity["line_start"] = line_start
        identity["line_end"] = line_end
    for key in ("immutable_locator", "role", "license"):
        if value.get(key) is not None:
            normalized[key] = nonempty_string(value[key], f"artifact.{key}")
    normalized["blob_sha"] = blob_sha
    normalized["verified_at"] = normalize_timestamp(
        value.get("verified_at"), "artifact.verified_at", default_time
    )
    return sha256_json(identity), normalized


def database_path(raw: str, must_exist: bool) -> Path:
    path = Path(raw)
    if not path.is_absolute():
        raise ContractError("--db must be an absolute path")
    if path.exists() and path.is_symlink():
        raise ContractError("--db must not be a symbolic link")
    if must_exist and not path.is_file():
        raise ContractError("cache database does not exist; run init first")
    if not path.parent.is_dir():
        raise ContractError("the parent directory for --db must already exist")
    return path


def connect_database(path: Path, create: bool) -> sqlite3.Connection:
    existed = path.exists()
    if create and not existed:
        descriptor = os.open(path, os.O_CREAT | os.O_EXCL | os.O_RDWR, 0o600)
        os.close(descriptor)
    connection = sqlite3.connect(path)
    connection.row_factory = sqlite3.Row
    connection.execute("PRAGMA foreign_keys = ON")
    if create:
        if existed:
            ensure_schema(connection)
        else:
            initialize_schema(connection)
            connection.commit()
    else:
        ensure_schema(connection)
    return connection


def initialize_schema(connection: sqlite3.Connection) -> None:
    connection.executescript(
        """
        CREATE TABLE IF NOT EXISTS cache_meta (
            key TEXT PRIMARY KEY,
            value TEXT NOT NULL
        );
        CREATE TABLE IF NOT EXISTS queries (
            query_fingerprint TEXT PRIMARY KEY,
            contract_json TEXT NOT NULL,
            first_seen_at TEXT NOT NULL,
            last_seen_at TEXT NOT NULL
        );
        CREATE TABLE IF NOT EXISTS search_runs (
            run_id INTEGER PRIMARY KEY AUTOINCREMENT,
            query_fingerprint TEXT NOT NULL REFERENCES queries(query_fingerprint),
            searched_at TEXT NOT NULL,
            provider TEXT NOT NULL,
            status TEXT NOT NULL CHECK (status IN ('complete', 'partial', 'failed')),
            complete INTEGER NOT NULL CHECK (complete IN (0, 1)),
            next_cursor TEXT,
            result_count INTEGER NOT NULL CHECK (result_count >= 0),
            UNIQUE (query_fingerprint, searched_at, provider)
        );
        CREATE TABLE IF NOT EXISTS artifacts (
            artifact_id TEXT PRIMARY KEY,
            canonical_repository TEXT NOT NULL,
            full_commit_sha TEXT NOT NULL,
            file_path TEXT NOT NULL,
            symbol TEXT,
            line_start INTEGER,
            line_end INTEGER,
            blob_sha TEXT,
            immutable_locator TEXT,
            role TEXT,
            license TEXT,
            verified_at TEXT NOT NULL,
            first_seen_at TEXT NOT NULL,
            last_seen_at TEXT NOT NULL
        );
        CREATE TABLE IF NOT EXISTS query_artifacts (
            query_fingerprint TEXT NOT NULL REFERENCES queries(query_fingerprint),
            artifact_id TEXT NOT NULL REFERENCES artifacts(artifact_id),
            first_seen_at TEXT NOT NULL,
            last_seen_at TEXT NOT NULL,
            PRIMARY KEY (query_fingerprint, artifact_id)
        );
        CREATE TABLE IF NOT EXISTS evaluations (
            artifact_id TEXT NOT NULL REFERENCES artifacts(artifact_id),
            rubric_version TEXT NOT NULL,
            verdict TEXT NOT NULL CHECK (verdict IN ('accepted', 'partial', 'rejected')),
            scores_json TEXT NOT NULL,
            rationale TEXT NOT NULL,
            evaluated_at TEXT NOT NULL,
            PRIMARY KEY (artifact_id, rubric_version)
        );
        CREATE TABLE IF NOT EXISTS catalog_entries (
            artifact_id TEXT NOT NULL,
            rubric_version TEXT NOT NULL,
            note TEXT NOT NULL,
            promoted_at TEXT NOT NULL,
            PRIMARY KEY (artifact_id, rubric_version),
            FOREIGN KEY (artifact_id, rubric_version)
                REFERENCES evaluations(artifact_id, rubric_version)
        );
        CREATE TRIGGER IF NOT EXISTS catalog_entries_require_accepted_insert
        BEFORE INSERT ON catalog_entries
        FOR EACH ROW
        WHEN NOT EXISTS (
            SELECT 1 FROM evaluations
            WHERE artifact_id = NEW.artifact_id
              AND rubric_version = NEW.rubric_version
              AND verdict = 'accepted'
        )
        BEGIN
            SELECT RAISE(ABORT, 'catalog entry requires an accepted evaluation');
        END;
        CREATE TRIGGER IF NOT EXISTS catalog_entries_require_accepted_update
        BEFORE UPDATE ON catalog_entries
        FOR EACH ROW
        WHEN NOT EXISTS (
            SELECT 1 FROM evaluations
            WHERE artifact_id = NEW.artifact_id
              AND rubric_version = NEW.rubric_version
              AND verdict = 'accepted'
        )
        BEGIN
            SELECT RAISE(ABORT, 'catalog entry requires an accepted evaluation');
        END;
        CREATE TRIGGER IF NOT EXISTS remove_catalog_entry_after_evaluation_demotion
        AFTER UPDATE OF verdict ON evaluations
        FOR EACH ROW
        WHEN NEW.verdict <> 'accepted'
        BEGIN
            DELETE FROM catalog_entries
            WHERE artifact_id = NEW.artifact_id
              AND rubric_version = NEW.rubric_version;
        END;
        """
    )
    row = connection.execute("SELECT value FROM cache_meta WHERE key = 'schema_version'").fetchone()
    if row is None:
        connection.execute(
            "INSERT INTO cache_meta(key, value) VALUES ('schema_version', ?)",
            (str(SCHEMA_VERSION),),
        )
    elif row["value"] != str(SCHEMA_VERSION):
        raise ContractError(f"unsupported schema version: {row['value']}")
    ensure_schema(connection)


def table_columns(connection: sqlite3.Connection, table: str) -> dict[str, tuple[str, int, int]]:
    return {
        row["name"]: (row["type"].upper(), row["notnull"], row["pk"])
        for row in connection.execute(f"PRAGMA table_info({table})")
    }


def unique_indexes(connection: sqlite3.Connection, table: str) -> set[tuple[str, ...]]:
    indexes: set[tuple[str, ...]] = set()
    for row in connection.execute(f"PRAGMA index_list({table})"):
        if row["unique"]:
            index_name = '"' + row["name"].replace('"', '""') + '"'
            columns = tuple(
                item["name"]
                for item in connection.execute(f"PRAGMA index_info({index_name})")
            )
            indexes.add(columns)
    return indexes


def ensure_schema(connection: sqlite3.Connection) -> None:
    try:
        row = connection.execute(
            "SELECT value FROM cache_meta WHERE key = 'schema_version'"
        ).fetchone()
    except sqlite3.Error as exc:
        raise ContractError("not a code-search cache database") from exc
    if row is None or row["value"] != str(SCHEMA_VERSION):
        found = None if row is None else row["value"]
        raise ContractError(f"unsupported schema version: {found}")

    objects = {
        (item["type"], item["name"])
        for item in connection.execute(
            "SELECT type, name FROM sqlite_master WHERE type IN ('table', 'trigger')"
        )
    }
    missing_tables = sorted(
        table for table in REQUIRED_TABLE_COLUMNS if ("table", table) not in objects
    )
    if missing_tables:
        raise ContractError(f"missing required table: {', '.join(missing_tables)}")

    for table, expected_columns in REQUIRED_TABLE_COLUMNS.items():
        actual_columns = table_columns(connection, table)
        if actual_columns != expected_columns:
            raise ContractError(f"table {table} has incompatible columns")

    for table, expected_keys in REQUIRED_FOREIGN_KEYS.items():
        actual_keys = {
            (item["from"], item["table"], item["to"])
            for item in connection.execute(f"PRAGMA foreign_key_list({table})")
        }
        if not expected_keys.issubset(actual_keys):
            raise ContractError(f"table {table} is missing required foreign keys")

    for table, expected_indexes in REQUIRED_UNIQUE_INDEXES.items():
        actual_indexes = unique_indexes(connection, table)
        if not expected_indexes.issubset(actual_indexes):
            raise ContractError(f"table {table} is missing a required unique constraint")

    missing_triggers = sorted(
        trigger for trigger in REQUIRED_TRIGGERS if ("trigger", trigger) not in objects
    )
    if missing_triggers:
        raise ContractError(f"missing required trigger: {', '.join(missing_triggers)}")

    if connection.execute("PRAGMA foreign_key_check").fetchone() is not None:
        raise ContractError("cache database contains foreign-key violations")
    invalid_catalog = connection.execute(
        """
        SELECT 1 FROM catalog_entries c
        LEFT JOIN evaluations e
          ON e.artifact_id = c.artifact_id AND e.rubric_version = c.rubric_version
        WHERE e.verdict IS NULL OR e.verdict <> 'accepted'
        LIMIT 1
        """
    ).fetchone()
    if invalid_catalog is not None:
        raise ContractError("cache database contains a catalog entry without an accepted evaluation")


def load_input(path: str) -> Any:
    if path == "-":
        return json.load(sys.stdin)
    with Path(path).open("r", encoding="utf-8") as handle:
        return json.load(handle)


def output(value: Any) -> None:
    json.dump(value, sys.stdout, ensure_ascii=False, sort_keys=True, indent=2)
    sys.stdout.write("\n")


def record_run(connection: sqlite3.Connection, payload: Any) -> dict[str, Any]:
    if not isinstance(payload, dict):
        raise ContractError("record-run input must be an object")
    reject_unknown_keys(payload, {"query_contract", "run", "artifacts"}, "record-run input")
    fingerprint, contract = query_fingerprint(payload.get("query_contract"))
    now = utc_now()
    run = payload.get("run", {})
    if not isinstance(run, dict):
        raise ContractError("record-run.run must be an object")
    reject_unknown_keys(run, RUN_KEYS, "record-run.run")
    provider = nonempty_string(run.get("provider", contract["provider"]), "record-run.run.provider").lower()
    if provider != contract["provider"]:
        raise ContractError("record-run.run.provider must match query_contract.provider")
    searched_at = normalize_timestamp(run.get("searched_at"), "record-run.run.searched_at", now)
    status = run.get("status", "complete")
    if status not in {"complete", "partial", "failed"}:
        raise ContractError("record-run.run.status must be complete, partial, or failed")
    complete = run.get("complete", status == "complete")
    if not isinstance(complete, bool):
        raise ContractError("record-run.run.complete must be a boolean")
    if complete != (status == "complete"):
        raise ContractError("record-run.run.complete must be true exactly when status is complete")
    next_cursor = run.get("next_cursor")
    if next_cursor is not None:
        next_cursor = nonempty_string(next_cursor, "record-run.run.next_cursor")

    raw_artifacts = payload.get("artifacts", [])
    if not isinstance(raw_artifacts, list):
        raise ContractError("record-run.artifacts must be an array")
    normalized_artifacts = [normalize_artifact(item, searched_at) for item in raw_artifacts]
    result_count = run.get("result_count", len(normalized_artifacts))
    if not isinstance(result_count, int) or isinstance(result_count, bool) or result_count < 0:
        raise ContractError("record-run.run.result_count must be a non-negative integer")

    with connection:
        connection.execute(
            """
            INSERT INTO queries(query_fingerprint, contract_json, first_seen_at, last_seen_at)
            VALUES (?, ?, ?, ?)
            ON CONFLICT(query_fingerprint) DO UPDATE SET
                last_seen_at = MAX(queries.last_seen_at, excluded.last_seen_at)
            """,
            (fingerprint, canonical_json(contract), searched_at, searched_at),
        )
        connection.execute(
            """
            INSERT INTO search_runs(
                query_fingerprint, searched_at, provider, status, complete, next_cursor, result_count
            ) VALUES (?, ?, ?, ?, ?, ?, ?)
            ON CONFLICT(query_fingerprint, searched_at, provider) DO UPDATE SET
                status = excluded.status,
                complete = excluded.complete,
                next_cursor = excluded.next_cursor,
                result_count = excluded.result_count
            """,
            (fingerprint, searched_at, provider, status, int(complete), next_cursor, result_count),
        )
        unique_artifacts = 0
        evaluations_invalidated = 0
        catalog_entries_invalidated = 0
        for artifact_id, artifact in normalized_artifacts:
            existing = connection.execute(
                """
                SELECT blob_sha, immutable_locator, role, license
                FROM artifacts WHERE artifact_id = ?
                """,
                (artifact_id,),
            ).fetchone()
            if (
                existing is not None
                and existing["blob_sha"] is not None
                and artifact["blob_sha"] is not None
                and existing["blob_sha"] != artifact["blob_sha"]
            ):
                raise ContractError(f"artifact {artifact_id} has conflicting blob_sha values")
            if existing is None:
                unique_artifacts += 1
            else:
                evidence_changed = any(
                    artifact.get(field) is not None
                    and existing[field] != artifact.get(field)
                    for field in ("blob_sha", "immutable_locator", "role", "license")
                )
                if evidence_changed:
                    catalog_entries_invalidated += connection.execute(
                        "DELETE FROM catalog_entries WHERE artifact_id = ?", (artifact_id,)
                    ).rowcount
                    evaluations_invalidated += connection.execute(
                        "DELETE FROM evaluations WHERE artifact_id = ?", (artifact_id,)
                    ).rowcount
            connection.execute(
                """
                INSERT INTO artifacts(
                    artifact_id, canonical_repository, full_commit_sha, file_path, symbol,
                    line_start, line_end, blob_sha, immutable_locator, role, license,
                    verified_at, first_seen_at, last_seen_at
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                ON CONFLICT(artifact_id) DO UPDATE SET
                    line_start = COALESCE(excluded.line_start, artifacts.line_start),
                    line_end = COALESCE(excluded.line_end, artifacts.line_end),
                    blob_sha = COALESCE(artifacts.blob_sha, excluded.blob_sha),
                    immutable_locator = COALESCE(excluded.immutable_locator, artifacts.immutable_locator),
                    role = COALESCE(excluded.role, artifacts.role),
                    license = COALESCE(excluded.license, artifacts.license),
                    verified_at = MAX(artifacts.verified_at, excluded.verified_at),
                    last_seen_at = MAX(artifacts.last_seen_at, excluded.last_seen_at)
                """,
                (
                    artifact_id,
                    artifact["canonical_repository"],
                    artifact["full_commit_sha"],
                    artifact["file_path"],
                    artifact["symbol"],
                    artifact["line_start"],
                    artifact["line_end"],
                    artifact["blob_sha"],
                    artifact.get("immutable_locator"),
                    artifact.get("role"),
                    artifact.get("license"),
                    artifact["verified_at"],
                    searched_at,
                    searched_at,
                ),
            )
            connection.execute(
                """
                INSERT INTO query_artifacts(
                    query_fingerprint, artifact_id, first_seen_at, last_seen_at
                ) VALUES (?, ?, ?, ?)
                ON CONFLICT(query_fingerprint, artifact_id)
                DO UPDATE SET last_seen_at = MAX(query_artifacts.last_seen_at, excluded.last_seen_at)
                """,
                (fingerprint, artifact_id, searched_at, searched_at),
            )
    return {
        "query_fingerprint": fingerprint,
        "run_id": connection.execute(
            """
            SELECT run_id FROM search_runs
            WHERE query_fingerprint = ? AND searched_at = ? AND provider = ?
            """,
            (fingerprint, searched_at, provider),
        ).fetchone()["run_id"],
        "artifacts_recorded": len(normalized_artifacts),
        "unique_artifacts_added": unique_artifacts,
        "evaluations_invalidated": evaluations_invalidated,
        "catalog_entries_invalidated": catalog_entries_invalidated,
    }


def lookup(
    connection: sqlite3.Connection,
    contract_input: Any,
    rubric_version: str | None = None,
) -> dict[str, Any]:
    fingerprint, contract = query_fingerprint(contract_input)
    if rubric_version is not None:
        rubric_version = nonempty_string(rubric_version, "--rubric-version")
    query = connection.execute(
        "SELECT * FROM queries WHERE query_fingerprint = ?", (fingerprint,)
    ).fetchone()
    if query is None:
        return {"query_fingerprint": fingerprint, "cache_state": "miss", "artifacts": []}

    latest_run = connection.execute(
        """
        SELECT searched_at, provider, status, complete, next_cursor, result_count
        FROM search_runs WHERE query_fingerprint = ?
        ORDER BY searched_at DESC, run_id DESC LIMIT 1
        """,
        (fingerprint,),
    ).fetchone()
    rows = connection.execute(
        """
        SELECT a.*, qa.last_seen_at AS query_last_seen_at FROM artifacts a
        JOIN query_artifacts qa ON qa.artifact_id = a.artifact_id
        WHERE qa.query_fingerprint = ?
        ORDER BY a.canonical_repository, a.file_path, a.symbol, a.line_start
        """,
        (fingerprint,),
    ).fetchall()
    artifacts = []
    for row in rows:
        item = dict(row)
        query_last_seen_at = item.pop("query_last_seen_at")
        item["last_seen_for_query_at"] = query_last_seen_at
        item["mutable_revalidation_required"] = True
        evaluations = connection.execute(
            """
            SELECT rubric_version, verdict, scores_json, rationale, evaluated_at
            FROM evaluations WHERE artifact_id = ? ORDER BY rubric_version
            """,
            (row["artifact_id"],),
        ).fetchall()
        item["evaluations"] = [
            {
                **{key: value for key, value in dict(evaluation).items() if key != "scores_json"},
                "scores": json.loads(evaluation["scores_json"]),
            }
            for evaluation in evaluations
        ]
        selected_evaluation = next(
            (
                evaluation
                for evaluation in item["evaluations"]
                if evaluation["rubric_version"] == rubric_version
            ),
            None,
        )
        if rubric_version is None and len(item["evaluations"]) == 1:
            selected_evaluation = item["evaluations"][0]
        if selected_evaluation is not None and selected_evaluation["verdict"] in {
            "partial",
            "rejected",
        }:
            item["reuse_state"] = selected_evaluation["verdict"]
        elif (
            latest_run is not None
            and bool(latest_run["complete"])
            and query_last_seen_at < latest_run["searched_at"]
        ):
            item["reuse_state"] = "stale"
        else:
            item["reuse_state"] = "reused"
        artifacts.append(item)
    latest_run_output = None
    if latest_run is not None:
        latest_run_output = dict(latest_run)
        latest_run_output["complete"] = bool(latest_run_output["complete"])
    return {
        "query_fingerprint": fingerprint,
        "query_contract": contract,
        "rubric_version": rubric_version,
        "cache_state": "hit" if artifacts else "hit_empty",
        "latest_run": latest_run_output,
        "artifacts": artifacts,
    }


def normalize_scores(value: Any) -> dict[str, float]:
    if not isinstance(value, dict):
        raise ContractError("evaluation.scores must be an object")
    scores: dict[str, float] = {}
    for key, raw_score in value.items():
        name = nonempty_string(key, "evaluation score name")
        if isinstance(raw_score, bool) or not isinstance(raw_score, (int, float)):
            raise ContractError(f"evaluation score {name} must be numeric")
        score = float(raw_score)
        if not math.isfinite(score):
            raise ContractError(f"evaluation score {name} must be finite")
        scores[name] = score
    return scores


def evaluate(connection: sqlite3.Connection, payload: Any) -> dict[str, Any]:
    if not isinstance(payload, dict):
        raise ContractError("evaluate input must be an object")
    reject_unknown_keys(payload, EVALUATION_KEYS, "evaluate input")
    artifact_id = nonempty_string(payload.get("artifact_id"), "evaluation.artifact_id")
    rubric_version = nonempty_string(payload.get("rubric_version"), "evaluation.rubric_version")
    verdict = payload.get("verdict")
    if verdict not in {"accepted", "partial", "rejected"}:
        raise ContractError("evaluation.verdict must be accepted, partial, or rejected")
    scores = normalize_scores(payload.get("scores", {}))
    rationale = nonempty_string(payload.get("rationale"), "evaluation.rationale")
    evaluated_at = normalize_timestamp(payload.get("evaluated_at"), "evaluation.evaluated_at", utc_now())
    if connection.execute("SELECT 1 FROM artifacts WHERE artifact_id = ?", (artifact_id,)).fetchone() is None:
        raise ContractError(f"unknown artifact_id: {artifact_id}")
    with connection:
        catalog_removed = False
        if verdict != "accepted":
            catalog_removed = connection.execute(
                """
                DELETE FROM catalog_entries
                WHERE artifact_id = ? AND rubric_version = ?
                """,
                (artifact_id, rubric_version),
            ).rowcount > 0
        connection.execute(
            """
            INSERT INTO evaluations(
                artifact_id, rubric_version, verdict, scores_json, rationale, evaluated_at
            ) VALUES (?, ?, ?, ?, ?, ?)
            ON CONFLICT(artifact_id, rubric_version) DO UPDATE SET
                verdict = excluded.verdict,
                scores_json = excluded.scores_json,
                rationale = excluded.rationale,
                evaluated_at = excluded.evaluated_at
            """,
            (artifact_id, rubric_version, verdict, canonical_json(scores), rationale, evaluated_at),
        )
    return {
        "artifact_id": artifact_id,
        "rubric_version": rubric_version,
        "verdict": verdict,
        "catalog_removed": catalog_removed,
    }


def promote(connection: sqlite3.Connection, payload: Any) -> dict[str, Any]:
    if not isinstance(payload, dict):
        raise ContractError("promote input must be an object")
    reject_unknown_keys(payload, PROMOTION_KEYS, "promote input")
    artifact_id = nonempty_string(payload.get("artifact_id"), "promotion.artifact_id")
    rubric_version = nonempty_string(payload.get("rubric_version"), "promotion.rubric_version")
    note = nonempty_string(payload.get("note"), "promotion.note")
    promoted_at = normalize_timestamp(payload.get("promoted_at"), "promotion.promoted_at", utc_now())
    with connection:
        promoted = connection.execute(
            """
            INSERT INTO catalog_entries(artifact_id, rubric_version, note, promoted_at)
            SELECT artifact_id, rubric_version, ?, ?
            FROM evaluations
            WHERE artifact_id = ? AND rubric_version = ? AND verdict = 'accepted'
            ON CONFLICT(artifact_id, rubric_version) DO UPDATE SET
                note = excluded.note,
                promoted_at = excluded.promoted_at
            """,
            (note, promoted_at, artifact_id, rubric_version),
        )
        if promoted.rowcount == 0:
            raise ContractError("only an accepted evaluation can be promoted to the catalog")
    return {"artifact_id": artifact_id, "rubric_version": rubric_version, "cataloged": True}


def catalog(connection: sqlite3.Connection, rubric_version: str | None) -> dict[str, Any]:
    parameters: tuple[Any, ...] = ()
    where = ""
    if rubric_version is not None:
        rubric_version = nonempty_string(rubric_version, "--rubric-version")
        where = "WHERE c.rubric_version = ?"
        parameters = (rubric_version,)
    rows = connection.execute(
        f"""
        SELECT c.artifact_id, c.rubric_version, c.note, c.promoted_at,
               e.verdict, e.scores_json, e.rationale, e.evaluated_at,
               a.canonical_repository, a.full_commit_sha, a.file_path, a.symbol,
               a.line_start, a.line_end, a.blob_sha, a.immutable_locator, a.role,
               a.license, a.verified_at
        FROM catalog_entries c
        JOIN evaluations e
          ON e.artifact_id = c.artifact_id AND e.rubric_version = c.rubric_version
        JOIN artifacts a ON a.artifact_id = c.artifact_id
        {where}
        ORDER BY c.promoted_at DESC, c.artifact_id
        """,
        parameters,
    ).fetchall()
    entries = []
    for row in rows:
        item = dict(row)
        item["scores"] = json.loads(item.pop("scores_json"))
        entries.append(item)
    return {"rubric_version": rubric_version, "entries": entries}


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description=__doc__)
    subparsers = parser.add_subparsers(dest="command", required=True)

    init_parser = subparsers.add_parser("init", help="create or validate a cache database")
    init_parser.add_argument("--db", required=True)

    fingerprint_parser = subparsers.add_parser("fingerprint", help="hash a query contract")
    fingerprint_parser.add_argument("--input", required=True, help="JSON file or - for stdin")

    lookup_parser = subparsers.add_parser("lookup")
    lookup_parser.add_argument("--db", required=True)
    lookup_parser.add_argument("--input", required=True, help="JSON file or - for stdin")
    lookup_parser.add_argument("--rubric-version")

    for command in ("record-run", "evaluate", "promote"):
        command_parser = subparsers.add_parser(command)
        command_parser.add_argument("--db", required=True)
        command_parser.add_argument("--input", required=True, help="JSON file or - for stdin")

    catalog_parser = subparsers.add_parser("catalog", help="read promoted catalog entries")
    catalog_parser.add_argument("--db", required=True)
    catalog_parser.add_argument("--rubric-version")
    return parser


def main(argv: list[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)
    try:
        if args.command == "fingerprint":
            fingerprint, contract = query_fingerprint(load_input(args.input))
            output({"query_fingerprint": fingerprint, "query_contract": contract})
            return 0

        create = args.command == "init"
        path = database_path(args.db, must_exist=not create)
        with connect_database(path, create=create) as connection:
            if args.command == "init":
                output({"db": str(path), "schema_version": SCHEMA_VERSION})
            elif args.command == "lookup":
                output(lookup(connection, load_input(args.input), args.rubric_version))
            elif args.command == "record-run":
                output(record_run(connection, load_input(args.input)))
            elif args.command == "evaluate":
                output(evaluate(connection, load_input(args.input)))
            elif args.command == "promote":
                output(promote(connection, load_input(args.input)))
            elif args.command == "catalog":
                output(catalog(connection, args.rubric_version))
        return 0
    except (ContractError, json.JSONDecodeError, OSError, sqlite3.Error) as exc:
        parser.error(str(exc))
        return 2


if __name__ == "__main__":
    raise SystemExit(main())
