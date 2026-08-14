from __future__ import annotations

import sys

from .base import MediaController
from .linux_mpris import (
    SUPPORTED_ACTIONS as LINUX_SUPPORTED_ACTIONS,
)
from .linux_mpris import MusicController


def get_supported_actions(
    *,
    platform: str | None = None,
) -> frozenset[str]:
    target = sys.platform if platform is None else platform

    if target.startswith("linux"):
        return LINUX_SUPPORTED_ACTIONS

    if target == "win32":
        from .windows_gsmtc import (
            SUPPORTED_ACTIONS as WINDOWS_SUPPORTED_ACTIONS,
        )

        return WINDOWS_SUPPORTED_ACTIONS

    raise RuntimeError(
        f"Unsupported IR media platform: {target}",
    )


def create_media_controller(
    cfg: dict,
    *,
    platform: str | None = None,
) -> MediaController:
    target = sys.platform if platform is None else platform

    if target.startswith("linux"):
        return MusicController(cfg)

    if target == "win32":
        from .windows_gsmtc import WindowsMediaController

        return WindowsMediaController(cfg)

    raise RuntimeError(
        f"Unsupported IR media platform: {target}",
    )
