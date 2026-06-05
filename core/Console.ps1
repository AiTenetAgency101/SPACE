# AiFACTORi  Unified Console

param([string]$Intent = "status")

Write-Host "=== AiFACTORi Console ==="
Write-Host "Intent: $Intent"
Write-Host ""

$Task = & "C:\AiFACTORi\Tasks\Tasks.ps1" -Intent $Intent
& "C:\AiFACTORi\Pipelines\Pipeline.ps1" -Task $Task
& "C:\AiFACTORi\Core\AgentEngine.ps1" -Intent $Intent
& "C:\AiFACTORi\Logs\LogEngine.ps1" -Intent $Intent -Status "Complete"
& "C:\AiFACTORi\Core\StateEngine.ps1" -Intent $Intent -Status "Complete"
& "C:\AiFACTORi\Core\HistoryEngine.ps1" -Intent $Intent -Status "Complete"
& "C:\AiFACTORi\Core\SnapshotEngine.ps1" -Intent $Intent

Write-Host ""
Write-Host "=== Console Complete ==="

