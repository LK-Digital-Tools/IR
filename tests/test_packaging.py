from __future__ import annotations

import tomllib
import unittest
from pathlib import Path


class PackagingTests(unittest.TestCase):
    def test_windows_extra_declares_media_dependencies(self):
        data = tomllib.loads(
            Path("pyproject.toml").read_text(
                encoding="utf-8",
            )
        )

        windows = data["project"]["optional-dependencies"]["windows"]

        self.assertEqual(
            windows,
            [
                "winrt-Windows.Media.Control==3.2.1; platform_system == 'Windows'",
                "pycaw==20251023; platform_system == 'Windows'",
            ],
        )
