"""Asset cache and camera clamp."""

import os

os.environ.setdefault("SDL_VIDEODRIVER", "dummy")
os.environ.setdefault("SDL_AUDIODRIVER", "dummy")

import pygame

import config
from src.core.assets import AssetLoader
from src.gameplay.camera import Camera


def test_loads_player_sprite_and_missing_placeholder():
    pygame.init()
    pygame.display.set_mode((config.SCREEN_WIDTH, config.SCREEN_HEIGHT))
    loader = AssetLoader()
    standing = loader.image("player/playerstanding.png")
    assert standing.get_width() > 0
    assert standing.get_height() > 0
    assert loader.image("player/playerstanding.png") is standing

    missing = loader.image("does/not/exist.png")
    assert missing.get_size() == (48, 48)
    corner = missing.get_at((40, 2))
    assert corner[0] == 255
    assert corner[2] == 255


def test_camera_follows_and_clamps_to_zone():
    camera = Camera(1280, 720, zone_width=4000)
    camera.follow(0, 600)
    assert camera.x == 0
    camera.follow(3900, 600)
    assert camera.x == 4000 - 1280
    camera.follow(2000, 600)
    assert 0 < camera.x < 4000 - 1280
