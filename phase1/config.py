"""
Training Configuration for LLM Fine-Tuning
"""

from dataclasses import dataclass


@dataclass
class TrainingConfig:
    """Configuration for model fine-tuning"""
    
    # Model
    base_model: str = "unsloth/llama-3-8b-bnb-4bit"
    max_seq_length: int = 2048
    load_in_4bit: bool = True
    
    # LoRA Configuration
    lora_r: int = 16
    lora_alpha: int = 16
    lora_dropout: float = 0.0
    target_modules: list = None
    
    # Training Hyperparameters
    batch_size: int = 2
    gradient_accumulation_steps: int = 4
    warmup_steps: int = 5
    max_steps: int = 60
    learning_rate: float = 2e-4
    fp16: bool = False
    bf16: bool = True
    
    # Optimizer
    optim: str = "adamw_8bit"
    weight_decay: float = 0.01
    lr_scheduler_type: str = "linear"
    
    # Logging
    logging_steps: int = 1
    
    # Output
    output_dir: str = "./outputs"
    logging_dir: str = "./logs"
    save_steps: int = 25
    
    # Data
    dataset_text_field: str = "text"
    packing: bool = False
    
    def __post_init__(self):
        if self.target_modules is None:
            # Default target modules for Llama
            self.target_modules = [
                "q_proj", "k_proj", "v_proj", "o_proj",
                "gate_proj", "up_proj", "down_proj"
            ]
