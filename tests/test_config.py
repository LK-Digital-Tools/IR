from __future__ import annotations

import json
import tempfile
import unittest
from pathlib import Path

from argo.config import (
    default_config_path,
    load_config,
)


class ConfigTests(unittest.TestCase):
    def test_load_config_expands_home_paths(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            path = Path(temp_dir) / "config.json"
            path.write_text(
                json.dumps(
                    {
                        "voice": {
                            "models": {
                                "ru": "~/models/ru",
                            }
                        },
                        "music": {
                            "library_root": "~/Музыка",
                        },
                    }
                ),
                encoding="utf-8",
            )

            config = load_config(path)

        self.assertFalse(config["voice"]["models"]["ru"].startswith("~"))
        self.assertFalse(config["music"]["library_root"].startswith("~"))

    def test_load_config_expands_environment_variables(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            path = Path(temp_dir) / "config.json"
            path.write_text(
                json.dumps(
                    {
                        "voice": {
                            "models": {
                                "en": "$HOME/models/en",
                            }
                        }
                    }
                ),
                encoding="utf-8",
            )

            config = load_config(path)

        self.assertNotIn(
            "$HOME",
            config["voice"]["models"]["en"],
        )

    def test_non_object_config_is_rejected(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            path = Path(temp_dir) / "config.json"
            path.write_text(
                "[]",
                encoding="utf-8",
            )

            with self.assertRaises(ValueError):
                load_config(path)

    def test_linux_default_preserves_private_compatible_path(self):
        path = default_config_path(
            platform="linux",
            environ={},
        )

        self.assertTrue(
            str(path).endswith(
                "/.config/argo/config.json",
            )
        )

    def test_windows_default_uses_appdata(self):
        path = default_config_path(
            platform="win32",
            environ={
                "APPDATA": r"C:\Users\Ron\AppData\Roaming",
            },
        )

        self.assertEqual(
            path,
            Path(r"C:\Users\Ron\AppData\Roaming") / "IR" / "config.json",
        )

    def test_ir_config_override_wins_on_all_platforms(self):
        path = default_config_path(
            platform="win32",
            environ={
                "APPDATA": r"C:\Users\Ron\AppData\Roaming",
                "IR_CONFIG": "~/custom-ir.json",
            },
        )

        self.assertTrue(
            str(path).endswith(
                "/custom-ir.json",
            )
        )
