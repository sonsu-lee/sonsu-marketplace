#!/usr/bin/env python3
"""Collect public Madia video evidence in a local, uncommitted cache."""
from __future__ import annotations

import argparse
import fcntl
import html
import json
import math
import os
import re
import subprocess
import sys
import unicodedata
from pathlib import Path
from typing import Any

CACHE = Path(os.environ.get("MADIA_CACHE_DIR", "~/.cache/sonsu-marketplace/madia")).expanduser()
FFMPEG = "/opt/homebrew/bin/ffmpeg"
FFPROBE = "/opt/homebrew/bin/ffprobe"
VIDEO_ID = re.compile(r"^[A-Za-z0-9_-]{11}$")
SLEEP = ["--sleep-requests", "1", "--sleep-interval", "3", "--max-sleep-interval", "8"]
BLOCKED = {
    "private video": "비공개 영상",
    "members-only": "멤버십 전용 영상",
    "join this channel": "채널 가입이 필요한 영상",
    "video unavailable": "사용할 수 없는 영상",
    "has been removed": "삭제된 영상",
    "confirm your age": "연령 확인이 필요한 영상",
}


class MediaError(Exception):
    def __init__(self, message: str, code: int = 1):
        super().__init__(message)
        self.code = code


def directory(video_id: str) -> Path:
    if not VIDEO_ID.fullmatch(video_id):
        raise MediaError("invalid video ID")
    path = CACHE / video_id
    path.mkdir(parents=True, exist_ok=True)
    return path


def save(path: Path, value: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    temporary = path.with_suffix(path.suffix + ".tmp")
    temporary.write_text(json.dumps(value, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    temporary.replace(path)


def load(path: Path) -> Any:
    return json.loads(path.read_text(encoding="utf-8"))


def classify_error(stderr: str) -> tuple[int, str]:
    lowered = stderr.lower()
    if "rate-limited" in lowered:
        return 4, "RETRY_LATER"
    for phrase, reason in BLOCKED.items():
        if phrase in lowered:
            return 3, reason
    if "http error 429" in lowered or "not a bot" in lowered:
        return 4, "RETRY_LATER"
    return 1, stderr.strip() or "영상 도구 실행 실패"


def ytdlp(video_id: str, args: list[str]) -> str:
    url = f"https://www.youtube.com/watch?v={video_id}"
    for launcher in (["uvx", "--from", "yt-dlp[default]", "yt-dlp"], ["uvx", "yt-dlp@latest"]):
        result = subprocess.run(launcher + SLEEP + args + [url], text=True, capture_output=True)
        if result.returncode == 0:
            return result.stdout
        code, reason = classify_error(result.stderr)
    if code == 3:
        save(directory(video_id) / "fetch.json", {"video_id": video_id, "status": "blocked", "reason": reason})
    raise MediaError(("BLOCKED: " if code == 3 else "") + reason, code)


def run(command: list[str]) -> subprocess.CompletedProcess:
    result = subprocess.run(command, text=True, capture_output=True)
    if result.returncode:
        raise MediaError(result.stderr.strip() or "media command failed")
    return result


def probe(video_id: str) -> dict:
    path = directory(video_id) / "probe.json"
    if not path.exists():
        save(path, json.loads(ytdlp(video_id, ["-J"])))
    return load(path)


def select_caption(metadata: dict) -> tuple[str, str | None]:
    manual = metadata.get("subtitles") or {}
    automatic = metadata.get("automatic_captions") or {}
    if manual.get("ko"):
        return "manual", "ko"
    for key in manual:
        if key.startswith("ko") and manual[key]:
            return "manual", key
    for key in ("ko-orig", "ko"):
        if automatic.get(key):
            return "auto", key
    for key in manual:
        if key.startswith("en") and manual[key]:
            return "manual", key
    return "none", None


def download_video(video_id: str) -> Path:
    path = directory(video_id) / "video.mp4"
    with (path.parent / "video.lock").open("a") as lock:
        fcntl.flock(lock.fileno(), fcntl.LOCK_EX)
        if not path.exists():
            ytdlp(video_id, ["-f", "bv*[height<=1080][vcodec^=avc1]+ba[ext=m4a]/b[height<=1080]/b",
                             "--merge-output-format", "mp4", "--remux-video", "mp4",
                             "--ffmpeg-location", str(Path(FFMPEG).parent),
                             "-o", str(path.with_suffix(".%(ext)s"))])
        if not path.is_file():
            raise MediaError("video.mp4 was not produced")
    return path


def fetch(video_id: str) -> dict:
    folder = directory(video_id)
    metadata = probe(video_id)
    source, language = select_caption(metadata)
    caption = None
    if language is not None:
        caption = f"captions.{language}.vtt"
        if not (folder / caption).is_file():
            ytdlp(video_id, ["--skip-download", "--write-subs" if source == "manual" else "--write-auto-subs",
                             "--sub-langs", "^" + re.escape(language) + "$", "--sub-format", "vtt",
                             "-o", str(folder / "captions.%(ext)s")])
        if not (folder / caption).is_file():
            raise MediaError("selected VTT caption was not produced")
    video = download_video(video_id)
    duration = float(run([FFPROBE, "-v", "error", "-show_entries", "format=duration",
                          "-of", "default=noprint_wrappers=1:nokey=1", str(video)]).stdout)
    if not math.isfinite(duration) or duration <= 0:
        raise MediaError("invalid video duration")
    result = {"video_id": video_id, "status": "ok", "duration": duration,
              "caption_source": source, "caption_file": caption}
    save(folder / "fetch.json", result)
    return result


def seconds(value: str) -> float:
    parts = value.split(":")
    total = 0.0
    for part in parts:
        total = total * 60 + float(part)
    return total


def parse_vtt(text: str | None) -> list[dict]:
    if text is None:
        return []
    cues = []
    previous_last = None
    pattern = re.compile(r"(?P<start>(?:\d+:)?\d{2}:\d{2}\.\d{3})\s+-->\s+(?P<end>(?:\d+:)?\d{2}:\d{2}\.\d{3})")
    for block in re.split(r"\n{2,}", text.replace("\r\n", "\n").strip()):
        lines = block.splitlines()
        timing = next(((index, pattern.match(line)) for index, line in enumerate(lines) if pattern.match(line)), None)
        if timing is None:
            continue
        index, match = timing
        clean = [html.unescape(re.sub(r"<[^>]*>", "", line)).strip() for line in lines[index + 1:]]
        clean = [line for line in clean if line]
        if not clean:
            continue
        raw_last = clean[-1]
        # Keep single-line repeats to merge their transition intervals below.
        if len(clean) > 1 and clean[0] == previous_last:
            clean = clean[1:]
        previous_last = raw_last
        content = " ".join(clean)
        start, end = seconds(match.group("start")), seconds(match.group("end"))
        if cues and cues[-1]["text"] == content:
            cues[-1]["end"] = max(cues[-1]["end"], end)
        else:
            cues.append({"start": start, "end": end, "text": content})
    return cues


def cues(video_id: str) -> list[dict]:
    folder = directory(video_id)
    info = load(folder / "fetch.json")
    caption = info.get("caption_file")
    result = parse_vtt((folder / caption).read_text(encoding="utf-8-sig") if caption else None)
    save(folder / "cues.json", result)
    return result


def sheet_interval(duration: float) -> int:
    return 1 if duration <= 90 else 2 if duration <= 600 else 4


def sheets(video_id: str) -> dict:
    folder = directory(video_id)
    duration = load(folder / "fetch.json")["duration"]
    interval = sheet_interval(duration)
    video = download_video(video_id)
    output = folder / "sheets"
    output.mkdir(exist_ok=True)
    for old in output.glob("sheet-*.jpg"):
        old.unlink()
    sampled = run([FFMPEG, "-hide_banner", "-y", "-i", str(video),
                   "-vf", f"fps=1/{interval}:start_time=0:round=up,scale=480:-1,showinfo,tile=4x3",
                   "-fps_mode", "vfr", "-q:v", "3", str(output / "sheet-%04d.jpg")])
    times = [float(value) for value in re.findall(r"pts_time:([0-9.eE+-]+)", sampled.stderr)]
    files = sorted(output.glob("sheet-*.jpg"))
    if len(files) != math.ceil(len(times) / 12):
        raise MediaError("contact sheet count does not match video sampling times")
    result = {"interval": interval, "sheets": [
        {"file": str(path.relative_to(folder)), "times": times[index * 12:(index + 1) * 12]}
        for index, path in enumerate(files)
    ]}
    save(folder / "sheets.json", result)
    scene_output = run([FFMPEG, "-hide_banner", "-i", str(video), "-vf",
                        "select='gt(scene,0.06)',showinfo", "-an", "-f", "null", "-"])
    changes = sorted(set(float(value) for value in re.findall(r"pts_time:([0-9.]+)", scene_output.stderr)))
    save(folder / "scenes.json", changes)
    return result


def crop_region(value: str) -> tuple[float, float, float, float]:
    try:
        region = tuple(float(item) for item in value.split(","))
    except ValueError as error:
        raise argparse.ArgumentTypeError("crop must contain four normalized numbers") from error
    if len(region) != 4 or not all(math.isfinite(item) for item in region):
        raise argparse.ArgumentTypeError("crop must contain four normalized finite numbers")
    x, y, w, h = region
    if x < 0 or y < 0 or w <= 0 or h <= 0 or x + w > 1 or y + h > 1:
        raise argparse.ArgumentTypeError("crop must fit the normalized frame")
    return region


def frame(video_id: str, time: float, crop: tuple | None = None) -> Path:
    if not math.isfinite(time) or time < 0:
        raise MediaError("frame time must be nonnegative and finite")
    folder = directory(video_id)
    video = download_video(video_id)
    suffix = "" if crop is None else "-crop-" + "_".join(f"{item:.3f}" for item in crop)
    path = folder / "frames" / f"t-{round(time * 1000)}{suffix}.png"
    path.parent.mkdir(exist_ok=True)
    command = [FFMPEG, "-hide_banner", "-loglevel", "error", "-y", "-ss", str(time), "-i", str(video)]
    if crop is not None:
        x, y, w, h = crop
        command += ["-vf", f"crop=iw*{w}:ih*{h}:iw*{x}:ih*{y}"]
    run(command + ["-frames:v", "1", "-update", "1", str(path)])
    if not path.is_file():
        raise MediaError("frame time lies outside decodable video")
    return path


def normalize_title(title: str) -> str:
    value = unicodedata.normalize("NFKC", title).lower()
    value = re.sub(r"#\S+", "", value)
    return re.sub(r"[^0-9a-z가-힣]", "", value)


def grouped_indices(edges: list[tuple[int, int]], videos: list[dict], prefix: str) -> list[dict]:
    parents = list(range(len(videos)))
    def root(index: int) -> int:
        while parents[index] != index:
            parents[index] = parents[parents[index]]
            index = parents[index]
        return index
    for first, second in edges:
        parents[root(second)] = root(first)
    groups: dict[int, list[int]] = {}
    for index in range(len(videos)):
        groups.setdefault(root(index), []).append(index)
    return [{"key": f"{prefix}:{members[0]}", "video_ids": [videos[index]["video_id"] for index in members]}
            for members in groups.values() if len(members) > 1]


def candidate_groups(videos: list[dict], kind: str, cached: dict | None = None) -> list[dict]:
    eligible = [index for index, video in enumerate(videos) if video["status"] != "blocked"]
    edges = []
    seen: dict[str, int] = {}
    if kind == "duplicate":
        for index in eligible:
            key = normalize_title(videos[index]["title"])
            if key in seen:
                edges.append((seen[key], index))
            seen[key] = index
        result = grouped_indices(edges, videos, "title")
        cached = cached or {}
        for position, first in enumerate(eligible):
            a = cached.get(videos[first]["video_id"])
            if a is None:
                continue
            for second in eligible[position + 1:]:
                b = cached.get(videos[second]["video_id"])
                if b is not None and abs(a["duration"] - b["duration"]) <= 1 and a["texts"] == b["texts"]:
                    result.append({"key": f"media:{first}:{second}", "video_ids": [videos[first]["video_id"], videos[second]["video_id"]]})
        return result
    previous = None
    for index in eligible:
        title = videos[index]["title"]
        if not re.search(r"\d+부", title):
            continue
        keys = ["prefix:" + normalize_title(re.split(r"[\[｜|]", title)[0])]
        token = re.search(r"컨펌 #\d+", title)
        if token:
            keys.append("token:" + token.group())
        for key in keys:
            if key in seen:
                edges.append((seen[key], index))
            seen[key] = index
        if previous is not None and index - previous <= 5:
            edges.append((previous, index))
        previous = index
    return grouped_indices(edges, videos, "series")


def groups(catalog: Path, kind: str) -> list[dict]:
    videos = load(catalog)["videos"]
    cached = {}
    if kind == "duplicate":
        for video in videos:
            folder = CACHE / video["video_id"]
            if (folder / "fetch.json").is_file() and (folder / "cues.json").is_file():
                info = load(folder / "fetch.json")
                if info.get("status") == "ok":
                    cached[video["video_id"]] = {"duration": info["duration"], "texts": [cue["text"] for cue in load(folder / "cues.json")[:3]]}
    return candidate_groups(videos, kind, cached)


class VideoArgumentParser(argparse.ArgumentParser):
    def _parse_optional(self, arg_string):
        # A valid YouTube ID can begin with either '-' or '--'.
        if VIDEO_ID.fullmatch(arg_string):
            return None
        return super()._parse_optional(arg_string)


def parse_args(argv: list[str] | None = None):
    parser = VideoArgumentParser(description=__doc__)
    commands = parser.add_subparsers(dest="command", required=True)
    for name in ("probe", "fetch", "cues", "sheets", "prepare", "frame", "purge"):
        command = commands.add_parser(name)
        command.add_argument("video_id")
        if name == "frame":
            command.add_argument("seconds", type=float)
            command.add_argument("--crop", type=crop_region)
    command = commands.add_parser("groups")
    command.add_argument("--catalog", type=Path, required=True)
    command.add_argument("--kind", choices=("duplicate", "series"), required=True)
    return parser.parse_args(argv)


def main() -> int:
    args = parse_args()
    try:
        if args.command == "groups":
            print(json.dumps(groups(args.catalog, args.kind), ensure_ascii=False, indent=2))
        elif args.command == "prepare":
            fetch(args.video_id)
            cues(args.video_id)
            sheets(args.video_id)
            print(f"OK: prepared {args.video_id}")
        elif args.command == "frame":
            print(frame(args.video_id, args.seconds, args.crop))
        elif args.command == "purge":
            (directory(args.video_id) / "video.mp4").unlink(missing_ok=True)
            print(f"OK: purged {args.video_id}")
        else:
            result = {"probe": probe, "fetch": fetch, "cues": cues, "sheets": sheets}[args.command](args.video_id)
            print(json.dumps(result, ensure_ascii=False, indent=2))
        return 0
    except MediaError as error:
        print(str(error), file=sys.stderr)
        return error.code
    except (OSError, ValueError, KeyError) as error:
        print(f"ERROR: {error}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
