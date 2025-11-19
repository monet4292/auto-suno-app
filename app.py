"""
Suno Account Manager - Main Entry Point
Modern UI application for managing Suno accounts and downloading songs
"""
import sys
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent))

from src.ui import run_app

if __name__ == "__main__":
    run_app()
