from __future__ import annotations

import importlib.util
import unittest
from pathlib import Path

SPEC = importlib.util.spec_from_file_location("madia_media", Path(__file__).resolve().parents[2] / "scripts/madia_media.py")
MEDIA = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(MEDIA)


class MediaTests(unittest.TestCase):
    def test_hyphenated_video_ids_remain_positional_with_frame_options(self):
        for video_id in ("-3unfQVvsU4", "--m2d_Ojwvw"):
            for command in ("prepare", "purge", "probe", "fetch", "cues", "sheets"):
                self.assertEqual(MEDIA.parse_args([command, video_id]).video_id, video_id)
            args = MEDIA.parse_args(["frame", video_id, "1", "--crop", "0,0,1,1"])
            self.assertEqual((args.video_id, args.seconds, args.crop),
                             (video_id, 1.0, (0.0, 0.0, 1.0, 1.0)))

    def test_rolling_captions_preserve_speech_across_cues(self):
        text = """WEBVTT

00:00:01.000 --> 00:00:02.000 align:start
<c>읽는 순서를</c>

00:00:02.000 --> 00:00:03.000
읽는 순서를
같게 만들어야

00:00:03.000 --> 00:00:04.000
같게 만들어야
비교하기 편해요.

00:00:04.000 --> 00:00:05.000
비교하기 편해요.
"""
        cues = MEDIA.parse_vtt(text)
        self.assertEqual(cues, [
            {"start": 1.0, "end": 2.0, "text": "읽는 순서를"},
            {"start": 2.0, "end": 3.0, "text": "같게 만들어야"},
            {"start": 3.0, "end": 5.0, "text": "비교하기 편해요."},
        ])
        excerpt = "읽는 순서를 같게 만들어야 비교하기 편해요."
        self.assertIn("".join(excerpt.split()), "".join("".join(cue["text"].split()) for cue in cues))

    def test_youtube_leading_space_line_preserves_first_speech_interval(self):
        text = ("WEBVTT\n\n00:00:00.680 --> 00:00:03.070\n \n"
                "읽는<00:00:01.000><c> 순서</c>\n\n"
                "00:00:03.070 --> 00:00:03.080\n읽는 순서\n \n")
        self.assertEqual(MEDIA.parse_vtt(text),
                         [{"start": 0.68, "end": 3.08, "text": "읽는 순서"}])

    def test_vtt_hours_identifiers_entities_and_missing_captions(self):
        self.assertEqual(MEDIA.parse_vtt(None), [])
        self.assertEqual(MEDIA.parse_vtt("WEBVTT\n\nNOTE metadata"), [])
        self.assertEqual(MEDIA.parse_vtt("WEBVTT\n\nid\n01:02:03.250 --> 01:02:04.500\nA &amp; B"),
                         [{"start": 3723.25, "end": 3724.5, "text": "A & B"}])

    def test_sampling_boundaries(self):
        for duration, interval in [(1, 1), (90, 1), (90.01, 2), (600, 2), (600.01, 4)]:
            with self.subTest(duration=duration):
                self.assertEqual(MEDIA.sheet_interval(duration), interval)

    def test_caption_priority(self):
        metadata = {"subtitles": {"en": [1], "ko-KR": [1], "ko": [1]},
                    "automatic_captions": {"ko": [1], "ko-orig": [1]}}
        self.assertEqual(MEDIA.select_caption(metadata), ("manual", "ko"))
        del metadata["subtitles"]["ko"]
        self.assertEqual(MEDIA.select_caption(metadata), ("manual", "ko-KR"))
        del metadata["subtitles"]["ko-KR"]
        self.assertEqual(MEDIA.select_caption(metadata), ("auto", "ko-orig"))
        del metadata["automatic_captions"]["ko-orig"]
        self.assertEqual(MEDIA.select_caption(metadata), ("auto", "ko"))
        metadata["automatic_captions"] = {}
        self.assertEqual(MEDIA.select_caption(metadata), ("manual", "en"))
        metadata["subtitles"] = {"ja": [1]}
        self.assertEqual(MEDIA.select_caption(metadata), ("none", None))

    def test_failure_classification_preserves_access_and_retry_boundaries(self):
        for phrase in MEDIA.BLOCKED:
            self.assertEqual(MEDIA.classify_error(phrase.upper())[0], 3)
        self.assertEqual(MEDIA.classify_error("Private Video HTTP error 429")[0], 3)
        self.assertEqual(MEDIA.classify_error("HTTP Error 429"), (4, "RETRY_LATER"))
        self.assertEqual(MEDIA.classify_error("Sign in to confirm you're not a bot")[0], 4)
        self.assertEqual(MEDIA.classify_error("network timeout"), (1, "network timeout"))
        rate_limit = ("Video unavailable. This content isn't available, try again later. "
                      "The current session has been rate-limited by YouTube for up to an hour.")
        self.assertEqual(MEDIA.classify_error(rate_limit), (4, "RETRY_LATER"))

    def test_title_normalization(self):
        self.assertEqual(MEDIA.normalize_title("ＡＢＣ  디자인! #Figma #한국어"), "abc디자인")

    @staticmethod
    def videos(titles):
        return [{"video_id": f"video{index:06d}", "title": title, "status": "pending"}
                for index, title in enumerate(titles)]

    def test_duplicates_exclude_blocked_and_include_media_pairs(self):
        videos = self.videos(["Ａ 디자인 #UX", "a 디자인", "다른 제목", "A 디자인"])
        videos[3]["status"] = "blocked"
        cached = {"video000001": {"duration": 20, "texts": ["a", "b", "c"]},
                  "video000002": {"duration": 21, "texts": ["a", "b", "c"]}}
        groups = MEDIA.candidate_groups(videos, "duplicate", cached)
        self.assertEqual([g["video_ids"] for g in groups],
                         [["video000000", "video000001"], ["video000001", "video000002"]])
        cached["video000002"]["duration"] = 21.01
        self.assertEqual(len(MEDIA.candidate_groups(videos, "duplicate", cached)), 1)

    def test_series_union_uses_original_tokens_prefix_and_catalog_distance(self):
        videos = self.videos(["무관"] * 25)
        for index, title in {0: "첫 작업 1부 컨펌 #15", 6: "다른 작업 2부 컨펌 #15",
                             12: "같은 작업｜1부", 18: "같은 작업[2부]",
                             23: "독립 작업 3부", 24: "제목만 비슷한 작업"}.items():
            videos[index]["title"] = title
        self.assertEqual([g["video_ids"] for g in MEDIA.candidate_groups(videos, "series")],
                         [["video000000", "video000006"],
                          ["video000012", "video000018", "video000023"]])


if __name__ == "__main__":
    unittest.main()
