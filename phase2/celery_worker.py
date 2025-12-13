"""
Celery Worker - Wraps Phase 1 training script as async task
"""

import os
import traceback
from pathlib import Path
from datetime import datetime
from celery import Task
from phase2.celery_config import celery_app

# Import Phase 1 training components
from phase1.train import LLMTrainer
from phase1.config import TrainingConfig


class TrainingTask(Task):
    """Custom task class with callbacks"""
    
    def on_failure(self, exc, task_id, args, kwargs, einfo):
        """Handle task failure"""
        print(f"❌ Task {task_id} failed: {exc}")
        
    def on_success(self, retval, task_id, args, kwargs):
        """Handle task success"""
        print(f"✅ Task {task_id} completed successfully")


@celery_app.task(bind=True, base=TrainingTask, name="celery_worker.train_model")
def train_model(
    self,
    data_path: str,
    output_dir: str,
    config_dict: dict
) -> dict:
    """
    Celery task to train a model
    
    Args:
        self: Task instance (bound)
        data_path: Path to training data JSONL
        output_dir: Output directory for model
        config_dict: Training configuration as dictionary
        
    Returns:
        Dictionary with training results
    """
    task_id = self.request.id
    
    try:
        # Update state to STARTED
        self.update_state(
            state="STARTED",
            meta={
                "status": "Initializing training...",
                "progress": 0,
                "current_step": 0,
                "total_steps": config_dict.get("max_steps", 60)
            }
        )
        
        print(f"\n{'='*60}")
        print(f"🔥 Starting Training Task: {task_id}")
        print(f"{'='*60}")
        print(f"📊 Data: {data_path}")
        print(f"📁 Output: {output_dir}")
        print(f"⚙️ Config: {config_dict}")
        print(f"{'='*60}\n")
        
        # Validate data file exists
        if not os.path.exists(data_path):
            raise FileNotFoundError(f"Training data not found: {data_path}")
        
        # Create configuration
        config = TrainingConfig(**config_dict)
        config.output_dir = output_dir
        
        # Update state
        self.update_state(
            state="PROGRESS",
            meta={
                "status": "Loading model...",
                "progress": 10,
                "current_step": 0,
                "total_steps": config.max_steps
            }
        )
        
        # Initialize trainer
        trainer = LLMTrainer(config)
        
        # Load model
        trainer.load_model()
        
        self.update_state(
            state="PROGRESS",
            meta={
                "status": "Setting up LoRA adapters...",
                "progress": 20,
                "current_step": 0,
                "total_steps": config.max_steps
            }
        )
        
        # Setup LoRA
        trainer.setup_lora()
        
        self.update_state(
            state="PROGRESS",
            meta={
                "status": "Loading dataset...",
                "progress": 30,
                "current_step": 0,
                "total_steps": config.max_steps
            }
        )
        
        # Load and prepare data
        dataset = trainer.load_and_prepare_data(data_path, format_type="alpaca")
        
        self.update_state(
            state="PROGRESS",
            meta={
                "status": "Training in progress...",
                "progress": 40,
                "current_step": 0,
                "total_steps": config.max_steps
            }
        )
        
        # Train (this is the long-running part)
        start_time = datetime.now()
        trainer.train(dataset, output_dir)
        end_time = datetime.now()
        training_duration = (end_time - start_time).total_seconds()
        
        self.update_state(
            state="PROGRESS",
            meta={
                "status": "Saving adapter...",
                "progress": 90,
                "current_step": config.max_steps,
                "total_steps": config.max_steps
            }
        )
        
        # Save adapter
        adapter_dir = Path(output_dir) / "adapter"
        adapter_dir.mkdir(parents=True, exist_ok=True)
        trainer.save_adapter(str(adapter_dir))
        
        # Prepare result
        result = {
            "status": "completed",
            "task_id": task_id,
            "output_dir": output_dir,
            "adapter_dir": str(adapter_dir),
            "training_duration_seconds": training_duration,
            "dataset_size": len(dataset),
            "max_steps": config.max_steps,
            "completed_at": datetime.now().isoformat(),
            "model": config.base_model,
        }
        
        print(f"\n{'='*60}")
        print(f"✅ Training Task Completed: {task_id}")
        print(f"⏱️  Duration: {training_duration:.2f}s")
        print(f"📁 Output: {adapter_dir}")
        print(f"{'='*60}\n")
        
        return result
        
    except Exception as e:
        error_msg = str(e)
        error_trace = traceback.format_exc()
        
        print(f"\n{'='*60}")
        print(f"❌ Training Task Failed: {task_id}")
        print(f"Error: {error_msg}")
        print(f"{'='*60}")
        print(error_trace)
        print(f"{'='*60}\n")
        
        # Update state to FAILURE with error details
        self.update_state(
            state="FAILURE",
            meta={
                "status": "failed",
                "error": error_msg,
                "traceback": error_trace,
                "task_id": task_id
            }
        )
        
        raise


@celery_app.task(name="celery_worker.health_check")
def health_check() -> dict:
    """Simple health check task"""
    return {
        "status": "healthy",
        "timestamp": datetime.now().isoformat()
    }
