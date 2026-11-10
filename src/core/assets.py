"""Cached image loading for the forest art, scaled to the 1280x720 window."""

from pathlib import Path

import pygame

import config

# The jam art was drawn for a 1300x800 window.
REFERENCE_SIZE = (1300, 800)


class AssetLoader:
    """Load pictures once and hand back the same surface next time."""

    def __init__(self, images_dir: Path = None):
        self.images_dir = Path(images_dir) if images_dir else config.IMAGES_DIR
        self._cache = {}
        self.scale_x = config.SCREEN_WIDTH / REFERENCE_SIZE[0]
        self.scale_y = config.SCREEN_HEIGHT / REFERENCE_SIZE[1]

    def image(self, relative_path: str) -> pygame.Surface:
        key = relative_path.replace("\\", "/")
        cached = self._cache.get(key)
        if cached is not None:
            return cached
        path = self.images_dir / key
        if not path.exists():
            surface = self.placeholder(key)
        else:
            loaded = pygame.image.load(str(path))
            if pygame.display.get_surface():
                loaded = loaded.convert_alpha()
            width = max(1, int(loaded.get_width() * self.scale_x))
            height = max(1, int(loaded.get_height() * self.scale_y))
            surface = pygame.transform.scale(loaded, (width, height))
        self._cache[key] = surface
        return surface

    def placeholder(self, name: str) -> pygame.Surface:
        """A visible stand-in so a missing file does not crash the frame."""
        surface = pygame.Surface((48, 48), pygame.SRCALPHA)
        surface.fill((255, 0, 255, 255))
        pygame.draw.line(surface, (0, 0, 0), (0, 0), (47, 47), 2)
        return surface
