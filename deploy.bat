@echo off
REM SentinelOneWay - Quick Deployment Script (Windows)
REM Run this script to deploy the entire application with Docker

echo ==========================================
echo   SentinelOneWay - Deployment Script
echo ==========================================
echo.

REM Check if Docker is installed
docker --version >nul 2>&1
if errorlevel 1 (
    echo [ERROR] Docker is not installed!
    echo Please install Docker Desktop for Windows:
    echo https://docs.docker.com/desktop/install/windows-install/
    pause
    exit /b 1
)

docker-compose --version >nul 2>&1
if errorlevel 1 (
    echo [ERROR] Docker Compose is not installed!
    echo Please install Docker Compose or update Docker Desktop
    pause
    exit /b 1
)

echo [OK] Docker and Docker Compose are installed
echo.

REM Stop existing containers
echo Stopping existing containers (if any)...
docker-compose down >nul 2>&1
echo [OK] Cleaned up existing containers
echo.

REM Build images
echo Building Docker images...
echo This may take a few minutes on first run...
echo.
docker-compose build --no-cache
if errorlevel 1 (
    echo [ERROR] Failed to build images!
    pause
    exit /b 1
)
echo [OK] Images built successfully
echo.

REM Start services
echo Starting services...
docker-compose up -d
if errorlevel 1 (
    echo [ERROR] Failed to start services!
    pause
    exit /b 1
)
echo [OK] Services started
echo.

REM Wait for services to be healthy
echo Waiting for services to be healthy...
timeout /t 10 /nobreak >nul

REM Check backend health
echo Checking backend health...
set /a attempts=0
:check_backend
set /a attempts+=1
curl -s http://localhost:8000/health >nul 2>&1
if errorlevel 1 (
    if %attempts% LSS 30 (
        echo Waiting... (%attempts%/30)
        timeout /t 2 /nobreak >nul
        goto check_backend
    ) else (
        echo [ERROR] Backend failed to start
        echo Check logs with: docker-compose logs backend
        pause
        exit /b 1
    )
)
echo [OK] Backend is healthy
echo.

REM Check frontend health
echo Checking frontend health...
set /a attempts=0
:check_frontend
set /a attempts+=1
curl -s http://localhost:80 >nul 2>&1
if errorlevel 1 (
    if %attempts% LSS 30 (
        echo Waiting... (%attempts%/30)
        timeout /t 2 /nobreak >nul
        goto check_frontend
    ) else (
        echo [ERROR] Frontend failed to start
        echo Check logs with: docker-compose logs frontend
        pause
        exit /b 1
    )
)
echo [OK] Frontend is healthy
echo.

echo ==========================================
echo   Deployment Successful!
echo ==========================================
echo.
echo Access your application:
echo   Frontend: http://localhost
echo   Backend:  http://localhost:8000
echo   API Docs: http://localhost:8000/docs
echo.
echo Useful commands:
echo   View logs:      docker-compose logs -f
echo   Stop services:  docker-compose down
echo   Restart:        docker-compose restart
echo   Status:         docker-compose ps
echo.
echo Happy monitoring!
echo.
pause
