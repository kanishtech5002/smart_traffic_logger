import os
import sys

# Add parent directory to sys.path so app can be imported properly
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app import app
