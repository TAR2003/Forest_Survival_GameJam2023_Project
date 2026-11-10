"""Forest Survival entry point."""

import sys
import traceback
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

try:
    import pygame
    from src.game import ForestSurvivalGame
except ImportError as exc:
    print(f"Failed to import required modules: {exc}")
    print("Install dependencies with: pip install -r requirements.txt")
    sys.exit(1)


def main():
    """Create the game, run until quit, and always clean up."""
    game = None
    try:
        game = ForestSurvivalGame()
        game.run()
    except pygame.error as exc:
        print(f"Pygame error: {exc}")
        return 1
    except KeyboardInterrupt:
        print("\nGame interrupted by user.")
        return 0
    except Exception as exc:
        print(f"Unexpected error occurred: {exc}")
        traceback.print_exc()
        return 1
    finally:
        if game:
            game.cleanup()
        try:
            pygame.quit()
        except Exception:
            pass
    return 0


if __name__ == "__main__":
    sys.exit(main())
