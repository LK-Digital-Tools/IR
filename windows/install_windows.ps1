$ErrorActionPreference = "Stop"

$Project = Split-Path -Parent $PSScriptRoot
$Venv = Join-Path $Project ".venv"
$Python = Join-Path $Venv "Scripts\python.exe"
$Pythonw = Join-Path $Venv "Scripts\pythonw.exe"
$ConfigDir = Join-Path $env:APPDATA "IR"
$ConfigPath = Join-Path $ConfigDir "config.json"
$ConfigExample = Join-Path $Project "config.windows.example.json"
$TaskName = "IR Voice"

if (-not (Get-Command python -ErrorAction SilentlyContinue)) {
    throw "Python is not available on PATH."
}

if (-not (Test-Path $Venv)) {
    python -m venv $Venv
}

& $Python -m pip install --upgrade pip
& $Python -m pip install -e "$Project[windows]"

New-Item -ItemType Directory -Force -Path $ConfigDir | Out-Null

if (-not (Test-Path $ConfigPath)) {
    Copy-Item $ConfigExample $ConfigPath
}

$Action = New-ScheduledTaskAction `
    -Execute $Pythonw `
    -Argument '-c "from argo.voice_runtime import main; main()"' `
    -WorkingDirectory $Project

$Trigger = New-ScheduledTaskTrigger `
    -AtLogOn `
    -User $env:USERNAME

Register-ScheduledTask `
    -TaskName $TaskName `
    -Action $Action `
    -Trigger $Trigger `
    -Description "IR local voice media controller" `
    -Force | Out-Null

Write-Host "IR WINDOWS INSTALL: PASS"
Write-Host "Config: $ConfigPath"
Write-Host "Autostart task: $TaskName"
