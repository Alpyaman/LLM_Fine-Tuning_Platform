"""
FastAPI Application - LLM Fine-Tuning Platform Backend
Provides REST API for managing training jobs
"""

import os
import sys
import uuid
from datetime import datetime
from typing import Optional, List
from pathlib import Path

# Add parent directory to path to enable cross-phase imports
parent_dir = Path(__file__).resolve().parent.parent
if str(parent_dir) not in sys.path:
    sys.path.insert(0, str(parent_dir))

from fastapi import FastAPI, File, UploadFile, HTTPException, BackgroundTasks
from fastapi.responses import JSONResponse
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field
from pydantic_settings import BaseSettings

from celery.result import AsyncResult
from phase2.celery_config import celery_app
from phase2.storage import get_storage


# Configuration
class Settings(BaseSettings):
    """Application settings"""
    app_name: str = "LLM Fine-Tuning Platform"
    app_version: str = "2.0.0"
    debug: bool = True
    
    # Storage
    storage_type: str = "local"  # 'local' or 's3'
    storage_base_dir: str = "./storage"
    s3_bucket: Optional[str] = None
    
    # Redis/Celery
    redis_host: str = "localhost"
    redis_port: int = 6379
    redis_db: int = 0
    
    # Model defaults
    default_model: str = "unsloth/llama-3-8b-bnb-4bit"
    default_max_steps: int = 60
    default_batch_size: int = 2
    default_learning_rate: float = 2e-4
    
    class Config:
        env_file = ".env"


settings = Settings()

# Initialize FastAPI app
app = FastAPI(
    title=settings.app_name,
    version=settings.app_version,
    description="API for fine-tuning LLMs with Unsloth"
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialize storage
storage = get_storage(settings.storage_type, base_dir=settings.storage_base_dir)


# Pydantic models
class TrainingConfig(BaseModel):
    """Training configuration request"""
    base_model: str = Field(default="unsloth/llama-3-8b-bnb-4bit", description="Base model to fine-tune")
    max_steps: int = Field(default=60, ge=1, le=10000, description="Maximum training steps")
    batch_size: int = Field(default=2, ge=1, le=32, description="Batch size")
    learning_rate: float = Field(default=2e-4, gt=0, description="Learning rate")
    lora_r: int = Field(default=16, ge=4, le=64, description="LoRA rank")
    lora_alpha: int = Field(default=16, ge=4, le=64, description="LoRA alpha")
    max_seq_length: int = Field(default=2048, description="Maximum sequence length")


class TrainRequest(BaseModel):
    """Training job request"""
    dataset_filename: str = Field(..., description="Filename of uploaded dataset")
    config: Optional[TrainingConfig] = Field(default=None, description="Training configuration")
    job_name: Optional[str] = Field(default=None, description="Optional job name")


class JobResponse(BaseModel):
    """Job creation response"""
    job_id: str
    status: str
    message: str
    created_at: str


class JobStatus(BaseModel):
    """Job status response"""
    job_id: str
    status: str
    progress: Optional[int] = None
    current_step: Optional[int] = None
    total_steps: Optional[int] = None
    result: Optional[dict] = None
    error: Optional[str] = None


class HealthResponse(BaseModel):
    """Health check response"""
    status: str
    app: str
    version: str
    redis_connected: bool
    celery_workers: int


# API Endpoints

@app.get("/", response_model=dict)
async def root():
    """Root endpoint"""
    return {
        "message": f"Welcome to {settings.app_name}",
        "version": settings.app_version,
        "docs": "/docs",
        "endpoints": {
            "upload": "POST /upload",
            "train": "POST /train",
            "status": "GET /status/{job_id}",
            "jobs": "GET /jobs",
            "health": "GET /health"
        }
    }


@app.get("/health", response_model=HealthResponse)
async def health_check():
    """Health check endpoint"""
    # Check Redis connection
    try:
        celery_app.backend.client.ping()
        redis_connected = True
    except Exception as e:
        print(f"Redis connection error: {e}")
        redis_connected = False
    
    # Check active workers
    try:
        inspect = celery_app.control.inspect()
        active_workers = len(inspect.active() or {})
    except Exception as e:
        print(f"Celery inspect error: {e}")
        active_workers = 0
    
    return HealthResponse(
        status="healthy" if redis_connected else "degraded",
        app=settings.app_name,
        version=settings.app_version,
        redis_connected=redis_connected,
        celery_workers=active_workers
    )


@app.post("/upload", response_model=dict)
async def upload_dataset(
    file: UploadFile = File(...),
    job_id: Optional[str] = None
):
    """
    Upload training dataset
    
    Accepts JSONL files with format:
    {"instruction": "...", "output": "...", "input": "..."}
    """
    # Validate file type
    if not file.filename.endswith(('.jsonl', '.json')):
        raise HTTPException(
            status_code=400,
            detail="Invalid file format. Only .jsonl and .json files are accepted."
        )
    
    # Generate job ID if not provided
    if not job_id:
        job_id = str(uuid.uuid4())
    
    try:
        # Read file content
        content = await file.read()
        
        # Save to storage
        file_path = await storage.save_dataset(content, file.filename, job_id)
        
        return {
            "status": "success",
            "message": "Dataset uploaded successfully",
            "job_id": job_id,
            "filename": file.filename,
            "file_path": file_path,
            "file_size": len(content),
            "uploaded_at": datetime.now().isoformat()
        }
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Upload failed: {str(e)}")


@app.post("/train", response_model=JobResponse)
async def start_training(request: TrainRequest):
    """
    Start a training job
    
    Returns job_id for tracking progress
    """
    # Generate job ID
    job_id = str(uuid.uuid4())
    
    # Get dataset path
    dataset_path = storage.get_dataset_path(job_id, request.dataset_filename)
    
    # Validate dataset exists
    if not os.path.exists(dataset_path):
        raise HTTPException(
            status_code=404,
            detail=f"Dataset not found. Please upload the dataset first with job_id={job_id}"
        )
    
    # Get output directory
    output_dir = storage.get_model_dir(job_id)
    
    # Prepare config
    if request.config:
        config_dict = request.config.model_dump()
    else:
        config_dict = {
            "base_model": settings.default_model,
            "max_steps": settings.default_max_steps,
            "batch_size": settings.default_batch_size,
            "learning_rate": settings.default_learning_rate,
        }
    
    try:
        # Queue the training task
        task = celery_app.send_task(
            "phase2.celery_worker.train_model",
            args=[dataset_path, output_dir, config_dict],
            task_id=job_id
        )
        
        return JobResponse(
            job_id=job_id,
            status="queued",
            message="Training job queued successfully",
            created_at=datetime.now().isoformat()
        )
    
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Failed to queue training job: {str(e)}"
        )


@app.get("/status/{job_id}", response_model=JobStatus)
async def get_job_status(job_id: str):
    """
    Get status of a training job
    
    Returns:
        - PENDING: Job is queued
        - STARTED: Job has started
        - PROGRESS: Job is in progress
        - SUCCESS: Job completed successfully
        - FAILURE: Job failed
    """
    try:
        result = AsyncResult(job_id, app=celery_app)
        
        response = JobStatus(
            job_id=job_id,
            status=result.state
        )
        
        if result.state == "PENDING":
            response.status = "queued"
        
        elif result.state == "STARTED":
            response.status = "started"
            if result.info:
                response.progress = result.info.get("progress")
                response.current_step = result.info.get("current_step")
                response.total_steps = result.info.get("total_steps")
        
        elif result.state == "PROGRESS":
            response.status = "training"
            if result.info:
                response.progress = result.info.get("progress")
                response.current_step = result.info.get("current_step")
                response.total_steps = result.info.get("total_steps")
        
        elif result.state == "SUCCESS":
            response.status = "completed"
            response.progress = 100
            response.result = result.result
        
        elif result.state == "FAILURE":
            response.status = "failed"
            response.error = str(result.info)
        
        return response
    
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Failed to get job status: {str(e)}"
        )


@app.get("/jobs", response_model=List[dict])
async def list_jobs():
    """
    List all jobs (active and completed)
    """
    try:
        inspect = celery_app.control.inspect()
        
        # Get active tasks
        active = inspect.active() or {}
        scheduled = inspect.scheduled() or {}
        reserved = inspect.reserved() or {}
        
        jobs = []
        
        # Process active jobs
        for worker, tasks in active.items():
            for task in tasks:
                jobs.append({
                    "job_id": task.get("id"),
                    "status": "active",
                    "worker": worker,
                    "name": task.get("name")
                })
        
        # Process scheduled jobs
        for worker, tasks in scheduled.items():
            for task in tasks:
                jobs.append({
                    "job_id": task.get("request", {}).get("id"),
                    "status": "scheduled",
                    "worker": worker,
                    "name": task.get("request", {}).get("name")
                })
        
        return jobs
    
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Failed to list jobs: {str(e)}"
        )


@app.delete("/job/{job_id}")
async def cancel_job(job_id: str):
    """
    Cancel a running job
    """
    try:
        celery_app.control.revoke(job_id, terminate=True)
        
        return {
            "status": "success",
            "message": f"Job {job_id} has been cancelled",
            "job_id": job_id
        }
    
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Failed to cancel job: {str(e)}"
        )


@app.get("/download/{job_id}")
async def download_model(job_id: str):
    """
    Get download link for trained model
    """
    model_dir = storage.get_model_dir(job_id)
    adapter_dir = Path(model_dir) / "adapter"
    
    if not adapter_dir.exists():
        raise HTTPException(
            status_code=404,
            detail="Model not found. Job may not be completed yet."
        )
    
    # In production, you'd generate a signed URL or stream the file
    return {
        "status": "success",
        "job_id": job_id,
        "model_path": str(adapter_dir),
        "files": [f.name for f in adapter_dir.iterdir()],
        "message": "Model is ready for download"
    }


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "phase2.api:app",
        host="0.0.0.0",
        port=8000,
        reload=True
    )
