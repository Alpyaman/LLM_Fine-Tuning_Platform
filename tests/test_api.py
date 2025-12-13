#!/usr/bin/env python3
"""
Quick test script for Phase 2 API
Tests the complete workflow: upload -> train -> status
"""

import requests
import time
import sys
from pathlib import Path

BASE_URL = "http://localhost:8000"
TEST_DATA_FILE = "example_data.jsonl"


def print_section(title):
    """Print section header"""
    print("\n" + "="*60)
    print(f"  {title}")
    print("="*60)


def test_health():
    """Test health endpoint"""
    print_section("1. Health Check")
    
    try:
        response = requests.get(f"{BASE_URL}/health")
        response.raise_for_status()
        data = response.json()
        
        print(f"✓ Status: {data['status']}")
        print(f"✓ Redis Connected: {data['redis_connected']}")
        print(f"✓ Celery Workers: {data['celery_workers']}")
        
        if not data['redis_connected']:
            print("\n❌ Redis is not connected!")
            print("   Run: docker-compose up -d")
            sys.exit(1)
        
        if data['celery_workers'] == 0:
            print("\n⚠️  No Celery workers found!")
            print("   Run: celery -A celery_config worker --loglevel=info -Q training -P solo")
        
        return True
    
    except requests.exceptions.ConnectionError:
        print("❌ Cannot connect to API!")
        print("   Make sure the API is running: python api.py")
        sys.exit(1)
    except Exception as e:
        print(f"❌ Health check failed: {e}")
        sys.exit(1)


def test_upload():
    """Test dataset upload"""
    print_section("2. Upload Dataset")
    
    if not Path(TEST_DATA_FILE).exists():
        print(f"❌ Test file not found: {TEST_DATA_FILE}")
        sys.exit(1)
    
    try:
        with open(TEST_DATA_FILE, 'rb') as f:
            files = {'file': (TEST_DATA_FILE, f, 'application/json')}
            response = requests.post(f"{BASE_URL}/upload", files=files)
            response.raise_for_status()
            data = response.json()
        
        print(f"✓ Status: {data['status']}")
        print(f"✓ Job ID: {data['job_id']}")
        print(f"✓ Filename: {data['filename']}")
        print(f"✓ File Size: {data['file_size']} bytes")
        
        return data['job_id']
    
    except Exception as e:
        print(f"❌ Upload failed: {e}")
        sys.exit(1)


def test_train(job_id):
    """Test training job submission"""
    print_section("3. Start Training Job")
    
    payload = {
        "dataset_filename": TEST_DATA_FILE,
        "config": {
            "base_model": "unsloth/llama-3-8b-bnb-4bit",
            "max_steps": 10,  # Quick test
            "batch_size": 2,
            "learning_rate": 0.0002
        }
    }
    
    try:
        response = requests.post(f"{BASE_URL}/train", json=payload)
        response.raise_for_status()
        data = response.json()
        
        print(f"✓ Status: {data['status']}")
        print(f"✓ Job ID: {data['job_id']}")
        print(f"✓ Message: {data['message']}")
        
        return data['job_id']
    
    except Exception as e:
        print(f"❌ Training submission failed: {e}")
        if hasattr(e, 'response'):
            print(f"   Response: {e.response.text}")
        sys.exit(1)


def test_status(job_id):
    """Test status polling"""
    print_section("4. Monitor Training Progress")
    
    print(f"Polling job: {job_id}")
    print("(This may take a few minutes...)\n")
    
    last_status = None
    
    try:
        while True:
            response = requests.get(f"{BASE_URL}/status/{job_id}")
            response.raise_for_status()
            data = response.json()
            
            status = data['status']
            
            # Print updates when status changes
            if status != last_status:
                print(f"\n📊 Status: {status}")
                last_status = status
            
            # Show progress
            if data.get('progress') is not None:
                current = data.get('current_step', 0)
                total = data.get('total_steps', 0)
                progress = data.get('progress', 0)
                print(f"   Progress: {progress}% (Step {current}/{total})", end='\r')
            
            # Check if completed
            if status == "completed":
                print("\n\n✅ Training completed!")
                result = data.get('result', {})
                print(f"   Duration: {result.get('training_duration_seconds', 0):.2f}s")
                print(f"   Output: {result.get('adapter_dir', 'N/A')}")
                return True
            
            # Check if failed
            if status == "failed":
                print("\n\n❌ Training failed!")
                print(f"   Error: {data.get('error', 'Unknown error')}")
                return False
            
            # Wait before next poll
            time.sleep(3)
    
    except KeyboardInterrupt:
        print("\n\n⚠️  Monitoring cancelled (job still running)")
        return None
    except Exception as e:
        print(f"\n❌ Status check failed: {e}")
        return False


def main():
    """Run all tests"""
    print("\n🧪 Phase 2 API Test Suite")
    print("="*60)
    
    # Test 1: Health
    test_health()
    
    # Test 2: Upload
    job_id = test_upload()
    
    # Test 3: Train
    train_job_id = test_train(job_id)
    
    # Test 4: Status
    success = test_status(train_job_id)
    
    # Summary
    print_section("Test Complete")
    if success:
        print("✅ All tests passed!")
        print("\nYour model is ready at:")
        print(f"  ./storage/models/{train_job_id}/adapter/")
    else:
        print("⚠️  Some tests failed. Check logs for details.")
    
    print("\n" + "="*60)


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n\nTest interrupted by user")
        sys.exit(0)
