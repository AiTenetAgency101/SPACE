# GIT SYNC PIPELINE (GENERIC)
param(
    [string]$RepoPath = 'C:\COM'
)

Set-Location $RepoPath

if (!(Test-Path '.git')) { git init }

$remote = git remote get-url origin 2>$null
if (-not $remote) {
    $url = Read-Host 'Enter Git remote URL'
    git remote add origin $url
}

git add -A
$msg = "sync 2026-05-11T13:00:29.6641568+10:00"
git commit -m "$msg" 2>$null
git branch -M main
git push -u origin main
