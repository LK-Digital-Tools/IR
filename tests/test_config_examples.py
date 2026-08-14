from __future__ import annotations

import json
import unittest
from pathlib import Path


class ConfigExampleTests(unittest.TestCase):
    def _load(self, name: str) -> dict:
        return json.loads(
            Path(name).read_text(
                encoding="utf-8",
            )
        )

    def test_linux_example_has_both_languages_and_library_root(self):
        config = self._load(
            "config.linux.example.json",
        )

        self.assertEqual(
            set(config["voice"]["models"]),
            {
                "ru",
                "en",
            },
        )
        self.assertEqual(
            config["music"]["player_name"],
            "rhythmbox",
        )
        self.assertIn(
            "library_root",
            config["music"],
        )

    def test_windows_example_has_both_languages_and_process_name(self):
        config = self._load(
            "config.windows.example.json",
        )

        self.assertEqual(
            set(config["voice"]["models"]),
            {
                "ru",
                "en",
            },
        )
        self.assertEqual(
            config["music"]["process_name"],
            "vlc.exe",
        )
        self.assertNotIn(
            "library_root",
            config["music"],
        )

    def test_generic_example_points_to_platform_examples(self):
        config = self._load(
            "config.example.json",
        )

        self.assertIn(
            "config.linux.example.json",
            config["_note"],
        )
        self.assertIn(
            "config.windows.example.json",
            config["_note"],
        )
