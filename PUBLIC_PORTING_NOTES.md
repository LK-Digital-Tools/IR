# IR Public 0.1 — porting notes

Source baseline:
- Private IR V5
- Linux/Dandi
- 11 Russian voice commands
- 25 tests PASS

Public goals:
- Keep private V5 unchanged.
- Add Russian + English language packs.
- Separate core commands from platform-specific media control.
- Keep Linux support.
- Add Windows media backend.
- Remove personal absolute paths from code and templates.
- Keep offline speech recognition.
- Keep cloud/API dependencies out of the core.
- Add portable install documentation.
- Publish only after clean-install tests on Linux and Windows.

Not in scope yet:
- GitHub remote
- release packaging
- installer EXE
- cloud STT/TTS
- Telegram
- Minerva/OpenAI integration

## Completed refactor steps

- Russian command phrases extracted to `argo/languages/ru.py`.
- `voice_runtime.py` keeps the existing public `VOSK_PHRASES` alias, so runtime behavior and tests remain unchanged.
- English command phrases added in `argo/languages/en.py`; runtime selection is intentionally not wired yet.
- Runtime language selection added via `voice.language` (`ru` or `en`); the configured Vosk model must match the selected language.
- Vosk model paths are now configured per language via `voice.models.ru` and `voice.models.en`.
- Linux Rhythmbox/playerctl implementation moved to `argo/media/linux_mpris.py`; runtime behavior is unchanged.
- Platform-neutral media interface and backend factory added; Linux selects the MPRIS backend and unsupported platforms fail closed.
- Media `Result` moved to the platform-neutral backend base so Windows code will not depend on the Linux implementation.
- Initial Windows GSMTC backend added for play/pause/next/previous/status/repeat/stop; volume, player activation, and file deletion remain fail-closed until implemented and tested on Windows.
- Windows PyWinRT dependency is isolated behind the `windows` extra and pinned to `winrt-Windows.Media.Control==3.2.1`.
- Windows `open_player` now launches a configured argv-style `music.launch_command` via `subprocess.Popen`; volume and current-file deletion remain fail-closed.
