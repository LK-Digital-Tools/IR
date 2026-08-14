$ErrorActionPreference = "Stop"

$TaskName = "IR Voice"

$Task = Get-ScheduledTask `
    -TaskName $TaskName `
    -ErrorAction SilentlyContinue

if ($null -ne $Task) {
    Unregister-ScheduledTask `
        -TaskName $TaskName `
        -Confirm:$false
}

Write-Host "IR WINDOWS AUTOSTART REMOVED: PASS"
