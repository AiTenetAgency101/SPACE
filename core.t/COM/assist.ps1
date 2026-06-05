param([string]$InputText)

$ErrorActionPreference = "Stop"

# ==============================
# ENGINE DEFINITIONS
# ==============================
$Engines = @(
    @{
        Name = "Newton"
        Path = "C:\AiFACTORi\ENGINE2\COM\SHELLS\SHELL1\run.ps1"
        Entrypoint = "operator.engine1.newton.answer"
    },
    @{
        Name = "Tesla"
        Path = "C:\AiFACTORi\ENGINE2\COM\SHELLS\SHELL2\run.ps1"
        Entrypoint = "operator.engine2.tesla.answer"
    },
    @{
        Name = "Einstein"
        Path = "C:\AiFACTORi\ENGINE2\COM\SHELLS\SHELL3\run.ps1"
        Entrypoint = "operator.engine3.einstein.answer"
    }
)

# ==============================
# SYSTEM TELEMETRY
# ==============================
function Get-SystemState {
    try {
        $cpu = (Get-Counter '\Processor(_Total)\% Processor Time').CounterSamples.CookedValue
        $mem = Get-CimInstance Win32_OperatingSystem

        return [PSCustomObject]@{
            CPU = [math]::Round($cpu,2)
            Memory = [math]::Round((($mem.TotalVisibleMemorySize - $mem.FreePhysicalMemory) / $mem.TotalVisibleMemorySize) * 100,2)
        }
    }
    catch {
        return [PSCustomObject]@{
            CPU = 0
            Memory = 0
        }
    }
}

# ==============================
# ENGINE-SPECIFIC SIGNALS
# ==============================
function Assist-Signal {
    param($EngineName, $Output)

    switch ($EngineName) {

        "Newton" {
            if ($Output -match "disk|space|pressure|full|io") {
                Write-Host "?? [Newton Assist] IO or disk pressure rising" -ForegroundColor Yellow
            }
        }

        "Tesla" {
            if ($Output -match "loop|retry|again|spike|storm") {
                Write-Host "?? [Tesla Assist] Loop or retry storm detected" -ForegroundColor Yellow
            }
        }

        "Einstein" {
            if ($Output -match "invalid|failed|exception|critical|unstable") {
                Write-Host "?? [Einstein Assist] System invariants breaking" -ForegroundColor Red
            }
        }
    }
}

# ==============================
# SYSTEM-LEVEL ASSIST
# ==============================
function Assist-System {
    param($state)

    if ($state.CPU -gt 85) {
        Write-Host "?? [Assist] High CPU load ($($state.CPU)%)" -ForegroundColor Red
    }

    if ($state.Memory -gt 90) {
        Write-Host "?? [Assist] Memory pressure critical ($($state.Memory)%)" -ForegroundColor Red
    }
}

# ==============================
# ENGINE EXECUTION (STREAMED)
# ==============================
function Run-EngineLive {
    param($Engine)

    Write-Host "`n=== RUNNING $($Engine.Name) ===" -ForegroundColor Cyan

    if (-not (Test-Path $Engine.Path)) {
        Write-Host "[ERROR] Missing $($Engine.Path)" -ForegroundColor Red
        return ""
    }

    $collected = ""

    & $Engine.Path -Entrypoint $Engine.Entrypoint -InputText $InputText 6>&1 |
    ForEach-Object {

        $line = $_.ToString()
        $collected += $line + "`n"

        Write-Host $line

        Assist-Signal -EngineName $Engine.Name -Output $line

        $state = Get-SystemState
        Assist-System $state
    }

    return $collected.Trim()
}

# ==============================
# FINAL ANALYSIS
# ==============================
function Assist-Logic {
    param($Results)

    Write-Host "`n=== ASSIST FINAL ANALYSIS ===" -ForegroundColor Cyan

    $issues = @()

    foreach ($name in $Results.Keys) {
        $text = $Results[$name]

        if ($text -match "error|fail|exception") {
            $issues += "$name encountered errors"
        }

        if ($text -match "loop|retry|storm") {
            $issues += "$name may be looping"
        }
    }

    if ($issues.Count -eq 0) {
        Write-Host "? All engines completed cleanly" -ForegroundColor Green
    } else {
        foreach ($i in $issues) {
            Write-Host "?? $i" -ForegroundColor Yellow
        }
    }

    Write-Host "`n=== ACTION GUIDANCE ===" -ForegroundColor Cyan
    Write-Host "• Check flagged engines for instability"
    Write-Host "• Monitor CPU/Memory if warnings appeared"
    Write-Host "• Stop processes if loop/storm detected"
}

# ==============================
# MAIN EXECUTION
# ==============================
Write-Host "=== ASSIST MODULE (LIVE MODE) ===" -ForegroundColor Cyan

$Results = @{}

foreach ($engine in $Engines) {
    $Results[$engine.Name] = Run-EngineLive $engine
}

Write-Host "`n=== ENGINE OUTPUT SUMMARY ===" -ForegroundColor Cyan

foreach ($name in $Results.Keys) {
    Write-Host "`n$name OUTPUT:`n$($Results[$name])"
}

Assist-Logic $Results
