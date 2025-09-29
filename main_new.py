"""
Forest Survival - Game Entry Point
Production-ready entry point with proper initialization and error handling.
"""

import sys
import traceback
from pathlib import Path

# Add src directory to path for imports
sys.path.insert(0, str(Path(__file__).parent / "src"))

try:
    import pygame
    from src.game import ForestSurvivalGame
    from src.core.performance_monitor import PerformanceMonitor
    import config
except ImportError as e:
    print(f"Failed to import required modules: {e}")
    print("Please ensure pygame is installed: pip install pygame")
    sys.exit(1)


def main():
    """Main entry point for Forest Survival game."""
    performance_monitor = None
    game = None
    
    try:
        # Initialize performance monitoring
        performance_monitor = PerformanceMonitor()
        
        # Initialize and run the game
        game = ForestSurvivalGame()
        game.run()
        
    except pygame.error as e:
        print(f"Pygame error: {e}")
        print("Please check your display settings and audio drivers.")
        return 1
        
    except KeyboardInterrupt:
        print("\nGame interrupted by user.")
        return 0
        
    except Exception as e:
        print(f"Unexpected error occurred: {e}")
        print("Error details:")
        traceback.print_exc()
        return 1
        
    finally:
        # Cleanup
        if game:
            game.cleanup()
        if performance_monitor:
            performance_monitor.save_session_data()
        
        # Quit pygame
        try:
            pygame.quit()
        except:
            pass
    
    return 0


if __name__ == "__main__":
    sys.exit(main())