"""
Verify Phase 2 Setup
Checks if all imports and modules are correctly configured
"""

import sys
from pathlib import Path

# Colors for terminal output
GREEN = '\033[92m'
RED = '\033[91m'
YELLOW = '\033[93m'
RESET = '\033[0m'


def print_status(message, success=True):
    """Print colored status message"""
    color = GREEN if success else RED
    symbol = "✓" if success else "✗"
    print(f"{color}{symbol}{RESET} {message}")


def check_imports():
    """Verify all critical imports work"""
    print("\n" + "="*60)
    print("Checking Module Imports")
    print("="*60)
    
    checks_passed = 0
    checks_total = 0
    
    # Check Phase 1 imports
    tests = [
        ("phase1.train", "LLMTrainer"),
        ("phase1.config", "TrainingConfig"),
        ("phase1.data_formatter", "DataFormatter"),
        ("phase2.celery_config", "celery_app"),
        ("phase2.celery_worker", "train_model"),
        ("phase2.storage", "get_storage"),
        ("phase2.api", "app"),
    ]
    
    for module_name, attr_name in tests:
        checks_total += 1
        try:
            module = __import__(module_name, fromlist=[attr_name])
            getattr(module, attr_name)
            print_status(f"{module_name}.{attr_name}", success=True)
            checks_passed += 1
        except Exception as e:
            print_status(f"{module_name}.{attr_name} - {str(e)}", success=False)
    
    return checks_passed, checks_total


def check_structure():
    """Verify project structure"""
    print("\n" + "="*60)
    print("Checking Project Structure")
    print("="*60)
    
    project_root = Path(__file__).resolve().parent
    
    required_files = [
        "phase1/__init__.py",
        "phase2/__init__.py",
        "phase1/train.py",
        "phase1/config.py",
        "phase2/api.py",
        "phase2/celery_config.py",
        "phase2/celery_worker.py",
        "docker-compose.yml",
        "requirements.txt",
    ]
    
    checks_passed = 0
    checks_total = len(required_files)
    
    for file_path in required_files:
        full_path = project_root / file_path
        if full_path.exists():
            print_status(file_path, success=True)
            checks_passed += 1
        else:
            print_status(f"{file_path} - NOT FOUND", success=False)
    
    return checks_passed, checks_total


def check_environment():
    """Check environment setup"""
    print("\n" + "="*60)
    print("Checking Environment")
    print("="*60)
    
    checks_passed = 0
    checks_total = 0
    
    # Check Python version
    checks_total += 1
    py_version = sys.version_info
    if py_version.major == 3 and py_version.minor >= 10:
        print_status(f"Python {py_version.major}.{py_version.minor}.{py_version.micro}", success=True)
        checks_passed += 1
    else:
        print_status(f"Python {py_version.major}.{py_version.minor} (requires 3.10+)", success=False)
    
    # Check required packages
    required_packages = [
        "fastapi",
        "celery",
        "redis",
        "uvicorn",
        "transformers",
        "torch",
    ]
    
    for package in required_packages:
        checks_total += 1
        try:
            __import__(package)
            print_status(f"Package: {package}", success=True)
            checks_passed += 1
        except ImportError:
            print_status(f"Package: {package} - NOT INSTALLED", success=False)
    
    return checks_passed, checks_total


def check_redis():
    """Check Redis connection"""
    print("\n" + "="*60)
    print("Checking Redis Connection")
    print("="*60)
    
    try:
        import redis
        client = redis.Redis(host='localhost', port=6379, db=0)
        client.ping()
        print_status("Redis connection", success=True)
        return 1, 1
    except Exception as e:
        print_status(f"Redis connection - {str(e)}", success=False)
        print(f"{YELLOW}  → Start Redis with: docker-compose up -d{RESET}")
        return 0, 1


def main():
    """Run all checks"""
    print("\n" + "="*60)
    print("🔍 Phase 2 Setup Verification")
    print("="*60)
    
    # Check working directory
    cwd = Path.cwd()
    print(f"\nCurrent directory: {cwd}")
    
    if cwd.name != "LLM_Fine-Tuning_Platform":
        print(f"{YELLOW}⚠ Warning: Not in project root!{RESET}")
        print(f"  → cd to: {cwd.parent / 'LLM_Fine-Tuning_Platform'}")
    
    # Run all checks
    total_passed = 0
    total_checks = 0
    
    passed, total = check_structure()
    total_passed += passed
    total_checks += total
    
    passed, total = check_environment()
    total_passed += passed
    total_checks += total
    
    passed, total = check_imports()
    total_passed += passed
    total_checks += total
    
    passed, total = check_redis()
    total_passed += passed
    total_checks += total
    
    # Summary
    print("\n" + "="*60)
    print("Summary")
    print("="*60)
    
    percentage = (total_passed / total_checks) * 100
    
    if total_passed == total_checks:
        print(f"{GREEN}✅ All checks passed! ({total_passed}/{total_checks}){RESET}")
        print("\n🚀 Ready to start Phase 2!")
        print("\nNext steps:")
        print("  1. docker-compose up -d")
        print("  2. run_worker.bat  (or celery -A phase2.celery_config worker ...)")
        print("  3. run_api.bat     (or python -m phase2.api)")
    elif percentage >= 80:
        print(f"{YELLOW}⚠ Most checks passed ({total_passed}/{total_checks}){RESET}")
        print("\nAddress the failed checks above, then try again.")
    else:
        print(f"{RED}❌ Many checks failed ({total_passed}/{total_checks}){RESET}")
        print("\nPlease review the errors above.")
        print("\nCommon fixes:")
        print("  - Run from project root")
        print("  - Install dependencies: pip install -r requirements.txt")
        print("  - Start Redis: docker-compose up -d")
    
    print("\n" + "="*60)
    
    return 0 if total_passed == total_checks else 1


if __name__ == "__main__":
    sys.exit(main())
