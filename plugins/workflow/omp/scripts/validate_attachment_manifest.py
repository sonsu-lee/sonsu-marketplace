#!/usr/bin/env python3
"""PR 첨부 manifest와 로컬 파일을 읽기 전용으로 검사해 JSON으로 출력한다.

upload, 파일 수정, decoder 실행을 하지 않고 내용·민감정보·metadata 안전성을 판정하지 않는다.
사용법: --manifest FILE --phase pre-create|pre-upload [--attachment-order N]
        [--video-plan unknown|free|paid] [--paid-video-eligible]
출력: schema_version, phase, status, errors, checked_files, manual_checks
종료 코드: 0 로컬 판정 통과(manual_checks는 별도 수행), 1 manifest·파일·기록 상태 차단, 2 입력·CLI 오류.
입력 schema: skills/to-pr/references/media-attachments.md#manifest를-검사한다
"""

import argparse
import hashlib
import json
import math
import os
from pathlib import Path
import re
import stat
import sys
from urllib.parse import urlsplit


FORMATS = {
    ".png": ("image", "image/png"),
    ".jpg": ("image", "image/jpeg"),
    ".jpeg": ("image", "image/jpeg"),
    ".gif": ("image", "image/gif"),
    ".webp": ("image", "image/webp"),
    ".svg": ("image", "image/svg+xml"),
    ".mp4": ("video", "video/mp4"),
    ".mov": ("video", "video/quicktime"),
    ".webm": ("video", "video/webm"),
}
OPERATION_FIELDS = ("repository", "base", "head", "head_ref_oid", "pr_url", "target_pr_state", "attachments")
ATTACHMENT_FIELDS = (
    "source_path", "local_path", "kind", "purpose", "body_section", "display_order",
    "required_for_ready", "alt_text_or_caption", "mime_type", "file_size", "width", "height",
    "duration", "codec", "sha256", "annotation_status", "annotation_method",
    "sensitive_data_check", "embedded_metadata_check", "upload_status", "body_status",
    "provider", "remote_url", "deletion_locator",
)
MANUAL_CHECKS = [
    "trusted decoder: actual content type, extension agreement, decoding and playback",
    "human/model: annotation, caption timestamps, full content/audio privacy and embedded metadata",
    "operator: publish authorization, safe staging location, CLI/host/token/plan/visibility support",
    "remote readback: exact new Draft PR, repository/base/head/headRefOid, upload and body rendering",
]


def text(value):
    return isinstance(value, str) and bool(value.strip())


def positive_integer(value):
    return type(value) is int and value > 0


def positive_number(value):
    return positive_integer(value) or (type(value) is float and value > 0 and math.isfinite(value))


def https_url(value):
    if not text(value) or any(character.isspace() or ord(character) < 32 for character in value):
        return False
    try:
        parsed = urlsplit(value)
        return parsed.scheme == "https" and bool(parsed.hostname) and not parsed.username and not parsed.password
    except ValueError:
        return False


def matching_pr_url(value, repository):
    if not https_url(value) or not isinstance(repository, str):
        return False
    parsed = urlsplit(value)
    return not parsed.query and not parsed.fragment and re.fullmatch(
        "/" + re.escape(repository) + r"/pull/[1-9][0-9]*/?", parsed.path
    ) is not None


def fingerprint(info):
    return (info.st_dev, info.st_ino, info.st_size, info.st_mtime_ns, info.st_ctime_ns)


class Validator:
    def __init__(self, args):
        self.args = args
        self.errors = []
        self.checked_files = []

    def error(self, field, code, message):
        self.errors.append({"field": field, "code": code, "message": message})

    def require(self, value, field, predicate, description):
        if not predicate(value):
            self.error(field, "invalid-field", description)

    def fields(self, value, fields, prefix):
        for field in fields:
            if field not in value:
                self.error(prefix + field, "missing-field", "required field is absent")

    def attachment_schema(self, item, prefix):
        self.fields(item, ATTACHMENT_FIELDS, prefix)
        for name in ("source_path", "local_path", "purpose", "body_section", "alt_text_or_caption"):
            self.require(item.get(name), prefix + name, text, "expected a nonempty string")
        for name in ("source_path", "local_path"):
            value = item.get(name)
            if text(value) and (not Path(value).is_absolute() or any(ord(c) < 32 or 127 <= ord(c) <= 159 for c in value)):
                self.error(prefix + name, "unsafe-path", "expected an absolute path without control characters")
        for name in ("display_order", "file_size", "width", "height"):
            self.require(item.get(name), prefix + name, positive_integer, "expected a positive integer, not a boolean")
        self.require(item.get("required_for_ready"), prefix + "required_for_ready", lambda v: type(v) is bool,
                     "expected a boolean")
        self.require(item.get("sha256"), prefix + "sha256",
                     lambda v: isinstance(v, str) and re.fullmatch(r"[0-9a-fA-F]{64}", v) is not None,
                     "expected a 64-digit hexadecimal SHA-256")
        enums = {
            "kind": ("image", "video"),
            "annotation_status": ("not_checked", "verified", "failed", "inconclusive"),
            "sensitive_data_check": ("not_checked", "passed", "failed", "inconclusive"),
            "embedded_metadata_check": ("not_checked", "passed", "failed", "inconclusive"),
            "upload_status": ("not_started", "uploaded", "failed", "not_attempted", "unknown"),
            "body_status": ("not_checked", "verified", "missing", "wrong_render", "unknown"),
        }
        for name, allowed in enums.items():
            self.require(item.get(name), prefix + name, lambda v, allowed=allowed: v in allowed,
                         "expected one of: " + ", ".join(allowed))
        for name in ("annotation_method", "provider", "deletion_locator"):
            self.require(item.get(name), prefix + name, lambda v: v is None or text(v),
                         "expected null or a nonempty string")
        self.require(item.get("remote_url"), prefix + "remote_url", lambda v: v is None or https_url(v),
                     "expected null or an HTTPS URL")
        if item.get("kind") == "video":
            self.require(item.get("duration"), prefix + "duration", positive_number, "expected finite positive seconds")
            self.require(item.get("codec"), prefix + "codec", text, "expected the decoder-reported codec")
        else:
            self.require(item.get("duration"), prefix + "duration", lambda v: v is None or positive_number(v),
                         "expected null or finite positive seconds (animated image)")
            self.require(item.get("codec"), prefix + "codec", lambda v: v is None or text(v),
                         "expected null or a nonempty string")
        path = item.get("local_path")
        if text(path):
            if "#" in Path(path).name:
                self.error(prefix + "local_path", "unsafe-basename", "final basename cannot contain #")
            expected = FORMATS.get(Path(path).suffix.lower())
            if expected is None:
                self.error(prefix + "local_path", "unsupported-extension", "extension is not supported")
            elif (item.get("kind"), item.get("mime_type")) != expected:
                self.error(prefix + "mime_type", "format-mismatch", "kind and declared MIME must match extension")

    def recorded_checks(self, item, prefix):
        for name, expected in (("annotation_status", "verified"), ("sensitive_data_check", "passed"),
                               ("embedded_metadata_check", "passed")):
            if item.get(name) != expected:
                self.error(prefix + name, "review-incomplete", "required recorded review state: " + expected)
        if not text(item.get("annotation_method")):
            self.error(prefix + "annotation_method", "review-incomplete", "record the image marking or video caption method")

    def inspect_file(self, item, prefix, identities, hash_file):
        path_value = item.get("local_path")
        if not text(path_value) or not Path(path_value).is_absolute() or "\x00" in path_value:
            return
        path = Path(path_value)
        try:
            info = path.stat()  # Follow symbolic links; device/inode also detects hard links.
            if not stat.S_ISREG(info.st_mode):
                self.error(prefix + "local_path", "not-regular-file", "expected an existing regular file")
                return
            identity = (info.st_dev, info.st_ino)
            if identity in identities:
                self.error(prefix + "local_path", "duplicate-file", "same underlying file as " + identities[identity])
            else:
                identities[identity] = prefix + "local_path"
            limit = 10 * 1024**2
            if item.get("kind") == "video":
                limit = min(100 * 1024**2, 100_000_000 if self.args.video_plan == "paid" and self.args.paid_video_eligible else 10_000_000)
            if info.st_size == 0:
                self.error(prefix + "file_size", "empty-file", "empty attachments are not allowed")
            if info.st_size > limit:
                self.error(prefix + "file_size", "size-limit", f"file exceeds {limit} bytes")
            if info.st_size != item.get("file_size"):
                self.error(prefix + "file_size", "size-mismatch", "actual size differs from manifest")
            record = {"field": prefix + "local_path", "display_order": item.get("display_order"),
                      "realpath": str(path.resolve()), "device": info.st_dev, "inode": info.st_ino,
                      "file_size": info.st_size, "limit_bytes": limit, "sha256": None}
            self.checked_files.append(record)
            if not hash_file or info.st_size > limit or info.st_size == 0:
                return
            # Nonblocking open avoids hanging if a file is replaced with a FIFO after stat.
            fd = os.open(path, os.O_RDONLY | os.O_NONBLOCK)
            with os.fdopen(fd, "rb") as stream:
                before = os.fstat(stream.fileno())
                if not stat.S_ISREG(before.st_mode) or fingerprint(before) != fingerprint(info):
                    self.error(prefix + "local_path", "file-changed", "file changed before hashing")
                    return
                digest = hashlib.sha256()
                remaining = info.st_size
                while remaining:
                    chunk = stream.read(min(1024 * 1024, remaining))
                    if not chunk:
                        break
                    digest.update(chunk)
                    remaining -= len(chunk)
                if remaining or fingerprint(os.fstat(stream.fileno())) != fingerprint(info) or fingerprint(path.stat()) != fingerprint(info):
                    self.error(prefix + "local_path", "file-changed", "file changed while hashing")
                    return
            record["sha256"] = digest.hexdigest()
            expected = item.get("sha256")
            if not isinstance(expected, str) or record["sha256"] != expected.lower():
                self.error(prefix + "sha256", "sha256-mismatch", "actual SHA-256 differs from manifest")
        except (OSError, ValueError, RuntimeError) as error:
            self.error(prefix + "local_path", "file-unreadable", str(error))

    def validate(self, manifest):
        if not isinstance(manifest, dict):
            self.error("manifest", "invalid-field", "expected an object")
            return
        self.fields(manifest, OPERATION_FIELDS, "")
        for name in ("repository", "base", "head"):
            self.require(manifest.get(name), name, text, "expected a nonempty string")
        repository = manifest.get("repository")
        self.require(repository, "repository", lambda v: isinstance(v, str) and re.fullmatch(r"[^/\s]+/[^/\s]+", v) is not None,
                     "expected owner/repository")
        self.require(manifest.get("head_ref_oid"), "head_ref_oid",
                     lambda v: isinstance(v, str) and re.fullmatch(r"(?:[0-9a-fA-F]{40}|[0-9a-fA-F]{64})", v) is not None,
                     "expected a full 40- or 64-digit Git object ID")
        self.require(manifest.get("target_pr_state"), "target_pr_state", lambda v: v in ("draft", "ready"),
                     "expected draft or ready")
        pr_url = manifest.get("pr_url")
        if self.args.phase == "pre-create":
            self.require(pr_url, "pr_url", lambda v: v is None, "pre-create requires null; never edit a pre-existing PR")
        elif not matching_pr_url(pr_url, repository):
            self.error("pr_url", "invalid-field", "pre-upload requires an HTTPS PR URL matching repository")
        attachments = manifest.get("attachments")
        if not isinstance(attachments, list) or not attachments:
            self.error("attachments", "invalid-field", "expected a nonempty array")
            return
        orders = set()
        identities = {}
        selected = False
        for index, item in enumerate(attachments):
            prefix = f"attachments[{index}]."
            if not isinstance(item, dict):
                self.error(prefix[:-1], "invalid-field", "expected an object")
                continue
            self.attachment_schema(item, prefix)
            order = item.get("display_order")
            if positive_integer(order):
                if order in orders:
                    self.error(prefix + "display_order", "duplicate-order", "display_order must be unique")
                orders.add(order)
            is_selected = self.args.phase == "pre-upload" and order == self.args.attachment_order
            selected = selected or is_selected
            if (self.args.phase == "pre-create" and item.get("required_for_ready") is True) or is_selected:
                self.recorded_checks(item, prefix)
            if self.args.phase == "pre-create":
                if item.get("upload_status") != "not_started" or item.get("body_status") != "not_checked" or item.get("remote_url") is not None or item.get("deletion_locator") is not None:
                    self.error(prefix + "upload_status", "not-fresh", "new publish requires untouched upload/body state and null remote locators")
            elif is_selected and item.get("upload_status") != "not_started":
                self.error(prefix + "upload_status", "not-next-upload", "only not_started files may enter the normal upload sequence")
            self.inspect_file(item, prefix, identities, self.args.phase == "pre-create" or is_selected)
        if self.args.phase == "pre-upload" and not selected:
            self.error("attachment_order", "attachment-not-found", "no attachment has the requested display_order")
        elif self.args.phase == "pre-upload":
            self.upload_sequence(attachments)

    def upload_sequence(self, attachments):
        """Required files go first, then display_order; every earlier file must be confirmed uploaded."""
        items = [item for item in attachments if isinstance(item, dict) and positive_integer(item.get("display_order"))
                 and type(item.get("required_for_ready")) is bool]
        items.sort(key=lambda item: (not item["required_for_ready"], item["display_order"]))
        for item in items:
            if item["display_order"] == self.args.attachment_order:
                return
            if item.get("upload_status") != "uploaded":
                self.error("attachment_order", "out-of-sequence",
                           f"display_order {item['display_order']} must be uploaded first")


def unique_object(pairs):
    result = {}
    for key, value in pairs:
        if key in result:
            raise ValueError("duplicate JSON key: " + key)
        result[key] = value
    return result


def reject_constant(value):
    raise ValueError("non-finite JSON number: " + value)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--manifest", type=Path, required=True)
    parser.add_argument("--phase", choices=("pre-create", "pre-upload"), required=True)
    parser.add_argument("--attachment-order", type=int)
    parser.add_argument("--video-plan", choices=("unknown", "free", "paid"), default="unknown")
    parser.add_argument("--paid-video-eligible", action="store_true", help="operator verified paid-plan large-video eligibility")
    args = parser.parse_args()
    if (args.phase == "pre-upload") != (args.attachment_order is not None):
        parser.error("--attachment-order is required only for pre-upload")
    if args.attachment_order is not None and args.attachment_order <= 0:
        parser.error("--attachment-order must be positive")
    if args.paid_video_eligible and args.video_plan != "paid":
        parser.error("--paid-video-eligible requires --video-plan paid")
    validator = Validator(args)
    try:
        with args.manifest.open(encoding="utf-8") as stream:
            manifest = json.load(stream, object_pairs_hook=unique_object, parse_constant=reject_constant)
    except (OSError, ValueError, RecursionError) as error:
        validator.error("manifest", "input-error", str(error))
        code = 2
    else:
        validator.validate(manifest)
        code = 1 if validator.errors else 0
    print(json.dumps({"schema_version": 1, "phase": args.phase,
                      "status": "passed" if code == 0 else "input-error" if code == 2 else "blocked",
                      "errors": validator.errors, "checked_files": validator.checked_files,
                      "manual_checks": MANUAL_CHECKS}, ensure_ascii=False, indent=2))
    return code


if __name__ == "__main__":
    raise SystemExit(main())
