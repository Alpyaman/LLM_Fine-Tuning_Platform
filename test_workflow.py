"""
Test the correct API workflow:
1. Upload dataset and get job_id
2. Use that job_id to start training
"""

import requests
import json
import time

# Your API URL (replace with your ngrok URL or localhost)
API_URL = "http://localhost:8000"  # Change this to your ngrok URL

def test_workflow():
    print("=" * 60)
    print("Testing LLM Fine-Tuning API Workflow")
    print("=" * 60)
    
    # Step 1: Health check
    print("\n1️⃣ Checking API health...")
    response = requests.get(f"{API_URL}/health")
    if response.status_code == 200:
        print("✅ API is healthy")
        print(json.dumps(response.json(), indent=2))
    else:
        print("❌ API health check failed")
        return
    
    # Step 2: Upload dataset
    print("\n2️⃣ Uploading dataset...")
    
    # Create a small test dataset
    test_data = [
        {
            "instruction": "What is Python?",
            "input": "",
            "output": "Python is a high-level programming language."
        },
        {
            "instruction": "Explain machine learning",
            "input": "",
            "output": "Machine learning is a subset of AI that enables systems to learn from data."
        }
    ]
    
    # Save to file
    with open('test_dataset.jsonl', 'w') as f:
        for item in test_data:
            f.write(json.dumps(item) + '\n')
    
    # Upload
    with open('test_dataset.jsonl', 'rb') as f:
        files = {'file': ('test_dataset.jsonl', f, 'application/json')}
        response = requests.post(f"{API_URL}/upload", files=files)
    
    if response.status_code == 200:
        upload_result = response.json()
        print("✅ Dataset uploaded successfully!")
        print(f"   Job ID: {upload_result['job_id']}")
        print(f"   Filename: {upload_result['filename']}")
        
        # IMPORTANT: Save the job_id
        job_id = upload_result['job_id']
    else:
        print(f"❌ Upload failed: {response.text}")
        return
    
    # Step 3: Start training with the SAME job_id
    print(f"\n3️⃣ Starting training with job_id: {job_id}")
    
    train_payload = {
        "dataset_filename": "test_dataset.jsonl",
        "job_id": job_id,  # ⚠️ CRITICAL: Use the job_id from upload!
        "config": {
            "base_model": "unsloth/llama-3-8b-bnb-4bit",
            "max_steps": 10,  # Very small for testing
            "batch_size": 2,
            "learning_rate": 0.0002
        }
    }
    
    response = requests.post(f"{API_URL}/train", json=train_payload)
    
    if response.status_code == 200:
        train_result = response.json()
        print("✅ Training started successfully!")
        print(f"   Job ID: {train_result['job_id']}")
        print(f"   Status: {train_result['status']}")
        
        # Verify it's the same job_id
        if train_result['job_id'] == job_id:
            print("   ✅ Job IDs match correctly!")
        else:
            print("   ⚠️ Warning: Job IDs don't match")
            
        return train_result['job_id']
    else:
        print(f"❌ Training failed to start:")
        print(f"   Status code: {response.status_code}")
        print(f"   Response: {response.json()}")
        return None
    
    # Step 4: Monitor progress
    print(f"\n4️⃣ Monitoring progress...")
    for i in range(5):
        time.sleep(2)
        response = requests.get(f"{API_URL}/status/{job_id}")
        if response.status_code == 200:
            status = response.json()
            print(f"   Status: {status['status']}")
            if status.get('progress'):
                print(f"   Progress: {status['progress']}%")
        time.sleep(3)

if __name__ == "__main__":
    test_workflow()
