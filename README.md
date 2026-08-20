# IR Public 0.1

IR is a local, offline voice controller for desktop music playback.

Current target platforms:

- Linux: full 11-command surface through MPRIS/playerctl
- Windows: validated 8-command voice surface through GSMTC, targeted WM_APPCOMMAND fallback, and Core Audio
- Languages: Russian and English
- Speech recognition: local Vosk
- Cloud services: none

## Voice commands

Russian:

- `Ир, плей`
- `Ир, пауза`
- `Ир, следующий`
- `Ир, предыдущий`
- `Ир, трек` — Linux only
- `Ир, повтор` — Linux only
- `Ир, тише`
- `Ир, громче`
- `Ир, стоп`
- `Ир, музыка`
- `Ир, удалить` — Linux only

English:

- `iris play`
- `iris pause`
- `iris next`
- `iris previous`
- `iris track` — Linux only
- `iris repeat` — Linux only
- `iris quieter`
- `iris louder`
- `iris stop`
- `iris music`
- `iris delete` — Linux only

Commands are exact and require the wake word.

## Platform capability matrix

| Action | Linux | Windows |
|---|---:|---:|
| play | yes | yes |
| pause | yes | yes |
| next | yes | yes |
| previous | yes | yes |
| track/status | yes | no |
| repeat current | yes | no |
| quieter | yes | yes |
| louder | yes | yes |
| stop as resumable pause | yes | yes |
| open player | yes | yes |
| delete current local file | yes | no |

Windows voice grammar deliberately omits `status`, `repeat_current`, and `delete_current`. The validated host exposed no active GSMTC session, and Windows file deletion remains unsupported.

## Linux

Requirements include:

- Python
- Vosk model
- `playerctl`
- `wmctrl`
- a compatible MPRIS player

Example config:

`config.linux.example.json`

Default config path:

`~/.config/argo/config.json`

Install:

```bash
./install_dandi.sh
```

## Windows

Requirements include:

- Python available on `PATH`
- Vosk model
- a GSMTC-compatible media player

Example config:

`config.windows.example.json`

Default config path:

`%APPDATA%\IR\config.json`

Install from PowerShell:

```powershell
.\windows\install_windows.ps1
```

Static + host readiness verification:

```powershell
.\windows\verify_windows.ps1
```

Remove only the IR autostart task:

```powershell
.\windows\uninstall_windows_autostart.ps1
```

The Windows installer creates a project-local virtual environment, installs the `windows` extra, creates a config if needed, and registers a per-user logon task using `pythonw.exe`.

## Config override

Set `IR_CONFIG` to use a non-default config file.

## Vosk models

The config contains separate model paths for `ru` and `en`.

Linux example:

```json
{
  "voice": {
    "language": "ru",
    "models": {
      "ru": "~/.local/share/ir/vosk/vosk-model-small-ru-0.22",
      "en": "~/.local/share/ir/vosk/vosk-model-small-en-us-0.15"
    }
  }
}
```

Windows paths may use environment variables such as `%LOCALAPPDATA%`.

## Safety behavior

IR intentionally fails closed when a platform capability is unavailable.

Linux file deletion accepts only an existing local regular file inside the configured music library root and rejects remote URLs, symlinks, missing files, and paths outside the library.

Windows file deletion is not exposed in the voice grammar.

## Tests

Run:

```bash
python -m unittest discover -v
```

Lint and formatting:

```bash
python -m ruff check argo tests tools
python -m ruff format --check argo tests tools
```

## Status

Linux behavior is derived from the stable private IR V5 baseline.

Windows transport commands prefer GSMTC and fall back to targeted `WM_APPCOMMAND` for play/pause/next/previous/stop when no GSMTC session exists. The stable Windows voice grammar excludes `status`, `repeat`, and `delete`.

Windows live validation is complete for the current 8-command voice surface.

License: MIT. Copyright (c) 2026 LK Digital Tools.

English wake name: `Iris`.

Validated Windows voice surface: `play`, `pause`, `next`, `previous`, `quieter`, `louder`, `stop`, `music`.
