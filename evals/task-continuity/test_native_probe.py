"""The native probe must inspect the installed package, not its source fixture."""
from pathlib import Path
import tempfile
import unittest

import native_probe


class InstalledReferenceTests(unittest.TestCase):
    def test_requires_reference_beside_installed_hook(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            home = root / "home"
            installed = home / "plugins/cache/fixture/engineering/3.0.0"
            source = root / "marketplace/plugins/engineering"
            (installed / "hooks").mkdir(parents=True)
            (source / "references").mkdir(parents=True)
            (installed / "hooks/hooks.json").write_text("{}")
            (source / "references/continuity.md").write_text("# Source copy\n")
            hook = {"sourcePath": str(installed / "hooks/hooks.json")}

            with self.assertRaisesRegex(RuntimeError, "missing its recovery reference"):
                native_probe.installed_reference(home, hook)

            (installed / "references").mkdir()
            expected = installed / "references/continuity.md"
            expected.write_text("# Installed copy\n")
            self.assertEqual(native_probe.installed_reference(home, hook), expected.resolve())

            with self.assertRaisesRegex(RuntimeError, "outside the installed plugin cache"):
                native_probe.installed_reference(home, {"sourcePath": str(source / "references/continuity.md")})
