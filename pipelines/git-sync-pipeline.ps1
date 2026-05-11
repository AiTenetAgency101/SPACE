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

git config user.name  'AiTenet'
git config user.email 'engine@local'

git add -A
$msg = Read-Host 'Commit message (blank = auto)'
if ($msg -eq '') { $msg = "sync update 2026-05-11T12:53:52.3888523+10:00" }
git commit -m "$msg" 2>$null
git branch -M main
git push -u origin main
