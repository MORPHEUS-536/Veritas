#!/usr/bin/env python3
"""
Quick Status Check for Monitoring System
"""

import sys
import subprocess

print("\n" + "="*60)
print("  MONITORING SYSTEM 2.0 - STATUS CHECK")
print("="*60 + "\n")

checks = {
    "Python": "python --version",
    "FastAPI": "python -c 'import fastapi; print(fastapi.__version__)'",
    "Uvicorn": "python -c 'import uvicorn; print(uvicorn.__version__)'",
    "Pydantic": "python -c 'import pydantic; print(pydantic.__version__)'",
    "Python-dotenv": "python -c 'import dotenv; print(dotenv.__version__)'",
    "Groq": "python -c 'import groq; print(groq.__version__)'",
}

all_good = True

for name, cmd in checks.items():
    try:
        result = subprocess.run(cmd, shell=True, capture_output=True, text=True, timeout=5)
        if result.returncode == 0:
            version = result.stdout.strip()
            print(f"✓ {name:20} {version}")
        else:
            print(f"✗ {name:20} ERROR")
            all_good = False
    except Exception as e:
        print(f"✗ {name:20} {str(e)}")
        all_good = False

print("\n" + "="*60)

# Check files
print("\n  File Structure Check:\n")
import os

required_files = [
    ".env",
    "main.py",
    "requirements.txt",
    "test_api.py",
    "app/config.py",
    "app/monitoring/engine.py",
    "app/services/groq_service.py",
    "app/api/routes.py",
]

for file_path in required_files:
    if os.path.exists(file_path):
        print(f"✓ {file_path}")
    else:
        print(f"✗ {file_path} - MISSING")
        all_good = False

print("\n" + "="*60)
print("\n  Configuration Check:\n")

try:
    from app.config import settings
    settings.validate()
    print(f"✓ Debug Mode:              {settings.DEBUG}")
    print(f"✓ Host:Port:               {settings.HOST}:{settings.PORT}")
    print(f"✓ LLM Monitoring:          {settings.ENABLE_LLM_MONITORING}")
    print(f"✓ Groq API Key:            {'SET' if settings.GROQ_API_KEY else 'NOT SET'}")
    print(f"✓ Warning Threshold:       {settings.WARNING_THRESHOLD}")
    print(f"✓ Critical Threshold:      {settings.CRITICAL_THRESHOLD}")
    print(f"✓ Max Log Entries:         {settings.MAX_LOG_ENTRIES}")
except Exception as e:
    print(f"✗ Configuration Error: {str(e)}")
    all_good = False

print("\n" + "="*60)

if all_good:
    print("\n  ✓ ALL SYSTEMS READY!\n")
    print("  To start the server, run:")
    print("    python main.py\n")
    print("  Then visit http://localhost:8000/docs\n")
else:
    print("\n  ✗ SOME CHECKS FAILED\n")
    print("  Please fix the issues above.\n")

print("="*60 + "\n")
