from __future__ import annotations

import importlib.util
import tempfile
import unittest
from pathlib import Path
from unittest import mock


ROOT = Path(__file__).resolve().parents[2]
SCRIPT = ROOT / "scripts" / "render-design-quality.py"
SPEC = importlib.util.spec_from_file_location("render_design_quality", SCRIPT)
assert SPEC is not None and SPEC.loader is not None
MODULE = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(MODULE)


class DesignQualityRendererTests(unittest.TestCase):
    def test_managed_outputs_detects_removed_generated_references_and_assets(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            plugin = root / "plugins" / "sample"
            references = plugin / "references"
            assets = plugin / "assets" / "design-quality"
            scripts = plugin / "scripts"
            references.mkdir(parents=True)
            assets.mkdir(parents=True)
            scripts.mkdir(parents=True)
            generated_reference = references / "removed-reference.md"
            generated_reference.write_bytes(MODULE.MARKER + b"stale\n")
            user_reference = references / "user-authored.md"
            user_reference.write_text("keep\n", encoding="utf-8")
            stale_asset = assets / "removed.schema.json"
            stale_asset.write_text("{}\n", encoding="utf-8")
            validator = scripts / "validate_design_quality.py"
            validator.write_text("# generated\n", encoding="utf-8")
            with (
                mock.patch.object(MODULE, "ROOT", root),
                mock.patch.object(MODULE, "PLUGINS", ("sample",)),
            ):
                managed = MODULE.managed_outputs()
            self.assertIn(generated_reference, managed)
            self.assertIn(stale_asset, managed)
            self.assertIn(validator, managed)
            self.assertNotIn(user_reference, managed)


if __name__ == "__main__":
    unittest.main()
