import sys
import os

# Add the project root to python path so we can import backend.main
sys.path.append(os.getcwd())

try:
    from backend.main import app
    print("✅ Backend initialized successfully.")
except ImportError as e:
    print(f"❌ Import Error: {e}")
    sys.exit(1)
except Exception as e:
    print(f"❌ Application Error: {e}")
    sys.exit(1)
