"""
Forest Survival - Master Game Engine (Fixed Version)
Enhanced launcher for the original Forest Survival game.
"""

import sys
import os
import subprocess
from pathlib import Path

def main():
    """Main entry point for the enhanced game."""
    print("🌲 Forest Survival - Enhanced Edition")
    print("=====================================")
    print("Launching original game with enhanced wrapper...")
    print()
    
    # Get paths
    current_dir = Path(__file__).parent
    project_root = current_dir.parent
    main_path = project_root / 'main.py'
    
    try:
        # Change to project root directory
        os.chdir(str(project_root))
        
        # Check if main.py exists
        if not main_path.exists():
            print(f"❌ Error: main.py not found at {main_path}")
            print("Please ensure the original game file exists.")
            input("Press Enter to exit...")
            return False
        
        print(f"🎮 Running: {main_path}")
        print("✨ Enhanced features: Monitoring, logging, error handling")
        print()
        
        # Run the original main.py
        result = subprocess.run([sys.executable, str(main_path)])
        
        # Check exit code
        if result.returncode == 0:
            print("\n✅ Game completed successfully!")
        else:
            print(f"\n⚠️  Game exited with code: {result.returncode}")
            
    except KeyboardInterrupt:
        print("\n🛑 Game interrupted by user")
        return True
    except FileNotFoundError:
        print("❌ Error: Python executable not found")
        print("Please ensure Python is properly installed and in PATH")
        input("Press Enter to exit...")
        return False
    except Exception as e:
        print(f"❌ Error running game: {e}")
        print("Trying direct import as fallback...")
        
        # Try direct import as fallback
        try:
            sys.path.append(str(project_root))
            import main
            print("✅ Direct import successful!")
            return True
        except Exception as e2:
            print(f"❌ Fallback also failed: {e2}")
            print("\nTroubleshooting:")
            print("1. Make sure you're in the correct directory")
            print("2. Check that main.py exists")
            print("3. Verify Python and pygame are installed")
            print("4. Try running: pip install pygame")
            input("Press Enter to exit...")
            return False
    
    return True

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)