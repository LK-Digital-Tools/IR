$ErrorActionPreference = "Stop"

$Project = Split-Path -Parent $PSScriptRoot
$Python = Join-Path $Project ".venv\Scripts\python.exe"
$Config = Join-Path $env:APPDATA "IR\config.json"

if (-not (Test-Path $Python)) {
    throw "IR venv not found. Run windows\install_windows.ps1 first."
}

& $Python -m unittest discover -v
if ($LASTEXITCODE -ne 0) {
    throw "Unit tests failed."
}

& $Python -c "from winrt.windows.media.control import GlobalSystemMediaTransportControlsSessionManager; print('WINRT IMPORT: PASS')"
if ($LASTEXITCODE -ne 0) {
    throw "WinRT media import failed."
}

& $Python -c "from pycaw.pycaw import AudioUtilities; print('PYCAW IMPORT: PASS')"
if ($LASTEXITCODE -ne 0) {
    throw "pycaw import failed."
}

& $Python -c "import sounddevice; import vosk; print('VOICE DEPENDENCIES: PASS')"
if ($LASTEXITCODE -ne 0) {
    throw "Voice dependency import failed."
}

if (-not (Test-Path $Config)) {
    throw "IR config not found: $Config"
}

$env:IR_CONFIG = $Config

& $Python -c "from argo.config import load_config; cfg = load_config(); print('CONFIG LOAD: PASS'); print('LANGUAGE:', cfg['voice']['language'])"
if ($LASTEXITCODE -ne 0) {
    throw "Config load failed."
}

& $Python -c "from argo.media import get_supported_actions; actions = get_supported_actions(platform='win32'); assert len(actions) == 10; assert 'delete_current' not in actions; print('WINDOWS ACTION SURFACE: PASS'); print('ACTIONS:', ' '.join(sorted(actions)))"
if ($LASTEXITCODE -ne 0) {
    throw "Windows action surface verification failed."
}

& $Python -c "import sounddevice as sd; devices = sd.query_devices(); assert len(devices) > 0; print('AUDIO DEVICES: PASS'); print('COUNT:', len(devices))"
if ($LASTEXITCODE -ne 0) {
    throw "No audio devices visible to sounddevice."
}

Write-Host "WINDOWS READINESS VERIFIER: PASS"
Write-Host "NEXT: live microphone + media-control test"
