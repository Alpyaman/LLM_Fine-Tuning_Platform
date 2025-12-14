@echo off
REM Startup script for Phase 2 - Windows

echo ========================================
echo Starting LLM Fine-Tuning Platform - Phase 2
echo ========================================

REM Check Docker
echo.
echo Checking Docker...
docker ps >nul 2>&1
if %errorlevel% neq 0 (
    echo ERROR: Docker is not running. Please start Docker Desktop.
    pause
    exit /b 1
)

REM Start Redis
echo.
echo Starting Redis with Docker Compose...
docker-compose up -d
timeout /t 3 >nul

REM Instructions for user
echo.
echo ========================================
echo Services Starting...
echo ========================================
echo.
echo To complete setup, open 2 MORE terminals:
echo.
echo Terminal 2 - Celery Worker:
echo   celery -A phase2.celery_config worker --loglevel=info -Q training -P solo
echo.
echo Terminal 3 - FastAPI Server:
echo   python -m phase2.api
echo.
echo ========================================
echo Access Points:
echo   API:    http://localhost:8000
echo   Docs:   http://localhost:8000/docs
echo   Flower: http://localhost:5555
echo ========================================
echo.

REM Option to start automatically
echo.
set /p START="Start Celery Worker and API automatically? (y/n): "
if /i "%START%"=="y" (
    echo.
    echo Starting Celery Worker...
    start "Celery Worker" cmd /k "celery -A phase2.celery_config worker --loglevel=info -Q training -P solo"
    timeout /t 2 >nul
    
    echo Starting FastAPI Server...
    start "FastAPI Server" cmd /k "python -m phase2.api"
    
    echo.
    echo Services started in separate windows!
) else (
    echo.
    echo Please start services manually as shown above.
)

echo.
pause
