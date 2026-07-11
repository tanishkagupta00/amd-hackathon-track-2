import sys
import os

backend_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), "backend")
sys.path.insert(0, backend_path)

from backend.main import app
