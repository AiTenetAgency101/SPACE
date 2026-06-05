
param([string]$InputText)

Write-Host "=== INTEGRATION LAYER ==="

function Capture-HostOutput {
    param($ScriptPath, $Entrypoint, $InputText)

    # Create a new PowerShell instance to capture ALL host output
    $ps = [powershell]::Create()
    $ps.AddScript("& `"$ScriptPath`" -Entrypoint `"$Entrypoint`" -InputText `"$InputText`"") | Out-Null

    # Invoke and capture EVERYTHING printed (Write-Host included)
    $output = $ps.Invoke() | Out-String
    $ps.Dispose()

    return $output
}

Write-Host "`n--- Newton (ENGINE1) ---"
$N = Capture-HostOutput `
        "C:\AiFACTORi\ENGINE2\COM\SHELLS\SHELL1\run.ps1" `
        "operator.engine1.newton.answer" `
        $InputText

Write-Host "`n--- Tesla (ENGINE2) ---"
$T = Capture-HostOutput `
        "C:\AiFACTORi\ENGINE2\COM\SHELLS\SHELL2\run.ps1" `
        "operator.engine2.tesla.answer" `
        $InputText

Write-Host "`n--- Einstein (ENGINE3) ---"
$E = Capture-HostOutput `
        "C:\AiFACTORi\ENGINE2\COM\SHELLS\SHELL3\run.ps1" `
        "operator.engine3.einstein.answer" `
        $InputText

Write-Host "`n=== ASSIST OUTPUT ==="
Write-Host "`nNewton:`n$N"
Write-Host "`nTesla:`n$T"
Write-Host "`nEinstein:`n$E"

