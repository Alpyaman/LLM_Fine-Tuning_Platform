@echo off
REM Run FastAPI Server from project root

echo ========================================
echo Starting FastAPI Server
echo ========================================

REM Change to project root
cd /d "%~dp0"

REM Start API server
python -m phase2.api

pause
