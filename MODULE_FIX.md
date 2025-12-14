# Module Structure Fix - Phase 2

## ✅ What Was Fixed

The project was restructured into `phase1/` and `phase2/` folders, but Python couldn't find the modules when running Celery. Here's what we fixed:

### 1. Added Python Path Configuration

All phase2 files now add the parent directory to `sys.path`:

```python
import sys
from pathlib import Path

parent_dir = Path(__file__).resolve().parent.parent
if str(parent_dir) not in sys.path:
    sys.path.insert(0, str(parent_dir))
```

### 2. Updated All Import Statements

Changed from relative imports to absolute imports:

**Before:**
```python
from celery_config import celery_app
from storage import get_storage
from phase1.train import LLMTrainer
```

**After:**
```python
from phase2.celery_config import celery_app
from phase2.storage import get_storage
from phase1.train import LLMTrainer
```

### 3. Updated Celery Task Names

Changed task names to include module path:

**Before:**
```python
@celery_app.task(name="celery_worker.train_model")
celery_app.send_task("celery_worker.train_model", ...)
```

**After:**
```python
@celery_app.task(name="phase2.celery_worker.train_model")
celery_app.send_task("phase2.celery_worker.train_model", ...)
```

### 4. Created Helper Scripts

Created scripts to run from project root:

- `run_worker.bat` / `run_worker.sh` - Start Celery worker
- `run_api.bat` / `run_api.sh` - Start FastAPI server
- Updated `start.bat` with correct commands

### 5. Updated Command Instructions

**Old way (from phase2 folder):**
```bash
cd phase2
celery -A celery_config worker ...  # ❌ Doesn't work
```

**New way (from project root):**
```bash
cd LLM_Fine-Tuning_Platform
celery -A phase2.celery_config worker ...  # ✅ Works!
```

## 📁 File Changes

### Modified Files:
- `phase2/celery_config.py` - Added sys.path, updated include list
- `phase2/celery_worker.py` - Added sys.path, updated imports and task names
- `phase2/api.py` - Added sys.path, updated imports and task references
- `start.bat` - Updated with correct commands

### New Files:
- `run_worker.bat` / `run_worker.sh` - Helper to start worker
- `run_api.bat` / `run_api.sh` - Helper to start API
- `QUICKSTART.md` - Quick reference guide

## 🚀 How to Run Now

### Windows:

```bash
# Terminal 1: Start Redis
docker-compose up -d

# Terminal 2: Start Worker
run_worker.bat
# OR
celery -A phase2.celery_config worker --loglevel=info -Q training -P solo

# Terminal 3: Start API
run_api.bat
# OR
python -m phase2.api
```

### Linux/Mac:

```bash
# Terminal 1: Start Redis
docker-compose up -d

# Terminal 2: Start Worker
./run_worker.sh
# OR
celery -A phase2.celery_config worker --loglevel=info -Q training

# Terminal 3: Start API
./run_api.sh
# OR
python -m phase2.api
```

## ✅ Verification

After starting all services:

1. **Check Health:** http://localhost:8000/health
2. **Check Docs:** http://localhost:8000/docs
3. **Check Flower:** http://localhost:5555
4. **Run Tests:** `python tests/test_api.py`

## 💡 Key Takeaways

1. **Always run from project root** - Commands must be executed from the main project directory
2. **Use module paths** - Reference modules as `phase2.module_name` not just `module_name`
3. **Helper scripts** - Use the provided batch files for easier startup
4. **__init__.py files** - These make phase1/ and phase2/ proper Python packages

## 🐛 Troubleshooting

### Still getting ModuleNotFoundError?

1. Check current directory:
   ```bash
   pwd  # or cd (Windows)
   # Should be: .../LLM_Fine-Tuning_Platform
   ```

2. Verify __init__.py files exist:
   ```bash
   ls phase1/__init__.py
   ls phase2/__init__.py
   ```

3. Make sure you're using phase2.celery_config:
   ```bash
   celery -A phase2.celery_config worker ...
   # NOT: celery -A celery_config worker ...
   ```

### Worker not picking up tasks?

Check the task is registered:
```bash
celery -A phase2.celery_config inspect registered
```

Should show: `phase2.celery_worker.train_model`

## 📚 References

- [QUICKSTART.md](QUICKSTART.md) - Quick reference
- [PHASE2_GUIDE.md](phase2/PHASE2_GUIDE.md) - Detailed Phase 2 guide
- [Python Packages](https://docs.python.org/3/tutorial/modules.html#packages) - Official Python docs
