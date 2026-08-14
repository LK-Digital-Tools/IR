# IR — local voice music controller

IR is a private, fully local voice controller for music on Dandi.

Current stable baseline: V5.

## Runtime

- Python 3.11+
- Vosk offline speech recognition
- sounddevice microphone input
- Rhythmbox
- playerctl / MPRIS
- wmctrl for presenting the Rhythmbox window
- systemd user service
- Cinnamon tray indicator

No cloud STT.
No TTS.
No OpenAI API.
No Telegram.
No arbitrary shell execution.

## Voice commands

Exact Russian voice surface:

- `Ир, плей`
- `Ир, пауза`
- `Ир, следующий`
- `Ир, предыдущий`
- `Ир, трек`
- `Ир, повтор`
- `Ир, тише`
- `Ир, громче`
- `Ир, стоп`
- `Ир, музыка`
- `Ир, удалить`

`Ир, стоп` is intentionally implemented as a resumable pause.

`Ир, удалить` only deletes the current local file when it is
inside the configured music library root.

## Tests

```bash
.venv/bin/python -m unittest discover -v
```

Current baseline: 25 tests, PASS.

## Configuration

Runtime configuration:

`~/.config/argo/config.json`

Example:

```json
{
  "voice": {
    "sample_rate": 16000,
    "vosk_model": "~/.local/share/argo/vosk/vosk-model-small-ru-0.22"
  },
  "music": {
    "player_name": "rhythmbox",
    "launch_command": ["rhythmbox"],
    "library_root": "~/Музыка"
  }
}
```

## Service

User service:

`~/.config/systemd/user/ir.service`

Useful commands:

```bash
systemctl --user status ir.service
systemctl --user restart ir.service
journalctl --user -u ir.service -n 50 --no-pager
```

## Scope

This directory is the private Linux/Dandi implementation.

The stable V5 implementation remains the private baseline while a future
public branch is developed separately for:

- Russian + English voice commands
- Linux + Windows
- portable configuration
- public GitHub release
