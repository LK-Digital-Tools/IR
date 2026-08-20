# IR Public — Windows Live Validation — 2026-08-19

Target: Windows 11 x86-64.

Verified live:

- installer: PASS
- Windows unit suite after portability repairs: PASS
- PyWinRT runtime: PASS
- Windows.Foundation: PASS
- Windows.Foundation.Collections: PASS
- Windows.Media.Control: PASS
- pycaw: PASS
- Vosk + sounddevice: PASS
- config load: PASS
- English Vosk model: PASS
- audio devices: PASS
- Windows action surface: 8; delete_current omitted
- VLC per-session volume: PASS
- player launch: PASS
- WM_APPCOMMAND pause/play on Windows Media Player Legacy: PASS
- WM_APPCOMMAND next/previous with a multi-track queue: PASS

Observed: VLC and Windows Media Player Legacy exposed no GSMTC sessions on the validation host.

Canonical transport policy:

1. Prefer GSMTC.
2. If GSMTC has no active session, use targeted WM_APPCOMMAND for play, pause, next, previous, and stop-as-pause.
3. Status and repeat remain GSMTC-dependent.
4. Windows delete_current remains unavailable.
- Final Windows live voice validation: English wake name `Iris`; stable Windows grammar = play, pause, next, previous, quieter, louder, stop, open_player. Status/repeat/delete are excluded.
