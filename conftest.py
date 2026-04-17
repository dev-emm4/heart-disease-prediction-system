import sys
import os

# Add src/ to path so bare imports like `from domain...` resolve
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "src"))