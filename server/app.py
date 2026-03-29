import sys
import os
import uvicorn

# Add your project root directory to the Python path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Import your FastAPI app from your original root server.py file
from server import app

def run():
    uvicorn.run("server:app", host="0.0.0.0", port=7860)