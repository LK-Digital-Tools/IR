from __future__ import annotations

import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

from argo.music import (
    MusicController,
    Result,
)


class MusicControllerTests(unittest.TestCase):
    def setUp(self):
        self.music = MusicController(
            {
                "player_name": "rhythmbox",
                "launch_command": ["rhythmbox"],
            }
        )

    def test_stop_is_resumable_pause(
        self,
    ):
        with patch.object(
            self.music,
            "_playerctl",
            return_value=Result(
                True,
                "готово",
            ),
        ) as playerctl:
            result = self.music.stop()

        playerctl.assert_called_once_with("pause")

        self.assertEqual(
            result,
            Result(
                True,
                "Музыка: выполнить stop. готово",
            ),
        )

    def test_previous_retries_when_rhythmbox_restarts_same_track(
        self,
    ):
        with (
            patch.object(
                self.music,
                "_track_id",
                side_effect=[
                    "same",
                    "same",
                ],
            ),
            patch.object(
                self.music,
                "_playerctl",
                return_value=Result(
                    True,
                    "готово",
                ),
            ) as playerctl,
            patch("argo.music.time.sleep"),
        ):
            result = self.music.previous()

        self.assertTrue(result.ok)

        self.assertEqual(
            playerctl.call_count,
            2,
        )

    def test_previous_does_not_retry_when_track_changes(
        self,
    ):
        with (
            patch.object(
                self.music,
                "_track_id",
                side_effect=[
                    "one",
                    "two",
                ],
            ),
            patch.object(
                self.music,
                "_playerctl",
                return_value=Result(
                    True,
                    "готово",
                ),
            ) as playerctl,
            patch("argo.music.time.sleep"),
        ):
            result = self.music.previous()

        self.assertTrue(result.ok)

        playerctl.assert_called_once_with("previous")

    def test_previous_propagates_first_failure(
        self,
    ):
        with (
            patch.object(
                self.music,
                "_track_id",
                return_value="one",
            ),
            patch.object(
                self.music,
                "_playerctl",
                return_value=Result(
                    False,
                    "failed",
                ),
            ) as playerctl,
        ):
            result = self.music.previous()

        self.assertFalse(result.ok)

        playerctl.assert_called_once_with("previous")


if __name__ == "__main__":
    unittest.main()


class MusicColdStartTests(unittest.TestCase):
    def test_play_recovers_once_from_rhythmbox_null_source(self):
        music = MusicController(
            {
                "player_name": "rhythmbox",
                "launch_command": ["rhythmbox"],
            }
        )

        with (
            patch.object(
                music,
                "_playerctl",
                side_effect=[
                    Result(False, "Current playing source is NULL"),
                    Result(True, "готово"),
                    Result(True, "готово"),
                ],
            ) as playerctl,
            patch("argo.music.time.sleep") as sleep,
        ):
            result = music.play()

        self.assertTrue(result.ok)
        self.assertEqual(
            [call.args for call in playerctl.call_args_list],
            [("play",), ("pause",), ("play",)],
        )
        sleep.assert_called_once_with(0.1)

    def test_play_does_not_retry_unrelated_failure(self):
        music = MusicController(
            {
                "player_name": "rhythmbox",
                "launch_command": ["rhythmbox"],
            }
        )

        with patch.object(
            music,
            "_playerctl",
            return_value=Result(False, "different error"),
        ) as playerctl:
            result = music.play()

        self.assertFalse(result.ok)
        playerctl.assert_called_once_with("play")


class MusicDeleteTests(unittest.TestCase):
    def make_music(self, root: Path) -> MusicController:
        return MusicController(
            {
                "player_name": "rhythmbox",
                "launch_command": ["rhythmbox"],
                "library_root": str(root),
            }
        )

    def test_delete_current_removes_local_file_and_advances(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            track = root / "delete-me.mp3"
            track.write_bytes(b"test")

            music = self.make_music(root)

            with patch.object(
                music,
                "_playerctl",
                side_effect=[
                    Result(True, track.as_uri()),
                    Result(True, "готово"),
                ],
            ) as playerctl:
                result = music.delete_current()

            self.assertTrue(result.ok)
            self.assertFalse(track.exists())
            self.assertEqual(
                [call.args for call in playerctl.call_args_list],
                [
                    ("metadata", "xesam:url"),
                    ("next",),
                ],
            )

    def test_delete_current_rejects_remote_url(self):
        with tempfile.TemporaryDirectory() as directory:
            music = self.make_music(Path(directory))

            with patch.object(
                music,
                "_playerctl",
                return_value=Result(
                    True,
                    "https://example.invalid/song.mp3",
                ),
            ) as playerctl:
                result = music.delete_current()

            self.assertFalse(result.ok)
            playerctl.assert_called_once_with(
                "metadata",
                "xesam:url",
            )

    def test_delete_current_rejects_file_outside_library_root(self):
        with tempfile.TemporaryDirectory() as directory:
            base = Path(directory)
            root = base / "music"
            root.mkdir()

            outside = base / "outside.mp3"
            outside.write_bytes(b"keep")

            music = self.make_music(root)

            with patch.object(
                music,
                "_playerctl",
                return_value=Result(
                    True,
                    outside.as_uri(),
                ),
            ):
                result = music.delete_current()

            self.assertFalse(result.ok)
            self.assertTrue(outside.exists())

    def test_delete_current_rejects_missing_file(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            missing = root / "missing.mp3"

            music = self.make_music(root)

            with patch.object(
                music,
                "_playerctl",
                return_value=Result(
                    True,
                    missing.as_uri(),
                ),
            ):
                result = music.delete_current()

            self.assertFalse(result.ok)

    def test_delete_current_rejects_symlink(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            target = root / "real.mp3"
            target.write_bytes(b"keep")

            link = root / "link.mp3"
            link.symlink_to(target)

            music = self.make_music(root)

            with patch.object(
                music,
                "_playerctl",
                return_value=Result(
                    True,
                    link.as_uri(),
                ),
            ):
                result = music.delete_current()

            self.assertFalse(result.ok)
            self.assertTrue(target.exists())
            self.assertTrue(link.is_symlink())


class MusicRepeatTests(unittest.TestCase):
    def setUp(self):
        self.music = MusicController(
            {
                "player_name": "rhythmbox",
                "launch_command": ["rhythmbox"],
            }
        )

    def test_repeat_current_seeks_to_start_and_plays(self):
        with patch.object(
            self.music,
            "_playerctl",
            side_effect=[
                Result(True, "готово"),
                Result(True, "готово"),
            ],
        ) as playerctl:
            result = self.music.repeat_current()

        self.assertTrue(result.ok)

        self.assertEqual(
            [call.args for call in playerctl.call_args_list],
            [
                ("position", "0"),
                ("play",),
            ],
        )

    def test_repeat_current_does_not_play_when_seek_fails(self):
        with patch.object(
            self.music,
            "_playerctl",
            return_value=Result(
                False,
                "seek failed",
            ),
        ) as playerctl:
            result = self.music.repeat_current()

        self.assertFalse(result.ok)
        playerctl.assert_called_once_with(
            "position",
            "0",
        )


class MusicOpenPlayerTests(unittest.TestCase):
    def test_open_player_presents_existing_rhythmbox_window(self):
        music = MusicController(
            {
                "player_name": "rhythmbox",
                "launch_command": ["rhythmbox"],
            }
        )

        process = type(
            "Process",
            (),
            {"returncode": 0},
        )()

        with (
            patch(
                "argo.music.shutil.which",
                return_value="/usr/bin/wmctrl",
            ),
            patch(
                "argo.music.subprocess.run",
                return_value=process,
            ) as run,
        ):
            result = music.open_player()

        self.assertTrue(result.ok)
        self.assertEqual(
            result.message,
            "rhythmbox: показан.",
        )

        run.assert_called_once_with(
            [
                "/usr/bin/wmctrl",
                "-xa",
                "rhythmbox.Rhythmbox",
            ],
            text=True,
            capture_output=True,
            timeout=5,
        )


class MusicVolumeTests(unittest.TestCase):
    def setUp(self):
        self.music = MusicController(
            {
                "player_name": "rhythmbox",
                "launch_command": ["rhythmbox"],
            }
        )

    def test_quieter_decreases_volume_by_five_percent(self):
        with patch.object(
            self.music,
            "_playerctl",
            return_value=Result(
                True,
                "готово",
            ),
        ) as playerctl:
            result = self.music.quieter()

        self.assertTrue(result.ok)
        playerctl.assert_called_once_with(
            "volume",
            "0.05-",
        )

    def test_louder_increases_volume_by_five_percent(self):
        with patch.object(
            self.music,
            "_playerctl",
            return_value=Result(
                True,
                "готово",
            ),
        ) as playerctl:
            result = self.music.louder()

        self.assertTrue(result.ok)
        playerctl.assert_called_once_with(
            "volume",
            "0.05+",
        )
