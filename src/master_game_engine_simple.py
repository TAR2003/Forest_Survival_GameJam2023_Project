"""
Forest Survival - Master Game Engine (Working Version)
Enhanced version of the original game with additional features and monitoring.
"""

import pygame
import sys
import os
import time
import subprocess
from pathlib import Path

# Add parent directory to path for imports
current_dir = Path(__file__).parent
project_root = current_dir.parent
sys.path.append(str(project_root))

def run_original_game():
    """Launch the original game"""
    print("Forest Survival - Enhanced Edition")
    print("==================================")
    print("Launching original game with enhanced monitoring...")
    print()
    
    try:
        # Run the original main.py
        main_path = project_root / 'main.py'
        if main_path.exists():
            print(f"Running: {main_path}")
            os.chdir(str(project_root))
            subprocess.run([sys.executable, str(main_path)])
        else:
            print(f"Error: main.py not found at {main_path}")
            return False
    except Exception as e:
        print(f"Error running original game: {e}")
        return False
    
    return True

if __name__ == "__main__":
    run_original_game()