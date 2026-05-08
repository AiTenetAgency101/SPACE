# QUICK COMMAND REFERENCE
## Run these anytime to monitor your 3 running engines

---

## WINDOWS - BATCH FILE (Easiest)
```
ENGINE_MONITOR.bat
```
Interactive menu with 15 options. Run and select option number.

---

## WINDOWS - POWERSHELL (Most Powerful)
```
. .\ENGINE_MONITOR.ps1
```
Then run any command below:

### One-Liners (Copy & Paste These)

```powershell
# QUICK STATUS - All 3 engines
docker exec engine-365-days cat /logs/metrics.json | ConvertFrom-Json | Select timestamp, uptime_days, cycles_completed, consensus_rate, rejection_rate
docker exec ultimate-engine cat /logs/ultimate_sovereign_metrics.json | ConvertFrom-Json | Select timestamp, uptime_days, cycles, execution_rate
docker exec tenetaiagency-101 cat /logs/metrics.json | ConvertFrom-Json | Select timestamp, uptime_days, ticks, rejection_rate

# LIVE RESOURCE STATS
docker stats --no-stream engine-365-days ultimate-engine tenetaiagency-101

# RECENT CYCLES (Last 20)
docker exec engine-365-days tail -20 /logs/cycles.log
docker exec tenetaiagency-101 tail -20 /logs/audit.log

# CONTAINER STATUS
docker ps | Select-String "engine-365|ultimate|tenet"

# CONSENSUS RATES
docker exec engine-365-days cat /logs/metrics.json | ConvertFrom-Json | Select consensus_rate
docker exec ultimate-engine cat /logs/ultimate_sovereign_metrics.json | ConvertFrom-Json | Select execution_rate

# REJECTION RATES
docker exec engine-365-days cat /logs/metrics.json | ConvertFrom-Json | Select rejection_rate
docker exec ultimate-engine cat /logs/ultimate_sovereign_metrics.json | ConvertFrom-Json | Select rejection_rate
docker exec tenetaiagency-101 cat /logs/metrics.json | ConvertFrom-Json | Select rejection_rate

# VALIDATOR HEALTH (Engine 365)
docker exec engine-365-days cat /logs/metrics.json | ConvertFrom-Json | Select -ExpandProperty validator_health

# BYZANTINE LAYERS (Ultimate Engine)
docker exec ultimate-engine cat /logs/ultimate_sovereign_metrics.json | ConvertFrom-Json | Select byzantine_layers, sovereignty_orders, architecture
```

---

## INDIVIDUAL ENGINE COMMANDS

### Engine-365-Days (Core 365)
```powershell
# Full Metrics
docker exec engine-365-days cat /logs/metrics.json

# Summary
$e = docker exec engine-365-days cat /logs/metrics.json | ConvertFrom-Json
"Cycles: $($e.cycles_completed) | Consensus: $($e.consensus_rate*100)% | Rejection: $($e.rejection_rate*100)%"

# Validators
docker exec engine-365-days cat /logs/metrics.json | ConvertFrom-Json | Select -ExpandProperty validator_health | ft

# Last Cycles
docker exec engine-365-days tail -20 /logs/cycles.log
```

### Ultimate-Engine (Sovereign)
```powershell
# Full Metrics
docker exec ultimate-engine cat /logs/ultimate_sovereign_metrics.json

# Summary
$u = docker exec ultimate-engine cat /logs/ultimate_sovereign_metrics.json | ConvertFrom-Json
"Cycles: $($u.cycles) | Execution: $($u.execution_rate*100)% | Rejection: $($u.rejection_rate*100)% | Layers: $($u.byzantine_layers)"

# Audit
docker exec ultimate-engine tail -20 /logs/ultimate_sovereign_audit.jsonl
```

### Tenet-AI-Agency-101
```powershell
# Full Metrics
docker exec tenetaiagency-101 cat /logs/metrics.json

# Summary
$t = docker exec tenetaiagency-101 cat /logs/metrics.json | ConvertFrom-Json
"Ticks: $($t.ticks) | Rejection: $($t.rejection_rate*100)% | Drift: $($t.drift_ratio)"

# Heartbeat Log
docker exec tenetaiagency-101 tail -20 /logs/audit.log
```

---

## CREATE CUSTOM MONITORING SCRIPTS

### All 3 Engines Quick View
```powershell
$engine365 = docker exec engine-365-days cat /logs/metrics.json | ConvertFrom-Json
$ultimate = docker exec ultimate-engine cat /logs/ultimate_sovereign_metrics.json | ConvertFrom-Json
$tenet = docker exec tenetaiagency-101 cat /logs/metrics.json | ConvertFrom-Json

Write-Host "ENGINE-365-DAYS:      Cycles=$($engine365.cycles_completed) K=$($engine365.consensus_rate.ToString('P'))" -ForegroundColor Cyan
Write-Host "ULTIMATE-ENGINE:      Cycles=$($ultimate.cycles) Exec=$($ultimate.execution_rate.ToString('P'))" -ForegroundColor Green
Write-Host "TENETAIAGENCY-101:    Ticks=$($tenet.ticks) Rejection=$($tenet.rejection_rate.ToString('P'))" -ForegroundColor Yellow
```

### Continuous Monitoring (Every 5 seconds)
```powershell
while ($true) {
    Clear-Host
    Write-Host "$(Get-Date) - ENGINE STATUS"
    
    $e = docker exec engine-365-days cat /logs/metrics.json | ConvertFrom-Json
    $u = docker exec ultimate-engine cat /logs/ultimate_sovereign_metrics.json | ConvertFrom-Json
    $t = docker exec tenetaiagency-101 cat /logs/metrics.json | ConvertFrom-Json
    
    Write-Host "E365: $($e.cycles_completed) cycles | $($e.consensus_rate*100)% consensus" -ForegroundColor Cyan
    Write-Host "ULTI: $($u.cycles) cycles | $($u.execution_rate*100)% execution" -ForegroundColor Green
    Write-Host "TENET: $($t.ticks) ticks | $($t.rejection_rate*100)% rejection" -ForegroundColor Yellow
    
    Start-Sleep -Seconds 5
}
```

### Export Metrics to CSV
```powershell
$timestamp = Get-Date -Format "yyyy-MM-dd_HHmm"
$file = "engine_metrics_$timestamp.csv"

$e = docker exec engine-365-days cat /logs/metrics.json | ConvertFrom-Json
$u = docker exec ultimate-engine cat /logs/ultimate_sovereign_metrics.json | ConvertFrom-Json
$t = docker exec tenetaiagency-101 cat /logs/metrics.json | ConvertFrom-Json

@(
    [PSCustomObject]@{Engine='engine-365-days'; Cycles=$e.cycles_completed; ConsensusRate=$e.consensus_rate; RejectionRate=$e.rejection_rate}
    [PSCustomObject]@{Engine='ultimate-engine'; Cycles=$u.cycles; ExecutionRate=$u.execution_rate; RejectionRate=$u.rejection_rate}
    [PSCustomObject]@{Engine='tenetaiagency-101'; Ticks=$t.ticks; RejectionRate=$t.rejection_rate; DriftRatio=$t.drift_ratio}
) | Export-Csv -Path $file -NoTypeInformation

Write-Host "Exported to $file"
```

---

## DOCKER COMMANDS

### Start Monitoring 
```bash
# Watch all 3 containers in real-time
docker stats engine-365-days ultimate-engine tenetaiagency-101

# View logs
docker logs -f engine-365-days
docker logs -f ultimate-engine
docker logs -f tenetaiagency-101

# View detailed info
docker inspect engine-365-days
docker inspect ultimate-engine
docker inspect tenetaiagency-101

# Health check
docker ps --all | grep -E "engine-365|ultimate|tenet"
```

---

## KEY METRICS TO MONITOR

### Engine-365-Days
- **cycles_completed**: Total cycles executed (should be growing)
- **consensus_rate**: Should be 1.0 (100%)
- **rejection_rate**: Currently ~0.71 (71% of decisions rejected)
- **validator_health**: Circle, Monotonic, Range reliability (all 100%)

### Ultimate-Engine
- **cycles**: Total cycles (should be growing)
- **execution_rate**: ~39% (39% of decisions executed)
- **rejection_rate**: ~61% (61% of decisions rejected)
- **byzantine_layers**: 12 layers of consensus
- **sovereignty_orders**: 10 orders

### Tenet-AI-Agency-101
- **ticks**: Total ticks (641M+, should be growing)
- **decisions_executed**: Total executed (0)
- **decisions_rejected**: Total rejected (641M+)
- **rejection_rate**: 100% (all decisions currently rejected)
- **drift_ratio**: Phase drift tracking

---

## TROUBLESHOOTING

### Container not responding
```powershell
docker restart engine-365-days
docker restart ultimate-engine
docker restart tenetaiagency-101
```

### View error logs
```powershell
docker logs engine-365-days 2>&1 | tail -50
docker logs ultimate-engine 2>&1 | tail -50
docker logs tenetaiagency-101 2>&1 | tail -50
```

### Check resource limits
```powershell
docker stats --no-stream
docker inspect engine-365-days | Select-String "Memory"
```

### Force full restart
```powershell
docker stop engine-365-days ultimate-engine tenetaiagency-101
docker start engine-365-days ultimate-engine tenetaiagency-101
```

---

## AUTOMATION

### Create scheduled task in Windows
```powershell
# Run monitoring every hour
$trigger = New-ScheduledTaskTrigger -AtStartup -RepetitionInterval (New-TimeSpan -Hours 1)
$action = New-ScheduledTaskAction -Execute "PowerShell.exe" -Argument "-NoProfile -WindowStyle Hidden -File C:\path\to\ENGINE_MONITOR.ps1"
Register-ScheduledTask -TaskName "Engine-Monitor" -Trigger $trigger -Action $action -RunLevel Highest
```

### Create alert script
```powershell
# Alert if rejection rate > 75%
$e = docker exec engine-365-days cat /logs/metrics.json | ConvertFrom-Json
if ($e.rejection_rate -gt 0.75) {
    Write-Host "WARNING: High rejection rate $($e.rejection_rate*100)%" -ForegroundColor Red
}
```

---

## QUICK ALIASES (Add to PowerShell Profile)

```powershell
# Add to $PROFILE file
Set-Alias -Name e365 -Value { docker exec engine-365-days cat /logs/metrics.json | ConvertFrom-Json }
Set-Alias -Name eult -Value { docker exec ultimate-engine cat /logs/ultimate_sovereign_metrics.json | ConvertFrom-Json }
Set-Alias -Name eten -Value { docker exec tenetaiagency-101 cat /logs/metrics.json | ConvertFrom-Json }
Set-Alias -Name estats -Value { docker stats --no-stream engine-365-days ultimate-engine tenetaiagency-101 }
```

Then use: `e365`, `eult`, `eten`, `estats`

---

## NEED HELP?

Run these to understand your engines:

```powershell
# What is each engine?
Write-Host "Engine-365-Days: Core validator with 3 validation layers (Circle, Monotonic, Range)"
Write-Host "Ultimate-Engine: Sovereign decision maker with 12 Byzantine layers"
Write-Host "TenetAI-Agency-101: Continuous decision rejection agent (drift tracking)"

# Current status summary
docker ps | Select-String "engine-365|ultimate|tenet"

# All running processes
docker ps -a
```

---

**Save this file and bookmark it. Run these commands anytime to check your engines.**
