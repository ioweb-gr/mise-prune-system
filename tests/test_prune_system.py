from __future__ import annotations

import importlib.util
import importlib.machinery
import pathlib
import sys
import tempfile
import unittest


SCRIPT = pathlib.Path(__file__).parents[1] / "bin" / "ioweb-prune-system"
LOADER = importlib.machinery.SourceFileLoader("ioweb_prune_system", str(SCRIPT))
SPEC = importlib.util.spec_from_loader("ioweb_prune_system", LOADER)
assert SPEC and SPEC.loader
pruner = importlib.util.module_from_spec(SPEC)
sys.modules[SPEC.name] = pruner
SPEC.loader.exec_module(pruner)


class PruneSystemTests(unittest.TestCase):
    def test_numeric_versions_sort_by_components_and_keep_stable_release(self) -> None:
        self.assertGreater(pruner.version_key("1.0.10"), pruner.version_key("1.0.9"))
        self.assertGreater(pruner.version_key("1.0.0"), pruner.version_key("1.0.0-rc.2"))
        self.assertGreater(pruner.version_key("1.0.0-rc.10"), pruner.version_key("1.0.0-rc.2"))

    def test_unknown_version_schemes_are_not_ordered(self) -> None:
        self.assertIsNone(pruner.version_key("temurin-21.0.2+13"))

    def test_newest_numeric_system_version_is_kept(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            installs_dir = pathlib.Path(temporary) / "installs"
            old_path = installs_dir / "npm-example" / "1.0.9"
            newest_path = installs_dir / "npm-example" / "1.0.10"
            old_path.mkdir(parents=True)
            newest_path.mkdir(parents=True)
            data = {
                "npm:example": [
                    {"installed": True, "version": "1.0.9", "install_path": str(old_path)},
                    {"installed": True, "version": "1.0.10", "install_path": str(newest_path)},
                ]
            }

            found = pruner.find_installs(installs_dir, data, set())

        by_version = {item.version: item for item in found}
        self.assertEqual(by_version["1.0.9"].reasons_kept, ())
        self.assertIn("newest numeric system version for tool", by_version["1.0.10"].reasons_kept)


if __name__ == "__main__":
    unittest.main()
