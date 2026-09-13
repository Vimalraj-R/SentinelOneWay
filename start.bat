@echo off
REM SentinelOneWay Quick Start Script for Windows
REM Run this with: start.bat

echo ==========================================
echo    SentinelOneWay - Quick Start
echo ==========================================
echo.

echo What would you like to do?
echo.
echo 1) Start Backend Only
echo 2) Start Frontend Only
echo 3) Generate Sample Data
echo 4) View URLs
echo 5) Check Status
echo.

set /p choice="Enter choice [1-5]: "

if "%choice%"=="1" goto backend
if "%choice%"=="2" goto frontend
if "%choice%"=="3" goto generate
if "%choice%"=="4" goto urls
if "%choice%"=="5" goto status
goto end

:backend
echo Starting Backend...
cd backend
call venv\Scripts\activate
echo Backend starting at http://localhost:8000
echo Press CTRL+C to stop
uvicorn main:app --reload
goto end

:frontend
echo Starting Frontend...
cd frontend
echo Frontend starting at http://localhost:5173
echo Press CTRL+C to stop
npm run dev
goto end

:generate
echo Generating Sample Data...
cd backend
call venv\Scripts\activate
python demo_correlation.py
echo.
echo Done! Generated:
echo   - 15 alerts (Port Scans, C2 Beacons, Exfiltration)
echo   - 3 correlated incidents (Multi-stage attacks)
echo.
echo Refresh your dashboard to see the data!
pause
goto end

:urls
echo.
echo === SentinelOneWay URLs ===
echo.
echo Frontend Dashboard:
echo   http://localhost:5173
echo.
echo Backend API:
echo   http://localhost:8000
echo   http://localhost:8000/docs (API Documentation)
echo   http://localhost:8000/health (Health Check)
echo.
echo WebSocket:
echo   ws://localhost:8000/ws/alerts
echo.
pause
goto end

:status
echo.
echo Checking Backend...
curl -s http://localhost:8000/health >nul 2>&1
if %errorlevel%==0 (
    echo   [OK] Backend is RUNNING (http://localhost:8000)
) else (
    echo   [X] Backend is NOT running
)

echo.
echo Checking Frontend...
curl -s http://localhost:5173 >nul 2>&1
if %errorlevel%==0 (
    echo   [OK] Frontend is RUNNING (http://localhost:5173)
) else (
    echo   [X] Frontend is NOT running
)
echo.
pause
goto end

:end
