# AiFACTORi  History Engine

param(
    [string]$Intent,
    [string]$Status
)

$entry = @{
    Intent    = $Intent
    Status    = $Status
    Timestamp = (Get-Date).ToString("yyyy-MM-dd HH:mm:ss")
}

$entry | ConvertTo-Json | Add-Content "C:\AiFACTORi\Core\history.log"

