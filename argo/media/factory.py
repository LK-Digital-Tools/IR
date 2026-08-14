from __future__ import annotations

import sys

from .base import MediaController
from .linux_mpris import MusicController


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
