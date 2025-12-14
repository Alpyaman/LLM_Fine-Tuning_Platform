#!/bin/bash
# Run FastAPI Server from project root

echo "========================================"
echo "Starting FastAPI Server"
echo "========================================"

# Get script directory (project root)
cd "$(dirname "$0")"

# Start API server
python -m phase2.api
