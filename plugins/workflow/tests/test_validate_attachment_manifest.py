"""Attachment gates use real temporary files; arbitrary bytes do not imply decoding."""

import copy
import hashlib
import json
import os
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest


SCRIPT = Path(__file__).resolve().parents[1] / "scripts/validate_attachment_manifest.py"
OPERATION_FIELDS = ("repository", "base", "head", "head_ref_oid", "pr_url", "target_pr_state", "attachments")
ATTACHMENT_FIELDS = (
    "source_path", "local_path", "kind", "purpose", "body_section", "display_order",
    "required_for_ready", "alt_text_or_caption", "mime_type", "file_size", "width", "height",
    "duration", "codec", "sha256", "annotation_status", "annotation_method",
    "sensitive_data_check", "embedded_metadata_check", "upload_status", "body_status",
    "provider", "remote_url", "deletion_locator",
)


class AttachmentManifestTest(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name)
        self.manifest_path = self.root / "manifest.json"
        self.path = self.root / "evidence.png"
        self.path.write_bytes(b"not an actual image: decoder review is external")
        self.manifest = {
            "repository": "studio/console", "base": "main", "head": "navigation-review",
            "head_ref_oid": "a" * 40, "pr_url": None, "target_pr_state": "draft",
            "attachments": [self.attachment(self.path)],
        }

    def attachment(self, path, order=1, kind="image", mime="image/png"):
        with path.open("rb") as stream:
            digest = hashlib.sha256()
            for block in iter(lambda: stream.read(1024 * 1024), b""):
                digest.update(block)
        return {
            "source_path": str(path), "local_path": str(path), "kind": kind,
            "purpose": "Show relocated navigation", "body_section": "Visual evidence",
            "display_order": order, "required_for_ready": True,
            "alt_text_or_caption": "Marker 1 identifies the changed navigation trigger",
            "mime_type": mime, "file_size": path.stat().st_size, "width": 1280, "height": 720,
            "duration": 2.5 if kind == "video" else None, "codec": "h264" if kind == "video" else None,
            "sha256": digest.hexdigest(), "annotation_status": "verified", "annotation_method": "outlined trigger",
            "sensitive_data_check": "passed", "embedded_metadata_check": "passed",
            "upload_status": "not_started", "body_status": "not_checked", "provider": "github",
            "remote_url": None, "deletion_locator": None,
        }

    def run_tool(self, manifest=None, phase="pre-create", extra=()):
        if manifest is None:
            manifest = self.manifest
        self.manifest_path.write_text(json.dumps(manifest), encoding="utf-8")
        return self.run_raw(phase, extra)

    def run_raw(self, phase="pre-create", extra=()):
        result = subprocess.run([sys.executable, "-B", str(SCRIPT), "--manifest", str(self.manifest_path),
                                 "--phase", phase, *extra], cwd=self.root, capture_output=True,
                                text=True, check=False, timeout=15)
        return result, json.loads(result.stdout) if result.stdout else None

    def assert_passed(self, **kwargs):
        result, data = self.run_tool(**kwargs)
        self.assertEqual(result.returncode, 0, result.stderr + result.stdout)
        self.assertEqual(data["status"], "passed")
        self.assertEqual(data["errors"], [])
        return data

    def assert_blocked(self, code, **kwargs):
        result, data = self.run_tool(**kwargs)
        self.assertEqual(result.returncode, 1, result.stderr + result.stdout)
        self.assertEqual(data["status"], "blocked")
        self.assertIn(code, [error["code"] for error in data["errors"]])
        return data

    def test_valid_is_read_only_and_does_not_claim_decoding(self):
        before = self.path.read_bytes()
        data = self.assert_passed()
        self.assertEqual(self.path.read_bytes(), before)
        self.assertEqual(json.loads(self.manifest_path.read_text()), self.manifest)
        self.assertEqual({p.name for p in self.root.iterdir()}, {"manifest.json", "evidence.png"})
        self.assertEqual(data["checked_files"][0]["sha256"], hashlib.sha256(before).hexdigest())
        self.assertTrue(any("decoder" in check for check in data["manual_checks"]))
        self.assertTrue(any("privacy" in check for check in data["manual_checks"]))

    def test_every_required_field_is_checked(self):
        for field in OPERATION_FIELDS:
            with self.subTest(operation_field=field):
                manifest = copy.deepcopy(self.manifest)
                del manifest[field]
                self.assert_blocked("missing-field", manifest=manifest)
        for field in ATTACHMENT_FIELDS:
            with self.subTest(attachment_field=field):
                manifest = copy.deepcopy(self.manifest)
                del manifest["attachments"][0][field]
                self.assert_blocked("missing-field", manifest=manifest)

    def test_invalid_shapes_and_values(self):
        for field, value in (("display_order", True), ("file_size", True), ("width", 0), ("height", -1),
                             ("required_for_ready", 1), ("sha256", "bad"), ("annotation_status", {}),
                             ("source_path", []), ("provider", False), ("remote_url", "http://example.com/a")):
            with self.subTest(field=field):
                manifest = copy.deepcopy(self.manifest)
                manifest["attachments"][0][field] = value
                self.assert_blocked("invalid-field", manifest=manifest)
        for manifest in ([], {**self.manifest, "attachments": []}, {**self.manifest, "attachments": [None]},
                         {**self.manifest, "head_ref_oid": "abc"}, {**self.manifest, "target_pr_state": "closed"}):
            self.assert_blocked("invalid-field", manifest=manifest)

    def test_size_and_same_size_content_changes(self):
        self.path.write_bytes(b"replacement")
        self.assert_blocked("size-mismatch")
        self.manifest["attachments"][0]["file_size"] = self.path.stat().st_size
        self.assert_blocked("sha256-mismatch")

    def test_same_content_distinct_files_are_allowed(self):
        other = self.root / "other.png"
        other.write_bytes(self.path.read_bytes())
        self.manifest["attachments"].append(self.attachment(other, 2))
        self.assert_passed()

    def test_duplicate_paths_symbolic_links_and_hard_links(self):
        symbolic = self.root / "symbolic.png"
        symbolic.symlink_to(self.path)
        hard = self.root / "hard.png"
        os.link(self.path, hard)
        for path in (self.path, symbolic, hard, self.root / "." / "evidence.png"):
            with self.subTest(path=path):
                self.manifest["attachments"] = [self.attachment(self.path), self.attachment(path, 2)]
                self.assert_blocked("duplicate-file")

    def test_single_symbolic_link_is_a_regular_file(self):
        symbolic = self.root / "symbolic.png"
        symbolic.symlink_to(self.path)
        self.manifest["attachments"] = [self.attachment(symbolic)]
        data = self.assert_passed()
        self.assertEqual(data["checked_files"][0]["realpath"], str(self.path.resolve()))

    def test_nonfiles_and_unsafe_names(self):
        directory = self.root / "directory.png"
        directory.mkdir()
        fifo = self.root / "pipe.png"
        os.mkfifo(fifo)
        broken = self.root / "broken.png"
        broken.symlink_to(self.root / "absent")
        loop = self.root / "loop.png"
        loop.symlink_to(loop)
        for path, code in ((directory, "not-regular-file"), (fifo, "not-regular-file"),
                           (broken, "file-unreadable"), (loop, "file-unreadable"),
                           (self.root / "missing.png", "file-unreadable"),
                           ("-", "unsafe-path"), ("relative.png", "unsafe-path")):
            with self.subTest(path=str(path)):
                manifest = copy.deepcopy(self.manifest)
                manifest["attachments"][0]["local_path"] = str(path)
                self.assert_blocked(code, manifest=manifest)
        for name, code in (("evidence#caption.png", "unsafe-basename"), ("evidence\n.png", "unsafe-path")):
            path = self.root / name
            path.write_bytes(b"data")
            self.manifest["attachments"] = [self.attachment(path)]
            self.assert_blocked(code)

    def test_empty_file(self):
        self.path.write_bytes(b"")
        self.manifest["attachments"] = [self.attachment(self.path)]
        self.assert_blocked("empty-file")

    def test_supported_extensions_and_exact_declared_mime(self):
        formats = (("PNG", "image", "image/png"), ("jpg", "image", "image/jpeg"),
                   ("JPEG", "image", "image/jpeg"), ("gif", "image", "image/gif"),
                   ("webp", "image", "image/webp"), ("svg", "image", "image/svg+xml"),
                   ("mp4", "video", "video/mp4"), ("MOV", "video", "video/quicktime"),
                   ("webm", "video", "video/webm"))
        for extension, kind, mime in formats:
            with self.subTest(extension=extension):
                path = self.root / ("file." + extension)
                path.write_bytes(b"arbitrary bytes are not a decoded format")
                self.manifest["attachments"] = [self.attachment(path, kind=kind, mime=mime)]
                self.assert_passed()
                self.manifest["attachments"][0]["mime_type"] = "application/octet-stream"
                self.assert_blocked("format-mismatch")
        self.manifest["attachments"][0]["local_path"] = str(self.root / "file.exe")
        self.assert_blocked("unsupported-extension")

    def test_video_metadata_and_image_optional_metadata(self):
        path = self.root / "recording.mp4"
        path.write_bytes(b"video fixture")
        self.manifest["attachments"] = [self.attachment(path, kind="video", mime="video/mp4")]
        for field, value in (("duration", None), ("duration", 0), ("duration", True), ("codec", "")):
            manifest = copy.deepcopy(self.manifest)
            manifest["attachments"][0][field] = value
            self.assert_blocked("invalid-field", manifest=manifest)
        self.manifest["attachments"] = [self.attachment(self.path)]
        self.manifest["attachments"][0].update(duration=1.5, codec="gif")
        self.assert_passed()

    def test_image_limit_inclusive(self):
        with self.path.open("wb") as stream:
            stream.truncate(10 * 1024**2)
        self.manifest["attachments"] = [self.attachment(self.path)]
        self.assert_passed()
        with self.path.open("ab") as stream:
            stream.write(b"x")
        self.assert_blocked("size-limit")

    def test_video_limit_unknown_free_paid_and_eligibility(self):
        path = self.root / "recording.mp4"
        with path.open("wb") as stream:
            stream.truncate(10_000_000)
        self.manifest["attachments"] = [self.attachment(path, kind="video", mime="video/mp4")]
        self.assert_passed()
        self.assert_passed(extra=("--video-plan", "free"))
        with path.open("ab") as stream:
            stream.write(b"x")
        self.manifest["attachments"] = [self.attachment(path, kind="video", mime="video/mp4")]
        for extra in ((), ("--video-plan", "free"), ("--video-plan", "paid")):
            self.assert_blocked("size-limit", extra=extra)
        paid = ("--video-plan", "paid", "--paid-video-eligible")
        self.assert_passed(extra=paid)
        with path.open("wb") as stream:
            stream.truncate(100_000_000)
        self.manifest["attachments"] = [self.attachment(path, kind="video", mime="video/mp4")]
        self.assert_passed(extra=paid)
        with path.open("ab") as stream:
            stream.write(b"x")
        self.assert_blocked("size-limit", extra=paid)
        with path.open("wb") as stream:
            stream.truncate(100 * 1024**2 + 1)
        self.assert_blocked("size-limit", extra=paid)

    def test_recorded_checks_gate_required_and_selected_files(self):
        for field in ("annotation_status", "sensitive_data_check", "embedded_metadata_check"):
            for value in ("not_checked", "failed", "inconclusive"):
                with self.subTest(field=field, value=value):
                    manifest = copy.deepcopy(self.manifest)
                    manifest["attachments"][0][field] = value
                    self.assert_blocked("review-incomplete", manifest=manifest)
                    manifest["attachments"][0]["required_for_ready"] = False
                    self.assert_passed(manifest=manifest)
                    manifest["pr_url"] = "https://github.com/studio/console/pull/17"
                    self.assert_blocked("review-incomplete", manifest=manifest, phase="pre-upload",
                                        extra=("--attachment-order", "1"))

    def test_precreate_requires_new_operation(self):
        self.manifest["pr_url"] = "https://github.com/studio/console/pull/17"
        self.assert_blocked("invalid-field")
        self.manifest["pr_url"] = None
        self.manifest["attachments"][0]["upload_status"] = "uploaded"
        self.assert_blocked("not-fresh")

    def test_preupload_requires_matching_pr_and_selected_fresh_file(self):
        args = {"phase": "pre-upload", "extra": ("--attachment-order", "1")}
        self.assert_blocked("invalid-field", **args)
        self.manifest["pr_url"] = "https://github.com/other/project/pull/17"
        self.assert_blocked("invalid-field", **args)
        self.manifest["pr_url"] = "https://github.com/studio/console/pull/17?expand=1"
        self.assert_blocked("invalid-field", **args)
        self.manifest["pr_url"] = "https://github.com/studio/console/pull/17"
        self.assert_passed(**args)
        self.assert_blocked("attachment-not-found", phase="pre-upload", extra=("--attachment-order", "9"))
        for status in ("unknown", "not_attempted", "failed", "uploaded"):
            self.manifest["attachments"][0]["upload_status"] = status
            self.assert_blocked("not-next-upload", **args)

    def test_preupload_requires_required_files_first_then_display_order(self):
        other = self.root / "other.png"
        other.write_bytes(b"another file")
        self.manifest["attachments"][0]["required_for_ready"] = False
        self.manifest["attachments"].append(self.attachment(other, 2))
        self.manifest["pr_url"] = "https://github.com/studio/console/pull/17"
        self.assert_passed(phase="pre-upload", extra=("--attachment-order", "2"))
        first_optional = {"phase": "pre-upload", "extra": ("--attachment-order", "1")}
        for status in ("not_started", "unknown", "failed", "not_attempted"):
            self.manifest["attachments"][1]["upload_status"] = status
            self.assert_blocked("out-of-sequence", **first_optional)
        self.manifest["attachments"][1]["upload_status"] = "uploaded"
        self.assert_passed(**first_optional)

    def test_preupload_rehashes_selected_but_checks_all_identities(self):
        other = self.root / "other.png"
        other.write_bytes(b"another file")
        self.manifest["attachments"].append(self.attachment(other, 2))
        self.manifest["pr_url"] = "https://github.com/studio/console/pull/17"
        self.manifest["attachments"][0].update(sha256="0" * 64, upload_status="uploaded")
        args = {"phase": "pre-upload", "extra": ("--attachment-order", "2")}
        data = self.assert_passed(**args)
        self.assertIsNone(data["checked_files"][0]["sha256"])
        self.assertIsNotNone(data["checked_files"][1]["sha256"])
        other.write_bytes(b"changed file")
        self.assert_blocked("sha256-mismatch", **args)
        self.manifest["attachments"][1]["local_path"] = str(self.path)
        self.assert_blocked("duplicate-file", **args)

    def test_orders_unique_but_manifest_is_not_one_fifty_file_command(self):
        self.manifest["attachments"] = []
        for order in range(1, 52):
            path = self.root / f"attachment-{order}.png"
            path.write_bytes(b"identical bytes")
            self.manifest["attachments"].append(self.attachment(path, order))
        self.assert_passed()
        self.manifest["attachments"][-1]["display_order"] = 1
        self.assert_blocked("duplicate-order")

    def test_malformed_duplicate_nonfinite_and_missing_input(self):
        for raw in ("{broken", '{"repository":"a/b","repository":"c/d"}', '{"duration":NaN}', "\xff"):
            self.manifest_path.write_bytes(raw.encode("latin-1"))
            result, data = self.run_raw()
            self.assertEqual(result.returncode, 2, result.stderr)
            self.assertEqual(data["status"], "input-error")
        self.manifest_path.unlink()
        result, data = self.run_raw()
        self.assertEqual(result.returncode, 2)
        self.assertEqual(data["errors"][0]["code"], "input-error")

    def test_cli_usage_errors(self):
        for phase, extra in (("pre-upload", ()), ("pre-create", ("--attachment-order", "1")),
                             ("pre-upload", ("--attachment-order", "0")),
                             ("pre-create", ("--paid-video-eligible",))):
            result, data = self.run_tool(phase=phase, extra=extra)
            self.assertEqual(result.returncode, 2)
            self.assertIsNone(data)
            self.assertIn("error:", result.stderr)


if __name__ == "__main__":
    unittest.main()
