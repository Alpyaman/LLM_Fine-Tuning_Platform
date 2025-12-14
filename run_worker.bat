@echo off
REM Run Celery Worker from project root

echo ========================================
echo Starting Celery Worker
echo ========================================

REM Change to project root
cd /d "%~dp0"

REM Start Celery worker
celery -A phase2.celery_config worker --loglevel=info -Q training -P solo

pause
