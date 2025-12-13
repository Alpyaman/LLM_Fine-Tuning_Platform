#!/bin/bash
# Startup script for Phase 2 - Run all services

echo "🚀 Starting LLM Fine-Tuning Platform - Phase 2"
echo "=============================================="

# Check if Redis is running
echo "📡 Checking Redis..."
if ! docker ps | grep -q llm-redis; then
    echo "Starting Redis with Docker Compose..."
    docker-compose up -d
    sleep 3
else
    echo "✓ Redis is already running"
fi

# Start Celery Worker in background
echo ""
echo "👷 Starting Celery Worker..."
celery -A celery_config worker --loglevel=info -Q training -P solo &
CELERY_PID=$!
sleep 2

# Start FastAPI Server
echo ""
echo "🌐 Starting FastAPI Server..."
echo "=============================================="
echo "API: http://localhost:8000"
echo "Docs: http://localhost:8000/docs"
echo "Flower: http://localhost:5555"
echo "=============================================="
echo ""
python api.py

# Cleanup on exit
trap "kill $CELERY_PID; docker-compose down" EXIT
