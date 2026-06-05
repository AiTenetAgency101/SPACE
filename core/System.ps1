# AI I Am  System Orchestrator

param(
    [string]$Intent = "boot"
)

Write-Host "=== AiFACTORi System ==="
Write-Host "Intent: $Intent"
Write-Host ""

# 1. Load Identity
Write-Host "[1] Loading Identity..."
$Identity = Get-Content "C:\AiFACTORi\Core\IdentityMemory.txt" -Raw
Write-Host $Identity
Write-Host ""

# 2. Load Architecture
Write-Host "[2] Loading Architecture..."
$Architecture = & "C:\AiFACTORi\Core\Architecture.ps1"
Write-Host $Architecture
Write-Host ""

# 3. Route Intent to Agent Engine
Write-Host "[3] Routing to Agent Engine..."
& "C:\AiFACTORi\Core\AgentEngine.ps1" -Intent $Intent

Write-Host ""
Write-Host "=== System Complete ==="

