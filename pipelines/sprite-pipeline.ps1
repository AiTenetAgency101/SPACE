param(
    [string]$InDir  = 'C:\COM\sprite-src',
    [string]$OutDir = 'C:\COM\sprite-out',
    [string]$Sheet  = 'sprite-sheet.png'
)

if (!(Test-Path $OutDir)) { New-Item -ItemType Directory -Path $OutDir | Out-Null }

$frames = Get-ChildItem $InDir -Filter *.png -ErrorAction SilentlyContinue | Sort-Object Name
$manifestPath = Join-Path $OutDir 'sprite-manifest.txt'
$frames.FullName | Set-Content $manifestPath

'SPRITE-PIPELINE'
" IN       = $InDir"
" OUT      = $OutDir\$Sheet"
" FRAMES   = $($frames.Count)"
" MANIFEST = $manifestPath"
