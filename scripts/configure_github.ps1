# AI-Powered Smart Irrigation - GitHub Configuration Script
param (
    [Parameter(Mandatory=$true, HelpMessage="Enter your GitHub Repository URL (e.g. https://github.com/username/smart-irrigation.git)")]
    [string]$RepoUrl,

    [Parameter(Mandatory=$false)]
    [string]$GitUser = "Abir Chatterjee",

    [Parameter(Mandatory=$false)]
    [string]$GitEmail = "abir.chatterjee@example.com"
)

Write-Host "=====================================================" -ForegroundColor Green
Write-Host "🌾 Configuring Git & GitHub Remote for SmartIrrigate" -ForegroundColor Green
Write-Host "=====================================================" -ForegroundColor Green

python scripts/push_to_github.py $RepoUrl

Write-Host "`nGit remote configuration complete!" -ForegroundColor Cyan
