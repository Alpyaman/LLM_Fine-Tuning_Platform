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

### 🔄 Phase 2-5: Coming Soon
- [ ] FastAPI Backend
- [ ] Redis + Celery Job Queue
- [ ] Next.js Frontend
- [ ] Cloud Deployment (RunPod/Lambda Labs)

## 🚀 Quick Start (Phase 1)

### Prerequisites
- Python 3.10+
- CUDA-capable GPU (or use Google Colab)
- Hugging Face account

### Installation

```bash
# Clone the repository
git clone <your-repo-url>
cd LLM_Fine-Tuning_Platform

# Create virtual environment
python -m venv venv
venv\Scripts\activate  # Windows
# source venv/bin/activate  # Linux/Mac

# Install dependencies
pip install -r requirements.txt

# Setup environment
copy .env.example .env
# Edit .env and add your HF_TOKEN
```

### Train Your First Model

```bash
# Using example data
python train.py --data example_data.jsonl --max-steps 60

# Custom training
python train.py \
    --data your_data.jsonl \
    --output ./outputs/my_model \
    --max-steps 100 \
    --batch-size 2 \
    --save-merged
```

## 📁 Project Structure

```
LLM_Fine-Tuning_Platform/
├── train.py              # Main training script
├── data_formatter.py     # Data formatting utilities
├── config.py             # Training configuration
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

- **⚡ Unsloth**: 2-5x faster than standard fine-tuning
- **💾 Memory Efficient**: 4-bit quantization for smaller GPUs
- **🎛️ LoRA Adapters**: Parameter-efficient fine-tuning
- **📝 Auto-formatting**: Converts raw data to instruction format
- **🔧 Configurable**: Easy hyperparameter tuning
- **💼 Production-ready**: Designed for scale

## 📖 Documentation

- [Phase 1 Setup Guide](PHASE1_GUIDE.md) - Complete Phase 1 walkthrough
- [Data Formatting](data_formatter.py) - How to prepare your data
- [Configuration](config.py) - Training parameters explained

## 🛠️ Tech Stack

**Phase 1 (Current):**
- Unsloth - Fast LLM fine-tuning
- PyTorch - Deep learning framework
- Transformers - HuggingFace models
- TRL - Transformer Reinforcement Learning
- PEFT - Parameter-Efficient Fine-Tuning

**Coming Soon:**
- FastAPI - Backend API
- Redis - Message broker
- Celery - Task queue
- Next.js - Frontend dashboard
- AWS S3 - Model storage
- RunPod/Lambda Labs - GPU infrastructure

## 🎓 Usage Examples

### Basic Training
```bash
python train.py --data my_data.jsonl
```

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

**Status**: 🟢 Phase 1 Complete | Ready for Phase 2

Built with ❤️ for the AI community