"""
Train.py - Core LLM Fine-Tuning Script with Unsloth
Accepts a JSONL dataset and outputs a fine-tuned LoRA adapter
"""

import argparse
from pathlib import Path
from typing import Optional
import torch
from datasets import load_dataset
from transformers import TrainingArguments
from trl import SFTTrainer
from unsloth import FastLanguageModel
from dotenv import load_dotenv

from data_formatter import DataFormatter
from config import TrainingConfig


class LLMTrainer:
    """Handles the complete fine-tuning pipeline with Unsloth"""
    
    def __init__(self, config: TrainingConfig):
        self.config = config
        self.model = None
        self.tokenizer = None
        
    def load_model(self):
        """Load base model and tokenizer with Unsloth optimizations"""
        print(f"📦 Loading model: {self.config.base_model}")
        
        self.model, self.tokenizer = FastLanguageModel.from_pretrained(
            model_name=self.config.base_model,
            max_seq_length=self.config.max_seq_length,
            dtype=None,  # Auto-detect
            load_in_4bit=self.config.load_in_4bit,
        )
        
        print("✓ Model loaded successfully")
        
    def setup_lora(self):
        """Configure LoRA (Low-Rank Adaptation) for efficient fine-tuning"""
        print("🔧 Setting up LoRA adapters...")
        
        self.model = FastLanguageModel.get_peft_model(
            self.model,
            r=self.config.lora_r,
            target_modules=self.config.target_modules,
            lora_alpha=self.config.lora_alpha,
            lora_dropout=self.config.lora_dropout,
            bias="none",
            use_gradient_checkpointing="unsloth",
            random_state=3407,
            use_rslora=False,
            loftq_config=None,
        )
        
        # Print trainable parameters
        trainable_params = sum(p.numel() for p in self.model.parameters() if p.requires_grad)
        total_params = sum(p.numel() for p in self.model.parameters())
        print(f"✓ LoRA configured: {trainable_params:,} / {total_params:,} parameters trainable "
              f"({100 * trainable_params / total_params:.2f}%)")
    
    def load_and_prepare_data(
        self,
        data_path: str,
        format_type: str = "alpaca"
    ):
        """Load and format training data"""
        print(f"📁 Loading dataset from: {data_path}")
        
        # Check if data needs formatting
        if not Path(data_path).exists():
            raise FileNotFoundError(f"Dataset not found: {data_path}")
        
        # Load the dataset
        dataset = load_dataset("json", data_files=data_path, split="train")
        
        # Check if data is already formatted (has 'text' field)
        if "text" not in dataset.column_names:
            print("⚠️  Data not formatted. Formatting now...")
            
            # Format the data
            formatted_data = DataFormatter.load_and_format_jsonl(
                data_path,
                format_type=format_type
            )
            
            # Save formatted data temporarily
            temp_path = Path(data_path).parent / "formatted_temp.jsonl"
            DataFormatter.save_formatted_data(formatted_data, str(temp_path))
            
            # Reload formatted dataset
            dataset = load_dataset("json", data_files=str(temp_path), split="train")
            temp_path.unlink()  # Clean up temp file
        
        print(f"✓ Dataset loaded: {len(dataset)} examples")
        return dataset
    
    def train(
        self,
        dataset,
        output_dir: Optional[str] = None
    ):
        """Execute the fine-tuning process"""
        if output_dir is None:
            output_dir = self.config.output_dir
        
        # Create output directory
        Path(output_dir).mkdir(parents=True, exist_ok=True)
        
        print("🚀 Starting training...")
        print(f"   Output: {output_dir}")
        
        # Define training arguments
        training_args = TrainingArguments(
            output_dir=output_dir,
            per_device_train_batch_size=self.config.batch_size,
            gradient_accumulation_steps=self.config.gradient_accumulation_steps,
            warmup_steps=self.config.warmup_steps,
            max_steps=self.config.max_steps,
            learning_rate=self.config.learning_rate,
            fp16=not torch.cuda.is_bf16_supported(),
            bf16=torch.cuda.is_bf16_supported(),
            logging_steps=self.config.logging_steps,
            optim=self.config.optim,
            weight_decay=self.config.weight_decay,
            lr_scheduler_type=self.config.lr_scheduler_type,
            seed=3407,
            save_steps=self.config.save_steps,
            save_total_limit=2,
            report_to="none",  # Disable wandb/tensorboard for now
        )
        
        # Initialize trainer
        trainer = SFTTrainer(
            model=self.model,
            tokenizer=self.tokenizer,
            train_dataset=dataset,
            dataset_text_field=self.config.dataset_text_field,
            max_seq_length=self.config.max_seq_length,
            dataset_num_proc=2,
            packing=self.config.packing,
            args=training_args,
        )
        
        # Train the model
        trainer.train()
        
        print("✓ Training completed!")
        
        return trainer
    
    def save_adapter(self, output_dir: str):
        """Save the fine-tuned LoRA adapter"""
        print(f"💾 Saving adapter to: {output_dir}")
        
        # Save LoRA adapter
        self.model.save_pretrained(output_dir)
        self.tokenizer.save_pretrained(output_dir)
        
        print("✓ Adapter saved successfully!")
        print(f"   Location: {output_dir}")
        print("   Files: adapter_config.json, adapter_model.safetensors")
    
    def save_merged_model(self, output_dir: str, quantization: Optional[str] = None):
        """
        Save the fully merged model (optional)
        
        Args:
            output_dir: Where to save the merged model
            quantization: Optional quantization ('q4_k_m', 'q8_0', etc.) for GGUF
        """
        print(f"💾 Saving merged model to: {output_dir}")
        
        if quantization:
            # Save as quantized GGUF
            self.model.save_pretrained_gguf(
                output_dir,
                self.tokenizer,
                quantization_method=quantization
            )
            print(f"✓ Merged & quantized model saved ({quantization})")
        else:
            # Save full precision merged model
            self.model.save_pretrained_merged(
                output_dir,
                self.tokenizer,
                save_method="merged_16bit"
            )
            print("✓ Merged model saved (16-bit)")


def main():
    """Main training pipeline"""
    parser = argparse.ArgumentParser(
        description="Fine-tune LLM with Unsloth"
    )
    
    # Required arguments
    parser.add_argument(
        "--data",
        required=True,
        help="Path to training data (JSONL format)"
    )
    
    # Optional arguments
    parser.add_argument(
        "--output",
        default="./outputs/adapter",
        help="Output directory for adapter"
    )
    parser.add_argument(
        "--model",
        default="unsloth/llama-3-8b-bnb-4bit",
        help="Base model to fine-tune"
    )
    parser.add_argument(
        "--format",
        default="alpaca",
        choices=["alpaca", "chatml"],
        help="Data format"
    )
    parser.add_argument(
        "--max-steps",
        type=int,
        default=60,
        help="Maximum training steps"
    )
    parser.add_argument(
        "--batch-size",
        type=int,
        default=2,
        help="Training batch size"
    )
    parser.add_argument(
        "--learning-rate",
        type=float,
        default=2e-4,
        help="Learning rate"
    )
    parser.add_argument(
        "--lora-r",
        type=int,
        default=16,
        help="LoRA rank"
    )
    parser.add_argument(
        "--save-merged",
        action="store_true",
        help="Also save merged model (not just adapter)"
    )
    parser.add_argument(
        "--quantize",
        choices=["q4_k_m", "q8_0", "f16"],
        help="Quantization format for merged model"
    )
    
    args = parser.parse_args()
    
    # Load environment variables
    load_dotenv()
    
    # Create configuration
    config = TrainingConfig(
        base_model=args.model,
        max_steps=args.max_steps,
        batch_size=args.batch_size,
        learning_rate=args.learning_rate,
        lora_r=args.lora_r,
        output_dir=args.output,
    )
    
    # Initialize trainer
    print("=" * 60)
    print("🔥 Unsloth LLM Fine-Tuning Pipeline")
    print("=" * 60)
    
    trainer = LLMTrainer(config)
    
    # Load model
    trainer.load_model()
    
    # Setup LoRA
    trainer.setup_lora()
    
    # Load and prepare data
    dataset = trainer.load_and_prepare_data(args.data, args.format)
    
    # Train
    trainer.train(dataset, args.output)
    
    # Save adapter
    adapter_dir = Path(args.output) / "adapter"
    adapter_dir.mkdir(parents=True, exist_ok=True)
    trainer.save_adapter(str(adapter_dir))
    
    # Optionally save merged model
    if args.save_merged:
        merged_dir = Path(args.output) / "merged"
        merged_dir.mkdir(parents=True, exist_ok=True)
        trainer.save_merged_model(str(merged_dir), args.quantize)
    
    print("\n" + "=" * 60)
    print("✅ Fine-tuning complete!")
    print("=" * 60)
    print(f"📁 Adapter location: {adapter_dir}")
    if args.save_merged:
        print(f"📁 Merged model: {merged_dir}")


if __name__ == "__main__":
    main()
