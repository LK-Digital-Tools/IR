from __future__ import annotations

import unittest

from argo.media.factory import (
    create_media_controller,
    get_supported_actions,
)
from argo.media.linux_mpris import MusicController


class MediaFactoryTests(unittest.TestCase):
    def test_linux_platform_selects_mpris_backend(self):
        controller = create_media_controller(
            {
                "player_name": "rhythmbox",
                "launch_command": ["rhythmbox"],
            },
            platform="linux",
        )

        self.assertIsInstance(
            controller,
            MusicController,
        )

    def test_linux_variant_selects_mpris_backend(self):
        controller = create_media_controller(
            {},
            platform="linux2",
        )

        self.assertIsInstance(
            controller,
            MusicController,
        )

    def test_windows_platform_selects_gsmtc_backend(self):
        from argo.media.windows_gsmtc import WindowsMediaController

        controller = create_media_controller(
            {},
            platform="win32",
        )

        self.assertIsInstance(
            controller,
            WindowsMediaController,
        )

    def test_linux_supports_full_action_surface(self):
        actions = get_supported_actions(
            platform="linux",
        )

        self.assertEqual(
            len(actions),
            11,
        )
        self.assertIn(
            "delete_current",
            actions,
        )

    def test_windows_excludes_unavailable_delete_current(self):
        actions = get_supported_actions(
            platform="win32",
        )

        self.assertEqual(
            len(actions),
            10,
        )
        self.assertNotIn(
            "delete_current",
            actions,
        )

    def test_unsupported_platform_fails_closed(self):
        with self.assertRaisesRegex(
            RuntimeError,
            "Unsupported IR media platform",
        ):
            create_media_controller(
                {},
                platform="darwin",
            )

        with self.assertRaisesRegex(
            RuntimeError,
            "Unsupported IR media platform",
        ):
            get_supported_actions(
                platform="darwin",
            )
