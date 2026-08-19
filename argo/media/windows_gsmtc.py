from __future__ import annotations

import asyncio
import ntpath
import shutil
import subprocess

from .base import Result
from .windows_appcommand import (
    APPCOMMAND_MEDIA_NEXTTRACK,
    APPCOMMAND_MEDIA_PAUSE,
    APPCOMMAND_MEDIA_PLAY,
    APPCOMMAND_MEDIA_PREVIOUSTRACK,
    send_appcommand,
)

SUPPORTED_ACTIONS = frozenset(
    {
        "play",
        "pause",
        "next",
        "previous",
        "status",
        "repeat_current",
        "quieter",
        "louder",
        "stop",
        "open_player",
    }
)


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

    def _send_appcommand(
        self,
        command: int,
        success_message: str,
    ) -> Result:
        return send_appcommand(
            self._target_process_name(),
            command,
            success_message,
        )

    def _transport_command(
        self,
        method_name: str,
        success_message: str,
        appcommand: int,
    ) -> Result:
        try:
            return asyncio.run(
                self._command(
                    method_name,
                    success_message,
                )
            )
        except RuntimeError as exc:
            if str(exc) == "No active Windows media session.":
                return self._send_appcommand(
                    appcommand,
                    success_message,
                )

            return Result(
                False,
                f"Windows media error: {exc}",
            )
        except Exception as exc:
            return Result(
                False,
                f"Windows media error: {exc}",
            )

    def play(self) -> Result:
        return self._transport_command(
            "try_play_async",
            "play: ready",
            APPCOMMAND_MEDIA_PLAY,
        )

    def pause(self) -> Result:
        return self._transport_command(
            "try_pause_async",
            "pause: ready",
            APPCOMMAND_MEDIA_PAUSE,
        )

    def next(self) -> Result:
        return self._transport_command(
            "try_skip_next_async",
            "next: ready",
            APPCOMMAND_MEDIA_NEXTTRACK,
        )

    def previous(self) -> Result:
        return self._transport_command(
            "try_skip_previous_async",
            "previous: ready",
            APPCOMMAND_MEDIA_PREVIOUSTRACK,
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

    def _target_process_name(self) -> str:
        configured = self.cfg.get(
            "process_name",
            "",
        )

        if isinstance(configured, str) and configured.strip():
            return configured.strip()

        launch = self.cfg.get(
            "launch_command",
            [],
        )

        if isinstance(launch, list) and launch and isinstance(launch[0], str) and launch[0]:
            return ntpath.basename(
                launch[0],
            )

        return ""

    def _get_simple_audio_volume(self):
        try:
            from pycaw.pycaw import AudioUtilities
        except ImportError as exc:
            raise RuntimeError(
                "Windows volume support is missing. Install IR with the 'windows' extra.",
            ) from exc

        target = self._target_process_name()

        if not target:
            raise RuntimeError(
                "Windows music.process_name or launch_command is required for per-session volume.",
            )

        for session in AudioUtilities.GetAllSessions():
            process = session.Process

            if process is None:
                continue

            if process.name().casefold() == target.casefold():
                return session.SimpleAudioVolume

        raise RuntimeError(
            f"Windows audio session not found: {target}",
        )

    def _change_volume(
        self,
        delta: float,
    ) -> Result:
        try:
            volume = self._get_simple_audio_volume()
            current = float(volume.GetMasterVolume())
            target = min(
                1.0,
                max(
                    0.0,
                    current + delta,
                ),
            )
            volume.SetMasterVolume(
                target,
                None,
            )
        except Exception as exc:
            return Result(
                False,
                f"Windows volume error: {exc}",
            )

        return Result(
            True,
            f"Windows volume: {round(target * 100)}%",
        )

    def quieter(self) -> Result:
        return self._change_volume(
            -0.05,
        )

    def louder(self) -> Result:
        return self._change_volume(
            0.05,
        )

    def open_player(self) -> Result:
        launch = self.cfg.get(
            "launch_command",
            [],
        )

        if (
            not isinstance(launch, list)
            or not launch
            or not all(isinstance(item, str) and item for item in launch)
        ):
            return Result(
                False,
                "Windows player launch_command is not configured.",
            )

        executable = launch[0]

        if shutil.which(executable) is None:
            return Result(
                False,
                f"Windows player executable not found: {executable}",
            )

        try:
            subprocess.Popen(
                launch,
                stdout=subprocess.DEVNULL,
                stderr=subprocess.DEVNULL,
            )
        except OSError as exc:
            return Result(
                False,
                f"Windows player launch failed: {exc}",
            )

        return Result(
            True,
            "Windows player launched.",
        )

    def delete_current(self) -> Result:
        return Result(
            False,
            "Windows current-file deletion is not implemented yet.",
        )
