#!/bin/bash
# Run Celery Worker from project root

echo "========================================"
echo "Starting Celery Worker"
echo "========================================"

# Get script directory (project root)
cd "$(dirname "$0")"

# Start Celery worker
celery -A phase2.celery_config worker --loglevel=info -Q training -P solo
