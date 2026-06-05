# AiFACTORi  State Engine

param(
    [string]$Intent,
    [string]$Status
)

$state = @{
    LastIntent = $Intent
    LastStatus = $Status
    Timestamp  = (Get-Date).ToString("yyyy-MM-dd HH:mm:ss")
}

$state | ConvertTo-Json | Set-Content "C:\AiFACTORi\Core\state.json" -Encoding UTF8

