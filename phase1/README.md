# Phase 1 - Core Training Engine

This module contains the core LLM fine-tuning functionality.

## Files

- `train.py` - Main training script with LLMTrainer class
- `config.py` - Training configuration dataclass
- `data_formatter.py` - Data formatting utilities
- `inference.py` - Model inference script (if in phase1)
- `Colab_Fine_Tuning.ipynb` - Google Colab notebook

## Usage

### From Project Root:

```python
from phase1.train import LLMTrainer
from phase1.config import TrainingConfig
from phase1.data_formatter import DataFormatter
```

### Direct Execution:

```bash
# From project root
python -m phase1.train --data example_data.jsonl
```

## Documentation

See [PHASE1_GUIDE.md](PHASE1_GUIDE.md) for detailed setup and usage instructions.
