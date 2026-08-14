from __future__ import annotations

import unittest
from unittest.mock import patch

from argo.media.windows_gsmtc import WindowsMediaController


class FakeVolume:
    def __init__(
        self,
        level: float = 0.5,
    ) -> None:
        self.level = level
        self.set_calls: list[float] = []

    def GetMasterVolume(self):
        return self.level

    def SetMasterVolume(
        self,
        level: float,
        _context,
    ):
        self.level = level
        self.set_calls.append(level)


class FakeProperties:
    artist = "Artist"
    title = "Track"


class FakeSession:
    def __init__(self) -> None:
        self.calls: list[object] = []

    async def try_play_async(self):
        self.calls.append("play")
        return True

    async def try_pause_async(self):
        self.calls.append("pause")
        return True

    async def try_skip_next_async(self):
        self.calls.append("next")
        return True

    async def try_skip_previous_async(self):
        self.calls.append("previous")
        return True

    async def try_get_media_properties_async(self):
        self.calls.append("status")
        return FakeProperties()

    async def try_change_playback_position_async(
        self,
        position: int,
    ):
        self.calls.append(
            (
                "position",
                position,
            )
        )
        return True


class TestWindowsController(
    WindowsMediaController,
):
    def __init__(
        self,
        session: FakeSession,
    ) -> None:
        super().__init__({})
        self.session = session

    async def _get_session(self):
        return self.session


class VolumeWindowsController(
    WindowsMediaController,
):
    def __init__(
        self,
        volume: FakeVolume,
    ) -> None:
        super().__init__(
            {
                "process_name": "player.exe",
            }
        )
        self.volume = volume

    def _get_simple_audio_volume(self):
        return self.volume


class WindowsMediaTests(unittest.TestCase):
    def setUp(self):
        self.session = FakeSession()
        self.controller = TestWindowsController(
            self.session,
        )

    def test_play(self):
        result = self.controller.play()

        self.assertTrue(result.ok)
        self.assertEqual(
            self.session.calls,
            ["play"],
        )

    def test_pause(self):
        result = self.controller.pause()

        self.assertTrue(result.ok)
        self.assertEqual(
            self.session.calls,
            ["pause"],
        )

    def test_next(self):
        result = self.controller.next()

        self.assertTrue(result.ok)
        self.assertEqual(
            self.session.calls,
            ["next"],
        )

    def test_previous(self):
        result = self.controller.previous()

        self.assertTrue(result.ok)
        self.assertEqual(
            self.session.calls,
            ["previous"],
        )

    def test_stop_is_resumable_pause(self):
        result = self.controller.stop()

        self.assertTrue(result.ok)
        self.assertEqual(
            self.session.calls,
            ["pause"],
        )

    def test_status(self):
        result = self.controller.status()

        self.assertTrue(result.ok)
        self.assertEqual(
            result.message,
            "Artist — Track",
        )

    def test_repeat_current(self):
        result = self.controller.repeat_current()

        self.assertTrue(result.ok)
        self.assertEqual(
            self.session.calls,
            [
                (
                    "position",
                    0,
                ),
                "play",
            ],
        )

    def test_open_player_launches_configured_command(self):
        controller = TestWindowsController(
            self.session,
        )
        controller.cfg = {
            "launch_command": [
                "player.exe",
                "--flag",
            ]
        }

        with (
            patch(
                "argo.media.windows_gsmtc.shutil.which",
                return_value="C:/Apps/player.exe",
            ),
            patch(
                "argo.media.windows_gsmtc.subprocess.Popen",
            ) as popen,
        ):
            result = controller.open_player()

        self.assertTrue(result.ok)
        popen.assert_called_once()

    def test_open_player_rejects_missing_configuration(self):
        result = self.controller.open_player()

        self.assertFalse(result.ok)

    def test_quieter_reduces_session_volume_by_five_percent(self):
        volume = FakeVolume(
            0.50,
        )
        controller = VolumeWindowsController(
            volume,
        )

        result = controller.quieter()

        self.assertTrue(result.ok)
        self.assertAlmostEqual(
            volume.level,
            0.45,
        )

    def test_louder_increases_session_volume_by_five_percent(self):
        volume = FakeVolume(
            0.50,
        )
        controller = VolumeWindowsController(
            volume,
        )

        result = controller.louder()

        self.assertTrue(result.ok)
        self.assertAlmostEqual(
            volume.level,
            0.55,
        )

    def test_volume_is_clamped_to_zero_and_one(self):
        quiet = FakeVolume(
            0.02,
        )
        loud = FakeVolume(
            0.98,
        )

        self.assertTrue(
            VolumeWindowsController(
                quiet,
            )
            .quieter()
            .ok
        )
        self.assertTrue(
            VolumeWindowsController(
                loud,
            )
            .louder()
            .ok
        )

        self.assertEqual(
            quiet.level,
            0.0,
        )
        self.assertEqual(
            loud.level,
            1.0,
        )

    def test_process_name_falls_back_to_launch_command(self):
        controller = WindowsMediaController(
            {
                "launch_command": [
                    r"C:\\Program Files\\Player\\player.exe",
                ]
            }
        )

        self.assertEqual(
            controller._target_process_name(),
            "player.exe",
        )

    def test_delete_current_remains_fail_closed(self):
        self.assertFalse(self.controller.delete_current().ok)
