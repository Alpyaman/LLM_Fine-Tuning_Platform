"""
Storage utilities for managing datasets and models
Supports local filesystem and AWS S3
"""

import os
import shutil
from pathlib import Path
from typing import Optional
import aiofiles


class LocalStorage:
    """Local filesystem storage"""
    
    def __init__(self, base_dir: str = "./storage"):
        self.base_dir = Path(base_dir)
        self.datasets_dir = self.base_dir / "datasets"
        self.models_dir = self.base_dir / "models"
        
        # Create directories
        self.datasets_dir.mkdir(parents=True, exist_ok=True)
        self.models_dir.mkdir(parents=True, exist_ok=True)
    
    async def save_dataset(self, file_content: bytes, filename: str, job_id: str) -> str:
        """
        Save uploaded dataset
        
        Args:
            file_content: File content as bytes
            filename: Original filename
            job_id: Unique job identifier
            
        Returns:
            Path to saved file
        """
        # Create job-specific directory
        job_dir = self.datasets_dir / job_id
        job_dir.mkdir(parents=True, exist_ok=True)
        
        # Save file
        file_path = job_dir / filename
        async with aiofiles.open(file_path, 'wb') as f:
            await f.write(file_content)
        
        return str(file_path)
    
    def get_dataset_path(self, job_id: str, filename: str) -> str:
        """Get path to a dataset"""
        return str(self.datasets_dir / job_id / filename)
    
    def get_model_dir(self, job_id: str) -> str:
        """Get directory for model outputs"""
        model_dir = self.models_dir / job_id
        model_dir.mkdir(parents=True, exist_ok=True)
        return str(model_dir)
    
    def list_datasets(self, job_id: str) -> list:
        """List all datasets for a job"""
        job_dir = self.datasets_dir / job_id
        if not job_dir.exists():
            return []
        return [f.name for f in job_dir.iterdir() if f.is_file()]
    
    def delete_dataset(self, job_id: str):
        """Delete dataset for a job"""
        job_dir = self.datasets_dir / job_id
        if job_dir.exists():
            shutil.rmtree(job_dir)
    
    def delete_model(self, job_id: str):
        """Delete model outputs for a job"""
        model_dir = self.models_dir / job_id
        if model_dir.exists():
            shutil.rmtree(model_dir)


class S3Storage:
    """AWS S3 storage (optional)"""
    
    def __init__(
        self,
        bucket_name: str,
        aws_access_key: Optional[str] = None,
        aws_secret_key: Optional[str] = None,
        region: str = "us-east-1"
    ):
        """
        Initialize S3 storage
        
        Args:
            bucket_name: S3 bucket name
            aws_access_key: AWS access key (or use env vars)
            aws_secret_key: AWS secret key (or use env vars)
            region: AWS region
        """
        try:
            import boto3
            
            self.bucket_name = bucket_name
            self.s3_client = boto3.client(
                's3',
                aws_access_key_id=aws_access_key or os.getenv('AWS_ACCESS_KEY_ID'),
                aws_secret_access_key=aws_secret_key or os.getenv('AWS_SECRET_ACCESS_KEY'),
                region_name=region
            )
        except ImportError:
            raise ImportError("boto3 required for S3 storage. Install with: pip install boto3")
    
    async def save_dataset(self, file_content: bytes, filename: str, job_id: str) -> str:
        """Upload dataset to S3"""
        key = f"datasets/{job_id}/{filename}"
        
        self.s3_client.put_object(
            Bucket=self.bucket_name,
            Key=key,
            Body=file_content
        )
        
        return f"s3://{self.bucket_name}/{key}"
    
    def get_dataset_path(self, job_id: str, filename: str) -> str:
        """Get S3 path to dataset"""
        return f"s3://{self.bucket_name}/datasets/{job_id}/{filename}"
    
    def download_dataset(self, job_id: str, filename: str, local_path: str):
        """Download dataset from S3 to local path"""
        key = f"datasets/{job_id}/{filename}"
        self.s3_client.download_file(self.bucket_name, key, local_path)
    
    def upload_model(self, local_dir: str, job_id: str):
        """Upload trained model to S3"""
        for root, dirs, files in os.walk(local_dir):
            for file in files:
                local_file = os.path.join(root, file)
                relative_path = os.path.relpath(local_file, local_dir)
                s3_key = f"models/{job_id}/{relative_path}"
                
                self.s3_client.upload_file(local_file, self.bucket_name, s3_key)
        
        return f"s3://{self.bucket_name}/models/{job_id}/"


# Storage factory
def get_storage(storage_type: str = "local", **kwargs):
    """
    Get storage instance based on type
    
    Args:
        storage_type: 'local' or 's3'
        **kwargs: Additional arguments for storage initialization
        
    Returns:
        Storage instance
    """
    if storage_type == "local":
        return LocalStorage(**kwargs)
    elif storage_type == "s3":
        return S3Storage(**kwargs)
    else:
        raise ValueError(f"Unknown storage type: {storage_type}")
