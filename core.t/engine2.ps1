param(
    [string]$Module,
    [string]$Entrypoint
)

$root = "C:\AiFACTORi\ENGINE2\modules"

if (-not $Module) { Write-Host "ENGINE2: No module specified."; exit }

$path = Join-Path $root $Module
if (-not (Test-Path $path)) { Write-Host "ENGINE2: Module '$Module' not found."; exit }

$manifest = Join-Path $path "module.json"
if (-not (Test-Path $manifest)) { Write-Host "ENGINE2: module.json missing."; exit }

$data = Get-Content $manifest | ConvertFrom-Json

if (-not $Entrypoint) {
    Write-Host "ENGINE2: No entrypoint specified."
    Write-Host "Available entrypoints:"
    $data.entrypoints.PSObject.Properties | ForEach-Object { Write-Host " - $($_.Value)" }
    exit
}

$resolved = $data.entrypoints.PSObject.Properties | Where-Object { $_.Value -eq $Entrypoint } | Select-Object -ExpandProperty Value -ErrorAction SilentlyContinue
if (-not $resolved) { Write-Host "ENGINE2: Entrypoint '$Entrypoint' not found."; exit }

$script = Join-Path $path ("$Entrypoint.ps1")
if (-not (Test-Path $script)) { Write-Host "ENGINE2: Entrypoint script missing."; exit }

Write-Host "ENGINE2: Running $Module ? $Entrypoint" -ForegroundColor Cyan
& $script
