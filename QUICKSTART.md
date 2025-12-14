# Quick Start Guide - Phase 2

## 🚀 Running Phase 2 (From Project Root)

### Important: Always run from project root directory!

```bash
# Navigate to project root
cd C:\Users\alpyaman\Desktop\Projects\LLM_Fine-Tuning_Platform
```

## Option 1: Automated Start (Windows)

```bash
# Run the automated startup script
start.bat
```

## Option 2: Manual Start (Recommended for debugging)

### Step 1: Start Redis

```bash
docker-compose up -d
```

### Step 2: Start Celery Worker (Terminal 1)

From project root:
```bash
celery -A phase2.celery_config worker --loglevel=info -Q training -P solo
```

Or use the helper script:
```bash
run_worker.bat
```

### Step 3: Start FastAPI Server (Terminal 2)

From project root:
```bash
python -m phase2.api
```

Or use the helper script:
```bash
run_api.bat
```

## ✅ Verify Everything Works

1. Open http://localhost:8000/health - Should show healthy status
2. Open http://localhost:8000/docs - Interactive API documentation
3. Open http://localhost:5555 - Flower monitoring UI

## 🧪 Test the API

From project root:
```bash
python tests/test_api.py
```

## ❌ Common Issues

### Issue: ModuleNotFoundError: No module named 'phase1'

**Solution**: Make sure you're running from the project root, not from phase2 folder!

```bash
# Wrong ❌
cd phase2
celery -A celery_config worker ...

# Correct ✅
cd C:\Users\alpyaman\Desktop\Projects\LLM_Fine-Tuning_Platform
celery -A phase2.celery_config worker ...
```

### Issue: Redis connection failed

**Solution**: Start Redis with Docker
```bash
docker-compose up -d
docker ps  # Should show llm-redis running
```

### Issue: No Celery workers

**Solution**: Check worker is running
```bash
celery -A phase2.celery_config inspect active
```

## 📝 Important Notes

1. **Always run commands from project root** (where start.bat is located)
2. Use `phase2.celery_config` not just `celery_config`
3. Use `python -m phase2.api` not just `python api.py`
4. The __init__.py files in phase1/ and phase2/ enable module imports

## 🔧 Project Structure

```
LLM_Fine-Tuning_Platform/  ← Run commands from here!
├── phase1/
│   ├── __init__.py        ← Makes phase1 a module
│   ├── train.py
│   ├── config.py
│   └── ...
├── phase2/
│   ├── __init__.py        ← Makes phase2 a module
│   ├── api.py
│   ├── celery_config.py
│   ├── celery_worker.py
│   └── ...
├── run_worker.bat         ← Helper to run worker
├── run_api.bat            ← Helper to run API
└── start.bat              ← Automated startup
```

## 📚 Next Steps

Once everything is running:
1. Upload a dataset: `POST http://localhost:8000/upload`
2. Start training: `POST http://localhost:8000/train`
3. Check status: `GET http://localhost:8000/status/{job_id}`

See PHASE2_GUIDE.md for detailed API documentation.
