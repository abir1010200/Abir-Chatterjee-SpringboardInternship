# KrishiPals AI Smart Irrigation Ecosystem - PowerShell Launcher (Zero Docker)
Write-Host "======================================================================" -ForegroundColor Cyan
Write-Host "   Starting KrishiPals AI Smart Irrigation Ecosystem (Local Mode)     " -ForegroundColor Green
Write-Host "======================================================================" -ForegroundColor Cyan
Write-Host " - Backend API:    http://127.0.0.1:8000" -ForegroundColor White
Write-Host " - Swagger Docs:   http://127.0.0.1:8000/docs" -ForegroundColor White
Write-Host " - ML Engine:      http://127.0.0.1:8001" -ForegroundColor White
Write-Host " - Frontend Web:   http://localhost:3000" -ForegroundColor White
Write-Host "======================================================================" -ForegroundColor Cyan

$rootDir = Split-Path -Parent $MyInvocation.MyCommand.Path

# 1. Start Backend API
Write-Host "[1/3] Starting FastAPI Backend on Port 8000..." -ForegroundColor Yellow
Start-Process powershell -ArgumentList "-NoExit", "-Command", "Set-Location '$rootDir'; python -m uvicorn backend.main:app --host 127.0.0.1 --port 8000"

# 2. Start ML Engine
Write-Host "[2/3] Starting ML Engine on Port 8001..." -ForegroundColor Yellow
Start-Process powershell -ArgumentList "-NoExit", "-Command", "Set-Location '$rootDir'; python -m uvicorn ml.serving.api:app --host 127.0.0.1 --port 8001"

# 3. Start Frontend
Write-Host "[3/3] Starting Next.js Frontend on Port 3000..." -ForegroundColor Yellow
$frontendDir = Join-Path $rootDir "frontend"
Start-Process powershell -ArgumentList "-NoExit", "-Command", "Set-Location '$frontendDir'; npm run dev"

Start-Sleep -Seconds 5
Start-Process "http://localhost:3000"
Write-Host "`nAll 3 services are running! Your browser should open to http://localhost:3000" -ForegroundColor Green
