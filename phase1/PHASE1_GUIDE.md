# Phase 1: Core Engine - Setup Guide

## 🚀 Quick Start

### 1. Install Dependencies

First, create a virtual environment (recommended):

```bash
python -m venv venv
venv\Scripts\activate  # Windows
# source venv/bin/activate  # Linux/Mac
```

Install required packages:

```bash
pip install -r requirements.txt
```

**Note:** Unsloth requires a CUDA-capable GPU. For local testing, you can use Google Colab with a T4 GPU.

### 2. Setup Environment

Copy the example environment file:

```bash
copy .env.example .env
```

Edit `.env` and add your Hugging Face token (get one from https://huggingface.co/settings/tokens):

```
HF_TOKEN=hf_your_token_here
```

### 3. Run Training

Basic usage with example data:

```bash
python train.py --data example_data.jsonl --max-steps 60
```

Advanced usage with custom parameters:

```bash
python train.py \
    --data my_dataset.jsonl \
    --output ./outputs/my_model \
    --model unsloth/llama-3-8b-bnb-4bit \
    --format alpaca \
    --max-steps 100 \
    --batch-size 2 \
    --learning-rate 2e-4 \
    --lora-r 16 \
    --save-merged
```

## 📊 Data Format

Your JSONL file should contain entries like:

```json
{"instruction": "Your instruction here", "output": "Expected response", "input": "Optional context"}
{"instruction": "Another instruction", "output": "Another response", "input": ""}
```

## 🔧 Components

### `train.py`
Main training script that orchestrates the entire fine-tuning pipeline:
- Loads Unsloth-optimized model
- Configures LoRA adapters
- Trains using SFTTrainer
- Saves adapter files

### `data_formatter.py`
Utility for converting raw data to instruction format:
- Supports Alpaca format
- Supports ChatML format
- Can be used standalone:

```bash
python data_formatter.py --input raw_data.jsonl --output formatted_data.jsonl --format alpaca
```

### `config.py`
Configuration dataclass with all hyperparameters:
- Model settings
- LoRA configuration
- Training parameters
- Can be easily modified for different experiments

## 📁 Output Structure

After training, you'll get:

```
outputs/
├── adapter/
│   ├── adapter_config.json
│   ├── adapter_model.safetensors
│   └── tokenizer files...
└── merged/  (if --save-merged flag used)
    └── merged model files...
```

## 🎯 Key Features

✅ **Unsloth Integration** - 2-5x faster training
✅ **4-bit Quantization** - Train on smaller GPUs
✅ **LoRA Adapters** - Efficient parameter updates
✅ **Multiple Formats** - Alpaca and ChatML support
✅ **Auto-formatting** - Handles raw data conversion
✅ **Flexible Configuration** - Easy parameter tuning

## 💡 Tips

1. **Start Small**: Test with `--max-steps 60` first
2. **Monitor GPU**: Use `nvidia-smi` to check memory usage
3. **Batch Size**: Reduce if you get OOM errors
4. **Learning Rate**: 2e-4 is good for most cases
5. **LoRA Rank**: Higher rank = more trainable parameters (but more memory)

## 🐛 Troubleshooting

**CUDA Out of Memory:**
- Reduce `--batch-size` to 1
- Reduce `max_seq_length` in config.py
- Enable gradient checkpointing (already default)

**Import Errors:**
- Make sure you're in the virtual environment
- Try `pip install --upgrade unsloth`

**Model Download Issues:**
- Check your HF_TOKEN in .env
- Ensure you have internet connection
- Some models require accepting license on HuggingFace

## 📈 Next Steps

Phase 1 Complete! You now have:
- ✅ Working training pipeline
- ✅ Data formatting utilities
- ✅ LoRA adapter outputs

Ready for **Phase 2: FastAPI Backend** to expose this as an API!
