from __future__ import annotations

import asyncio

from .base import Result


class WindowsMediaController:
    def __init__(
        self,
        cfg: dict,
    ) -> None:
        self.cfg = cfg

    async def _get_session(self):
        try:
            from winrt.windows.media.control import (
                GlobalSystemMediaTransportControlsSessionManager,
            )
        except ImportError as exc:
            raise RuntimeError(
                "Windows media support is missing. Install IR with the 'windows' extra.",
            ) from exc

        manager = await GlobalSystemMediaTransportControlsSessionManager.request_async()
        session = manager.get_current_session()

        if session is None:
            raise RuntimeError("No active Windows media session.")

        return session

    def _run(
        self,
        operation,
    ) -> Result:
        try:
            return asyncio.run(operation)
        except Exception as exc:
            return Result(
                False,
                f"Windows media error: {exc}",
            )

    async def _command(
        self,
        method_name: str,
        success_message: str,
    ) -> Result:
        session = await self._get_session()
        method = getattr(
            session,
            method_name,
        )
        accepted = await method()

        if not accepted:
            return Result(
                False,
                "Windows media command rejected.",
            )

        return Result(
            True,
            success_message,
        )

    def play(self) -> Result:
        return self._run(
            self._command(
                "try_play_async",
                "play: ready",
            )
        )

    def pause(self) -> Result:
        return self._run(
            self._command(
                "try_pause_async",
                "pause: ready",
            )
        )

    def next(self) -> Result:
        return self._run(
            self._command(
                "try_skip_next_async",
                "next: ready",
            )
        )

    def previous(self) -> Result:
        return self._run(
            self._command(
                "try_skip_previous_async",
                "previous: ready",
            )
        )

    def stop(self) -> Result:
        return self.pause()

    async def _status(self) -> Result:
        session = await self._get_session()
        properties = await session.try_get_media_properties_async()

        artist = str(
            getattr(
                properties,
                "artist",
                "",
            )
            or ""
        ).strip()
        title = str(
            getattr(
                properties,
                "title",
                "",
            )
            or ""
        ).strip()

        message = f"{artist} — {title}" if artist and title else title or artist or "Unknown track"

        return Result(
            True,
            message,
        )

    def status(self) -> Result:
        return self._run(self._status())

    async def _repeat_current(self) -> Result:
        session = await self._get_session()

        positioned = await session.try_change_playback_position_async(
            0,
        )

        if not positioned:
            return Result(
                False,
                "Windows media seek rejected.",
            )

        played = await session.try_play_async()

        if not played:
            return Result(
                False,
                "Windows media play rejected.",
            )

        return Result(
            True,
            "repeat: ready",
        )

    def repeat_current(self) -> Result:
        return self._run(self._repeat_current())

    def quieter(self) -> Result:
        return Result(
            False,
            "Windows per-session volume is not implemented yet.",
        )

    def louder(self) -> Result:
        return Result(
            False,
            "Windows per-session volume is not implemented yet.",
        )

    def open_player(self) -> Result:
        return Result(
            False,
            "Windows player activation is not implemented yet.",
        )

    def delete_current(self) -> Result:
        return Result(
            False,
            "Windows current-file deletion is not implemented yet.",
        )
