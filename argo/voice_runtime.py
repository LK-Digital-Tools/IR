from __future__ import annotations

import json
import queue
import shutil
import subprocess
import sys
from pathlib import Path

from .config import load_config
from .music import MusicController, Result

VOSK_PHRASES = {
    "ир плей": "play",
    "ир пауза": "pause",
    "ир следующий": "next",
    "ир предыдущий": "previous",
    "ир трек": "status",
    "ир повтор": "repeat_current",
    "ир тише": "quieter",
    "ир громче": "louder",
    "ир стоп": "stop",
    "ир музыка": "open_player",
    "ир удалить": "delete_current",
}

VOSK_GRAMMAR = [
    *VOSK_PHRASES,
    "[unk]",
]


def command_from_vosk_text(
    text: str,
) -> str | None:
    normalized = " ".join(text.strip().casefold().split())

    return VOSK_PHRASES.get(normalized)


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
    music: MusicController,
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

    model_path = Path(
        voice_cfg.get(
            "vosk_model",
            "~/.local/share/argo/vosk/vosk-model-small-ru-0.22",
        )
    ).expanduser()

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
            VOSK_GRAMMAR,
            ensure_ascii=False,
        ),
    )

    music = MusicController(
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

                action = command_from_vosk_text(text)

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
