# AiFACTORi  Execution Pipeline

param([hashtable]$Task)

Write-Host "=== Pipeline ==="
Write-Host "Task: $($Task.Name)"
Write-Host "Description: $($Task.Description)"
Write-Host ""

$index = 1
foreach ($step in $Task.Steps) {
    Write-Host ("[Step {0}] {1}" -f $index, $step)
    $index++
}

Write-Host ""
Write-Host "Pipeline complete (safe mode)."

