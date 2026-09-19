#!/usr/bin/env python3
"""Snapshot Madia Designer public video metadata without copying media or transcripts."""

from __future__ import annotations

import argparse
import copy
import json
import os
import re
import subprocess
import sys
import tempfile
import urllib.request
import xml.etree.ElementTree as ET
from datetime import date
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[1]
CATALOG = ROOT / "docs" / "research" / "madia-design-practice-catalog.json"
SUMMARY = ROOT / "docs" / "research" / "madia-design-practice-catalog.md"
VALIDATOR = ROOT / "scripts" / "validate_madia_design_catalog.py"
SOURCE_MANIFEST_PATH = ROOT / "shared" / "design-quality" / "madia-source-manifest.json"
SOURCE_MANIFEST = json.loads(SOURCE_MANIFEST_PATH.read_text(encoding="utf-8"))
CHANNEL = SOURCE_MANIFEST["channel"]
CHANNEL_ID = CHANNEL["id"]
PLAYLISTS = SOURCE_MANIFEST["playlists"]
UPLOADS_PLAYLIST_ID = PLAYLISTS["uploads"]
MAX_DISCOVERY_DEPTH = 256
MAX_DISCOVERY_NODES = 100_000
MAX_PLAYLIST_CONTINUATION_PAGES = 500
MAX_PLAYLIST_VIDEOS = 100_000
VIDEO_ID_RE = re.compile(r"^[A-Za-z0-9_-]{11}$")
CHANNEL_ID_RE = re.compile(r"^UC[A-Za-z0-9_-]{22}$")
USER_AGENT = "Mozilla/5.0 (compatible; design-research-metadata-snapshot/1.0)"


def fetch_text(url: str) -> str:
    request = urllib.request.Request(url, headers={"User-Agent": USER_AGENT})
    with urllib.request.urlopen(request, timeout=30) as response:
        return response.read().decode("utf-8")


def post_json(url: str, payload: dict[str, Any]) -> dict[str, Any]:
    request = urllib.request.Request(
        url,
        data=json.dumps(payload).encode("utf-8"),
        headers={"Content-Type": "application/json", "User-Agent": USER_AGENT},
    )
    with urllib.request.urlopen(request, timeout=30) as response:
        return json.load(response)


def parse_initial_data(page: str) -> dict[str, Any]:
    marker = "var ytInitialData = "
    start = page.find(marker)
    if start < 0:
        raise ValueError("ytInitialData not found")
    data, _ = json.JSONDecoder().raw_decode(page[start + len(marker) :])
    return data


def title_from_lockup(lockup: dict[str, Any]) -> str | None:
    try:
        title = lockup["metadata"]["lockupMetadataViewModel"]["title"]["content"]
    except (KeyError, TypeError):
        return None
    return title if isinstance(title, str) and title.strip() else None


def direct_lockup(item: Any) -> dict[str, Any] | None:
    if not isinstance(item, dict):
        return None
    lockup = item.get("lockupViewModel")
    return lockup if isinstance(lockup, dict) else None


def direct_continuation(item: Any) -> str | None:
    if not isinstance(item, dict):
        return None
    view = item.get("continuationItemViewModel")
    if not isinstance(view, dict):
        return None
    command = view.get("continuationCommand")
    if not isinstance(command, dict):
        return None
    inner = command.get("innertubeCommand")
    if isinstance(inner, dict):
        command = inner.get("continuationCommand")
    if not isinstance(command, dict):
        return None
    token = command.get("token")
    return token if isinstance(token, str) and token else None


def bounded_walk(value: Any):
    stack: list[tuple[Any, int]] = [(value, 0)]
    visited = 0
    while stack:
        item, depth = stack.pop()
        visited += 1
        if depth > MAX_DISCOVERY_DEPTH or visited > MAX_DISCOVERY_NODES:
            raise ValueError("playlist parser traversal limit exceeded")
        yield item
        if isinstance(item, dict):
            stack.extend((child, depth + 1) for child in reversed(list(item.values())))
        elif isinstance(item, list):
            stack.extend((child, depth + 1) for child in reversed(item))


def candidate_item_lists(value: Any):
    stack: list[tuple[Any, int, Any]] = [(value, 0, None)]
    visited = 0
    while stack:
        item, depth, parent = stack.pop()
        visited += 1
        if depth > MAX_DISCOVERY_DEPTH or visited > MAX_DISCOVERY_NODES:
            raise ValueError("playlist parser traversal limit exceeded")
        if isinstance(item, list):
            lockup_count = sum(1 for child in item if direct_lockup(child) is not None)
            if lockup_count:
                yield item, lockup_count, parent
            stack.extend((child, depth + 1, item) for child in reversed(item))
        elif isinstance(item, dict):
            stack.extend(
                (child, depth + 1, item)
                for child in reversed(list(item.values()))
            )


def extract_video_page(data: dict[str, Any]) -> tuple[list[dict[str, str]], str | None]:
    candidates = list(candidate_item_lists(data))
    if not candidates:
        return [], None
    maximum = max(candidate[1] for candidate in candidates)
    strongest = [candidate for candidate in candidates if candidate[1] == maximum]
    if len(strongest) != 1:
        raise ValueError("playlist parser found ambiguous item lists")
    items, _, selected_parent = strongest[0]
    videos: list[dict[str, str]] = []
    for item in items:
        if isinstance(item, dict) and "lockupViewModel" in item:
            lockup = direct_lockup(item)
            if lockup is None:
                raise ValueError("playlist parser found malformed video lockup")
            video_id = lockup.get("contentId")
            title = title_from_lockup(lockup)
            if not isinstance(video_id, str) or not VIDEO_ID_RE.fullmatch(video_id) or not title:
                raise ValueError("playlist parser found malformed video lockup")
            videos.append({"video_id": video_id, "title": title})

    continuation_tokens: set[str] = set()
    malformed_continuation = False
    continuation_roots: list[Any] = [items]
    if isinstance(selected_parent, dict):
        for key, value in selected_parent.items():
            if value is items:
                continue
            normalized_key = str(key).casefold()
            if "continuation" in normalized_key or "pagination" in normalized_key:
                continuation_roots.append(value)
    for root in continuation_roots:
        for value in bounded_walk(root):
            if isinstance(value, dict) and "continuationItemViewModel" in value:
                token = direct_continuation(value)
                if token is None:
                    malformed_continuation = True
                else:
                    continuation_tokens.add(token)
    if malformed_continuation:
        raise ValueError("playlist parser found malformed continuation")
    if len(continuation_tokens) > 1:
        raise ValueError("playlist parser found ambiguous continuation tokens")
    continuation = (
        next(iter(continuation_tokens)) if continuation_tokens else None
    )
    return videos, continuation


def fetch_playlist(playlist_id: str) -> tuple[list[dict[str, str]], bool]:
    url = f"https://www.youtube.com/playlist?list={playlist_id}"
    page = fetch_text(url)
    data = parse_initial_data(page)
    api_key_match = re.search(r'"INNERTUBE_API_KEY":"([^"]+)"', page)
    version_match = re.search(r'"INNERTUBE_CONTEXT_CLIENT_VERSION":"([^"]+)"', page)
    if not api_key_match or not version_match:
        raise ValueError(f"YouTube browse configuration missing for {playlist_id}")
    videos, continuation = extract_video_page(data)
    if not videos:
        raise ValueError(f"playlist parser returned no videos for {playlist_id}")
    all_videos = list(videos)
    if len(all_videos) > MAX_PLAYLIST_VIDEOS:
        raise ValueError(f"playlist video limit exceeded for {playlist_id}")
    seen_tokens: set[str] = set()
    continuation_pages = 0
    while continuation:
        if continuation_pages >= MAX_PLAYLIST_CONTINUATION_PAGES:
            raise ValueError(f"continuation page limit exceeded for {playlist_id}")
        if continuation in seen_tokens:
            raise ValueError(f"repeated continuation token for {playlist_id}")
        seen_tokens.add(continuation)
        continuation_pages += 1
        response = post_json(
            f"https://www.youtube.com/youtubei/v1/browse?key={api_key_match.group(1)}",
            {
                "context": {
                    "client": {
                        "clientName": "WEB",
                        "clientVersion": version_match.group(1),
                        "hl": "ko",
                    }
                },
                "continuation": continuation,
            },
        )
        page_videos, continuation = extract_video_page(response)
        if not page_videos:
            raise ValueError(f"continuation returned no videos for {playlist_id}")
        all_videos.extend(page_videos)
        if len(all_videos) > MAX_PLAYLIST_VIDEOS:
            raise ValueError(f"playlist video limit exceeded for {playlist_id}")
    unique: dict[str, dict[str, str]] = {}
    for video in all_videos:
        unique.setdefault(video["video_id"], video)
    return list(unique.values()), True


def fetch_recent_feed() -> dict[str, dict[str, str]]:
    xml = fetch_text(f"https://www.youtube.com/feeds/videos.xml?channel_id={CHANNEL_ID}")
    root = ET.fromstring(xml)
    namespaces = {
        "atom": "http://www.w3.org/2005/Atom",
        "yt": "http://www.youtube.com/xml/schemas/2015",
    }
    recent: dict[str, dict[str, str]] = {}
    for entry in root.findall("atom:entry", namespaces):
        video_id = entry.findtext("yt:videoId", namespaces=namespaces)
        channel_id = entry.findtext("yt:channelId", namespaces=namespaces)
        title = entry.findtext("atom:title", namespaces=namespaces)
        published = entry.findtext("atom:published", namespaces=namespaces)
        link = entry.find("atom:link[@rel='alternate']", namespaces)
        href = link.get("href") if link is not None else None
        if video_id:
            if channel_id != CHANNEL_ID:
                raise ValueError(
                    f"channel feed entry {video_id} is not owned by the canonical channel"
                )
            if not isinstance(title, str) or not title.strip():
                raise ValueError(f"channel feed title missing for {video_id}")
            recent[video_id] = {
                "title": title.strip(),
                "published_at": published,
                "content_type": "short" if href and "/shorts/" in href else "unknown",
            }
    return recent


def fetch_video_channel_id(video_id: str) -> str:
    page = fetch_text(f"https://www.youtube.com/watch?v={video_id}")
    matches = set(
        re.findall(r'"externalChannelId"\s*:\s*"(UC[A-Za-z0-9_-]{22})"', page)
    )
    if len(matches) != 1:
        raise ValueError(f"unable to verify canonical channel ownership for {video_id}")
    channel_id = next(iter(matches))
    if not CHANNEL_ID_RE.fullmatch(channel_id):
        raise ValueError(f"invalid channel owner metadata for {video_id}")
    return channel_id


def load_existing() -> dict[str, Any] | None:
    if not CATALOG.exists():
        return None
    return json.loads(CATALOG.read_text(encoding="utf-8"))


def validate_existing_catalog(value: Any) -> None:
    if not isinstance(value, dict):
        raise ValueError("existing catalog must be a JSON object")
    CATALOG.parent.mkdir(parents=True, exist_ok=True)
    temporary: Path | None = None
    try:
        with tempfile.NamedTemporaryFile(
            "w", encoding="utf-8", dir=CATALOG.parent, delete=False
        ) as handle:
            json.dump(value, handle, ensure_ascii=False)
            temporary = Path(handle.name)
        try:
            validate(temporary)
        except ValueError as error:
            raise ValueError(f"existing catalog is invalid: {error}") from error
    finally:
        if temporary is not None:
            temporary.unlink(missing_ok=True)


def pending_video(video_id: str, title: str) -> dict[str, Any]:
    return {
        "video_id": video_id,
        "title": title,
        "url": f"https://www.youtube.com/watch?v={video_id}",
        "published_at": None,
        "content_type": "unknown",
        "playlist_ids": [],
        "status": "pending",
        "exclusion_reason": None,
        "blocking_reason": None,
        "duplicate_of": None,
        "evidence_units": [],
    }


def build_catalog(as_of: str) -> dict[str, Any]:
    playlist_videos: dict[str, list[dict[str, str]]] = {}
    complete = True
    for name, playlist_id in PLAYLISTS.items():
        videos, playlist_complete = fetch_playlist(playlist_id)
        if not playlist_complete:
            raise ValueError(f"playlist discovery is incomplete for {playlist_id}")
        playlist_videos[name] = videos
        complete = complete and playlist_complete
    discovered: dict[str, dict[str, str]] = {}
    for name in PLAYLISTS:
        for video in playlist_videos[name]:
            discovered.setdefault(video["video_id"], video)
    recent = fetch_recent_feed()
    for video_id, metadata in recent.items():
        title = metadata.get("title")
        if not isinstance(title, str) or not title.strip():
            raise ValueError(f"channel feed title missing for {video_id}")
        discovered.setdefault(
            video_id,
            {"video_id": video_id, "title": title.strip()},
        )
    playlist_video_ids = {
        video["video_id"]
        for videos in playlist_videos.values()
        for video in videos
    }
    for video_id in sorted(playlist_video_ids):
        owner = fetch_video_channel_id(video_id)
        if owner != CHANNEL_ID:
            raise ValueError(
                f"playlist video {video_id} is not owned by the canonical channel"
            )
    existing_value = load_existing()
    if existing_value is None:
        existing: dict[str, Any] = {}
    else:
        validate_existing_catalog(existing_value)
        existing = existing_value
    existing_videos = {
        video.get("video_id"): video
        for video in existing.get("videos", [])
        if isinstance(video, dict) and isinstance(video.get("video_id"), str)
    }
    if not discovered:
        raise ValueError("playlist discovery returned zero videos; refusing catalog publication")
    missing_existing = sorted(set(existing_videos) - set(discovered))
    if missing_existing:
        raise ValueError(
            "playlist discovery omitted existing catalog videos; refusing partial publication "
            f"({len(missing_existing)} missing)"
        )
    membership: dict[str, set[str]] = {video_id: set() for video_id in discovered}
    for name, videos in playlist_videos.items():
        for video in videos:
            video_id = video["video_id"]
            membership[video_id].add(name)
    existing_queue = [
        video.get("video_id")
        for video in existing.get("videos", [])
        if isinstance(video, dict) and video.get("video_id") in discovered
    ]
    new_video_ids = [video_id for video_id in discovered if video_id not in existing_videos]
    merged: list[dict[str, Any]] = []
    for video_id in [*existing_queue, *new_video_ids]:
        metadata = discovered[video_id]
        prior = existing_videos.get(video_id)
        item = dict(prior) if prior else pending_video(video_id, metadata["title"])
        item["title"] = metadata["title"]
        item["url"] = f"https://www.youtube.com/watch?v={video_id}"
        item["playlist_ids"] = sorted(membership[video_id])
        if video_id in recent:
            item["published_at"] = recent[video_id]["published_at"]
            item["content_type"] = recent[video_id]["content_type"]
        merged.append(item)
    counts = {status: 0 for status in ("analyzed", "excluded", "blocked", "pending")}
    for item in merged:
        counts[item["status"]] += 1
    total = len(merged)
    coverage = (counts["analyzed"] + counts["excluded"] + counts["blocked"]) / total if total else 0.0
    principles = copy.deepcopy(existing.get("principles", []))
    reliability = copy.deepcopy(existing.get(
        "reliability",
        {
            "pilot_sample_size": None,
            "pilot_kappa": None,
            "pilot_evidence": [],
            "production_double_coded_ratio": None,
            "production_kappa": None,
            "production_evidence": [],
        },
    ))
    gates = copy.deepcopy(existing.get(
        "quality_gates",
        [{"id": f"M{index}", "status": "not_run", "evidence": []} for index in range(9)],
    ))
    if existing and new_video_ids:
        for principle in principles:
            if isinstance(principle, dict):
                principle["tier"] = "P0"
                principle["validation_status"] = "not_run"
                fixture = principle.get("behavior_fixture")
                if isinstance(fixture, dict):
                    fixture["status"] = "not_run"
        reliability["production_double_coded_ratio"] = None
        reliability["production_kappa"] = None
        reliability["production_evidence"] = []
        gates = [
            {"id": f"M{index}", "status": "not_run", "evidence": []}
            for index in range(9)
        ]
    return {
        "schema_version": "madia-design-practice-catalog-v1",
        "as_of": as_of,
        "channel": {
            "id": CHANNEL_ID,
            "title": CHANNEL["title"],
            "url": CHANNEL["url"],
        },
        "scope": "Every discovered public channel video is inventoried; UI/UX-relevant videos require full video and screen-change analysis before promotion.",
        "source_policy": {
            "public_only": True,
            "paid_or_membership_excluded": True,
            "metadata_is_not_principle_evidence": True,
        },
        "copyright": {"stores_full_transcripts": False, "stores_media": False},
        "inventory": {
            "discovery_complete": complete,
            "discovery_sources": [
                f"uploads-playlist:{UPLOADS_PLAYLIST_ID}",
                *[f"playlist:{name}:{playlist_id}" for name, playlist_id in PLAYLISTS.items() if name != "uploads"],
                f"channel-feed:{CHANNEL_ID}",
            ],
            "discovered_unique_videos": total,
            **counts,
            "corpus_coverage": coverage,
        },
        "reliability": reliability,
        "videos": merged,
        "principles": principles,
        "quality_gates": gates,
    }


def render_summary(catalog: dict[str, Any]) -> str:
    inventory = catalog["inventory"]
    gate_rows = "".join(
        f"| {gate['id']} | `{gate['status']}` |\n" for gate in catalog["quality_gates"]
    )
    principle_rows = ""
    for principle in catalog["principles"]:
        principle_rows += (
            f"| `{principle['id']}` | `{principle['tier']}` | {principle['label']} | "
            f"`{principle['validation_status']}` |\n"
        )
    if not principle_rows:
        principle_rows = "| - | - | 아직 승격된 원칙 없음 | `not_run` |\n"
    return f"""# Madia Designer 디자인 실무 관찰 카탈로그

기준일: {catalog['as_of']}

이 문서는 [Madia Designer 공개 채널]({catalog['channel']['url']})의 영상을 실무 관찰 코퍼스로 분석하기 위한 상태 요약이다. 개인의 조언을 UX 표준으로 간주하지 않으며, 영상 전체와 화면 수정 전후를 확인하지 않은 항목은 원칙 근거가 아니다.

## 현재 상태

- 발견한 고유 공개 영상: {inventory['discovered_unique_videos']}
- 분석 완료: {inventory['analyzed']}
- 범위 제외: {inventory['excluded']}
- 접근 차단: {inventory['blocked']}
- 분석 대기: {inventory['pending']}
- 코퍼스 커버리지: {inventory['corpus_coverage']:.4f}
- discovery complete: `{str(inventory['discovery_complete']).lower()}`

모든 영상별 상태와 URL은 [JSON 원장](madia-design-practice-catalog.json)에 있다. 코딩 단위, 이중 코딩과 원칙 승격 절차는 [연구 방법](madia-design-practice-method.md)을 따른다. 전체 자막, 영상, 썸네일이나 유료·멤버십 자료는 저장하지 않는다.

## 승격된 원칙

| ID | Tier | 원칙 | 동작 평가 |
| --- | --- | --- | --- |
{principle_rows}
## 연구 퀄리티 게이트

| Gate | 상태 |
| --- | --- |
{gate_rows}
`P1` 이상은 비중복 직접 관찰 3건과 서로 다른 프로젝트 2개 이상, `P2`는 독립 근거, `P3`는 적용 조건·예외·행동 평가 통과가 필요하다. `M0`–`M8` 중 하나라도 필수 조건을 충족하지 못하면 해당 원칙을 스킬의 차단 규칙으로 승격하지 않는다.
"""


def validate(path: Path) -> None:
    result = subprocess.run(
        [sys.executable, str(VALIDATOR), str(path)],
        cwd=ROOT,
        text=True,
        capture_output=True,
        check=False,
    )
    if result.returncode:
        raise ValueError(result.stdout + result.stderr)


def atomic_write(path: Path, data: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    temporary: Path | None = None
    try:
        with tempfile.NamedTemporaryFile("w", encoding="utf-8", dir=path.parent, delete=False) as handle:
            handle.write(data)
            temporary = Path(handle.name)
        os.replace(temporary, path)
        temporary = None
    finally:
        if temporary is not None:
            temporary.unlink(missing_ok=True)


def publish_catalog(catalog: dict[str, Any]) -> None:
    encoded = json.dumps(catalog, ensure_ascii=False, indent=2) + "\n"
    CATALOG.parent.mkdir(parents=True, exist_ok=True)
    temporary: Path | None = None
    try:
        with tempfile.NamedTemporaryFile(
            "w", encoding="utf-8", dir=CATALOG.parent, delete=False
        ) as handle:
            handle.write(encoded)
            temporary = Path(handle.name)
        validate(temporary)
    finally:
        if temporary is not None:
            temporary.unlink(missing_ok=True)
    summary = render_summary(catalog)
    previous = {
        path: path.read_text(encoding="utf-8") if path.exists() else None
        for path in (CATALOG, SUMMARY)
    }
    try:
        atomic_write(CATALOG, encoded)
        atomic_write(SUMMARY, summary)
    except OSError:
        for path, content in previous.items():
            if content is None:
                path.unlink(missing_ok=True)
            else:
                atomic_write(path, content)
        raise


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--check", action="store_true", help="validate the committed snapshot without network access")
    parser.add_argument("--as-of", default=date.today().isoformat())
    args = parser.parse_args()
    try:
        if args.check:
            validate(CATALOG)
            catalog = json.loads(CATALOG.read_text(encoding="utf-8"))
            expected = render_summary(catalog)
            if not SUMMARY.exists() or SUMMARY.read_text(encoding="utf-8") != expected:
                print(f"stale: {SUMMARY.relative_to(ROOT)}")
                return 1
            print("OK: Madia catalog snapshot and summary")
            return 0
        catalog = build_catalog(args.as_of)
        publish_catalog(catalog)
        print(
            f"updated: {CATALOG.relative_to(ROOT)} "
            f"({catalog['inventory']['discovered_unique_videos']} videos, "
            f"{catalog['inventory']['pending']} pending)"
        )
        return 0
    except (OSError, ValueError, RecursionError, json.JSONDecodeError, ET.ParseError) as error:
        print(f"ERROR: {error}")
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
