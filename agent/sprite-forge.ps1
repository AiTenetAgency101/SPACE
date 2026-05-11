# SPRITE-FORGE AGENT
param(
    [string]$InDir  = 'C:\COM\sprite-src',
    [string]$OutDir = 'C:\COM\sprite-out'
)

if (!(Test-Path $OutDir)) { New-Item -ItemType Directory -Path $OutDir | Out-Null }

$frames = Get-ChildItem $InDir -Filter *.png -ErrorAction SilentlyContinue | Sort-Object Name
$manifest = Join-Path $OutDir 'sprite-manifest.txt'
$frames.FullName | Set-Content $manifest

$stamp = Get-Date -Format o

'SPRITE-FORGE: ACTIVE'
"FRAMES:   $($frames.Count)"
"MANIFEST: $manifest"
"STAMP:    $stamp"
