from __future__ import annotations

import shutil
import subprocess
import time
from pathlib import Path
from urllib.parse import unquote, urlparse

from .base import Result


class MusicController:
    def __init__(self, cfg: dict):
        self.player = str(cfg.get("player_name", "rhythmbox"))
        self.library_root = Path(cfg.get("library_root", "~/Музыка")).expanduser()

        launch = cfg.get("launch_command", ["rhythmbox"])
        self.launch_command = launch if isinstance(launch, list) else ["rhythmbox"]

    def _player_running(self) -> bool:
        try:
            process = subprocess.run(
                ["playerctl", "--list-all"],
                text=True,
                capture_output=True,
                timeout=2,
            )
        except (OSError, subprocess.TimeoutExpired):
            return False

        if process.returncode != 0:
            return False

        names = [line.strip() for line in process.stdout.splitlines() if line.strip()]

        return any(name == self.player or name.startswith(f"{self.player}.") for name in names)

    def open_player(self) -> Result:
        if self.player == "rhythmbox":
            wmctrl = shutil.which("wmctrl")

            if wmctrl is not None:
                try:
                    process = subprocess.run(
                        [
                            wmctrl,
                            "-xa",
                            "rhythmbox.Rhythmbox",
                        ],
                        text=True,
                        capture_output=True,
                        timeout=5,
                    )
                except (
                    OSError,
                    subprocess.TimeoutExpired,
                ):
                    process = None

                if process is not None and process.returncode == 0:
                    return Result(
                        True,
                        "rhythmbox: показан.",
                    )

        if not self.launch_command or not all(
            isinstance(item, str) for item in self.launch_command
        ):
            return Result(
                False,
                "Некорректная команда запуска музыкального проигрывателя.",
            )

        executable = self.launch_command[0]

        if shutil.which(executable) is None:
            return Result(
                False,
                f"Не найден музыкальный проигрыватель: {executable}",
            )

        try:
            subprocess.Popen(
                self.launch_command,
                stdout=subprocess.DEVNULL,
                stderr=subprocess.DEVNULL,
                start_new_session=True,
            )
        except OSError as exc:
            return Result(
                False,
                f"Не удалось запустить {self.player}: {exc}",
            )

        return Result(
            True,
            f"{self.player}: вызван.",
        )

    def _ensure_player(self) -> Result:
        if shutil.which("playerctl") is None:
            return Result(
                False,
                "Не найден playerctl.",
            )

        if self._player_running():
            return Result(
                True,
                "player ready",
            )

        started = self.open_player()

        if not started.ok:
            return started

        for _ in range(30):
            time.sleep(0.1)

            if self._player_running():
                return Result(
                    True,
                    "player ready",
                )

        return Result(
            False,
            f"Не удалось запустить {self.player} через MPRIS.",
        )

    def _playerctl(self, *args: str) -> Result:
        ready = self._ensure_player()

        if not ready.ok:
            return ready

        try:
            process = subprocess.run(
                [
                    "playerctl",
                    "--player",
                    self.player,
                    *args,
                ],
                text=True,
                capture_output=True,
                timeout=3,
            )
        except (
            OSError,
            subprocess.TimeoutExpired,
        ) as exc:
            return Result(
                False,
                f"playerctl: {exc}",
            )

        if process.returncode != 0:
            message = (process.stderr or process.stdout or "playerctl error").strip()

            return Result(
                False,
                message,
            )

        return Result(
            True,
            (process.stdout or "готово").strip(),
        )

    def _track_id(self) -> str:
        try:
            process = subprocess.run(
                [
                    "playerctl",
                    "--player",
                    self.player,
                    "metadata",
                    "mpris:trackid",
                ],
                text=True,
                capture_output=True,
                timeout=2,
            )
        except (
            OSError,
            subprocess.TimeoutExpired,
        ):
            return ""

        if process.returncode != 0:
            return ""

        return process.stdout.strip()

    def quieter(self) -> Result:
        return self._playerctl(
            "volume",
            "0.05-",
        )

    def louder(self) -> Result:
        return self._playerctl(
            "volume",
            "0.05+",
        )

    def status(self) -> Result:
        return self._playerctl(
            "metadata",
            "--format",
            "{{artist}} — {{title}}",
        )

    def play(self) -> Result:
        result = self._playerctl("play")

        if result.ok:
            return result

        # Rhythmbox can expose MPRIS before its current source is
        # initialized. Recover once from that specific cold-start state.
        if "Current playing source is NULL" not in result.message:
            return result

        self._playerctl("pause")
        time.sleep(0.1)
        return self._playerctl("play")

    def pause(self) -> Result:
        return self._playerctl("pause")

    def stop(self) -> Result:
        # IR "стоп" intentionally means resumable pause.
        result = self._playerctl("pause")

        if result.ok:
            return Result(
                True,
                "Музыка: выполнить stop. готово",
            )

        return result

    def delete_current(self) -> Result:
        metadata = self._playerctl(
            "metadata",
            "xesam:url",
        )

        if not metadata.ok:
            return metadata

        parsed = urlparse(metadata.message.strip())

        if parsed.scheme != "file" or parsed.netloc not in ("", "localhost"):
            return Result(
                False,
                "Удаление разрешено только для локального музыкального файла.",
            )

        candidate = Path(unquote(parsed.path))

        if candidate.is_symlink():
            return Result(
                False,
                "Удаление через символическую ссылку запрещено.",
            )

        try:
            root = self.library_root.resolve(strict=True)
            track = candidate.resolve(strict=True)
        except OSError:
            return Result(
                False,
                "Файл текущего трека не найден.",
            )

        if not track.is_relative_to(root):
            return Result(
                False,
                "Трек находится вне разрешённой музыкальной папки.",
            )

        if not track.is_file():
            return Result(
                False,
                "Текущий объект не является обычным файлом.",
            )

        try:
            track.unlink()
        except OSError as exc:
            return Result(
                False,
                f"Не удалось удалить {track.name}: {exc}",
            )

        advanced = self._playerctl("next")

        if not advanced.ok:
            return Result(
                True,
                f"Удалено: {track.name}. Следующий трек не запущен: {advanced.message}",
            )

        return Result(
            True,
            f"Удалено: {track.name}",
        )

    def repeat_current(self) -> Result:
        positioned = self._playerctl(
            "position",
            "0",
        )

        if not positioned.ok:
            return positioned

        played = self._playerctl("play")

        if not played.ok:
            return played

        return Result(
            True,
            "Музыка: текущий трек с начала. готово",
        )

    def next(self) -> Result:
        return self._playerctl("next")

    def previous(self) -> Result:
        # Rhythmbox may treat the first "previous" as restart-current.
        before = self._track_id()

        first = self._playerctl("previous")

        if not first.ok:
            return first

        time.sleep(0.2)

        after = self._track_id()

        if before and after and before == after:
            return self._playerctl("previous")

        return first
