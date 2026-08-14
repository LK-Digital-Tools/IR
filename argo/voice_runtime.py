from __future__ import annotations

import json
import queue
import shutil
import subprocess
import sys
from pathlib import Path

from .config import load_config
from .languages import get_command_phrases
from .media import MediaController, Result, create_media_controller

VOSK_PHRASES = get_command_phrases("ru")


VOSK_GRAMMAR = [
    *VOSK_PHRASES,
    "[unk]",
]


def get_vosk_model_path(
    voice_cfg: dict,
    language: str,
) -> Path:
    models = voice_cfg.get(
        "models",
        {},
    )

    if not isinstance(models, dict):
        raise ValueError("voice.models must be an object")

    model = models.get(language)

    if not isinstance(model, str) or not model.strip():
        raise ValueError(
            f"No Vosk model configured for language: {language}",
        )

    return Path(model).expanduser()


def command_from_vosk_text(
    text: str,
    phrases: dict[str, str] | None = None,
) -> str | None:
    normalized = " ".join(text.strip().casefold().split())
    active_phrases = VOSK_PHRASES if phrases is None else phrases

    return active_phrases.get(normalized)


def notify_now_playing(
    text: str,
) -> bool:
    executable = shutil.which("notify-send")

    if executable is None:
        return False

    try:
        subprocess.Popen(
            [
                executable,
                "--app-name=IR",
                "--expire-time=4000",
                "Сейчас играет",
                text,
            ],
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL,
        )
    except OSError:
        return False

    return True


def dispatch(
    action: str,
    music: MediaController,
) -> Result:
    if action not in VOSK_PHRASES.values():
        return Result(
            False,
            f"Неизвестная команда IR: {action}",
        )

    return getattr(music, action)()


def main() -> None:
    cfg = load_config()

    voice_cfg = cfg.get(
        "voice",
        {},
    )

    language = str(
        voice_cfg.get(
            "language",
            "ru",
        )
    ).casefold()

    try:
        command_phrases = get_command_phrases(language)
    except ValueError as exc:
        print(
            str(exc),
            file=sys.stderr,
        )
        raise SystemExit(2) from exc

    try:
        import sounddevice as sd
        from vosk import (
            KaldiRecognizer,
            Model,
            SetLogLevel,
        )
    except ImportError as exc:
        print(
            f"IR voice dependency missing: {exc}",
            file=sys.stderr,
        )

        raise SystemExit(2) from exc

    sample_rate = int(
        voice_cfg.get(
            "sample_rate",
            16000,
        )
    )

    try:
        model_path = get_vosk_model_path(
            voice_cfg,
            language,
        )
    except ValueError as exc:
        print(
            str(exc),
            file=sys.stderr,
        )
        raise SystemExit(2) from exc

    if not model_path.is_dir():
        print(
            f"IR Vosk model not found: {model_path}",
            file=sys.stderr,
        )

        raise SystemExit(2)

    SetLogLevel(-1)

    print("IR: загружаю Vosk...")

    model = Model(str(model_path))

    recognizer = KaldiRecognizer(
        model,
        sample_rate,
        json.dumps(
            [
                *command_phrases,
                "[unk]",
            ],
            ensure_ascii=False,
        ),
    )

    music = create_media_controller(
        cfg.get(
            "music",
            {},
        )
    )

    audio_queue: queue.Queue[bytes] = queue.Queue()

    def callback(
        indata,
        _frames,
        _time_info,
        status,
    ):
        if status:
            print(f"AUDIO: {status}")

        audio_queue.put(bytes(indata))

    print("IR active. Vosk grammar. Music only.")

    try:
        with sd.RawInputStream(
            samplerate=sample_rate,
            blocksize=4000,
            dtype="int16",
            channels=1,
            callback=callback,
        ):
            while True:
                data = audio_queue.get()

                if not recognizer.AcceptWaveform(data):
                    continue

                result_json = json.loads(recognizer.Result())

                text = result_json.get(
                    "text",
                    "",
                ).strip()

                if not text:
                    continue

                print(f"HEARD: {text}")

                action = command_from_vosk_text(
                    text,
                    command_phrases,
                )

                if action is None:
                    continue

                result = dispatch(
                    action,
                    music,
                )

                print(f"IR: {result.message}")

                if action == "status" and result.ok:
                    notify_now_playing(result.message)

    except KeyboardInterrupt:
        print("\nIR stopped.")


if __name__ == "__main__":
    main()
