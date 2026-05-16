# AiFACTORi  Snapshot Engine

param([string]$Intent)

$snapshot = @{
    Intent       = $Intent
    Timestamp    = (Get-Date).ToString("yyyy-MM-dd HH:mm:ss")
    Identity     = Get-Content "C:\AiFACTORi\Core\IdentityMemory.txt" -Raw
    Architecture = & "C:\AiFACTORi\Core\Architecture.ps1"
}

$filename = "C:\AiFACTORi\Core\snap_" + (Get-Date -Format "yyyyMMdd_HHmmss") + ".json"
$snapshot | ConvertTo-Json | Set-Content $filename -Encoding UTF8

