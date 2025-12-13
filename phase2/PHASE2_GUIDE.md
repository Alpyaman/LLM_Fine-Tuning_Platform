# Phase 2: Async Backend - Setup Guide

## 🎯 Overview

Phase 2 wraps the Phase 1 training script in an async API using FastAPI + Celery + Redis. Training jobs are queued and processed by background workers.

## 📦 Architecture

```
Client (cURL/Postman)
    ↓
FastAPI (api.py) - REST API
    ↓
Redis - Message Broker
    ↓
Celery Worker - GPU Training
    ↓
Storage (Local/S3) - Models & Datasets
```

## 🚀 Quick Start

### 1. Install Dependencies

```bash
# Install Phase 2 requirements
pip install -r requirements.txt
```

### 2. Start Redis

**Option A: Docker (Recommended)**
```bash
# Start Redis + Flower (monitoring UI)
docker-compose up -d

# Check status
docker ps
```

**Option B: Local Redis**
```bash
# Windows (via WSL or installer)
redis-server

# Linux/Mac
brew install redis  # Mac
sudo apt install redis  # Ubuntu
redis-server
```

### 3. Update Environment

Add to your `.env`:
```env
# Redis Configuration
REDIS_HOST=localhost
REDIS_PORT=6379
REDIS_DB=0

# Storage Configuration
STORAGE_TYPE=local
STORAGE_BASE_DIR=./storage

# Optional: AWS S3
# STORAGE_TYPE=s3
# S3_BUCKET=your-bucket-name
# AWS_ACCESS_KEY_ID=your-key
# AWS_SECRET_ACCESS_KEY=your-secret
```

### 4. Start Celery Worker

Open a **new terminal** and run:

```bash
celery -A celery_config worker --loglevel=info -Q training -P solo
```

**Note for Windows**: Use `-P solo` or `-P threads` instead of default pool.

### 5. Start FastAPI Server

Open **another terminal** and run:

```bash
python api.py

# Or with uvicorn
uvicorn api:app --reload --host 0.0.0.0 --port 8000
```

### 6. Verify Setup

Open http://localhost:8000/health

You should see:
```json
{
  "status": "healthy",
  "redis_connected": true,
  "celery_workers": 1
}
```

## 📡 API Endpoints

### 1. Upload Dataset

```bash
curl -X POST "http://localhost:8000/upload" \
  -F "file=@example_data.jsonl"
```

Response:
```json
{
  "status": "success",
  "job_id": "abc-123-def",
  "filename": "example_data.jsonl",
  "uploaded_at": "2025-12-13T10:30:00"
}
```

### 2. Start Training

```bash
curl -X POST "http://localhost:8000/train" \
  -H "Content-Type: application/json" \
  -d '{
    "dataset_filename": "example_data.jsonl",
    "config": {
      "base_model": "unsloth/llama-3-8b-bnb-4bit",
      "max_steps": 60,
      "batch_size": 2,
      "learning_rate": 0.0002
    }
  }'
```

Response:
```json
{
  "job_id": "abc-123-def",
  "status": "queued",
  "message": "Training job queued successfully",
  "created_at": "2025-12-13T10:31:00"
}
```

### 3. Check Status

```bash
curl "http://localhost:8000/status/abc-123-def"
```

Response (in progress):
```json
{
  "job_id": "abc-123-def",
  "status": "training",
  "progress": 45,
  "current_step": 27,
  "total_steps": 60
}
```

Response (completed):
```json
{
  "job_id": "abc-123-def",
  "status": "completed",
  "progress": 100,
  "result": {
    "output_dir": "./storage/models/abc-123-def",
    "adapter_dir": "./storage/models/abc-123-def/adapter",
    "training_duration_seconds": 180.5,
    "dataset_size": 5
  }
}
```

### 4. List All Jobs

```bash
curl "http://localhost:8000/jobs"
```

### 5. Cancel Job

```bash
curl -X DELETE "http://localhost:8000/job/abc-123-def"
```

### 6. Download Model

```bash
curl "http://localhost:8000/download/abc-123-def"
```

## 🔍 Monitoring

### Flower UI (Celery Monitoring)

If you used Docker Compose, access Flower at:
```
http://localhost:5555
```

Features:
- View active workers
- Monitor task progress
- See task history
- Worker resource usage

### API Documentation

Interactive API docs:
```
http://localhost:8000/docs
```

## 🧪 Testing with Postman

1. **Import Collection**: Create requests for each endpoint
2. **Set Environment Variables**: 
   - `base_url`: http://localhost:8000
   - `job_id`: (save from upload response)

3. **Test Flow**:
   ```
   1. POST /upload (save job_id)
   2. POST /train (use job_id from step 1)
   3. GET /status/{job_id} (poll until complete)
   4. GET /download/{job_id}
   ```

## 📁 File Structure

```
LLM_Fine-Tuning_Platform/
├── api.py                 # FastAPI application
├── celery_config.py       # Celery configuration
├── celery_worker.py       # Celery tasks (wraps train.py)
├── storage.py             # Storage utilities
├── docker-compose.yml     # Redis + Flower
├── storage/               # Data storage (created)
│   ├── datasets/          # Uploaded datasets
│   └── models/            # Trained models
└── Phase 1 files...
```

## ⚙️ Configuration Options

### Training Config Options

```json
{
  "base_model": "unsloth/llama-3-8b-bnb-4bit",
  "max_steps": 60,
  "batch_size": 2,
  "learning_rate": 0.0002,
  "lora_r": 16,
  "lora_alpha": 16,
  "max_seq_length": 2048
}
```

### Environment Variables

```env
# App
DEBUG=True

# Redis
REDIS_HOST=localhost
REDIS_PORT=6379
REDIS_DB=0

# Storage
STORAGE_TYPE=local  # or 's3'
STORAGE_BASE_DIR=./storage

# S3 (if using)
S3_BUCKET=my-llm-bucket
AWS_ACCESS_KEY_ID=xxx
AWS_SECRET_ACCESS_KEY=yyy

# Defaults
DEFAULT_MODEL=unsloth/llama-3-8b-bnb-4bit
DEFAULT_MAX_STEPS=60
DEFAULT_BATCH_SIZE=2
DEFAULT_LEARNING_RATE=0.0002
```

## 🐛 Troubleshooting

### Redis Connection Failed
```bash
# Check if Redis is running
docker ps  # If using Docker
redis-cli ping  # Should return PONG

# Restart Redis
docker-compose restart redis
```

### No Celery Workers
```bash
# Check workers
celery -A celery_config inspect active

# Restart worker
# Ctrl+C in worker terminal, then restart:
celery -A celery_config worker --loglevel=info -Q training -P solo
```

### Task Stuck in Queue
```bash
# Check task status
celery -A celery_config inspect scheduled

# Purge all tasks (careful!)
celery -A celery_config purge
```

### Dataset Not Found
Make sure to:
1. Upload dataset first (POST /upload)
2. Use the same `job_id` when calling POST /train
3. Check `./storage/datasets/` directory

### Training Fails
- Check worker logs for detailed errors
- Verify GPU is available
- Check dataset format (valid JSONL)
- Ensure sufficient disk space

## 💡 Tips

1. **Testing**: Start with small datasets and `max_steps: 10`
2. **Monitoring**: Keep Flower UI open to watch progress
3. **Logs**: Watch both API and worker terminal outputs
4. **Storage**: Use S3 for production (easier scaling)
5. **Workers**: Run multiple workers for concurrent jobs

## 📈 Next Steps

Phase 2 Complete! You now have:
- ✅ Async API with FastAPI
- ✅ Job queue with Redis + Celery
- ✅ File upload handling
- ✅ Job status tracking
- ✅ Worker monitoring

Ready for **Phase 3: Frontend Dashboard** with Next.js!

## 🔗 Useful Commands

```bash
# Check all workers
celery -A celery_config inspect active

# View registered tasks
celery -A celery_config inspect registered

# Monitor in real-time
celery -A celery_config events

# Flower monitoring
celery -A celery_config flower

# Purge all queued tasks
celery -A celery_config purge

# Check Redis
redis-cli info
redis-cli keys "*"
```

---

**🎉 Milestone Achieved**: You can now trigger training via API and poll for completion!
