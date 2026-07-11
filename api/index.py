import sys
import os

# Add the backend directory to sys.path so imports like `from api_v1.routes import ...` work
backend_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), "backend")
if backend_path not in sys.path:
    sys.path.insert(0, backend_path)

from main import app  # main.py lives inside backend/
