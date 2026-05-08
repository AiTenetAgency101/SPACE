# ENGINE MONITORING SUITE - PowerShell Version
# Run these commands anytime to monitor your 3 engines
# Usage: . .\ENGINE_MONITOR.ps1 or copy individual commands

# ============================================================================
# 3 RUNNING ENGINES
# ============================================================================
# engine-365-days (Core 365) - Makes 12M+ cycles with 3 validators
# ultimate-engine (Ultimate Sovereign) - 2.5M cycles, 12 Byzantine layers
# tenetaiagency-101 (Tenet AI Agency) - 641M+ ticks, heartbeat monitoring
# ============================================================================

# ===========================================================================
# QUICK STATUS - Run this to see all 3 engines at a glance
# ===========================================================================
function Get-QuickStatus {
    Write-Host "============================================================================" -ForegroundColor Cyan
    Write-Host "   QUICK STATUS - ALL 3 ENGINES" -ForegroundColor Cyan
    Write-Host "============================================================================" -ForegroundColor Cyan
    Write-Host ""
    
    Write-Host "[1] ENGINE-365-DAYS" -ForegroundColor Yellow
    Write-Host "-----" -ForegroundColor Gray
    docker exec engine-365-days cat /logs/metrics.json 2>$null | ConvertFrom-Json | Select-Object timestamp, uptime_days, cycles_completed, consensus_rate, rejection_rate | Format-List
    
    Write-Host "[2] ULTIMATE-ENGINE" -ForegroundColor Yellow
    Write-Host "-----" -ForegroundColor Gray
    docker exec ultimate-engine cat /logs/ultimate_sovereign_metrics.json 2>$null | ConvertFrom-Json | Select-Object timestamp, uptime_days, cycles, execution_rate, rejection_rate | Format-List
    
    Write-Host "[3] TENETAIAGENCY-101" -ForegroundColor Yellow
    Write-Host "-----" -ForegroundColor Gray
    docker exec tenetaiagency-101 cat /logs/metrics.json 2>$null | ConvertFrom-Json | Select-Object timestamp, uptime_days, ticks, rejection_rate | Format-List
}

# ===========================================================================
# DETAILED METRICS - Full JSON metrics from all engines
# ===========================================================================
function Get-DetailedMetrics {
    Write-Host "============================================================================" -ForegroundColor Cyan
    Write-Host "   DETAILED METRICS - ALL 3 ENGINES" -ForegroundColor Cyan
    Write-Host "============================================================================" -ForegroundColor Cyan
    Write-Host ""
    
    Write-Host "[1] ENGINE-365-DAYS METRICS" -ForegroundColor Yellow
    Write-Host "============================" -ForegroundColor Gray
    docker exec engine-365-days cat /logs/metrics.json 2>$null | ConvertFrom-Json | ConvertTo-Json -Depth 10
    
    Write-Host ""
    Write-Host "[2] ULTIMATE-ENGINE METRICS" -ForegroundColor Yellow
    Write-Host "============================" -ForegroundColor Gray
    docker exec ultimate-engine cat /logs/ultimate_sovereign_metrics.json 2>$null | ConvertFrom-Json | ConvertTo-Json -Depth 10
    
    Write-Host ""
    Write-Host "[3] TENETAIAGENCY-101 METRICS" -ForegroundColor Yellow
    Write-Host "=============================" -ForegroundColor Gray
    docker exec tenetaiagency-101 cat /logs/metrics.json 2>$null | ConvertFrom-Json | ConvertTo-Json -Depth 10
}

# ===========================================================================
# LIVE RESOURCE STATS - Real-time CPU and memory usage
# ===========================================================================
function Get-LiveStats {
    Write-Host "============================================================================" -ForegroundColor Cyan
    Write-Host "   LIVE RESOURCE STATISTICS" -ForegroundColor Cyan
    Write-Host "============================================================================" -ForegroundColor Cyan
    Write-Host ""
    
    docker stats --no-stream engine-365-days ultimate-engine tenetaiagency-101
}

# ===========================================================================
# ENGINE-365-DAYS DEEP DIVE
# ===========================================================================
function Get-Engine365Deep {
    Write-Host "============================================================================" -ForegroundColor Cyan
    Write-Host "   ENGINE-365-DAYS (Core 365) - DEEP ANALYSIS" -ForegroundColor Cyan
    Write-Host "============================================================================" -ForegroundColor Cyan
    Write-Host ""
    
    Write-Host "[METRICS]" -ForegroundColor Yellow
    Write-Host "---------" -ForegroundColor Gray
    docker exec engine-365-days cat /logs/metrics.json 2>$null | ConvertFrom-Json | ConvertTo-Json -Depth 10
    
    Write-Host ""
    Write-Host "[RECENT CYCLES - Last 20]" -ForegroundColor Yellow
    Write-Host "-------------------------" -ForegroundColor Gray
    docker exec engine-365-days tail -20 /logs/cycles.log 2>$null
    
    Write-Host ""
    Write-Host "[VALIDATOR HEALTH]" -ForegroundColor Yellow
    Write-Host "------------------" -ForegroundColor Gray
    docker exec engine-365-days cat /logs/metrics.json 2>$null | ConvertFrom-Json | Select-Object -ExpandProperty validator_health | Format-Table
}

# ===========================================================================
# ULTIMATE-ENGINE DEEP DIVE
# ===========================================================================
function Get-UltimateEngineDeep {
    Write-Host "============================================================================" -ForegroundColor Cyan
    Write-Host "   ULTIMATE-ENGINE (Sovereign) - DEEP ANALYSIS" -ForegroundColor Cyan
    Write-Host "============================================================================" -ForegroundColor Cyan
    Write-Host ""
    
    Write-Host "[METRICS]" -ForegroundColor Yellow
    Write-Host "---------" -ForegroundColor Gray
    docker exec ultimate-engine cat /logs/ultimate_sovereign_metrics.json 2>$null | ConvertFrom-Json | ConvertTo-Json -Depth 10
    
    Write-Host ""
    Write-Host "[CONTAINER STATUS]" -ForegroundColor Yellow
    Write-Host "------------------" -ForegroundColor Gray
    docker ps | Select-String "ultimate-engine"
    
    Write-Host ""
    Write-Host "[AUDIT TRAIL - Last 10]" -ForegroundColor Yellow
    Write-Host "----------------------" -ForegroundColor Gray
    docker exec ultimate-engine tail -10 /logs/ultimate_sovereign_audit.jsonl 2>$null || Write-Host "Audit log not available" -ForegroundColor Gray
}

# ===========================================================================
# TENETAIAGENCY-101 DEEP DIVE
# ===========================================================================
function Get-TenetAIDeep {
    Write-Host "============================================================================" -ForegroundColor Cyan
    Write-Host "   TENETAIAGENCY-101 - DEEP ANALYSIS" -ForegroundColor Cyan
    Write-Host "============================================================================" -ForegroundColor Cyan
    Write-Host ""
    
    Write-Host "[METRICS]" -ForegroundColor Yellow
    Write-Host "---------" -ForegroundColor Gray
    docker exec tenetaiagency-101 cat /logs/metrics.json 2>$null | ConvertFrom-Json | ConvertTo-Json -Depth 10
    
    Write-Host ""
    Write-Host "[HEARTBEAT LOG - Last 20]" -ForegroundColor Yellow
    Write-Host "------------------------" -ForegroundColor Gray
    docker exec tenetaiagency-101 tail -20 /logs/audit.log 2>$null
    
    Write-Host ""
    Write-Host "[CONTAINER STATUS]" -ForegroundColor Yellow
    Write-Host "------------------" -ForegroundColor Gray
    docker ps | Select-String "tenetaiagency-101"
}

# ===========================================================================
# HEALTH CHECK - Container status
# ===========================================================================
function Get-HealthCheck {
    Write-Host "============================================================================" -ForegroundColor Cyan
    Write-Host "   CONTAINER HEALTH CHECK" -ForegroundColor Cyan
    Write-Host "============================================================================" -ForegroundColor Cyan
    Write-Host ""
    
    Write-Host "[RUNNING CONTAINERS]" -ForegroundColor Yellow
    Write-Host "--------------------" -ForegroundColor Gray
    docker ps | Select-String "engine-365|ultimate|tenet"
    
    Write-Host ""
    Write-Host "[HEALTH STATUS]" -ForegroundColor Yellow
    Write-Host "---------------" -ForegroundColor Gray
    docker ps --all --filter "name=engine-365-days" --format "table {{.Names}}\t{{.Status}}"
    docker ps --all --filter "name=ultimate-engine" --format "table {{.Names}}\t{{.Status}}"
    docker ps --all --filter "name=tenetaiagency-101" --format "table {{.Names}}\t{{.Status}}"
}

# ===========================================================================
# CONSENSUS ANALYSIS
# ===========================================================================
function Get-ConsensusAnalysis {
    Write-Host "============================================================================" -ForegroundColor Cyan
    Write-Host "   CONSENSUS RATE ANALYSIS" -ForegroundColor Cyan
    Write-Host "============================================================================" -ForegroundColor Cyan
    Write-Host ""
    
    $engine365 = docker exec engine-365-days cat /logs/metrics.json 2>$null | ConvertFrom-Json
    $ultimate = docker exec ultimate-engine cat /logs/ultimate_sovereign_metrics.json 2>$null | ConvertFrom-Json
    $tenet = docker exec tenetaiagency-101 cat /logs/metrics.json 2>$null | ConvertFrom-Json
    
    Write-Host "ENGINE-365-DAYS Consensus: $($engine365.consensus_rate * 100)%" -ForegroundColor Green
    Write-Host "  Grid Passed: $($engine365.grid_passed)" -ForegroundColor Gray
    Write-Host "  Grid Rejected: $($engine365.grid_rejected)" -ForegroundColor Gray
    
    Write-Host ""
    Write-Host "ULTIMATE-ENGINE Execution: $($ultimate.execution_rate * 100)%" -ForegroundColor Green
    Write-Host "  Decisions Executed: $($ultimate.decisions_executed)" -ForegroundColor Gray
    Write-Host "  Decisions Rejected: $($ultimate.decisions_rejected)" -ForegroundColor Gray
    
    Write-Host ""
    Write-Host "TENETAIAGENCY-101 Status:" -ForegroundColor Green
    Write-Host "  Decisions Executed: $($tenet.decisions_executed)" -ForegroundColor Gray
    Write-Host "  Decisions Rejected: $($tenet.decisions_rejected)" -ForegroundColor Gray
    Write-Host "  Rejection Rate: $($tenet.rejection_rate * 100)%" -ForegroundColor Yellow
}

# ===========================================================================
# DECISION EXECUTION SUMMARY
# ===========================================================================
function Get-DecisionSummary {
    Write-Host "============================================================================" -ForegroundColor Cyan
    Write-Host "   DECISION EXECUTION SUMMARY" -ForegroundColor Cyan
    Write-Host "============================================================================" -ForegroundColor Cyan
    Write-Host ""
    
    $engine365 = docker exec engine-365-days cat /logs/metrics.json 2>$null | ConvertFrom-Json
    $ultimate = docker exec ultimate-engine cat /logs/ultimate_sovereign_metrics.json 2>$null | ConvertFrom-Json
    $tenet = docker exec tenetaiagency-101 cat /logs/metrics.json 2>$null | ConvertFrom-Json
    
    Write-Host "ENGINE-365-DAYS:" -ForegroundColor Yellow
    Write-Host "  Decisions Evaluated: $($engine365.decisions_evaluated)" -ForegroundColor Cyan
    Write-Host "  Decisions Allowed: $($engine365.decisions_allowed)" -ForegroundColor Cyan
    Write-Host "  Grid Passed: $($engine365.grid_passed)" -ForegroundColor Green
    Write-Host "  Grid Rejected: $($engine365.grid_rejected)" -ForegroundColor Yellow
    
    Write-Host ""
    Write-Host "ULTIMATE-ENGINE:" -ForegroundColor Yellow
    Write-Host "  Decisions Executed: $($ultimate.decisions_executed)" -ForegroundColor Cyan
    Write-Host "  Decisions Rejected: $($ultimate.decisions_rejected)" -ForegroundColor Cyan
    Write-Host "  Execution Rate: $($ultimate.execution_rate * 100)%" -ForegroundColor Green
    
    Write-Host ""
    Write-Host "TENETAIAGENCY-101:" -ForegroundColor Yellow
    Write-Host "  Decisions Executed: $($tenet.decisions_executed)" -ForegroundColor Cyan
    Write-Host "  Decisions Rejected: $($tenet.decisions_rejected)" -ForegroundColor Cyan
}

# ===========================================================================
# REJECTION RATE ANALYSIS
# ===========================================================================
function Get-RejectionAnalysis {
    Write-Host "============================================================================" -ForegroundColor Cyan
    Write-Host "   REJECTION RATE ANALYSIS" -ForegroundColor Cyan
    Write-Host "============================================================================" -ForegroundColor Cyan
    Write-Host ""
    
    $engine365 = docker exec engine-365-days cat /logs/metrics.json 2>$null | ConvertFrom-Json
    $ultimate = docker exec ultimate-engine cat /logs/ultimate_sovereign_metrics.json 2>$null | ConvertFrom-Json
    $tenet = docker exec tenetaiagency-101 cat /logs/metrics.json 2>$null | ConvertFrom-Json
    
    $rejection365 = $engine365.rejection_rate * 100
    $rejectionUltimate = $ultimate.rejection_rate * 100
    $rejectionTenet = $tenet.rejection_rate * 100
    
    Write-Host "ENGINE-365-DAYS Rejection: $rejection365%" -ForegroundColor $(if ($rejection365 -lt 75) { "Green" } else { "Yellow" })
    Write-Host "ULTIMATE-ENGINE Rejection: $rejectionUltimate%" -ForegroundColor $(if ($rejectionUltimate -lt 70) { "Green" } else { "Yellow" })
    Write-Host "TENETAIAGENCY-101 Rejection: $rejectionTenet%" -ForegroundColor $(if ($rejectionTenet -eq 100) { "Yellow" } else { "Green" })
}

# ===========================================================================
# BYZANTINE STATUS
# ===========================================================================
function Get-ByzantineStatus {
    Write-Host "============================================================================" -ForegroundColor Cyan
    Write-Host "   BYZANTINE LAYERS & CONSENSUS STATUS" -ForegroundColor Cyan
    Write-Host "============================================================================" -ForegroundColor Cyan
    Write-Host ""
    
    $ultimate = docker exec ultimate-engine cat /logs/ultimate_sovereign_metrics.json 2>$null | ConvertFrom-Json
    $engine365 = docker exec engine-365-days cat /logs/metrics.json 2>$null | ConvertFrom-Json
    
    Write-Host "ULTIMATE-ENGINE Byzantine Configuration:" -ForegroundColor Yellow
    Write-Host "  Byzantine Layers: $($ultimate.byzantine_layers)" -ForegroundColor Cyan
    Write-Host "  Sovereignty Orders: $($ultimate.sovereignty_orders)" -ForegroundColor Cyan
    Write-Host "  Architecture: $($ultimate.architecture)" -ForegroundColor Cyan
    
    Write-Host ""
    Write-Host "ENGINE-365-DAYS Validator Health:" -ForegroundColor Yellow
    $engine365.validator_health | ForEach-Object {
        $reliability = $_.reliability * 100
        Write-Host "  $($_.name):" -ForegroundColor Cyan
        Write-Host "    Checks: $($_.checks) | Failures: $($_.failures) | Reliability: $reliability%" -ForegroundColor Gray
    }
}

# ===========================================================================
# FULL SYSTEM DIAGNOSTICS
# ===========================================================================
function Get-FullDiagnostics {
    Write-Host "============================================================================" -ForegroundColor Cyan
    Write-Host "   FULL SYSTEM DIAGNOSTICS" -ForegroundColor Cyan
    Write-Host "============================================================================" -ForegroundColor Cyan
    Write-Host ""
    
    Write-Host "[1] ALL CONTAINERS STATUS" -ForegroundColor Yellow
    Write-Host "==========================" -ForegroundColor Gray
    docker ps --all | Select-String "engine|ultimate|tenet"
    
    Write-Host ""
    Write-Host "[2] RESOURCE USAGE" -ForegroundColor Yellow
    Write-Host "==================" -ForegroundColor Gray
    docker stats --no-stream engine-365-days ultimate-engine tenetaiagency-101
    
    Write-Host ""
    Write-Host "[3] METRICS SUMMARY" -ForegroundColor Yellow
    Write-Host "===================" -ForegroundColor Gray
    Get-QuickStatus
}

# ===========================================================================
# MAIN MENU
# ===========================================================================
function Show-Menu {
    Clear-Host
    Write-Host ""
    Write-Host "============================================================================" -ForegroundColor Cyan
    Write-Host "   ENGINE MONITORING & DIAGNOSTICS SUITE" -ForegroundColor Cyan
    Write-Host "============================================================================" -ForegroundColor Cyan
    Write-Host ""
    Write-Host "Quick Commands:" -ForegroundColor Yellow
    Write-Host "  Get-QuickStatus              - All 3 engines at a glance"
    Write-Host "  Get-DetailedMetrics          - Full JSON metrics from all"
    Write-Host "  Get-LiveStats                - Real-time resource usage"
    Write-Host "  Get-Engine365Deep            - Engine-365-Days analysis"
    Write-Host "  Get-UltimateEngineDeep       - Ultimate Engine analysis"
    Write-Host "  Get-TenetAIDeep              - Tenet AI Agency 101 analysis"
    Write-Host "  Get-HealthCheck              - Container health status"
    Write-Host "  Get-ConsensusAnalysis        - Consensus rates across engines"
    Write-Host "  Get-DecisionSummary          - Decision execution summary"
    Write-Host "  Get-RejectionAnalysis        - Rejection rate analysis"
    Write-Host "  Get-ByzantineStatus          - Byzantine layers status"
    Write-Host "  Get-FullDiagnostics          - Complete system diagnostics"
    Write-Host ""
    Write-Host "Usage: Type a command name and press Enter" -ForegroundColor Green
    Write-Host "Example: Get-QuickStatus" -ForegroundColor Green
    Write-Host ""
}

# Display menu on startup
Show-Menu
