import sys
import os

# Load .env file for local development (Vercel injects env vars natively, no .env needed there)
try:
    from dotenv import load_dotenv
    root = os.path.dirname(os.path.dirname(__file__))
    load_dotenv(os.path.join(root, ".env"))
    load_dotenv(os.path.join(root, "backend", ".env"))
except ImportError:
    pass

# Add the backend directory to sys.path so imports like `from api_v1.routes import ...` work
backend_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), "backend")
if backend_path not in sys.path:
    sys.path.insert(0, backend_path)

from main import app  # main.py lives inside backend/
