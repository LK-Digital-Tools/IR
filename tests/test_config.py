from __future__ import annotations

import json
import tempfile
import unittest
from pathlib import Path

from argo.config import load_config


class ConfigTests(unittest.TestCase):
    def test_load_config_expands_home_paths(
        self,
    ):
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "config.json"

            path.write_text(
                json.dumps(
                    {
                        "voice": {"vosk_model": ("~/.local/share/argo/vosk/model")},
                        "music": {"launch_command": ["rhythmbox"]},
                    }
                ),
                encoding="utf-8",
            )

            config = load_config(path)

        self.assertTrue(config["voice"]["vosk_model"].startswith(str(Path.home())))

    def test_non_object_config_is_rejected(
        self,
    ):
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "config.json"

            path.write_text(
                "[]",
                encoding="utf-8",
            )

            with self.assertRaises(ValueError):
                load_config(path)


if __name__ == "__main__":
    unittest.main()
