"""
Celery Configuration
"""

import os
from celery import Celery
from dotenv import load_dotenv

load_dotenv()

# Redis configuration
REDIS_HOST = os.getenv("REDIS_HOST", "localhost")
REDIS_PORT = os.getenv("REDIS_PORT", "6379")
REDIS_DB = os.getenv("REDIS_DB", "0")
REDIS_URL = f"redis://{REDIS_HOST}:{REDIS_PORT}/{REDIS_DB}"

# Create Celery app
celery_app = Celery(
    "llm_training",
    broker=REDIS_URL,
    backend=REDIS_URL,
    include=["celery_worker"]
)

# Celery configuration
celery_app.conf.update(
    task_serializer="json",
    accept_content=["json"],
    result_serializer="json",
    timezone="UTC",
    enable_utc=True,
    task_track_started=True,
    task_acks_late=True,
    worker_prefetch_multiplier=1,
    result_expires=3600 * 24,  # 24 hours
    broker_connection_retry_on_startup=True,
)

# Task routes (optional - for multiple queues)
celery_app.conf.task_routes = {
    "celery_worker.train_model": {"queue": "training"},
}
