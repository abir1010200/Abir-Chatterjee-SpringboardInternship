@echo off
title KrishiPals AI Smart Irrigation Launcher
color 0A

echo ======================================================================
echo    Starting KrishiPals AI Smart Irrigation Ecosystem (Local Mode)
echo ======================================================================
echo  - No Docker / No WSL required!
echo  - Backend API:    http://127.0.0.1:8000
echo  - Swagger Docs:   http://127.0.0.1:8000/docs
echo  - ML Engine:      http://127.0.0.1:8001
echo  - Frontend Web:   http://localhost:3000
echo ======================================================================
echo.

cd /d "%~dp0"

echo [1/3] Launching FastAPI Backend (Port 8000)...
start "KrishiPals - Backend API" cmd /k "cd /d "%~dp0" && python -m uvicorn backend.main:app --host 127.0.0.1 --port 8000"

echo [2/3] Launching ML Serving Engine (Port 8001)...
start "KrishiPals - ML Engine" cmd /k "cd /d "%~dp0" && python -m uvicorn ml.serving.api:app --host 127.0.0.1 --port 8001"

echo [3/3] Launching Next.js Frontend (Port 3000)...
start "KrishiPals - Frontend" cmd /k "cd /d "%~dp0frontend" && npm run dev"

echo.
echo All services launched in separate windows!
echo Opening browser to http://localhost:3000 in 5 seconds...
timeout /t 5 /nobreak >nul
start http://localhost:3000

echo Done! Keep the opened terminal windows running while using the app.
pause
