from __future__ import annotations

import unittest

from argo.media.windows_gsmtc import WindowsMediaController


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

    def test_unimplemented_capabilities_fail_closed(self):
        for result in (
            self.controller.quieter(),
            self.controller.louder(),
            self.controller.open_player(),
            self.controller.delete_current(),
        ):
            self.assertFalse(result.ok)
