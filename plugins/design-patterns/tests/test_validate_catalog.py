import json
from pathlib import Path
import shutil
import subprocess
import sys
import tempfile
import unittest


REPOSITORY_ROOT = Path(__file__).resolve().parents[3]
VALIDATOR = REPOSITORY_ROOT / "plugins/design-patterns/scripts/validate_catalog.py"


def indexed_pattern(pattern_id="object-oriented-example", **overrides):
    pattern = {
        "id": pattern_id,
        "name": "Example Pattern",
        "aliases": [],
        "family": "object-oriented",
        "level": "code",
        "maturity": "indexed",
        "sources": [
            {
                "title": "Example source",
                "url": "https://example.com/pattern",
                "type": "primary",
            }
        ],
    }
    pattern.update(overrides)
    return pattern


def decision_ready_pattern(pattern_id="object-oriented-example", **overrides):
    pattern = indexed_pattern(
        pattern_id,
        maturity="decision-ready",
        problem="A recurring problem needs a stable variation point.",
        forces=["Callers vary", "The stable path must remain unchanged"],
        preconditions=["At least two concrete variants are known"],
        contraindications=["A direct function argument is sufficient"],
        solution="Separate the varying policy behind a narrow callable boundary.",
        guarantees=["The caller can replace the policy without changing orchestration"],
        costs=["Adds an indirection and another named concept"],
        failure_modes=["The policy boundary grows into an unrelated service interface"],
        language_realizations={"python": "A Protocol plus injected callable or object"},
        relations=[],
    )
    pattern.update(overrides)
    return pattern


def decision_ready_overlay_pattern(pattern_id="object-oriented-example", **overrides):
    pattern = decision_ready_pattern(pattern_id, **overrides)
    for field in ("name", "aliases", "family", "level", "sources"):
        pattern.pop(field)
    return pattern


def write_catalog(root, families):
    catalog = root / "catalog"
    catalog.mkdir(parents=True)
    index_families = []
    for family_id, patterns in families.items():
        filename = f"{family_id}.json"
        (catalog / filename).write_text(
            json.dumps(
                {
                    "schema_version": 1,
                    "family": {
                        "id": family_id,
                        "name": family_id.replace("-", " ").title(),
                        "scope": "Test scope",
                    },
                    "patterns": patterns,
                }
            ),
            encoding="utf-8",
        )
        index_families.append(
            {
                "id": family_id,
                "file": filename,
                "expected_count": len(patterns),
                "decision_ready_count": sum(
                    pattern.get("maturity") == "decision-ready" for pattern in patterns
                ),
            }
        )
    (catalog / "index.json").write_text(
        json.dumps(
            {
                "schema_version": 1,
                "maturity": [
                    "indexed",
                    "normalized",
                    "decision-ready",
                    "contextual",
                    "superseded",
                ],
                "expected_total_count": sum(len(patterns) for patterns in families.values()),
                "expected_decision_ready_count": sum(
                    pattern.get("maturity") == "decision-ready"
                    for patterns in families.values()
                    for pattern in patterns
                ),
                "families": index_families,
            }
        ),
        encoding="utf-8",
    )


def write_decision_overlay(root, patterns, defaults=None):
    (root / "catalog/decision-ready.json").write_text(
        json.dumps(
            {
                "schema_version": 1,
                "defaults": defaults or {},
                "patterns": patterns,
            }
        ),
        encoding="utf-8",
    )
    index_path = root / "catalog/index.json"
    index = json.loads(index_path.read_text(encoding="utf-8"))
    family_by_pattern = {}
    maturity_by_pattern = {}
    for family in index["families"]:
        document = json.loads(
            (root / "catalog" / family["file"]).read_text(encoding="utf-8")
        )
        family_defaults = document.get("defaults", {})
        for pattern in document["patterns"]:
            effective = {**family_defaults, **pattern}
            family_by_pattern[effective["id"]] = family["id"]
            maturity_by_pattern[effective["id"]] = effective["maturity"]
    for pattern in patterns:
        if pattern.get("id") in maturity_by_pattern:
            maturity_by_pattern[pattern["id"]] = {
                **(defaults or {}),
                **pattern,
            }.get("maturity", maturity_by_pattern[pattern["id"]])
    counts = {family["id"]: 0 for family in index["families"]}
    for pattern_id, maturity in maturity_by_pattern.items():
        if maturity == "decision-ready":
            counts[family_by_pattern[pattern_id]] += 1
    for family in index["families"]:
        family["decision_ready_count"] = counts[family["id"]]
    index["expected_decision_ready_count"] = sum(counts.values())
    index_path.write_text(json.dumps(index), encoding="utf-8")


class CatalogValidatorTest(unittest.TestCase):
    def run_validator(self, root, *, fixture_policy=True):
        if fixture_policy:
            fixture_runner = """
import importlib.util
import sys

spec = importlib.util.spec_from_file_location("catalog_validator", sys.argv[1])
validator = importlib.util.module_from_spec(spec)
spec.loader.exec_module(validator)
validator.DECISION_READY_PER_FAMILY = None
validator.EXPECTED_TOTAL = None
validator.EXPECTED_FAMILIES = None
validator.EXPECTED_FAMILY_COUNTS = None
validator.EXPECTED_FAMILY_SNAPSHOTS = None
validator.REQUIRE_SOURCE_MANIFEST = False
validator.EXPECTED_SOURCE_MANIFEST_SHA256 = None
raise SystemExit(validator.main(["--root", sys.argv[2]]))
"""
            command = [
                sys.executable,
                "-c",
                fixture_runner,
                str(VALIDATOR),
                str(root),
            ]
        else:
            command = [sys.executable, str(VALIDATOR), "--root", str(root)]
        return subprocess.run(
            command,
            text=True,
            capture_output=True,
            check=False,
        )

    def test_accepts_indexed_entries_and_decision_ready_overlay(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            write_catalog(
                root,
                {
                    "object-oriented": [
                        indexed_pattern("object-oriented-indexed-example"),
                        indexed_pattern("object-oriented-ready-example"),
                    ]
                },
            )
            write_decision_overlay(
                root,
                [decision_ready_overlay_pattern("object-oriented-ready-example")],
            )

            result = self.run_validator(root)

            self.assertEqual(result.returncode, 0, result.stderr)
            self.assertIn("2 patterns across 1 families", result.stdout)

    def test_accepts_family_defaults_for_compact_indexed_entries(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            write_catalog(root, {"object-oriented": []})
            family_path = root / "catalog/object-oriented.json"
            family = json.loads(family_path.read_text(encoding="utf-8"))
            family["defaults"] = {
                "aliases": [],
                "family": "object-oriented",
                "level": "code",
                "maturity": "indexed",
                "sources": indexed_pattern()["sources"],
            }
            family["patterns"] = [
                {"id": "object-oriented-compact-entry", "name": "Compact Entry"}
            ]
            family_path.write_text(json.dumps(family), encoding="utf-8")
            index_path = root / "catalog/index.json"
            index = json.loads(index_path.read_text(encoding="utf-8"))
            index["families"][0]["expected_count"] = 1
            index["expected_total_count"] = 1
            index_path.write_text(json.dumps(index), encoding="utf-8")

            result = self.run_validator(root)

            self.assertEqual(result.returncode, 0, result.stderr)

    def test_rejects_unsupported_family_document_field(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            write_catalog(root, {"object-oriented": [indexed_pattern()]})
            family_path = root / "catalog/object-oriented.json"
            family = json.loads(family_path.read_text(encoding="utf-8"))
            family["unexpected"] = True
            family_path.write_text(json.dumps(family), encoding="utf-8")

            result = self.run_validator(root)

            self.assertNotEqual(result.returncode, 0)
            self.assertIn(
                "family document object-oriented.json contains unsupported fields: unexpected",
                result.stderr,
            )

    def test_rejects_unsupported_family_metadata_field(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            write_catalog(root, {"object-oriented": [indexed_pattern()]})
            family_path = root / "catalog/object-oriented.json"
            family = json.loads(family_path.read_text(encoding="utf-8"))
            family["family"]["unexpected"] = True
            family_path.write_text(json.dumps(family), encoding="utf-8")

            result = self.run_validator(root)

            self.assertNotEqual(result.returncode, 0)
            self.assertIn(
                "family metadata object-oriented.json contains unsupported fields: unexpected",
                result.stderr,
            )

    def test_rejects_unsupported_family_defaults_field(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            write_catalog(root, {"object-oriented": [indexed_pattern()]})
            family_path = root / "catalog/object-oriented.json"
            family = json.loads(family_path.read_text(encoding="utf-8"))
            family["defaults"] = {"unexpected": True}
            family_path.write_text(json.dumps(family), encoding="utf-8")

            result = self.run_validator(root)

            self.assertNotEqual(result.returncode, 0)
            self.assertIn(
                "family object-oriented.defaults contains unsupported fields: unexpected",
                result.stderr,
            )

    def test_rejects_unsupported_raw_pattern_field(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            write_catalog(
                root,
                {
                    "object-oriented": [
                        indexed_pattern(unexpected=True),
                    ]
                },
            )

            result = self.run_validator(root)

            self.assertNotEqual(result.returncode, 0)
            self.assertIn(
                "object-oriented.json.patterns[0] contains unsupported fields: unexpected",
                result.stderr,
            )

    def test_rejects_duplicate_ids(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            write_catalog(
                root,
                {
                    "object-oriented": [
                        indexed_pattern("object-oriented-duplicate"),
                        indexed_pattern("object-oriented-duplicate"),
                    ]
                },
            )

            result = self.run_validator(root)

            self.assertNotEqual(result.returncode, 0)
            self.assertIn(
                "duplicate pattern id: object-oriented-duplicate", result.stderr
            )

    def test_rejects_pattern_id_without_family_prefix(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            write_catalog(root, {"object-oriented": [indexed_pattern("example")]})

            result = self.run_validator(root)

            self.assertNotEqual(result.returncode, 0)
            self.assertIn(
                "pattern id example must start with family prefix object-oriented-",
                result.stderr,
            )

    def test_rejects_dangling_relation_targets(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            write_catalog(root, {"object-oriented": [indexed_pattern()]})
            write_decision_overlay(
                root,
                [
                    decision_ready_overlay_pattern(
                        relations=[{"type": "alternative-to", "target": "missing"}]
                    )
                ],
            )

            result = self.run_validator(root)

            self.assertNotEqual(result.returncode, 0)
            self.assertIn("relation target does not exist: missing", result.stderr)

    def test_rejects_incomplete_decision_ready_entry(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            pattern = decision_ready_overlay_pattern()
            del pattern["contraindications"]
            write_catalog(root, {"object-oriented": [indexed_pattern()]})
            write_decision_overlay(root, [pattern])

            result = self.run_validator(root)

            self.assertNotEqual(result.returncode, 0)
            self.assertIn(
                "decision-ready overlay object-oriented-example must declare directly: contraindications",
                result.stderr,
            )

    def test_rejects_decision_ready_fields_inherited_from_family_defaults(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            write_catalog(root, {"object-oriented": [indexed_pattern()]})
            family_path = root / "catalog/object-oriented.json"
            family = json.loads(family_path.read_text(encoding="utf-8"))
            decision = decision_ready_pattern()
            family["defaults"] = {
                key: value
                for key, value in decision.items()
                if key not in {"id", "name"}
            }
            family["patterns"] = [
                {"id": "object-oriented-example", "name": "Example Pattern"}
            ]
            family_path.write_text(json.dumps(family), encoding="utf-8")

            result = self.run_validator(root)

            self.assertNotEqual(result.returncode, 0)
            self.assertIn(
                "family pattern object-oriented-example must be promoted through decision-ready.json",
                result.stderr,
            )

    def test_rejects_index_count_drift(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            write_catalog(root, {"object-oriented": [indexed_pattern()]})
            index_path = root / "catalog/index.json"
            index = json.loads(index_path.read_text(encoding="utf-8"))
            index["families"][0]["expected_count"] = 2
            index_path.write_text(json.dumps(index), encoding="utf-8")

            result = self.run_validator(root)

            self.assertNotEqual(result.returncode, 0)
            self.assertIn("expected 2 patterns but found 1", result.stderr)

    def test_rejects_total_count_drift(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            write_catalog(root, {"object-oriented": [indexed_pattern()]})
            index_path = root / "catalog/index.json"
            index = json.loads(index_path.read_text(encoding="utf-8"))
            index["expected_total_count"] = 2
            index_path.write_text(json.dumps(index), encoding="utf-8")

            result = self.run_validator(root)

            self.assertNotEqual(result.returncode, 0)
            self.assertIn("catalog expected 2 patterns but found 1", result.stderr)

    def test_accepts_declared_legacy_http_primary_source(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            source = {
                "title": "Legacy primary catalog",
                "url": "http://example.com/patterns",
                "type": "primary",
                "transport": "legacy-http",
            }
            write_catalog(
                root,
                {"object-oriented": [indexed_pattern(sources=[source])]},
            )

            result = self.run_validator(root)

            self.assertEqual(result.returncode, 0, result.stderr)

    def test_rejects_undeclared_http_source(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            source = {
                "title": "Unexpected insecure source",
                "url": "http://example.com/patterns",
                "type": "primary",
            }
            write_catalog(
                root,
                {"object-oriented": [indexed_pattern(sources=[source])]},
            )

            result = self.run_validator(root)

            self.assertNotEqual(result.returncode, 0)
            self.assertIn("HTTP sources must declare transport=legacy-http", result.stderr)

    def test_accepts_decision_ready_overlay_for_indexed_pattern(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            write_catalog(root, {"object-oriented": [indexed_pattern()]})
            decision = decision_ready_pattern()
            overlay = {
                key: value
                for key, value in decision.items()
                if key
                not in {"name", "aliases", "family", "level", "sources"}
            }
            overlay["id"] = "object-oriented-example"
            overlay["maturity"] = "decision-ready"
            write_decision_overlay(root, [overlay])

            result = self.run_validator(root)

            self.assertEqual(result.returncode, 0, result.stderr)

    def test_rejects_decision_ready_tradeoffs_inherited_from_defaults(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            write_catalog(root, {"object-oriented": [indexed_pattern()]})
            decision = decision_ready_pattern()
            overlay = {
                key: value
                for key, value in decision.items()
                if key
                not in {
                    "name",
                    "aliases",
                    "family",
                    "level",
                    "sources",
                    "preconditions",
                    "costs",
                    "failure_modes",
                }
            }
            write_decision_overlay(
                root,
                [overlay],
                defaults={
                    "preconditions": ["Generic precondition"],
                    "costs": ["Generic cost"],
                    "failure_modes": ["Generic failure mode"],
                },
            )

            result = self.run_validator(root)

            self.assertNotEqual(result.returncode, 0)
            self.assertIn(
                "decision-ready overlay defaults contains unsupported fields: costs, failure_modes, preconditions",
                result.stderr,
            )

    def test_rejects_base_identity_override_in_decision_ready_overlay(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            write_catalog(root, {"object-oriented": [indexed_pattern()]})
            decision = decision_ready_pattern()
            overlay = {
                key: value
                for key, value in decision.items()
                if key not in {"aliases", "family", "level", "sources"}
            }
            overlay["name"] = "Fabricated Identity"
            write_decision_overlay(root, [overlay])

            result = self.run_validator(root)

            self.assertNotEqual(result.returncode, 0)
            self.assertIn(
                "decision-ready overlay object-oriented-example contains unsupported fields: name",
                result.stderr,
            )

    def test_rejects_decision_metadata_inherited_from_overlay_defaults(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            write_catalog(root, {"object-oriented": [indexed_pattern()]})
            decision = decision_ready_pattern()
            overlay = {
                key: value
                for key, value in decision.items()
                if key
                not in {
                    "name",
                    "aliases",
                    "family",
                    "level",
                    "sources",
                    "problem",
                }
            }
            write_decision_overlay(
                root,
                [overlay],
                defaults={
                    "maturity": "decision-ready",
                    "problem": "One generic problem for every pattern.",
                },
            )

            result = self.run_validator(root)

            self.assertNotEqual(result.returncode, 0)
            self.assertIn(
                "decision-ready overlay defaults contains unsupported fields: problem",
                result.stderr,
            )

    def test_rejects_unrelated_cross_family_same_name_patterns(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            write_catalog(
                root,
                {
                    "microservices": [
                        indexed_pattern(
                            "microservices-circuit-breaker",
                            name="Circuit Breaker",
                            family="microservices",
                            level="architecture",
                        )
                    ],
                    "cloud-resilience": [
                        indexed_pattern(
                            "cloud-resilience-circuit-breaker",
                            name="Circuit Breaker",
                            family="cloud-resilience",
                            level="distributed-system",
                        )
                    ],
                },
            )

            result = self.run_validator(root)

            self.assertNotEqual(result.returncode, 0)
            self.assertIn(
                "same normalized name requires same-name-different-scope relation: "
                "cloud-resilience-circuit-breaker <-> microservices-circuit-breaker",
                result.stderr,
            )

    def test_rejects_same_name_relation_with_different_normalized_names(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            write_catalog(
                root,
                {
                    "microservices": [
                        indexed_pattern(
                            "microservices-circuit-breaker",
                            name="Circuit Breaker",
                            family="microservices",
                            level="architecture",
                            relations=[
                                {
                                    "type": "same-name-different-scope",
                                    "target": "cloud-resilience-retry",
                                }
                            ],
                        )
                    ],
                    "cloud-resilience": [
                        indexed_pattern(
                            "cloud-resilience-retry",
                            name="Retry",
                            family="cloud-resilience",
                            level="distributed-system",
                        )
                    ],
                },
            )

            result = self.run_validator(root)

            self.assertNotEqual(result.returncode, 0)
            self.assertIn(
                "same-name-different-scope relation requires matching normalized names: "
                "microservices-circuit-breaker -> cloud-resilience-retry",
                result.stderr,
            )

    def test_rejects_same_name_relation_within_one_family(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            write_catalog(
                root,
                {
                    "object-oriented": [
                        indexed_pattern(
                            "object-oriented-example-one",
                            relations=[
                                {
                                    "type": "same-name-different-scope",
                                    "target": "object-oriented-example-two",
                                }
                            ],
                        ),
                        indexed_pattern("object-oriented-example-two"),
                    ]
                },
            )

            result = self.run_validator(root)

            self.assertNotEqual(result.returncode, 0)
            self.assertIn(
                "same-name-different-scope relation must cross families: "
                "object-oriented-example-one -> object-oriented-example-two",
                result.stderr,
            )

    def test_overlay_relations_replace_base_relations_for_final_graph(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            write_catalog(
                root,
                {
                    "microservices": [
                        indexed_pattern(
                            "microservices-circuit-breaker",
                            name="Circuit Breaker",
                            family="microservices",
                            level="architecture",
                            relations=[
                                {
                                    "type": "same-name-different-scope",
                                    "target": "cloud-resilience-circuit-breaker",
                                }
                            ],
                        )
                    ],
                    "cloud-resilience": [
                        indexed_pattern(
                            "cloud-resilience-circuit-breaker",
                            name="Circuit Breaker",
                            family="cloud-resilience",
                            level="distributed-system",
                        )
                    ],
                },
            )
            write_decision_overlay(
                root,
                [
                    decision_ready_overlay_pattern(
                        "microservices-circuit-breaker",
                        relations=[],
                    )
                ],
            )

            result = self.run_validator(root)

            self.assertNotEqual(result.returncode, 0)
            self.assertIn(
                "same normalized name requires same-name-different-scope relation: "
                "cloud-resilience-circuit-breaker <-> microservices-circuit-breaker",
                result.stderr,
            )

    def test_rejects_decision_ready_count_redistributed_between_families(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory) / "design-patterns"
            shutil.copytree(REPOSITORY_ROOT / "plugins/design-patterns", root)
            overlay_path = root / "catalog/decision-ready.json"
            overlay = json.loads(overlay_path.read_text(encoding="utf-8"))
            architecture_entry = next(
                pattern
                for pattern in overlay["patterns"]
                if pattern["id"] == "architecture-microkernel"
            )
            architecture_entry["id"] = "object-oriented-abstract-factory"
            overlay_path.write_text(json.dumps(overlay), encoding="utf-8")
            index_path = root / "catalog/index.json"
            index = json.loads(index_path.read_text(encoding="utf-8"))
            for family in index["families"]:
                if family["id"] == "object-oriented":
                    family["decision_ready_count"] = 4
                elif family["id"] == "architecture":
                    family["decision_ready_count"] = 2
            index_path.write_text(json.dumps(index), encoding="utf-8")

            result = self.run_validator(root, fixture_policy=False)

            self.assertNotEqual(result.returncode, 0)
            self.assertIn(
                "family object-oriented decision_ready_count must be 3 but found 4",
                result.stderr,
            )

    def test_real_catalog_uses_standard_three_per_family_policy(self):
        result = self.run_validator(
            REPOSITORY_ROOT / "plugins/design-patterns",
            fixture_policy=False,
        )

        self.assertEqual(result.returncode, 0, result.stderr)

    def test_rejects_approved_family_set_drift(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory) / "design-patterns"
            shutil.copytree(REPOSITORY_ROOT / "plugins/design-patterns", root)
            index_path = root / "catalog/index.json"
            index = json.loads(index_path.read_text(encoding="utf-8"))
            index["families"] = [
                family for family in index["families"] if family["id"] != "security"
            ]
            index_path.write_text(json.dumps(index), encoding="utf-8")

            result = self.run_validator(root, fixture_policy=False)

            self.assertNotEqual(result.returncode, 0)
            self.assertIn(
                "catalog family set must contain the 12 approved families (missing: security)",
                result.stderr,
            )

    def test_rejects_missing_expected_total_count(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            write_catalog(root, {"object-oriented": [indexed_pattern()]})
            index_path = root / "catalog/index.json"
            index = json.loads(index_path.read_text(encoding="utf-8"))
            del index["expected_total_count"]
            index_path.write_text(json.dumps(index), encoding="utf-8")

            result = self.run_validator(root)

            self.assertNotEqual(result.returncode, 0)
            self.assertIn(
                "catalog expected_total_count must be a non-negative integer",
                result.stderr,
            )

    def test_rejects_expected_total_policy_drift(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory) / "design-patterns"
            shutil.copytree(REPOSITORY_ROOT / "plugins/design-patterns", root)
            index_path = root / "catalog/index.json"
            index = json.loads(index_path.read_text(encoding="utf-8"))
            index["expected_total_count"] = 552
            index_path.write_text(json.dumps(index), encoding="utf-8")

            result = self.run_validator(root, fixture_policy=False)

            self.assertNotEqual(result.returncode, 0)
            self.assertIn(
                "catalog expected_total_count must be 553 but found 552",
                result.stderr,
            )

    def test_rejects_pattern_redistributed_between_source_families(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory) / "design-patterns"
            shutil.copytree(REPOSITORY_ROOT / "plugins/design-patterns", root)
            architecture_path = root / "catalog/architecture.json"
            architecture = json.loads(architecture_path.read_text(encoding="utf-8"))
            moved = next(
                pattern
                for pattern in architecture["patterns"]
                if pattern["id"] == "architecture-blackboard"
            )
            architecture["patterns"] = [
                pattern
                for pattern in architecture["patterns"]
                if pattern["id"] != "architecture-blackboard"
            ]
            architecture_path.write_text(json.dumps(architecture), encoding="utf-8")
            object_oriented_path = root / "catalog/object-oriented.json"
            object_oriented = json.loads(
                object_oriented_path.read_text(encoding="utf-8")
            )
            object_oriented["patterns"].append(
                {**moved, "id": "object-oriented-fabricated-blackboard"}
            )
            object_oriented_path.write_text(
                json.dumps(object_oriented), encoding="utf-8"
            )
            index_path = root / "catalog/index.json"
            index = json.loads(index_path.read_text(encoding="utf-8"))
            for family in index["families"]:
                if family["id"] == "object-oriented":
                    family["expected_count"] = 24
                elif family["id"] == "architecture":
                    family["expected_count"] = 7
            index_path.write_text(json.dumps(index), encoding="utf-8")

            result = self.run_validator(root, fixture_policy=False)

            self.assertNotEqual(result.returncode, 0)
            self.assertIn(
                "family object-oriented expected_count must be 23 but found 24",
                result.stderr,
            )

    def test_rejects_count_preserving_family_snapshot_drift(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory) / "design-patterns"
            shutil.copytree(REPOSITORY_ROOT / "plugins/design-patterns", root)
            family_path = root / "catalog/object-oriented.json"
            family = json.loads(family_path.read_text(encoding="utf-8"))
            family["patterns"][0]["name"] = "Fabricated Factory"
            family_path.write_text(json.dumps(family), encoding="utf-8")

            result = self.run_validator(root, fixture_policy=False)

            self.assertNotEqual(result.returncode, 0)
            self.assertIn(
                "family object-oriented snapshot digest does not match the approved catalog",
                result.stderr,
            )

    def test_rejects_source_manifest_mapping_drift(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory) / "design-patterns"
            shutil.copytree(REPOSITORY_ROOT / "plugins/design-patterns", root)
            manifest_path = root / "catalog/source-manifest.json"
            catalog = root / "catalog"
            index = json.loads((catalog / "index.json").read_text(encoding="utf-8"))
            manifest = {
                "schema_version": 1,
                "observed_at": index["observed_at"],
                "scope": "Test source manifest",
                "families": [],
            }
            for family in index["families"]:
                document = json.loads(
                    (catalog / family["file"]).read_text(encoding="utf-8")
                )
                defaults = document.get("defaults", {})
                effective = [{**defaults, **pattern} for pattern in document["patterns"]]
                manifest["families"].append(
                    {
                        "id": family["id"],
                        "source": effective[0]["sources"][0],
                        "source_locator": "Primary catalog index",
                        "verification_method": "manual-primary-source-index-audit",
                        "observed_count": len(effective),
                        "limitations": "Names and source locators only.",
                        "entries": [
                            {
                                "id": pattern["id"],
                                "source_name": pattern["name"],
                                "name": pattern["name"],
                                "source_path": pattern.get("source_path"),
                                "normalization_note": None,
                            }
                            for pattern in effective
                        ],
                    }
                )
            manifest["families"][0]["entries"][0]["name"] = "Fabricated Source Name"
            manifest_path.write_text(json.dumps(manifest), encoding="utf-8")

            result = self.run_validator(root, fixture_policy=False)

            self.assertNotEqual(result.returncode, 0)
            self.assertIn(
                "source manifest mapping does not match family object-oriented",
                result.stderr,
            )

    def test_real_catalog_spells_service_component_test_correctly(self):
        family = json.loads(
            (
                REPOSITORY_ROOT
                / "plugins/design-patterns/catalog/microservices.json"
            ).read_text(encoding="utf-8")
        )
        pattern = next(
            pattern
            for pattern in family["patterns"]
            if pattern["source_path"] == "testing/service-component-test.html"
        )

        self.assertEqual(pattern["id"], "microservices-service-component-test")
        self.assertEqual(pattern["name"], "Service component test")

    def test_majority_quorum_claims_intersection_not_consensus(self):
        overlay = json.loads(
            (
                REPOSITORY_ROOT
                / "plugins/design-patterns/catalog/decision-ready.json"
            ).read_text(encoding="utf-8")
        )
        pattern = next(
            pattern
            for pattern in overlay["patterns"]
            if pattern["id"] == "distributed-systems-majority-quorum"
        )
        asserted_scope = " ".join(
            [
                pattern["problem"],
                *pattern["guarantees"],
                *pattern["language_realizations"].values(),
            ]
        ).casefold()

        self.assertNotIn("conflicting decisions", asserted_scope)
        self.assertNotIn("consensus", asserted_scope)
        self.assertIn("intersect", asserted_scope)
        self.assertTrue(
            any(
                "consensus safety" in failure_mode.casefold()
                for failure_mode in pattern["failure_modes"]
            )
        )

    def test_retry_allows_non_idempotent_operations_with_deduplication(self):
        overlay = json.loads(
            (
                REPOSITORY_ROOT
                / "plugins/design-patterns/catalog/decision-ready.json"
            ).read_text(encoding="utf-8")
        )
        pattern = next(
            pattern
            for pattern in overlay["patterns"]
            if pattern["id"] == "cloud-resilience-retry"
        )
        contraindications = " ".join(pattern["contraindications"]).casefold()

        self.assertIn("without deduplication", contraindications)
        self.assertIn("permanent", contraindications)

    def test_layers_guarantee_does_not_claim_dependency_inversion(self):
        overlay = json.loads(
            (
                REPOSITORY_ROOT
                / "plugins/design-patterns/catalog/decision-ready.json"
            ).read_text(encoding="utf-8")
        )
        pattern = next(
            pattern
            for pattern in overlay["patterns"]
            if pattern["id"] == "architecture-layers"
        )
        guarantees = " ".join(pattern["guarantees"]).casefold()

        self.assertIn("declared direction", guarantees)
        self.assertNotIn("implementation details", guarantees)

    def test_review_skill_is_explicit_only_in_codex_metadata(self):
        openai_agent = (
            REPOSITORY_ROOT
            / "plugins/design-patterns/skills/review-pattern-usage/agents/openai.yaml"
        ).read_text(encoding="utf-8")

        self.assertIn("allow_implicit_invocation: false", openai_agent)

    def test_rejects_decision_ready_overlay_for_unknown_pattern(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            write_catalog(root, {"object-oriented": [indexed_pattern()]})
            write_decision_overlay(
                root,
                [{"id": "not-indexed", "maturity": "decision-ready"}],
            )

            result = self.run_validator(root)

            self.assertNotEqual(result.returncode, 0)
            self.assertIn("decision-ready overlay id is not indexed: not-indexed", result.stderr)

    def test_rejects_missing_declared_decision_ready_pattern(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            write_catalog(root, {"object-oriented": [indexed_pattern()]})
            index_path = root / "catalog/index.json"
            index = json.loads(index_path.read_text(encoding="utf-8"))
            index["expected_decision_ready_count"] = 1
            index["families"][0]["decision_ready_count"] = 1
            index_path.write_text(json.dumps(index), encoding="utf-8")

            result = self.run_validator(root)

            self.assertNotEqual(result.returncode, 0)
            self.assertIn(
                "family object-oriented expected 1 decision-ready patterns but found 0",
                result.stderr,
            )


if __name__ == "__main__":
    unittest.main()
