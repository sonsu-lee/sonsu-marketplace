from __future__ import annotations

import copy
import importlib.util
import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path
from unittest import mock


ROOT = Path(__file__).resolve().parents[2]
SCRIPT = ROOT / "scripts" / "update_madia_design_catalog.py"
SPEC = importlib.util.spec_from_file_location("update_madia_design_catalog", SCRIPT)
assert SPEC is not None and SPEC.loader is not None
MODULE = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(MODULE)


class MadiaCatalogUpdateTests(unittest.TestCase):
    @staticmethod
    def existing_catalog(videos: list[dict]) -> dict:
        catalog = json.loads(
            (ROOT / "docs" / "research" / "madia-design-practice-catalog.json").read_text(
                encoding="utf-8"
            )
        )
        catalog["videos"] = videos
        catalog["principles"] = []
        catalog["reliability"] = {
            "pilot_sample_size": None,
            "pilot_kappa": None,
            "pilot_evidence": [],
            "production_double_coded_ratio": None,
            "production_kappa": None,
            "production_evidence": [],
        }
        catalog["quality_gates"] = [
            {"id": f"M{index}", "status": "not_run", "evidence": []}
            for index in range(9)
        ]
        catalog["inventory"].update(
            {
                "discovered_unique_videos": len(videos),
                "analyzed": sum(video["status"] == "analyzed" for video in videos),
                "excluded": sum(video["status"] == "excluded" for video in videos),
                "blocked": sum(video["status"] == "blocked" for video in videos),
                "pending": sum(video["status"] == "pending" for video in videos),
                "corpus_coverage": (
                    sum(video["status"] != "pending" for video in videos) / len(videos)
                    if videos
                    else 0.0
                ),
            }
        )
        return catalog

    @staticmethod
    def build_with_uploads(existing: dict | None, uploads: list[dict]):
        def fetch_playlist(playlist_id: str):
            if playlist_id == MODULE.UPLOADS_PLAYLIST_ID:
                return uploads, True
            return [], True

        with (
            mock.patch.object(MODULE, "fetch_playlist", side_effect=fetch_playlist),
            mock.patch.object(MODULE, "fetch_recent_feed", return_value={}),
            mock.patch.object(MODULE, "load_existing", return_value=existing),
            mock.patch.object(
                MODULE, "fetch_video_channel_id", return_value=MODULE.CHANNEL_ID
            ),
        ):
            return MODULE.build_catalog("2026-09-17")

    def test_refresh_preserves_existing_queue_and_appends_new_videos(self) -> None:
        old_first = MODULE.pending_video("oldvideo001", "Old first")
        old_second = MODULE.pending_video("oldvideo002", "Old second")
        existing = self.existing_catalog([old_first, old_second])
        uploads = [
            {"video_id": "newvideo001", "title": "New"},
            {"video_id": "oldvideo002", "title": "Old second updated"},
            {"video_id": "oldvideo001", "title": "Old first updated"},
        ]

        def fetch_playlist(playlist_id: str):
            if playlist_id == MODULE.UPLOADS_PLAYLIST_ID:
                return uploads, True
            return [], True

        with (
            mock.patch.object(MODULE, "fetch_playlist", side_effect=fetch_playlist),
            mock.patch.object(MODULE, "fetch_recent_feed", return_value={}),
            mock.patch.object(MODULE, "load_existing", return_value=existing),
            mock.patch.object(
                MODULE, "fetch_video_channel_id", return_value=MODULE.CHANNEL_ID
            ),
        ):
            catalog = MODULE.build_catalog("2026-09-17")

        self.assertEqual(
            [video["video_id"] for video in catalog["videos"]],
            ["oldvideo001", "oldvideo002", "newvideo001"],
        )
        self.assertEqual(catalog["videos"][1]["title"], "Old second updated")

    def test_empty_upload_discovery_cannot_erase_existing_catalog(self) -> None:
        existing = self.existing_catalog(
            [MODULE.pending_video("oldvideo001", "Old")]
        )
        with self.assertRaisesRegex(ValueError, "zero videos"):
            self.build_with_uploads(existing, [])

    def test_fresh_empty_discovery_is_rejected(self) -> None:
        with self.assertRaisesRegex(ValueError, "zero videos"):
            self.build_with_uploads(None, [])

    def test_related_playlist_videos_are_included_in_inventory_union(self) -> None:
        uploads = [{"video_id": "uploadvid01", "title": "Upload"}]
        related = [{"video_id": "relatedvd01", "title": "Related"}]

        def fetch_playlist(playlist_id: str):
            if playlist_id == MODULE.UPLOADS_PLAYLIST_ID:
                return uploads, True
            if playlist_id == MODULE.PLAYLISTS["uxui"]:
                return related, True
            return [], True

        with (
            mock.patch.object(MODULE, "fetch_playlist", side_effect=fetch_playlist),
            mock.patch.object(MODULE, "fetch_recent_feed", return_value={}),
            mock.patch.object(MODULE, "load_existing", return_value=None),
            mock.patch.object(
                MODULE,
                "fetch_video_channel_id",
                return_value=MODULE.CHANNEL_ID,
                create=True,
            ),
        ):
            catalog = MODULE.build_catalog("2026-09-17")

        self.assertEqual(
            [video["video_id"] for video in catalog["videos"]],
            ["uploadvid01", "relatedvd01"],
        )
        self.assertEqual(catalog["videos"][1]["playlist_ids"], ["uxui"])

    def test_initial_parser_failure_is_not_reported_as_complete(self) -> None:
        page = (
            '<html><script>var ytInitialData = {};</script>'
            '<script>"INNERTUBE_API_KEY":"key";</script>'
            '<script>"INNERTUBE_CONTEXT_CLIENT_VERSION":"1.0";</script></html>'
        )
        with mock.patch.object(MODULE, "fetch_text", return_value=page):
            with self.assertRaisesRegex(ValueError, "no videos"):
                MODULE.fetch_playlist("playlist")

    def test_partial_upload_discovery_cannot_drop_existing_video(self) -> None:
        existing = self.existing_catalog(
            [
                MODULE.pending_video("oldvideo001", "Old first"),
                MODULE.pending_video("oldvideo002", "Old second"),
            ]
        )
        uploads = [{"video_id": "oldvideo001", "title": "Old first"}]
        with self.assertRaisesRegex(ValueError, "omitted existing catalog videos"):
            self.build_with_uploads(existing, uploads)

    def test_invalid_candidate_is_never_published(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            catalog_path = Path(tmp) / "catalog.json"
            summary_path = Path(tmp) / "catalog.md"
            catalog_path.write_text("existing catalog\n", encoding="utf-8")
            summary_path.write_text("existing summary\n", encoding="utf-8")
            with (
                mock.patch.object(MODULE, "CATALOG", catalog_path),
                mock.patch.object(MODULE, "SUMMARY", summary_path),
            ):
                with self.assertRaises(ValueError):
                    MODULE.publish_catalog({"invalid": True})
            self.assertEqual(catalog_path.read_text(encoding="utf-8"), "existing catalog\n")
            self.assertEqual(summary_path.read_text(encoding="utf-8"), "existing summary\n")

    def test_malformed_existing_catalog_is_rejected_cleanly(self) -> None:
        with self.assertRaisesRegex(ValueError, "existing catalog"):
            MODULE.validate_existing_catalog([])
        with self.assertRaisesRegex(ValueError, "status"):
            MODULE.validate_existing_catalog(
                {"videos": [{"video_id": "oldvideo001", "status": "unknown"}]}
            )
        with self.assertRaisesRegex(ValueError, "existing catalog"):
            MODULE.validate_existing_catalog(
                {"videos": [MODULE.pending_video("oldvideo001", "Old")]}
            )

    def test_ambiguous_or_malformed_continuation_is_rejected(self) -> None:
        lockup = {
            "lockupViewModel": {
                "contentId": "video000001",
                "metadata": {
                    "lockupMetadataViewModel": {"title": {"content": "First"}}
                },
            }
        }

        def continuation(token=None):
            command = {} if token is None else {"token": token}
            return {
                "continuationItemViewModel": {
                    "continuationCommand": {
                        "innertubeCommand": {"continuationCommand": command}
                    }
                }
            }

        with self.assertRaisesRegex(ValueError, "ambiguous continuation"):
            MODULE.extract_video_page(
                {"items": [lockup, continuation("token-a"), continuation("token-b")]}
            )
        with self.assertRaisesRegex(ValueError, "malformed continuation"):
            MODULE.extract_video_page({"items": [lockup, continuation()]})

    def test_deep_playlist_payload_is_rejected_without_recursion_error(self) -> None:
        payload: object = {
            "items": [
                {
                    "lockupViewModel": {
                        "contentId": "video000001",
                        "metadata": {
                            "lockupMetadataViewModel": {"title": {"content": "First"}}
                        },
                    }
                }
            ]
        }
        for _ in range(1200):
            payload = {"nested": payload}
        with self.assertRaisesRegex(ValueError, "traversal limit"):
            MODULE.extract_video_page(payload)

    def test_equal_sized_candidate_lists_are_rejected_as_ambiguous(self) -> None:
        def lockup(video_id: str) -> dict:
            return {
                "lockupViewModel": {
                    "contentId": video_id,
                    "metadata": {
                        "lockupMetadataViewModel": {"title": {"content": video_id}}
                    },
                }
            }

        payload = {
            "left": {"items": [lockup("video000001")]},
            "right": {"items": [lockup("video000002")]},
        }
        with self.assertRaisesRegex(ValueError, "ambiguous item lists"):
            MODULE.extract_video_page(payload)

    def test_malformed_direct_lockup_cannot_be_silently_skipped(self) -> None:
        valid = {
            "lockupViewModel": {
                "contentId": "video000001",
                "metadata": {
                    "lockupMetadataViewModel": {"title": {"content": "First"}}
                },
            }
        }
        malformed = {
            "lockupViewModel": {
                "contentId": "bad",
                "metadata": {"lockupMetadataViewModel": {"title": {}}},
            }
        }
        with self.assertRaisesRegex(ValueError, "malformed video lockup"):
            MODULE.extract_video_page({"items": [valid, malformed]})

    def test_continuation_is_bound_to_the_selected_item_subtree(self) -> None:
        def lockup(video_id: str) -> dict:
            return {
                "lockupViewModel": {
                    "contentId": video_id,
                    "metadata": {
                        "lockupMetadataViewModel": {"title": {"content": video_id}}
                    },
                }
            }

        unrelated_continuation = {
            "continuationItemViewModel": {
                "continuationCommand": {
                    "innertubeCommand": {
                        "continuationCommand": {"token": "unrelated-token"}
                    }
                }
            }
        }
        videos, continuation = MODULE.extract_video_page(
            {
                "selected": {"items": [lockup("video000001"), lockup("video000002")]},
                "unrelated": {"items": [lockup("video000003"), unrelated_continuation]},
            }
        )
        self.assertEqual([item["video_id"] for item in videos], ["video000001", "video000002"])
        self.assertIsNone(continuation)

    def test_root_candidate_ignores_unrelated_sibling_continuation(self) -> None:
        def lockup(video_id: str) -> dict:
            return {
                "lockupViewModel": {
                    "contentId": video_id,
                    "metadata": {
                        "lockupMetadataViewModel": {"title": {"content": video_id}}
                    },
                }
            }

        unrelated_continuation = {
            "continuationItemViewModel": {
                "continuationCommand": {
                    "innertubeCommand": {
                        "continuationCommand": {"token": "unrelated-token"}
                    }
                }
            }
        }
        videos, continuation = MODULE.extract_video_page(
            {
                "items": [lockup("video000001"), lockup("video000002")],
                "unrelated": unrelated_continuation,
            }
        )
        self.assertEqual([item["video_id"] for item in videos], ["video000001", "video000002"])
        self.assertIsNone(continuation)

    def test_fresh_continuation_chain_is_bounded(self) -> None:
        def lockup(video_id: str) -> dict:
            return {
                "lockupViewModel": {
                    "contentId": video_id,
                    "metadata": {
                        "lockupMetadataViewModel": {"title": {"content": video_id}}
                    },
                }
            }

        def continuation(token: str) -> dict:
            return {
                "continuationItemViewModel": {
                    "continuationCommand": {
                        "innertubeCommand": {
                            "continuationCommand": {"token": token}
                        }
                    }
                }
            }

        initial = {"items": [lockup("video000001"), continuation("token-0")]}
        page = (
            f"<html><script>var ytInitialData = {json.dumps(initial)};</script>"
            '<script>"INNERTUBE_API_KEY":"key";</script>'
            '<script>"INNERTUBE_CONTEXT_CLIENT_VERSION":"1.0";</script></html>'
        )
        calls = 0

        def next_page(*_args, **_kwargs):
            nonlocal calls
            calls += 1
            if calls > 3:
                raise AssertionError("continuation bound was not enforced")
            return {
                "items": [
                    lockup(f"video{calls + 1:06d}"),
                    continuation(f"token-{calls}"),
                ]
            }

        with (
            mock.patch.object(MODULE, "fetch_text", return_value=page),
            mock.patch.object(MODULE, "post_json", side_effect=next_page),
            mock.patch.object(MODULE, "MAX_PLAYLIST_CONTINUATION_PAGES", 2, create=True),
        ):
            with self.assertRaisesRegex(ValueError, "continuation page limit"):
                MODULE.fetch_playlist("playlist")
        self.assertEqual(calls, 2)

    def test_playlist_video_accumulation_is_bounded(self) -> None:
        def lockup(video_id: str) -> dict:
            return {
                "lockupViewModel": {
                    "contentId": video_id,
                    "metadata": {
                        "lockupMetadataViewModel": {"title": {"content": video_id}}
                    },
                }
            }

        initial = {
            "items": [
                lockup("video000001"),
                {
                    "continuationItemViewModel": {
                        "continuationCommand": {
                            "innertubeCommand": {
                                "continuationCommand": {"token": "next-token"}
                            }
                        }
                    }
                },
            ]
        }
        page = (
            f"<html><script>var ytInitialData = {json.dumps(initial)};</script>"
            '<script>"INNERTUBE_API_KEY":"key";</script>'
            '<script>"INNERTUBE_CONTEXT_CLIENT_VERSION":"1.0";</script></html>'
        )
        with (
            mock.patch.object(MODULE, "fetch_text", return_value=page),
            mock.patch.object(
                MODULE,
                "post_json",
                return_value={"items": [lockup("video000002"), lockup("video000003")]},
            ),
            mock.patch.object(MODULE, "MAX_PLAYLIST_VIDEOS", 2, create=True),
        ):
            with self.assertRaisesRegex(ValueError, "video limit"):
                MODULE.fetch_playlist("playlist")

    def test_channel_feed_only_video_is_included_in_inventory_union(self) -> None:
        uploads = [{"video_id": "uploadvid01", "title": "Upload"}]

        def fetch_playlist(playlist_id: str):
            if playlist_id == MODULE.UPLOADS_PLAYLIST_ID:
                return uploads, True
            return [], True

        recent = {
            "feedvideo01": {
                "title": "Feed only",
                "published_at": "2026-09-17T00:00:00Z",
                "content_type": "short",
            }
        }
        with (
            mock.patch.object(MODULE, "fetch_playlist", side_effect=fetch_playlist),
            mock.patch.object(MODULE, "fetch_recent_feed", return_value=recent),
            mock.patch.object(MODULE, "load_existing", return_value=None),
            mock.patch.object(
                MODULE, "fetch_video_channel_id", return_value=MODULE.CHANNEL_ID
            ),
        ):
            catalog = MODULE.build_catalog("2026-09-17")

        self.assertEqual(
            [video["video_id"] for video in catalog["videos"]],
            ["uploadvid01", "feedvideo01"],
        )
        self.assertEqual(catalog["videos"][1]["playlist_ids"], [])

    def test_channel_feed_rejects_entries_owned_by_another_channel(self) -> None:
        feed = f"""<?xml version="1.0" encoding="UTF-8"?>
        <feed xmlns="http://www.w3.org/2005/Atom"
              xmlns:yt="http://www.youtube.com/xml/schemas/2015">
          <entry>
            <yt:videoId>feedvideo01</yt:videoId>
            <yt:channelId>UC0000000000000000000000</yt:channelId>
            <title>Foreign video</title>
            <published>2026-09-17T00:00:00+00:00</published>
            <link rel="alternate" href="https://www.youtube.com/watch?v=feedvideo01" />
          </entry>
        </feed>"""
        with mock.patch.object(MODULE, "fetch_text", return_value=feed):
            with self.assertRaisesRegex(ValueError, "canonical channel"):
                MODULE.fetch_recent_feed()

    def test_related_playlist_video_requires_canonical_channel_owner(self) -> None:
        uploads = [{"video_id": "uploadvid01", "title": "Upload"}]
        related = [{"video_id": "relatedvd01", "title": "Related"}]

        def fetch_playlist(playlist_id: str):
            if playlist_id == MODULE.UPLOADS_PLAYLIST_ID:
                return uploads, True
            if playlist_id == MODULE.PLAYLISTS["uxui"]:
                return related, True
            return [], True

        with (
            mock.patch.object(MODULE, "fetch_playlist", side_effect=fetch_playlist),
            mock.patch.object(MODULE, "fetch_recent_feed", return_value={}),
            mock.patch.object(MODULE, "load_existing", return_value=None),
            mock.patch.object(
                MODULE,
                "fetch_video_channel_id",
                return_value="UC0000000000000000000000",
                create=True,
            ),
        ):
            with self.assertRaisesRegex(ValueError, "canonical channel"):
                MODULE.build_catalog("2026-09-17")

    def test_upload_video_requires_canonical_channel_owner(self) -> None:
        uploads = [{"video_id": "uploadvid01", "title": "Upload"}]

        def fetch_playlist(playlist_id: str):
            if playlist_id == MODULE.UPLOADS_PLAYLIST_ID:
                return uploads, True
            return [], True

        with (
            mock.patch.object(MODULE, "fetch_playlist", side_effect=fetch_playlist),
            mock.patch.object(MODULE, "fetch_recent_feed", return_value={}),
            mock.patch.object(MODULE, "load_existing", return_value=None),
            mock.patch.object(
                MODULE,
                "fetch_video_channel_id",
                return_value="UC0000000000000000000000",
            ) as owner,
        ):
            with self.assertRaisesRegex(ValueError, "canonical channel"):
                MODULE.build_catalog("2026-09-17")
        owner.assert_called_once_with("uploadvid01")

    def test_playlist_video_in_channel_feed_still_requires_watch_page_owner(self) -> None:
        uploads = [{"video_id": "uploadvid01", "title": "Upload"}]

        def fetch_playlist(playlist_id: str):
            if playlist_id == MODULE.UPLOADS_PLAYLIST_ID:
                return uploads, True
            return [], True

        recent = {
            "uploadvid01": {
                "title": "Upload",
                "published_at": "2026-09-17T00:00:00Z",
                "content_type": "long-form",
            }
        }
        with (
            mock.patch.object(MODULE, "fetch_playlist", side_effect=fetch_playlist),
            mock.patch.object(MODULE, "fetch_recent_feed", return_value=recent),
            mock.patch.object(MODULE, "load_existing", return_value=None),
            mock.patch.object(
                MODULE,
                "fetch_video_channel_id",
                return_value="UC0000000000000000000000",
            ) as owner,
        ):
            with self.assertRaisesRegex(ValueError, "canonical channel"):
                MODULE.build_catalog("2026-09-17")
        owner.assert_called_once_with("uploadvid01")

    def test_new_discovery_invalidates_promotions_and_dependent_gates(self) -> None:
        old = MODULE.pending_video("oldvideo001", "Old")
        existing = self.existing_catalog([old])
        existing["principles"] = [
            {
                "id": "promoted-principle",
                "tier": "P3",
                "validation_status": "passed",
                "behavior_fixture": {
                    "fixture_id": "promoted-principle-v1",
                    "run_id": "promoted-principle-run-1",
                    "artifact_revision": "artifact-v1",
                    "status": "passed",
                    "expected": ["Expected behavior"],
                    "must_not": ["Prohibited behavior"],
                    "observed": ["Expected behavior"],
                    "evidence": ["evidence/promoted-principle.json"],
                },
            }
        ]
        existing["reliability"].update(
            {
                "production_double_coded_ratio": 0.2,
                "production_kappa": 0.8,
                "production_evidence": ["evidence/production.json"],
            }
        )
        existing["quality_gates"] = [
            {"id": f"M{index}", "status": "passed", "evidence": [f"evidence/m{index}.md"]}
            for index in range(9)
        ]
        uploads = [
            {"video_id": "oldvideo001", "title": "Old"},
            {"video_id": "newvideo001", "title": "New"},
        ]

        def fetch_playlist(playlist_id: str):
            if playlist_id == MODULE.UPLOADS_PLAYLIST_ID:
                return uploads, True
            return [], True

        with (
            mock.patch.object(MODULE, "fetch_playlist", side_effect=fetch_playlist),
            mock.patch.object(MODULE, "fetch_recent_feed", return_value={}),
            mock.patch.object(MODULE, "load_existing", return_value=existing),
            mock.patch.object(MODULE, "validate_existing_catalog", return_value=None),
            mock.patch.object(
                MODULE, "fetch_video_channel_id", return_value=MODULE.CHANNEL_ID
            ),
        ):
            catalog = MODULE.build_catalog("2026-09-17")

        self.assertTrue(all(gate["status"] == "not_run" for gate in catalog["quality_gates"]))
        self.assertTrue(all(gate["evidence"] == [] for gate in catalog["quality_gates"]))
        self.assertEqual(catalog["principles"][0]["tier"], "P0")
        self.assertEqual(catalog["principles"][0]["validation_status"], "not_run")
        self.assertEqual(
            catalog["principles"][0]["behavior_fixture"]["status"], "not_run"
        )
        self.assertIsNone(catalog["reliability"]["production_double_coded_ratio"])
        self.assertIsNone(catalog["reliability"]["production_kappa"])
        self.assertEqual(catalog["reliability"]["production_evidence"], [])

    def test_sibling_continuation_is_followed(self) -> None:
        def lockup(video_id: str, title: str) -> dict:
            return {
                "lockupViewModel": {
                    "contentId": video_id,
                    "metadata": {
                        "lockupMetadataViewModel": {"title": {"content": title}}
                    },
                }
            }

        initial = {
            "page": {
                "items": [lockup("video000001", "First")],
                "pagination": {
                    "continuationItemViewModel": {
                        "continuationCommand": {
                            "innertubeCommand": {
                                "continuationCommand": {"token": "next-token"}
                            }
                        }
                    }
                },
            }
        }
        page = (
            f"<html><script>var ytInitialData = {json.dumps(initial)};</script>"
            '<script>"INNERTUBE_API_KEY":"key";</script>'
            '<script>"INNERTUBE_CONTEXT_CLIENT_VERSION":"1.0";</script></html>'
        )
        continuation = {"items": [lockup("video000002", "Second")]}
        with (
            mock.patch.object(MODULE, "fetch_text", return_value=page),
            mock.patch.object(MODULE, "post_json", return_value=continuation) as post,
        ):
            videos, complete = MODULE.fetch_playlist("playlist")
        self.assertTrue(complete)
        self.assertEqual([item["video_id"] for item in videos], ["video000001", "video000002"])
        post.assert_called_once()

    def test_catalog_and_summary_roll_back_together_on_second_replace_failure(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            catalog_path = Path(tmp) / "catalog.json"
            summary_path = Path(tmp) / "catalog.md"
            catalog_path.write_text("existing catalog\n", encoding="utf-8")
            summary_path.write_text("existing summary\n", encoding="utf-8")
            real_replace = MODULE.os.replace
            failed = False

            def fail_summary_once(source, target):
                nonlocal failed
                if Path(target) == summary_path and not failed:
                    failed = True
                    raise OSError("summary replace failed")
                return real_replace(source, target)

            with (
                mock.patch.object(MODULE, "CATALOG", catalog_path),
                mock.patch.object(MODULE, "SUMMARY", summary_path),
                mock.patch.object(MODULE.os, "replace", side_effect=fail_summary_once),
                mock.patch.object(MODULE, "render_summary", return_value="new summary\n"),
            ):
                with self.assertRaisesRegex(OSError, "summary replace failed"):
                    MODULE.publish_catalog(
                        self.existing_catalog([MODULE.pending_video("oldvideo001", "Old")])
                    )
            self.assertEqual(catalog_path.read_text(encoding="utf-8"), "existing catalog\n")
            self.assertEqual(summary_path.read_text(encoding="utf-8"), "existing summary\n")


    def test_normalize_cli_preserves_queue_and_is_idempotent(self) -> None:
        catalog = self.existing_catalog([MODULE.pending_video("oldvideo001", "Old")])
        catalog["schema_version"] = "madia-design-practice-catalog-v1"
        del catalog["videos"][0]["analysis_receipt"]
        catalog["inventory"]["pending"] = 0
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "catalog.json"
            path.write_text(json.dumps(catalog), encoding="utf-8")
            command = [sys.executable, str(SCRIPT), "--normalize", "--catalog", str(path)]
            subprocess.run(command, check=True, capture_output=True, text=True)
            first = path.read_bytes(), path.with_suffix(".md").read_bytes()
            normalized = json.loads(first[0])
            self.assertEqual(normalized["schema_version"], "madia-design-practice-catalog-v2")
            self.assertEqual(normalized["videos"][0]["video_id"], "oldvideo001")
            self.assertIsNone(normalized["videos"][0]["analysis_receipt"])
            self.assertEqual(normalized["inventory"]["pending"], 1)
            subprocess.run(command, check=True, capture_output=True, text=True)
            self.assertEqual(first, (path.read_bytes(), path.with_suffix(".md").read_bytes()))


class MadiaAnalysisUpdateTests(unittest.TestCase):
    """Exercise cache inputs and catalog publication through the public CLI."""

    def setUp(self) -> None:
        spec = importlib.util.spec_from_file_location(
            "madia_validator_fixtures", Path(__file__).with_name("test_validate_madia_catalog.py")
        )
        assert spec is not None and spec.loader is not None
        self.fixtures = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(self.fixtures)
        temporary = tempfile.TemporaryDirectory()
        self.addCleanup(temporary.cleanup)
        self.base = Path(temporary.name)
        self.catalog_path = self.base / "catalog.json"
        self.ledger_path = self.base / "ledger.json"
        self.evidence = self.base / "madia-evidence"
        self.evidence.mkdir()
        self.ids = [f"video{index:06d}" for index in range(3)]
        self.save(self.catalog_path, MadiaCatalogUpdateTests.existing_catalog([
            MODULE.pending_video(video_id, f"Video {index}")
            for index, video_id in enumerate(self.ids)
        ]))
        self.save(self.ledger_path, {
            "schema_version": "design-terminology-v1",
            "terms": [{"id": "term.spacing", "status": "candidate"},
                      {"id": "term.alignment", "status": "held"},
                      {"id": "term.retired", "status": "rejected"}],
        })
        self.catalog_path.with_suffix(".md").write_text("Before publication\n", encoding="utf-8")

    @staticmethod
    def save(path: Path, payload: dict | list) -> None:
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(json.dumps(payload, ensure_ascii=False), encoding="utf-8")

    @staticmethod
    def load(path: Path):
        return json.loads(path.read_text(encoding="utf-8"))

    def snapshot(self) -> dict:
        paths = [self.catalog_path, self.catalog_path.with_suffix(".md")]
        paths.extend(self.evidence.rglob("*"))
        return {str(path.relative_to(self.base)): path.read_bytes()
                for path in paths if path.is_file()}

    def cli(self, *arguments, succeeds: bool = True, fail_summary: bool = False):
        args = [str(SCRIPT), *map(str, arguments), "--catalog", str(self.catalog_path),
                "--ledger", str(self.ledger_path)]
        if fail_summary:
            # Fault injection only: run the genuine CLI and genuine publisher.
            program = (
                "import os,runpy,sys\n"
                "target=sys.argv.pop(1); original=os.replace; failed=False\n"
                "def replace(source,destination):\n"
                " global failed\n"
                " if os.path.realpath(destination)==os.path.realpath(target) and not failed:\n"
                "  failed=True\n"
                "  raise OSError('injected publication failure')\n"
                " return original(source,destination)\n"
                "os.replace=replace\n"
                "sys.argv=sys.argv[1:]\n"
                "runpy.run_path(sys.argv[0],run_name='__main__')\n"
            )
            command = [sys.executable, "-c", program, str(self.catalog_path.with_suffix(".md")), *args]
        else:
            command = [sys.executable, *args]
        result = subprocess.run(command, capture_output=True, text=True, check=False)
        if succeeds:
            self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
        else:
            self.assertNotEqual(result.returncode, 0, result.stdout + result.stderr)
        if fail_summary:
            self.assertIn("injected publication failure", result.stdout + result.stderr)
        return result

    def selection(self, ids: list[str], *, pilot: bool = False) -> None:
        name = "pilot-selection" if pilot else "production-sample"
        payload = {"schema_version": f"madia-{name}-v1", "rule": "Fixed test selection", "video_ids": ids}
        if pilot:
            payload.update(selected_at="2026-10-03", replacements=[])
        self.save(self.evidence / f"{name}.json", payload)

    def cache(self, index: int = 0, *, double: bool = False, excluded: bool = False) -> Path:
        video_id = self.ids[index]
        directory = self.base / "cache" / video_id
        bundle = self.fixtures.analysis_bundle()
        bundle.update(video_id=video_id, session_id=f"{video_id}-coder-a")
        unit = bundle["evidence_units"][0]
        unit.update(id=f"{video_id}:001", project_id=f"{video_id}:p1",
                    source_locator=f"https://www.youtube.com/watch?v={video_id}&t=10s")
        if excluded:
            bundle.update(proposed_status="excluded", reason="not_relevant: 디자인 판단 없음",
                          evidence_units=[], frames_requested=[],
                          ratings={"relevance": "not_relevant", "decision_stage": "none", "evidence_kind": "none"})
        self.save(directory / "fetch.json", {"video_id": video_id, "status": "ok",
                  "duration": 40, "caption_source": "manual", "caption_file": "captions.vtt"})
        self.save(directory / "cues.json", [{"start": 8, "end": 27, "text": "비교할 때 순서가 같아야 편해요."}])
        self.save(directory / "analysis-coder-a.json", bundle)
        if double:
            for role in ("coder-b", "adjudicator"):
                other = copy.deepcopy(bundle)
                other.update(coder=role, session_id=f"{video_id}-{role}")
                self.save(directory / f"analysis-{role}.json", other)
        verification = self.fixtures.verification_bundle(bundle)
        verification["verifier"] = f"{video_id}-verifier"
        if excluded:
            verification["exclusion_confirmed"] = True
        self.save(directory / "verification.json", verification)
        return directory

    def curate(self, **changes):
        path = self.base / "curation.json"
        self.save(path, {"schema_version": "madia-curation-v1", **changes})
        return path

    def principle(self, occurrences: list[str]) -> dict:
        principle = copy.deepcopy(self.fixtures.valid_catalog()["principles"][0])
        principle.pop("independent_projects")
        principle.update(tier="P0", occurrence_ids=occurrences, external_sources=[],
                         validation_status="not_run", behavior_fixture=None)
        return principle

    def test_single_coding_merges_without_pilot_selection(self) -> None:
        directory = self.cache()
        self.cli("--merge-analysis", directory)
        catalog = self.load(self.catalog_path)
        video = catalog["videos"][0]
        self.assertEqual(video["status"], "analyzed")
        self.assertEqual(catalog["inventory"]["pending"], 2)
        self.assertEqual(catalog["inventory"]["analyzed"], 1)
        self.assertEqual(video["analysis_receipt"]["coders"], ["coder-a"])
        self.assertEqual(video["analysis_receipt"]["sessions"],
                         {"coder-a": f"{self.ids[0]}-coder-a", "verifier": f"{self.ids[0]}-verifier"})
        self.assertEqual(video["evidence_units"][0]["verification"]["status"], "confirmed")
        self.assertEqual(video["evidence_units"][0]["principle_candidate_ids"], [])

    def test_invalid_batch_never_publishes_partial_success(self) -> None:
        good, bad = self.cache(), self.cache(1, double=True)
        (bad / "analysis-adjudicator.json").unlink()
        before = self.snapshot()
        self.cli("--merge-analysis", good, bad, succeeds=False)
        self.assertEqual(self.snapshot(), before)

    def test_pilot_selection_and_mode_requirements(self) -> None:
        directory = self.cache(double=True)
        for selected, pilot in ((None, True), ([], True), ([self.ids[0]], False)):
            with self.subTest(selected=selected, pilot=pilot):
                if selected is not None:
                    self.selection(selected, pilot=True)
                before = self.snapshot()
                self.cli("--merge-analysis", directory, *(["--pilot"] if pilot else []), succeeds=False)
                self.assertEqual(self.snapshot(), before)
        self.selection([self.ids[0]], pilot=True)
        (directory / "analysis-coder-b.json").unlink()
        before = self.snapshot()
        self.cli("--merge-analysis", directory, "--pilot", succeeds=False)
        self.assertEqual(self.snapshot(), before)

    def test_role_caption_and_excerpt_failures_leave_catalog_unchanged(self) -> None:
        for failure in ("session", "caption", "excerpt", "missing-fetch", "missing-sample"):
            with self.subTest(failure=failure):
                directory = self.cache(double=failure == "missing-sample")
                if failure == "session":
                    verification = self.load(directory / "verification.json")
                    verification["verifier"] = f"{self.ids[0]}-coder-a"
                    self.save(directory / "verification.json", verification)
                elif failure == "caption":
                    fetch = self.load(directory / "fetch.json")
                    fetch["caption_source"] = "auto"
                    self.save(directory / "fetch.json", fetch)
                elif failure == "excerpt":
                    self.save(directory / "cues.json", [{"start": 8, "end": 27, "text": "무관한 발화"}])
                elif failure == "missing-fetch":
                    (directory / "fetch.json").unlink()
                before = self.snapshot()
                self.cli("--merge-analysis", directory, succeeds=False)
                self.assertEqual(self.snapshot(), before)

    def test_exclusion_requires_verifier_agreement(self) -> None:
        directory = self.cache(excluded=True)
        verification = self.load(directory / "verification.json")
        verification.update(exclusion_confirmed=False, exclusion_note="화면에 디자인 판단이 있다.")
        self.save(directory / "verification.json", verification)
        before = self.snapshot()
        self.cli("--merge-analysis", directory, succeeds=False)
        self.assertEqual(self.snapshot(), before)
        verification.update(exclusion_confirmed=True, exclusion_note=None)
        self.save(directory / "verification.json", verification)
        self.cli("--merge-analysis", directory)
        video = self.load(self.catalog_path)["videos"][0]
        self.assertEqual(video["status"], "excluded")
        self.assertEqual(video["evidence_units"], [])
        self.assertIsNotNone(video["analysis_receipt"])

    def test_blocked_fetch_bypasses_pilot_and_coding_requirements(self) -> None:
        directory = self.base / "cache" / self.ids[0]
        self.save(directory / "fetch.json", {"video_id": self.ids[0], "status": "blocked", "reason": "비공개 영상"})
        self.cli("--merge-analysis", directory, "--pilot")
        video = self.load(self.catalog_path)["videos"][0]
        self.assertEqual(video["status"], "blocked")
        self.assertEqual(video["blocking_reason"], "비공개 영상")
        self.assertEqual(video["evidence_units"], [])
        for field in ("analysis_receipt", "exclusion_reason", "duplicate_of"):
            self.assertIsNone(video[field])

    def test_corrections_are_applied_before_excerpt_matching_and_units_are_sorted(self) -> None:
        directory = self.cache()
        bundle = self.load(directory / "analysis-coder-a.json")
        first = bundle["evidence_units"][0]
        first["speech_excerpt"] = "잘못 옮긴 발화"
        earlier = copy.deepcopy(first)
        earlier.update(id=f"{self.ids[0]}:002", timestamp_start=1, timestamp_end=5,
                       source_locator=f"https://www.youtube.com/watch?v={self.ids[0]}&t=1s",
                       speech_excerpt="앞선 발화")
        earlier["visual_evidence"][0]["frame_time"] = 2
        bundle["evidence_units"].append(earlier)
        self.save(directory / "analysis-coder-a.json", bundle)
        verification = self.fixtures.verification_bundle(bundle)
        verification["units"][0].update(status="corrected", note="발췌와 시작 시각 교정",
                                       corrections={"timestamp_start": 9, "speech_excerpt": "비교할 때 순서가 같아야 편해요."})
        self.save(directory / "verification.json", verification)
        self.save(directory / "cues.json", [
            {"start": 1, "end": 5, "text": "앞선 발화"},
            {"start": 8, "end": 15, "text": "비교할 때 순서가"},
            {"start": 15, "end": 27, "text": "같아야 편해요."},
        ])
        self.cli("--merge-analysis", directory)
        units = self.load(self.catalog_path)["videos"][0]["evidence_units"]
        self.assertEqual([u["id"] for u in units], [earlier["id"], first["id"]])
        self.assertEqual(units[1]["source_locator"], f"https://www.youtube.com/watch?v={self.ids[0]}&t=9s")
        self.assertEqual(units[1]["verification"]["status"], "corrected")
        self.assertEqual(units[1]["speech_excerpt"], "비교할 때 순서가 같아야 편해요.")

    def test_rejected_units_are_removed_and_production_records_are_pruned(self) -> None:
        self.selection([self.ids[0]])
        directory = self.cache(double=True)
        self.cli("--merge-analysis", directory)
        evidence_path = self.evidence / "production-coder-evidence.json"
        self.assertEqual([r["unit_id"] for r in self.load(evidence_path)["records"]], [self.ids[0]])
        verification = self.load(directory / "verification.json")
        verification["units"][0].update(status="rejected", note="원자료가 판단을 반박한다.")
        self.save(directory / "verification.json", verification)
        self.cli("--merge-analysis", directory)
        catalog = self.load(self.catalog_path)
        self.assertEqual(catalog["videos"][0]["status"], "excluded")
        self.assertEqual(catalog["videos"][0]["evidence_units"], [])
        self.assertIsNotNone(catalog["videos"][0]["analysis_receipt"])
        self.assertEqual(catalog["reliability"]["production_evidence"], [])
        self.assertIsNone(catalog["reliability"]["production_double_coded_ratio"])
        if evidence_path.exists():
            self.assertEqual(self.load(evidence_path)["records"], [])

    def test_out_of_sample_adjudication_does_not_enter_production_reliability(self) -> None:
        self.selection([self.ids[1]])
        self.cli("--merge-analysis", self.cache(double=True))
        reliability = self.load(self.catalog_path)["reliability"]
        self.assertEqual(reliability["production_evidence"], [])
        self.assertIsNone(reliability["production_double_coded_ratio"])
        path = self.evidence / "production-coder-evidence.json"
        if path.exists():
            self.assertEqual(self.load(path)["records"], [])

    def test_pilot_records_preserve_preconsensus_ratings_and_replace_on_remerge(self) -> None:
        self.selection([self.ids[0]], pilot=True)
        directory = self.cache(double=True)
        b_path = directory / "analysis-coder-b.json"
        b = self.load(b_path)
        b["ratings"]["relevance"] = "design_explanation"
        self.save(b_path, b)
        self.cli("--merge-analysis", directory, "--pilot")
        path = self.evidence / "pilot-coder-evidence.json"
        payload = self.load(path)
        self.assertEqual(payload["population_size"], 3)
        self.assertEqual(payload["records"], [{
            "unit_id": self.ids[0],
            "ratings": {
                "relevance": {"coder-a": "direct_design_work", "coder-b": "design_explanation"},
                "decision_stage": {"coder-a": "information_priority", "coder-b": "information_priority"},
                "evidence_kind": {"coder-a": "verbalized", "coder-b": "verbalized"},
            },
        }])
        self.assertIsNone(self.load(self.catalog_path)["reliability"]["pilot_kappa"])
        b["ratings"]["relevance"] = "tool_or_workflow"
        self.save(b_path, b)
        self.cli("--merge-analysis", directory, "--pilot")
        self.assertEqual(self.load(path)["records"][0]["ratings"]["relevance"]["coder-b"], "tool_or_workflow")
        self.assertEqual(len(self.load(path)["records"]), 1)

    def test_publication_failure_restores_existing_and_new_evidence(self) -> None:
        self.selection([self.ids[0]])
        directory = self.cache(double=True)
        before = self.snapshot()
        self.cli("--merge-analysis", directory, succeeds=False, fail_summary=True)
        self.assertEqual(self.snapshot(), before)
        self.cli("--merge-analysis", directory)
        b_path = directory / "analysis-coder-b.json"
        bundle = self.load(b_path)
        bundle["ratings"]["relevance"] = "design_explanation"
        self.save(b_path, bundle)
        before = self.snapshot()
        self.cli("--merge-analysis", directory, succeeds=False, fail_summary=True)
        self.assertEqual(self.snapshot(), before)

    def test_curation_derives_projects_and_rebuilds_reverse_references(self) -> None:
        self.cli("--merge-analysis", self.cache(), self.cache(1))
        occurrences = [f"{video_id}:001" for video_id in self.ids[:2]]
        principle = self.principle(occurrences)
        self.cli("--apply-curation", self.curate(principles=[principle]))
        self.assertEqual(self.load(self.catalog_path)["principles"][0]["independent_projects"], 2)
        self.cli("--apply-curation", self.curate(
            project_links={f"{video_id}:p1": "madia-proj-shared" for video_id in self.ids[:2]},
            principles=[principle],
        ))
        catalog = self.load(self.catalog_path)
        self.assertEqual(catalog["principles"][0]["independent_projects"], 1)
        for video in catalog["videos"][:2]:
            self.assertEqual(video["evidence_units"][0]["principle_candidate_ids"], [principle["id"]])
            self.assertEqual(video["evidence_units"][0]["project_id"], "madia-proj-shared")
        self.cli("--apply-curation", self.curate(principles=[]))
        self.assertEqual(self.load(self.catalog_path)["principles"], [])
        for video in self.load(self.catalog_path)["videos"][:2]:
            self.assertEqual(video["evidence_units"][0]["principle_candidate_ids"], [])

    def test_term_assignment_replaces_and_rewrites_units_and_principles(self) -> None:
        self.cli("--merge-analysis", self.cache())
        unit_id = f"{self.ids[0]}:001"
        principle = self.principle([unit_id])
        principle["term_ids"] = ["term.spacing"]
        self.cli("--apply-curation", self.curate(
            principles=[principle], term_assignments={unit_id: ["term.spacing", "term.spacing"]}))
        self.cli("--apply-curation", self.curate(term_assignments={unit_id: ["term.alignment"]}))
        self.assertEqual(self.load(self.catalog_path)["videos"][0]["evidence_units"][0]["term_ids"], ["term.alignment"])
        self.cli("--apply-curation", self.curate(term_rewrites={"term.spacing": "term.alignment"}))
        self.assertEqual(self.load(self.catalog_path)["principles"][0]["term_ids"], ["term.alignment"])
        self.cli("--apply-curation", self.curate(term_rewrites={"term.alignment": None}))
        catalog = self.load(self.catalog_path)
        self.assertEqual(catalog["principles"][0]["term_ids"], [])
        self.assertEqual(catalog["videos"][0]["evidence_units"][0]["term_ids"], [])

    def test_invalid_assignments_and_unverified_principles_are_atomic(self) -> None:
        self.cli("--merge-analysis", self.cache())
        unit_id = f"{self.ids[0]}:001"
        for assignments in ({unit_id: ["term.retired"]}, {unit_id: ["term.unknown"]},
                            {"missing:001": ["term.spacing"]}):
            with self.subTest(assignments=assignments):
                before = self.snapshot()
                self.cli("--apply-curation", self.curate(term_assignments=assignments), succeeds=False)
                self.assertEqual(self.snapshot(), before)
        directory = self.cache()
        verification = self.load(directory / "verification.json")
        verification["units"][0].update(status="held", note="화면이 불명확하다.")
        self.save(directory / "verification.json", verification)
        self.cli("--merge-analysis", directory)
        before = self.snapshot()
        self.cli("--apply-curation", self.curate(principles=[self.principle([unit_id])]), succeeds=False)
        self.assertEqual(self.snapshot(), before)

    def test_duplicate_and_remerge_restrictions_preserve_referenced_evidence(self) -> None:
        self.cli("--merge-analysis", self.cache())
        self.selection([self.ids[1]], pilot=True)
        for video_id, target in ((self.ids[0], self.ids[0]), (self.ids[0], "absent00000"),
                                 (self.ids[1], self.ids[0])):
            with self.subTest(video_id=video_id, target=target):
                before = self.snapshot()
                self.cli("--apply-curation", self.curate(mark_duplicates={
                    video_id: {"duplicate_of": target, "reason": "duplicate: 같은 영상"}}), succeeds=False)
                self.assertEqual(self.snapshot(), before)
        self.cli("--apply-curation", self.curate(principles=[self.principle([f"{self.ids[0]}:001"])]))
        before = self.snapshot()
        self.cli("--merge-analysis", self.cache(), succeeds=False)
        self.assertEqual(self.snapshot(), before)
        self.cli("--apply-curation", self.curate(mark_duplicates={
            self.ids[0]: {"duplicate_of": self.ids[2], "reason": "duplicate: 같은 영상"}}), succeeds=False)
        self.assertEqual(self.snapshot(), before)

    def test_mark_duplicate_removes_receipt_and_production_sample_record(self) -> None:
        self.selection([self.ids[0]])
        self.cli("--merge-analysis", self.cache(double=True), self.cache(1))
        self.cli("--apply-curation", self.curate(mark_duplicates={
            self.ids[0]: {"duplicate_of": self.ids[1], "reason": "duplicate: 재업로드"}}))
        catalog = self.load(self.catalog_path)
        video = catalog["videos"][0]
        self.assertEqual(video["status"], "excluded")
        self.assertEqual(video["duplicate_of"], self.ids[1])
        self.assertEqual(video["evidence_units"], [])
        self.assertIsNone(video["analysis_receipt"])
        self.assertEqual(catalog["reliability"]["production_evidence"], [])

    def test_p3_text_change_rejects_receipt_before_publication(self) -> None:
        self.cli("--merge-analysis", self.cache(), self.cache(1), self.cache(2))
        principle = copy.deepcopy(self.fixtures.valid_catalog()["principles"][0])
        principle.pop("independent_projects")
        receipt_path = self.base / principle["behavior_fixture"]["evidence"][0]
        self.save(receipt_path, {
            "schema_version": "madia-behavior-receipt-v1",
            "principle_sha256": "0" * 64,
            "fixture_id": principle["behavior_fixture"]["fixture_id"],
            "run_id": principle["behavior_fixture"]["run_id"],
            "artifact_revision": principle["behavior_fixture"]["artifact_revision"],
            "scenario": "Compare repeated products", "output": "Inspect must-know fields.",
            "behavior_options": principle["behavior_fixture"]["expected"] + principle["behavior_fixture"]["must_not"],
            "observed": principle["behavior_fixture"]["observed"], "evaluator_notes": "Observed inspection",
        })
        before = self.snapshot()
        result = self.cli("--apply-curation", self.curate(principles=[principle]), succeeds=False)
        # Distinguish the stale receipt guard from unrelated P3 gate failures.
        self.assertIn("principle text changed after behavior run", result.stdout + result.stderr)
        self.assertEqual(self.snapshot(), before)

    def test_reliability_recomputes_denominators_filters_records_and_keeps_inputs(self) -> None:
        catalog = self.load(self.catalog_path)
        for video in catalog["videos"][:2]:
            video["status"] = "analyzed"
        def record(video_id, a, b):
            return {"unit_id": video_id, "ratings": {
                "relevance": {"coder-a": a, "coder-b": b},
                "decision_stage": {"coder-a": "information_priority" if a == "direct_design_work" else "visual_system",
                                   "coder-b": "information_priority" if b == "direct_design_work" else "visual_system"},
                "evidence_kind": {"coder-a": "verbalized" if a == "direct_design_work" else "inferred",
                                  "coder-b": "verbalized" if b == "direct_design_work" else "inferred"},
            }}
        records = [record(self.ids[0], "direct_design_work", "design_explanation"),
                   record(self.ids[1], "design_explanation", "direct_design_work")]
        pilot = {"schema_version": "madia-coder-evidence-v1", "phase": "pilot", "coders": ["coder-a", "coder-b"],
                 "population_size": 999, "records": records}
        production = copy.deepcopy(pilot)
        production["phase"] = "production"
        production["records"].append(record(self.ids[2], "direct_design_work", "direct_design_work"))
        originals = copy.deepcopy((catalog, pilot, production))
        p, q, reliability = MODULE.compute_reliability(catalog, pilot, production, set(self.ids[:2]), set(self.ids))
        self.assertEqual((catalog, pilot, production), originals)
        self.assertEqual(p["population_size"], 3)
        self.assertEqual(q["population_size"], 2)
        self.assertEqual([r["unit_id"] for r in q["records"]], self.ids[:2])
        self.assertEqual(reliability["pilot_sample_size"], 2)
        self.assertEqual(reliability["pilot_kappa"], -1.0)
        self.assertEqual(reliability["production_kappa"], -1.0)
        self.assertEqual(reliability["production_double_coded_ratio"], 1.0)
        _, q, reliability = MODULE.compute_reliability(catalog, None, production, set(), {self.ids[0]})
        self.assertEqual([r["unit_id"] for r in q["records"]], [self.ids[0]])
        self.assertEqual(reliability["production_double_coded_ratio"], 0.5)
        self.assertEqual(reliability["pilot_evidence"], [])
        self.assertIsNone(reliability["pilot_sample_size"])
        _, _, reliability = MODULE.compute_reliability(catalog, None, None, set(), set())
        self.assertEqual(reliability, {
            "pilot_sample_size": None, "pilot_kappa": None, "pilot_evidence": [],
            "production_double_coded_ratio": None, "production_kappa": None, "production_evidence": [],
        })

    def test_all_existing_bundles_and_cross_role_sessions_are_checked(self) -> None:
        self.selection([self.ids[0]])
        directory = self.cache(double=True)
        b_path = directory / "analysis-coder-b.json"
        original = self.load(b_path)
        for change in ("invalid-unused-bundle", "shared-session"):
            with self.subTest(change=change):
                b = copy.deepcopy(original)
                if change == "invalid-unused-bundle":
                    b["evidence_units"][0]["visual_evidence"] = []
                else:
                    b["session_id"] = f"{self.ids[0]}-coder-a"
                self.save(b_path, b)
                before = self.snapshot()
                self.cli("--merge-analysis", directory, succeeds=False)
                self.assertEqual(self.snapshot(), before)

    def test_reliability_uses_weakest_dimension_and_null_for_undefined_dimension(self) -> None:
        catalog = self.load(self.catalog_path)
        payload = {
            "schema_version": "madia-coder-evidence-v1", "phase": "pilot", "coders": ["coder-a", "coder-b"],
            "population_size": 3, "records": [
                {"unit_id": self.ids[0], "ratings": {
                    "relevance": {"coder-a": "direct_design_work", "coder-b": "design_explanation"},
                    "decision_stage": {"coder-a": "information_priority", "coder-b": "information_priority"},
                    "evidence_kind": {"coder-a": "verbalized", "coder-b": "verbalized"},
                }},
                {"unit_id": self.ids[1], "ratings": {
                    "relevance": {"coder-a": "design_explanation", "coder-b": "direct_design_work"},
                    "decision_stage": {"coder-a": "visual_system", "coder-b": "visual_system"},
                    "evidence_kind": {"coder-a": "inferred", "coder-b": "inferred"},
                }},
            ],
        }
        _, _, reliability = MODULE.compute_reliability(catalog, payload, None, set(self.ids[:2]), set())
        self.assertEqual(reliability["pilot_kappa"], -1.0)
        payload["records"][1]["ratings"]["evidence_kind"] = {"coder-a": "verbalized", "coder-b": "verbalized"}
        _, _, reliability = MODULE.compute_reliability(catalog, payload, None, set(self.ids[:2]), set())
        self.assertIsNone(reliability["pilot_kappa"])
        payload["records"] = []
        _, _, reliability = MODULE.compute_reliability(catalog, payload, None, set(self.ids[:2]), set())
        self.assertIsNone(reliability["pilot_sample_size"])
        self.assertEqual(reliability["pilot_evidence"], [])

    def test_normalize_recomputes_reliability_and_rolls_back_evidence(self) -> None:
        self.selection([self.ids[0]])
        self.cli("--merge-analysis", self.cache(double=True), self.cache(1))
        path = self.evidence / "production-coder-evidence.json"
        payload = self.load(path)
        stale = copy.deepcopy(payload["records"][0])
        stale["unit_id"] = self.ids[1]
        payload["records"].append(stale)
        payload["population_size"] = 999
        self.save(path, payload)
        before = self.snapshot()
        self.cli("--normalize", succeeds=False, fail_summary=True)
        self.assertEqual(self.snapshot(), before)
        self.cli("--normalize")
        self.assertEqual(self.load(path)["population_size"], 2)
        self.assertEqual([r["unit_id"] for r in self.load(path)["records"]], [self.ids[0]])
        self.assertEqual(self.load(self.catalog_path)["reliability"]["production_double_coded_ratio"], 0.5)
        normalized = self.snapshot()
        self.cli("--normalize")
        self.assertEqual(self.snapshot(), normalized)

    def test_quality_gate_replacement_validates_before_publishing_other_changes(self) -> None:
        self.cli("--merge-analysis", self.cache())
        gates = self.load(self.catalog_path)["quality_gates"]
        gates[0] = {"id": "M0", "status": "blocked", "evidence": ["madia-evidence/gate.txt"]}
        (self.evidence / "gate.txt").write_text("Discovery is incomplete.", encoding="utf-8")
        self.cli("--apply-curation", self.curate(quality_gates=gates))
        self.assertEqual(self.load(self.catalog_path)["quality_gates"], gates)
        gates[0]["status"] = "passed"
        before = self.snapshot()
        self.cli("--apply-curation", self.curate(
            quality_gates=gates, term_assignments={f"{self.ids[0]}:001": ["term.spacing"]}),
            succeeds=False)
        self.assertEqual(self.snapshot(), before)


if __name__ == "__main__":
    unittest.main()
