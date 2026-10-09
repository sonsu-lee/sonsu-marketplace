#!/usr/bin/env python3
"""Snapshot Madia Designer public video metadata without copying media or transcripts."""

from __future__ import annotations

import argparse
import copy
import hashlib
import importlib.util
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
        "analysis_receipt": None,
        "evidence_units": [],
    }


def status_counts(videos: list[dict[str, Any]]) -> tuple[dict[str, int], float]:
    counts = {status: 0 for status in ("analyzed", "excluded", "blocked", "pending")}
    for video in videos:
        status = video.get("status")
        if not isinstance(status, str) or status not in counts:
            raise ValueError(f"{video.get('video_id', '<unknown>')}: invalid status")
        counts[status] += 1
    closed = len(videos) - counts["pending"]
    return counts, closed / len(videos) if videos else 0.0


def normalize_catalog(catalog: dict[str, Any]) -> dict[str, Any]:
    result = copy.deepcopy(catalog)
    if result.get("schema_version") == "madia-design-practice-catalog-v1":
        result["schema_version"] = "madia-design-practice-catalog-v2"
    for video in result["videos"]:
        video.setdefault("analysis_receipt", None)
    for principle in result["principles"]:
        principle.setdefault("durability", "contextual")
        principle.setdefault("term_ids", [])
    counts, coverage = status_counts(result["videos"])
    result["inventory"].update(
        discovered_unique_videos=len(result["videos"]), corpus_coverage=coverage, **counts
    )
    return result


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
            f"({len(missing_existing)} missing): {missing_existing}"
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
    counts, coverage = status_counts(merged)
    total = len(merged)
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
        "schema_version": "madia-design-practice-catalog-v2",
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
`P1` 이상은 검증된 직접 관찰 3건, 고유 프로젝트 3개, 서로 다른 영상 3편 이상, `P2`는 독립 근거, `P3`는 적용 조건·예외·행동 평가 통과가 필요하다. `M0`–`M8` 중 하나라도 필수 조건을 충족하지 못하면 해당 원칙을 스킬의 차단 규칙으로 승격하지 않는다.
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


def atomic_write(path: Path, data: str | bytes) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    temporary: Path | None = None
    try:
        options = {"encoding": "utf-8"} if isinstance(data, str) else {}
        with tempfile.NamedTemporaryFile(
            "w" if isinstance(data, str) else "wb", dir=path.parent, delete=False, **options
        ) as handle:
            temporary = Path(handle.name)
            handle.write(data)
        os.replace(temporary, path)
        temporary = None
    finally:
        if temporary is not None:
            temporary.unlink(missing_ok=True)


def validator_module():
    spec = importlib.util.spec_from_file_location("madia_catalog_validator", VALIDATOR)
    assert spec is not None and spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def publish_catalog(catalog: dict[str, Any]) -> None:
    encoded = json.dumps(catalog, ensure_ascii=False, indent=2) + "\n"
    errors = validator_module().validate_catalog(catalog, CATALOG.parent)
    if errors:
        contextual = []
        for error in errors:
            match = re.match(r"videos\[(\d+)\]", error)
            if match:
                video = catalog["videos"][int(match.group(1))]
                error = f"{video.get('video_id', '<unknown>')}: {error}"
            contextual.append(error)
        raise ValueError("\n".join(contextual))
    summary = render_summary(catalog)
    previous = {
        path: path.read_bytes() if path.exists() else None
        for path in (CATALOG, SUMMARY)
    }
    try:
        atomic_write(CATALOG, encoded)
        atomic_write(SUMMARY, summary)
    except Exception:
        for path, content in previous.items():
            if content is None:
                path.unlink(missing_ok=True)
            else:
                atomic_write(path, content)
        raise

VALIDATION = validator_module()
EVIDENCE_FILES = {
    "pilot": "pilot-coder-evidence.json",
    "production": "production-coder-evidence.json",
}


def read_json(path: Path) -> Any:
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except (OSError, UnicodeError, ValueError) as error:
        raise ValueError(f"cannot read {path.name}: {error}") from error


def selection_ids(path: Path, phase: str, catalog_ids: set[str]) -> set[str]:
    if not path.exists():
        return set()
    payload = read_json(path)
    schema = "madia-pilot-selection-v1" if phase == "pilot" else "madia-production-sample-v1"
    if not isinstance(payload, dict) or payload.get("schema_version") != schema:
        raise ValueError(f"{path.name}: schema_version must be {schema}")
    ids = payload.get("video_ids")
    if not VALIDATION.unique_string_list(ids, allow_empty=True):
        raise ValueError(f"{path.name}: video_ids must be a unique string array")
    if set(ids) - catalog_ids:
        raise ValueError(f"{path.name}: unknown video ids: {sorted(set(ids) - catalog_ids)}")
    return set(ids)


def load_ledger_term_ids(path: Path) -> set[str]:
    ledger = read_json(path)
    if not isinstance(ledger, dict) or ledger.get("schema_version") != "design-terminology-v1" or not isinstance(ledger.get("terms"), list):
        raise ValueError("ledger must be a design-terminology-v1 object with terms")
    ids: set[str] = set()
    seen: set[str] = set()
    for term in ledger["terms"]:
        if (
            not isinstance(term, dict) or not isinstance(term.get("id"), str)
            or not VALIDATION.TERM_ID_RE.fullmatch(term["id"])
            or not VALIDATION.choice(term.get("status"), {"candidate", "adopted", "held", "rejected"})
        ):
            raise ValueError("ledger terms must contain valid ids and statuses")
        if term["id"] in seen:
            raise ValueError(f"duplicate ledger term: {term['id']}")
        seen.add(term["id"])
        if term["status"] != "rejected":
            ids.add(term["id"])
    return ids


def compute_reliability(
    catalog, pilot_payload, production_payload, pilot_ids, sample_ids
) -> tuple[Any, Any, dict[str, Any]]:
    """Recompute pre-consensus agreement without reading or writing files."""
    all_ids = {video["video_id"] for video in catalog["videos"]}
    analyzed = {video["video_id"] for video in catalog["videos"] if video["status"] == "analyzed"}
    reliability = {
        "pilot_sample_size": None, "pilot_kappa": None, "pilot_evidence": [],
        "production_double_coded_ratio": None, "production_kappa": None,
        "production_evidence": [],
    }
    outputs = []
    for phase, original, eligible, population in (
        ("pilot", pilot_payload, all_ids & set(pilot_ids), len(all_ids)),
        ("production", production_payload, analyzed & set(sample_ids), len(analyzed)),
    ):
        if original is None:
            outputs.append(None)
            continue
        if not isinstance(original, dict) or set(original) != VALIDATION.CODER_EVIDENCE_FIELDS:
            raise ValueError(f"{phase} coder evidence must contain exact schema fields")
        if original.get("schema_version") != "madia-coder-evidence-v1" or original.get("phase") != phase or original.get("coders") != ["coder-a", "coder-b"]:
            raise ValueError(f"{phase} coder evidence has invalid schema, phase or coders")
        if not isinstance(original.get("records"), list):
            raise ValueError(f"{phase} coder evidence records must be an array")
        payload = copy.deepcopy(original)
        records = []
        seen = set()
        for record in payload["records"]:
            if not isinstance(record, dict) or set(record) != VALIDATION.CODER_RECORD_FIELDS or not VALIDATION.non_empty_string(record.get("unit_id")):
                raise ValueError(f"{phase} coder evidence record must contain unit_id and ratings")
            video_id = record["unit_id"]
            if video_id in seen:
                raise ValueError(f"{video_id}: duplicate coder evidence record")
            seen.add(video_id)
            ratings = record["ratings"]
            if not isinstance(ratings, dict) or set(ratings) != VALIDATION.CODER_DIMENSIONS:
                raise ValueError(f"{video_id}: coder evidence ratings must contain exact dimensions")
            for dimension, allowed in VALIDATION.RATING_CODES.items():
                values = ratings[dimension]
                if not isinstance(values, dict) or set(values) != {"coder-a", "coder-b"} or not all(VALIDATION.choice(value, allowed) for value in values.values()):
                    raise ValueError(f"{video_id}: invalid coder evidence ratings for {dimension}")
            if video_id in eligible:
                records.append(record)
        payload["records"] = records
        payload["population_size"] = population
        outputs.append(payload)
        if not records:
            continue
        kappas = [
            VALIDATION.cohen_kappa(
                [record["ratings"][dimension]["coder-a"] for record in records],
                [record["ratings"][dimension]["coder-b"] for record in records],
            )
            for dimension in sorted(VALIDATION.CODER_DIMENSIONS)
        ]
        reliability[f"{phase}_kappa"] = None if None in kappas else min(kappas)
        reliability[f"{phase}_evidence"] = [f"madia-evidence/{EVIDENCE_FILES[phase]}"]
        if phase == "pilot":
            reliability["pilot_sample_size"] = len(records)
        else:
            reliability["production_double_coded_ratio"] = len(records) / population
    return outputs[0], outputs[1], reliability


def reliability_inputs(catalog):
    directory = CATALOG.parent / "madia-evidence"
    ids = {video["video_id"] for video in catalog["videos"]}
    pilot_ids = selection_ids(directory / "pilot-selection.json", "pilot", ids)
    sample_path = directory / "production-sample.json"
    sample_ids = selection_ids(sample_path, "production", ids)
    payloads = [
        read_json(directory / filename) if (directory / filename).exists() else None
        for filename in EVIDENCE_FILES.values()
    ]
    return pilot_ids, sample_ids, sample_path.exists(), payloads[0], payloads[1]


def publish_with_reliability(catalog, pilot_payload, production_payload, pilot_ids, sample_ids):
    counts, coverage = status_counts(catalog["videos"])
    catalog["inventory"].update(
        discovered_unique_videos=len(catalog["videos"]), corpus_coverage=coverage, **counts
    )
    pilot_payload, production_payload, reliability = compute_reliability(
        catalog, pilot_payload, production_payload, pilot_ids, sample_ids
    )
    catalog["reliability"] = reliability
    directory = CATALOG.parent / "madia-evidence"
    writes = {
        directory / EVIDENCE_FILES[phase]: payload
        for phase, payload in (("pilot", pilot_payload), ("production", production_payload))
        if payload is not None
    }
    previous = {path: path.read_bytes() if path.exists() else None for path in writes}
    directory_existed = directory.exists()
    try:
        for path, payload in writes.items():
            atomic_write(path, json.dumps(payload, ensure_ascii=False, indent=2) + "\n")
        publish_catalog(catalog)
    except Exception:
        for path, content in previous.items():
            if content is None:
                path.unlink(missing_ok=True)
            else:
                atomic_write(path, content)
        if not directory_existed and directory.exists() and not any(directory.iterdir()):
            directory.rmdir()
        raise


def referenced_video_ids(catalog) -> set[str]:
    occurrences = {
        occurrence for principle in catalog["principles"]
        for occurrence in principle["occurrence_ids"]
    }
    return {
        video["video_id"] for video in catalog["videos"]
        if any(unit["id"] in occurrences for unit in video["evidence_units"])
    }


def merge_analysis(
    catalog, directories, *, pilot, ledger_term_ids, pilot_ids, sample_ids,
    production_sample_exists, pilot_payload, production_payload,
):
    result = copy.deepcopy(catalog)
    payloads = {"pilot": copy.deepcopy(pilot_payload), "production": copy.deepcopy(production_payload)}
    videos = {video["video_id"]: video for video in result["videos"]}
    referenced = referenced_video_ids(result)
    seen = set()
    for directory in directories:
        directory = Path(directory)
        video_id = directory.name
        try:
            fetch = read_json(directory / "fetch.json")
            if not isinstance(fetch, dict):
                raise ValueError("fetch.json must be an object")
            if not isinstance(fetch.get("video_id"), str) or not VIDEO_ID_RE.fullmatch(fetch["video_id"]):
                raise ValueError("fetch.json video_id must be an 11-character YouTube video id")
            video_id = fetch["video_id"]
            if video_id not in videos:
                raise ValueError("video is not in catalog")
            if video_id in seen:
                raise ValueError("video appears in multiple merge directories")
            seen.add(video_id)
            if video_id in referenced:
                raise ValueError("video referenced by principles cannot be re-merged")
            video = videos[video_id]
            if fetch.get("status") == "blocked":
                if not VALIDATION.non_empty_string(fetch.get("reason")):
                    raise ValueError("blocked fetch requires a reason")
                video.update(
                    status="blocked", blocking_reason=fetch["reason"], evidence_units=[],
                    analysis_receipt=None, exclusion_reason=None, duplicate_of=None,
                )
                for payload in payloads.values():
                    if payload is not None:
                        payload["records"] = [record for record in payload["records"] if record["unit_id"] != video_id]
                continue
            if fetch.get("status") != "ok":
                raise ValueError("fetch.json status must be ok or blocked")
            if pilot and not (CATALOG.parent / "madia-evidence" / "pilot-selection.json").exists():
                raise ValueError("pilot-selection.json is required with --pilot")
            if pilot and video_id not in pilot_ids:
                raise ValueError("not a pilot video")
            if not pilot and video_id in pilot_ids:
                raise ValueError("pilot video must be merged with --pilot")
            bundles = {}
            for role in ("coder-a", "coder-b", "adjudicator"):
                path = directory / f"analysis-{role}.json"
                if path.exists():
                    bundle = read_json(path)
                    errors = VALIDATION.validate_analysis_bundle(bundle, ledger_term_ids)
                    if errors:
                        raise ValueError("\n".join(errors))
                    if bundle["video_id"] != video_id or bundle["coder"] != role:
                        raise ValueError(f"{path.name} must match video_id and coder role")
                    bundles[role] = bundle
            if "coder-b" in bundles and "adjudicator" not in bundles:
                raise ValueError("double-coded video requires adjudication")
            if "coder-a" not in bundles:
                raise ValueError("analysis-coder-a.json is required")
            if pilot and not {"coder-b", "adjudicator"} <= set(bundles):
                raise ValueError("pilot video requires coder-b and adjudicator")
            if "adjudicator" in bundles and "coder-b" not in bundles:
                raise ValueError("adjudication requires coder-b")
            final = bundles.get("adjudicator", bundles["coder-a"])
            verification = read_json(directory / "verification.json")
            sessions = [bundle["session_id"] for bundle in bundles.values()]
            if isinstance(verification, dict) and VALIDATION.non_empty_string(verification.get("verifier")):
                sessions.append(verification["verifier"])
            if len(sessions) != len(set(sessions)):
                raise ValueError("roles must use distinct sessions")
            errors = VALIDATION.validate_verification(verification, final, ledger_term_ids)
            if errors:
                raise ValueError("\n".join(errors))
            if final["caption_source"] != fetch.get("caption_source"):
                raise ValueError("bundle caption_source must match fetch.json")
            if final["proposed_status"] == "excluded" and verification["exclusion_confirmed"] is not True:
                raise ValueError("exclusion not confirmed by verifier")
            checks = {item["unit_id"]: item for item in verification["units"]}
            units = []
            for original in final["evidence_units"]:
                item = checks[original["id"]]
                if item["status"] == "rejected":
                    continue
                unit = copy.deepcopy(original)
                unit.update(copy.deepcopy(item["corrections"]))
                unit["source_locator"] = f"https://www.youtube.com/watch?v={video_id}&t={int(unit['timestamp_start'])}s"
                unit["verification"] = {
                    "status": item["status"], "verifier": verification["verifier"],
                    "checks": item["checks"], "note": item["note"],
                }
                unit["principle_candidate_ids"] = []
                units.append(unit)
            if any(unit["speech_excerpt"] is not None for unit in units):
                cues = read_json(directory / "cues.json")
                if not isinstance(cues, list) or not all(
                    isinstance(cue, dict) and VALIDATION.finite_number(cue.get("start"))
                    and VALIDATION.finite_number(cue.get("end")) and 0 <= cue["start"] <= cue["end"]
                    and isinstance(cue.get("text"), str) for cue in cues
                ):
                    raise ValueError("cues.json must contain valid start, end and text records")
                for unit in units:
                    if unit["speech_excerpt"] is None:
                        continue
                    text = "".join(
                        cue["text"] for cue in cues
                        if cue["end"] >= unit["timestamp_start"] - 2
                        and cue["start"] <= unit["timestamp_end"] + 2
                    )
                    if re.sub(r"\s", "", unit["speech_excerpt"]) not in re.sub(r"\s", "", text):
                        raise ValueError(f"speech_excerpt not found in cues: {unit['id']}")
            receipt = {
                key: final[key] for key in ("codebook_version", "caption_source", "sheets_total", "sheets_viewed")
            }
            receipt.update(
                coders=list(bundles),
                sessions={**{role: bundle["session_id"] for role, bundle in bundles.items()}, "verifier": verification["verifier"]},
            )
            video.update(
                status="analyzed" if units else "excluded",
                exclusion_reason=None if units else (
                    final["reason"] if final["proposed_status"] == "excluded"
                    else "no_design_judgment: 검증에서 모든 근거 단위가 기각됨"
                ),
                blocking_reason=None, duplicate_of=None, analysis_receipt=receipt,
                evidence_units=sorted(units, key=lambda unit: unit["timestamp_start"]),
            )
            phase = "pilot" if pilot else "production"
            if not pilot and "coder-b" in bundles and not production_sample_exists:
                raise ValueError("production-sample.json is required for non-pilot double coding")
            payload = payloads[phase]
            if payload is not None:
                payload["records"] = [record for record in payload["records"] if record["unit_id"] != video_id]
            if "coder-b" in bundles and (pilot or video_id in sample_ids):
                if payload is None:
                    payload = {
                        "schema_version": "madia-coder-evidence-v1", "phase": phase,
                        "coders": ["coder-a", "coder-b"], "population_size": 0, "records": [],
                    }
                    payloads[phase] = payload
                payload["records"].append({
                    "unit_id": video_id,
                    "ratings": {
                        dimension: {role: bundles[role]["ratings"][dimension] for role in ("coder-a", "coder-b")}
                        for dimension in sorted(VALIDATION.CODER_DIMENSIONS)
                    },
                })
        except (OSError, ValueError, TypeError, KeyError, IndexError, AttributeError, OverflowError) as error:
            raise ValueError("\n".join(f"{video_id}: {line}" for line in str(error).splitlines())) from error
    return result, payloads["pilot"], payloads["production"]


def apply_curation(catalog, payload, ledger_term_ids, pilot_ids):
    fields = {"schema_version", "mark_duplicates", "project_links", "principles", "term_assignments", "term_rewrites", "quality_gates"}
    if not isinstance(payload, dict) or payload.get("schema_version") != "madia-curation-v1":
        raise ValueError("curation.schema_version must be madia-curation-v1")
    unknown = set(payload) - fields
    if unknown:
        raise ValueError(f"curation has unknown fields: {sorted(unknown)}")
    for field in fields - {"schema_version", "principles", "quality_gates"}:
        if field in payload and not isinstance(payload[field], dict):
            raise ValueError(f"curation.{field} must be an object")
    result = copy.deepcopy(catalog)
    videos = {video["video_id"]: video for video in result["videos"]}
    referenced = referenced_video_ids(result)
    for video_id, duplicate in payload.get("mark_duplicates", {}).items():
        if video_id not in videos:
            raise ValueError(f"{video_id}: unknown video for mark_duplicates")
        if video_id in referenced:
            raise ValueError(f"{video_id}: video referenced by principles cannot be marked duplicate")
        if video_id in pilot_ids:
            raise ValueError(f"{video_id}: pilot video cannot be marked duplicate")
        if not isinstance(duplicate, dict) or set(duplicate) != {"duplicate_of", "reason"}:
            raise ValueError(f"{video_id}: duplicate must contain duplicate_of and reason")
        target, reason = duplicate["duplicate_of"], duplicate["reason"]
        if not isinstance(target, str) or target not in videos or target == video_id:
            raise ValueError(f"{video_id}: duplicate_of must reference another catalog video")
        if not isinstance(reason, str) or not reason.startswith("duplicate: ") or not reason[len("duplicate: "):].strip():
            raise ValueError(f"{video_id}: duplicate reason must start with duplicate: and contain a reason")
        videos[video_id].update(
            status="excluded", exclusion_reason=reason, duplicate_of=target,
            evidence_units=[], analysis_receipt=None, blocking_reason=None,
        )
    units = {
        unit["id"]: unit for video in result["videos"] for unit in video["evidence_units"]
    }
    unit_videos = {
        unit["id"]: video["video_id"] for video in result["videos"] for unit in video["evidence_units"]
    }
    links = payload.get("project_links", {})
    for old, new in links.items():
        if not VALIDATION.non_empty_string(old) or not isinstance(new, str) or not re.fullmatch(r"madia-proj-[a-z0-9]+(?:-[a-z0-9]+)*", new):
            raise ValueError(f"project_links must map project ids to madia-proj-<kebab>: {old}")
    for unit in units.values():
        unit["project_id"] = links.get(unit["project_id"], unit["project_id"])
    for unit_id, terms in payload.get("term_assignments", {}).items():
        video_id = unit_videos.get(unit_id, unit_id.split(":", 1)[0])
        if unit_id not in units:
            raise ValueError(f"{video_id}: unknown unit for term_assignments: {unit_id}")
        if not isinstance(terms, list) or not all(isinstance(term, str) for term in terms):
            raise ValueError(f"{video_id}: term_assignments must contain term id arrays: {unit_id}")
        if set(terms) - ledger_term_ids:
            raise ValueError(f"{video_id}: term_assignments must reference non-rejected ledger terms: {unit_id}")
        units[unit_id]["term_ids"] = sorted(set(terms))
    rewrites = payload.get("term_rewrites", {})
    for old, new in rewrites.items():
        if not VALIDATION.TERM_ID_RE.fullmatch(old) or (new is not None and (not isinstance(new, str) or new not in ledger_term_ids)):
            raise ValueError(f"term_rewrites must map term ids to non-rejected ledger terms or null: {old}")
    if "term_rewrites" in payload:
        for item in list(units.values()) + result["principles"]:
            item["term_ids"] = sorted({
                rewrites.get(term, term) for term in item["term_ids"]
                if rewrites.get(term, term) is not None
            })
    if "principles" in payload:
        principles = payload["principles"]
        if not isinstance(principles, list):
            raise ValueError("curation.principles must be an array")
        result["principles"] = copy.deepcopy(principles)
        for unit in units.values():
            unit["principle_candidate_ids"] = []
        for principle in result["principles"]:
            if not isinstance(principle, dict):
                raise ValueError("curation.principles entries must be objects")
            if "independent_projects" in principle:
                raise ValueError("curation principles must not supply independent_projects")
            if not VALIDATION.non_empty_string(principle.get("id")) or not VALIDATION.unique_string_list(principle.get("occurrence_ids")):
                raise ValueError("curation principles require id and unique non-empty occurrence_ids")
            principle_id = principle["id"]
            unknown = set(principle["occurrence_ids"]) - set(units)
            if unknown:
                raise ValueError(f"principle references unknown occurrence ids: {principle_id}: {sorted(unknown)}")
            for unit_id in principle["occurrence_ids"]:
                units[unit_id]["principle_candidate_ids"].append(principle_id)
    # Project linking can change the derived count even without replacing principles.
    for principle in result["principles"]:
        direct = {
            units[unit_id]["project_id"] for unit_id in principle["occurrence_ids"]
            if unit_id in units and units[unit_id]["evidence_kind"] in {"verbalized", "demonstrated"}
            and units[unit_id]["verification"]["status"] in {"confirmed", "corrected"}
        }
        if not direct:
            raise ValueError(f"principle has no verified direct occurrence: {principle['id']}")
        principle["independent_projects"] = len(direct)
        if principle.get("tier") == "P3":
            fixture = principle.get("behavior_fixture")
            evidence = fixture.get("evidence") if isinstance(fixture, dict) else None
            if not isinstance(evidence, list) or not evidence:
                raise ValueError(f"P3 principle requires behavior receipt: {principle['id']}")
            errors: list[str] = []
            path = VALIDATION.resolve_catalog_file(evidence[0], "behavior_fixture.evidence[0]", CATALOG.parent, errors)
            if path is None:
                raise ValueError("\n".join(errors))
            receipt = read_json(path)
            text = {field: principle.get(field) for field in ("label", "trigger", "inspect", "decide", "act", "verify", "exceptions")}
            digest = hashlib.sha256(json.dumps(text, ensure_ascii=False, sort_keys=True).encode("utf-8")).hexdigest()
            if not isinstance(receipt, dict) or receipt.get("principle_sha256") != digest:
                raise ValueError(f"principle text changed after behavior run: {principle['id']}")
    if "quality_gates" in payload:
        gates = payload["quality_gates"]
        if not isinstance(gates, list) or len(gates) != 9:
            raise ValueError("curation.quality_gates must contain all nine gates")
        result["quality_gates"] = copy.deepcopy(gates)
    errors = []
    for video in result["videos"]:
        for unit in video["evidence_units"]:
            VALIDATION.validate_ledger_terms(unit, ledger_term_ids, f"{video['video_id']}: {unit['id']}", errors)
    for principle in result["principles"]:
        VALIDATION.validate_ledger_terms(principle, ledger_term_ids, f"principle {principle['id']}", errors)
    if errors:
        raise ValueError("\n".join(errors))
    return result


def main() -> int:
    global CATALOG, SUMMARY
    parser = argparse.ArgumentParser(description=__doc__)
    modes = parser.add_mutually_exclusive_group()
    modes.add_argument("--check", action="store_true", help="validate the committed snapshot without network access")
    modes.add_argument("--normalize", action="store_true", help="migrate schema and recompute inventory without discovery")
    modes.add_argument("--merge-analysis", type=Path, nargs="+", metavar="DIR", help="merge verified analysis directories")
    modes.add_argument("--apply-curation", type=Path, metavar="PATH", help="apply a curation bundle")
    parser.add_argument("--pilot", action="store_true", help="merge pilot coding results")
    parser.add_argument("--ledger", type=Path, default=ROOT / "docs/research/design-terminology.json")
    parser.add_argument("--catalog", type=Path, default=CATALOG)
    parser.add_argument("--as-of", default=date.today().isoformat())
    args = parser.parse_args()
    if args.pilot and args.merge_analysis is None:
        parser.error("--pilot requires --merge-analysis")
    CATALOG = args.catalog.resolve()
    SUMMARY = CATALOG.with_suffix(".md")
    try:
        if args.check:
            validate(CATALOG)
            catalog = json.loads(CATALOG.read_text(encoding="utf-8"))
            expected = render_summary(catalog)
            if not SUMMARY.exists() or SUMMARY.read_text(encoding="utf-8") != expected:
                print(f"stale: {SUMMARY}")
                return 1
            print("OK: Madia catalog snapshot and summary")
            return 0
        if args.normalize or args.merge_analysis is not None or args.apply_curation is not None:
            existing = load_existing()
            if existing is None:
                raise ValueError(f"catalog does not exist: {CATALOG}")
            if not isinstance(existing, dict):
                raise ValueError("catalog must be a JSON object")
            catalog = normalize_catalog(existing) if args.normalize else existing
            pilot_ids, sample_ids, sample_exists, pilot_payload, production_payload = reliability_inputs(catalog)
            # Check evidence structure before a merge can replace existing records.
            compute_reliability(catalog, pilot_payload, production_payload, pilot_ids, sample_ids)
            if args.merge_analysis is not None:
                catalog, pilot_payload, production_payload = merge_analysis(
                    catalog, args.merge_analysis, pilot=args.pilot,
                    ledger_term_ids=load_ledger_term_ids(args.ledger),
                    pilot_ids=pilot_ids, sample_ids=sample_ids,
                    production_sample_exists=sample_exists,
                    pilot_payload=pilot_payload, production_payload=production_payload,
                )
            elif args.apply_curation is not None:
                catalog = apply_curation(
                    catalog, read_json(args.apply_curation),
                    load_ledger_term_ids(args.ledger), pilot_ids,
                )
            publish_with_reliability(catalog, pilot_payload, production_payload, pilot_ids, sample_ids)
        else:
            catalog = build_catalog(args.as_of)
            publish_catalog(catalog)
        print(
            f"updated: {CATALOG} "
            f"({catalog['inventory']['discovered_unique_videos']} videos, "
            f"{catalog['inventory']['pending']} pending)"
        )
        return 0
    except (OSError, ValueError, RecursionError, TypeError, KeyError, IndexError, AttributeError, OverflowError, ET.ParseError) as error:
        print(f"ERROR: {error}")
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
