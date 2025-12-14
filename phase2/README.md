# Phase 2 - Async Backend API

This module contains the FastAPI backend with Celery task queue.

## Files

- `api.py` - FastAPI application with REST endpoints
- `celery_config.py` - Celery configuration
- `celery_worker.py` - Background task workers
- `storage.py` - Storage utilities (local & S3)

## Usage

### Running Services (from project root):

```bash
# Start Celery Worker
celery -A phase2.celery_config worker --loglevel=info -Q training -P solo

# Start FastAPI Server
python -m phase2.api
```

### Importing in Code:

```python
from phase2.celery_config import celery_app
from phase2.storage import get_storage
```

## API Endpoints

- `POST /upload` - Upload training dataset
- `POST /train` - Start training job
- `GET /status/{job_id}` - Check job status
- `GET /jobs` - List all jobs
- `GET /health` - Health check

## Documentation

See [PHASE2_GUIDE.md](PHASE2_GUIDE.md) for detailed API documentation.

## Important Notes

⚠️ **Always run from project root**, not from phase2 directory!

```bash
# Wrong ❌
cd phase2
celery -A celery_config worker ...

# Correct ✅
cd LLM_Fine-Tuning_Platform
celery -A phase2.celery_config worker ...
```
