# 🔥 Serverless LLM Fine-Tuning Platform

A modern, production-ready platform for fine-tuning large language models using Unsloth for 2-5x faster training.

## 🏗️ Architecture

**The Decoupled Trainer System:**

- **Frontend**: Next.js dashboard for uploads and monitoring
- **Backend**: FastAPI for API management and auth
- **Queue**: Redis + Celery for job orchestration
- **Engine**: Unsloth (GPU workers) for efficient training
- **Infrastructure**: RunPod/Lambda Labs + AWS S3

## 📋 Project Status

### ✅ Phase 1: Core Engine (COMPLETED)
- [x] Unsloth integration for fast fine-tuning
- [x] Data formatter (Alpaca & ChatML)
- [x] SFTTrainer with LoRA adapters
- [x] Local training pipeline
- [x] Model export (.safetensors)

### ✅ Phase 2: Async Backend (COMPLETED)
- [x] FastAPI REST API
- [x] Redis + Celery job queue
- [x] File upload handling
- [x] Job status tracking
- [x] Worker monitoring (Flower)
- [x] Local & S3 storage support

### 🔄 Phase 3-5: Coming Soon
- [ ] Next.js Frontend Dashboard
- [ ] Authentication & User Management
- [ ] Cloud Deployment (RunPod/Lambda Labs)

## 🚀 Quick Start

### Prerequisites
- Python 3.10+
- CUDA-capable GPU (or use Google Colab for Phase 1)
- Docker Desktop (for Phase 2)
- Hugging Face account

### Phase 1: Local Training

```bash
# Install dependencies
pip install -r requirements.txt

# Setup environment
copy .env.example .env
# Edit .env and add your HF_TOKEN

# Train locally
python train.py --data example_data.jsonl --max-steps 60
```

See [PHASE1_GUIDE.md](PHASE1_GUIDE.md) for details.

### Phase 2: API Server

```bash
# Start services (Windows)
start.bat

# Or manually:
# 1. Start Redis
docker-compose up -d

# 2. Start Celery Worker
celery -A celery_config worker --loglevel=info -Q training -P solo

# 3. Start API Server
python api.py
```

**Test the API:**
```bash
python test_api.py
```

See Phase 1 - Core Engine
│   ├── train.py              # Main training script
│   ├── inference.py          # Model inference
│   ├── data_formatter.py     # Data formatting
│   ├── config.py             # Training configuration
│   ├── PHASE1_GUIDE.md       # Phase 1 guide
│   └── Colab_Fine_Tuning.ipynb
│
├── Phase 2 - Async Backend
│   ├── api.py                # FastAPI application
│   ├── celery_config.py      # Celery configuration
│   ├── celery_worker.py      # Background tasks
│   ├── storage.py            # Storage utilities
│   ├── docker-compose.yml    # Redis + Flower
│   ├── PHASE2_GUIDE.md       # Phase 2 guide
│   ├── test_api.py           # API test suite
│   └── start.bat / start.sh  # Startup scripts
│
├── requirements.txt      # All dependencies
├── example_data.jsonl    # Sample dataset
├── .env.example          # Environment template
└── storage/              # Data storage (created)
    ├── datasets/         # Uploaded datasets
    └── models/           # Trained modelation
├── requirements.txt      # Python dependencies
├── example_data.jsonl    # Sample dataset
├── PHASE1_GUIDE.md       # Detailed Phase 1 guide
├── .env.example          # Environment variables template
└── outputs/              # Training outputs (created)
    └── adapter/          # LoRA adapter files
```

## 📊 Data Format

Your training data should be in JSONL format:

```json
{"instruction": "What is AI?", "output": "AI is...", "input": ""}
{"instruction": "Translate to Spanish", "output": "Hola", "input": "Hello"}
```

## 🎯 Key Features

- **⚡ Unsl- Training Engine:**
- Unsloth - Fast LLM fine-tuning
- PyTorch - Deep learning framework
- Transformers - HuggingFace models
- TRL - Transformer Reinforcement Learning
- PEFT - Parameter-Efficient Fine-Tuning

**Phase 2 - Backend API:**
- FastAPI - REST API framework
- Redis - Message broker
- Celery - Distributed task queue
- Flower - Task monitoring UI
- Pydantic - Data validation
- Docker - Containerization

**Coming Soon:**ata_formatter.py) - How to prepare your data
- [Configuration](config.py) - Training parameters explained
Phase 1: Local Training

```bash
# Basic training
python train.py --data my_data.jsonl --max-steps 60

# Advanced training
python train.py \
    --data dataset.jsonl \
    --model unsloth/llama-3-8b-bnb-4bit \
    --max-steps 200 \
    --batch-size 4 \
    --learning-rate 3e-4 \
    --lora-r 32 \
    --save-merged

# Test model
python inference.py --adapter adapter.zip
```

### Phase 2: API Usage

```bash
# Upload dataset
curl -X POST "http://localhost:8000/upload" \
  -F "file=@my_data.jsonl"

# Start training
curl -X POST "http://localhost:8000/train" \
  -H "Content-Type: application/json" \
  -d '{
    "dataset_filename": "my_data.jsonl",
    "config": {
      "max_steps": 100,
      "batch_size": 2,
      "learning_rate": 0.0002
    }
  }'

# Check status
curl "http://localhost:8000/status/{job_id}"
### Advanced Training
```bash
python train.py \
    --data dataset.jsonl \
    --model unsloth/llama-3-8b-bnb-4bit \
    --format alpaca \
    --max-steps 200 \
    --batch-size 4 \
    --learning-rate 3e-4 \
    --lora-r 32 \
    --save-merged \
    --quantize q4_k_m
```

### Format Data
```bash
python data_formatter.py \
    --input raw_data.jsonl \
    --output formatted_data.jsonl \
    --format alpaca
```

## 🐛 Troubleshooting

**Out of Memory?**
- Reduce `--batch-size` to 1
- Lower `max_seq_length` in config.py

**Model Not Downloading?**
- Check `HF_TOKEN` in `.env`
- Accept model license on HuggingFace

**Import Errors?**
- Activate virtual environment
- Run `pip install --upgrade unsloth`

## 🤝 Contributing

This is a learning project following a 5-phase roadmap. Contributions welcome after Phase 5 completion!

## 📝 License

MIT License - see [LICENSE](LICENSE) file

## 🙏 Credits

- **Unsloth** - For blazing fast fine-tuning
- **HuggingFace** - For transformers and model hub
- **RunPod/Lambda Labs** - GPU infrastructure partners

---

**Status**: 🟢 Phase 2 Complete | Ready for Phase 3

Built with ❤️ for the AI community