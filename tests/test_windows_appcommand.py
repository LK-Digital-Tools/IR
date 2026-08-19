from __future__ import annotations

import unittest

from argo.media.base import Result
from argo.media.windows_appcommand import (
    APPCOMMAND_MEDIA_NEXTTRACK,
    APPCOMMAND_MEDIA_PAUSE,
    APPCOMMAND_MEDIA_PLAY,
    APPCOMMAND_MEDIA_PREVIOUSTRACK,
)
from argo.media.windows_gsmtc import WindowsMediaController


class NoSessionWindowsController(
    WindowsMediaController,
):
    def __init__(self) -> None:
        super().__init__(
            {
                "process_name": "wmplayer.exe",
            }
        )
        self.commands: list[int] = []

    async def _get_session(self):
        raise RuntimeError(
            "No active Windows media session.",
        )

    def _send_appcommand(
        self,
        command: int,
        success_message: str,
    ) -> Result:
        self.commands.append(command)
        return Result(True, success_message)


class WindowsAppCommandFallbackTests(unittest.TestCase):
    def setUp(self):
        self.controller = NoSessionWindowsController()

    def test_play_fallback(self):
        self.assertTrue(self.controller.play().ok)
        self.assertEqual(
            self.controller.commands,
            [APPCOMMAND_MEDIA_PLAY],
        )

    def test_pause_fallback(self):
        self.assertTrue(self.controller.pause().ok)
        self.assertEqual(
            self.controller.commands,
            [APPCOMMAND_MEDIA_PAUSE],
        )

    def test_next_fallback(self):
        self.assertTrue(self.controller.next().ok)
        self.assertEqual(
            self.controller.commands,
            [APPCOMMAND_MEDIA_NEXTTRACK],
        )

    def test_previous_fallback(self):
        self.assertTrue(self.controller.previous().ok)
        self.assertEqual(
            self.controller.commands,
            [APPCOMMAND_MEDIA_PREVIOUSTRACK],
        )

    def test_stop_preserves_pause_semantics(self):
        self.assertTrue(self.controller.stop().ok)
        self.assertEqual(
            self.controller.commands,
            [APPCOMMAND_MEDIA_PAUSE],
        )
