from __future__ import annotations

import importlib.util
import json
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
                mock.patch.object(MODULE, "validate", side_effect=ValueError("invalid candidate")),
            ):
                with self.assertRaisesRegex(ValueError, "invalid candidate"):
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
                mock.patch.object(MODULE, "validate", return_value=None),
                mock.patch.object(MODULE.os, "replace", side_effect=fail_summary_once),
                mock.patch.object(MODULE, "render_summary", return_value="new summary\n"),
            ):
                with self.assertRaisesRegex(OSError, "summary replace failed"):
                    MODULE.publish_catalog({"inventory": {}})
            self.assertEqual(catalog_path.read_text(encoding="utf-8"), "existing catalog\n")
            self.assertEqual(summary_path.read_text(encoding="utf-8"), "existing summary\n")


if __name__ == "__main__":
    unittest.main()
